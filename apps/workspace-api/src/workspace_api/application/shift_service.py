"""Shift application service — makes freeze a real cross-record invariant.

A 2026-07-22 independent review (docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md,
Critical Finding #1) found `freeze_shift` had no identity/permission/prerequisite
check and that mutations on a frozen shift's children were not blocked in
SqlLedger. This service is the single place freeze is requested from, so the
chain cannot be bypassed by calling the ledger directly from a router.

freeze-policy.yaml requires shift_closed, report_approved and
open_handover_items_linked. P2A-HANDOVER-VERTICAL (2026-07-26) made
open_handover_items_linked real. P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE
(SPEC R19-R21) now makes report_approved real too and RETIRES the override
entirely: freeze selects exactly one current, APPROVED END_SHIFT Report,
revalidates its snapshot, and transitions Report+Shift to FROZEN atomically
with both readiness checks and both audits, in one transaction. The two
legacy override fields are still accepted on the wire but ONLY at their
defaults - any attempt to set them is refused with 422 before any mutation.

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

from operations_domain.models import ReportStatus, Shift, ShiftStatus
from workspace_api.application import report_freeze
from workspace_api.application.handover_service import assert_freeze_ready
from workspace_api.domain.models import ShiftAssignment

_FREEZE_CHAIN = ["identity", "permission", "freeze", "audit"]

# F6 repair: only a genuine PostgreSQL serialization failure or deadlock
# (SQLSTATE 40001/40P01) is a transient, safe-to-retry conflict. Any other
# OperationalError (e.g. a real connectivity/driver fault) must propagate to
# the normal internal-error path, never be silently retried and relabeled as
# a controlled 409.
_RETRYABLE_SQLSTATES = {"40001", "40P01"}


def _is_retryable_serialization_conflict(exc: Exception) -> bool:
    sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)
    if sqlstate is not None:
        return sqlstate in _RETRYABLE_SQLSTATES
    # SQLite (and any other backend without a `.orig.sqlstate`) has no
    # SERIALIZABLE-conflict OperationalError to retry in the first place -
    # report_freeze_transaction() already gives it an equivalent single-writer
    # guarantee via transaction()'s lock, so a bare OperationalError there is
    # never this specific, retryable category.
    return False
_CLOSE_CHAIN = ["identity", "permission", "close", "audit"]
_CREATE_CHAIN = ["identity", "permission", "create", "audit"]


class ShiftService:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def create(self, name: str, starts_at, ends_at, principal: Principal) -> Shift:
        """SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29: previously
        POST /shifts called ledger.create_shift(...) directly with no
        identity/permission/audit at all (INTAKE probe: anonymous create ->
        200). This is now the single governed entry point, following the
        same identity -> permission -> transaction(mutate + audit) shape as
        close/freeze. Permission admission happens before opening the
        mutation transaction (SPEC R5) - a refused caller never reaches the
        ledger at all.

        P2C-MUTATION-FULL-UI-C3A1 (SPEC R4): the creator must exist as a
        persisted active user (checked before opening the transaction, same
        admission-before-mutation shape), and atomically gains an ACTIVE
        assignment for the new shift alongside its creation and audit - one
        transaction; any failure rolls back all three. This does NOT make
        existing operational routes assignment-scoped (C3a2).
        """
        require_action(principal, "shift.create")

        creator = self.ledger.get_user_by_id(principal.user_id)
        if creator is None or not creator.is_active:
            raise CvfDenied(
                control="create",
                reason=f"creator is not a persisted active user: {principal.user_id!r}",
                http_status=422,
            )

        shift = Shift(name=name, starts_at=starts_at, ends_at=ends_at)

        with self.ledger.transaction() as unit:
            created = self.ledger.create_shift(shift, unit=unit)

            assignment = ShiftAssignment(
                shift_id=created.shift_id, user_id=principal.user_id, assigned_by=principal.user_id
            )
            self.ledger.add_assignment(assignment, unit=unit)

            self.ledger.append_audit(
                AuditRecord(
                    actor_id=principal.user_id,
                    actor_role=principal.role,
                    action="shift.create",
                    record_type="Shift",
                    record_id=str(created.shift_id),
                    control_chain=_CREATE_CHAIN,
                    before_state=None,
                    after_state=str(created.status),
                ),
                unit=unit,
            )
        return created

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
        # SPEC R19: the legacy override fields are retired. Any attempt to
        # set them (true, or any non-null reason including an empty string)
        # is refused before any read beyond admission - no mutation/audit.
        if override_unimplemented_prerequisites or override_reason is not None:
            raise CvfDenied(
                control="freeze",
                reason=(
                    "override_unimplemented_prerequisites/override_reason are "
                    "deprecated and refused: report_approved is now a real, "
                    "checked freeze prerequisite"
                ),
                http_status=422,
            )

        shift = self.ledger.get_shift(shift_id)

        require_action(principal, "shift.freeze")

        if shift.status == ShiftStatus.FROZEN:
            # SPEC R21: idempotent only if the paired current report is also
            # FROZEN and unambiguous - never a bare pass-through anymore.
            with self.ledger.transaction() as unit:
                report_freeze.assert_frozen_shift_report_integrity(self.ledger, shift_id, unit=unit)
            return shift

        if shift.status != ShiftStatus.CLOSED:
            raise CvfDenied(
                control="freeze",
                reason=(
                    f"freeze requires shift_closed; shift is {shift.status}. "
                    "Close the shift before freezing."
                ),
                http_status=409,
            )

        return self._freeze_transaction(shift_id, principal)

    _MAX_SERIALIZATION_RETRIES = 3

    def _freeze_transaction(self, shift_id, principal: Principal) -> Shift:
        """SPEC R22: re-read CLOSED, real open_handover_items_linked
        readiness, real report_approved readiness (SPEC R20), the Report
        FROZEN transition, the Shift freeze mutation and both actor-bound
        audits all share the SAME SERIALIZABLE (PostgreSQL) transaction -
        any failure, including a serialization conflict, rolls back every
        write together. A concurrent-conflict is retried a bounded number of
        times before surfacing as a controlled 409."""
        from sqlalchemy.exc import OperationalError

        attempt = 0
        while True:
            try:
                with self.ledger.report_freeze_transaction() as unit:
                    fresh = self.ledger.get_shift(shift_id, unit=unit)
                    if fresh.status != ShiftStatus.CLOSED:
                        raise CvfDenied(
                            control="freeze",
                            reason=f"freeze requires shift_closed; shift is {fresh.status}",
                            http_status=409,
                        )
                    assert_freeze_ready(self.ledger, shift_id, unit=unit)
                    report = report_freeze.assert_report_freeze_ready(self.ledger, shift_id, unit=unit)
                    frozen_report = report_freeze.freeze_report(self.ledger, report, unit=unit)
                    frozen = self.ledger.freeze_shift(shift_id, unit=unit)
                    self._append_freeze_audits(principal, shift_id, frozen_report, frozen, unit=unit)
                return frozen
            except OperationalError as exc:
                if not _is_retryable_serialization_conflict(exc):
                    # Not a PostgreSQL serialization/deadlock conflict - a
                    # real, unrelated OperationalError must propagate to the
                    # normal internal-error path, not be retried or relabeled.
                    raise
                attempt += 1
                if attempt > self._MAX_SERIALIZATION_RETRIES:
                    raise CvfDenied(
                        control="freeze",
                        reason=f"freeze aborted after {attempt - 1} serialization retries: concurrent conflict",
                        http_status=409,
                    ) from exc
                continue

    def _append_freeze_audits(self, principal, shift_id, frozen_report, frozen, *, unit) -> None:
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action="report.freeze",
                record_type="Report",
                record_id=str(frozen_report.report_id),
                control_chain=["identity", "permission", "freeze", "audit"],
                before_state=str(ReportStatus.APPROVED),
                after_state=str(frozen_report.status),
            ),
            unit=unit,
        )
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
