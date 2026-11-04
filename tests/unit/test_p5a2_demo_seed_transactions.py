"""Native SQLite transaction tests for the AM2 synthetic seed/CAS seam."""
from __future__ import annotations

import hmac
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, event, insert, update

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from operations_ledger import tables as ledger_tables  # noqa: E402
from operations_ledger._report_store import reports  # noqa: E402
from operations_ledger.sql_ledger import SqlLedger, make_engine  # noqa: E402
from p5a2_source_demo_recovery_inventory import expected_tables  # noqa: E402
from workspace_api.demo.bundle import load_bundle  # noqa: E402
from workspace_api.demo.coverage import load_authority  # noqa: E402
from workspace_api.demo import seed_recovery  # noqa: E402
from workspace_api.demo.seed_recovery_compare import compare_rows  # noqa: E402
from workspace_api.domain import models  # noqa: E402

PASSWORD = "unit-test-only-viewer-password"
FINGERPRINT = "a" * 64
TARGET = {"users": 1, "shifts": 36, "shift_assignments": 36, "reports": 37}
UTC = timezone.utc


def _aware_datetime(raw):
    value = datetime.fromisoformat(raw.decode("utf-8"))
    value = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
    return value.isoformat(timespec="microseconds")


@pytest.fixture
def rig(monkeypatch):
    # SQLite stores these PostgreSQL values as text/integers. DB-API converters
    # restore the native types expected by the raw-column contract; no row or
    # comparison helper is replaced.
    monkeypatch.setitem(sqlite3.converters, "BOOLEAN", lambda raw: bool(int(raw)))
    monkeypatch.setitem(sqlite3.converters, "DATETIME", _aware_datetime)
    monkeypatch.setitem(sqlite3.converters, "CHAR",
                        lambda raw: str(UUID(hex=raw.decode("ascii"))))
    monkeypatch.setitem(sqlite3.converters, "JSON",
                        lambda raw: json.loads(raw.decode("utf-8")))
    engine = make_engine("sqlite://", connect_args={"detect_types": sqlite3.PARSE_DECLTYPES})
    ledger_tables.metadata.create_all(engine)
    names = expected_tables()
    assert len(names) == 31 and set(ledger_tables.metadata.tables) <= set(names)
    with engine.begin() as conn:
        for name in sorted(set(names) - set(ledger_tables.metadata.tables)):
            conn.exec_driver_sql(f'CREATE TABLE "{name}" (_test_id INTEGER PRIMARY KEY)')
    trace, dml = [], []

    def locks(_conn, locked):
        trace.append(("locks", locked))

    def fingerprint(_conn):
        trace.append(("fingerprint", None))
        return FINGERPRINT

    def statements(_conn, _cursor, statement, _parameters, _context, _many):
        sql = statement.lstrip().upper()
        if sql.startswith("SELECT"):
            trace.append(("select", statement))
        if sql.startswith(("INSERT", "UPDATE", "DELETE", "REPLACE")):
            dml.append(statement)

    monkeypatch.setattr(seed_recovery, "lock_tables", locks)
    monkeypatch.setattr(seed_recovery, "database_fingerprint", fingerprint)
    event.listen(engine, "before_cursor_execute", statements)
    from types import SimpleNamespace

    rig = SimpleNamespace(engine=engine,
        ledger=SqlLedger("sqlite://", models=models, engine=engine),
        bundle=load_bundle(), authority=load_authority(), names=names,
        trace=trace, dml=dml)
    yield rig
    event.remove(engine, "before_cursor_execute", statements)
    engine.dispose()


def snapshot(rig):
    with rig.engine.connect() as conn:
        schema = seed_recovery.schema_digest(conn, rig.names)
        state = compare_rows(seed_recovery.read_rows(conn, rig.names),
                             rig.bundle, PASSWORD, models.User)
    return {key: state[key] for key in ("classification", "state_digest",
                                         "observed_created_at")} | {
        "db_fingerprint": FINGERPRINT, "table_names": sorted(rig.names),
        "schema_digest": schema}


def frozen_timestamp(rig):
    return datetime.fromisoformat(rig.bundle["user"]["created_at"].replace("Z", "+00:00"))


def run(rig, expected):
    return seed_recovery.seed_transaction(rig.ledger, rig.bundle, rig.authority,
                                          PASSWORD, expected)


def read_user(rig):
    with rig.engine.connect() as conn:
        return seed_recovery.read_rows(conn, rig.names)["users"][0]


def counts(rig):
    with rig.engine.connect() as conn:
        return {name: conn.exec_driver_sql(f'SELECT COUNT(*) FROM "{name}"').scalar_one()
                for name in rig.names}


def test_empty_seed_persists_frozen_timestamp_and_locks_before_revalidation(rig):
    expected = snapshot(rig)
    rig.trace.clear()
    result = run(rig, expected)
    assert result["result"] == "SEEDED"
    assert result["family_record"]["outcome"] == "SEEDED_ATOMIC"
    assert result["family_record"]["durable_application_writes"] == 110
    assert result["family_record"]["exact_rows_verified"] is True
    assert counts(rig) == {name: TARGET.get(name, 0) for name in rig.names}
    assert read_user(rig)["created_at"] == frozen_timestamp(rig).isoformat(timespec="microseconds")
    assert rig.trace[0][0] == "locks" and len(rig.trace[0][1]) == 31
    assert rig.trace.index(next(item for item in rig.trace if item[0] == "locks")) < \
        rig.trace.index(next(item for item in rig.trace if item[0] == "select"))


def test_exact_seed_is_idempotent_with_zero_writes(rig):
    run(rig, snapshot(rig))
    rig.dml.clear()
    result = run(rig, snapshot(rig))
    assert result["result"] == "VERIFY"
    assert result["family_record"]["outcome"] == "EXACT_VERIFIED"
    assert result["family_record"]["durable_application_writes"] == 0
    assert rig.dml == []


def test_sole_timestamp_cas_preserves_every_other_user_value(rig):
    run(rig, snapshot(rig))
    old = datetime(2024, 1, 2, tzinfo=UTC)
    with rig.engine.begin() as conn:
        conn.execute(update(ledger_tables.users).values(created_at=old))
    expected = snapshot(rig)
    before = read_user(rig)
    rig.dml.clear()
    result = run(rig, expected)
    after = read_user(rig)
    assert result["result"] == "CREATED_AT_REPAIRED"
    assert result["family_record"]["outcome"] == "CREATED_AT_REPAIRED"
    assert result["family_record"]["durable_application_writes"] == 1
    assert result["family_record"]["changed_user_id"] == "PUBLIC_ACTOR"
    assert len(rig.dml) == 1 and rig.dml[0].lstrip().upper().startswith("UPDATE")
    assert set(before) == set(after)
    assert {k: v for k, v in before.items() if k != "created_at"} == \
        {k: v for k, v in after.items() if k != "created_at"}
    assert hmac.compare_digest(before["password_hash"], after["password_hash"])
    assert after["created_at"] == frozen_timestamp(rig).isoformat(timespec="microseconds")


@pytest.mark.parametrize("damage", ["partial", "foreign", "hash", "security", "extra_column"])
def test_unapproved_rows_or_security_mismatches_refuse_without_writes(rig, damage):
    run(rig, snapshot(rig))
    expected = snapshot(rig)
    with rig.engine.begin() as conn:
        if damage == "partial":
            conn.execute(delete(reports).where(reports.c.report_id ==
                UUID(rig.bundle["reports"][0]["report_id"])))
        elif damage == "foreign":
            conn.execute(insert(ledger_tables.audit_records).values(
                audit_id=uuid4(), action="test", target_type="test",
                target_id="foreign"))
        elif damage == "hash":
            conn.execute(update(ledger_tables.users).values(password_hash="invalid-test-hash"))
        elif damage == "security":
            conn.execute(update(ledger_tables.users).values(role="operator"))
        else:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN unmodeled_test_column TEXT")
    rig.dml.clear()
    before = counts(rig)
    with pytest.raises((RuntimeError, ValueError)):
        run(rig, expected)
    assert rig.dml == []
    assert counts(rig) == before


def test_stale_prewrite_snapshot_and_old_created_at_drift_refuse(rig):
    empty = snapshot(rig)
    run(rig, empty)
    rig.dml.clear()
    with pytest.raises(RuntimeError, match="prewrite snapshot changed"):
        run(rig, empty)
    assert rig.dml == []

    first = datetime(2024, 1, 2, tzinfo=UTC)
    second = datetime(2024, 2, 3, tzinfo=UTC)
    with rig.engine.begin() as conn:
        conn.execute(update(ledger_tables.users).values(created_at=first))
    stale = snapshot(rig)
    with rig.engine.begin() as conn:
        conn.execute(update(ledger_tables.users).values(created_at=second))
    rig.dml.clear()
    with pytest.raises(RuntimeError, match="prewrite snapshot changed"):
        run(rig, stale)
    assert rig.dml == []
    assert read_user(rig)["created_at"] == second.isoformat(timespec="microseconds")


def test_schema_column_drift_refuses_before_application_writes(rig):
    expected = snapshot(rig)
    before = counts(rig)
    with rig.engine.begin() as conn:
        conn.exec_driver_sql('ALTER TABLE "audit_records" ADD COLUMN drift_test TEXT')
        assert seed_recovery.installed_tables(conn) == rig.names
    rig.trace.clear()
    rig.dml.clear()
    with pytest.raises(RuntimeError, match="schema columns changed"):
        run(rig, expected)
    assert rig.trace[0][0] == "locks" and len(rig.trace[0][1]) == 31
    assert rig.dml == []
    assert counts(rig) == before


def test_cas_rowcount_race_rolls_back_timestamp_change(rig):
    run(rig, snapshot(rig))
    first, second = datetime(2024, 1, 2, tzinfo=UTC), datetime(2024, 2, 3, tzinfo=UTC)
    with rig.engine.begin() as conn:
        conn.execute(update(ledger_tables.users).values(created_at=first))
    expected = snapshot(rig)
    injected = False

    def race(conn, _cursor, statement, _parameters, _context, _many):
        nonlocal injected
        if not injected and statement.lstrip().upper().startswith("UPDATE USERS SET CREATED_AT"):
            injected = True
            conn.exec_driver_sql("UPDATE users SET created_at=? WHERE user_id=?",
                                 (second.isoformat(sep=" ", timespec="microseconds"),
                                  "PUBLIC_ACTOR"))

    event.listen(rig.engine, "before_cursor_execute", race)
    try:
        with pytest.raises(RuntimeError, match="timestamp CAS failed"):
            run(rig, expected)
    finally:
        event.remove(rig.engine, "before_cursor_execute", race)
    assert injected is True
    assert read_user(rig)["created_at"] == first.isoformat(timespec="microseconds")


def test_readback_failure_rolls_back_all_seed_inserts(rig):
    expected = snapshot(rig)
    with rig.engine.begin() as conn:
        conn.exec_driver_sql("""CREATE TRIGGER corrupt_seed AFTER INSERT ON users
            BEGIN UPDATE users SET created_at='2024-01-02T00:00:00.000000+00:00'
            WHERE user_id=NEW.user_id; END""")
    rig.dml.clear()
    with pytest.raises(RuntimeError, match="exact readback failed"):
        run(rig, expected)
    assert counts(rig) == {name: 0 for name in rig.names}
    assert sum(sql.lstrip().upper().startswith("INSERT") for sql in rig.dml) == 110


def test_readback_failure_rolls_back_cas_and_preserves_user_security(rig):
    run(rig, snapshot(rig))
    old = datetime(2024, 1, 2, tzinfo=UTC)
    with rig.engine.begin() as conn:
        conn.execute(update(ledger_tables.users).values(created_at=old))
        conn.exec_driver_sql("""CREATE TRIGGER corrupt_cas AFTER UPDATE OF created_at ON users
            BEGIN UPDATE users SET username='changed-by-trigger' WHERE user_id=NEW.user_id; END""")
    expected = snapshot(rig)
    before = read_user(rig)
    with pytest.raises(RuntimeError, match="USER_ROW_INVALID"):
        run(rig, expected)
    after = read_user(rig)
    assert before["created_at"] == after["created_at"]
    assert before["user_id"] == after["user_id"] and before["role"] == after["role"]
    assert before["username"] == after["username"]
    assert hmac.compare_digest(before["password_hash"], after["password_hash"])
