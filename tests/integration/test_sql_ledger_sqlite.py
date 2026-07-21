"""Real round-trip test for SqlLedger against a SQLite file on disk.

This is the P1-A' verification: SqlLedger's dual-backend table definitions
(Uuid/JSON with a PostgreSQL variant) work end-to-end against a real embedded
database, not just against in-memory Python state. It proves persistence
across a connection close/reopen — the thing InMemoryLedger cannot do.

Scope note (do not over-claim): this exercises SQLite, the zero-setup backend.
It does NOT verify a real PostgreSQL round-trip — Docker was unavailable in
this environment. See docs/catalog/MODULE_REGISTRY.json (operations-ledger)
and docs/implementation/EXECUTION_ROADMAP.md (P1-A) for that remaining item.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cvf_runtime.audit import AuditRecord
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.domain import models as domain_models
from workspace_api.domain.models import Correction, OperationalEvent, RiskClass, Shift


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "ledger_roundtrip.sqlite3"


def _open_ledger(db_path: Path) -> SqlLedger:
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    return SqlLedger(str(db_path), models=domain_models, engine=engine)


def test_shift_and_event_survive_reconnect(db_path: Path):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=RiskClass.R2,
    )

    # First connection: write.
    ledger = _open_ledger(db_path)
    ledger.create_shift(shift)
    ledger.add_event(event)
    ledger.engine.dispose()  # close the connection entirely

    # Second connection (simulates process restart): read back.
    reopened = SqlLedger(str(db_path), models=domain_models, engine=make_engine(f"sqlite:///{db_path}"))
    fetched_shift = reopened.get_shift(shift.shift_id)
    fetched_event = reopened.get_event(event.event_id)

    assert fetched_shift.shift_id == shift.shift_id
    assert fetched_shift.name == "Day"
    assert fetched_event.event_id == event.event_id
    assert fetched_event.title == "Crane 3 stopped"
    assert str(fetched_event.risk_class) == "R2"


def test_correction_is_append_only_and_persists(db_path: Path):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Night", starts_at=now, ends_at=now + timedelta(hours=8))
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Pump failure",
        risk_class=RiskClass.R2,
    )
    ledger = _open_ledger(db_path)
    ledger.create_shift(shift)
    ledger.add_event(event)

    correction = Correction(
        record_type="OperationalEvent",
        record_id=event.event_id,
        reason="Corrected downtime window",
        requested_by="sup1",
        previous_version=1,
        new_version=2,
    )
    ledger.add_correction(correction)
    ledger.engine.dispose()

    reopened = SqlLedger(str(db_path), models=domain_models, engine=make_engine(f"sqlite:///{db_path}"))
    stored = reopened.corrections_for(event.event_id)
    assert len(stored) == 1
    assert stored[0].reason == "Corrected downtime window"
    assert stored[0].previous_version == 1
    assert stored[0].new_version == 2

    # Append-only: adding a second correction must not remove the first.
    correction_2 = Correction(
        record_type="OperationalEvent",
        record_id=event.event_id,
        reason="Second correction",
        requested_by="sup1",
        previous_version=2,
        new_version=3,
    )
    reopened.add_correction(correction_2)
    all_corrections = reopened.corrections_for(event.event_id)
    assert len(all_corrections) == 2
    assert {c.reason for c in all_corrections} == {"Corrected downtime window", "Second correction"}


def test_audit_record_persists_across_reconnect(db_path: Path):
    ledger = _open_ledger(db_path)
    record = AuditRecord(
        actor_id="sup1",
        actor_role="shift_supervisor",
        action="event.confirm",
        record_type="OperationalEvent",
        record_id="11111111-1111-1111-1111-111111111111",
        control_chain=["identity", "permission", "approval", "audit"],
        before_state="PROPOSED",
        after_state="CONFIRMED",
    )
    ledger.append_audit(record)
    ledger.engine.dispose()

    reopened = SqlLedger(str(db_path), models=domain_models, engine=make_engine(f"sqlite:///{db_path}"))
    entries = reopened.audit_entries_for("11111111-1111-1111-1111-111111111111")
    assert len(entries) == 1
    assert entries[0]["action"] == "event.confirm"
    assert entries[0]["metadata"]["before_state"] == "PROPOSED"
    assert entries[0]["metadata"]["after_state"] == "CONFIRMED"


def test_freeze_shift_persists(db_path: Path):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger = _open_ledger(db_path)
    ledger.create_shift(shift)
    ledger.freeze_shift(shift.shift_id)
    ledger.engine.dispose()

    reopened = SqlLedger(str(db_path), models=domain_models, engine=make_engine(f"sqlite:///{db_path}"))
    fetched = reopened.get_shift(shift.shift_id)
    assert str(fetched.status) == "FROZEN"
    assert fetched.version == 2
