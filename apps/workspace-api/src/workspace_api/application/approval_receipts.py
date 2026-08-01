"""Approval-receipt creation and quorum-authority resolution.

Split out of ``approval_service.py`` (CVF-FILE-SPLIT-GUARD-HARDENING) to keep
each module under the hard line limit. Owns the authenticated receipt-creation
flow and the server-owned authority resolver every governed service
(EventService/CorrectionService/TaskService) uses to evaluate a quorum.
``approval_service.py`` re-exports these names unchanged as the compatibility
facade; import from there, not from this module, in new code.
"""

from __future__ import annotations

from typing import Callable

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority
from cvf_runtime.policy_loader import CvfProfile, load_profile
from cvf_runtime.risk import requirement_for
from operations_ledger import Ledger

from operations_domain.models import ApprovalReceipt
from workspace_api.application.assignment_scope import require_active_assignment

# The only (record_type, action) pairs this tranche authorizes (SPEC section 5.2).
_VALID_RECORD_ACTION_PAIRS = {
    ("OperationalEvent", "event.confirm"),
    ("OperationalEvent", "event.correct"),
    ("Task", "task.create"),
    # P2A-INCIDENT-VERTICAL: incident.acknowledge reuses the same
    # already-persisted-target receipt shape as event.confirm - no second
    # creation-intent mechanism (ADR section 2.2).
    ("Incident", "incident.acknowledge"),
    # P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE (SPEC R16): report.approve
    # reuses the same already-persisted-target receipt shape. risk_class is
    # fixed to R2 (Report has no independent risk_class field, unlike
    # Incident); payload_digest is the stored current report's exact
    # snapshot_digest, not None.
    ("Report", "report.approve"),
}


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


def has_authority_for_any_required_seat(profile: CvfProfile, risk_class: str, role: str) -> bool:
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
            shift_id = record.shift_id
        elif record_type == "Incident":
            try:
                record = ledger.get_incident(record_id, unit=unit)
            except KeyError as exc:
                raise CvfDenied(
                    control="approval", reason="target incident not found", http_status=404
                ) from exc
            risk_class = str(record.risk_class)
            target_version = record.version
            payload_digest = None
            shift_id = record.shift_id
        elif record_type == "Report":
            try:
                record = ledger.get_report(record_id, unit=unit)
            except KeyError as exc:
                raise CvfDenied(
                    control="approval", reason="target report not found", http_status=404
                ) from exc
            report_lifecycle_ok = record.is_current and str(record.status) == "IN_REVIEW"
            risk_class = "R2"
            target_version = record.version
            payload_digest = record.content.snapshot_digest
            shift_id = record.shift_id
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
            shift_id = intent.shift_id

        user = ledger.get_user_by_id(principal.user_id, unit=unit)
        if user is None or not user.is_active:
            raise CvfDenied(
                control="approval",
                reason="approver is not a known, active user",
                http_status=403,
            )
        if not has_authority_for_any_required_seat(profile, risk_class, user.role):
            raise CvfDenied(
                control="approval",
                reason=(
                    f"role {user.role!r} has no authority for any seat "
                    f"{risk_class} requires"
                ),
                http_status=403,
            )
        require_active_assignment(ledger, shift_id, principal, unit=unit)
        if record_type == "Report" and not report_lifecycle_ok:
            raise CvfDenied(
                control="approval",
                reason="report is not a current IN_REVIEW report",
                http_status=409,
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
