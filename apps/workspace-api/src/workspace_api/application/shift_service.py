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
"""

from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from operations_ledger import Ledger

from workspace_api.domain.models import Shift, ShiftStatus

_FREEZE_CHAIN = ["identity", "permission", "freeze", "audit"]

# Conditions from freeze-policy.yaml this service can actually verify today.
_CHECKABLE_PREREQUISITES = {"shift_closed"}
# Conditions the policy names but this repo has no model for yet.
_UNIMPLEMENTED_PREREQUISITES = {"report_approved", "open_handover_items_linked"}


class ShiftService:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

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

        frozen = self.ledger.freeze_shift(shift_id)

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
            )
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
            )
        )
        return frozen
