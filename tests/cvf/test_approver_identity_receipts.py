"""P2B-APPROVER-IDENTITY-RECONCILIATION vertical test: approval-receipt
mechanics (AC-10, AC-11, AC-23, F15, F16, F17, F18b, F19).

CVF-FILE-SPLIT-GUARD-HARDENING split this out of
`test_approver_identity_reconciliation.py` (uniqueness, version scoping,
ordering invariance, response schema, idempotency, and risk-class/digest
binding for approval receipts); shared fixtures live in
`_approver_identity_support.py`. No test node was deleted or weakened, only
relocated.
"""

from itertools import permutations

import pytest

from cvf_runtime.errors import CvfDenied

from workspace_api.application.services import EventService
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger
from operations_domain.models import DataState, RiskClass
from _auth_test_helpers import auth_headers

from _approver_identity_support import (
    _R3_PAIRS,
    _R4_PAIRS,
    _action,
    _backends,
    _client_for,
    _clear_overrides,
    _confirmer,
    _fill_seats,
    _new_event,
    _new_shift,
    _receipt,
    _user,
)


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
