"""Task golden vertical: the CVF chain replicated to a second operational domain.

Proves the SAME cvf-runtime gates enforce Task create/transition, plus the
task-specific status lifecycle.
"""

from datetime import datetime, timedelta, timezone

import pytest

from cvf_runtime.approval import Approval
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application.task_service import TaskService
from workspace_api.domain.models import (
    EvidenceRef,
    RiskClass,
    Shift,
    Task,
    TaskStatus,
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _ledger_with_shift():
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
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


def test_r1_task_created_and_audited():
    ledger, shift = _ledger_with_shift()
    task = _task(shift, risk=RiskClass.R1)
    created = TaskService(ledger).create_task(task, _operator(), approvals=[])
    assert created.status == TaskStatus.OPEN
    audit = ledger.audit_entries_for(str(created.task_id))
    assert audit[-1].action == "task.create"


def test_viewer_cannot_create_task():
    ledger, shift = _ledger_with_shift()
    viewer = Principal(user_id="v1", role="viewer")
    with pytest.raises(CvfDenied) as exc:
        TaskService(ledger).create_task(_task(shift), viewer, approvals=[])
    assert exc.value.control == "permission"


def test_r3_task_requires_evidence_and_dual_approval():
    ledger, shift = _ledger_with_shift()
    # R3 with no evidence -> evidence gate refuses first.
    with pytest.raises(CvfDenied) as exc:
        TaskService(ledger).create_task(
            _task(shift, risk=RiskClass.R3, evidence=0), _supervisor(), approvals=[]
        )
    assert exc.value.control == "evidence"

    # R3 with evidence but no quorum -> approval gate refuses.
    with pytest.raises(CvfDenied) as exc:
        TaskService(ledger).create_task(
            _task(shift, risk=RiskClass.R3, evidence=1),
            _supervisor(),
            approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
        )
    assert exc.value.control == "approval"

    # R3 with evidence + full dual quorum -> created.
    created = TaskService(ledger).create_task(
        _task(shift, risk=RiskClass.R3, evidence=1),
        _supervisor(),
        approvals=[
            Approval(approver_id="sup2", role="shift_supervisor"),
            Approval(approver_id="mgr1", role="responsible_manager"),
        ],
    )
    assert created.status == TaskStatus.OPEN


def test_valid_status_transition():
    ledger, shift = _ledger_with_shift()
    created = TaskService(ledger).create_task(_task(shift), _operator(), approvals=[])
    moved = TaskService(ledger).transition(created.task_id, _operator(), TaskStatus.IN_PROGRESS)
    assert moved.status == TaskStatus.IN_PROGRESS
    assert moved.version == 2


def test_illegal_status_transition_blocked():
    ledger, shift = _ledger_with_shift()
    created = TaskService(ledger).create_task(_task(shift), _operator(), approvals=[])
    # OPEN -> DONE is not allowed directly.
    with pytest.raises(ValueError):
        TaskService(ledger).transition(created.task_id, _operator(), TaskStatus.DONE)


def test_done_task_is_terminal():
    ledger, shift = _ledger_with_shift()
    created = TaskService(ledger).create_task(_task(shift), _operator(), approvals=[])
    svc = TaskService(ledger)
    svc.transition(created.task_id, _operator(), TaskStatus.IN_PROGRESS)
    svc.transition(created.task_id, _operator(), TaskStatus.DONE)
    with pytest.raises(ValueError):
        svc.transition(created.task_id, _operator(), TaskStatus.IN_PROGRESS)
