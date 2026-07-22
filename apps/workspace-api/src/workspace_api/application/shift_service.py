"""Shift application service — makes freeze a real cross-record invariant.

A 2026-07-22 independent review (docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md,
Critical Finding #1) found `freeze_shift` had no identity/permission/prerequisite
check and that mutations on a frozen shift's children were not blocked in
SqlLedger. This service is the single place freeze is requested from, so the
chain cannot be bypassed by calling the ledger directly from a router.

freeze-policy.yaml requires shift_closed, report_approved and
open_handover_items_linked. This repo has no Report or Handover model yet
(Phase 5 / P2-D), so those two conditions cannot be checked for real. Rather
than pretend to check them, freezing while they are unimplemented requires an
explicit, audited override with a reason — never a silent skip.

P-FIX-6 (2026-07-22): a SECOND independent review rejected the P-FIX-5 closure
claim because `POST /shifts/{shift_id}/close` still called `ledger.close_shift()`
directly from the router with no identity/permission/audit at all (probe:
anonymous close -> 200 CLOSED, audit_count=0). Since `ShiftService.freeze`
only checks `shift.status == ShiftStatus.CLOSED`, that anonymous close could
silently satisfy freeze's `shift_closed` prerequisite. `close` below is the
single governed place shift-close is requested from now, following the exact
identity -> permission -> state-check -> transaction(mutate + audit) shape of
`freeze`.
"""

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from operations_ledger import Ledger

from operations_domain.models import Shift, ShiftStatus

_FREEZE_CHAIN = ["identity", "permission", "freeze", "audit"]
_CLOSE_CHAIN = ["identity", "permission", "close", "audit"]

# Conditions from freeze-policy.yaml this service can actually verify today.
_CHECKABLE_PREREQUISITES = {"shift_closed"}
# Conditions the policy names but this repo has no model for yet.
_UNIMPLEMENTED_PREREQUISITES = {"report_approved", "open_handover_items_linked"}


class ShiftService:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def close(self, shift_id, principal: Principal) -> Shift:
        shift = self.ledger.get_shift(shift_id)

        require_action(principal, "shift.close")

        if shift.status == ShiftStatus.FROZEN:
            # Mirrors freeze's bad-state mapping: a state-transition conflict
            # is a 409, not a permission or validation error.
            raise CvfDenied(
                control="close",
                reason=f"cannot close: shift is {shift.status}",
                http_status=409,
            )

        before = str(shift.status)

        # Unit-of-work: the close itself and its audit record commit or roll
        # back together, same as freeze/create_task/transition (P-FIX-2).
        with self.ledger.transaction() as unit:
            closed = self.ledger.close_shift(shift_id, unit=unit)

            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="shift.close",
                    record_type="Shift",
                    record_id=str(shift_id),
                    control_chain=_CLOSE_CHAIN,
                    before_state=before,
                    after_state=str(closed.status),
                ),
                unit=unit,
            )
        return closed

    def freeze(
        self,
        shift_id,
        principal: Principal,
        *,
        override_unimplemented_prerequisites: bool = False,
        override_reason: str | None = None,
    ) -> Shift:
        shift = self.ledger.get_shift(shift_id)

        require_action(principal, "shift.freeze")

        if shift.status == ShiftStatus.FROZEN:
            return shift  # idempotent: already frozen, nothing to re-check.

        if shift.status != ShiftStatus.CLOSED:
            raise CvfDenied(
                control="freeze",
                reason=(
                    f"freeze requires shift_closed; shift is {shift.status}. "
                    "Close the shift before freezing."
                ),
                http_status=409,
            )

        if not override_unimplemented_prerequisites:
            raise CvfDenied(
                control="freeze",
                reason=(
                    "freeze-policy.yaml also requires report_approved and "
                    "open_handover_items_linked, which have no implemented "
                    "model yet (see EXECUTION_ROADMAP.md P2-D/P5-A). Freezing "
                    "without them requires an explicit "
                    "override_unimplemented_prerequisites=true and a reason."
                ),
                http_status=422,
            )
        if not override_reason or not override_reason.strip():
            raise CvfDenied(
                control="freeze",
                reason="override_reason is required when overriding unimplemented prerequisites",
                http_status=422,
            )

        # Unit-of-work: the freeze itself and both audit records (freeze +
        # override) commit or roll back together (P-FIX-2 / High Finding #5).
        with self.ledger.transaction() as unit:
            frozen = self.ledger.freeze_shift(shift_id, unit=unit)

            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="shift.freeze",
                    record_type="Shift",
                    record_id=str(shift_id),
                    control_chain=_FREEZE_CHAIN,
                    before_state=str(ShiftStatus.CLOSED),
                    after_state=str(frozen.status),
                ),
                unit=unit,
            )
            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="shift.freeze_override_unimplemented_prerequisites",
                    record_type="Shift",
                    record_id=str(shift_id),
                    control_chain=_FREEZE_CHAIN,
                    before_state=None,
                    after_state=f"report_approved,open_handover_items_linked not checked: {override_reason.strip()}",
                ),
                unit=unit,
            )
        return frozen
