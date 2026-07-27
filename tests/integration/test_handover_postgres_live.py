"""Opt-in live PostgreSQL 16 handover suite (P2A-HANDOVER-VERTICAL).

Coherent, separate module - joins test_sql_ledger_postgres_live.py and
test_incident_postgres_live.py in the same disposable container/migration
pass (scripts/run_postgres_live_roundtrip.py). Same opt-in contract: every
test below requires LIVE_POSTGRES_DATABASE_URL, set only by that runner after
applying database/migrations/001-006 against a disposable container; without
it they skip. NEVER calls metadata.create_all() and NEVER falls back to
SQLite - the migration is the schema authority.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect as sa_inspect, insert, text
from sqlalchemy.exc import IntegrityError

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger import tables as t

from workspace_api.application.handover_service import HandoverService
from workspace_api.domain import models as domain_models
from operations_domain.models import Shift

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")
_RECEIVER = Principal(user_id="sup2", role="shift_supervisor")


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Live PG shift", starts_at=now, ends_at=now + timedelta(hours=8), **kw)


def test_live_handovers_tables_and_enum_present(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    tables = inspector.get_table_names()
    assert "handovers" in tables and "handover_items" in tables
    with sql_ledger.engine.connect() as conn:
        enums = {r[0] for r in conn.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e'"))}
    assert "handover_status" in enums


def test_live_handovers_column_and_check_parity(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("handovers")}
    code_cols = {c.name for c in t.handovers.columns}
    assert live_cols == code_cols
    live_pk = set(inspector.get_pk_constraint("handovers")["constrained_columns"])
    assert live_pk == {"handover_id"}
    live_fks = {(fk["referred_table"], fk["referred_columns"][0]) for fk in inspector.get_foreign_keys("handovers")}
    assert live_fks == {("shifts", "shift_id")}
    assert len(inspector.get_check_constraints("handovers")) >= 1


def test_live_handover_items_column_and_fk_parity(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("handover_items")}
    code_cols = {c.name for c in t.handover_items.columns}
    assert live_cols == code_cols
    live_fks = {(fk["referred_table"], fk["referred_columns"][0]) for fk in inspector.get_foreign_keys("handover_items")}
    assert live_fks == {("handovers", "handover_id")}


def test_handover_round_trip_survives_reconnect(sql_ledger, live_database_url):
    s1, s2 = _shift(), _shift()
    sql_ledger.create_shift(s1)
    sql_ledger.create_shift(s2)
    created = HandoverService(sql_ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_handover(created.handover_id)
    assert got.from_shift_id == s1.shift_id and got.to_shift_id == s2.shift_id
    assert got.status.value == "DRAFT"


def test_handover_review_then_acknowledge_persists_and_audits_through_reconnect(sql_ledger, live_database_url):
    s1, s2 = _shift(), _shift()
    sql_ledger.create_shift(s1)
    sql_ledger.create_shift(s2)
    svc = HandoverService(sql_ledger)
    h = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    h = svc.review(h.handover_id, _SUPERVISOR)
    h = svc.acknowledge(h.handover_id, _RECEIVER)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_handover(h.handover_id)
    audits = fresh.audit_entries_for(str(h.handover_id))
    assert got.status.value == "ACKNOWLEDGED" and got.acknowledged is True
    assert {"handover.create", "handover.review", "handover.acknowledge"} <= {a["action"] for a in audits}


def _rejected_then_usable(engine, values_builder):
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(values_builder(conn))
    with engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_handover_with_unknown_shift_rejected(sql_ledger):
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.handovers).values(
        handover_id=uuid4(), from_shift_id=uuid4(), to_shift_id=uuid4(),
        status="DRAFT", created_by="op1", version=1))


def test_handover_same_from_and_to_shift_rejected_by_live_database_check(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.handovers).values(
        handover_id=uuid4(), from_shift_id=shift.shift_id, to_shift_id=shift.shift_id,
        status="DRAFT", created_by="op1", version=1))


def test_handover_item_source_type_outside_check_constraint_rejected(sql_ledger):
    s1, s2 = _shift(), _shift()
    sql_ledger.create_shift(s1)
    sql_ledger.create_shift(s2)
    handover = HandoverService(sql_ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.handover_items).values(
        item_id=uuid4(), handover_id=handover.handover_id, source_record_type="NotARealType",
        source_record_id=uuid4(), source_digest="x", summary="bad"))


def test_handover_transaction_rollback_removes_all_writes(sql_ledger, live_database_url):
    """Mirrors test_sql_ledger_handovers.py's atomicity test: call the ledger
    directly (not the service, which owns its own transaction) so the raised
    failure shares the SAME unit of work as the add_handover write."""
    from operations_domain.models import Handover

    s1, s2 = _shift(), _shift()
    sql_ledger.create_shift(s1)
    sql_ledger.create_shift(s2)
    handover = Handover(from_shift_id=s1.shift_id, to_shift_id=s2.shift_id, created_by="op1")

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with sql_ledger.transaction() as unit:
            sql_ledger.add_handover(handover, unit=unit)
            raise _Boom("simulated failure")

    fresh = _reconnected(live_database_url)
    with pytest.raises(KeyError):
        fresh.get_handover(handover.handover_id)
