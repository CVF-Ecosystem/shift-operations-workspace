"""Incident golden vertical: the CVF chain replicated to a fifth operational
domain (P2-A). Report is immediate; acknowledge is the protected R2+ decision
reusing the durable-receipt architecture; transition is post-acknowledgement
only. Proves the SAME cvf-runtime gates (identity/permission/domain_lock/risk/
evidence/approval/audit/freeze) enforce this vertical, on both ledger backends
where relevant.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application import approval_service
from workspace_api.application.incident_service import IncidentService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import User
from operations_domain.models import EvidenceRef, Incident, IncidentStatus, RiskClass, Shift
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_OPERATOR = Principal(user_id="op1", role="operator")


def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'incidents.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "incidents.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _incident(shift, **overrides):
    kwargs = dict(shift_id=shift.shift_id, summary="Crane 3 stopped", risk_class=RiskClass.R2)
    kwargs.update(overrides)
    return Incident(**kwargs)


def _reported_with_receipt(ledger, approver_id="sup2", *, evidence=True):
    """A REPORTED incident plus a genuine, active-approver receipt bound to
    its current version - the ready-to-acknowledge fixture every acknowledge/
    transition test below starts from."""
    ev = [EvidenceRef(source_type="message", source_id="m1")] if evidence else []
    incident = IncidentService(ledger).report(_incident(_new_shift(ledger), evidence=ev), _OPERATOR)
    ledger.add_user(User(user_id=approver_id, username=approver_id, password_hash="x", role="shift_supervisor"))
    approval_service.create_approval_receipt(
        ledger, Principal(user_id=approver_id, role="shift_supervisor"), record_type="Incident",
        action="incident.acknowledge", record_id=incident.incident_id,
    )
    return incident


@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


# --- AC-07: report ----------------------------------------------------------


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_report_persists_incident_evidence_and_audit_atomically(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    incident = _incident(_new_shift(ledger), evidence=[EvidenceRef(source_type="message", source_id="m1")])
    reported = IncidentService(ledger).report(incident, _OPERATOR)

    assert reported.status.value == "REPORTED"
    assert len(ledger.get_incident(reported.incident_id).evidence) == 1
    assert len(ledger.audit_entries_for(str(reported.incident_id))) == 1


def test_report_rejects_viewer_role():
    ledger = InMemoryLedger()
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).report(_incident(_new_shift(ledger)), Principal(user_id="v1", role="viewer"))
    assert exc.value.control == "permission"


def test_report_rejected_under_frozen_shift():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    ledger.freeze_shift(shift.shift_id)
    with pytest.raises(ValueError, match="frozen"):
        IncidentService(ledger).report(_incident(shift), _OPERATOR)


# --- AC-08/AC-09: acknowledge ------------------------------------------------


def test_acknowledge_insufficient_evidence_denied():
    ledger = InMemoryLedger()
    incident = IncidentService(ledger).report(_incident(_new_shift(ledger), evidence=[]), _OPERATOR)
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    assert exc.value.control == "evidence"


def test_acknowledge_fabricated_zero_receipts_denied():
    ledger = InMemoryLedger()
    incident = IncidentService(ledger).report(
        _incident(_new_shift(ledger), evidence=[EvidenceRef(source_type="message", source_id="m1")]), _OPERATOR
    )
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    assert exc.value.control == "approval"


def test_acknowledge_self_approval_denied():
    ledger = InMemoryLedger()
    incident = _reported_with_receipt(ledger, approver_id="sup1")
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    assert exc.value.control == "approval"


def test_acknowledge_inactive_approver_receipt_denied():
    """Authority is re-derived FRESH at acknowledge time, never trusted from
    the receipt's stored approver_role: sup2 is deactivated after its receipt
    was created while still active."""
    ledger = InMemoryLedger()
    incident = _reported_with_receipt(ledger)
    ledger.users["sup2"].is_active = False
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    assert exc.value.control == "approval"


def test_acknowledge_stale_version_receipt_denied():
    """A receipt bound to a version the incident has since moved past cannot
    authorize acknowledgement (SPEC R8)."""
    ledger = InMemoryLedger()
    incident = _reported_with_receipt(ledger)
    stale = ledger.get_incident(incident.incident_id)
    stale.version += 1
    ledger.put_incident(stale)
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    assert exc.value.control == "approval"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_acknowledge_succeeds_with_distinct_authenticated_receipt(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    incident = _reported_with_receipt(ledger)
    acknowledged = IncidentService(ledger).acknowledge(
        incident.incident_id, Principal(user_id="sup1", role="shift_supervisor")
    )
    assert acknowledged.status.value == "ACKNOWLEDGED"
    assert acknowledged.version == 2


# --- AC-10: post-acknowledgement transition ---------------------------------


def test_transition_rejects_reported_status():
    ledger = InMemoryLedger()
    incident = IncidentService(ledger).report(_incident(_new_shift(ledger)), _OPERATOR)
    with pytest.raises(CvfDenied) as exc:
        IncidentService(ledger).transition(incident.incident_id, _OPERATOR, IncidentStatus.ACKNOWLEDGED)
    assert exc.value.control == "lifecycle"


def test_transition_progresses_and_audits_atomically():
    ledger = InMemoryLedger()
    incident = _reported_with_receipt(ledger)
    IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    resolved = IncidentService(ledger).transition(incident.incident_id, _OPERATOR, IncidentStatus.RESOLVED)
    assert resolved.status.value == "RESOLVED"
    actions = {a.action for a in ledger.audit_entries_for(str(incident.incident_id))}
    assert {"incident.report", "incident.acknowledge", "incident.transition"} <= actions


def test_transition_rejected_under_frozen_shift():
    ledger = InMemoryLedger()
    incident = _reported_with_receipt(ledger)
    IncidentService(ledger).acknowledge(incident.incident_id, Principal(user_id="sup1", role="shift_supervisor"))
    ledger.freeze_shift(incident.shift_id)
    with pytest.raises(ValueError, match="frozen"):
        IncidentService(ledger).transition(incident.incident_id, _OPERATOR, IncidentStatus.RESOLVED)


# --- INC-REV-F2: cross-backend ledger parity ---------------------------------


def _force_equal_created_at(ledger, name, ids):
    """Give every incident in ``ids`` the SAME ``created_at`` so only the
    ``incident_id`` tie-break can determine list order (SPEC R6-A)."""
    fixed = datetime(2026, 1, 1, tzinfo=timezone.utc)
    if name == "in_memory":
        for i in ids:
            ledger.incidents[i].created_at = fixed
    else:
        from sqlalchemy import update as sa_update
        from operations_ledger.tables import incidents as inc_table

        with ledger.engine.begin() as conn:
            for i in ids:
                conn.execute(sa_update(inc_table).where(inc_table.c.incident_id == i).values(created_at=fixed))


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_add_raises_same_controlled_error_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    incident = _incident(_new_shift(ledger))
    ledger.add_incident(incident)
    with pytest.raises(ValueError, match="duplicate incident_id"):
        ledger.add_incident(incident)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_missing_incident_raises_keyerror_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    ghost = _incident(_new_shift(ledger))
    with pytest.raises(KeyError):
        ledger.put_incident(ghost)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_incidents_orders_by_created_at_then_incident_id_when_tied(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    i1 = _incident(shift, summary="a")
    i2 = _incident(shift, summary="b")
    ledger.add_incident(i1)
    ledger.add_incident(i2)
    _force_equal_created_at(ledger, name, [i1.incident_id, i2.incident_id])

    got = ledger.list_incidents_for_shift(shift.shift_id)
    assert [i.incident_id for i in got] == sorted([i1.incident_id, i2.incident_id])
    # Determinism: calling it again returns the identical order, not a
    # coincidence of dict/row iteration order.
    assert [i.incident_id for i in ledger.list_incidents_for_shift(shift.shift_id)] == [i.incident_id for i in got]


# --- AC-11: HTTP -------------------------------------------------------------


def test_http_report_requires_auth(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = http.post("/incidents", json={"shift_id": str(shift.shift_id), "summary": "s"})
    assert res.status_code == 401


def test_http_report_forbidden_for_viewer(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = http.post(
        "/incidents", json={"shift_id": str(shift.shift_id), "summary": "s"}, headers=auth_headers("v1", "viewer")
    )
    assert res.status_code == 403


def test_http_report_extra_field_rejected_422(client):
    ledger, http = client
    shift = _new_shift(ledger)
    res = http.post(
        "/incidents",
        json={"shift_id": str(shift.shift_id), "summary": "s", "approvals": ["fake"]},
        headers=auth_headers("op1", "operator"),
    )
    assert res.status_code == 422


def test_http_get_missing_incident_404(client):
    _ledger, http = client
    res = http.get("/incidents/00000000-0000-4000-8000-000000000099", headers=auth_headers("op1", "operator"))
    assert res.status_code == 404


def test_http_list_incidents_scoped_by_shift_query(client):
    ledger, http = client
    shift = _new_shift(ledger)
    IncidentService(ledger).report(_incident(shift), _OPERATOR)
    IncidentService(ledger).report(_incident(_new_shift(ledger)), _OPERATOR)
    res = http.get("/incidents", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("op1", "operator"))
    assert res.status_code == 200
    assert len(res.json()) == 1
