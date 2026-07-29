"""SQL event-list query for a single shift.

Split out of sql_ledger.py (P2C-OPERATIONS-CONSOLE-READ-SLICE Amendment 1,
SPEC R20) to keep that host module under the 300-line file-size guard after
adding the deterministic event-list query. Owns only the event-list
select/materialization/ordering mechanics used by
SqlLedger.list_events_for_shift - no mutation, no other aggregate query, no
schema definition and no authorization logic.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from operations_ledger import _evidence, _rows
from operations_ledger.tables import operational_events

_EVENT_RECORD_TYPE = "OperationalEvent"


def list_events_for_shift(open_conn, models, shift_id: UUID) -> list:
    """Deterministic event-list query for one shift (SPEC R3/R20).

    ``open_conn`` is the caller's already-open connection context manager
    (``SqlLedger._open(unit)``); this function does not manage its own
    transaction. Order: events with a non-null ``starts_at`` before events
    without one, ascending ``starts_at``, then ascending ``str(event_id)``.
    Evidence is preserved on every returned event.
    """
    with open_conn as c:
        rows = c.execute(
            select(operational_events).where(operational_events.c.shift_id == shift_id)
        ).mappings().all()
        events = [
            _rows.row_to_event(
                models, row,
                evidence=_evidence.evidence_for(
                    c, models, record_type=_EVENT_RECORD_TYPE, record_id=row["event_id"]
                ),
            )
            for row in rows
        ]
    events.sort(
        key=lambda e: (
            e.starts_at is None,
            e.starts_at if e.starts_at is not None else "",
            str(e.event_id),
        )
    )
    return events
