"""Handover golden vertical (P2A-HANDOVER-VERTICAL): server-derived carry-over,
sender review, distinct receiver acknowledgement. Freeze integration is
exercised in test_freeze_invariant.py / test_shift_close_freeze_interaction.py,
not duplicated here.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.handover_service import HandoverService, compute_source_digest
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment
from operations_domain.models import EvidenceRef, HandoverStatus, Incident, Shift, Task, TaskStatus
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")
_RECEIVER = Principal(user_id="sup2", role="shift_supervisor")


def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'handovers.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "handovers.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _seed(ledger, shift_id, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _shift(ledger, **kw):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8), **kw)
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    _seed(ledger, shift.shift_id, "sup1", "shift_supervisor")
    return shift


def _pair(ledger):
    s1, s2 = _shift(ledger), _shift(ledger)
    _seed(ledger, s2.shift_id, "sup2", "shift_supervisor")
    return s1, s2


def _action_of(entry) -> str:
    """Normalize InMemoryLedger AuditRecord objects vs SqlLedger dict rows."""
    return entry.action if hasattr(entry, "action") else entry["action"]


@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


# --- AC-01: model/shim identity, lifecycle matrix ---------------------------

def test_shim_identity_and_status_values():
    from operations_domain import models as canonical
    assert domain_models.Handover is canonical.Handover
    assert domain_models.HandoverItem is canonical.HandoverItem
    assert domain_models.HandoverStatus is canonical.HandoverStatus
    assert {s.value for s in HandoverStatus} == {"DRAFT", "REVIEWED", "ACKNOWLEDGED"}

def test_acknowledged_is_derived_from_status_and_serializes():
    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    created = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    assert created.acknowledged is False
    assert created.model_dump(mode="json")["acknowledged"] is False

def test_invalid_lifecycle_transitions_rejected():
    """Same from/to shift, DRAFT->ACKNOWLEDGED direct, re-review, post-ACKNOWLEDGED all fail."""
    ledger = InMemoryLedger()
    lone_shift = _shift(ledger)
    with pytest.raises(CvfDenied) as exc:
        HandoverService(ledger).create(lone_shift.shift_id, lone_shift.shift_id, _OPERATOR)
    assert exc.value.control == "lifecycle"

    s1, s2 = _pair(ledger)
    svc = HandoverService(ledger)
    h = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    with pytest.raises(CvfDenied) as exc:
        svc.acknowledge(h.handover_id, _RECEIVER)
    assert exc.value.control == "lifecycle"

    h = svc.review(h.handover_id, _SUPERVISOR)
    with pytest.raises(CvfDenied):
        svc.review(h.handover_id, _SUPERVISOR)

    h = svc.acknowledge(h.handover_id, _RECEIVER)
    with pytest.raises(CvfDenied):
        svc.review(h.handover_id, _SUPERVISOR)

# --- AC-03/AC-23: permission, distinct receiver, no assignment claim --------

def test_create_rejects_viewer_role():
    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    with pytest.raises(CvfDenied) as exc:
        HandoverService(ledger).create(s1.shift_id, s2.shift_id, Principal(user_id="v1", role="viewer"))
    assert exc.value.control == "permission"

def test_acknowledge_requires_distinct_receiver_and_makes_no_assignment_claim():
    """AC-23: no assignment registry exists - bounded to receiver identity only."""
    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    svc = HandoverService(ledger)
    h = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    h = svc.review(h.handover_id, _SUPERVISOR)
    with pytest.raises(CvfDenied) as exc:
        svc.acknowledge(h.handover_id, _SUPERVISOR)
    assert exc.value.control == "lifecycle" and "differ" in str(exc.value)

    acknowledged = svc.acknowledge(h.handover_id, _RECEIVER)
    assert not hasattr(acknowledged, "assigned_to_shift")
    assert acknowledged.received_by == "sup2"

# --- AC-04/AC-07: server-derived snapshot and digest ------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_derives_open_task_and_incident_but_excludes_done_and_closed(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    open_task = Task(shift_id=s1.shift_id, title="Inspect crane")
    done_task = Task(shift_id=s1.shift_id, title="Already done", status=TaskStatus.DONE)
    open_incident = Incident(shift_id=s1.shift_id, summary="Crane stopped")
    ledger.add_task(open_task)
    ledger.add_task(done_task)
    ledger.add_incident(open_incident)

    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    ids = {i.source_record_id for i in handover.items}
    assert open_task.task_id in ids
    assert open_incident.incident_id in ids
    assert done_task.task_id not in ids

def test_digest_deterministic_and_empty_handover_valid():
    shift = Shift(name="A", starts_at=datetime.now(timezone.utc), ends_at=datetime.now(timezone.utc) + timedelta(hours=1))
    e1, e2 = EvidenceRef(source_type="message", source_id="m1"), EvidenceRef(source_type="message", source_id="m2")
    t1 = Task(shift_id=shift.shift_id, title="x", evidence=[e1, e2])
    t2 = t1.model_copy(update={"evidence": [e2, e1]})
    assert compute_source_digest("Task", t1) == compute_source_digest("Task", t2)

    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    assert handover.items == [] and handover.status == HandoverStatus.DRAFT

# --- AC-10: stale/new/mutated source invalidates prior snapshot ------------

def test_review_rejects_stale_snapshot_after_new_open_work_appears():
    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    ledger.add_task(Task(shift_id=s1.shift_id, title="Appeared after create"))
    with pytest.raises(CvfDenied) as exc:
        HandoverService(ledger).review(handover.handover_id, _SUPERVISOR)
    assert exc.value.control == "lifecycle"
    assert "snapshot" in str(exc.value)

def test_acknowledge_rejects_stale_snapshot_after_source_task_mutates():
    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    task = Task(shift_id=s1.shift_id, title="Inspect crane")
    ledger.add_task(task)
    svc = HandoverService(ledger)
    handover = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    handover = svc.review(handover.handover_id, _SUPERVISOR)

    mutated = ledger.get_task(task.task_id)
    mutated.status = TaskStatus.IN_PROGRESS
    ledger.put_task(mutated)

    with pytest.raises(CvfDenied) as exc:
        svc.acknowledge(handover.handover_id, _RECEIVER)
    assert exc.value.control == "lifecycle"

# --- AC-04/AC-09: shift/actor invariants rechecked at every transition ------

def test_shift_state_rechecked_at_create_and_review():
    ledger = InMemoryLedger()
    s1, s2 = _pair(ledger)
    ledger.close_shift(s2.shift_id)
    with pytest.raises(CvfDenied) as exc:
        HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    assert exc.value.control == "lifecycle"

    s3, s4 = _pair(ledger)
    ledger.freeze_shift(s3.shift_id)
    with pytest.raises(CvfDenied) as exc:
        HandoverService(ledger).create(s3.shift_id, s4.shift_id, _OPERATOR)
    assert exc.value.control == "freeze"

    s5, s6 = _pair(ledger)
    handover = HandoverService(ledger).create(s5.shift_id, s6.shift_id, _OPERATOR)
    ledger.close_shift(s6.shift_id)
    with pytest.raises(CvfDenied) as exc:
        HandoverService(ledger).review(handover.handover_id, _SUPERVISOR)
    assert exc.value.control == "lifecycle"

# --- AC-06/AC-08/AC-12: ledger parity and atomic persistence ----------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_review_acknowledge_persist_and_audit_atomically_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    _seed(ledger, s2.shift_id, "sup2", "shift_supervisor")
    ledger.add_task(Task(shift_id=s1.shift_id, title="Inspect crane"))
    svc = HandoverService(ledger)
    h = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    assert len(ledger.get_handover(h.handover_id).items) == 1
    assert len(ledger.audit_entries_for(str(h.handover_id))) == 1

    h = svc.review(h.handover_id, _SUPERVISOR)
    assert h.status == HandoverStatus.REVIEWED
    h = svc.acknowledge(h.handover_id, _RECEIVER)
    assert h.status == HandoverStatus.ACKNOWLEDGED and h.acknowledged is True
    actions = {_action_of(a) for a in ledger.audit_entries_for(str(h.handover_id))}
    assert {"handover.create", "handover.review", "handover.acknowledge"} <= actions

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_get_missing_raises_keyerror_and_list_orders_deterministically(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    with pytest.raises(KeyError):
        ledger.get_handover(uuid4())

    s1, s2 = _shift(ledger), _shift(ledger)
    svc = HandoverService(ledger)
    h1 = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    h2 = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    got = ledger.list_handovers_for_shift(s1.shift_id)
    assert {h.handover_id for h in got} == {h1.handover_id, h2.handover_id}
    assert [h.handover_id for h in got] == [h.handover_id for h in ledger.list_handovers_for_shift(s1.shift_id)]

# --- AC-13: HTTP -------------------------------------------------------------

def test_http_create_requires_auth_permission_and_rejects_extra_fields(client):
    ledger, http = client
    s1, s2 = _pair(ledger)
    body = {"from_shift_id": str(s1.shift_id), "to_shift_id": str(s2.shift_id)}
    assert http.post("/handovers", json=body).status_code == 401
    assert http.post("/handovers", json=body, headers=auth_headers("v1", "viewer")).status_code == 403
    extra = {**body, "items": []}
    assert http.post("/handovers", json=extra, headers=auth_headers("op1", "operator")).status_code == 422

def test_http_get_missing_404_and_list_scoped_by_from_shift_id_query(client):
    ledger, http = client
    res = http.get("/handovers/00000000-0000-4000-8000-000000000099", headers=auth_headers("op1", "operator"))
    assert res.status_code == 404

    s1, s2 = _shift(ledger), _shift(ledger)
    HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    HandoverService(ledger).create(_shift(ledger).shift_id, s2.shift_id, _OPERATOR)
    res = http.get("/handovers", params={"from_shift_id": str(s1.shift_id)}, headers=auth_headers("op1", "operator"))
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_http_review_then_acknowledge_over_full_route_chain(client):
    ledger, http = client
    s1, s2 = _shift(ledger), _shift(ledger)
    _seed(ledger, s2.shift_id, "sup2", "shift_supervisor")
    create_res = http.post(
        "/handovers",
        json={"from_shift_id": str(s1.shift_id), "to_shift_id": str(s2.shift_id)},
        headers=auth_headers("op1", "operator"),
    )
    handover_id = create_res.json()["handover_id"]

    review_res = http.post(f"/handovers/{handover_id}/review", json={}, headers=auth_headers("sup1", "shift_supervisor"))
    assert review_res.status_code == 200, review_res.text
    assert review_res.json()["status"] == "REVIEWED"

    ack_res = http.post(f"/handovers/{handover_id}/acknowledge", json={}, headers=auth_headers("sup2", "shift_supervisor"))
    assert ack_res.status_code == 200, ack_res.text
    assert ack_res.json()["status"] == "ACKNOWLEDGED"
    assert ack_res.json()["acknowledged"] is True
