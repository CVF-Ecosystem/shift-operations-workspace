"""SQL shift query/mutation helpers.

Split out of sql_ledger.py (P2C-OPERATIONS-CONSOLE-READ-SLICE Amendment 2,
SPEC R25) to keep that host module under the 300-line file-size guard after
restoring the docstring/formatting a prior repair had compressed. Owns only
the shift-query and shift-mutation select/update/materialization mechanics
used by SqlLedger.list_shifts/close_shift/freeze_shift - no other record
type's queries or mutations, no schema definition and no authorization
logic. Mirrors the _event_queries.py delegation pattern.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update

from operations_ledger.tables import shifts


def list_shifts(engine, models) -> list:
    with engine.connect() as conn:
        rows = conn.execute(select(shifts)).mappings().all()
    return [models.Shift(**dict(r)) for r in rows]


def close_shift(open_conn, models, shift_id: UUID):
    Status = models.ShiftStatus
    with open_conn as c:
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
    return models.Shift(**dict(row))


def freeze_shift(open_conn, models, shift_id: UUID):
    Status = models.ShiftStatus
    with open_conn as c:
        row = c.execute(select(shifts).where(shifts.c.shift_id == shift_id)).mappings().first()
        if row is None:
            raise KeyError(shift_id)
        if row["status"] == Status.FROZEN.value:
            return models.Shift(**dict(row))
        c.execute(
            update(shifts).where(shifts.c.shift_id == shift_id)
            .values(status=Status.FROZEN.value, version=row["version"] + 1)
        )
        row = c.execute(select(shifts).where(shifts.c.shift_id == shift_id)).mappings().first()
    return models.Shift(**dict(row))
