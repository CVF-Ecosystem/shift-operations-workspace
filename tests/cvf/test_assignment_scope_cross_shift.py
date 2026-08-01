"""Cross-shift and stored-target rules (P2C-MUTATION-FULL-UI-C3A2 WO section
3.3): handover create/review need SOURCE-shift assignment, acknowledge needs
DESTINATION-shift assignment; approval target shift resolves from the STORED
supported target, never a caller-supplied assertion; task-intent get resolves
the intent's stored shift; every id-based operation trusts the STORED shift,
never a request-body shift_id."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app
from operations_domain.models import Shift

from _auth_test_helpers import auth_headers
from _assignment_scope_fixtures import seed_active_assignment

_OP = ("operator-1", "operator")
_SUP1 = ("sup-1", "shift_supervisor")
_SUP2 = ("sup-2", "shift_supervisor")


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
    for user_id, role in (_OP, _SUP1, _SUP2):
        _seed_user(ledger, user_id, role)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _create_handover(http, src, dst, headers):
    return http.post(
        "/handovers", json={"from_shift_id": str(src), "to_shift_id": str(dst)}, headers=headers
    )


# --- handover create requires SOURCE-shift assignment ------------------------

def test_handover_create_requires_source_assignment_dest_alone_insufficient(client):
    ledger, http = client
    src, dst = _shift(ledger), _shift(ledger)
    seed_active_assignment(ledger, dst.shift_id, *_OP)
    res = _create_handover(http, src.shift_id, dst.shift_id, auth_headers(*_OP))
    assert res.status_code == 404
    seed_active_assignment(ledger, src.shift_id, *_OP)
    res = _create_handover(http, src.shift_id, dst.shift_id, auth_headers(*_OP))
    assert res.status_code == 200


# --- handover review requires SOURCE-shift assignment -------------------------

def test_handover_review_requires_source_assignment_dest_alone_insufficient(client):
    ledger, http = client
    src, dst = _shift(ledger), _shift(ledger)
    seed_active_assignment(ledger, src.shift_id, *_OP)
    seed_active_assignment(ledger, dst.shift_id, *_SUP2)
    create_res = _create_handover(http, src.shift_id, dst.shift_id, auth_headers(*_OP))
    handover_id = create_res.json()["handover_id"]
    review_body = {"expected_version": create_res.json()["version"]}

    # sup2 has destination assignment only - review is refused (enumeration-safe 404).
    res = http.post(f"/handovers/{handover_id}/review", json=review_body, headers=auth_headers(*_SUP2))
    assert res.status_code == 404

    seed_active_assignment(ledger, src.shift_id, *_SUP1)
    res = http.post(f"/handovers/{handover_id}/review", json=review_body, headers=auth_headers(*_SUP1))
    assert res.status_code == 200


# --- handover acknowledge requires DESTINATION-shift assignment ---------------

def test_handover_acknowledge_requires_destination_assignment_source_alone_insufficient(client):
    ledger, http = client
    src, dst = _shift(ledger), _shift(ledger)
    seed_active_assignment(ledger, src.shift_id, *_OP)
    seed_active_assignment(ledger, src.shift_id, *_SUP1)
    create_res = _create_handover(http, src.shift_id, dst.shift_id, auth_headers(*_OP))
    handover_id = create_res.json()["handover_id"]
    review_res = http.post(
        f"/handovers/{handover_id}/review",
        json={"expected_version": create_res.json()["version"]},
        headers=auth_headers(*_SUP1),
    )
    ack_body = {"expected_version": review_res.json()["version"]}

    # sup1 has source assignment only, not destination - acknowledge refused.
    res = http.post(f"/handovers/{handover_id}/acknowledge", json=ack_body, headers=auth_headers(*_SUP1))
    assert res.status_code == 404

    seed_active_assignment(ledger, dst.shift_id, *_SUP2)
    res = http.post(f"/handovers/{handover_id}/acknowledge", json=ack_body, headers=auth_headers(*_SUP2))
    assert res.status_code == 200
    assert res.json()["status"] == "ACKNOWLEDGED"


# --- approval target resolves from the STORED target, not caller assertion ---

def test_approval_target_shift_resolves_from_stored_event_not_caller_claim(client):
    """A caller cannot confer access by asserting a different record_type/id;
    the target shift used for the scope check is always the event's own
    persisted shift_id, resolved server-side."""
    ledger, http = client
    shift = _shift(ledger)
    other = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "event_type": "equipment_downtime", "title": "t", "risk_class": "R2"}
    event_id = http.post("/events", json=payload, headers=auth_headers(*_OP)).json()["event_id"]

    # sup1 is assigned only to `other`, never to the event's real stored shift.
    seed_active_assignment(ledger, other.shift_id, *_SUP1)
    body = {"record_type": "OperationalEvent", "action": "event.confirm", "record_id": event_id}
    res = http.post("/approvals", json=body, headers=auth_headers(*_SUP1))
    assert res.status_code == 404

    seed_active_assignment(ledger, shift.shift_id, *_SUP1)
    res = http.post("/approvals", json=body, headers=auth_headers(*_SUP1))
    assert res.status_code == 201


# --- task-intent get resolves the intent's stored shift -----------------------

def test_task_intent_get_resolves_stored_shift_not_a_different_assignment(client):
    ledger, http = client
    shift = _shift(ledger)
    other = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "title": "t", "risk_class": "R2"}
    intent_id = http.post(
        "/tasks/creation-intents", json=payload, headers=auth_headers(*_OP)
    ).json()["intent_id"]

    seed_active_assignment(ledger, other.shift_id, *_SUP1)
    res = http.get(f"/tasks/creation-intents/{intent_id}", headers=auth_headers(*_SUP1))
    assert res.status_code == 404

    seed_active_assignment(ledger, shift.shift_id, *_SUP1)
    res = http.get(f"/tasks/creation-intents/{intent_id}", headers=auth_headers(*_SUP1))
    assert res.status_code == 200
    assert res.json()["intent_id"] == intent_id


# --- id-based operations trust the STORED shift, never a body shift_id -------

def test_incident_acknowledge_ignores_a_mismatched_stored_shift_claim(client):
    """POST /incidents/{id}/acknowledge takes no body shift_id at all (the
    incident's own stored shift_id is the only authority) - proves a caller
    assigned to a DIFFERENT shift cannot acknowledge merely by naming the
    incident id; only assignment on the incident's real stored shift admits."""
    ledger, http = client
    shift = _shift(ledger)
    other = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    incident_id = http.post(
        "/incidents", json={"shift_id": str(shift.shift_id), "summary": "s"}, headers=auth_headers(*_OP)
    ).json()["incident_id"]

    ack_body = {"expected_version": 1}
    seed_active_assignment(ledger, other.shift_id, *_SUP1)
    res = http.post(f"/incidents/{incident_id}/acknowledge", json=ack_body, headers=auth_headers(*_SUP1))
    assert res.status_code == 404

    seed_active_assignment(ledger, shift.shift_id, *_SUP1)
    res = http.post(f"/incidents/{incident_id}/acknowledge", json=ack_body, headers=auth_headers(*_SUP1))
    assert res.status_code == 200


def test_customer_request_transition_trusts_stored_shift_not_body(client):
    """TransitionInput carries only target_status - no shift_id field exists
    on the wire to substitute; the stored request.shift_id is the only
    authority the scope check ever consults."""
    from operations_domain.models import CustomerRequest

    ledger, http = client
    shift = _shift(ledger)
    other = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    ledger.add_customer_request(request)

    seed_active_assignment(ledger, other.shift_id, *_SUP1)
    body = {"target_status": "ACKNOWLEDGED", "expected_version": request.version}
    res = http.post(f"/customer-requests/{request.request_id}/transition", json=body, headers=auth_headers(*_SUP1))
    assert res.status_code == 404

    seed_active_assignment(ledger, shift.shift_id, *_SUP1)
    res = http.post(f"/customer-requests/{request.request_id}/transition", json=body, headers=auth_headers(*_SUP1))
    assert res.status_code == 200
