"""Report freeze readiness/freeze (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).

The real ``report_approved`` freeze prerequisite (ADR Decision 5/SPEC R20),
consumed by ``ShiftService.freeze`` inside the SAME transaction as the real
``open_handover_items_linked`` check (``handover_service.assert_freeze_ready``)
and the Shift freeze mutation - mirrors how that function is a standalone,
ledger-driven readiness check rather than living inside a create/review/
acknowledge action.

``assert_report_freeze_ready`` selects exactly one current END_SHIFT Report,
requires APPROVED, and revalidates its snapshot against fresh R6-R8
derivation. ``freeze_report`` performs the FROZEN transition once readiness
is proven. Both raise ``CvfDenied(control="freeze", ...)`` on any
absence/ambiguity/staleness - never a silent skip, and this check can never
be bypassed by any override (SPEC R19 retires the override entirely).
"""

from __future__ import annotations

from uuid import UUID

from cvf_runtime.errors import CvfDenied
from operations_ledger import Ledger

from operations_domain.lifecycle import assert_report_transition
from operations_domain.models import Report, ReportStatus

from workspace_api.application.report_service import build_current_content

REPORT_TYPE = "END_SHIFT"


def assert_report_freeze_ready(ledger: Ledger, shift_id: UUID, *, unit=None) -> Report:
    """SPEC R20 steps 3-6: load the one current END_SHIFT Report, require it
    to be APPROVED, and recompute+match its complete snapshot/digest. Returns
    the validated Report so the caller can transition it in the SAME
    transaction - never re-reads it a second time (that would reopen a TOCTOU
    window between this check and the actual freeze mutation)."""
    try:
        report = ledger.get_current_report(shift_id, REPORT_TYPE, unit=unit)
    except ValueError as exc:
        # get_current_report raises ValueError itself when more than one
        # current row exists - that is exactly the "multiple current
        # candidates" integrity conflict SPEC R20 requires refusing.
        raise CvfDenied(
            control="freeze",
            reason=f"ambiguous current END_SHIFT report for shift {shift_id}: {exc}",
            http_status=409,
        ) from exc

    if report is None:
        raise CvfDenied(
            control="freeze",
            reason=(
                "freeze requires a current, APPROVED END_SHIFT report "
                "(report_approved) - none exists for this shift"
            ),
            http_status=409,
        )
    if report.status != ReportStatus.APPROVED:
        raise CvfDenied(
            control="freeze",
            reason=f"freeze requires an APPROVED report; current report is {report.status}",
            http_status=409,
        )

    fresh = build_current_content(ledger, shift_id, unit=unit)
    if fresh.snapshot_digest != report.content.snapshot_digest:
        raise CvfDenied(
            control="freeze",
            reason=(
                "the approved report's snapshot no longer matches current "
                "operational truth; a new version must be generated, reviewed "
                "and approved before this shift can freeze"
            ),
            http_status=409,
        )
    return report


def freeze_report(ledger: Ledger, report: Report, *, unit=None) -> Report:
    """Transitions the already-validated current, APPROVED Report to FROZEN.
    Caller (ShiftService.freeze) is responsible for sharing this call's unit
    with the Shift freeze mutation and both audits so all four writes commit
    or roll back together (SPEC R20)."""
    assert_report_transition(report.status, ReportStatus.FROZEN)
    report.status = ReportStatus.FROZEN
    return ledger.put_report(report, unit=unit)


def assert_frozen_shift_report_integrity(ledger: Ledger, shift_id: UUID, *, unit=None) -> None:
    """SPEC R21: an already-FROZEN shift is idempotent ONLY if exactly one
    current END_SHIFT report exists for it and that report is also FROZEN.
    Any other pairing (missing/multiple/non-current-only/non-FROZEN) is an
    integrity conflict, not silent success."""
    try:
        report = ledger.get_current_report(shift_id, REPORT_TYPE, unit=unit)
    except ValueError as exc:
        raise CvfDenied(
            control="freeze",
            reason=f"ambiguous current END_SHIFT report for already-frozen shift {shift_id}: {exc}",
            http_status=409,
        ) from exc
    if report is None or report.status != ReportStatus.FROZEN:
        raise CvfDenied(
            control="freeze",
            reason=(
                "shift is FROZEN but its paired current END_SHIFT report is "
                f"{'missing' if report is None else report.status} - integrity conflict"
            ),
            http_status=409,
        )
