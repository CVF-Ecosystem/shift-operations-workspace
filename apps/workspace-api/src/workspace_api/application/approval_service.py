"""Approval receipt / task-creation-intent application service.

P2B-APPROVER-IDENTITY-RECONCILIATION (closing High Finding #4). Owns
everything genuinely new in this tranche: authenticated receipt creation, the
digest-bound task creation-intent two-phase flow (ADR section 4.4), and the
server-owned authority resolver every governed service (EventService/
CorrectionService/TaskService) uses to evaluate a quorum. This keeps
``cvf_runtime.approval`` a pure gate function (Protocol-typed, no ledger/
domain import - see that module's docstring) while the actual persistence and
authority-lookup glue lives here, in the application layer, exactly like
every other governed action in this codebase.
"""

from __future__ import annotations

import hashlib
import json
from typing import Callable
from uuid import UUID

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority, require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from cvf_runtime.risk import requirement_for
from operations_ledger import Ledger

from operations_domain.models import ApprovalReceipt, Task, TaskCreationIntent

# The only (record_type, action) pairs this tranche authorizes (SPEC section 5.2).
_VALID_RECORD_ACTION_PAIRS = {
    ("OperationalEvent", "event.confirm"),
    ("OperationalEvent", "event.correct"),
    ("Task", "task.create"),
}


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


def authority_for_factory(ledger: Ledger, *, unit=None) -> Callable[[str], str | None]:
    """A server-owned closure resolving an approver's FRESH current role.

    Returns the role only for an existing, ``is_active`` user; ``None``
    otherwise (missing/inactive/removed) - SPEC R1.2/R3.1/R3.2: authority is
    always re-derived from the current `users` row, never from a receipt's
    stored ``approver_role`` or a JWT claim. Memoized only for the lifetime of
    this closure (one quorum evaluation), never across requests.
    """
    cache: dict[str, str | None] = {}

    def _authority_for(user_id: str) -> str | None:
        if user_id not in cache:
            user = ledger.get_user_by_id(user_id, unit=unit)
            cache[user_id] = user.role if user is not None and user.is_active else None
        return cache[user_id]

    return _authority_for


def collect_receipts_for(
    ledger: Ledger,
    *,
    record_type: str,
    record_id,
    action: str,
    target_version: int,
    risk_class: str | None = None,
    payload_digest: str | None = None,
    unit=None,
) -> list[ApprovalReceipt]:
    """Server-side auto-collection (SPEC R5.1): the governed request body
    never carries approver or receipt ids."""
    return ledger.list_approval_receipts_for(
        record_type=record_type,
        record_id=record_id,
        action=action,
        target_version=target_version,
        risk_class=risk_class,
        payload_digest=payload_digest,
        unit=unit,
    )


def _has_authority_for_any_required_seat(profile: CvfProfile, risk_class: str, role: str) -> bool:
    """True if ``role`` has authority for at least one seat the risk class
    requires (R2.2/R9.1's "sufficient for any required seat" bar)."""
    required_roles = requirement_for(profile, risk_class).required_roles
    return any(has_authority(role, seat_role) for seat_role in required_roles)


def create_approval_receipt(
    ledger: Ledger,
    principal: Principal,
    *,
    record_type: str,
    action: str,
    record_id,
    profile: CvfProfile | None = None,
) -> tuple[ApprovalReceipt, bool]:
    """Create (or idempotently return) a receipt for ``principal`` acting as
    approver.

    Returns ``(receipt, created)`` - ``created`` is ``False`` on an exact
    idempotent repeat (SPEC R2.4: HTTP 200, not a new row/duplicate audit).
    ``risk_class``/``target_version``/``payload_digest`` are always derived
    from the stored target, never accepted from the caller (R2.3/R9.2).
    """
    profile = profile or load_profile()

    if (record_type, action) not in _VALID_RECORD_ACTION_PAIRS:
        raise CvfDenied(
            control="approval",
            reason=f"unknown (record_type, action) pair: ({record_type!r}, {action!r})",
            http_status=422,
        )

    with ledger.transaction() as unit:
        if record_type == "OperationalEvent":
            try:
                record = ledger.get_event(record_id, unit=unit)
            except KeyError as exc:
                raise CvfDenied(
                    control="approval", reason="target event not found", http_status=404
                ) from exc
            risk_class = str(record.risk_class)
            target_version = record.version
            payload_digest = None
        else:  # ("Task", "task.create")
            try:
                intent = ledger.get_task_creation_intent(record_id, unit=unit)
            except KeyError as exc:
                raise CvfDenied(
                    control="approval", reason="creation intent not found", http_status=404
                ) from exc
            risk_class = str(intent.risk_class)
            target_version = 1
            payload_digest = intent.payload_digest

        user = ledger.get_user_by_id(principal.user_id, unit=unit)
        if user is None or not user.is_active:
            raise CvfDenied(
                control="approval",
                reason="approver is not a known, active user",
                http_status=403,
            )
        if not _has_authority_for_any_required_seat(profile, risk_class, user.role):
            raise CvfDenied(
                control="approval",
                reason=(
                    f"role {user.role!r} has no authority for any seat "
                    f"{risk_class} requires"
                ),
                http_status=403,
            )

        existing = ledger.get_approval_receipt(
            record_type=record_type,
            record_id=record_id,
            action=action,
            target_version=target_version,
            approver_id=principal.user_id,
            unit=unit,
        )
        if existing is not None:
            return existing, False

        receipt = ApprovalReceipt(
            record_type=record_type,
            record_id=record_id,
            action=action,
            target_version=target_version,
            risk_class=risk_class,
            payload_digest=payload_digest,
            approver_id=principal.user_id,
            approver_role=user.role,
        )
        ledger.add_approval_receipt(receipt, unit=unit)
        ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=user.role,
                action="approval.create",
                record_type=record_type,
                record_id=str(record_id),
                control_chain=["identity", "approval", "audit"],
                before_state=None,
                after_state=None,
            ),
            unit=unit,
        )
        return receipt, True


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
        or not _has_authority_for_any_required_seat(profile, str(intent.risk_class), user.role)
    ):
        raise CvfDenied(
            control="approval",
            reason="viewer is missing, inactive, or insufficiently authorized for this intent",
            http_status=403,
        )
    return intent
