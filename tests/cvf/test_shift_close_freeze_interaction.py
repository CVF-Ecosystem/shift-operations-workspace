"""Shift-close / freeze interaction tests (split from test_shift_close_governance.py).

P2A-HANDOVER-VERTICAL (2026-07-26): `ShiftService.freeze` now requires a real
ACKNOWLEDGED handover whose source snapshot matches current open work
(`open_handover_items_linked`), so every test below that expects freeze to
actually SUCCEED first creates/reviews/acknowledges a matching (empty)
handover via `_shift_close_fixtures.make_ready_handover`. The state-transition
guard tests (close-after-freeze, anonymous-close-then-freeze-still-409) do not
themselves depend on handover readiness because their expected failure
happens at an earlier check (already-FROZEN / shift-not-CLOSED).
"""

import pytest

from cvf_runtime.errors import CvfDenied

from workspace_api.application.shift_service import ShiftService

from _auth_test_helpers import auth_headers
from _shift_close_fixtures import (
    InMemoryLedger,
    client_for,
    clear_overrides,
    make_ready_handover,
    new_shift,
    operator,
    sql_ledger,
    supervisor,
)


# --- state-transition guard: cannot close an already-frozen shift -----------


def test_cannot_close_already_frozen_shift_in_memory():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, operator())
    make_ready_handover(ledger, shift)
    ShiftService(ledger).freeze(
        shift.shift_id, supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="Report model not implemented yet (P2-D)",
    )

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, operator())
    assert exc.value.http_status == 409


def test_cannot_close_already_frozen_shift_sql(tmp_path):
    ledger = sql_ledger(tmp_path)
    shift = new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, operator())
    make_ready_handover(ledger, shift)
    ShiftService(ledger).freeze(
        shift.shift_id, supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="Report model not implemented yet (P2-D)",
    )

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
    frozen = ShiftService(ledger).freeze(
        shift.shift_id, supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="Report model not implemented yet (P2-D)",
    )
    assert frozen.status.value == "FROZEN"

    entries = ledger.audit_entries_for(str(shift.shift_id))
    actions = [e.action for e in entries]
    assert "shift.close" in actions
    assert "shift.freeze" in actions
    # Existing override-audit behavior for freeze is unchanged by this tranche
    # (now narrowed to report_approved only - see test_freeze_invariant.py).
    assert "shift.freeze_override_unimplemented_prerequisites" in actions


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

        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={
                "override_unimplemented_prerequisites": True,
                "override_reason": "Report model not implemented yet (P2-D)",
            },
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
            json={
                "override_unimplemented_prerequisites": True,
                "override_reason": "test",
            },
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 409, freeze_resp.text
    finally:
        clear_overrides()
