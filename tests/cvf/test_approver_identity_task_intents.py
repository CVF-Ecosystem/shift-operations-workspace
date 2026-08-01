"""P2B-APPROVER-IDENTITY-RECONCILIATION vertical test: task creation-intent
lifecycle (AC-15, AC-17, AC-18, AC-19, AC-22, F18a).

CVF-FILE-SPLIT-GUARD-HARDENING split this out of
`test_approver_identity_reconciliation.py`; shared fixtures live in
`_approver_identity_support.py`. No test node was deleted or weakened, only
relocated.
"""

from unittest.mock import patch

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application.task_service import TaskService
from workspace_api.infrastructure.repository import InMemoryLedger
from operations_domain.models import EvidenceRef, RiskClass, Task

from _approver_identity_support import (
    _action,
    _assign,
    _backends,
    _confirmer,
    _new_shift,
    _r3_task_intent,
    _user,
)


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
    _assign(ledger, intent.shift_id, "sup2", "shift_supervisor")
    fetched = svc.get_creation_intent(intent.intent_id, Principal(user_id="sup2", role="shift_supervisor"))
    assert fetched.intent_id == intent.intent_id and fetched.payload_digest == intent.payload_digest
    actions = [_action(e) for e in ledger.audit_entries_for(str(intent.intent_id))]
    assert actions.count("task.creation_intent.create") == 1

def test_ac22_unauthorized_user_cannot_read_intent_snapshot():
    ledger = InMemoryLedger()
    svc, task, intent = _r3_task_intent(ledger, with_receipts=False)
    _assign(ledger, intent.shift_id, "op1", "operator")
    with pytest.raises(CvfDenied) as exc:
        svc.get_creation_intent(intent.intent_id, Principal(user_id="op1", role="operator"))
    assert exc.value.http_status == 403

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
