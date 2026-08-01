"""SqlLedger — append-only, dual-backend SQL persistence implementing Ledger Protocol."""
from __future__ import annotations

from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import create_engine, event, insert, select, update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError

from operations_ledger import _evidence, _event_queries, _rows, _shift_queries
from operations_ledger._approval_store import _ApprovalStoreMixin, _noop_cm
from operations_ledger._assignment_store import _AssignmentStoreMixin
from operations_ledger._customer_request_store import _CustomerRequestStoreMixin
from operations_ledger._handover_store import _HandoverStoreMixin
from operations_ledger._incident_store import _IncidentStoreMixin
from operations_ledger._message_store import _MessageStoreMixin
from operations_ledger._report_store import _ReportStoreMixin
from operations_ledger.tables import (
    audit_records,
    corrections,
    messages,
    operational_events,
    shifts,
    tasks,
)

_EVENT_RECORD_TYPE = "OperationalEvent"
_TASK_RECORD_TYPE = "Task"


def make_engine(database_url: str, **kwargs) -> Engine:
    """SQLite: enforce FK PRAGMA, disable pysqlite's transactional emulation,
    issue BEGIN per transaction - deferred UNLESS `conn.info["cvf_write_
    reserving"]` was set (only `_sqlite_write_reserving_transaction` does
    this) - an unrelated read-only transaction never blocks a second writer."""
    engine = create_engine(database_url, future=True, **kwargs)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _record):  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            dbapi_connection.isolation_level = None

        @event.listens_for(engine, "begin")
        def _begin(conn):  # noqa: ANN001
            mode = "BEGIN IMMEDIATE" if conn.info.get("cvf_write_reserving") else "BEGIN"
            conn.exec_driver_sql(mode)

    return engine


class SqlLedger(
    _ApprovalStoreMixin, _AssignmentStoreMixin, _CustomerRequestStoreMixin, _IncidentStoreMixin,
    _HandoverStoreMixin, _MessageStoreMixin, _ReportStoreMixin,
):
    def __init__(self, database_url: str, models, engine: Engine | None = None):
        # ``models`` exposes Shift, OperationalEvent, Correction, ShiftStatus.
        # If an engine is injected (tests), it must have been built with
        # make_engine() so SQLite FK enforcement is active.
        self.models = models
        self.engine = engine or make_engine(database_url)

    @contextmanager
    def transaction(self):
        """Unit-of-work: yields a Connection with one open transaction.
        Pass the yielded value as ``unit=`` to chain writes atomically; it
        commits on normal exit and rolls back if any exception propagates —
        including one from an audit write. Ordinary deferred BEGIN on SQLite
        (F6): every other vertical uses this and must never reserve the
        writer lock merely by opening."""
        with self.engine.begin() as conn:
            yield conn

    @contextmanager
    def _sqlite_write_reserving_transaction(self):
        """F6/Finding 2: BEGIN IMMEDIATE on THIS transaction only, via a
        `conn.info` marker the "begin" listener checks - always cleared in
        `finally` (even on an exceptional exit), since `conn.info` is backed
        by the pooled DBAPI connection and would otherwise leak the marker
        forward into the next checkout of this same connection."""
        with self.engine.connect() as conn:
            conn.info["cvf_write_reserving"] = True
            try:
                with conn.begin():
                    yield conn
            finally:
                conn.info.pop("cvf_write_reserving", None)

    @contextmanager
    def report_mutation_transaction(self):
        """F6: write-reserving mode for Report generate/submit-review/approve/
        create_successor - guards the same current-report race. Only SQLite
        needs an upgrade; PostgreSQL row-locks on UPDATE."""
        if self.engine.dialect.name == "sqlite":
            with self._sqlite_write_reserving_transaction() as conn:
                yield conn
        else:
            with self.engine.begin() as conn:
                yield conn

    @contextmanager
    def report_freeze_transaction(self):
        """SPEC R22: SERIALIZABLE on PostgreSQL - one concurrent transaction
        wins, the other aborts and ``ShiftService.freeze`` retries. SQLite
        has no SERIALIZABLE level; BEGIN IMMEDIATE (F6, this connection only)
        gives an equivalent write-reserving guarantee there."""
        if self.engine.dialect.name == "postgresql":
            with self.engine.connect() as conn:
                conn = conn.execution_options(isolation_level="SERIALIZABLE")
                with conn.begin():
                    yield conn
        elif self.engine.dialect.name == "sqlite":
            with self._sqlite_write_reserving_transaction() as conn:
                yield conn
        else:
            with self.engine.begin() as conn:
                yield conn

    def _conn(self, unit) -> tuple[Connection, bool]:
        """Return (connection, owns_transaction). Opens one if unit is None."""
        if unit is not None:
            return unit, False
        return self.engine.begin(), True

    def _open(self, unit):
        """Context manager yielding a connection for ``unit``, same semantics
        as ``_conn`` but as a single ``with`` target (used by every method
        below and by ``_ApprovalStoreMixin``)."""
        conn, owns = self._conn(unit)
        return conn if owns else _noop_cm(conn)

    def _fetch_one(self, stmt, *, unit=None):
        with self._open(unit) as c:
            return c.execute(stmt).mappings().first()

    def _fetch_all(self, stmt, *, unit=None):
        with self._open(unit) as c:
            return c.execute(stmt).mappings().all()

    # --- shifts ---
    def create_shift(self, shift, *, unit=None):
        with self._open(unit) as c:
            c.execute(insert(shifts).values(**_rows.shift_row(shift)))
        return shift

    def get_shift(self, shift_id: UUID, *, unit=None):
        row = self._fetch_one(select(shifts).where(shifts.c.shift_id == shift_id), unit=unit)
        if row is None:
            raise KeyError(shift_id)
        return self.models.Shift(**dict(row))

    def list_shifts(self):
        # SPEC R25: delegated to _shift_queries for the file-size guard.
        return _shift_queries.list_shifts(self.engine, self.models)

    def close_shift(self, shift_id: UUID, *, unit=None):
        # SPEC R25: delegated to _shift_queries for the file-size guard.
        return _shift_queries.close_shift(self._open(unit), self.models, shift_id)

    def _assert_shift_not_frozen(self, conn, shift_id: UUID, what: str) -> None:
        # Post-freeze, the ONLY permitted change is a correction record -
        # every direct mutation path must check this, not just "create".
        row = conn.execute(
            select(shifts.c.status).where(shifts.c.shift_id == shift_id)
        ).mappings().first()
        if row is None:
            raise KeyError(shift_id)
        if row["status"] == self.models.ShiftStatus.FROZEN.value:
            raise ValueError(f"Cannot {what}: shift is frozen")

    def freeze_shift(self, shift_id: UUID, *, unit=None):
        # SPEC R25: delegated to _shift_queries for the file-size guard.
        return _shift_queries.freeze_shift(self._open(unit), self.models, shift_id)

    # --- messages: add_message/get_message implemented by _MessageStoreMixin ---
    def message_exists(self, message_id: UUID, *, unit=None) -> bool:
        with self._open(unit) as c:
            row = c.execute(
                select(messages.c.message_id).where(messages.c.message_id == message_id)
            ).first()
        return row is not None

    # --- events ---
    def add_event(self, event, *, unit=None):
        with self._open(unit) as c:
            self._assert_shift_not_frozen(c, event.shift_id, "add event to a frozen shift")
            c.execute(insert(operational_events).values(**_rows.event_row(event)))
            _evidence.insert_evidence(c, event.evidence, record_type=_EVENT_RECORD_TYPE, record_id=event.event_id)
        return event

    def get_event(self, event_id: UUID, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(select(operational_events).where(operational_events.c.event_id == event_id)).mappings().first()
            if row is None:
                raise KeyError(event_id)
            evidence = _evidence.evidence_for(c, self.models, record_type=_EVENT_RECORD_TYPE, record_id=event_id)
        return _rows.row_to_event(self.models, row, evidence=evidence)

    def list_events_for_shift(self, shift_id: UUID, *, unit=None) -> list:
        # SPEC R3/R20: delegated to _event_queries for the file-size guard.
        return _event_queries.list_events_for_shift(self._open(unit), self.models, shift_id)

    def put_event(self, event, *, allow_when_frozen: bool = False, unit=None):
        with self._open(unit) as c:
            if not allow_when_frozen:
                self._assert_shift_not_frozen(c, event.shift_id, "modify event in a frozen shift")
            c.execute(
                update(operational_events)
                .where(operational_events.c.event_id == event.event_id)
                .values(**_rows.event_row(event))
            )
        return event

    # --- tasks ---
    def add_task(self, task, *, unit=None):
        with self._open(unit) as c:
            self._assert_shift_not_frozen(c, task.shift_id, "add task to a frozen shift")
            # R9.6: task_id := intent_id, so a second POST /tasks against an
            # already-consumed intent collides on this PK - re-raised as the
            # same ValueError shape InMemoryLedger uses.
            try:
                c.execute(insert(tasks).values(**_rows.task_row(task)))
            except IntegrityError as exc:
                raise ValueError(f"duplicate task_id: {task.task_id}") from exc
            _evidence.insert_evidence(c, task.evidence, record_type=_TASK_RECORD_TYPE, record_id=task.task_id)
        return task

    def get_task(self, task_id: UUID, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(select(tasks).where(tasks.c.task_id == task_id)).mappings().first()
            if row is None:
                raise KeyError(task_id)
            evidence = _evidence.evidence_for(c, self.models, record_type=_TASK_RECORD_TYPE, record_id=task_id)
        return _rows.row_to_task(self.models, row, evidence=evidence)

    def put_task(self, task, *, allow_when_frozen: bool = False, unit=None):
        with self._open(unit) as c:
            if not allow_when_frozen:
                self._assert_shift_not_frozen(c, task.shift_id, "modify task in a frozen shift")
            c.execute(update(tasks).where(tasks.c.task_id == task.task_id).values(**_rows.task_row(task)))
        return task

    # --- customer requests: add_customer_request/get_customer_request/
    # put_customer_request/transition_customer_request implemented by
    # _CustomerRequestStoreMixin ---

    # --- users, approval receipts / task creation intents: see _ApprovalStoreMixin ---

    # --- corrections (append-only) ---
    def add_correction(self, correction, *, unit=None):
        with self._open(unit) as c:
            c.execute(insert(corrections).values(**_rows.correction_row(correction)))
        return correction

    def corrections_for(self, record_id: UUID, *, unit=None) -> list:
        with self._open(unit) as c:
            rows = c.execute(select(corrections).where(corrections.c.record_id == record_id)).mappings().all()
        return [_rows.row_to_correction(self.models, r) for r in rows]

    # --- audit (append-only) ---
    def audit_entries_for(self, record_id: str) -> list:
        with self.engine.connect() as conn:
            rows = conn.execute(select(audit_records).where(audit_records.c.target_id == record_id)).mappings().all()
        return [dict(r) for r in rows]

    def append_audit(self, record, *, unit=None) -> None:
        metadata = {
            "actor_role": record.actor_role, "control_chain": record.control_chain,
            "before_state": record.before_state, "after_state": record.after_state,
        }
        with self._open(unit) as c:
            c.execute(insert(audit_records).values(
                audit_id=record.audit_id, actor_id=record.actor_id, action=record.action,
                target_type=record.record_type, target_id=record.record_id,
                metadata=metadata, occurred_at=record.at,
            ))
