"""P2B-APPROVER-IDENTITY-RECONCILIATION vertical test: AC-01 through AC-23."""

from datetime import datetime, timedelta, timezone
from itertools import permutations
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application import approval_service
from workspace_api.application.correction_service import CorrectionService
from workspace_api.application.services import EventService
from workspace_api.application.task_service import TaskService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import User
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app
from operations_domain.models import DataState, EvidenceRef, OperationalEvent, RiskClass, Shift, Task
from _auth_test_helpers import auth_headers

_R3_PAIRS = (("sup2", "shift_supervisor"), ("mgr1", "responsible_manager"))
_R4_PAIRS = (("mgr1", "responsible_manager"), ("exec1", "authorized_executive"))

def _sql_ledger(tmp_path, name="approver_identity.sqlite3"):
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)

def _backends(tmp_path): return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]
def _client_for(ledger):
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)
def _clear_overrides(): app.dependency_overrides.pop(get_ledger, None)

def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift

def _new_event(ledger, *, risk=RiskClass.R3, evidence_count=1):
    event = OperationalEvent(
        shift_id=_new_shift(ledger).shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=risk,
        state=DataState.PROPOSED,
        evidence=[EvidenceRef(source_type="message", source_id=f"m{i}") for i in range(evidence_count)],
    )
    ledger.add_event(event)
    return event

def _user(ledger, user_id: str, role: str, *, is_active: bool = True) -> None:
    ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role, is_active=is_active))

def _receipt(ledger, *, record_type, action, record_id, approver_id, role):
    return approval_service.create_approval_receipt(
        ledger, Principal(user_id=approver_id, role=role), record_type=record_type, action=action, record_id=record_id
    )[0]

def _seat(ledger, record_id, approver_id, role, *, record_type="OperationalEvent", action="event.confirm", is_active=True):
    _user(ledger, approver_id, role, is_active=is_active)
    return _receipt(ledger, record_type=record_type, action=action, record_id=record_id, approver_id=approver_id, role=role)

def _fill_seats(ledger, record_id, pairs=_R3_PAIRS, *, record_type="OperationalEvent", action="event.confirm"):
    for approver_id, role in pairs:
        _seat(ledger, record_id, approver_id, role, record_type=record_type, action=action)

def _confirmer():
    return Principal(user_id="sup1", role="shift_supervisor")

def _action(a):
    return a.action if hasattr(a, "action") else a["action"]

def _r3_task_intent(ledger, *, with_receipts=True):
    _user(ledger, "sup1", "shift_supervisor")
    svc = TaskService(ledger)
    task = Task(shift_id=_new_shift(ledger).shift_id, title="Inspect crane", risk_class=RiskClass.R3, evidence=[EvidenceRef(source_type="message", source_id="m1")])
    intent = svc.create_creation_intent(task, _confirmer())
    if with_receipts:
        _fill_seats(ledger, intent.intent_id, record_type="Task", action="task.create")
    return svc, task, intent

def test_ac01_no_receipts_r3_confirm_refused_and_old_approvals_body_422():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert exc.value.control == "approval" and exc.value.http_status == 409
    client = _client_for(ledger)
    try:
        resp = client.post(f"/events/{event.event_id}/confirm", json={"approvals": [{"approver_id": "sup2", "role": "shift_supervisor"}]}, headers=auth_headers("sup1", "shift_supervisor"))
        assert resp.status_code == 422
    finally:
        _clear_overrides()

def test_ac02_receipt_records_authenticated_approver_id_not_a_payload_field():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    _user(ledger, "sup2", "shift_supervisor")
    client = _client_for(ledger)
    try:
        resp = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=auth_headers("sup2", "shift_supervisor"))
        assert resp.status_code == 201
        body = resp.json()
        assert body["approver_id"] == "sup2" and body["approver_role"] == "shift_supervisor"
    finally:
        _clear_overrides()

def test_ac03_unknown_token_rejected_at_auth_layer():
    client = TestClient(app)
    resp = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(uuid4())}, headers={"Authorization": "Bearer not-a-valid-token"})
    assert resp.status_code == 401

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac04_inactive_user_receipt_attempt_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _user(ledger, "sup2", "shift_supervisor", is_active=False)
    with pytest.raises(CvfDenied) as exc:
        _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="sup2", role="shift_supervisor")
    assert exc.value.http_status == 403

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac05_wrong_role_receipt_attempt_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _user(ledger, "op1", "operator")
    with pytest.raises(CvfDenied) as exc:
        _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="op1", role="operator")
    assert exc.value.http_status == 403

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac06_self_approval_alone_fails_for_r2(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R2)
    _seat(ledger, event.event_id, "sup1", "shift_supervisor")
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert exc.value.http_status == 409 and exc.value.control == "approval"

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac07_insufficient_quorum_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _seat(ledger, event.event_id, "sup2", "shift_supervisor")
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert exc.value.http_status == 409

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac08_valid_two_seat_r3_quorum_succeeds_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _fill_seats(ledger, event.event_id)
    confirmed = EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert confirmed.state == DataState.CONFIRMED
    audits = ledger.audit_entries_for(str(event.event_id))
    assert any(_action(a) == "event.confirm" for a in audits)

def test_ac10_uniqueness_repeat_receipt_idempotent():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    _user(ledger, "sup2", "shift_supervisor")
    r1 = _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="sup2", role="shift_supervisor")
    r2 = _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="sup2", role="shift_supervisor")
    assert r1.receipt_id == r2.receipt_id and len(ledger.approval_receipts) == 1
    assert [_action(e) for e in ledger.audit_entries_for(str(event.event_id))].count("approval.create") == 1

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac11_receipt_is_scoped_to_target_version(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _fill_seats(ledger, event.event_id)
    stored = ledger.get_event(event.event_id)  # backend-agnostic version bump
    stored.version += 1
    ledger.put_event(stored)
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert exc.value.http_status == 409

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac14_r3_correction_requires_approval_quorum(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _fill_seats(ledger, event.event_id)
    svc = EventService(ledger, audit=None)
    _user(ledger, "sup1", "shift_supervisor")
    svc.confirm(event.event_id, _confirmer())
    corr_svc = CorrectionService(ledger, audit=None)
    with pytest.raises(CvfDenied) as exc:  # no event.correct receipts yet
        corr_svc.correct_event(event.event_id, _confirmer(), reason="Fix description")
    assert exc.value.http_status == 409
    for approver_id, role in _R3_PAIRS:  # sup2/mgr1 already registered; add correct receipts
        _receipt(ledger, record_type="OperationalEvent", action="event.correct",
                 record_id=event.event_id, approver_id=approver_id, role=role)
    assert corr_svc.correct_event(event.event_id, _confirmer(), reason="Fix description") is not None

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac15_r3_task_creation_requires_creation_intent_and_approval_quorum(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    svc, task, intent = _r3_task_intent(ledger, with_receipts=True)
    created = svc.create_task(task, _confirmer(), intent_id=intent.intent_id)
    assert created.task_id == intent.intent_id

def test_ac17_direct_task_create_without_intent_id_for_r3_fails():
    ledger = InMemoryLedger()
    _user(ledger, "sup1", "shift_supervisor")
    svc = TaskService(ledger)
    task = Task(shift_id=_new_shift(ledger).shift_id, title="Inspect crane", risk_class=RiskClass.R3, evidence=[EvidenceRef(source_type="message", source_id="m1")])
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(task, _confirmer())
    assert exc.value.http_status == 422

def test_ac18_task_payload_substitution_fails():
    ledger = InMemoryLedger()
    svc, task, intent = _r3_task_intent(ledger, with_receipts=True)
    task.title = "Substituted title"
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(task, _confirmer(), intent_id=intent.intent_id)
    assert exc.value.http_status == 409

def test_ac19_non_proposer_cannot_consume_creation_intent():
    ledger = InMemoryLedger()
    svc, task, intent = _r3_task_intent(ledger, with_receipts=True)  # sup2/mgr1 already registered
    other = Principal(user_id="sup2", role="shift_supervisor")
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(task, other, intent_id=intent.intent_id)
    assert exc.value.http_status == 409

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac22_authorized_approver_can_read_intent_snapshot(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    svc, task, intent = _r3_task_intent(ledger, with_receipts=False)
    _user(ledger, "sup2", "shift_supervisor")
    fetched = svc.get_creation_intent(intent.intent_id, Principal(user_id="sup2", role="shift_supervisor"))
    assert fetched.intent_id == intent.intent_id and fetched.payload_digest == intent.payload_digest
    actions = [_action(e) for e in ledger.audit_entries_for(str(intent.intent_id))]
    assert actions.count("task.creation_intent.create") == 1

def test_ac22_unauthorized_user_cannot_read_intent_snapshot():
    ledger = InMemoryLedger()
    svc, task, intent = _r3_task_intent(ledger, with_receipts=False)
    _user(ledger, "op1", "operator")
    with pytest.raises(CvfDenied) as exc:
        svc.get_creation_intent(intent.intent_id, Principal(user_id="op1", role="operator"))
    assert exc.value.http_status == 403

@pytest.mark.parametrize("order", list(permutations(["sup2", "mgr1"])))
def test_ac23_r3_confirm_passes_for_every_receipt_creation_order(order):
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    roles = dict(_R3_PAIRS)
    _fill_seats(ledger, event.event_id, pairs=[(a, roles[a]) for a in order])
    assert EventService(ledger, audit=None).confirm(event.event_id, _confirmer()).state == DataState.CONFIRMED

def test_ac23_higher_authority_receipt_created_before_lower_does_not_false_deny():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    _fill_seats(ledger, event.event_id, pairs=(("mgr1", "responsible_manager"), ("sup2", "shift_supervisor")))
    assert EventService(ledger, audit=None).confirm(event.event_id, _confirmer()).state == DataState.CONFIRMED

def test_f15_confirmer_plus_distinct_valid_r2_approver_succeeds():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R2)
    _user(ledger, "sup1", "shift_supervisor")
    _user(ledger, "sup2", "shift_supervisor")
    _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="sup1", role="shift_supervisor")
    _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="sup2", role="shift_supervisor")
    svc = EventService(ledger, audit=None)
    assert svc.confirm(event.event_id, _confirmer()).state == DataState.CONFIRMED

def test_f15_sole_confirmer_cannot_self_approve_fails():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R2)
    _user(ledger, "sup1", "shift_supervisor")
    _receipt(ledger, record_type="OperationalEvent", action="event.confirm", record_id=event.event_id, approver_id="sup1", role="shift_supervisor")
    svc = EventService(ledger, audit=None)
    with pytest.raises(CvfDenied) as exc:
        svc.confirm(event.event_id, _confirmer())
    assert exc.value.http_status == 409 and exc.value.control == "approval"

def test_f16_wrong_risk_class_on_receipt_cannot_satisfy_quorum():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R4, evidence_count=2)
    _user(ledger, "mgr1", "responsible_manager"); _user(ledger, "exec1", "authorized_executive")
    ledger.add_approval_receipt(domain_models.ApprovalReceipt(record_type="OperationalEvent", record_id=event.event_id, action="event.confirm", target_version=event.version, risk_class="R3", approver_id="mgr1", approver_role="responsible_manager"))
    with pytest.raises(CvfDenied) as exc: EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert exc.value.http_status == 409

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_f16_event_receipt_non_null_digest_rejected_against_null_scope(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _user(ledger, "sup2", "shift_supervisor"); _user(ledger, "mgr1", "responsible_manager")
    for app_id, role in _R3_PAIRS:
        ledger.add_approval_receipt(domain_models.ApprovalReceipt(record_type="OperationalEvent", record_id=event.event_id, action="event.confirm", target_version=event.version, risk_class="R3", payload_digest="bad_digest", approver_id=app_id, approver_role=role))
    with pytest.raises(CvfDenied) as exc: EventService(ledger, audit=None).confirm(event.event_id, _confirmer())
    assert exc.value.http_status == 409

def test_f17_exact_response_schemas_spec_5_4():
    ledger = InMemoryLedger(); shift = _new_shift(ledger); _user(ledger, "sup1", "shift_supervisor"); _user(ledger, "sup2", "shift_supervisor")
    event = _new_event(ledger, risk=RiskClass.R3); client = _client_for(ledger)
    try:
        r1 = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=auth_headers("sup2", "shift_supervisor"))
        assert r1.status_code == 201 and set(r1.json().keys()) == {"receipt_id", "record_type", "record_id", "action", "target_version", "risk_class", "approver_id", "approver_role", "created_at"}
        r2 = client.post("/tasks/creation-intents", json={"shift_id": str(shift.shift_id), "title": "t", "risk_class": "R3"}, headers=auth_headers("sup1", "shift_supervisor"))
        assert r2.status_code == 201 and set(r2.json().keys()) == {"intent_id", "payload_digest", "risk_class", "created_at"}
        r3 = client.get(f"/tasks/creation-intents/{r2.json()['intent_id']}", headers=auth_headers("sup2", "shift_supervisor"))
        assert r3.status_code == 200 and set(r3.json().keys()) == {"intent_id", "payload_snapshot", "payload_digest", "risk_class", "created_by", "created_at"}
    finally: _clear_overrides()

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_f18a_creation_intent_rolls_back_when_audit_fails(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger); _user(ledger, "sup1", "shift_supervisor")
    task = Task(shift_id=shift.shift_id, title="Intent test", risk_class=RiskClass.R3, evidence=[EvidenceRef(source_type="message", source_id="m1")])
    svc = TaskService(ledger)
    class _Boom(Exception): pass
    with patch.object(type(ledger), "append_audit", side_effect=_Boom("simulated failure")):
        with pytest.raises(_Boom): svc.create_creation_intent(task, _confirmer())
    if name == "in_memory":
        assert len(ledger.task_creation_intents) == 0 and not any(_action(e) == "task.creation_intent.create" for e in ledger._audit._entries)
    else:
        from sqlalchemy import select
        from operations_ledger.tables import audit_records, task_creation_intents
        assert len(ledger._fetch_all(select(task_creation_intents))) == 0
        assert not any(r["action"] == "task.creation_intent.create" for r in ledger._fetch_all(select(audit_records)))

@pytest.mark.parametrize("name", ["in_memory", "sql"])
@pytest.mark.parametrize("order", list(permutations(["sup2", "mgr1"])))
def test_f18b_r3_permutations_http_both_backends(tmp_path, name, order):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3); roles = dict(_R3_PAIRS); _user(ledger, "sup1", "shift_supervisor"); client = _client_for(ledger)
    try:
        for a in order:
            _user(ledger, a, roles[a])
            assert client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=auth_headers(a, roles[a])).status_code == 201
        assert client.post(f"/events/{event.event_id}/confirm", json={}, headers=auth_headers("sup1", "shift_supervisor")).status_code == 200
    finally: _clear_overrides()

@pytest.mark.parametrize("name", ["in_memory", "sql"])
@pytest.mark.parametrize("order", list(permutations(["mgr1", "exec1"])))
def test_f18b_r4_permutations_http_both_backends(tmp_path, name, order):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R4, evidence_count=2); roles = dict(_R4_PAIRS); _user(ledger, "sup1", "shift_supervisor"); client = _client_for(ledger)
    try:
        for a in order:
            _user(ledger, a, roles[a])
            assert client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=auth_headers(a, roles[a])).status_code == 201
        assert client.post(f"/events/{event.event_id}/confirm", json={}, headers=auth_headers("sup1", "shift_supervisor")).status_code == 200
    finally: _clear_overrides()

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_f19_idempotency_http_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3); _user(ledger, "sup2", "shift_supervisor"); client = _client_for(ledger)
    try:
        payload = {"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}
        hdrs = auth_headers("sup2", "shift_supervisor")
        r1 = client.post("/approvals", json=payload, headers=hdrs)
        assert r1.status_code == 201 and set(r1.json().keys()) == {"receipt_id", "record_type", "record_id", "action", "target_version", "risk_class", "approver_id", "approver_role", "created_at"}
        d1 = r1.json()
        r2 = client.post("/approvals", json=payload, headers=hdrs)
        assert r2.status_code == 200 and r2.json()["receipt_id"] == d1["receipt_id"]
        if name == "in_memory":
            assert len(ledger.approval_receipts) == 1
            acts = [_action(e) for e in ledger._audit._entries]
        else:
            from sqlalchemy import select
            from operations_ledger.tables import approval_receipts, audit_records
            assert len(ledger._fetch_all(select(approval_receipts))) == 1
            acts = [r["action"] for r in ledger._fetch_all(select(audit_records))]
        assert acts.count("approval.create") == 1
    finally: _clear_overrides()
