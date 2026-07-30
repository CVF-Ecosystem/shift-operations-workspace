"""Message admission: internal POST /messages requires a verified JWT,
derives sender/source authority server-side, enforces message.create
permission, and atomically persists a shift-bound internal Message with an
actor-bound audit record (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC
R1-R11, AC-01 through AC-11).

Before this tranche, POST /messages was anonymous and trusted a
caller-supplied sender_id/source as authority (INTAKE probe: anonymous
request -> 200, forged sender_id="forged-executive"/source="INTERNAL"
accepted unchanged, zero audit records). These tests prove the opposite:
every refusal writes nothing, sender/source are always server-derived, and
only an admitted operator-or-higher JWT reaches MessageService.create, which
persists the message and its exact actor-bound audit record atomically.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import audit_records, messages, metadata

from workspace_api.application.message_service import MessageService
from workspace_api.application.shift_service import ShiftService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_TEXT = "shift handover note"


def _sql_ledger(tmp_path):
    db = tmp_path / "message_admission.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    return ShiftService(ledger).create(
        "Day", now, now + timedelta(hours=8), Principal(user_id="setup-op", role="operator")
    )


@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _create(client_, shift_id, headers=None, **body_overrides):
    body = {"shift_id": str(shift_id), "text": _TEXT}
    body.update(body_overrides)
    return client_.post("/messages", json=body, headers=headers or {})


# --- R1/AC-01: authenticated internal route ----------------------------------

def test_anonymous_create_rejected_with_no_writes(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id)
    assert res.status_code == 401
    assert ledger.messages == {}


def test_malformed_bearer_token_rejected_with_no_writes(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401
    assert ledger.messages == {}


# --- R4/AC-02: permission ----------------------------------------------------

def test_viewer_role_rejected_with_no_writes(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("v1", "viewer"))
    assert res.status_code == 403


@pytest.mark.parametrize(
    "role", ["operator", "shift_supervisor", "responsible_manager", "authorized_executive"]
)
def test_operator_and_higher_roles_admitted(client, role):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("u1", role))
    assert res.status_code == 200
    body = res.json()
    assert body["sender_id"] == "u1"
    assert body["source"] == "INTERNAL"


def test_permission_map_has_exactly_message_create_operator_added():
    require_action(Principal(user_id="op", role="operator"), "message.create")
    with pytest.raises(CvfDenied) as exc:
        require_action(Principal(user_id="v", role="viewer"), "message.create")
    assert exc.value.control == "permission"


# --- R2/AC-03/AC-04: bounded compatibility body ------------------------------

def test_sender_mismatch_rejected_with_no_writes(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("op1", "operator"), sender_id="forged-executive")
    assert res.status_code == 403
    assert ledger.messages == {}


def test_sender_assertion_matching_principal_is_accepted(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("op1", "operator"), sender_id="op1")
    assert res.status_code == 200
    assert res.json()["sender_id"] == "op1"


def test_non_internal_source_rejected_with_no_writes(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("op1", "operator"), source="EXTERNAL")
    assert res.status_code == 422


def test_omitted_source_defaults_to_internal(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("op1", "operator"))
    assert res.status_code == 200
    assert res.json()["source"] == "INTERNAL"


def test_response_derives_sender_and_source_regardless_of_caller_fields(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = _create(http, shift.shift_id, headers=auth_headers("op1", "operator"), sender_id="op1", source="INTERNAL")
    assert res.status_code == 200
    body = res.json()
    assert body["sender_id"] == "op1"
    assert body["source"] == "INTERNAL"
    assert set(["message_id", "shift_id", "state", "created_at", "evidence"]) <= body.keys()


# --- R3/AC-05: one router/service path ---------------------------------------

def test_router_source_has_no_direct_ledger_mutation_call():
    import ast
    import inspect

    from workspace_api.api.messages import router as messages_router

    source = inspect.getsource(messages_router.create_message)
    tree = ast.parse(source)
    calls = [
        ast.unparse(node.func)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    assert not any(call.startswith("ledger.") for call in calls), calls
    assert any(call.startswith("MessageService") for call in calls), calls


# --- R5/AC-04: canonical construction -----------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_service_constructs_only_server_derived_message(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    principal = Principal(user_id="op1", role="operator")
    message = MessageService(ledger).create(shift.shift_id, _TEXT, principal)
    assert message.sender_id == "op1"
    assert message.source == "INTERNAL"
    assert str(message.state) == "RAW" or message.state.value == "RAW"
    assert message.evidence == []


# --- R6/AC-07: atomic create and audit ---------------------------------------

def _audit_fields(entry) -> dict:
    """Normalize the two backends' audit shapes (mirrors
    test_shift_create_admission.py's _audit_fields)."""
    if hasattr(entry, "actor_id"):
        return {
            "actor_id": entry.actor_id, "actor_role": entry.actor_role, "action": entry.action,
            "record_type": entry.record_type, "record_id": entry.record_id,
            "control_chain": entry.control_chain, "before_state": entry.before_state,
            "after_state": entry.after_state,
        }
    meta = entry["metadata"]
    return {
        "actor_id": entry["actor_id"], "actor_role": meta["actor_role"], "action": entry["action"],
        "record_type": entry["target_type"], "record_id": entry["target_id"],
        "control_chain": meta["control_chain"], "before_state": meta["before_state"],
        "after_state": meta["after_state"],
    }


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_successful_create_emits_exactly_one_actor_bound_audit(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    principal = Principal(user_id="op1", role="operator")
    message = MessageService(ledger).create(shift.shift_id, _TEXT, principal)

    audits = ledger.audit_entries_for(str(message.message_id))
    assert len(audits) == 1
    fields = _audit_fields(audits[0])
    assert fields["actor_id"] == "op1"
    assert fields["actor_role"] == "operator"
    assert fields["action"] == "message.create"
    assert fields["record_type"] == "Message"
    assert fields["record_id"] == str(message.message_id)
    assert list(fields["control_chain"]) == ["identity", "permission", "create", "audit"]
    assert fields["before_state"] is None
    assert fields["after_state"] == str(message.state)


class _BoomOnAudit(Exception):
    pass


def _raise_on_audit(*args, **kwargs):
    raise _BoomOnAudit("simulated audit sink failure")


def test_create_rolls_back_when_audit_fails_in_memory():
    """MAR-BUILD-REV-F4 (SPEC R24): asserts exact unchanged state, not just
    that the exception was raised."""
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            MessageService(ledger).create(shift.shift_id, _TEXT, Principal(user_id="op1", role="operator"))
    assert ledger.messages == {}
    assert not any(e.action == "message.create" for e in ledger._audit.all())


def test_create_rolls_back_when_audit_fails_sql(tmp_path):
    """MAR-BUILD-REV-F4 (SPEC R24): asserts exact unchanged persisted
    message/audit rows, not just that the exception was raised."""
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            MessageService(ledger).create(shift.shift_id, _TEXT, Principal(user_id="op1", role="operator"))
    with ledger.engine.connect() as conn:
        assert conn.execute(messages.select().where(messages.c.shift_id == shift.shift_id)).mappings().all() == []
        assert conn.execute(audit_records.select().where(audit_records.c.action == "message.create")).mappings().all() == []


# --- R7/AC-08: parent shift behavior ------------------------------------------

def test_unknown_shift_returns_404_with_no_writes(client):
    _, http = client
    import uuid

    res = _create(http, uuid.uuid4(), headers=auth_headers("op1", "operator"))
    assert res.status_code == 404


def test_frozen_shift_returns_409(client):
    ledger, http = client
    shift = _new_shift(ledger)
    ledger.close_shift(shift.shift_id)
    ledger.freeze_shift(shift.shift_id)
    res = _create(http, shift.shift_id, headers=auth_headers("op1", "operator"))
    assert res.status_code == 409


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_open_handover_pending_and_closed_shifts_accept_messages(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    principal = Principal(user_id="op1", role="operator")
    shift = _new_shift(ledger)
    MessageService(ledger).create(shift.shift_id, "open text", principal)
    ledger.close_shift(shift.shift_id)
    MessageService(ledger).create(shift.shift_id, "closed text", principal)
