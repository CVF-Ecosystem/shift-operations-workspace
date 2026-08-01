"""Browser-required assignment-scoped reads (P2C-MUTATION-FULL-UI-C3B1, SPEC
R11/R36/R37).

The single application boundary for the three new browser list reads:
Message, Task and CustomerRequest, each scoped to one shift. Every call
requires verified authentication (the caller already holds a ``Principal``
from ``get_principal``) followed directly by current ACTIVE assignment — no
invented read-action permission exists for these routes (C3B1-WO-REV-F2).

Task and CustomerRequest reuse the exact ledger queries Report snapshots
already use (``list_tasks_for_shift``/``list_customer_requests_for_shift``,
both terminal-inclusive); Message gains the new parity method
``list_messages_for_shift``. No second repository/query implementation is
added for any of the three.

Ordering is exact SPEC R36: Message ``(created_at, message_id)``, Task
``(created_at, task_id)``, CustomerRequest ``(received_at, request_id)``, all
ascending — already the order each underlying ledger method returns. 0-500
matches return completely; 501+ raises :class:`ReadLimitExceeded` so the
router maps it to a controlled 422 without ever truncating silently.
"""

from __future__ import annotations

from uuid import UUID

from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.assignment_scope import require_active_assignment

# SPEC R11/R36: hard maximum per returned array; 501+ is a controlled 422.
MAX_RECORDS = 500


class ReadLimitExceeded(Exception):
    """Raised when a shift-scoped list exceeds the SPEC R36 hard maximum."""

    def __init__(self, surface: str, count: int):
        self.surface = surface
        self.count = count
        super().__init__(
            f"{surface} list exceeds {MAX_RECORDS}-record maximum; pagination not yet implemented"
        )


def _bounded(surface: str, records: list) -> list:
    if len(records) > MAX_RECORDS:
        raise ReadLimitExceeded(surface, len(records))
    return records


def list_messages_for_shift(ledger: Ledger, shift_id: UUID, principal: Principal) -> list:
    """SPEC R11/R37: authenticated then ACTIVE-assignment-scoped Message
    list, ascending ``(created_at, message_id)``. Raises ``KeyError`` for a
    missing/inaccessible shift (enumeration-safe 404) and
    :class:`ReadLimitExceeded` at 501+."""
    require_active_assignment(ledger, shift_id, principal)
    return _bounded("Message", ledger.list_messages_for_shift(shift_id))


def list_tasks_for_shift(ledger: Ledger, shift_id: UUID, principal: Principal) -> list:
    """SPEC R11/R37: authenticated then ACTIVE-assignment-scoped Task list
    including terminal history, ascending ``(created_at, task_id)`` — reuses
    the same ``list_tasks_for_shift`` Report generation already calls."""
    require_active_assignment(ledger, shift_id, principal)
    return _bounded("Task", ledger.list_tasks_for_shift(shift_id))


def list_customer_requests_for_shift(ledger: Ledger, shift_id: UUID, principal: Principal) -> list:
    """SPEC R11/R37: authenticated then ACTIVE-assignment-scoped
    CustomerRequest list including terminal history, ascending
    ``(received_at, request_id)`` — reuses the same
    ``list_customer_requests_for_shift`` Report generation already calls.
    Only requests bound to the requested shift are returned (SPEC R7: a null
    ``shift_id`` request is outside this shift console)."""
    require_active_assignment(ledger, shift_id, principal)
    return _bounded("CustomerRequest", ledger.list_customer_requests_for_shift(shift_id))
