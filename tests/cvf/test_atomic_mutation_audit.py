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

from workspace_api.application import approval_service
from workspace_api.application.correction_service import CorrectionService
from workspace_api.application.handover_service import HandoverService
from workspace_api.application.report_service import ReportService
from workspace_api.application.services import EventService
from workspace_api.application.shift_service import ShiftService
from workspace_api.application.task_service import TaskService
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from operations_domain.models import (
    DataState,
    OperationalEvent,
    ReportStatus,
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


def _seed(ledger, shift_id, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    _seed(ledger, shift.shift_id, "sup1", "shift_supervisor")
    return shift


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _receiving_supervisor():
    return Principal(user_id="sup2", role="shift_supervisor")


def _make_ready_handover(ledger, shift):
    """HOV-AUTH-F4 repair: a genuine server-derived, reviewed and
    ACKNOWLEDGED (empty) handover - the real `open_handover_items_linked`
    freeze prerequisite - via the same HandoverService application chain
    every other test uses, never a direct terminal-state insertion or mock."""
    now = datetime.now(timezone.utc)
    dest = Shift(name="Next", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(dest)
    _seed(ledger, dest.shift_id, "sup2", "shift_supervisor")
    svc = HandoverService(ledger)
    handover = svc.create(shift.shift_id, dest.shift_id, _operator())
    handover = svc.review(handover.handover_id, _supervisor())
    return svc.acknowledge(handover.handover_id, _receiving_supervisor())


def _make_ready_report(ledger, shift):
    """A current, APPROVED END_SHIFT report - the real `report_approved`
    freeze prerequisite (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE)."""
    svc = ReportService(ledger)
    report = svc.generate(shift.shift_id, _operator())
    report = svc.submit_review(report.report_id, _operator())
    _seed(ledger, shift.shift_id, "sup3", "shift_supervisor")
    approval_service.create_approval_receipt(
        ledger, Principal(user_id="sup3", role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    return svc.approve(report.report_id, _supervisor())


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
            EventService(ledger, AuditLog()).confirm(event.event_id, _supervisor())

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
            EventService(ledger, AuditLog()).confirm(event.event_id, _supervisor())

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
                event.event_id, _supervisor(), reason="fix title"
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
                event.event_id, _supervisor(), reason="fix title"
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
            TaskService(ledger).create_task(task, _operator())

    with pytest.raises(KeyError):
        ledger.get_task(task.task_id)


def test_task_create_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="Inspect crane")

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            TaskService(ledger).create_task(task, _operator())

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
    _make_ready_handover(ledger, shift)
    report = _make_ready_report(ledger, shift)

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).freeze(shift.shift_id, _supervisor())

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.CLOSED, "freeze must not survive a failed audit write"
    # R20: readiness + Report FROZEN transition + Shift freeze mutation +
    # both audits share one transaction - the injected failure must leave
    # every effect of THIS attempt unwritten too (the earlier handover/report
    # setup's own audits are untouched, and the Report must not have moved).
    freeze_actions = {e.action for e in ledger.audit_entries_for(str(shift.shift_id))}
    assert "shift.freeze" not in freeze_actions
    assert ledger.get_report(report.report_id).status == ReportStatus.APPROVED


def test_shift_freeze_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    ledger.close_shift(shift.shift_id)
    _make_ready_handover(ledger, shift)
    report = _make_ready_report(ledger, shift)

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            ShiftService(ledger).freeze(shift.shift_id, _supervisor())

    fetched = ledger.get_shift(shift.shift_id)
    assert fetched.status == ShiftStatus.CLOSED, "freeze must not survive a failed audit write"
    freeze_actions = {e["action"] for e in ledger.audit_entries_for(str(shift.shift_id))}
    assert "shift.freeze" not in freeze_actions
    assert ledger.get_report(report.report_id).status == ReportStatus.APPROVED
