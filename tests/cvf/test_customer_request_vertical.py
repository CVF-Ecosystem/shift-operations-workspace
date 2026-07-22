"""Customer-request golden vertical: the CVF chain replicated to a fourth
operational domain (P2-A).

Proves the SAME cvf-runtime gates enforce CustomerRequest create/transition,
plus the customer-request-specific status lifecycle, the nullable-shift_id
frozen-shift invariant, and atomic mutation+audit on both ledger backends.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.customer_request_service import CustomerRequestService
from workspace_api.application.shift_service import ShiftService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import CustomerRequest, CustomerRequestStatus, Shift
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers


def _sql_ledger(tmp_path, name="customer_requests.sqlite3"):
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _operator():
    return Principal(user_id="op1", role="operator")


def _viewer():
    return Principal(user_id="v1", role="viewer")


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _request(shift=None, **overrides):
    kwargs = dict(customer_id="cust-1", summary="Container missing paperwork")
    if shift is not None:
        kwargs["shift_id"] = shift.shift_id
    kwargs.update(overrides)
    return CustomerRequest(**kwargs)


def _client_for(ledger):
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)


def _clear_overrides():
    app.dependency_overrides.pop(get_ledger, None)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


# --- service-level create --------------------------------------------------


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_without_shift_succeeds(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    created = CustomerRequestService(ledger).create_customer_request(
        _request(), _operator()
    )
    assert created.status == CustomerRequestStatus.NEW
    assert created.shift_id is None

    # InMemoryLedger.audit_entries_for returns AuditRecord objects;
    # SqlLedger.audit_entries_for returns plain dicts (existing dual-backend
    # asymmetry, also present for Task/Shift audit checks elsewhere in this
    # test suite - not something this tranche changes). Assert on the shape
    # each backend actually returns.
    audit = ledger.audit_entries_for(str(created.request_id))
    assert len(audit) == 1
    last = audit[-1]
    action = last.action if hasattr(last, "action") else last["action"]
    assert action == "customer_request.create"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_with_open_shift_succeeds(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    created = CustomerRequestService(ledger).create_customer_request(
        _request(shift), _operator()
    )
    assert created.shift_id == shift.shift_id


def test_viewer_cannot_create_customer_request():
    ledger = InMemoryLedger()
    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger).create_customer_request(_request(), _viewer())
    assert exc.value.control == "permission"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_with_frozen_shift_is_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, _operator())
    ShiftService(ledger).freeze(
        shift.shift_id,
        Principal(user_id="sup1", role="shift_supervisor"),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    with pytest.raises(ValueError):
        CustomerRequestService(ledger).create_customer_request(_request(shift), _operator())


# --- HTTP-level round trip ---------------------------------------------------


def test_http_create_round_trip():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={"customer_id": "cust-9", "summary": "Late delivery"},
            headers=auth_headers("op1", "operator"),
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["customer_id"] == "cust-9"
        assert body["summary"] == "Late delivery"
        assert body["status"] == "NEW"
    finally:
        _clear_overrides()


def test_http_anonymous_create_is_401():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={"customer_id": "cust-9", "summary": "Late delivery"},
        )
        assert resp.status_code == 401, resp.text
        assert ledger.customer_requests == {}
    finally:
        _clear_overrides()


def test_http_insufficient_role_create_is_403():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={"customer_id": "cust-9", "summary": "Late delivery"},
            headers=auth_headers("v1", "viewer"),
        )
        assert resp.status_code == 403, resp.text
    finally:
        _clear_overrides()


# --- transition ---------------------------------------------------------


def test_valid_status_transition_sequence():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())

    moved = svc.transition(created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED)
    assert moved.status == CustomerRequestStatus.ACKNOWLEDGED

    moved = svc.transition(created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS)
    assert moved.status == CustomerRequestStatus.IN_PROGRESS

    moved = svc.transition(created.request_id, _operator(), CustomerRequestStatus.RESOLVED)
    assert moved.status == CustomerRequestStatus.RESOLVED

    moved = svc.transition(created.request_id, _operator(), CustomerRequestStatus.CLOSED)
    assert moved.status == CustomerRequestStatus.CLOSED

    audit = ledger.audit_entries_for(str(created.request_id))
    assert audit[-1].action == "customer_request.transition"
    assert audit[-1].before_state == "RESOLVED"
    assert audit[-1].after_state == "CLOSED"


def test_waiting_cannot_go_directly_to_closed():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED)
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS)
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.WAITING)

    with pytest.raises(ValueError):
        svc.transition(created.request_id, _operator(), CustomerRequestStatus.CLOSED)

    # WAITING -> IN_PROGRESS remains a valid path back.
    moved = svc.transition(created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS)
    assert moved.status == CustomerRequestStatus.IN_PROGRESS


def test_closed_is_terminal():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED)
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS)
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.RESOLVED)
    svc.transition(created.request_id, _operator(), CustomerRequestStatus.CLOSED)

    with pytest.raises(ValueError):
        svc.transition(created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS)


def test_illegal_transition_skip_is_blocked():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())
    # NEW -> IN_PROGRESS directly is not allowed (must go through ACKNOWLEDGED).
    with pytest.raises(ValueError):
        svc.transition(created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS)


# --- atomicity: audit-append failure must not leave a mutated record --------


class _BoomOnAudit(Exception):
    pass


def _raise_on_audit(*args, **kwargs):
    raise _BoomOnAudit("simulated audit sink failure")


def test_create_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    request = _request()

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).create_customer_request(request, _operator())

    with pytest.raises(KeyError):
        ledger.get_customer_request(request.request_id)


def test_create_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    request = _request()

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).create_customer_request(request, _operator())

    with pytest.raises(KeyError):
        ledger.get_customer_request(request.request_id)


def test_transition_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    created = CustomerRequestService(ledger).create_customer_request(_request(), _operator())

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).transition(
                created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED
            )

    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.status == CustomerRequestStatus.NEW, "status must not advance"


def test_transition_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    created = CustomerRequestService(ledger).create_customer_request(_request(), _operator())

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).transition(
                created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED
            )

    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.status == CustomerRequestStatus.NEW, "status must not advance"
