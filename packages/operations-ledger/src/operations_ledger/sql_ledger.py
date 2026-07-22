"""SqlLedger — append-only, dual-backend SQL persistence implementing the Ledger Protocol.

Design notes:
* SQLAlchemy Core over the existing migration schema; the SQL migration stays
  the single schema authority (PostgreSQL is the schema of record).
* Dual-backend: ``tables.py`` uses SQLAlchemy's generic ``Uuid``/``JSON``
  types with a PostgreSQL variant, so the SAME table definitions work against
  SQLite (zero-setup dev/eval) or PostgreSQL (production) — pick by
  ``DATABASE_URL`` only, no code or schema change.
* Corrections are append-only: only INSERT, never UPDATE/DELETE. This is the
  durable form of "post-freeze changes go through a correction record and are
  never silently overwritten".
* Domain model classes are injected via ``models`` so this package does not
  import the application layer (dependency points one way: app -> ledger).
* ``psycopg``/other DB drivers are only required when actually connecting to
  that backend; importing this module never requires them.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import create_engine, event, insert, select, update
from sqlalchemy.engine import Engine

from operations_ledger import _rows
from operations_ledger.tables import (
    audit_records,
    corrections,
    operational_events,
    shifts,
    tasks,
)


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

    # --- shifts ---
    def create_shift(self, shift):
        with self.engine.begin() as conn:
            conn.execute(insert(shifts).values(**_rows.shift_row(shift)))
        return shift

    def get_shift(self, shift_id: UUID):
        with self.engine.connect() as conn:
            row = conn.execute(
                select(shifts).where(shifts.c.shift_id == shift_id)
            ).mappings().first()
        if row is None:
            raise KeyError(shift_id)
        return self.models.Shift(**dict(row))

    def list_shifts(self):
        with self.engine.connect() as conn:
            rows = conn.execute(select(shifts)).mappings().all()
        return [self.models.Shift(**dict(r)) for r in rows]

    def close_shift(self, shift_id: UUID):
        Status = self.models.ShiftStatus
        with self.engine.begin() as conn:
            row = conn.execute(
                select(shifts).where(shifts.c.shift_id == shift_id)
            ).mappings().first()
            if row is None:
                raise KeyError(shift_id)
            if row["status"] == Status.FROZEN.value:
                raise ValueError("Cannot close a frozen shift")
            conn.execute(
                update(shifts)
                .where(shifts.c.shift_id == shift_id)
                .values(status=Status.CLOSED.value, version=row["version"] + 1)
            )
            row = conn.execute(
                select(shifts).where(shifts.c.shift_id == shift_id)
            ).mappings().first()
        return self.models.Shift(**dict(row))

    def _assert_shift_not_frozen(self, conn, shift_id: UUID, what: str) -> None:
        # Post-freeze, the ONLY permitted change is a correction record.
        # Every direct mutation path must check this, not just "create".
        row = conn.execute(
            select(shifts.c.status).where(shifts.c.shift_id == shift_id)
        ).mappings().first()
        if row is None:
            raise KeyError(shift_id)
        if row["status"] == self.models.ShiftStatus.FROZEN.value:
            raise ValueError(f"Cannot {what}: shift is frozen")

    def freeze_shift(self, shift_id: UUID):
        Status = self.models.ShiftStatus
        with self.engine.begin() as conn:
            row = conn.execute(
                select(shifts).where(shifts.c.shift_id == shift_id)
            ).mappings().first()
            if row is None:
                raise KeyError(shift_id)
            if row["status"] == Status.FROZEN:
                return self.models.Shift(**dict(row))
            conn.execute(
                update(shifts)
                .where(shifts.c.shift_id == shift_id)
                .values(status=Status.FROZEN.value, version=row["version"] + 1)
            )
            row = conn.execute(
                select(shifts).where(shifts.c.shift_id == shift_id)
            ).mappings().first()
        return self.models.Shift(**dict(row))

    # --- messages (raw evidence preserved elsewhere; minimal here) ---
    def add_message(self, message):
        raise NotImplementedError("message persistence not yet wired to SQL")

    # --- events ---
    def add_event(self, event):
        with self.engine.begin() as conn:
            self._assert_shift_not_frozen(conn, event.shift_id, "add event to a frozen shift")
            conn.execute(insert(operational_events).values(**_rows.event_row(event)))
        return event

    def get_event(self, event_id: UUID):
        with self.engine.connect() as conn:
            row = conn.execute(
                select(operational_events).where(
                    operational_events.c.event_id == event_id
                )
            ).mappings().first()
        if row is None:
            raise KeyError(event_id)
        return _rows.row_to_event(self.models, row)

    def put_event(self, event, *, allow_when_frozen: bool = False):
        with self.engine.begin() as conn:
            if not allow_when_frozen:
                self._assert_shift_not_frozen(conn, event.shift_id, "modify event in a frozen shift")
            conn.execute(
                update(operational_events)
                .where(operational_events.c.event_id == event.event_id)
                .values(**_rows.event_row(event))
            )
        return event

    # --- tasks ---
    def add_task(self, task):
        with self.engine.begin() as conn:
            self._assert_shift_not_frozen(conn, task.shift_id, "add task to a frozen shift")
            conn.execute(insert(tasks).values(**_rows.task_row(task)))
        return task

    def get_task(self, task_id: UUID):
        with self.engine.connect() as conn:
            row = conn.execute(
                select(tasks).where(tasks.c.task_id == task_id)
            ).mappings().first()
        if row is None:
            raise KeyError(task_id)
        return _rows.row_to_task(self.models, row)

    def put_task(self, task, *, allow_when_frozen: bool = False):
        with self.engine.begin() as conn:
            if not allow_when_frozen:
                self._assert_shift_not_frozen(conn, task.shift_id, "modify task in a frozen shift")
            conn.execute(
                update(tasks).where(tasks.c.task_id == task.task_id).values(**_rows.task_row(task))
            )
        return task

    # --- corrections (append-only) ---
    def add_correction(self, correction):
        with self.engine.begin() as conn:
            conn.execute(insert(corrections).values(**_rows.correction_row(correction)))
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

    def append_audit(self, record) -> None:
        with self.engine.begin() as conn:
            conn.execute(
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
