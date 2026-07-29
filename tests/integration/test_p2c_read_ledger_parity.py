"""P2C-OPERATIONS-CONSOLE-READ-SLICE — ledger parity tests (SPEC R3/AC-02).

Both InMemoryLedger and SqlLedger (SQLite) must agree on:
- list_events_for_shift: same events, same deterministic order, evidence preserved;
- open_work_snapshot: same canonical open-work set, same UUID order, evidence preserved.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

from operations_domain.models import (
    CustomerRequest,
    EvidenceRef,
    Incident,
    OperationalEvent,
    RiskClass,
    Shift,
    Task,
    TaskStatus,
)
from operations_ledger.sql_ledger import SqlLedger, make_engine
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger


def _shift() -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Parity shift", starts_at=now, ends_at=now + timedelta(hours=8))


def _event(shift_id, *, starts_at=None, title="E1", event_id=None) -> OperationalEvent:
    kwargs = {}
    if event_id is not None:
        kwargs["event_id"] = event_id
    return OperationalEvent(
        shift_id=shift_id,
        event_type="equipment_downtime",
        title=title,
        risk_class=RiskClass.R2,
        starts_at=starts_at,
        evidence=[EvidenceRef(source_type="message", source_id="m1", sha256="ab" * 32)],
        **kwargs,
    )


def _task(shift_id) -> Task:
    return Task(shift_id=shift_id, title="T1", risk_class=RiskClass.R1)


def _request(shift_id) -> CustomerRequest:
    return CustomerRequest(customer_id="c1", shift_id=shift_id, summary="R1")


def _incident(shift_id) -> Incident:
    return Incident(shift_id=shift_id, summary="I1", risk_class=RiskClass.R2)


def _make_inmemory(shift) -> InMemoryLedger:
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    return ledger


def _make_sqlite(shift) -> SqlLedger:
    from operations_ledger.tables import metadata

    engine = make_engine("sqlite://")
    metadata.create_all(engine)
    ledger = SqlLedger("sqlite://", models=domain_models, engine=engine)
    ledger.create_shift(shift)
    return ledger


def test_list_events_for_shift_order_and_evidence_parity():
    """AC-02: both backends return the same deterministic order and evidence.

    B and D tie on starts_at (09:00), so the tie-break is ascending
    str(event_id) - fixed UUIDs make that deterministic instead of relying on
    the random default_factory ordering two calls happen to produce.
    """
    shift = _shift()
    lower_id = UUID("00000000-0000-0000-0000-000000000001")
    higher_id = UUID("00000000-0000-0000-0000-000000000002")
    assert str(lower_id) < str(higher_id)
    e1 = _event(shift.shift_id, starts_at=datetime(2026, 7, 28, 10, tzinfo=timezone.utc), title="A")
    e2 = _event(shift.shift_id, starts_at=datetime(2026, 7, 28, 9, tzinfo=timezone.utc), title="B", event_id=lower_id)
    e3 = _event(shift.shift_id, starts_at=None, title="C")
    e4 = _event(shift.shift_id, starts_at=datetime(2026, 7, 28, 9, tzinfo=timezone.utc), title="D", event_id=higher_id)

    for ledger in (_make_inmemory(shift), _make_sqlite(shift)):
        for e in (e1, e2, e3, e4):
            ledger.add_event(e)

        events = ledger.list_events_for_shift(shift.shift_id)
        assert len(events) == 4
        # Order: starts_at non-null first, ascending starts_at, then ascending str(event_id)
        assert events[0].title == "B"  # 09:00, lower event_id tie-break with D
        assert events[1].title == "D"  # 09:00, higher event_id
        assert events[2].title == "A"  # 10:00
        assert events[3].title == "C"  # None
        # Evidence preserved
        for e in events:
            assert len(e.evidence) == 1
            assert e.evidence[0].sha256 == "ab" * 32


def test_list_events_for_shift_excludes_other_shifts():
    """AC-02: events from another shift are not included."""
    shift = _shift()
    other = _shift()
    e1 = _event(shift.shift_id, title="belong")
    e2 = _event(other.shift_id, title="other")

    for ledger in (_make_inmemory(shift), _make_sqlite(shift)):
        ledger.create_shift(other)
        ledger.add_event(e1)
        ledger.add_event(e2)
        events = ledger.list_events_for_shift(shift.shift_id)
        assert len(events) == 1
        assert events[0].title == "belong"


def test_list_events_for_shift_empty_shift():
    """AC-02: a shift with no events returns an empty list."""
    shift = _shift()
    for ledger in (_make_inmemory(shift), _make_sqlite(shift)):
        events = ledger.list_events_for_shift(shift.shift_id)
        assert events == []


def test_open_work_snapshot_parity():
    """AC-01: both backends return the same open-work snapshot."""
    shift = _shift()
    task = _task(shift.shift_id)
    task.status = TaskStatus.IN_PROGRESS
    request = _request(shift.shift_id)
    incident = _incident(shift.shift_id)

    for ledger in (_make_inmemory(shift), _make_sqlite(shift)):
        ledger.add_task(task)
        ledger.add_customer_request(request)
        ledger.add_incident(incident)
        snapshot = ledger.open_work_snapshot(shift.shift_id)
        assert set(snapshot.keys()) == {"Task", "CustomerRequest", "Incident"}
        assert len(snapshot["Task"]) == 1
        assert len(snapshot["CustomerRequest"]) == 1
        assert len(snapshot["Incident"]) == 1
        assert snapshot["Task"][0].task_id == task.task_id
        assert snapshot["CustomerRequest"][0].request_id == request.request_id
        assert snapshot["Incident"][0].incident_id == incident.incident_id