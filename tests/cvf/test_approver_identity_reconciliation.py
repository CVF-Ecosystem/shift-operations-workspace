"""P2B-APPROVER-IDENTITY-RECONCILIATION vertical test: core identity/authority
gating (AC-01 through AC-08, AC-14).

CVF-FILE-SPLIT-GUARD-HARDENING split the remaining AC-01..AC-23 coverage into
`test_approver_identity_receipts.py` (receipt mechanics: uniqueness, version
scoping, ordering invariance, response schema, idempotency, risk-class/digest
binding) and `test_approver_identity_task_intents.py` (task creation-intent
lifecycle); shared fixtures moved to `_approver_identity_support.py`. No test
node was deleted or weakened, only relocated.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied

from workspace_api.application.correction_service import CorrectionService
from workspace_api.application.services import EventService
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app
from operations_domain.models import DataState, RiskClass
from _auth_test_helpers import auth_headers

from _approver_identity_support import (
    _R3_PAIRS,
    _action,
    _assign,
    _backends,
    _client_for,
    _clear_overrides,
    _confirmer,
    _fill_seats,
    _new_event,
    _receipt,
    _seat,
    _user,
)


def test_ac01_no_receipts_r3_confirm_refused_and_old_approvals_body_422():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer(), expected_version=event.version)
    assert exc.value.control == "approval" and exc.value.http_status == 409
    client = _client_for(ledger)
    try:
        resp = client.post(
            f"/events/{event.event_id}/confirm",
            json={"expected_version": event.version, "approvals": [{"approver_id": "sup2", "role": "shift_supervisor"}]},
            headers=auth_headers("sup1", "shift_supervisor"),
        )
        assert resp.status_code == 422
    finally:
        _clear_overrides()

def test_ac02_receipt_records_authenticated_approver_id_not_a_payload_field():
    ledger = InMemoryLedger()
    event = _new_event(ledger, risk=RiskClass.R3)
    _assign(ledger, event.shift_id, "sup2", "shift_supervisor")
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
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer(), expected_version=event.version)
    assert exc.value.http_status == 409 and exc.value.control == "approval"

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac07_insufficient_quorum_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _seat(ledger, event.event_id, "sup2", "shift_supervisor")
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit=None).confirm(event.event_id, _confirmer(), expected_version=event.version)
    assert exc.value.http_status == 409

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac08_valid_two_seat_r3_quorum_succeeds_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _fill_seats(ledger, event.event_id)
    confirmed = EventService(ledger, audit=None).confirm(
        event.event_id, _confirmer(), expected_version=event.version
    )
    assert confirmed.state == DataState.CONFIRMED
    audits = ledger.audit_entries_for(str(event.event_id))
    assert any(_action(a) == "event.confirm" for a in audits)

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_ac14_r3_correction_requires_approval_quorum(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    event = _new_event(ledger, risk=RiskClass.R3)
    _fill_seats(ledger, event.event_id)
    svc = EventService(ledger, audit=None)
    _user(ledger, "sup1", "shift_supervisor")
    confirmed = svc.confirm(event.event_id, _confirmer(), expected_version=event.version)
    corr_svc = CorrectionService(ledger, audit=None)
    with pytest.raises(CvfDenied) as exc:  # no event.correct receipts yet
        corr_svc.correct_event(
            event.event_id, _confirmer(), reason="Fix description", expected_version=confirmed.version
        )
    assert exc.value.http_status == 409
    for approver_id, role in _R3_PAIRS:  # sup2/mgr1 already registered; add correct receipts
        _receipt(ledger, record_type="OperationalEvent", action="event.correct",
                 record_id=event.event_id, approver_id=approver_id, role=role)
    assert corr_svc.correct_event(
        event.event_id, _confirmer(), reason="Fix description", expected_version=confirmed.version
    ) is not None
