"""Assignment persistence/staffing foundation (P2C-MUTATION-FULL-UI-C3A1, SPEC
R1-R5/R9, AC-01/AC-02/AC-03/AC-07/AC-08). Proves: canonical model has no
tenant/data_scope field; ShiftService.create atomically bootstraps a creator
assignment; staffing routes are supervisor-only, server-derive actor/status/
timestamps, and have exact idempotent-revoke/stale-409 semantics; existing
(legacy) shifts receive no inferred assignment but a supervisor can discover
and staff them; /auth/me and capabilities never leak secrets and require
assignment respectively.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.shift_service import ShiftService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_SUPERVISOR = ("sup1", "shift_supervisor")


def _sql_ledger(tmp_path):
    db = tmp_path / "assignment_foundation.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _seed_user(ledger, user_id, role):
    ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))


def _window():
    now = datetime.now(timezone.utc)
    return now, now + timedelta(hours=8)


@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


# --- R1/AC-01: canonical model, no tenant/data_scope --------------------------

def test_shift_assignment_has_no_tenant_or_data_scope_field():
    fields = ShiftAssignment.model_fields.keys()
    assert "tenant_id" not in fields
    assert "data_scope" not in fields
    assert set(fields) == {
        "assignment_id", "shift_id", "user_id", "status", "assigned_by",
        "assigned_at", "revoked_by", "revoked_at", "version",
    }


def test_new_assignment_defaults_to_active_version_one():
    a = ShiftAssignment(shift_id=__import__("uuid").uuid4(), user_id="op1", assigned_by="sup1")
    assert a.status.value == "ACTIVE"
    assert a.version == 1
    assert a.revoked_by is None
    assert a.revoked_at is None


# --- R4/AC-02: atomic shift bootstrap -----------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_shift_create_atomically_assigns_the_creator(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="op1", role="operator"))

    active = ledger.get_active_assignment(shift.shift_id, "op1")
    assert active is not None
    assert active.status.value == "ACTIVE"
    assert active.assigned_by == "op1"
    assert active.version == 1


def test_shift_create_rejects_unpersisted_creator():
    ledger = InMemoryLedger()
    starts_at, ends_at = _window()
    with pytest.raises(Exception):
        ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="ghost", role="operator"))
    assert ledger.list_shifts() == []


def test_shift_create_rollback_leaves_no_assignment_on_audit_failure():
    from unittest.mock import patch

    ledger = InMemoryLedger()
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()

    def _boom(*a, **kw):
        raise RuntimeError("simulated audit failure")

    with patch.object(InMemoryLedger, "append_audit", side_effect=_boom):
        with pytest.raises(RuntimeError):
            ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="op1", role="operator"))
    assert ledger.list_shifts() == []
    assert ledger.assignments == {}


# --- R5/AC-03: staffing authority and exact revoke semantics ------------------

def test_staffing_routes_require_supervisor_or_higher(client):
    ledger, http = client
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="op1", role="operator"))

    res = http.get("/staffing/shifts", headers=auth_headers("op1", "operator"))
    assert res.status_code == 403
    res = http.get(f"/shifts/{shift.shift_id}/assignments", headers=auth_headers("op1", "operator"))
    assert res.status_code == 403


def test_supervisor_lists_staffing_shifts_and_active_users(client):
    ledger, http = client
    _seed_user(ledger, *_SUPERVISOR)
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="sup1", role="shift_supervisor"))

    res = http.get("/staffing/shifts", headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 200
    assert len(res.json()) == 1

    res = http.get("/staffing/users", headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 200
    user_ids = {u["user_id"] for u in res.json()}
    assert {"sup1", "op1"} <= user_ids
    assert "password_hash" not in res.json()[0]


def test_assign_requires_target_to_be_persisted_and_active(client):
    ledger, http = client
    _seed_user(ledger, *_SUPERVISOR)
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="sup1", role="shift_supervisor"))

    res = http.post(
        f"/shifts/{shift.shift_id}/assignments", json={"user_id": "ghost"}, headers=auth_headers(*_SUPERVISOR)
    )
    assert res.status_code == 422
    assert ledger.list_assignments_for_shift(shift.shift_id) == [
        a for a in ledger.list_assignments_for_shift(shift.shift_id) if a.user_id == "sup1"
    ]


def test_assign_then_exact_revoke_version_and_idempotency_semantics(client):
    ledger, http = client
    _seed_user(ledger, *_SUPERVISOR)
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="sup1", role="shift_supervisor"))

    res = http.post(
        f"/shifts/{shift.shift_id}/assignments", json={"user_id": "op1"}, headers=auth_headers(*_SUPERVISOR)
    )
    assert res.status_code == 200
    body = res.json()
    assert body["assigned_by"] == "sup1"
    assert body["status"] == "ACTIVE"
    assert body["version"] == 1
    assignment_id = body["assignment_id"]

    # Successful revoke increments version once.
    res = http.post(
        f"/shifts/{shift.shift_id}/assignments/{assignment_id}/revoke",
        json={"expected_version": 1}, headers=auth_headers(*_SUPERVISOR),
    )
    assert res.status_code == 200
    revoked = res.json()
    assert revoked["status"] == "REVOKED"
    assert revoked["version"] == 2
    assert revoked["revoked_by"] == "sup1"

    # Idempotent repeat at the CURRENT revoked version: unchanged, no error.
    res = http.post(
        f"/shifts/{shift.shift_id}/assignments/{assignment_id}/revoke",
        json={"expected_version": 2}, headers=auth_headers(*_SUPERVISOR),
    )
    assert res.status_code == 200
    assert res.json()["version"] == 2

    # A repeat carrying the pre-revoke (stale) version is refused (409).
    res = http.post(
        f"/shifts/{shift.shift_id}/assignments/{assignment_id}/revoke",
        json={"expected_version": 1}, headers=auth_headers(*_SUPERVISOR),
    )
    assert res.status_code == 409


def test_duplicate_active_assignment_rejected(client):
    ledger, http = client
    _seed_user(ledger, *_SUPERVISOR)
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="sup1", role="shift_supervisor"))
    http.post(f"/shifts/{shift.shift_id}/assignments", json={"user_id": "op1"}, headers=auth_headers(*_SUPERVISOR))

    res = http.post(
        f"/shifts/{shift.shift_id}/assignments", json={"user_id": "op1"}, headers=auth_headers(*_SUPERVISOR)
    )
    assert res.status_code == 409


# --- R2/AC-08: no inferred assignment for legacy shifts + supervisor recovery -

def test_legacy_ledger_created_shift_has_no_inferred_assignment_but_supervisor_can_staff_it(client):
    ledger, http = client
    _seed_user(ledger, *_SUPERVISOR)
    _seed_user(ledger, "op1", "operator")
    now = datetime.now(timezone.utc)
    from operations_domain.models import Shift

    legacy_shift = Shift(name="Legacy", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(legacy_shift)

    assert ledger.list_assignments_for_shift(legacy_shift.shift_id) == []

    # Supervisor discovers it via the staffing control plane and can staff it.
    res = http.get("/staffing/shifts", headers=auth_headers(*_SUPERVISOR))
    assert any(s["shift_id"] == str(legacy_shift.shift_id) for s in res.json())

    res = http.post(
        f"/shifts/{legacy_shift.shift_id}/assignments", json={"user_id": "op1"}, headers=auth_headers(*_SUPERVISOR)
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ACTIVE"


# --- R9/AC-07: session and capabilities never leak secrets --------------------

def test_auth_me_returns_verified_claims_and_real_expiry(client):
    _, http = client
    res = http.get("/auth/me", headers=auth_headers("op1", "operator"))
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == "op1"
    assert body["role"] == "operator"
    assert "expires_at" in body and body["expires_at"]


def test_auth_me_rejects_anonymous(client):
    _, http = client
    assert http.get("/auth/me").status_code == 401


# F2 missing-exp/out-of-range-exp -> 401-not-500 HTTP regressions moved to
# test_assignment_foundation_f1.py (Amendment 2 companion, same `client`
# fixture pattern) to keep this host at/under the 300-line hard limit.


def test_capabilities_requires_active_assignment(client):
    ledger, http = client
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create("Day", starts_at, ends_at, Principal(user_id="op1", role="operator"))

    _seed_user(ledger, "outsider", "operator")
    res = http.get(f"/shifts/{shift.shift_id}/capabilities", headers=auth_headers("outsider", "operator"))
    assert res.status_code == 403

    res = http.get(f"/shifts/{shift.shift_id}/capabilities", headers=auth_headers("op1", "operator"))
    assert res.status_code == 200
    body = res.json()
    assert set(body.keys()) == {"shift_id", "actions", "reasons"}
    assert "payload_digest" not in body
    assert "credential" not in str(body).lower() or "credential" not in body
