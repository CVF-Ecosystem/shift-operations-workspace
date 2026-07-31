"""Shift create admission: POST /shifts requires a verified JWT, enforces
shift.create permission, and atomically persists the shift with an
actor-bound audit record (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29, SPEC
R1-R6, AC-01 through AC-08). Before this tranche, POST /shifts had no
Depends(get_principal) and called ledger.create_shift directly (INTAKE probe:
ANONYMOUS_SHIFT_CREATE status=200). These tests prove the opposite: every
refusal writes nothing, and only an admitted operator-or-higher JWT reaches
ShiftService.create, which persists the shift and its exact actor-bound audit
record atomically."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.shift_service import ShiftService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import User
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_NAME = "Day"


def _seed_user(ledger, user_id: str, role: str) -> None:
    """SPEC R4: ShiftService.create requires a persisted active creator."""
    ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))


def _window():
    now = datetime.now(timezone.utc)
    return now, now + timedelta(hours=8)


def _sql_ledger(tmp_path):
    db = tmp_path / "shift_create.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


@pytest.fixture
def sql_client(tmp_path):
    """SCR-BUILD-REV-F3 repair: the same HTTP refusal-zero-write proof as
    `client`, but backed by SqlLedger (SQLite) - SPEC R7 requires this on
    both backends, not InMemory only."""
    ledger = _sql_ledger(tmp_path)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _create(client_, headers=None):
    starts_at, ends_at = _window()
    params = {"name": _NAME, "starts_at": starts_at.isoformat(), "ends_at": ends_at.isoformat()}
    return client_.post("/shifts", params=params, headers=headers or {})


# --- R1/AC-01: verified identity ---------------------------------------------


def test_anonymous_create_rejected_with_no_writes(client):
    ledger, http = client
    res = _create(http)
    assert res.status_code == 401
    assert ledger.list_shifts() == []


def test_malformed_bearer_token_rejected_with_no_writes(client):
    ledger, http = client
    res = _create(http, headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401
    assert ledger.list_shifts() == []


def test_anonymous_create_rejected_with_no_writes_sql(sql_client):
    """SCR-BUILD-REV-F3: R7's refusal-zero-write proof, SQLite backend."""
    ledger, http = sql_client
    res = _create(http)
    assert res.status_code == 401
    assert ledger.list_shifts() == []


def test_viewer_role_rejected_with_no_writes_sql(sql_client):
    """SCR-BUILD-REV-F3: R7's refusal-zero-write proof, SQLite backend."""
    ledger, http = sql_client
    res = _create(http, headers=auth_headers("v1", "viewer"))
    assert res.status_code == 403
    assert ledger.list_shifts() == []


# --- R4/AC-02/AC-03: permission --------------------------------------------


def test_viewer_role_rejected_with_no_writes(client):
    ledger, http = client
    res = _create(http, headers=auth_headers("v1", "viewer"))
    assert res.status_code == 403
    assert ledger.list_shifts() == []


@pytest.mark.parametrize(
    "role", ["operator", "shift_supervisor", "responsible_manager", "authorized_executive"]
)
def test_operator_and_higher_roles_admitted(client, role):
    ledger, http = client
    _seed_user(ledger, "u1", role)
    res = _create(http, headers=auth_headers("u1", role))
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == _NAME
    assert body["status"] == "OPEN"
    assert body["version"] == 1


def test_permission_map_has_exactly_shift_create_operator_added():
    require_action(Principal(user_id="op", role="operator"), "shift.create")
    with pytest.raises(CvfDenied) as exc:
        require_action(Principal(user_id="v", role="viewer"), "shift.create")
    assert exc.value.control == "permission"


# --- R2/AC-04: compatibility-preserving request ------------------------------


def test_query_parameters_preserved_and_response_is_canonical_shift(client):
    ledger, http = client
    _seed_user(ledger, "op1", "operator")
    res = _create(http, headers=auth_headers("op1", "operator"))
    assert res.status_code == 200
    body = res.json()
    assert set(["shift_id", "name", "starts_at", "ends_at", "status", "version", "created_at"]) <= body.keys()


def test_invalid_window_returns_422_with_no_writes(client):
    ledger, http = client
    _seed_user(ledger, "op1", "operator")
    now = datetime.now(timezone.utc)
    params = {
        "name": _NAME,
        "starts_at": now.isoformat(),
        "ends_at": (now - timedelta(hours=1)).isoformat(),
    }
    res = http.post("/shifts", params=params, headers=auth_headers("op1", "operator"))
    assert res.status_code == 422
    assert ledger.list_shifts() == []


# --- R3/AC-05: one router-to-service path ------------------------------------


def test_router_source_has_no_direct_ledger_mutation_call():
    import ast
    import inspect

    from workspace_api.api.shifts import router as shifts_router

    source = inspect.getsource(shifts_router.create_shift)
    tree = ast.parse(source)
    calls = [
        ast.unparse(node.func)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    assert not any(call.startswith("ledger.") for call in calls), calls
    assert any(call.startswith("ShiftService") for call in calls), calls


# --- R5/AC-06: canonical construction -----------------------------------------


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_service_constructs_only_server_default_open_version_one_shift(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    shift = ShiftService(ledger).create(_NAME, starts_at, ends_at, Principal(user_id="op1", role="operator"))
    assert shift.status.value == "OPEN"
    assert shift.version == 1
    assert shift.created_at is not None


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_returned_record_equals_persisted_record(tmp_path, name):
    """SCR-BUILD-REV-F3: R7's returned-record-equals-persisted proof on both
    backends explicitly (SQLite's own equivalent lives in
    test_shift_create_sqlite.py; InMemoryLedger previously had no direct
    version of this check)."""
    ledger = dict(_backends(tmp_path))[name]
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    returned = ShiftService(ledger).create(_NAME, starts_at, ends_at, Principal(user_id="op1", role="operator"))

    fetched = ledger.get_shift(returned.shift_id)
    assert fetched.shift_id == returned.shift_id
    assert fetched.name == returned.name == _NAME
    assert fetched.status == returned.status
    assert fetched.version == returned.version == 1


# --- R6/AC-07: atomic create and audit ---------------------------------------


def _audit_fields(entry) -> dict:
    """Normalize the two backends' audit shapes: InMemoryLedger returns the
    real AuditRecord (flat fields); SqlLedger returns a row dict with
    target_type/target_id and the rest nested under metadata (mirrors
    test_atomic_mutation_audit.py's e.action / e["action"] split)."""
    if hasattr(entry, "actor_id"):
        return {
            "actor_id": entry.actor_id, "actor_role": entry.actor_role, "action": entry.action,
            "record_type": entry.record_type, "record_id": entry.record_id, "control_chain": entry.control_chain,
            "before_state": entry.before_state, "after_state": entry.after_state,
        }
    meta = entry["metadata"]
    return {
        "actor_id": entry["actor_id"], "actor_role": meta["actor_role"], "action": entry["action"],
        "record_type": entry["target_type"], "record_id": entry["target_id"], "control_chain": meta["control_chain"],
        "before_state": meta["before_state"], "after_state": meta["after_state"],
    }


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_successful_create_emits_exactly_one_actor_bound_audit(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    principal = Principal(user_id="op1", role="operator")
    shift = ShiftService(ledger).create(_NAME, starts_at, ends_at, principal)

    audits = ledger.audit_entries_for(str(shift.shift_id))
    assert len(audits) == 1
    fields = _audit_fields(audits[0])

    assert fields["actor_id"] == "op1"
    assert fields["actor_role"] == "operator"
    assert fields["action"] == "shift.create"
    assert fields["record_type"] == "Shift"
    assert fields["record_id"] == str(shift.shift_id)
    assert list(fields["control_chain"]) == ["identity", "permission", "create", "audit"]
    assert fields["before_state"] is None
    assert fields["after_state"] == str(shift.status)
# --- R6/AC-08: injected audit failure rolls back -----------------------------


class _BoomOnAudit(Exception):
    pass


def _raise_on_audit(*args, **kwargs):
    raise _BoomOnAudit("simulated audit sink failure")


def test_create_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).create(_NAME, starts_at, ends_at, Principal(user_id="op1", role="operator"))
    assert ledger.list_shifts() == []


def test_create_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    _seed_user(ledger, "op1", "operator")
    starts_at, ends_at = _window()
    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).create(_NAME, starts_at, ends_at, Principal(user_id="op1", role="operator"))
    assert ledger.list_shifts() == []
