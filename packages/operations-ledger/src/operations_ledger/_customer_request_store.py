"""SQL customer-request storage mixin (P2C-MUTATION-FULL-UI-C3B2, SPEC R12).

Split out of ``sql_ledger.py`` (same file-size-guard pattern as
``_message_store.py``/``_assignment_store.py``) to keep that host module
under the hard 300-line guard. ``_CustomerRequestStoreMixin`` expects
``self._open``/``self._assert_shift_not_frozen`` to already exist (provided
by ``SqlLedger``); it owns no state of its own.

``add_customer_request``/``get_customer_request``/``put_customer_request``
and their row mapping moved here intact from ``sql_ledger.py``/``_rows.py``
(Work Order section 3.1) - no behavior change, only relocation - alongside the
new ``transition_customer_request`` compare-and-swap this tranche adds.

``transition_customer_request`` mirrors ``_AssignmentStoreMixin.
revoke_assignment``'s CAS shape: the UPDATE's ``version = :expected``
predicate is the ONLY authority for whether the caller's expected version was
current, checked via rowcount, never inferred from a prior, separate SELECT -
so two concurrent callers racing on the same stale version can never both
"win".
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, select, update

from operations_ledger._rows import row_to_customer_request as _row_to_customer_request
from operations_ledger.tables import customer_requests


def _customer_request_row(request) -> dict:
    return {
        "request_id": request.request_id,
        "customer_id": request.customer_id,
        "shift_id": request.shift_id,
        "summary": request.summary,
        "details": request.details,
        "status": str(request.status),
        "source_message_id": request.source_message_id,
        "received_at": request.received_at,
        "promised_at": request.promised_at,
        "owner_id": request.owner_id,
        "version": request.version,
    }


class _CustomerRequestStoreMixin:
    # --- customer requests: shift_id is nullable, so the frozen-shift guard
    # only runs when one is present (mirrors InMemoryLedger). ---
    def add_customer_request(self, request, *, unit=None):
        with self._open(unit) as c:
            if request.shift_id is not None:
                self._assert_shift_not_frozen(c, request.shift_id, "add customer request to a frozen shift")
            c.execute(insert(customer_requests).values(**_customer_request_row(request)))
        return request

    def get_customer_request(self, request_id: UUID, *, unit=None):
        row = self._fetch_one(
            select(customer_requests).where(customer_requests.c.request_id == request_id), unit=unit
        )
        if row is None:
            raise KeyError(request_id)
        return _row_to_customer_request(self.models, row)

    def put_customer_request(self, request, *, unit=None):
        with self._open(unit) as c:
            if request.shift_id is not None:
                self._assert_shift_not_frozen(c, request.shift_id, "modify customer request in a frozen shift")
            c.execute(
                update(customer_requests).where(customer_requests.c.request_id == request.request_id)
                .values(**_customer_request_row(request))
            )
        return request

    def transition_customer_request(self, request_id: UUID, *, expected_version: int, target_status, unit=None):
        """P2C-MUTATION-FULL-UI-C3B2 (SPEC R12/R14): atomic compare-and-swap.
        A matching-version UPDATE increments the version exactly once and
        applies ``target_status``; a mismatch (including the version having
        moved between this method's own read and its write) is a controlled
        stale-version ``ValueError`` (mapped to 409 by the service layer) -
        no partial write, whatever the outcome."""
        with self._open(unit) as c:
            current = c.execute(
                select(customer_requests).where(customer_requests.c.request_id == request_id)
            ).mappings().first()
            if current is None:
                raise KeyError(request_id)
            if current["shift_id"] is not None:
                self._assert_shift_not_frozen(
                    c, current["shift_id"], "modify customer request in a frozen shift"
                )
            new_version = expected_version + 1
            result = c.execute(
                update(customer_requests)
                .where(
                    customer_requests.c.request_id == request_id,
                    customer_requests.c.version == expected_version,
                )
                .values(status=str(target_status), version=new_version)
            )
            if result.rowcount == 0:
                raise ValueError(
                    f"stale customer_request version: expected {expected_version}, "
                    f"request {request_id} was not at that version"
                )
            row = c.execute(
                select(customer_requests).where(customer_requests.c.request_id == request_id)
            ).mappings().first()
        return _row_to_customer_request(self.models, row)
