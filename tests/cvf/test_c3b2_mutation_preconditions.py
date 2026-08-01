"""P2C-MUTATION-FULL-UI-C3B2 focused matrix (SPEC R13/R14, AC-13/AC-14/AC-15):
every affected existing-aggregate mutation route requires an explicit
``expected_version`` (Report status-only transitions also require
``expected_status``); missing/invalid precondition is 422, stale is 409, and
every protected create/append/task-intent/approval-receipt route keeps its
exact prior contract with zero invented field."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.identity import Principal
from operations_domain.models import CustomerRequest, EvidenceRef, Incident, OperationalEvent, RiskClass, Shift, Task
from workspace_api.application.handover_service import HandoverService
from workspace_api.application.report_service import ReportService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app
from _auth_test_helpers import auth_headers

_OPERATOR = ("op1", "operator")
_SUPERVISOR = ("sup1", "shift_supervisor")
_OPERATOR_P = Principal(user_id=_OPERATOR[0], role=_OPERATOR[1])


def _seed(ledger, shift_id, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _new_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, *_OPERATOR)
    _seed(ledger, shift.shift_id, *_SUPERVISOR)
    return shift


@pytest.fixture
def client():
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _closed_shift_with_report(ledger):
    shift = _new_shift(ledger)
    ledger.close_shift(shift.shift_id)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR_P)
    return shift, report


# --- R13/AC-13: missing expected_version is a controlled 422 for every
# affected route. -----------------------------------------------------------

@pytest.mark.parametrize("name,expected_status", [("shift_close", 422), ("shift_freeze", 422)])
def test_shift_route_missing_expected_version_is_422(client, name, expected_status):
    ledger, http = client
    shift = _new_shift(ledger)
    path = f"/shifts/{shift.shift_id}/close" if name == "shift_close" else f"/shifts/{shift.shift_id}/freeze"
    res = http.post(path, json={}, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == expected_status, res.text
    if name == "shift_close":
        assert ledger.get_shift(shift.shift_id).status.value == "OPEN"
        assert ledger.audit_entries_for(str(shift.shift_id)) == []


def test_event_confirm_and_correct_missing_expected_version_is_422(client):
    ledger, http = client
    shift = _new_shift(ledger)
    event = OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="t", risk_class=RiskClass.R0)
    ledger.add_event(event)
    res = http.post(f"/events/{event.event_id}/confirm", json={}, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 422, res.text
    assert ledger.get_event(event.event_id).version == 1
    assert ledger.audit_entries_for(str(event.event_id)) == []

    confirmed_event = OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="t", state="CONFIRMED")
    ledger.add_event(confirmed_event)
    res = http.post(f"/corrections/events/{confirmed_event.event_id}", json={"reason": "x"}, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 422, res.text


def test_task_transition_missing_expected_version_is_422(client):
    ledger, http = client
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="t")
    ledger.add_task(task)
    res = http.post(f"/tasks/{task.task_id}/transition", json={"target_status": "IN_PROGRESS"}, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 422, res.text
    assert ledger.get_task(task.task_id).status.value == "OPEN"


def test_customer_request_transition_missing_expected_version_is_422(client):
    ledger, http = client
    shift = _new_shift(ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    ledger.add_customer_request(request)
    body = {"target_status": "ACKNOWLEDGED"}
    res = http.post(f"/customer-requests/{request.request_id}/transition", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 422, res.text
    assert ledger.get_customer_request(request.request_id).version == 1


def test_incident_acknowledge_and_transition_missing_expected_version_is_422(client):
    ledger, http = client
    shift = _new_shift(ledger)
    incident = Incident(shift_id=shift.shift_id, risk_class=RiskClass.R0, summary="s", evidence=[EvidenceRef(source_type="message", source_id="m1")])
    ledger.add_incident(incident)
    res = http.post(f"/incidents/{incident.incident_id}/acknowledge", json={}, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 422, res.text

    ack_incident = Incident(shift_id=shift.shift_id, risk_class=RiskClass.R0, summary="s", status="ACKNOWLEDGED")
    ledger.add_incident(ack_incident)
    body = {"target_status": "MITIGATING"}
    res = http.post(f"/incidents/{ack_incident.incident_id}/transition", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 422, res.text


def test_handover_review_and_acknowledge_missing_expected_version_is_422(client):
    ledger, http = client
    s1, s2 = _new_shift(ledger), _new_shift(ledger)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR_P)
    res = http.post(f"/handovers/{handover.handover_id}/review", json={}, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 422, res.text

    handover = HandoverService(ledger).review(handover.handover_id, Principal(user_id=_SUPERVISOR[0], role=_SUPERVISOR[1]), expected_version=handover.version)
    res = http.post(f"/handovers/{handover.handover_id}/acknowledge", json={}, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 422, res.text


@pytest.mark.parametrize("path_suffix,actor", [("submit-review", _OPERATOR), ("approve", _SUPERVISOR), ("versions", _OPERATOR)])
def test_report_routes_missing_body_is_422(client, path_suffix, actor):
    ledger, http = client
    _shift, report = _closed_shift_with_report(ledger)
    res = http.post(f"/reports/{report.report_id}/{path_suffix}", json={}, headers=auth_headers(*actor))
    assert res.status_code == 422, res.text


# --- R14/AC-13/AC-15: a stale precondition is a controlled 409 with zero mutation. ---

def test_shift_close_stale_version_is_409_with_zero_mutation(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = http.post(f"/shifts/{shift.shift_id}/close", json={"expected_version": shift.version + 1}, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 409, res.text
    assert ledger.get_shift(shift.shift_id).status.value == "OPEN"
    assert ledger.audit_entries_for(str(shift.shift_id)) == []


def test_task_transition_stale_version_is_409_with_zero_mutation(client):
    ledger, http = client
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="t")
    ledger.add_task(task)
    body = {"target_status": "IN_PROGRESS", "expected_version": task.version + 1}
    res = http.post(f"/tasks/{task.task_id}/transition", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 409, res.text
    fetched = ledger.get_task(task.task_id)
    assert fetched.status.value == "OPEN" and fetched.version == 1


def test_customer_request_transition_stale_version_is_409_with_zero_mutation(client):
    ledger, http = client
    shift = _new_shift(ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    ledger.add_customer_request(request)
    body = {"target_status": "ACKNOWLEDGED", "expected_version": request.version + 1}
    res = http.post(f"/customer-requests/{request.request_id}/transition", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 409, res.text
    fetched = ledger.get_customer_request(request.request_id)
    assert fetched.status.value == "NEW" and fetched.version == 1


def test_incident_acknowledge_stale_version_is_409(client):
    ledger, http = client
    shift = _new_shift(ledger)
    incident = Incident(shift_id=shift.shift_id, risk_class=RiskClass.R0, summary="s", evidence=[EvidenceRef(source_type="message", source_id="m1")])
    ledger.add_incident(incident)
    body = {"expected_version": incident.version + 1}
    res = http.post(f"/incidents/{incident.incident_id}/acknowledge", json=body, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 409, res.text
    assert ledger.get_incident(incident.incident_id).status.value == "REPORTED"


def test_report_submit_review_stale_status_is_409(client):
    ledger, http = client
    _shift, report = _closed_shift_with_report(ledger)
    body = {"expected_version": report.version, "expected_status": "IN_REVIEW"}
    res = http.post(f"/reports/{report.report_id}/submit-review", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 409, res.text
    assert ledger.get_report(report.report_id).status.value == "DRAFT"


# --- successful path leaves exactly the expected audit trail --------------

def test_shift_close_success_increments_version_and_audits(client):
    ledger, http = client
    shift = _new_shift(ledger)
    body = {"expected_version": shift.version}
    res = http.post(f"/shifts/{shift.shift_id}/close", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 200, res.text
    assert res.json()["version"] == 2  # OPEN (version 1) -> CLOSED increments once
    actions = {e.action for e in ledger.audit_entries_for(str(shift.shift_id))}
    assert "shift.close" in actions


# --- Work Order 3.2: protected create/append/task-intent/approval-receipt
# routes stay exactly unchanged - no invented precondition field newly
# required. EventInput/CustomerRequestInput never declared extra="forbid"
# (pre-existing, unrelated) so they silently ignore an extra field exactly
# as before; every other protected route already forbids extras. ----------

def test_event_and_customer_request_create_ignore_unrelated_extra_field_unchanged(client):
    ledger, http = client
    shift = _new_shift(ledger)
    event_body = {"shift_id": str(shift.shift_id), "event_type": "equipment_downtime", "title": "t", "expected_version": 1}
    res = http.post("/events", json=event_body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 200, res.text
    assert "expected_version" not in res.json()

    cr_body = {"customer_id": "c1", "summary": "s", "expected_version": 1}
    res = http.post("/customer-requests", json=cr_body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 200, res.text
    assert "expected_version" not in res.json()


@pytest.mark.parametrize("path,body_fn,actor", [
    ("/tasks", lambda s: {"shift_id": str(s.shift_id), "title": "t", "expected_version": 1}, _OPERATOR),
    ("/incidents", lambda s: {"shift_id": str(s.shift_id), "summary": "s", "expected_version": 1}, _OPERATOR),
    ("/tasks/creation-intents", lambda s: {"shift_id": str(s.shift_id), "title": "t", "risk_class": "R2", "expected_version": 1}, _SUPERVISOR),
    ("/reports", lambda s: {"shift_id": str(s.shift_id), "expected_version": 1}, _OPERATOR),
])
def test_protected_shift_bound_create_rejects_invented_expected_version_field(client, path, body_fn, actor):
    ledger, http = client
    shift = _new_shift(ledger)
    if path == "/reports":
        ledger.close_shift(shift.shift_id)
    res = http.post(path, json=body_fn(shift), headers=auth_headers(*actor))
    assert res.status_code == 422, res.text


def test_handover_create_rejects_invented_expected_version_field(client):
    ledger, http = client
    s1, s2 = _new_shift(ledger), _new_shift(ledger)
    body = {"from_shift_id": str(s1.shift_id), "to_shift_id": str(s2.shift_id), "expected_version": 1}
    res = http.post("/handovers", json=body, headers=auth_headers(*_OPERATOR))
    assert res.status_code == 422, res.text


def test_approval_receipt_create_rejects_invented_expected_version_field(client):
    ledger, http = client
    shift = _new_shift(ledger)
    event = OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="t", risk_class=RiskClass.R2)
    ledger.add_event(event)
    body = {"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id), "expected_version": 1}
    res = http.post("/approvals", json=body, headers=auth_headers(*_SUPERVISOR))
    assert res.status_code == 422, res.text


# --- direct-service boundary: an omitted/invalid precondition is also a
# controlled 422 (Work Order 3.2 / C3B2-WO-REV-F1) --------------------------

# REVIEW-F4: None/bool/float/string/zero/negative all fail 422 identically -
# none is silently coerced or admitted as "valid" (a genuinely valid-but-
# stale value's 409 is covered by the stale-precondition tests above).

@pytest.mark.parametrize("expected_version", [None, True, 1.0, "1", 0, -1])
def test_direct_service_call_with_invalid_expected_version_is_422_not_permissive(expected_version):
    from cvf_runtime.errors import CvfDenied
    from workspace_api.application.shift_service import ShiftService

    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).close(shift.shift_id, _OPERATOR_P, expected_version=expected_version)
    assert exc.value.http_status == 422
    assert ledger.get_shift(shift.shift_id).status.value == "OPEN"

# expected_status type/instance validation (None/raw-string/int/bool/float/
# unrelated-enum matrix) lives in tests/cvf/test_report_approval.py, the
# Report-specific precondition-ordering test host - REVIEW-REREV-F1.
