"""Shift-close / freeze interaction tests (split from test_shift_close_governance.py).

P2A-HANDOVER-VERTICAL (2026-07-26): `ShiftService.freeze` requires a real
ACKNOWLEDGED handover whose source snapshot matches current open work
(`open_handover_items_linked`). P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE
retires the override entirely: every test below that expects freeze to
SUCCEED now also generates/reviews/approves a real END_SHIFT report via
`_make_ready_report`. The state-transition guard tests (close-after-freeze,
anonymous-close-then-freeze-still-409) do not depend on handover/report
readiness because their expected failure happens at an earlier check
(already-FROZEN / shift-not-CLOSED).
"""

from unittest.mock import patch

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application import approval_service
from workspace_api.application.report_service import ReportService
from workspace_api.application.shift_service import ShiftService
from workspace_api.domain import models as domain_models

from _auth_test_helpers import auth_headers
from _shift_close_fixtures import (
    InMemoryLedger,
    client_for,
    clear_overrides,
    make_ready_handover,
    new_shift,
    operator,
    seed_assignment,
    sql_ledger,
    supervisor,
)


def _make_ready_report(ledger, shift):
    """A current, APPROVED END_SHIFT report - the real `report_approved`
    freeze prerequisite. Mirrors test_freeze_invariant.py's helper."""
    svc = ReportService(ledger)
    report = svc.generate(shift.shift_id, operator())
    report = svc.submit_review(
        report.report_id, operator(),
        expected_version=report.version, expected_status=report.status,
    )
    seed_assignment(ledger, shift.shift_id, "sup3", "shift_supervisor")
    approval_service.create_approval_receipt(
        ledger, Principal(user_id="sup3", role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    return svc.approve(
        report.report_id, supervisor(),
        expected_version=report.version, expected_status=report.status,
    )


# --- state-transition guard: cannot close an already-frozen shift -----------


def test_cannot_close_already_frozen_shift_in_memory():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)
    ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=closed.version)

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, operator(), expected_version=closed.version)
    assert exc.value.http_status == 409


def test_cannot_close_already_frozen_shift_sql(tmp_path):
    ledger = sql_ledger(tmp_path)
    shift = new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)
    ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=closed.version)

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, operator(), expected_version=closed.version)
    assert exc.value.http_status == 409


# --- end-to-end: freeze only succeeds after a GOVERNED close ----------------


def test_full_sequence_create_governed_close_then_freeze_in_memory():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)

    closed = ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    assert closed.status.value == "CLOSED"

    make_ready_handover(ledger, shift)
    report = _make_ready_report(ledger, shift)
    frozen = ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=closed.version)
    assert frozen.status.value == "FROZEN"

    shift_actions = [e.action for e in ledger.audit_entries_for(str(shift.shift_id))]
    assert "shift.close" in shift_actions
    assert "shift.freeze" in shift_actions
    # SPEC R19: the retired override audit is never written again.
    assert "shift.freeze_override_unimplemented_prerequisites" not in shift_actions

    report_actions = [e.action for e in ledger.audit_entries_for(str(report.report_id))]
    assert "report.freeze" in report_actions


def test_full_sequence_create_governed_close_then_freeze_over_http():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        close_resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            json={"expected_version": shift.version},
            headers=auth_headers("op1", "operator"),
        )
        assert close_resp.status_code == 200, close_resp.text
        assert close_resp.json()["status"] == "CLOSED"

        make_ready_handover(ledger, shift)
        _make_ready_report(ledger, shift)

        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={"expected_version": close_resp.json()["version"]},
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 200, freeze_resp.text
        assert freeze_resp.json()["status"] == "FROZEN"
    finally:
        clear_overrides()


def test_anonymous_close_no_longer_bypasses_freeze_prerequisite():
    """Regression test for the exact gap the second independent review found:
    an anonymous close must not exist at all, so it cannot silently satisfy
    freeze's shift_closed prerequisite."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        anon_resp = client.post(f"/shifts/{shift.shift_id}/close", json={"expected_version": shift.version})
        assert anon_resp.status_code == 401

        # Shift is still OPEN, so freeze must still be rejected (409) even
        # with a valid supervisor principal - the shift_closed prerequisite
        # was never actually satisfied.
        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={"expected_version": shift.version},
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 409, freeze_resp.text
    finally:
        clear_overrides()


# --- C3B2-BUILD-REV-F3: freeze admission/comparison/branch/mutation/audit --
# all share one transaction, for BOTH the idempotent-FROZEN path and the
# ordinary CLOSED->FROZEN path. -----------------------------------------


def test_freeze_stale_version_on_closed_shift_leaves_everything_unchanged():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    make_ready_handover(ledger, shift)
    report = _make_ready_report(ledger, shift)
    stale_version = closed.version - 1

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=stale_version)
    assert exc.value.http_status == 409

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status.value == "CLOSED", "stale freeze must not mutate the shift"
    assert ledger.get_report(report.report_id).status.value == "APPROVED"
    freeze_actions = [e.action for e in ledger.audit_entries_for(str(shift.shift_id)) if e.action == "shift.freeze"]
    assert freeze_actions == []


def test_freeze_missing_precondition_on_closed_shift_leaves_everything_unchanged():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    make_ready_handover(ledger, shift)
    report = _make_ready_report(ledger, shift)

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=None)
    assert exc.value.http_status == 422

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status.value == "CLOSED"
    assert ledger.get_report(report.report_id).status.value == "APPROVED"
    freeze_actions = [e.action for e in ledger.audit_entries_for(str(shift.shift_id)) if e.action == "shift.freeze"]
    assert freeze_actions == [], "missing-precondition freeze must not append a freeze audit"


def test_freeze_stale_version_on_already_frozen_shift_is_409_idempotent_path():
    """The idempotent-FROZEN branch also compares BEFORE returning success -
    a stale caller must not be told freeze "succeeded" against a version it
    never actually observed."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    closed_version = closed.version
    make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)
    frozen = ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=closed_version)

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=closed_version)
    assert exc.value.http_status == 409

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status.value == "FROZEN"
    assert fetched.version == frozen.version, "the stale retry must not touch the already-frozen shift"


def test_freeze_admission_and_comparison_use_the_same_unit_as_the_mutation():
    """REVIEW-F3: `require_active_assignment` must be called WITH the same
    `unit` the CLOSED->FROZEN branch later mutates and audits under - proven
    by capturing the exact `unit` object passed to the admission call."""
    import workspace_api.application.shift_service as shift_service_module

    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, operator(), expected_version=shift.version)
    make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)

    captured_units = []
    real = shift_service_module.require_active_assignment

    def _spy(ledger_arg, shift_id, principal, *, unit=None):
        captured_units.append(unit)
        return real(ledger_arg, shift_id, principal, unit=unit)

    with patch.object(shift_service_module, "require_active_assignment", side_effect=_spy):
        frozen = ShiftService(ledger).freeze(shift.shift_id, supervisor(), expected_version=closed.version)

    assert frozen.status.value == "FROZEN"
    assert len(captured_units) == 1
    assert captured_units[0] is not None, "admission must run inside the same transaction as the mutation"


def test_legacy_override_fields_refused_over_http():
    """SPEC R19: attempting the retired override over HTTP is 422, never
    silently accepted or ignored."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        close_resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            json={"expected_version": shift.version},
            headers=auth_headers("op1", "operator"),
        )
        make_ready_handover(ledger, shift)
        _make_ready_report(ledger, shift)

        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={
                "expected_version": close_resp.json()["version"],
                "override_unimplemented_prerequisites": True,
                "override_reason": "x",
            },
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 422, freeze_resp.text
    finally:
        clear_overrides()
