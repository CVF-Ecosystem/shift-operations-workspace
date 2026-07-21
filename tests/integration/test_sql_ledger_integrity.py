"""Database-level integrity tests for SqlLedger on SQLite.

These assert the SQL backend enforces referential integrity and CHECK
constraints itself — not just the Python/Pydantic layer above it. This is what
keeps SQLite and PostgreSQL behaving the same way: both reject an event that
points at a non-existent shift, or a time window that is inverted.

Inserts go straight through the table (bypassing the Pydantic models) so the
test exercises the DATABASE constraint, not the app-layer validator.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata, operational_events, shifts

from workspace_api.domain import models as domain_models


@pytest.fixture()
def ledger(tmp_path: Path) -> SqlLedger:
    db = tmp_path / "integrity.sqlite3"
    # make_engine() enables SQLite foreign-key enforcement on every connection.
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _now():
    return datetime.now(timezone.utc)


def test_foreign_key_blocks_event_with_unknown_shift(ledger: SqlLedger):
    # No shift inserted; this shift_id does not exist.
    with pytest.raises(IntegrityError):
        with ledger.engine.begin() as conn:
            conn.execute(
                insert(operational_events).values(
                    event_id=uuid4(),
                    shift_id=uuid4(),  # orphan reference
                    event_type="equipment_downtime",
                    title="orphan",
                    version=1,
                )
            )


def test_check_blocks_inverted_shift_window(ledger: SqlLedger):
    now = _now()
    with pytest.raises(IntegrityError):
        with ledger.engine.begin() as conn:
            conn.execute(
                insert(shifts).values(
                    shift_id=uuid4(),
                    name="bad",
                    starts_at=now,
                    ends_at=now - timedelta(hours=1),  # ends before starts
                    version=1,
                )
            )


def test_check_blocks_inverted_event_window(ledger: SqlLedger):
    now = _now()
    shift_id = uuid4()
    with ledger.engine.begin() as conn:
        conn.execute(
            insert(shifts).values(
                shift_id=shift_id, name="ok", starts_at=now,
                ends_at=now + timedelta(hours=8), version=1,
            )
        )
    with pytest.raises(IntegrityError):
        with ledger.engine.begin() as conn:
            conn.execute(
                insert(operational_events).values(
                    event_id=uuid4(),
                    shift_id=shift_id,
                    event_type="equipment_downtime",
                    title="bad window",
                    starts_at=now,
                    ends_at=now - timedelta(minutes=1),  # ends before starts
                    version=1,
                )
            )


def test_valid_event_with_existing_shift_is_accepted(ledger: SqlLedger):
    now = _now()
    shift_id = uuid4()
    with ledger.engine.begin() as conn:
        conn.execute(
            insert(shifts).values(
                shift_id=shift_id, name="ok", starts_at=now,
                ends_at=now + timedelta(hours=8), version=1,
            )
        )
        conn.execute(
            insert(operational_events).values(
                event_id=uuid4(), shift_id=shift_id,
                event_type="equipment_downtime", title="valid", version=1,
            )
        )
    # No exception == accepted.
