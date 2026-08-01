"""P-FIX-6: shift.close must be a governed action, not a direct ledger call.

A SECOND independent review (2026-07-22) rejected the P-FIX-5 closure claim
because `POST /shifts/{shift_id}/close` still called `ledger.close_shift()`
directly from the router with no identity/permission/audit check at all.
Probe: create -> 200, anonymous close -> 200 CLOSED, audit_count=0. Because
`ShiftService.freeze` only checks `shift.status == ShiftStatus.CLOSED`, that
anonymous close could silently satisfy freeze's `shift_closed` prerequisite -
a governance bypass on the exact invariant P-FIX-1 was supposed to make real.

These tests exercise the fixed close path end-to-end: HTTP (router ->
ShiftService -> ledger) for the identity/permission/audit boundary, and
service+ledger directly for the atomicity and cross-invariant checks, on both
InMemoryLedger and SqlLedger(SQLite) backends.

P2A-HANDOVER-VERTICAL (2026-07-26): split into this module (pure close
governance, no freeze) plus test_shift_close_freeze_interaction.py (tests
that also call ShiftService.freeze, which now requires a real acknowledged
handover) and the shared `_shift_close_fixtures.py` - the legacy 313-line
single module is retired debt (FILE_SPLIT_DEBT_BASELINE.json), not rehashed.
"""

from unittest.mock import patch

import pytest

from cvf_runtime.errors import CvfDenied
from operations_ledger.sql_ledger import SqlLedger

from workspace_api.application.shift_service import ShiftService
from operations_domain.models import ShiftStatus

from _auth_test_helpers import auth_headers
from _shift_close_fixtures import (
    InMemoryLedger,
    client_for,
    clear_overrides,
    new_shift,
    operator,
    seed_assignment,
    sql_ledger,
)


# --- HTTP-level identity/permission boundary ---------------------------------


def test_anonymous_close_is_rejected_not_200():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        resp = client.post(f"/shifts/{shift.shift_id}/close")
        assert resp.status_code == 401, resp.text

        fetched = ledger.get_shift(shift.shift_id)
        assert fetched.status == ShiftStatus.OPEN, "anonymous close must not mutate the shift"
        assert ledger.audit_entries_for(str(shift.shift_id)) == []
    finally:
        clear_overrides()


def test_insufficient_role_close_is_rejected():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_assignment(ledger, shift.shift_id, "v1", "viewer")
    client = client_for(ledger)
    try:
        resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            headers=auth_headers("v1", "viewer"),
        )
        assert resp.status_code == 403, resp.text

        fetched = ledger.get_shift(shift.shift_id)
        assert fetched.status == ShiftStatus.OPEN
    finally:
        clear_overrides()


def test_valid_operator_close_succeeds_over_http():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            headers=auth_headers("op1", "operator"),
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "CLOSED"

        entries = ledger.audit_entries_for(str(shift.shift_id))
        actions = {e.action for e in entries}
        assert "shift.close" in actions
    finally:
        clear_overrides()


# --- audit content -------------------------------------------------------


def test_successful_close_produces_audit_record_with_expected_fields():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, operator())
    assert closed.status == ShiftStatus.CLOSED

    entries = [e for e in ledger.audit_entries_for(str(shift.shift_id)) if e.action == "shift.close"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry.actor_id == "op1"
    assert entry.actor_role == "operator"
    assert entry.record_type == "Shift"
    assert entry.record_id == str(shift.shift_id)
    assert entry.before_state == "OPEN"
    assert entry.after_state == "CLOSED"
    assert "permission" in entry.control_chain
    assert "audit" in entry.control_chain


# --- atomicity: audit-append failure must not leave the shift CLOSED --------


class _BoomOnAudit(Exception):
    pass


def _raise_on_audit(*args, **kwargs):
    raise _BoomOnAudit("simulated audit sink failure")


def test_close_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).close(shift.shift_id, operator())

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.OPEN, "shift must remain OPEN when audit write fails"


def test_close_rolls_back_when_audit_fails_sql(tmp_path):
    # Real SQLite engine (not a mocked DB layer) - the point is proving real
    # transactional rollback via SqlLedger.transaction(), matching the pattern
    # already established in tests/cvf/test_atomic_mutation_audit.py.
    ledger = sql_ledger(tmp_path)
    shift = new_shift(ledger)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).close(shift.shift_id, operator())

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.OPEN, "shift must remain OPEN when audit write fails"


def test_old_header_impersonation_no_longer_grants_any_identity():
    """P2-B regression proof: the original vulnerability class was that
    setting X-User-Id/X-User-Role headers alone was trusted as identity, with
    no verification at all. Confirms that claiming even the highest role
    (authorized_executive) via those headers, with no Authorization bearer
    token, is refused (401) exactly like an anonymous request - the headers
    now carry no authority whatsoever."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    client = client_for(ledger)
    try:
        resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            headers={"X-User-Id": "op1", "X-User-Role": "authorized_executive"},
        )
        assert resp.status_code == 401, resp.text

        fetched = ledger.get_shift(shift.shift_id)
        assert fetched.status == ShiftStatus.OPEN
        assert ledger.audit_entries_for(str(shift.shift_id)) == []
    finally:
        clear_overrides()
