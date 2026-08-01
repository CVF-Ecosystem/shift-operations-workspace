"""Enumeration-safe and atomic refusal (P2C-MUTATION-FULL-UI-C3A2 WO section
3.4): unauthenticated stays 401, coarse permission denial stays 403; missing
and inaccessible-but-existing records share the same sanitized 404 shape;
list routes return only assigned records; assignment refusal happens before
any mutation/audit side effect."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

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
    for user_id, role in (_OP, _OUTSIDER, _OUTSIDER_SUP):
        _seed_user(ledger, user_id, role)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


# --- unauthenticated stays 401, coarse permission denial stays 403 -----------

def test_unauthenticated_open_work_is_401(client):
    ledger, http = client
    shift = _shift(ledger)
    res = http.get(f"/shifts/{shift.shift_id}/open-work")
    assert res.status_code == 401


def test_coarse_permission_denial_stays_403_even_when_assigned(client):
    """event.confirm requires shift_supervisor; an ACTIVE-assigned operator
    is still refused 403 by require_action, never masked as 404."""
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "event_type": "equipment_downtime", "title": "t"}
    event_id = http.post("/events", json=payload, headers=auth_headers(*_OP)).json()["event_id"]
    res = http.post(f"/events/{event_id}/confirm", json={}, headers=auth_headers(*_OP))
    assert res.status_code == 403


# --- missing vs. inaccessible-but-existing share the same sanitized 404 -----

def test_missing_and_inaccessible_handover_share_identical_404_body(client):
    ledger, http = client
    shift = _shift(ledger)
    other = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    seed_active_assignment(ledger, other.shift_id, *_OP)
    handover_id = http.post(
        "/handovers", json={"from_shift_id": str(shift.shift_id), "to_shift_id": str(other.shift_id)},
        headers=auth_headers(*_OP),
    ).json()["handover_id"]

    missing_res = http.get(f"/handovers/{uuid4()}", headers=auth_headers(*_OUTSIDER))
    inaccessible_res = http.get(f"/handovers/{handover_id}", headers=auth_headers(*_OUTSIDER))

    assert missing_res.status_code == inaccessible_res.status_code == 404
    assert set(missing_res.json().keys()) == set(inaccessible_res.json().keys())
    assert isinstance(missing_res.json()["detail"], str)
    assert isinstance(inaccessible_res.json()["detail"], str)
    assert str(handover_id) not in missing_res.text
    assert str(handover_id) not in inaccessible_res.text


def test_missing_and_inaccessible_incident_share_identical_404_body(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    incident_id = http.post(
        "/incidents", json={"shift_id": str(shift.shift_id), "summary": "s"}, headers=auth_headers(*_OP)
    ).json()["incident_id"]

    missing_res = http.get(f"/incidents/{uuid4()}", headers=auth_headers(*_OUTSIDER))
    inaccessible_res = http.get(f"/incidents/{incident_id}", headers=auth_headers(*_OUTSIDER))

    assert missing_res.status_code == inaccessible_res.status_code == 404
    assert set(missing_res.json().keys()) == set(inaccessible_res.json().keys())


# --- list routes reveal only assigned shifts/records -------------------------

def test_shift_list_never_reveals_unassigned_shift(client):
    ledger, http = client
    assigned = _shift(ledger)
    unassigned = _shift(ledger)
    seed_active_assignment(ledger, assigned.shift_id, *_OP)

    res = http.get("/shifts", headers=auth_headers(*_OP))
    assert res.status_code == 200
    ids = [s["shift_id"] for s in res.json()]
    assert ids == [str(assigned.shift_id)]
    assert str(unassigned.shift_id) not in res.text


def test_handover_list_never_reveals_unassigned_source_shift(client):
    ledger, http = client
    shift = _shift(ledger)
    other = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    seed_active_assignment(ledger, other.shift_id, *_OP)
    http.post(
        "/handovers", json={"from_shift_id": str(shift.shift_id), "to_shift_id": str(other.shift_id)},
        headers=auth_headers(*_OP),
    )
    res = http.get(f"/handovers?from_shift_id={other.shift_id}", headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404


# --- assignment refusal precedes any mutation/audit side effect --------------

def test_refused_message_create_leaves_zero_messages_and_zero_audit(client):
    ledger, http = client
    shift = _shift(ledger)
    before_messages = len(ledger.messages)
    before_audit = len(ledger.audit_entries_for(str(shift.shift_id)))

    res = http.post(
        "/messages", json={"shift_id": str(shift.shift_id), "text": "hi"}, headers=auth_headers(*_OUTSIDER)
    )
    assert res.status_code == 404
    assert len(ledger.messages) == before_messages
    assert len(ledger.audit_entries_for(str(shift.shift_id))) == before_audit


def test_refused_incident_acknowledge_leaves_incident_and_audit_unchanged(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    incident_id = http.post(
        "/incidents", json={"shift_id": str(shift.shift_id), "summary": "s"}, headers=auth_headers(*_OP)
    ).json()["incident_id"]
    before = ledger.get_incident(UUID(incident_id))
    before_audit_count = len(ledger.audit_entries_for(str(incident_id)))

    res = http.post(f"/incidents/{incident_id}/acknowledge", json={}, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 403  # insufficient role (operator) fires first

    after = ledger.get_incident(UUID(incident_id))
    assert after.status == before.status
    assert after.version == before.version
    assert len(ledger.audit_entries_for(str(incident_id))) == before_audit_count


def test_refused_approval_receipt_leaves_zero_receipts_and_zero_audit(client):
    """_OUTSIDER is a known active user (role operator) with no authority for
    any R2 seat, so the coarse identity/role check (F1: runs before the
    assignment-scope guard) refuses with 403 - never reaching a counted
    receipt, regardless of shift assignment."""
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    payload = {"shift_id": str(shift.shift_id), "event_type": "equipment_downtime", "title": "t", "risk_class": "R2"}
    event_id = http.post("/events", json=payload, headers=auth_headers(*_OP)).json()["event_id"]
    before_receipts = len(ledger.approval_receipts)
    before_audit = len(ledger.audit_entries_for(event_id))

    body = {"record_type": "OperationalEvent", "action": "event.confirm", "record_id": event_id}
    res = http.post("/approvals", json=body, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 403
    assert len(ledger.approval_receipts) == before_receipts
    assert len(ledger.audit_entries_for(event_id)) == before_audit


def test_report_approval_receipt_checks_authority_then_assignment_then_lifecycle(client):
    """C3A2-BUILD-REREV-F1: the Report branch's own lifecycle gate (is_current
    and IN_REVIEW) must never fire before authority/assignment - a DRAFT
    report (not yet IN_REVIEW) proves the exact order: unassigned+unauthorized
    viewer gets 403, unassigned-but-authorized supervisor gets 404, only an
    assigned supervisor reaches the real 409 lifecycle refusal. Zero receipts/
    audit written at every step."""
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    ledger.close_shift(shift.shift_id)
    report_id = http.post(
        "/reports", json={"shift_id": str(shift.shift_id)}, headers=auth_headers(*_OP)
    ).json()["report_id"]  # DRAFT, not IN_REVIEW
    before_receipts = len(ledger.approval_receipts)
    before_audit = len(ledger.audit_entries_for(report_id))
    body = {"record_type": "Report", "action": "report.approve", "record_id": report_id}

    res = http.post("/approvals", json=body, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 403  # operator has no R2 authority

    res = http.post("/approvals", json=body, headers=auth_headers(*_OUTSIDER_SUP))
    assert res.status_code == 404  # authorized role, but unassigned to the shift

    seed_active_assignment(ledger, shift.shift_id, *_OUTSIDER_SUP)
    res = http.post("/approvals", json=body, headers=auth_headers(*_OUTSIDER_SUP))
    assert res.status_code == 409  # authorized and assigned; real lifecycle refusal

    assert len(ledger.approval_receipts) == before_receipts
    assert len(ledger.audit_entries_for(report_id)) == before_audit
