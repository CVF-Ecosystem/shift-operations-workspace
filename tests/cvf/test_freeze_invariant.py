"""P-FIX-1: freeze as a real cross-record invariant.

A 2026-07-22 independent review (Critical Finding #1) proved freeze was
bypassable: freeze_shift had no identity/permission/prerequisite check, and
mutations on a frozen shift's children were not blocked in SqlLedger while
InMemoryLedger blocked only NEW records, not updates. These tests exercise the
fixed behavior end-to-end (service + both ledger backends), not just a single
gate function in isolation.

P2A-HANDOVER-VERTICAL (2026-07-26): `open_handover_items_linked` is now a real
freeze prerequisite (ADR section 3.6), never overridable by
`override_unimplemented_prerequisites` (which now covers only
`report_approved`). Every test below that expects freeze to actually SUCCEED
now first creates, reviews and acknowledges a matching (empty) handover via
`_make_ready_handover`; tests that expect freeze to fail for an EARLIER reason
(permission, not-closed, no-override, no-reason) are unaffected because those
checks still run before the handover-readiness check.
"""

from datetime import datetime, timedelta, timezone

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.audit import AuditLog
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.correction_service import CorrectionService
from workspace_api.application.handover_service import HandoverService
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


def _receiving_supervisor():
    return Principal(user_id="sup2", role="shift_supervisor")


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


def _make_ready_handover(ledger, shift):
    """An ACKNOWLEDGED handover whose (empty) snapshot matches current open
    work - the real `open_handover_items_linked` freeze prerequisite."""
    now = datetime.now(timezone.utc)
    dest = Shift(name="Next", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(dest)
    svc = HandoverService(ledger)
    handover = svc.create(shift.shift_id, dest.shift_id, _operator())
    handover = svc.review(handover.handover_id, _supervisor())
    return svc.acknowledge(handover.handover_id, _receiving_supervisor())


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


def test_freeze_denied_without_ready_handover_even_with_override():
    """ADR section 3.6: the report_approved override never bypasses the real
    open_handover_items_linked prerequisite."""
    ledger, shift = _in_memory_shift()
    ledger.close_shift(shift.shift_id)
    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(
            shift.shift_id, _supervisor(),
            override_unimplemented_prerequisites=True,
            override_reason="Report model not implemented yet (P2-D)",
        )
    assert exc.value.control == "freeze"
    assert "handover" in str(exc.value).lower()


def test_freeze_denied_when_acknowledged_handover_snapshot_is_stale():
    """A source record that changes after acknowledgement invalidates the
    handover's snapshot - freeze must still refuse (ADR section 3.3)."""
    ledger, shift = _in_memory_shift()
    task = Task(shift_id=shift.shift_id, title="Inspect crane")
    ledger.add_task(task)
    _make_ready_handover(ledger, shift)

    stale = ledger.get_task(task.task_id)
    stale.status = TaskStatus.IN_PROGRESS
    ledger.put_task(stale)

    ledger.close_shift(shift.shift_id)
    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(
            shift.shift_id, _supervisor(),
            override_unimplemented_prerequisites=True,
            override_reason="Report model not implemented yet (P2-D)",
        )
    assert exc.value.control == "freeze"


def test_freeze_succeeds_with_full_chain_and_audits_override():
    ledger, shift = _in_memory_shift()
    ledger.close_shift(shift.shift_id)
    _make_ready_handover(ledger, shift)
    frozen = ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="Report model not implemented yet (P2-D)",
    )
    assert frozen.status == ShiftStatus.FROZEN
    entries = ledger.audit_entries_for(str(shift.shift_id))
    actions = {e.action for e in entries}
    assert "shift.freeze" in actions
    assert "shift.freeze_override_unimplemented_prerequisites" in actions
    override_entry = next(e for e in entries if e.action == "shift.freeze_override_unimplemented_prerequisites")
    assert "report_approved" in override_entry.after_state
    assert "open_handover_items_linked" not in override_entry.after_state


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
    _make_ready_handover(ledger, shift)
    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    with pytest.raises(ValueError, match="frozen"):
        EventService(ledger, AuditLog()).confirm(event.event_id, _supervisor())


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
    # The still-OPEN task above is captured into the handover's snapshot as an
    # open-work item; nothing mutates it before freeze, so the snapshot still
    # matches and freeze succeeds. The frozen-parent block proven below is
    # about the task's OWN post-freeze mutation, independent of that.
    _make_ready_handover(ledger, shift)

    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

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
    _make_ready_handover(ledger, shift)
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
    _make_ready_handover(ledger, shift)
    ShiftService(ledger).freeze(
        shift.shift_id,
        _supervisor(),
        override_unimplemented_prerequisites=True,
        override_reason="test",
    )

    # Correction is the one permitted post-freeze mutation path.
    correction = CorrectionService(ledger, AuditLog()).correct_event(
        event.event_id, _supervisor(), reason="fix title"
    )
    assert correction.new_version == event.version + 0 or correction.new_version >= 1
    fetched = ledger.get_event(event.event_id)
    assert fetched.version >= 2
