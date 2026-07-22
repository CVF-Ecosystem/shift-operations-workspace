"""P-FIX-1: freeze as a real cross-record invariant.

A 2026-07-22 independent review (Critical Finding #1) proved freeze was
bypassable: freeze_shift had no identity/permission/prerequisite check, and
mutations on a frozen shift's children were not blocked in SqlLedger while
InMemoryLedger blocked only NEW records, not updates. These tests exercise the
fixed behavior end-to-end (service + both ledger backends), not just a single
gate function in isolation.
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.audit import AuditLog
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
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _supervisor():
    return Principal(user_id="sup1", role="shift_supervisor")


def _operator():
    return Principal(user_id="op1", role="operator")


def _sql_ledger(tmp_path):
    db = tmp_path / "freeze.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _in_memory_shift():
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return ledger, shift


# --- ShiftService.freeze prerequisite checks ---------------------------------

def test_freeze_denied_without_permission():
    ledger, shift = _in_memory_shift()
    viewer = Principal(user_id="v1", role="viewer")
    ledger.close_shift(shift.shift_id)
    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, viewer)
    assert exc.value.control == "permission"


def test_freeze_denied_when_shift_not_closed():
    ledger, shift = _in_memory_shift()
    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, _supervisor())
    assert exc.value.control == "freeze"
    assert "shift_closed" in str(exc.value) or "CLOSED" in str(exc.value)


def test_freeze_denied_without_explicit_override():
    ledger, shift = _in_memory_shift()
    ledger.close_shift(shift.shift_id)
    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, _supervisor())
    assert exc.value.control == "freeze"
    assert "override" in str(exc.value)


def test_freeze_denied_with_override_but_no_reason():
    ledger, shift = _in_memory_shift()
    ledger.close_shift(shift.shift_id)
    with pytest.raises(CvfDenied):
        ShiftService(ledger).freeze(
            shift.shift_id, _supervisor(), override_unimplemented_prerequisites=True
        )


def test_freeze_succeeds_with_full_chain_and_audits_override():
    ledger, shift = _in_memory_shift()
    ledger.close_shift(shift.shift_id)
    frozen = ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="Report/handover model not implemented yet (P2-D/P5-A)",
    )
    assert frozen.status == ShiftStatus.FROZEN
    entries = ledger.audit_entries_for(str(shift.shift_id))
    actions = {e.action for e in entries}
    assert "shift.freeze" in actions
    assert "shift.freeze_override_unimplemented_prerequisites" in actions


# --- cross-record invariant: frozen shift blocks child mutation --------------

@pytest.mark.parametrize("backend", ["in_memory", "sql"])
def test_event_confirm_blocked_after_parent_shift_frozen(backend, tmp_path):
    if backend == "in_memory":
        ledger, shift = _in_memory_shift()
    else:
        ledger = _sql_ledger(tmp_path)
        now = datetime.now(timezone.utc)
        shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
        ledger.create_shift(shift)

    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=RiskClass.R0,
        state=DataState.PROPOSED,
    )
    ledger.add_event(event)

    ledger.close_shift(shift.shift_id)
    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    with pytest.raises(ValueError, match="frozen"):
        EventService(ledger, AuditLog()).confirm(event.event_id, _supervisor(), approvals=[])


@pytest.mark.parametrize("backend", ["in_memory", "sql"])
def test_task_transition_blocked_after_parent_shift_frozen(backend, tmp_path):
    if backend == "in_memory":
        ledger, shift = _in_memory_shift()
    else:
        ledger = _sql_ledger(tmp_path)
        now = datetime.now(timezone.utc)
        shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
        ledger.create_shift(shift)

    task = Task(shift_id=shift.shift_id, title="Inspect crane")
    ledger.add_task(task)

    ledger.close_shift(shift.shift_id)
    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    from operations_domain.models import TaskStatus

    with pytest.raises(ValueError, match="frozen"):
        TaskService(ledger).transition(task.task_id, _operator(), TaskStatus.IN_PROGRESS)


@pytest.mark.parametrize("backend", ["in_memory", "sql"])
def test_new_event_rejected_on_frozen_shift(backend, tmp_path):
    if backend == "in_memory":
        ledger, shift = _in_memory_shift()
    else:
        ledger = _sql_ledger(tmp_path)
        now = datetime.now(timezone.utc)
        shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
        ledger.create_shift(shift)

    ledger.close_shift(shift.shift_id)
    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    new_event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="late report",
        risk_class=RiskClass.R0,
    )
    with pytest.raises(ValueError, match="frozen"):
        ledger.add_event(new_event)


def test_correction_still_allowed_after_freeze_in_memory():
    ledger, shift = _in_memory_shift()
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=RiskClass.R0,
        state=DataState.CONFIRMED,
    )
    ledger.add_event(event)
    ledger.close_shift(shift.shift_id)
    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    # Correction is the one permitted post-freeze mutation path.
    correction = CorrectionService(ledger, AuditLog()).correct_event(
        event.event_id, _supervisor(), reason="fix title", approvals=[]
    )
    assert correction.new_version == event.version + 0 or correction.new_version >= 1
    fetched = ledger.get_event(event.event_id)
    assert fetched.version >= 2
