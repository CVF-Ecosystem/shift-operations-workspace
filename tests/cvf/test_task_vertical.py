"""Task golden vertical: the CVF chain replicated to a second operational domain.

Proves the SAME cvf-runtime gates enforce Task create/transition, plus the
task-specific status lifecycle.

P2B-APPROVER-IDENTITY-RECONCILIATION (SPEC R9): an R2+ task can no longer be
created with an inline ``approvals`` list - the caller must first create a
``TaskCreationIntent`` (the durable, approver-visible target), collect
authenticated approval receipts scoped to it, then submit the SAME payload to
``create_task`` with ``intent_id`` set. R0/R1 tasks are unaffected (no intent,
no approval).
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application import approval_service
from workspace_api.application.task_service import TaskService
from workspace_api.domain.models import ShiftAssignment, User
from operations_domain.models import (
    EvidenceRef,
    RiskClass,
    Shift,
    Task,
    TaskStatus,
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _seed(ledger, shift_id, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _ledger_with_shift():
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    _seed(ledger, shift.shift_id, "sup1", "shift_supervisor")
    return ledger, shift


def _operator():
    return Principal(user_id="op1", role="operator")


def _supervisor():
    return Principal(user_id="sup1", role="shift_supervisor")


def _task(shift, *, risk=RiskClass.R1, evidence=0):
    return Task(
        shift_id=shift.shift_id,
        title="Inspect crane 3",
        risk_class=risk,
        evidence=[EvidenceRef(source_type="message", source_id=f"m{i}") for i in range(evidence)],
    )


def _approve_task_creation(ledger, intent_id, approver_id, role):
    intent = ledger.get_task_creation_intent(intent_id)
    _seed(ledger, intent.shift_id, approver_id, role)
    approval_service.create_approval_receipt(
        ledger,
        Principal(user_id=approver_id, role=role),
        record_type="Task",
        action="task.create",
        record_id=intent_id,
    )


def test_r1_task_created_and_audited():
    ledger, shift = _ledger_with_shift()
    task = _task(shift, risk=RiskClass.R1)
    created = TaskService(ledger).create_task(task, _operator())
    assert created.status == TaskStatus.OPEN
    audit = ledger.audit_entries_for(str(created.task_id))
    assert audit[-1].action == "task.create"


def test_viewer_cannot_create_task():
    ledger, shift = _ledger_with_shift()
    viewer = Principal(user_id="v1", role="viewer")
    with pytest.raises(CvfDenied) as exc:
        TaskService(ledger).create_task(_task(shift), viewer)
    assert exc.value.control == "permission"


def test_r3_task_requires_intent_evidence_and_dual_approval():
    ledger, shift = _ledger_with_shift()
    svc = TaskService(ledger)

    # No intent_id at all for a risk class that requires approval -> refused.
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(_task(shift, risk=RiskClass.R3, evidence=0), _supervisor())
    assert exc.value.control == "approval"
    assert exc.value.http_status == 422

    # An intent can be created even with no evidence (evidence is checked at
    # consume time, not intent-creation time) - but consuming it without
    # evidence is refused by the evidence gate.
    no_evidence_task = _task(shift, risk=RiskClass.R3, evidence=0)
    no_evidence_intent = svc.create_creation_intent(no_evidence_task, _supervisor())
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(no_evidence_task, _supervisor(), intent_id=no_evidence_intent.intent_id)
    assert exc.value.control == "evidence"

    # With evidence, a fresh intent + no receipts -> approval gate refuses.
    task = _task(shift, risk=RiskClass.R3, evidence=1)
    intent = svc.create_creation_intent(task, _supervisor())
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(task, _supervisor(), intent_id=intent.intent_id)
    assert exc.value.control == "approval"

    # Two distinct, authenticated, authorized approvers -> quorum met, created.
    _approve_task_creation(ledger, intent.intent_id, "sup2", "shift_supervisor")
    _approve_task_creation(ledger, intent.intent_id, "mgr1", "responsible_manager")
    created = svc.create_task(task, _supervisor(), intent_id=intent.intent_id)
    assert created.status == TaskStatus.OPEN
    assert created.task_id == intent.intent_id


def test_r0_r1_intent_id_must_be_omitted():
    ledger, shift = _ledger_with_shift()
    svc = TaskService(ledger)
    task = _task(shift, risk=RiskClass.R1)
    with pytest.raises(CvfDenied) as exc:
        svc.create_task(task, _operator(), intent_id=uuid4())
    assert exc.value.control == "approval"
    assert exc.value.http_status == 422


def test_r0_r1_creation_intent_rejected():
    """Creation intents exist only for risk classes that require approval."""
    ledger, shift = _ledger_with_shift()
    svc = TaskService(ledger)
    with pytest.raises(CvfDenied) as exc:
        svc.create_creation_intent(_task(shift, risk=RiskClass.R1), _operator())
    assert exc.value.control == "approval"
    assert exc.value.http_status == 422


def test_valid_status_transition():
    ledger, shift = _ledger_with_shift()
    created = TaskService(ledger).create_task(_task(shift), _operator())
    moved = TaskService(ledger).transition(created.task_id, _operator(), TaskStatus.IN_PROGRESS)
    assert moved.status == TaskStatus.IN_PROGRESS
    assert moved.version == 2


def test_illegal_status_transition_blocked():
    ledger, shift = _ledger_with_shift()
    created = TaskService(ledger).create_task(_task(shift), _operator())
    # OPEN -> DONE is not allowed directly.
    with pytest.raises(ValueError):
        TaskService(ledger).transition(created.task_id, _operator(), TaskStatus.DONE)


def test_done_task_is_terminal():
    ledger, shift = _ledger_with_shift()
    created = TaskService(ledger).create_task(_task(shift), _operator())
    svc = TaskService(ledger)
    svc.transition(created.task_id, _operator(), TaskStatus.IN_PROGRESS)
    svc.transition(created.task_id, _operator(), TaskStatus.DONE)
    with pytest.raises(ValueError):
        svc.transition(created.task_id, _operator(), TaskStatus.IN_PROGRESS)
