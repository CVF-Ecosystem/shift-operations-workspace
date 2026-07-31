"""Staffing application service (P2C-MUTATION-FULL-UI-C3A1, SPEC R5).

The single governed entry point for shift assignment management, following
the identity -> permission -> transaction(mutate + audit) shape every other
service in this codebase uses (ShiftService.close/freeze, MessageService.
create, IncidentService.report, ...). `shift.assignment.manage` requires at
least `shift_supervisor`; a supervisor may staff ANY shift (the bounded
staffing control-plane exception - ADR section 4.2), never a wider claim.

C3a1 does NOT enforce ACTIVE assignment on ordinary operational routes - that
route-wide enforcement is C3a2 (ADR section 2/4.3, fan-out addendum). This
service only implements the assignment/staffing surface itself.
"""

from __future__ import annotations

from uuid import UUID

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from operations_ledger import Ledger

from workspace_api.domain.models import ShiftAssignment

_ADD_CHAIN = ["identity", "permission", "assign", "audit"]
_REVOKE_CHAIN = ["identity", "permission", "revoke", "audit"]


class AssignmentService:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def list_for_shift(self, shift_id: UUID, principal: Principal) -> list[ShiftAssignment]:
        require_action(principal, "shift.assignment.manage")
        self.ledger.get_shift(shift_id)  # KeyError -> 404 if the shift itself is unknown
        return self.ledger.list_assignments_for_shift(shift_id)

    def assign(self, shift_id: UUID, target_user_id: str, principal: Principal) -> ShiftAssignment:
        """R4-analog for staffing: target must exist and be active; actor/
        status/timestamps are server-derived; add + audit are atomic."""
        require_action(principal, "shift.assignment.manage")

        self.ledger.get_shift(shift_id)  # KeyError -> 404 if unknown

        target = self.ledger.get_user_by_id(target_user_id)
        if target is None or not target.is_active:
            raise CvfDenied(
                control="assign",
                reason=f"target user is not a persisted active user: {target_user_id!r}",
                http_status=422,
            )

        existing = self.ledger.get_active_assignment(shift_id, target_user_id)
        if existing is not None:
            raise CvfDenied(
                control="assign",
                reason=f"user {target_user_id!r} already has an ACTIVE assignment for this shift",
                http_status=409,
            )

        assignment = ShiftAssignment(shift_id=shift_id, user_id=target_user_id, assigned_by=principal.user_id)

        with self.ledger.transaction() as unit:
            created = self.ledger.add_assignment(assignment, unit=unit)
            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="shift.assignment.manage",
                    record_type="ShiftAssignment",
                    record_id=str(created.assignment_id),
                    control_chain=_ADD_CHAIN,
                    before_state=None,
                    after_state=str(created.status),
                ),
                unit=unit,
            )
        return created

    def revoke(
        self, shift_id: UUID, assignment_id: UUID, expected_version: int, principal: Principal
    ) -> ShiftAssignment:
        require_action(principal, "shift.assignment.manage")

        current = self.ledger.get_assignment(assignment_id)
        if current.shift_id != shift_id:
            raise KeyError(assignment_id)
        before = str(current.status)

        with self.ledger.transaction() as unit:
            revoked = self.ledger.revoke_assignment(
                assignment_id, revoked_by=principal.user_id, expected_version=expected_version, unit=unit
            )
            # Idempotent repeat at the current revoked version writes no
            # second audit (SPEC R5); only a genuine state transition does.
            if before != str(revoked.status):
                self.ledger.append_audit(
                    AuditRecord(
                        actor_id=principal.user_id,
                        actor_role=principal.role,
                        action="shift.assignment.manage",
                        record_type="ShiftAssignment",
                        record_id=str(revoked.assignment_id),
                        control_chain=_REVOKE_CHAIN,
                        before_state=before,
                        after_state=str(revoked.status),
                    ),
                    unit=unit,
                )
        return revoked
