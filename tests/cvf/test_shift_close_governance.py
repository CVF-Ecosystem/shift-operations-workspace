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
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.shift_service import ShiftService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import Shift, ShiftStatus
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers


def _operator():
    return Principal(user_id="op1", role="operator")


def _supervisor():
    return Principal(user_id="sup1", role="shift_supervisor")


def _sql_ledger(tmp_path, name="close.sqlite3"):
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _client_for(ledger):
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)


def _clear_overrides():
    app.dependency_overrides.pop(get_ledger, None)


# --- HTTP-level identity/permission boundary ---------------------------------


def test_anonymous_close_is_rejected_not_200():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    client = _client_for(ledger)
    try:
        resp = client.post(f"/shifts/{shift.shift_id}/close")
        assert resp.status_code == 401, resp.text

        fetched = ledger.get_shift(shift.shift_id)
        assert fetched.status == ShiftStatus.OPEN, "anonymous close must not mutate the shift"
        assert ledger.audit_entries_for(str(shift.shift_id)) == []
    finally:
        _clear_overrides()


def test_insufficient_role_close_is_rejected():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    client = _client_for(ledger)
    try:
        resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            headers=auth_headers("v1", "viewer"),
        )
        assert resp.status_code == 403, resp.text

        fetched = ledger.get_shift(shift.shift_id)
        assert fetched.status == ShiftStatus.OPEN
    finally:
        _clear_overrides()


def test_valid_operator_close_succeeds_over_http():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    client = _client_for(ledger)
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
        _clear_overrides()


# --- audit content -------------------------------------------------------


def test_successful_close_produces_audit_record_with_expected_fields():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    closed = ShiftService(ledger).close(shift.shift_id, _operator())
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
    shift = _new_shift(ledger)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).close(shift.shift_id, _operator())

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.OPEN, "shift must remain OPEN when audit write fails"


def test_close_rolls_back_when_audit_fails_sql(tmp_path):
    # Real SQLite engine (not a mocked DB layer) - the point is proving real
    # transactional rollback via SqlLedger.transaction(), matching the pattern
    # already established in tests/cvf/test_atomic_mutation_audit.py.
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).close(shift.shift_id, _operator())

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.OPEN, "shift must remain OPEN when audit write fails"


# --- state-transition guard: cannot close an already-frozen shift -----------


def test_cannot_close_already_frozen_shift_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, _operator())
    ShiftService(ledger).freeze(
        shift.shift_id, _supervisor(),
        override_unimplemented_prerequisites=True, override_reason="test",
    )

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, _operator())
    assert exc.value.http_status == 409


def test_cannot_close_already_frozen_shift_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, _operator())
    ShiftService(ledger).freeze(
        shift.shift_id, _supervisor(),
        override_unimplemented_prerequisites=True, override_reason="test",
    )

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, _operator())
    assert exc.value.http_status == 409


# --- end-to-end: freeze only succeeds after a GOVERNED close ----------------


def test_full_sequence_create_governed_close_then_freeze_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)

    closed = ShiftService(ledger).close(shift.shift_id, _operator())
    assert closed.status == ShiftStatus.CLOSED

    frozen = ShiftService(ledger).freeze(
        shift.shift_id, _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="Report/handover model not implemented yet (P2-D/P5-A)",
    )
    assert frozen.status == ShiftStatus.FROZEN

    entries = ledger.audit_entries_for(str(shift.shift_id))
    actions = [e.action for e in entries]
    assert "shift.close" in actions
    assert "shift.freeze" in actions
    # Existing override-audit behavior for freeze is unchanged by this tranche.
    assert "shift.freeze_override_unimplemented_prerequisites" in actions


def test_full_sequence_create_governed_close_then_freeze_over_http():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    client = _client_for(ledger)
    try:
        close_resp = client.post(
            f"/shifts/{shift.shift_id}/close",
            headers=auth_headers("op1", "operator"),
        )
        assert close_resp.status_code == 200, close_resp.text
        assert close_resp.json()["status"] == "CLOSED"

        freeze_resp = client.post(
            f"/shifts/{shift.shift_id}/freeze",
            json={
                "override_unimplemented_prerequisites": True,
                "override_reason": "Report/handover model not implemented yet (P2-D/P5-A)",
            },
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert freeze_resp.status_code == 200, freeze_resp.text
        assert freeze_resp.json()["status"] == "FROZEN"
    finally:
        _clear_overrides()


def test_anonymous_close_no_longer_bypasses_freeze_prerequisite():
    """Regression test for the exact gap the second independent review found:
    an anonymous close must not exist at all, so it cannot silently satisfy
    freeze's shift_closed prerequisite."""
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    client = _client_for(ledger)
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
        _clear_overrides()


def test_old_header_impersonation_no_longer_grants_any_identity():
    """P2-B regression proof: the original vulnerability class was that
    setting X-User-Id/X-User-Role headers alone was trusted as identity, with
    no verification at all. Confirms that claiming even the highest role
    (authorized_executive) via those headers, with no Authorization bearer
    token, is refused (401) exactly like an anonymous request - the headers
    now carry no authority whatsoever."""
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    client = _client_for(ledger)
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
        _clear_overrides()
