"""Process-local usage ledger (SPEC R6).

Reserve-then-settle accounting so a concurrent caller cannot over-reserve past a
policy cap: the reservation is taken under a lock *before* dispatch and is later
either committed with actual usage or released.

Explicit non-claim: this is process-scoped in-memory state. It is NOT durable,
NOT shared across processes, and NOT production accounting. Durable usage/audit
persistence is deferred to a separate tranche with its own storage and
failure-recovery contract.

Money is integer USD-millis throughout; floats are never used, so reservation
arithmetic and receipt digests stay exact.
"""

from __future__ import annotations

import threading
from itertools import count

from .errors import BudgetUnavailableError, UsageLedgerError
from .models import BudgetFacts, UsageReservation


class UsageLedger:
    """Atomic in-process reservations against daily/monthly policy caps."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counter = count(1)
        self._open: dict[str, UsageReservation] = {}
        self._settled: set[str] = set()
        self._reserved_tokens = 0
        self._reserved_cost_usd_millis = 0
        self._committed_tokens = 0
        self._committed_cost_usd_millis = 0

    @property
    def committed_tokens(self) -> int:
        with self._lock:
            return self._committed_tokens

    @property
    def committed_cost_usd_millis(self) -> int:
        with self._lock:
            return self._committed_cost_usd_millis

    @property
    def outstanding_reservations(self) -> int:
        with self._lock:
            return len(self._open)

    @property
    def reserved_cost_usd_millis(self) -> int:
        with self._lock:
            return self._reserved_cost_usd_millis

    def reserve(self, facts: BudgetFacts, *, estimated_tokens: int) -> UsageReservation:
        """Atomically reserve estimated usage, or refuse fail-closed.

        Refuses when the per-request token limit is exceeded, or when the
        projected total would breach the daily or monthly cap. The projection
        is caller-supplied prior spend (``spent_today_usd_millis``/
        ``spent_month_usd_millis``, e.g. from durable accounting outside this
        process) PLUS this ledger's own already-committed cost PLUS its
        outstanding reservations PLUS this new estimate (P4A-REV-F2: the prior
        version omitted the ledger's own committed total, so sequential
        requests against the same caller-supplied prior-spend snapshot could
        each pass independently and blow through the cap). A cap of zero means
        "no cap declared" and is not treated as an immediate refusal.
        """
        if estimated_tokens < 0:
            raise UsageLedgerError("estimated tokens must be non-negative")
        if estimated_tokens > facts.per_request_token_limit:
            raise BudgetUnavailableError("estimated tokens exceed per-request limit")
        with self._lock:
            already_spent = (
                self._committed_cost_usd_millis
                + self._reserved_cost_usd_millis
                + facts.estimated_cost_usd_millis
            )
            projected_day = facts.spent_today_usd_millis + already_spent
            projected_month = facts.spent_month_usd_millis + already_spent
            if facts.daily_budget_usd_millis and projected_day > facts.daily_budget_usd_millis:
                raise BudgetUnavailableError("daily budget would be exceeded")
            if facts.monthly_budget_usd_millis and projected_month > facts.monthly_budget_usd_millis:
                raise BudgetUnavailableError("monthly budget would be exceeded")
            reservation = UsageReservation(
                reservation_id=f"res-{next(self._counter)}",
                estimated_tokens=estimated_tokens,
                estimated_cost_usd_millis=facts.estimated_cost_usd_millis,
            )
            self._open[reservation.reservation_id] = reservation
            self._reserved_tokens += reservation.estimated_tokens
            self._reserved_cost_usd_millis += reservation.estimated_cost_usd_millis
            return reservation

    def commit(self, reservation_id: str, *, actual_tokens: int, actual_cost_usd_millis: int) -> None:
        """Settle a reservation with actual usage exactly once."""
        if actual_tokens < 0 or actual_cost_usd_millis < 0:
            raise UsageLedgerError("actual usage must be non-negative")
        with self._lock:
            reservation = self._take_open(reservation_id)
            self._reserved_tokens -= reservation.estimated_tokens
            self._reserved_cost_usd_millis -= reservation.estimated_cost_usd_millis
            self._committed_tokens += actual_tokens
            self._committed_cost_usd_millis += actual_cost_usd_millis
            self._settled.add(reservation_id)

    def release(self, reservation_id: str) -> None:
        """Release an unused reservation exactly once (no usage recorded)."""
        with self._lock:
            reservation = self._take_open(reservation_id)
            self._reserved_tokens -= reservation.estimated_tokens
            self._reserved_cost_usd_millis -= reservation.estimated_cost_usd_millis
            self._settled.add(reservation_id)

    def _take_open(self, reservation_id: str) -> UsageReservation:
        """Pop an open reservation, refusing unknown or already-settled ids."""
        reservation = self._open.pop(reservation_id, None)
        if reservation is None:
            if reservation_id in self._settled:
                raise UsageLedgerError(f"reservation already settled: {reservation_id}")
            raise UsageLedgerError(f"unknown reservation: {reservation_id}")
        return reservation
