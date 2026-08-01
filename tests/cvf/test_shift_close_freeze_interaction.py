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
    report = svc.submit_review(report.report_id, operator())
    seed_assignment(ledger, shift.shift_id, "sup3", "shift_supervisor")
    approval_service.create_approval_receipt(
        ledger, Principal(user_id="sup3", role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    return svc.approve(report.report_id, supervisor())


# --- state-transition guard: cannot close an already-frozen shift -----------


def test_cannot_close_already_frozen_shift_in_memory():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, operator())
    make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)
    ShiftService(ledger).freeze(shift.shift_id, supervisor())

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, operator())
    assert exc.value.http_status == 409


def test_cannot_close_already_frozen_shift_sql(tmp_path):
    ledger = sql_ledger(tmp_path)
    shift = new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, operator())
    make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)
    ShiftService(ledger).freeze(shift.shift_id, supervisor())

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, operator())
    assert exc.value.http_status == 409


# --- end-to-end: freeze only succeeds after a GOVERNED close ----------------


def test_full_sequence_create_governed_close_then_freeze_in_memory():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)

    closed = ShiftService(ledger).close(shift.shift_id, operator())
    assert closed.status.value == "CLOSED"

    make_ready_handover(ledger, shift)
    report = _make_ready_report(ledger, shift)
    frozen = ShiftService(ledger).freeze(shift.shift_id, supervisor())
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
            headers=auth_headers("op1", "operator"),
        )
        assert close_resp.status_code == 200, close_resp.text
        assert close_resp.json()["status"] == "CLOSED"

        make_ready_handover(ledger, shift)
        _make_ready_report(ledger, shift)

        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={},
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
        anon_resp = client.post(f"/shifts/{shift.shift_id}/close")
        assert anon_resp.status_code == 401

        # Shift is still OPEN, so freeze must still be rejected (409) even
        # with a valid supervisor principal - the shift_closed prerequisite
        # was never actually satisfied.
        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={},
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 409, freeze_resp.text
    finally:
        clear_overrides()


def test_legacy_override_fields_refused_over_http():
    """SPEC R19: attempting the retired override over HTTP is 422, never
    silently accepted or ignored."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        client.post(f"/shifts/{shift.shift_id}/close", headers=auth_headers("op1", "operator"))
        make_ready_handover(ledger, shift)
        _make_ready_report(ledger, shift)

        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={"override_unimplemented_prerequisites": True, "override_reason": "x"},
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 422, freeze_resp.text
    finally:
        clear_overrides()
