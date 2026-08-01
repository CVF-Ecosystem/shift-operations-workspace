"""Report application service (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).

Owns SPEC R5 (generation) and R10-R18 (lifecycle/versioning/approval)
Report commands. Freeze readiness/freeze itself lives in ``report_freeze.py``
(consumed by ``ShiftService.freeze``), not here - mirrors how
``handover_service.assert_freeze_ready`` is separate from Handover's own
create/review/acknowledge actions.

F6 repair: every command below uses ``ledger.report_mutation_transaction()``,
not the generic ``transaction()`` - each one reads then decides then writes
the same (shift_id, report_type) current-report state a concurrent call
could race, so on SQLite it reserves the write lock from open (BEGIN
IMMEDIATE), scoped to only this call. Every OTHER vertical's own reads/
writes keep using plain ``transaction()`` unaffected.

Governed chains (ADR Decision 4; REVIEW-F5 fixed the exact order below):

* generate        -- identity -> permission -> closed-shift -> snapshot -> audit.
* submit_review   -- identity -> permission -> lookup -> assignment ->
                      precondition -> lifecycle -> revalidate -> audit.
* approve         -- identity -> permission -> lookup -> assignment ->
                      precondition -> lifecycle -> R2 approval -> audit.
* create_successor -- identity -> coarse permission -> lookup -> exact
                      permission -> assignment -> precondition -> lifecycle
                      -> reason (if revoking) -> new version -> audit.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from cvf_runtime.approval import assert_approval_satisfied
from cvf_runtime.audit import AuditRecord
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import CvfProfile, load_profile
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_report_transition
from operations_domain.models import Report, ReportStatus, ShiftStatus
from workspace_api.application import approval_service, report_snapshot
from workspace_api.application.assignment_scope import require_active_assignment
from workspace_api.application.mutation_preconditions import (
    assert_status_precondition,
    assert_version_precondition,
)

_RECORD_TYPE = "Report"
_APPROVE_ACTION = "report.approve"

_GENERATE_CHAIN = ["identity", "permission", "snapshot", "create", "audit"]
_SUBMIT_REVIEW_CHAIN = ["identity", "permission", "lifecycle", "snapshot", "audit"]
_APPROVE_CHAIN = ["identity", "permission", "lifecycle", "snapshot", "approval", "audit"]
_REGENERATE_CHAIN = ["identity", "permission", "snapshot", "version", "audit"]
_REVOKE_CHAIN = ["identity", "permission", "approval", "snapshot", "version", "audit"]

_MAX_REASON_LEN = 1000

def _gather_snapshot_inputs(ledger: Ledger, shift_id: UUID, *, unit=None) -> dict:
    events = report_snapshot.filter_eligible_events(ledger.list_events_for_shift(shift_id, unit=unit))
    event_ids = {e.event_id for e in events}
    all_corrections: list = []
    for event_id in event_ids:
        all_corrections.extend(ledger.corrections_for(event_id, unit=unit))
    corrections = report_snapshot.filter_corrections_for_events(all_corrections, event_ids)
    tasks = ledger.list_tasks_for_shift(shift_id, unit=unit)
    customer_requests = ledger.list_customer_requests_for_shift(shift_id, unit=unit)
    incidents = ledger.list_incidents_for_shift(shift_id, unit=unit)
    handovers = ledger.list_handovers_for_shift(shift_id, unit=unit)
    return {
        "events": report_snapshot.sort_events(events),
        "corrections": report_snapshot.sort_corrections(corrections),
        "tasks": report_snapshot.sort_tasks(tasks),
        "customer_requests": report_snapshot.sort_customer_requests(customer_requests),
        "incidents": report_snapshot.sort_incidents(incidents),
        "handovers": report_snapshot.sort_handovers(handovers),
    }


def build_current_content(ledger: Ledger, shift_id: UUID, *, unit=None):
    """SPEC R9: recompute the exact R6-R8 snapshot from CURRENT persisted
    truth - used by generate (initial) and every revalidation call site
    (submit-review, approve, freeze)."""
    inputs = _gather_snapshot_inputs(ledger, shift_id, unit=unit)
    return report_snapshot.build_snapshot(shift_id=shift_id, **inputs)


def _assert_revalidated(ledger: Ledger, report: Report, *, unit=None) -> None:
    fresh = build_current_content(ledger, report.shift_id, unit=unit)
    if fresh.snapshot_digest != report.content.snapshot_digest:
        raise CvfDenied(
            control="lifecycle",
            reason=(
                "report snapshot is stale: current operational truth no longer "
                "matches the persisted content; create a new version instead"
            ),
            http_status=409,
        )


class ReportService:
    def __init__(self, ledger: Ledger, profile: CvfProfile | None = None):
        self.ledger = ledger
        self.profile = profile or load_profile()

    def generate(self, shift_id: UUID, principal: Principal) -> Report:
        require_action(principal, "report.generate")

        with self.ledger.report_mutation_transaction() as unit:
            require_active_assignment(self.ledger, shift_id, principal, unit=unit)
            shift = self.ledger.get_shift(shift_id, unit=unit)
            if shift.status != ShiftStatus.CLOSED:
                raise CvfDenied(
                    control="lifecycle",
                    reason=f"report generation requires a CLOSED shift; shift is {shift.status}",
                    http_status=409,
                )
            existing = self.ledger.get_current_report(shift_id, report_snapshot.REPORT_TYPE, unit=unit)
            if existing is not None:
                raise CvfDenied(
                    control="lifecycle",
                    reason="a current END_SHIFT report already exists for this shift; use successor generation",
                    http_status=409,
                )

            content = build_current_content(self.ledger, shift_id, unit=unit)
            report = Report(
                shift_id=shift_id,
                generated_from_cutoff=datetime.now(timezone.utc),
                content=content,
            )
            stored = self.ledger.add_report(report, unit=unit)
            self._audit(principal, "report.generate", stored.report_id, _GENERATE_CHAIN, None, str(stored.status), unit=unit)
        return stored

    def submit_review(
        self,
        report_id: UUID,
        principal: Principal,
        *,
        expected_version: int | None = None,
        expected_status: ReportStatus | None = None,
    ) -> Report:
        require_action(principal, "report.submit_review")

        with self.ledger.report_mutation_transaction() as unit:
            report = self.ledger.get_report(report_id, unit=unit)
            require_active_assignment(self.ledger, report.shift_id, principal, unit=unit)
            # REVIEW-F5: admission, THEN precondition, THEN _assert_current/
            # lifecycle - Report submit/approve are status-only (content
            # `version` never increments).
            assert_version_precondition(
                control="lifecycle", expected_version=expected_version, current_version=report.version
            )
            assert_status_precondition(
                control="lifecycle", expected_status=expected_status, current_status=report.status
            )
            self._assert_current(report)
            if report.status != ReportStatus.DRAFT:
                raise CvfDenied(control="lifecycle", reason=f"report is {report.status}, expected DRAFT", http_status=409)
            assert_report_transition(report.status, ReportStatus.IN_REVIEW)
            _assert_revalidated(self.ledger, report, unit=unit)

            before = str(report.status)
            report.status = ReportStatus.IN_REVIEW
            stored = self.ledger.put_report(report, unit=unit)
            self._audit(principal, "report.submit_review", report_id, _SUBMIT_REVIEW_CHAIN, before, str(stored.status), unit=unit)
        return stored

    def approve(
        self,
        report_id: UUID,
        principal: Principal,
        *,
        expected_version: int | None = None,
        expected_status: ReportStatus | None = None,
    ) -> Report:
        # REVIEW-F5: authority before target lookup - never a 404-vs-403 oracle.
        require_action(principal, "report.approve")

        with self.ledger.report_mutation_transaction() as unit:
            report = self.ledger.get_report(report_id, unit=unit)
            require_active_assignment(self.ledger, report.shift_id, principal, unit=unit)
            # REVIEW-F5: admission, THEN precondition, THEN _assert_current.
            assert_version_precondition(
                control="lifecycle", expected_version=expected_version, current_version=report.version
            )
            assert_status_precondition(
                control="lifecycle", expected_status=expected_status, current_status=report.status
            )
            self._assert_current(report)
            if report.status != ReportStatus.IN_REVIEW:
                raise CvfDenied(control="lifecycle", reason=f"report is {report.status}, expected IN_REVIEW", http_status=409)
            assert_report_transition(report.status, ReportStatus.APPROVED)
            _assert_revalidated(self.ledger, report, unit=unit)

            risk_class = "R2"
            receipts = approval_service.collect_receipts_for(
                self.ledger, record_type=_RECORD_TYPE, record_id=report_id, action=_APPROVE_ACTION,
                target_version=report.version, risk_class=risk_class,
                payload_digest=report.content.snapshot_digest, unit=unit,
            )
            authority_for = approval_service.authority_for_factory(self.ledger, unit=unit)
            assert_approval_satisfied(
                profile=self.profile, risk_class=risk_class, confirmer=principal,
                receipts=receipts, authority_for=authority_for,
            )

            before = str(report.status)
            report.status = ReportStatus.APPROVED
            stored = self.ledger.put_report(report, unit=unit)
            self._audit(principal, _APPROVE_ACTION, report_id, _APPROVE_CHAIN, before, str(stored.status), unit=unit)
        return stored

    def create_successor(
        self,
        report_id: UUID,
        principal: Principal,
        *,
        reason: str | None = None,
        expected_version: int | None = None,
        expected_status: ReportStatus | None = None,
    ) -> Report:
        # REVIEW-F5: overloaded route - the EXACT action (generate vs
        # revoke_approval) depends on stored status, not yet known. Coarse
        # "report.generate" (the lower of the two role bars) is the floor
        # checked here so an unauthorized nonexistent target is 403, never an
        # existence-revealing 404; the exact action is re-checked below.
        require_action(principal, "report.generate")

        with self.ledger.report_mutation_transaction() as unit:
            previous = self.ledger.get_report(report_id, unit=unit)

            is_revocation = previous.status == ReportStatus.APPROVED
            require_action(principal, "report.revoke_approval" if is_revocation else "report.generate")

            require_active_assignment(self.ledger, previous.shift_id, principal, unit=unit)
            # REVIEW-F5: admission, THEN precondition (vs the predecessor
            # being superseded), THEN _assert_current/lifecycle/reason.
            assert_version_precondition(
                control="lifecycle", expected_version=expected_version, current_version=previous.version
            )
            assert_status_precondition(
                control="lifecycle", expected_status=expected_status, current_status=previous.status
            )
            self._assert_current(previous)

            if previous.status == ReportStatus.FROZEN:
                raise CvfDenied(control="lifecycle", reason="cannot regenerate a FROZEN report", http_status=409)
            shift = self.ledger.get_shift(previous.shift_id, unit=unit)
            if shift.status == ShiftStatus.FROZEN:
                raise CvfDenied(control="freeze", reason="cannot regenerate a report for a FROZEN shift", http_status=409)

            if is_revocation:
                trimmed = (reason or "").strip()
                if not (1 <= len(trimmed) <= _MAX_REASON_LEN):
                    raise CvfDenied(
                        control="lifecycle",
                        reason="reason is required (1-1000 trimmed characters) to regenerate an APPROVED report",
                        http_status=422,
                    )
            else:
                if previous.status not in (ReportStatus.DRAFT, ReportStatus.IN_REVIEW):
                    raise CvfDenied(control="lifecycle", reason=f"cannot regenerate report in status {previous.status}", http_status=409)

            content = build_current_content(self.ledger, previous.shift_id, unit=unit)
            successor = Report(
                shift_id=previous.shift_id,
                version=previous.version + 1,
                generated_from_cutoff=datetime.now(timezone.utc),
                content=content,
            )
            stored = self.ledger.create_report_successor(report_id, successor, unit=unit)

            action = "report.revoke_approval" if is_revocation else "report.regenerate"
            chain = _REVOKE_CHAIN if is_revocation else _REGENERATE_CHAIN
            after_summary = f"version={stored.version} status={stored.status}"
            self._audit(principal, action, report_id, chain, str(previous.status), after_summary, unit=unit)
        return stored

    def _assert_current(self, report: Report) -> None:
        if not report.is_current:
            raise CvfDenied(control="lifecycle", reason=f"report {report.report_id} is not the current version", http_status=409)

    def _audit(self, principal, action, record_id, chain, before, after, *, unit=None) -> None:
        self.ledger.append_audit(
            AuditRecord(
                actor_id=principal.user_id,
                actor_role=principal.role,
                action=action,
                record_type=_RECORD_TYPE,
                record_id=str(record_id),
                control_chain=chain,
                before_state=before,
                after_state=after,
            ),
            unit=unit,
        )
