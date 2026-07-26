"""SqlLedger — append-only, dual-backend SQL persistence implementing Ledger Protocol."""

from __future__ import annotations

from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import create_engine, event, insert, select, update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError

from operations_ledger import _evidence, _rows
from operations_ledger.tables import (
    approval_receipts,
    audit_records,
    corrections,
    customer_requests,
    messages,
    operational_events,
    shifts,
    task_creation_intents,
    tasks,
    users,
)

_EVENT_RECORD_TYPE = "OperationalEvent"
_TASK_RECORD_TYPE = "Task"


def make_engine(database_url: str, **kwargs) -> Engine:
    """Create an Engine with the backend correctly configured.

    Always use this instead of ``create_engine`` for the ledger. On SQLite it
    registers a connect-time PRAGMA so foreign keys are ENFORCED (SQLite has
    them OFF by default). The listener is attached before any connection is
    pooled, so every connection — including the first — honours it. Without
    this, SQLite would silently ignore the FK constraints that PostgreSQL
    enforces, and the two backends would diverge on referential integrity.
    """
    engine = create_engine(database_url, future=True, **kwargs)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _record):  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


class SqlLedger:
    def __init__(self, database_url: str, models, engine: Engine | None = None):
        # ``models`` exposes Shift, OperationalEvent, Correction, ShiftStatus.
        # If an engine is injected (tests), it must have been built with
        # make_engine() so SQLite FK enforcement is active.
        self.models = models
        self.engine = engine or make_engine(database_url)

    @contextmanager
    def transaction(self):
        """Unit-of-work: yields a Connection with one open transaction.

        Pass the yielded value as ``unit=`` to chain writes atomically. The
        transaction commits when the block exits normally and rolls back if
        any exception propagates — including one raised by an audit write.
        """
        with self.engine.begin() as conn:
            yield conn

    def _conn(self, unit) -> tuple[Connection, bool]:
        """Return (connection, owns_transaction). Opens one if unit is None."""
        if unit is not None:
            return unit, False
        return self.engine.begin(), True

    def _fetch_one(self, stmt, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            return c.execute(stmt).mappings().first()

    def _fetch_all(self, stmt, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            return c.execute(stmt).mappings().all()

    # --- shifts ---
    def create_shift(self, shift, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(insert(shifts).values(**_rows.shift_row(shift)))
        return shift

    def get_shift(self, shift_id: UUID, *, unit=None):
        row = self._fetch_one(select(shifts).where(shifts.c.shift_id == shift_id), unit=unit)
        if row is None:
            raise KeyError(shift_id)
        return self.models.Shift(**dict(row))

    def list_shifts(self):
        with self.engine.connect() as conn:
            rows = conn.execute(select(shifts)).mappings().all()
        return [self.models.Shift(**dict(r)) for r in rows]

    def close_shift(self, shift_id: UUID, *, unit=None):
        Status = self.models.ShiftStatus
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            row = c.execute(select(shifts).where(shifts.c.shift_id == shift_id)).mappings().first()
            if row is None:
                raise KeyError(shift_id)
            if row["status"] == Status.FROZEN.value:
                raise ValueError("Cannot close a frozen shift")
            c.execute(
                update(shifts).where(shifts.c.shift_id == shift_id)
                .values(status=Status.CLOSED.value, version=row["version"] + 1)
            )
            row = c.execute(select(shifts).where(shifts.c.shift_id == shift_id)).mappings().first()
        return self.models.Shift(**dict(row))

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
        Status = self.models.ShiftStatus
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            row = c.execute(select(shifts).where(shifts.c.shift_id == shift_id)).mappings().first()
            if row is None:
                raise KeyError(shift_id)
            if row["status"] == Status.FROZEN.value:
                return self.models.Shift(**dict(row))
            c.execute(
                update(shifts).where(shifts.c.shift_id == shift_id)
                .values(status=Status.FROZEN.value, version=row["version"] + 1)
            )
            row = c.execute(select(shifts).where(shifts.c.shift_id == shift_id)).mappings().first()
        return self.models.Shift(**dict(row))

    # --- messages (raw evidence preserved elsewhere; minimal here) ---
    def add_message(self, message, *, unit=None):
        raise NotImplementedError("message persistence not yet wired to SQL")

    def message_exists(self, message_id: UUID, *, unit=None) -> bool:
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            row = c.execute(
                select(messages.c.message_id).where(messages.c.message_id == message_id)
            ).first()
        return row is not None

    # --- events ---
    def add_event(self, event, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            self._assert_shift_not_frozen(c, event.shift_id, "add event to a frozen shift")
            c.execute(insert(operational_events).values(**_rows.event_row(event)))
            _evidence.insert_evidence(
                c, event.evidence, record_type=_EVENT_RECORD_TYPE, record_id=event.event_id
            )
        return event

    def get_event(self, event_id: UUID, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            row = c.execute(
                select(operational_events).where(operational_events.c.event_id == event_id)
            ).mappings().first()
            if row is None:
                raise KeyError(event_id)
            evidence = _evidence.evidence_for(
                c, self.models, record_type=_EVENT_RECORD_TYPE, record_id=event_id
            )
        return _rows.row_to_event(self.models, row, evidence=evidence)

    def put_event(self, event, *, allow_when_frozen: bool = False, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
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
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            self._assert_shift_not_frozen(c, task.shift_id, "add task to a frozen shift")
            # R9.6: task_id := intent_id on the consuming path, so a second
            # POST /tasks against an already-consumed intent collides on this
            # PK. Re-raised as the same ValueError shape InMemoryLedger uses
            # so the application layer maps both backends identically.
            try:
                c.execute(insert(tasks).values(**_rows.task_row(task)))
            except IntegrityError as exc:
                raise ValueError(f"duplicate task_id: {task.task_id}") from exc
            _evidence.insert_evidence(
                c, task.evidence, record_type=_TASK_RECORD_TYPE, record_id=task.task_id
            )
        return task

    def get_task(self, task_id: UUID, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            row = c.execute(select(tasks).where(tasks.c.task_id == task_id)).mappings().first()
            if row is None:
                raise KeyError(task_id)
            evidence = _evidence.evidence_for(
                c, self.models, record_type=_TASK_RECORD_TYPE, record_id=task_id
            )
        return _rows.row_to_task(self.models, row, evidence=evidence)

    def put_task(self, task, *, allow_when_frozen: bool = False, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            if not allow_when_frozen:
                self._assert_shift_not_frozen(c, task.shift_id, "modify task in a frozen shift")
            c.execute(
                update(tasks).where(tasks.c.task_id == task.task_id).values(**_rows.task_row(task))
            )
        return task

    # --- customer requests: shift_id is nullable, so the frozen-shift guard
    # only runs when one is actually present (mirrors InMemoryLedger). ---
    def add_customer_request(self, request, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            if request.shift_id is not None:
                self._assert_shift_not_frozen(c, request.shift_id, "add customer request to a frozen shift")
            c.execute(insert(customer_requests).values(**_rows.customer_request_row(request)))
        return request

    def get_customer_request(self, request_id: UUID, *, unit=None):
        row = self._fetch_one(
            select(customer_requests).where(customer_requests.c.request_id == request_id),
            unit=unit,
        )
        if row is None:
            raise KeyError(request_id)
        return _rows.row_to_customer_request(self.models, row)

    def put_customer_request(self, request, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            if request.shift_id is not None:
                self._assert_shift_not_frozen(c, request.shift_id, "modify customer request in a frozen shift")
            c.execute(
                update(customer_requests)
                .where(customer_requests.c.request_id == request.request_id)
                .values(**_rows.customer_request_row(request))
            )
        return request

    # --- users (P2-B: real authentication) ---
    def add_user(self, user, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(insert(users).values(**_rows.user_row(user)))
        return user

    def get_user_by_username(self, username: str, *, unit=None):
        row = self._fetch_one(select(users).where(users.c.username == username), unit=unit)
        return _rows.row_to_user(self.models, row) if row is not None else None

    def get_user_by_id(self, user_id: str, *, unit=None):
        row = self._fetch_one(select(users).where(users.c.user_id == user_id), unit=unit)
        return _rows.row_to_user(self.models, row) if row is not None else None

    # --- approval receipts / task creation intents ---
    def add_approval_receipt(self, receipt, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(insert(approval_receipts).values(**_rows.approval_receipt_row(receipt)))
        return receipt

    def list_approval_receipts_for(
        self,
        *,
        record_type,
        record_id,
        action,
        target_version,
        risk_class,
        payload_digest,
        unit=None,
    ):
        clauses = [
            approval_receipts.c.record_type == record_type,
            approval_receipts.c.record_id == record_id,
            approval_receipts.c.action == action,
            approval_receipts.c.target_version == target_version,
            approval_receipts.c.risk_class == risk_class,
            approval_receipts.c.payload_digest == payload_digest,
        ]
        rows = self._fetch_all(
            select(approval_receipts).where(*clauses),
            unit=unit,
        )
        return [_rows.row_to_approval_receipt(self.models, r) for r in rows]


    def get_approval_receipt(
        self, *, record_type, record_id, action, target_version, approver_id, unit=None
    ):
        row = self._fetch_one(
            select(approval_receipts).where(
                approval_receipts.c.record_type == record_type,
                approval_receipts.c.record_id == record_id,
                approval_receipts.c.action == action,
                approval_receipts.c.target_version == target_version,
                approval_receipts.c.approver_id == approver_id,
            ),
            unit=unit,
        )
        return _rows.row_to_approval_receipt(self.models, row) if row is not None else None

    def add_task_creation_intent(self, intent, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(
                insert(task_creation_intents).values(**_rows.task_creation_intent_row(intent))
            )
        return intent

    def get_task_creation_intent(self, intent_id, *, unit=None):
        row = self._fetch_one(
            select(task_creation_intents).where(task_creation_intents.c.intent_id == intent_id),
            unit=unit,
        )
        if row is None:
            raise KeyError(intent_id)
        return _rows.row_to_task_creation_intent(self.models, row)

    # --- corrections (append-only) ---
    def add_correction(self, correction, *, unit=None):
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(insert(corrections).values(**_rows.correction_row(correction)))
        return correction

    def corrections_for(self, record_id: UUID) -> list:
        with self.engine.connect() as conn:
            rows = conn.execute(
                select(corrections).where(corrections.c.record_id == record_id)
            ).mappings().all()
        return [_rows.row_to_correction(self.models, r) for r in rows]

    # --- audit (append-only) ---
    def audit_entries_for(self, record_id: str) -> list:
        with self.engine.connect() as conn:
            rows = conn.execute(
                select(audit_records).where(audit_records.c.target_id == record_id)
            ).mappings().all()
        return [dict(r) for r in rows]

    def append_audit(self, record, *, unit=None) -> None:
        conn, owns = self._conn(unit)
        with (conn if owns else _noop_cm(conn)) as c:
            c.execute(
                insert(audit_records).values(
                    audit_id=record.audit_id,
                    actor_id=record.actor_id,
                    action=record.action,
                    target_type=record.record_type,
                    target_id=record.record_id,
                    metadata={
                        "actor_role": record.actor_role,
                        "control_chain": record.control_chain,
                        "before_state": record.before_state,
                        "after_state": record.after_state,
                    },
                    occurred_at=record.at,
                )
            )


@contextmanager
def _noop_cm(conn: Connection):
    """Wrap an already-open connection for use in a ``with`` block without
    closing/committing it (the owning ``transaction()`` block does that)."""
    yield conn
