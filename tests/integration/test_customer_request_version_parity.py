"""Schema parity guard for `customer_requests.version` plus cross-backend
create/transition version behavior (P2C-MUTATION-FULL-UI-C3B2, SPEC R12,
AC-12).

`customer_requests` is defined across TWO migrations: the base CREATE TABLE
in 002_tasks_customers_reports.sql, then the `version` column added by
009_customer_request_version.sql. The generic `_schema_parity_parsing.
table_block()` regex only matches a single `CREATE TABLE IF NOT EXISTS ...
);` statement, so it cannot see 009's ALTER statements - this module parses
both migrations directly, mirroring test_schema_parity_reports.py's exact
precedent for `reports`/007.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import pytest

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import customer_requests, metadata

from workspace_api.application.customer_request_service import CustomerRequestService
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment
from operations_domain.models import CustomerRequest, CustomerRequestStatus, Shift
from workspace_api.infrastructure.repository import InMemoryLedger

from _schema_parity_parsing import code_columns, migration_columns, migration_text, table_block


def _operator() -> Principal:
    return Principal(user_id="op1", role="operator")


def _sql_ledger(tmp_path) -> SqlLedger:
    db = tmp_path / "customer_request_version.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _new_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    if ledger.get_user_by_id("op1") is None:
        ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))
    return shift


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


# --- static two-migration schema parity (mirrors test_schema_parity_reports.py) --


def test_customer_requests_table_exists_in_migration_002():
    sql = migration_text()
    assert "CREATE TABLE IF NOT EXISTS customer_requests" in sql


def test_version_column_added_by_migration_009():
    sql = migration_text()
    assert re.search(
        r"ALTER TABLE customer_requests ADD COLUMN IF NOT EXISTS version integer", sql
    ), "migration 009 must add the version column exactly this way"


def test_column_sets_match_exactly_across_both_migrations():
    """The base CREATE TABLE columns plus 009's version must exactly match
    the SQLAlchemy Table object - no drift in either direction."""
    sql = migration_text()
    block = table_block(sql, "customer_requests")
    migration_cols = set(migration_columns(block)) | {"version"}
    code_cols = set(code_columns(customer_requests))

    code_only = code_cols - migration_cols
    migration_only = migration_cols - code_cols
    assert not code_only, (
        f"customer_requests: tables.py declares columns neither migration has: {sorted(code_only)}"
    )
    assert not migration_only, (
        f"customer_requests: migrations declare columns tables.py does not map: {sorted(migration_only)}"
    )


def test_base_column_nullability_matches():
    sql = migration_text()
    block = table_block(sql, "customer_requests")
    migration_cols = migration_columns(block)
    code_cols = code_columns(customer_requests)
    for name in migration_cols:
        assert migration_cols[name]["nullable"] == code_cols[name]["nullable"], (
            f"customer_requests.{name}: nullable mismatch - migration says "
            f"nullable={migration_cols[name]['nullable']}, tables.py says "
            f"nullable={code_cols[name]['nullable']}"
        )


def test_version_not_null_with_default_one_and_check_constraint():
    """Migration 009 sets version NOT NULL DEFAULT 1 with a >=1 CHECK;
    tables.py must declare a matching server_default/CheckConstraint so a
    bare INSERT omitting it succeeds against a migration-created PostgreSQL
    database, and an invalid value is rejected the same way on both."""
    from sqlalchemy import CheckConstraint

    sql = migration_text()
    assert re.search(r"ALTER TABLE customer_requests ALTER COLUMN version SET NOT NULL", sql)
    assert re.search(r"ALTER TABLE customer_requests ALTER COLUMN version SET DEFAULT 1", sql)
    assert re.search(r"customer_requests_version_check", sql)

    version_col = customer_requests.c.version
    assert not version_col.nullable
    assert version_col.server_default is not None
    code_checks = [c for c in customer_requests.constraints if isinstance(c, CheckConstraint)]
    assert any("version" in str(c.sqltext) for c in code_checks)


def test_migration_009_never_deletes_or_rewrites_existing_rows():
    """SPEC R12: backfill only sets NULL rows to 1, no destructive statement
    against pre-existing data."""
    from pathlib import Path

    path_009 = Path(__file__).resolve().parents[2] / "database" / "migrations" / "009_customer_request_version.sql"
    text_009 = path_009.read_text(encoding="utf-8").upper()
    assert "DELETE FROM CUSTOMER_REQUESTS" not in text_009
    assert "DROP TABLE" not in text_009
    assert "TRUNCATE" not in text_009


# --- cross-backend create/transition version behavior (AC-12) ---------------


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_persists_and_returns_version_one(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(ledger).create_customer_request(request, _operator())
    assert created.version == 1
    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.version == 1


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_transition_increments_version_exactly_once(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(ledger).create_customer_request(request, _operator())

    moved = CustomerRequestService(ledger).transition(
        created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )
    assert moved.version == 2
    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.version == 2


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_stale_version_transition_is_409_with_zero_partial_write(tmp_path, name):
    from cvf_runtime.errors import CvfDenied

    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(ledger).create_customer_request(request, _operator())
    CustomerRequestService(ledger).transition(
        created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )

    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger).transition(
            created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=created.version
        )
    assert exc.value.http_status == 409

    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.status == CustomerRequestStatus.ACKNOWLEDGED, "stale transition must not have partially applied"
    assert fetched.version == 2


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_missing_expected_version_transition_is_422_with_zero_write(tmp_path, name):
    from cvf_runtime.errors import CvfDenied

    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(ledger).create_customer_request(request, _operator())

    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger).transition(
            created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED, expected_version=None
        )
    assert exc.value.http_status == 422

    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.status == CustomerRequestStatus.NEW
    assert fetched.version == 1


def test_existing_row_backfills_to_version_one_deterministically(tmp_path):
    """SPEC R12: a row inserted before this tranche's version column existed
    (simulated here via a direct SQL insert omitting version, relying on the
    server_default) must read back as version 1, exactly like migration 009's
    deterministic UPDATE backfill for pre-existing rows."""
    from sqlalchemy import insert

    ledger = _sql_ledger(tmp_path)
    shift = _new_shift(ledger)
    request_id = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s").request_id
    with ledger.engine.begin() as conn:
        conn.execute(
            insert(customer_requests).values(
                request_id=request_id,
                customer_id="c1",
                shift_id=shift.shift_id,
                summary="s",
                details=None,
                status="NEW",
                source_message_id=None,
                promised_at=None,
                owner_id=None,
            )
        )
    fetched = ledger.get_customer_request(request_id)
    assert fetched.version == 1
