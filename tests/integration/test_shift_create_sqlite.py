"""SqlLedger (SQLite) parity for shift-create admission (SHIFT-CREATE-
ADMISSION-REPAIR-2026-07-29, SPEC R7, AC-08/AC-09).

Proves the same ShiftService.create/Ledger.transaction path used by
InMemoryLedger also holds for a real on-disk SQLite database: the returned
record equals the persisted record, and both the shift and its audit survive
a connection dispose/reopen (the thing InMemoryLedger cannot demonstrate).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.shift_service import ShiftService
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import User

_OPERATOR = Principal(user_id="op1", role="operator")


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "shift_create_roundtrip.sqlite3"


def _open_ledger(db_path: Path) -> SqlLedger:
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    ledger = SqlLedger(str(db_path), models=domain_models, engine=engine)
    # P2C-MUTATION-FULL-UI-C3A1 (SPEC R4): ShiftService.create now requires
    # the creator to be a persisted active user.
    ledger.add_user(User(user_id="op1", username="op1", password_hash="x", role="operator"))
    return ledger


def _window():
    now = datetime.now(timezone.utc)
    return now, now + timedelta(hours=8)


def test_create_returns_the_persisted_record(db_path: Path):
    ledger = _open_ledger(db_path)
    starts_at, ends_at = _window()
    returned = ShiftService(ledger).create("Day", starts_at, ends_at, _OPERATOR)

    fetched = ledger.get_shift(returned.shift_id)
    assert fetched.shift_id == returned.shift_id
    assert fetched.name == returned.name == "Day"
    assert fetched.status == returned.status
    assert fetched.version == returned.version == 1


def test_shift_and_audit_survive_reconnect(db_path: Path):
    ledger = _open_ledger(db_path)
    starts_at, ends_at = _window()
    created = ShiftService(ledger).create("Night", starts_at, ends_at, _OPERATOR)
    ledger.engine.dispose()

    reopened = SqlLedger(str(db_path), models=domain_models, engine=make_engine(f"sqlite:///{db_path}"))
    fetched_shift = reopened.get_shift(created.shift_id)
    audits = reopened.audit_entries_for(str(created.shift_id))

    assert fetched_shift.shift_id == created.shift_id
    assert fetched_shift.name == "Night"
    assert len(audits) == 1
    assert audits[0]["action"] == "shift.create"
    assert audits[0]["actor_id"] == "op1"
