"""Both ledger backends must satisfy the same Ledger Protocol.

This guards the substitutability promise: services depend on the Protocol, so
swapping InMemoryLedger for SqlLedger must not require any service change.

Note: SqlLedger's live behaviour against PostgreSQL is NOT exercised here (no
database in this environment). This test only proves structural conformance to
the Protocol; a live integration test belongs in a separate DB-backed suite.
"""

from datetime import datetime, timedelta, timezone

import pytest

from operations_ledger import Ledger
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from operations_domain.models import Report, ReportContent, ReportSection, Shift
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger


def test_in_memory_ledger_is_a_ledger():
    assert isinstance(InMemoryLedger(), Ledger)


def test_sql_ledger_is_a_ledger():
    # Inject a throwaway engine so no PostgreSQL driver/connection is needed to
    # assert structural conformance. No DB round-trip occurs.
    from sqlalchemy import create_engine

    sql = SqlLedger(
        "postgresql+psycopg://unused",
        models=domain_models,
        engine=create_engine("sqlite://"),
    )
    assert isinstance(sql, Ledger)


def test_both_backends_expose_the_same_ledger_methods():
    required = {
        "create_shift", "get_shift", "list_shifts", "freeze_shift",
        "add_message", "get_message", "message_exists", "add_event", "get_event", "put_event",
        "list_events_for_shift",
        "add_correction", "corrections_for",
        "add_incident", "get_incident", "list_incidents_for_shift", "put_incident",
        "open_work_snapshot", "add_handover", "get_handover",
        "list_handovers_for_shift", "put_handover",
        "add_report", "get_report", "get_current_report",
        "list_reports_for_shift", "put_report", "create_report_successor",
    }
    for backend in (InMemoryLedger, SqlLedger):
        missing = {m for m in required if not hasattr(backend, m)}
        assert not missing, f"{backend.__name__} missing {missing}"


# --- F4 repair: add_report parent invariant parity (InMemory/SQLite) --------

def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'parent.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "parent.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _content():
    return ReportContent(
        sections=[ReportSection(section_type=s, records=[]) for s in (
            "operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers",
        )],
        source_manifest=[], snapshot_digest="a" * 64,
    )


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_report_rejects_unknown_parent_shift(tmp_path, name):
    """F4: an unknown parent is a controlled ValueError, never a raw FK
    IntegrityError, and never mislabeled as a duplicate report_id."""
    ledger = dict(_backends(tmp_path))[name]
    now = datetime.now(timezone.utc)
    report = Report(shift_id=__import__("uuid").uuid4(), generated_from_cutoff=now, content=_content())
    with pytest.raises(ValueError, match="unknown parent shift"):
        ledger.add_report(report)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_report_rejects_frozen_parent_shift_with_no_partial_write(tmp_path, name):
    """F4: a FROZEN parent is refused before any row is written - same
    category on both backends, and the rejection leaves zero reports behind."""
    ledger = dict(_backends(tmp_path))[name]
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    ledger.close_shift(shift.shift_id)
    ledger.freeze_shift(shift.shift_id)

    report = Report(shift_id=shift.shift_id, generated_from_cutoff=now, content=_content())
    with pytest.raises(ValueError, match="frozen"):
        ledger.add_report(report)
    assert ledger.get_current_report(shift.shift_id, "END_SHIFT") is None


# --- F6 repair: transaction boundary (BEGIN IMMEDIATE, unit sharing, retry) -

def _fresh_ledger(tmp_path, name):
    engine = make_engine(f"sqlite:///{tmp_path / name}", connect_args={"timeout": 0})
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / name), models=domain_models, engine=engine)


@pytest.mark.parametrize("txn_method", ["report_mutation_transaction", "report_freeze_transaction"])
def test_report_transaction_modes_are_write_reserving_from_first_statement(tmp_path, txn_method):
    """F6: report_mutation_transaction/report_freeze_transaction must reserve
    the write lock as soon as the block opens - not lazily, at the first
    write. A second connection's own BEGIN IMMEDIATE must block while the
    first is still open."""
    import sqlite3

    db_file = f"reserve-{txn_method}.sqlite3"
    ledger = _fresh_ledger(tmp_path, db_file)

    with getattr(ledger, txn_method)() as unit:
        second = sqlite3.connect(str(tmp_path / db_file), timeout=0)
        try:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                second.execute("BEGIN IMMEDIATE")
        finally:
            second.close()
        ledger.create_shift(Shift(
            name="Day", starts_at=datetime.now(timezone.utc),
            ends_at=datetime.now(timezone.utc) + timedelta(hours=8),
        ), unit=unit)


def test_plain_transaction_does_not_reserve_the_write_lock_from_open(tmp_path):
    """F6 repair proof (independent-review finding): the generic
    transaction() used by every OTHER vertical must NOT reserve the writer
    lock merely by opening - only Report mutation/freeze does. A second
    connection's BEGIN IMMEDIATE must succeed while a plain transaction() is
    open with no write yet issued."""
    import sqlite3

    db_file = "plain-no-reserve.sqlite3"
    ledger = _fresh_ledger(tmp_path, db_file)

    with ledger.transaction():
        second = sqlite3.connect(str(tmp_path / db_file), timeout=0)
        try:
            second.execute("BEGIN IMMEDIATE")  # must NOT raise "database is locked"
            second.execute("ROLLBACK")
        finally:
            second.close()


def test_corrections_for_shares_unit_with_report_snapshot_gathering(tmp_path):
    """F6: corrections_for must accept `unit` and actually use it - proven by
    passing an explicit transaction and confirming it observes writes made
    earlier in that SAME uncommitted transaction (impossible on a separate,
    unshared connection, which would see none of the not-yet-committed rows)."""
    from operations_domain.models import Correction, OperationalEvent

    ledger = dict(_backends(tmp_path))[("sql")]
    shift = Shift(name="Day", starts_at=datetime.now(timezone.utc), ends_at=datetime.now(timezone.utc) + timedelta(hours=8))
    ledger.create_shift(shift)
    event = OperationalEvent(shift_id=shift.shift_id, event_type="x", title="t")

    with ledger.transaction() as unit:
        ledger.add_event(event, unit=unit)
        correction = Correction(
            record_type="OperationalEvent", record_id=event.event_id, reason="r",
            requested_by="op1", previous_version=1, new_version=2,
        )
        ledger.add_correction(correction, unit=unit)
        # Same uncommitted transaction: must see the correction just added.
        found = ledger.corrections_for(event.event_id, unit=unit)
        assert [c.correction_id for c in found] == [correction.correction_id]


# --- Finding 2 repair: write-reserving marker must not leak across pool ----
# reuse. `conn.info` is backed by the pooled DBAPI connection, not the
# Connection wrapper, so it survives checkout/checkin - StaticPool forces
# the SAME underlying connection to be reused, which is what actually
# reproduces the leak (a fresh connection per call would hide it).

def _static_pool_ledger(tmp_path):
    from sqlalchemy.pool import StaticPool

    engine = make_engine(
        f"sqlite:///{tmp_path / 'pool-reuse.sqlite3'}",
        connect_args={"timeout": 0, "check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "pool-reuse.sqlite3"), models=domain_models, engine=engine)


def _assert_ordinary_transaction_does_not_reserve(ledger):
    with ledger.transaction() as unit:
        marker = unit.info.get("cvf_write_reserving")
        assert not marker, f"write-reserving marker leaked into ordinary transaction: {marker!r}"


def test_ordinary_transaction_before_any_report_transaction_is_not_reserving(tmp_path):
    _assert_ordinary_transaction_does_not_reserve(_static_pool_ledger(tmp_path))


def test_ordinary_transaction_after_successful_report_transaction_is_not_reserving(tmp_path):
    ledger = _static_pool_ledger(tmp_path)
    with ledger.report_mutation_transaction() as unit:
        ledger.create_shift(Shift(
            name="Day", starts_at=datetime.now(timezone.utc),
            ends_at=datetime.now(timezone.utc) + timedelta(hours=8),
        ), unit=unit)
    _assert_ordinary_transaction_does_not_reserve(ledger)


def test_ordinary_transaction_after_rolled_back_report_transaction_is_not_reserving(tmp_path):
    ledger = _static_pool_ledger(tmp_path)

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with ledger.report_mutation_transaction():
            raise _Boom("simulated failure")
    _assert_ordinary_transaction_does_not_reserve(ledger)


def test_freeze_retry_classifies_only_postgres_serialization_sqlstates():
    """F6: only SQLSTATE 40001 (serialization_failure) / 40P01 (deadlock_
    detected) are retried; any other OperationalError - e.g. a real
    connectivity fault - must propagate uncaught, never be silently retried
    and relabeled as a controlled 409."""
    from sqlalchemy.exc import OperationalError

    from workspace_api.application.shift_service import _is_retryable_serialization_conflict

    class _FakeOrig:
        def __init__(self, sqlstate):
            self.sqlstate = sqlstate

    def _exc(sqlstate):
        return OperationalError("stmt", {}, _FakeOrig(sqlstate))

    assert _is_retryable_serialization_conflict(_exc("40001")) is True
    assert _is_retryable_serialization_conflict(_exc("40P01")) is True
    assert _is_retryable_serialization_conflict(_exc("57014")) is False  # query_canceled
    assert _is_retryable_serialization_conflict(_exc(None)) is False
    # No `.orig` at all (e.g. a bare OperationalError) must also not retry.
    assert _is_retryable_serialization_conflict(OperationalError("stmt", {}, None)) is False