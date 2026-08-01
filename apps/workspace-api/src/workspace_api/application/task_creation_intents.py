"""Task-creation-intent digest, creation and lookup.

Split out of ``approval_service.py`` (CVF-FILE-SPLIT-GUARD-HARDENING) to keep
each module under the hard line limit. Owns the digest-bound task
creation-intent two-phase flow (ADR section 4.4). ``approval_service.py``
re-exports these names unchanged as the compatibility facade; import from
there, not from this module, in new code.
"""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from cvf_runtime.risk import requirement_for
from operations_ledger import Ledger

from operations_domain.models import Task, TaskCreationIntent
from workspace_api.application.assignment_scope import require_active_assignment

from workspace_api.application.approval_receipts import has_authority_for_any_required_seat


def compute_payload_digest(task: Task) -> str:
    """Canonical payload digest (SPEC section 5.3) over the fields an
    approver actually reviewed. ``evidence_id`` (random per ``EvidenceRef``)
    is deliberately excluded; only the meaningful evidence fields are
    digested, in submitted order.
    """
    canonical = json.dumps(
        {
            "shift_id": str(task.shift_id),
            "title": task.title,
            "description": task.description,
            "owner_id": task.owner_id,
            "risk_class": str(task.risk_class),
            "evidence": [
                {"source_type": e.source_type, "source_id": e.source_id, "sha256": e.sha256}
                for e in task.evidence
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def create_task_creation_intent(
    ledger: Ledger,
    principal: Principal,
    *,
    task: Task,
    profile: CvfProfile | None = None,
) -> TaskCreationIntent:
    """R9.1: persist the durable, approver-visible target `task.create`
    approvals bind to. Only valid when the submitted risk class actually
    requires approval - an R0/R1 intent would be a dead target nothing can
    ever bind a meaningful quorum to."""
    profile = profile or load_profile()
    require_action(principal, "task.create")
    require_active_assignment(ledger, task.shift_id, principal)
    risk_class = str(task.risk_class)
    requirement = requirement_for(profile, risk_class)
    if not requirement.required_roles:
        raise CvfDenied(
            control="approval",
            reason=(
                f"{risk_class} requires no approval; creation intents exist only "
                f"for risk classes with a required quorum"
            ),
            http_status=422,
        )

    digest = compute_payload_digest(task)
    intent = TaskCreationIntent(
        shift_id=task.shift_id,
        risk_class=risk_class,
        payload_snapshot={
            "shift_id": str(task.shift_id),
            "title": task.title,
            "description": task.description,
            "owner_id": task.owner_id,
            "risk_class": risk_class,
            "evidence": [e.model_dump(mode="json") for e in task.evidence],
        },
        payload_digest=digest,
        created_by=principal.user_id,
    )
    with ledger.transaction() as unit:
        ledger.add_task_creation_intent(intent, unit=unit)
        ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action="task.creation_intent.create",
                record_type="TaskCreationIntent",
                record_id=str(intent.intent_id),
                control_chain=["identity", "permission", "audit"],
                before_state=None,
                after_state=None,
            ),
            unit=unit,
        )
    return intent


def get_task_creation_intent(
    ledger: Ledger,
    principal: Principal,
    intent_id: UUID,
    *,
    profile: CvfProfile | None = None,
) -> TaskCreationIntent:
    """R9.1: an authenticated user may inspect the immutable intent only when
    a fresh `users` lookup finds them active with authority for at least one
    seat the intent's risk class requires."""
    profile = profile or load_profile()
    try:
        intent = ledger.get_task_creation_intent(intent_id)
    except KeyError as exc:
        raise CvfDenied(
            control="approval", reason="creation intent not found", http_status=404
        ) from exc

    user = ledger.get_user_by_id(principal.user_id)
    if (
        user is None
        or not user.is_active
        or not has_authority_for_any_required_seat(profile, str(intent.risk_class), user.role)
    ):
        raise CvfDenied(
            control="approval",
            reason="viewer is missing, inactive, or insufficiently authorized for this intent",
            http_status=403,
        )
    require_active_assignment(ledger, intent.shift_id, principal)
    return intent
