"""Opt-in live PostgreSQL 16 round-trip suite (P1-POSTGRESQL-LIVE-ROUNDTRIP).

SPEC R1: this file NEVER calls SQLAlchemy metadata.create_all() and NEVER
falls back to SQLite. Every test below requires LIVE_POSTGRES_DATABASE_URL,
set only by scripts/run_postgres_live_roundtrip.py after it has already
applied database/migrations/001-004 against a disposable container; without
it they skip with a clear reason (direct/ordinary root-suite execution).
Amendment 1 (WO 14.3 step 1): the runner's non-live unit tests moved to
test_postgres_live_runner.py, purely to respect the file-size guard - not a
behavior change to any pre-existing test.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import inspect as sa_inspect, insert, text
from sqlalchemy.exc import IntegrityError

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from run_postgres_live_roundtrip import POSTGRES_DB  # noqa: E402

from cvf_runtime.audit import AuditRecord
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger import tables as t
from workspace_api.domain import models as domain_models
from operations_domain.models import (
    Correction, EvidenceRef, OperationalEvent, RiskClass, Shift, Task, TaskStatus,
)
from operations_domain.models import ApprovalReceipt, TaskCreationIntent

from _schema_parity_parsing import migration_text
from test_schema_parity_types_and_checks import _ENUM_COLUMNS, _migration_enum_values

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"
_SQLLEDGER_TABLES = {
    "shifts": t.shifts, "operational_events": t.operational_events,
    "evidence_links": t.evidence_links, "corrections": t.corrections,
    "audit_records": t.audit_records, "tasks": t.tasks,
    "customer_requests": t.customer_requests, "users": t.users,
    "task_creation_intents": t.task_creation_intents, "approval_receipts": t.approval_receipts,
}
_ALL_MIGRATION_TABLES = set(_SQLLEDGER_TABLES) | {"messages", "approvals", "reports"}
_ALL_MIGRATION_ENUMS = {"data_state", "risk_class", "shift_status"}

# --- live fixtures -----------------------------------------------------------

@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R1)")
    return url

@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))

def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))

def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Live PG shift", starts_at=now, ends_at=now + timedelta(hours=8), **kw)

# --- R6: live identity -------------------------------------------------------

def test_live_identity_is_real_postgresql_16(sql_ledger):
    assert sql_ledger.engine.dialect.name == "postgresql"
    with sql_ledger.engine.connect() as conn:
        version = conn.execute(text("SHOW server_version")).scalar()
        dbname = conn.execute(text("SELECT current_database()")).scalar()
    assert version.split(".")[0].split(" ")[0] == "16"
    assert dbname == POSTGRES_DB

# --- R7: live schema ---------------------------------------------------------

def test_live_schema_has_all_migration_tables_and_enums(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    assert _ALL_MIGRATION_TABLES <= set(inspector.get_table_names())
    with sql_ledger.engine.connect() as conn:
        enums = {r[0] for r in conn.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e'"))}
    assert _ALL_MIGRATION_ENUMS <= enums

@pytest.mark.parametrize("table_name", sorted(_SQLLEDGER_TABLES))
def test_live_schema_column_parity_for_sqlledger_tables(sql_ledger, table_name):
    tbl_obj = _SQLLEDGER_TABLES[table_name]
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"]: c for c in inspector.get_columns(table_name)}
    code_cols = {c.name: c for c in tbl_obj.columns}
    assert set(live_cols) == set(code_cols), (table_name, sorted(live_cols), sorted(code_cols))
    for name, code_col in code_cols.items():
        assert bool(live_cols[name]["nullable"]) == bool(code_col.nullable), f"{table_name}.{name} nullable"
    live_pk = set(inspector.get_pk_constraint(table_name)["constrained_columns"])
    assert live_pk == set(tbl_obj.primary_key.columns.keys()), f"{table_name} PK"
    live_fks = {(fk["referred_table"], fk["referred_columns"][0]) for fk in inspector.get_foreign_keys(table_name)}
    code_fks = {(fk.column.table.name, fk.column.name) for col in tbl_obj.columns for fk in col.foreign_keys}
    assert live_fks == code_fks, f"{table_name} FK"

@pytest.mark.parametrize("table_name", ["shifts", "operational_events", "corrections", "tasks", "customer_requests", "users"])
def test_live_schema_has_expected_check_constraints(sql_ledger, table_name):
    inspector = sa_inspect(sql_ledger.engine)
    assert len(inspector.get_check_constraints(table_name)) >= 1, table_name

def test_live_schema_approval_receipts_unique_constraint(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    uniques = inspector.get_unique_constraints("approval_receipts")
    cols = {tuple(sorted(u["column_names"])) for u in uniques}
    expected = tuple(sorted(["record_type", "record_id", "action", "target_version", "approver_id"]))
    assert expected in cols

@pytest.mark.parametrize("table_column", sorted(_ENUM_COLUMNS))
def test_live_enum_type_name_and_value_parity(sql_ledger, table_column):
    """Amendment 1 R14/AC-24: query the LIVE PostgreSQL catalog's actual
    enum labels (not just tables.py's Python-side ENUM object, which
    test_native_enum_type_name_and_value_parity already checks statically)
    and compare against the same migration-derived expected values."""
    table_name, column_name = table_column
    enum_name, _tbl_obj = _ENUM_COLUMNS[table_column]
    with sql_ledger.engine.connect() as conn:
        live_values = conn.execute(text(
            "SELECT e.enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid "
            "WHERE t.typname = :name ORDER BY e.enumsortorder"
        ), {"name": enum_name}).scalars().all()
    expected = _migration_enum_values(migration_text(), enum_name)
    assert list(live_values) == expected, f"{table_name}.{column_name} ({enum_name}): live={list(live_values)} expected={expected}"

# --- R8: round trip across engine disposal + reconnect ----------------------

def test_shift_event_task_round_trip_survives_reconnect(sql_ledger, live_database_url):
    shift = _shift()
    event = OperationalEvent(
        shift_id=shift.shift_id, event_type="equipment_downtime", title="Crane stopped",
        risk_class=RiskClass.R2, evidence=[EvidenceRef(source_type="message", source_id="m1", sha256="ab" * 32)],
    )
    task = Task(shift_id=shift.shift_id, title="Inspect crane", risk_class=RiskClass.R1)
    sql_ledger.create_shift(shift)
    sql_ledger.add_event(event)
    sql_ledger.add_task(task)
    task.status = TaskStatus.IN_PROGRESS
    task.version = 2
    sql_ledger.put_task(task)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got_shift = fresh.get_shift(shift.shift_id)
    got_event = fresh.get_event(event.event_id)
    got_task = fresh.get_task(task.task_id)
    assert got_shift.name == "Live PG shift"
    assert got_event.title == "Crane stopped" and len(got_event.evidence) == 1
    assert got_event.evidence[0].sha256 == "ab" * 32
    assert str(got_task.status) == "IN_PROGRESS" and got_task.version == 2

def test_correction_audit_user_round_trip_survives_reconnect(sql_ledger, live_database_url):
    shift = _shift()
    event = OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="Pump failure")
    sql_ledger.create_shift(shift)
    sql_ledger.add_event(event)
    correction = Correction(record_type="OperationalEvent", record_id=event.event_id, reason="fix",
                             requested_by="sup1", previous_version=1, new_version=2)
    sql_ledger.add_correction(correction)
    sql_ledger.append_audit(AuditRecord(actor_id="sup1", actor_role="shift_supervisor", action="event.confirm",
                                         record_type="OperationalEvent", record_id=str(event.event_id),
                                         control_chain=["identity", "audit"], before_state="PROPOSED", after_state="CONFIRMED"))
    user_id = f"pg-live-{uuid4().hex[:8]}"
    sql_ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role="shift_supervisor"))
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    corrections = fresh.corrections_for(event.event_id)
    audits = fresh.audit_entries_for(str(event.event_id))
    user = fresh.get_user_by_id(user_id)
    assert len(corrections) == 1 and corrections[0].reason == "fix"
    assert len(audits) == 1 and audits[0]["metadata"]["after_state"] == "CONFIRMED"
    assert user is not None and user.username == user_id

def test_approval_receipt_and_task_creation_intent_round_trip_survives_reconnect(sql_ledger, live_database_url):
    shift = _shift()
    sql_ledger.create_shift(shift)
    user_id = f"pg-live-{uuid4().hex[:8]}"
    sql_ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role="responsible_manager"))
    intent = TaskCreationIntent(shift_id=shift.shift_id, risk_class="R3", payload_snapshot={"title": "t"},
                                 payload_digest="d" * 8, created_by=user_id)
    sql_ledger.add_task_creation_intent(intent)
    receipt = ApprovalReceipt(record_type="Task", record_id=intent.intent_id, action="task.create",
                               target_version=1, risk_class="R3", payload_digest="d" * 8,
                               approver_id=user_id, approver_role="responsible_manager")
    sql_ledger.add_approval_receipt(receipt)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got_intent = fresh.get_task_creation_intent(intent.intent_id)
    got_receipt = fresh.get_approval_receipt(record_type="Task", record_id=intent.intent_id, action="task.create",
                                              target_version=1, approver_id=user_id)
    assert got_intent.payload_digest == "d" * 8
    assert got_receipt is not None and got_receipt.receipt_id == receipt.receipt_id

# --- R9: constraint rejections, each followed by a usable connection -------

def _rejected_then_usable(engine, values_builder):
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(values_builder(conn))
    with engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1

def test_event_with_unknown_shift_rejected(sql_ledger):
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.operational_events).values(
        event_id=uuid4(), shift_id=uuid4(), event_type="x", title="orphan", version=1))

def test_inverted_shift_window_rejected(sql_ledger):
    now = datetime.now(timezone.utc)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.shifts).values(
        shift_id=uuid4(), name="bad", starts_at=now, ends_at=now - timedelta(hours=1), version=1))

def test_inverted_event_window_rejected(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    now = datetime.now(timezone.utc)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.operational_events).values(
        event_id=uuid4(), shift_id=shift.shift_id, event_type="x", title="bad",
        starts_at=now, ends_at=now - timedelta(minutes=1), version=1))

def test_status_outside_check_constraint_rejected(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.tasks).values(
        task_id=uuid4(), shift_id=shift.shift_id, title="t", status="NOT_A_REAL_STATUS", version=1))

def test_duplicate_approval_receipt_scope_key_rejected(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    user_id = f"pg-live-{uuid4().hex[:8]}"
    sql_ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role="shift_supervisor"))
    event = OperationalEvent(shift_id=shift.shift_id, event_type="x", title="t")
    sql_ledger.add_event(event)
    receipt = ApprovalReceipt(record_type="OperationalEvent", record_id=event.event_id, action="event.confirm",
                               target_version=1, risk_class="R3", approver_id=user_id, approver_role="shift_supervisor")
    sql_ledger.add_approval_receipt(receipt)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.approval_receipts).values(
        receipt_id=uuid4(), record_type="OperationalEvent", record_id=event.event_id, action="event.confirm",
        target_version=1, risk_class="R3", approver_id=user_id, approver_role="shift_supervisor"))

# --- P2C-OPERATIONS-CONSOLE-READ-SLICE: live event-list/open-work reads ----

def test_live_list_events_for_shift_order_and_evidence(sql_ledger):
    """R15: the real event-list query against live PostgreSQL preserves
    deterministic order and evidence - not just against SQLite."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    early = OperationalEvent(shift_id=shift.shift_id, event_type="x", title="early",
        starts_at=datetime(2026, 7, 28, 9, tzinfo=timezone.utc),
        evidence=[EvidenceRef(source_type="message", source_id="m1", sha256="ab" * 32)])
    late = OperationalEvent(shift_id=shift.shift_id, event_type="x", title="late",
        starts_at=datetime(2026, 7, 28, 10, tzinfo=timezone.utc))
    undated = OperationalEvent(shift_id=shift.shift_id, event_type="x", title="undated")
    for e in (late, early, undated):
        sql_ledger.add_event(e)

    events = sql_ledger.list_events_for_shift(shift.shift_id)
    assert [e.title for e in events] == ["early", "late", "undated"]
    assert len(events[0].evidence) == 1 and events[0].evidence[0].sha256 == "ab" * 32


def test_live_open_work_snapshot_reflects_real_rows(sql_ledger):
    """R15: open_work_snapshot against live PostgreSQL returns exactly the
    persisted open Task."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    task = Task(shift_id=shift.shift_id, title="Inspect crane", risk_class=RiskClass.R1)
    sql_ledger.add_task(task)

    snapshot = sql_ledger.open_work_snapshot(shift.shift_id)
    assert len(snapshot["Task"]) == 1
    assert snapshot["Task"][0].task_id == task.task_id


def test_transaction_rollback_removes_all_writes(sql_ledger, live_database_url):
    shift = _shift()

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with sql_ledger.transaction() as unit:
            sql_ledger.create_shift(shift, unit=unit)
            raise _Boom("simulated failure")

    fresh = _reconnected(live_database_url)
    with pytest.raises(KeyError):
        fresh.get_shift(shift.shift_id)
