"""Inert SQL statement/UOW checks and temporary SQLite negative; no PostgreSQL run."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
import sys
from types import SimpleNamespace
from uuid import NAMESPACE_DNS, uuid5

import pytest
from sqlalchemy import insert
from sqlalchemy.dialects import postgresql

from cvf_runtime.identity import Principal
from operations_ledger import _proactive_source_sql as source_sql
from operations_ledger._proactive_source_types import SourceReadFailure
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import shifts, users, shift_assignments
from workspace_api.application.proactive_source import TrustedSourceScope, query_source
from workspace_api.domain import models

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "unit"))
from p5a2_scoped_source_helpers import START, oracle  # noqa: E402


class Rows:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows):
        self.rows = list(rows)
        self.statements = []
        self.options = []
        self.parameters = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.closed = True
        return False

    def execution_options(self, **kwargs):
        self.options.append(kwargs)
        return self

    @contextmanager
    def begin(self):
        self.statements.append("BEGIN")
        yield self
        self.statements.append("ROLLBACK/END")

    def exec_driver_sql(self, statement):
        self.statements.append(statement)

    def execute(self, statement, params=None):
        compiled = statement.compile(dialect=postgresql.dialect())
        sql = str(compiled)
        self.statements.append(sql)
        self.parameters.append(dict(compiled.params))
        return Rows(self.rows.pop(0))


class FakeEngine:
    def __init__(self, *connections):
        self.dialect = SimpleNamespace(name="postgresql")
        self.connections = list(connections)
        self.opened = []

    def connect(self):
        conn = self.connections.pop(0)
        self.opened.append(conn)
        return conn


def test_pg_metadata_caps_and_single_read_unit_then_new_fresh_view():
    shift_id = uuid5(NAMESPACE_DNS, "sql-fixture-shift")
    assignment_id = uuid5(NAMESPACE_DNS, "sql-fixture-assignment")
    report_id = uuid5(NAMESPACE_DNS, "sql-fixture-report")
    first = FakeConnection([
        [(shift_id, START, assignment_id, 1)],
        [(shift_id, report_id, 1, START, START, "a" * 64)],
    ])
    fresh = FakeConnection([
        [(shift_id, START, assignment_id, 1)], [(shift_id,)],
    ])
    ledger = SimpleNamespace(engine=FakeEngine(first, fresh), models=models)
    end = START + timedelta(hours=1)
    with source_sql.scoped_source_read(ledger, "PUBLIC_ACTOR", START, end, end) as unit:
        cohort = unit.cohort()
        candidates = unit.candidates((shift_id,))
        assert len(cohort) == len(candidates) == 1
        assert len(ledger.engine.opened) == 1
    current = source_sql.fresh_scoped_cohort(ledger, "PUBLIC_ACTOR", START, end, (shift_id,))
    assert current.cohort == cohort and current.prior_active == {shift_id}
    assert len(ledger.engine.opened) == 2
    for conn in (first, fresh):
        assert conn.options == [{"isolation_level": "REPEATABLE READ"}]
        assert conn.statements[:2] == ["BEGIN", "SET TRANSACTION READ ONLY"]
    assert all("LIMIT" in sql for sql in first.statements if "FROM shifts" in sql or "FROM reports" in sql)
    assert any("shift_assignments.status" in sql for sql in first.statements)
    assert all("SELECT reports.content" not in sql and "CAST(reports.content ->>" in sql
               for sql in first.statements if "FROM reports" in sql)
    assert any("snapshot_digest" in params.values() for params in first.parameters)


def test_pg_jsonb_ref_preflight_is_scalar_before_body_load():
    rid = uuid5(NAMESPACE_DNS, "jsonb-report")
    conn = FakeConnection([[(rid, 4, 4)]])
    counts = source_sql.content.incident_ref_counts(conn, (rid,))
    assert counts == {rid: (4, 4)}
    sql = conn.statements[0]
    assert sql.count("jsonb_array_elements") == 3
    assert "source_manifest" in sql and "section_type" in sql
    assert "SELECT report_id" in sql and "SELECT *" not in sql


def test_sqlite_native_naive_timestamp_refuses_without_utc_repair(tmp_path):
    url = f"sqlite:///{tmp_path / 'naive.db'}"
    engine = make_engine(url)
    try:
        users.create(engine)
        shifts.create(engine)
        shift_assignments.create(engine)
        shift_id = uuid5(NAMESPACE_DNS, "sqlite-naive-shift")
        with engine.begin() as conn:
            conn.execute(insert(users).values(user_id="PUBLIC_ACTOR", username="public_actor",
                                              password_hash="fixture", role="operator"))
            conn.execute(insert(shifts).values(
                shift_id=shift_id, name="NAIVE", starts_at=START - timedelta(hours=1),
                ends_at=START, status="OPEN", version=1,
                created_at=START - timedelta(hours=2),
            ))
            conn.execute(insert(shift_assignments).values(
                assignment_id=uuid5(NAMESPACE_DNS, "sqlite-assignment"), shift_id=shift_id,
                user_id="PUBLIC_ACTOR", assigned_by="PUBLIC_ACTOR", status="ACTIVE",
                assigned_at=START - timedelta(hours=2), version=1,
            ))
        ledger = SqlLedger(url, models, engine=engine)
        case = next(x for x in oracle()["refusals"] if x["case"] == "naive_input_or_sqlite_timestamp")
        result = query_source(Principal(user_id="PUBLIC_ACTOR", role="operator"),
            TrustedSourceScope("PUBLIC_SCOPE", "PUBLIC_ACTOR", "SQLITE-INSTANCE"),
            START, START + timedelta(hours=1), START + timedelta(hours=1),
            ledger, coverage=SimpleNamespace())
        assert result.receipt == case["expected_receipt"] and result.payload is None
    finally:
        engine.dispose()


def test_foreign_sqlite_naive_shift_cannot_set_requested_diagnostic(tmp_path):
    url = f"sqlite:///{tmp_path / 'foreign-naive.db'}"
    engine = make_engine(url)
    try:
        users.create(engine)
        shifts.create(engine)
        shift_assignments.create(engine)
        sid = uuid5(NAMESPACE_DNS, "foreign-sqlite-shift")
        with engine.begin() as conn:
            conn.execute(insert(users), [
                {"user_id": "PUBLIC_ACTOR", "username": "public_actor", "password_hash": "x", "role": "operator"},
                {"user_id": "OTHER_ACTOR", "username": "other_actor", "password_hash": "x", "role": "operator"},
            ])
            conn.execute(insert(shifts).values(shift_id=sid, name="FOREIGN",
                starts_at=START - timedelta(hours=1), ends_at=START, status="OPEN",
                version=1, created_at=START - timedelta(hours=2)))
            conn.execute(insert(shift_assignments).values(
                assignment_id=uuid5(NAMESPACE_DNS, "foreign-sqlite-assignment"), shift_id=sid,
                user_id="OTHER_ACTOR", assigned_by="OTHER_ACTOR", status="ACTIVE",
                assigned_at=START - timedelta(hours=2), version=1))
        ledger = SqlLedger(url, models, engine=engine)
        result = query_source(Principal(user_id="PUBLIC_ACTOR", role="operator"),
            TrustedSourceScope("PUBLIC_SCOPE", "PUBLIC_ACTOR", "SQLITE-INSTANCE"),
            START, START + timedelta(hours=1), START + timedelta(hours=1),
            ledger, coverage=SimpleNamespace())
        assert result.receipt["reason"] == "SNAPSHOT_UNAVAILABLE"
    finally:
        engine.dispose()


def test_sql_capability_setup_and_fresh_fail_closed():
    class NoRepeatableRead(FakeConnection):
        def execution_options(self, **_kwargs):
            raise RuntimeError("secret driver detail")
    first = NoRepeatableRead([])
    ledger = SimpleNamespace(engine=FakeEngine(first), models=models)
    with pytest.raises(SourceReadFailure, match="SNAPSHOT_UNAVAILABLE"):
        with source_sql.scoped_source_read(ledger, "PUBLIC_ACTOR", START,
                                            START + timedelta(hours=1), START + timedelta(hours=1)):
            pass
    assert first.closed
    fresh = NoRepeatableRead([])
    ledger = SimpleNamespace(engine=FakeEngine(fresh), models=models)
    with pytest.raises(SourceReadFailure, match="SNAPSHOT_UNAVAILABLE"):
        source_sql.fresh_scoped_cohort(ledger, "PUBLIC_ACTOR", START,
                                       START + timedelta(hours=1), ())
    assert fresh.closed
    first = NoRepeatableRead([])
    ledger = SqlLedger("postgresql://fixture", models, engine=FakeEngine(first))
    result = query_source(Principal(user_id="PUBLIC_ACTOR", role="operator"),
        TrustedSourceScope("PUBLIC_SCOPE", "PUBLIC_ACTOR", "SQL-INSTANCE"),
        START, START + timedelta(hours=1), START + timedelta(hours=1),
        ledger, coverage=SimpleNamespace())
    assert result.receipt["reason"] == "SNAPSHOT_UNAVAILABLE" and first.closed


def test_initial_connect_storage_failure_and_fresh_connect_capability_refusals():
    class DownEngine:
        dialect = SimpleNamespace(name="postgresql")
        def connect(self):
            raise OSError("secret storage detail")
    ledger = SqlLedger("postgresql://fixture", models, engine=DownEngine())
    result = query_source(Principal(user_id="PUBLIC_ACTOR", role="operator"),
        TrustedSourceScope("PUBLIC_SCOPE", "PUBLIC_ACTOR", "SQL-INSTANCE"),
        START, START + timedelta(hours=1), START + timedelta(hours=1),
        ledger, coverage=SimpleNamespace())
    expected = next(x for x in oracle()["refusals"] if x["case"] == "storage_exception")
    assert result.receipt == expected["expected_receipt"] and result.payload is None
    with pytest.raises(SourceReadFailure, match="SNAPSHOT_UNAVAILABLE"):
        source_sql.fresh_scoped_cohort(ledger, "PUBLIC_ACTOR", START,
                                       START + timedelta(hours=1), ())


def test_malformed_persisted_body_is_invalid_lineage_but_storage_failure_is_unavailable():
    rid = uuid5(NAMESPACE_DNS, "malformed-body")
    class MappedRows:
        def mappings(self):
            return self
        def all(self):
            return [{"report_id": rid, "content": {"bad": "shape"}}]
    class MalformedConnection:
        def execute(self, *_args):
            return MappedRows()
    with pytest.raises(SourceReadFailure, match="INVALID_LINEAGE"):
        source_sql.content.load_reports(MalformedConnection(), models, (rid,))
    class DownConnection:
        def execute(self, *_args):
            raise RuntimeError("secret storage detail")
    with pytest.raises(RuntimeError, match="secret storage detail"):
        source_sql.content.load_reports(DownConnection(), models, (rid,))
