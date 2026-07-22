"""P-FIX-2: mutation + audit must be atomic.

A 2026-07-22 independent review (High Finding #5) proved audit was not atomic
with mutation: a failure-injection probe made `append_audit` raise, and
`EventService.confirm` returned an error while the event stayed CONFIRMED with
zero audit records - a governed mutation that "succeeded" with no audit trail.

These tests inject the same failure and assert the OPPOSITE outcome now: the
mutation must not be visible after a failed audit write, for every service
that combines a state change with an audit append, on both ledger backends.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine

from cvf_runtime.audit import AuditLog
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.correction_service import CorrectionService
from workspace_api.application.services import EventService
from workspace_api.application.shift_service import ShiftService
from workspace_api.application.task_service import TaskService
from workspace_api.domain import models as domain_models
from operations_domain.models import (
    DataState,
    OperationalEvent,
    RiskClass,
    Shift,
    ShiftStatus,
    Task,
    TaskStatus,
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _supervisor():
    return Principal(user_id="sup1", role="shift_supervisor")


def _operator():
    return Principal(user_id="op1", role="operator")


def _sql_ledger(tmp_path):
    db = tmp_path / "atomic.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


class _BoomOnAudit(Exception):
    pass


def _raise_on_audit(*args, **kwargs):
    raise _BoomOnAudit("simulated audit sink failure")


def test_event_confirm_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    event = OperationalEvent(
        shift_id=shift.shift_id, event_type="equipment_downtime",
        title="Crane 3 stopped", risk_class=RiskClass.R0, state=DataState.PROPOSED,
    )
    ledger.add_event(event)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            EventService(ledger, AuditLog()).confirm(event.event_id, _supervisor(), approvals=[])

    fetched = ledger.get_event(event.event_id)
    assert fetched.state == DataState.PROPOSED, "mutation must not survive a failed audit write"
    assert fetched.version == 1


def test_event_confirm_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    event = OperationalEvent(
        shift_id=shift.shift_id, event_type="equipment_downtime",
        title="Crane 3 stopped", risk_class=RiskClass.R0, state=DataState.PROPOSED,
    )
    ledger.add_event(event)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            EventService(ledger, AuditLog()).confirm(event.event_id, _supervisor(), approvals=[])

    fetched = ledger.get_event(event.event_id)
    assert fetched.state == DataState.PROPOSED, "mutation must not survive a failed audit write"
    assert fetched.version == 1


def test_correction_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    event = OperationalEvent(
        shift_id=shift.shift_id, event_type="equipment_downtime",
        title="Crane 3 stopped", risk_class=RiskClass.R0, state=DataState.CONFIRMED,
    )
    ledger.add_event(event)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CorrectionService(ledger, AuditLog()).correct_event(
                event.event_id, _supervisor(), reason="fix title", approvals=[]
            )

    fetched = ledger.get_event(event.event_id)
    assert fetched.state == DataState.CONFIRMED, "event must not be moved to CORRECTED"
    assert fetched.version == 1
    assert ledger.corrections_for(event.event_id) == [], "correction record must not survive"


def test_correction_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    event = OperationalEvent(
        shift_id=shift.shift_id, event_type="equipment_downtime",
        title="Crane 3 stopped", risk_class=RiskClass.R0, state=DataState.CONFIRMED,
    )
    ledger.add_event(event)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CorrectionService(ledger, AuditLog()).correct_event(
                event.event_id, _supervisor(), reason="fix title", approvals=[]
            )

    fetched = ledger.get_event(event.event_id)
    assert fetched.state == DataState.CONFIRMED, "event must not be moved to CORRECTED"
    assert fetched.version == 1
    assert ledger.corrections_for(event.event_id) == [], "correction record must not survive"


def test_task_create_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="Inspect crane")

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            TaskService(ledger).create_task(task, _operator(), approvals=[])

    with pytest.raises(KeyError):
        ledger.get_task(task.task_id)


def test_task_create_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="Inspect crane")

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            TaskService(ledger).create_task(task, _operator(), approvals=[])

    with pytest.raises(KeyError):
        ledger.get_task(task.task_id)


def test_task_transition_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="Inspect crane")
    ledger.add_task(task)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            TaskService(ledger).transition(task.task_id, _operator(), TaskStatus.IN_PROGRESS)

    fetched = ledger.get_task(task.task_id)
    assert fetched.status == TaskStatus.OPEN, "task status must not advance"
    assert fetched.version == 1


def test_task_transition_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="Inspect crane")
    ledger.add_task(task)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            TaskService(ledger).transition(task.task_id, _operator(), TaskStatus.IN_PROGRESS)

    fetched = ledger.get_task(task.task_id)
    assert fetched.status == TaskStatus.OPEN, "task status must not advance"
    assert fetched.version == 1


def test_shift_freeze_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    ledger.close_shift(shift.shift_id)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).freeze(
                shift.shift_id, _supervisor(),
                override_unimplemented_prerequisites=True, override_reason="test",
            )

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.CLOSED, "freeze must not survive a failed audit write"


def test_shift_freeze_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    ledger.close_shift(shift.shift_id)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).freeze(
                shift.shift_id, _supervisor(),
                override_unimplemented_prerequisites=True, override_reason="test",
            )

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.CLOSED, "freeze must not survive a failed audit write"
