"""R6 operational matrix (P2C-MUTATION-FULL-UI-C3A2 WO section 3.2): ACTIVE
assignment required for every existing shift-bound route. Unassigned is
refused (403 if a coarser permission check fires first, else 404
enumeration-safe); assigned passes the gate and reaches a further response."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app
from operations_domain.models import CustomerRequest, OperationalEvent, Shift, Task

from _auth_test_helpers import auth_headers
from _assignment_scope_fixtures import seed_active_assignment

_OP = ("operator-1", "operator")
_SUP = ("sup-1", "shift_supervisor")
_OUTSIDER = ("outsider-1", "operator")
_OUTSIDER_SUP = ("outsider-sup", "shift_supervisor")


def _window():
    now = datetime.now(timezone.utc)
    return now, now + timedelta(hours=8)


def _seed_user(ledger, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))


def _shift(ledger):
    starts_at, ends_at = _window()
    shift = Shift(name="Day", starts_at=starts_at, ends_at=ends_at)
    ledger.create_shift(shift)
    return shift


@pytest.fixture
def client():
    ledger = InMemoryLedger()
    for user_id, role in (_OP, _SUP, _OUTSIDER, _OUTSIDER_SUP):
        _seed_user(ledger, user_id, role)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


# --- read/list and simple create actions: (route, method, body, admitted range)

_SIMPLE_CASES = [
    ("open_work", "GET", lambda sid: f"/shifts/{sid}/open-work", None, (200,)),
    ("shift_close", "POST", lambda sid: f"/shifts/{sid}/close", None, (200,)),
    ("message_create", "POST", lambda sid: "/messages", lambda sid: {"shift_id": str(sid), "text": "hi"}, (200,)),
    (
        "event_create", "POST", lambda sid: "/events",
        lambda sid: {"shift_id": str(sid), "event_type": "equipment_downtime", "title": "t"}, (200,),
    ),
    ("event_list", "GET", lambda sid: f"/events?shift_id={sid}", None, (200,)),
    ("task_create", "POST", lambda sid: "/tasks", lambda sid: {"shift_id": str(sid), "title": "t"}, (200,)),
    (
        "customer_request_create", "POST", lambda sid: "/customer-requests",
        lambda sid: {"customer_id": "c1", "shift_id": str(sid), "summary": "s"}, (200,),
    ),
    ("incident_report", "POST", lambda sid: "/incidents", lambda sid: {"shift_id": str(sid), "summary": "s"}, (200,)),
    ("incident_list", "GET", lambda sid: f"/incidents?shift_id={sid}", None, (200,)),
]


@pytest.mark.parametrize("name,method,path_fn,body_fn,admitted", _SIMPLE_CASES, ids=[c[0] for c in _SIMPLE_CASES])
def test_route_requires_active_assignment(client, name, method, path_fn, body_fn, admitted):
    ledger, http = client
    shift = _shift(ledger)

    def _call(headers):
        path = path_fn(shift.shift_id)
        if method == "GET":
            return http.get(path, headers=headers)
        return http.post(path, json=(body_fn(shift.shift_id) if body_fn else {}), headers=headers)

    res = _call(auth_headers(*_OUTSIDER))
    assert res.status_code == 404, f"{name}: {res.status_code} {res.text}"
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    res = _call(auth_headers(*_OP))
    assert res.status_code in admitted, f"{name}: {res.status_code} {res.text}"


def test_shift_list_returns_only_assigned_shifts(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    res = http.get("/shifts", headers=auth_headers(*_OP))
    assert res.status_code == 200
    assert [s["shift_id"] for s in res.json()] == [str(shift.shift_id)]
    res = http.get("/shifts", headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 200
    assert res.json() == []


def test_shift_freeze_requires_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)
    res = http.post(f"/shifts/{shift.shift_id}/freeze", json={}, headers=auth_headers(*_OUTSIDER_SUP))
    assert res.status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    res = http.post(f"/shifts/{shift.shift_id}/freeze", json={}, headers=auth_headers(*_SUP))
    # Not assignment-refused: reaches the real (unmet) freeze precondition.
    assert res.status_code == 409


# --- supervisor-bar actions: insufficient role -> 403 before assignment ----

def test_event_confirm_role_then_assignment_ordering(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "event_type": "equipment_downtime", "title": "t"}
    event_id = http.post("/events", json=payload, headers=auth_headers(*_OP)).json()["event_id"]

    res = http.post(f"/events/{event_id}/confirm", json={}, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 403  # insufficient role fires before assignment
    res = http.post(f"/events/{event_id}/confirm", json={}, headers=auth_headers(*_OUTSIDER_SUP))
    assert res.status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    res = http.post(f"/events/{event_id}/confirm", json={}, headers=auth_headers(*_SUP))
    assert res.status_code != 404


def test_incident_acknowledge_role_then_assignment_ordering(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "summary": "s"}
    incident_id = http.post("/incidents", json=payload, headers=auth_headers(*_OP)).json()["incident_id"]
    ack_path = f"/incidents/{incident_id}/acknowledge"
    assert http.post(ack_path, json={}, headers=auth_headers(*_OUTSIDER)).status_code == 403
    assert http.post(ack_path, json={}, headers=auth_headers(*_OUTSIDER_SUP)).status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    assert http.post(ack_path, json={}, headers=auth_headers(*_SUP)).status_code != 404

    assert http.get(f"/incidents/{incident_id}", headers=auth_headers(*_OUTSIDER)).status_code == 404
    trans_body = {"target_status": "CLOSED"}
    trans_res = http.post(f"/incidents/{incident_id}/transition", json=trans_body, headers=auth_headers(*_OUTSIDER))
    assert trans_res.status_code == 404


def test_report_lifecycle_requires_active_assignment_at_every_step(client):
    """generate/list, get, submit-review (operator bar) and approve
    (supervisor bar) each independently require ACTIVE assignment."""
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    ledger.close_shift(shift.shift_id)

    res = http.post("/reports", json={"shift_id": str(shift.shift_id)}, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404
    res = http.get(f"/reports?shift_id={shift.shift_id}", headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404

    report_id = http.post(
        "/reports", json={"shift_id": str(shift.shift_id)}, headers=auth_headers(*_OP)
    ).json()["report_id"]
    assert http.get(f"/reports?shift_id={shift.shift_id}", headers=auth_headers(*_OP)).status_code == 200

    res = http.get(f"/reports/{report_id}", headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404
    assert http.get(f"/reports/{report_id}", headers=auth_headers(*_OP)).status_code == 200

    res = http.post(f"/reports/{report_id}/submit-review", headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404
    assert http.post(f"/reports/{report_id}/submit-review", headers=auth_headers(*_OP)).status_code == 200

    res = http.post(f"/reports/{report_id}/approve", headers=auth_headers(*_OUTSIDER_SUP))
    assert res.status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    res = http.post(f"/reports/{report_id}/approve", headers=auth_headers(*_SUP))
    assert res.status_code != 404


# --- get-by-id / transition / creation-intent / approvals ---------------------

def test_task_transition_requires_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    task = Task(shift_id=shift.shift_id, title="t")
    ledger.add_task(task)
    path, body = f"/tasks/{task.task_id}/transition", {"target_status": "IN_PROGRESS"}
    assert http.post(path, json=body, headers=auth_headers(*_OUTSIDER)).status_code == 404
    assert http.post(path, json=body, headers=auth_headers(*_OP)).status_code == 200


def test_task_creation_intent_create_and_get_require_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)
    payload = {"shift_id": str(shift.shift_id), "title": "t", "risk_class": "R2"}
    res = http.post("/tasks/creation-intents", json=payload, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    res = http.post("/tasks/creation-intents", json=payload, headers=auth_headers(*_OP))
    assert res.status_code == 201
    intent_id = res.json()["intent_id"]

    # get_creation_intent needs viewer authority for R2's required seat too.
    res = http.get(f"/tasks/creation-intents/{intent_id}", headers=auth_headers(*_OUTSIDER_SUP))
    assert res.status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    res = http.get(f"/tasks/creation-intents/{intent_id}", headers=auth_headers(*_SUP))
    assert res.status_code == 200


def test_customer_request_transition_requires_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    request = CustomerRequest(customer_id="cust-1", shift_id=shift.shift_id, summary="s")
    ledger.add_customer_request(request)
    path, body = f"/customer-requests/{request.request_id}/transition", {"target_status": "ACKNOWLEDGED"}
    assert http.post(path, json=body, headers=auth_headers(*_OUTSIDER)).status_code == 404
    assert http.post(path, json=body, headers=auth_headers(*_OP)).status_code == 200


def test_handover_create_get_list_require_active_assignment(client):
    ledger, http = client
    src, dst = _shift(ledger), _shift(ledger)
    seed_active_assignment(ledger, dst.shift_id, *_OP)  # dest-only is not enough for create
    payload = {"from_shift_id": str(src.shift_id), "to_shift_id": str(dst.shift_id)}
    assert http.post("/handovers", json=payload, headers=auth_headers(*_OP)).status_code == 404
    seed_active_assignment(ledger, src.shift_id, *_OP)
    res = http.post("/handovers", json=payload, headers=auth_headers(*_OP))
    assert res.status_code == 200
    handover_id = res.json()["handover_id"]

    assert http.get(f"/handovers/{handover_id}", headers=auth_headers(*_OUTSIDER)).status_code == 404
    assert http.get(f"/handovers/{handover_id}", headers=auth_headers(*_OP)).status_code == 200
    list_path = f"/handovers?from_shift_id={src.shift_id}"
    assert http.get(list_path, headers=auth_headers(*_OUTSIDER)).status_code == 404
    assert http.get(list_path, headers=auth_headers(*_OP)).status_code == 200


def test_approval_receipt_create_requires_active_assignment_for_stored_target(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "event_type": "equipment_downtime", "title": "t", "risk_class": "R2"}
    event_id = http.post("/events", json=payload, headers=auth_headers(*_OP)).json()["event_id"]
    body = {"record_type": "OperationalEvent", "action": "event.confirm", "record_id": event_id}
    assert http.post("/approvals", json=body, headers=auth_headers(*_OUTSIDER_SUP)).status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    assert http.post("/approvals", json=body, headers=auth_headers(*_SUP)).status_code == 201


def test_event_correct_role_then_assignment_ordering(client):
    ledger, http = client
    shift = _shift(ledger)
    event = OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="t")
    ledger.add_event(event)
    path, body = f"/corrections/events/{event.event_id}", {"reason": "typo fix"}
    assert http.post(path, json=body, headers=auth_headers(*_OUTSIDER)).status_code == 403  # role before assignment
    assert http.post(path, json=body, headers=auth_headers(*_OUTSIDER_SUP)).status_code == 404
    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    assert http.post(path, json=body, headers=auth_headers(*_SUP)).status_code != 404  # reaches quorum check


def test_report_create_version_requires_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    ledger.close_shift(shift.shift_id)
    report_id = http.post(
        "/reports", json={"shift_id": str(shift.shift_id)}, headers=auth_headers(*_OP)
    ).json()["report_id"]
    path = f"/reports/{report_id}/versions"
    assert http.post(path, json={}, headers=auth_headers(*_OUTSIDER)).status_code == 404
    assert http.post(path, json={}, headers=auth_headers(*_OP)).status_code == 201


# --- bootstrap exceptions and out-of-scope surfaces -------------------------

def test_shift_create_and_null_shift_customer_request_need_no_assignment(client):
    _, http = client
    starts_at, ends_at = _window()
    res = http.post(
        "/shifts",
        params={"name": "Day", "starts_at": starts_at.isoformat(), "ends_at": ends_at.isoformat()},
        headers=auth_headers(*_OP),
    )
    assert res.status_code == 200

    res = http.post("/customer-requests", json={"customer_id": "c1", "summary": "s"}, headers=auth_headers(*_OP))
    assert res.status_code == 200
