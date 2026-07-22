"""The Ledger Protocol — the persistence contract every backend must satisfy.

Structural typing (PEP 544): any object providing these methods IS a Ledger, so
neither backend needs to import the other and services depend only on this
interface. Domain records are typed loosely here (the domain models live in the
application layer today; when they move to operations-domain this Protocol can
import them directly).

Unit-of-work (P-FIX-2): ``transaction()`` returns a context manager yielding a
``unit`` token. Pass that token as the ``unit=`` keyword to every mutating call
made inside the same governed action (state change, correction insert, audit
append) so they commit or roll back together. A caller that does NOT pass
``unit`` still works exactly as before (each call opens/closes its own
transaction) — but every service in this codebase MUST use ``transaction()``
for any action that combines a state change with an audit write, per
EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md High Finding #5 (audit was not
atomic with mutation).
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class Ledger(Protocol):
    def transaction(self) -> AbstractContextManager[Any]: ...

    # --- shifts ---
    def create_shift(self, shift, *, unit: Any = None): ...
    def get_shift(self, shift_id: UUID, *, unit: Any = None): ...
    def list_shifts(self): ...
    def close_shift(self, shift_id: UUID, *, unit: Any = None): ...
    def freeze_shift(self, shift_id: UUID, *, unit: Any = None): ...

    # --- messages ---
    def add_message(self, message, *, unit: Any = None): ...
    # Narrow reference-validation seam (independent review, 2026-07-22,
    # Finding 2): message persistence itself is not implemented yet, but
    # customer_requests.source_message_id has a real FK to messages in the
    # migration. Before this method existed, InMemoryLedger silently accepted
    # ANY source_message_id (no check at all) while SqlLedger/SQLite raised an
    # uncaught IntegrityError from the FK - a real divergence that could
    # surface as an uncontrolled HTTP 500. This method lets a caller check
    # existence up front and raise the SAME controlled error on both backends
    # without implementing the full messages vertical.
    def message_exists(self, message_id: UUID, *, unit: Any = None) -> bool: ...

    # --- events ---
    def add_event(self, event, *, unit: Any = None): ...
    def get_event(self, event_id: UUID, *, unit: Any = None): ...
    # allow_when_frozen=True is for CorrectionService only: post-freeze the
    # ONLY permitted mutation is via a correction record (freeze-policy.yaml:
    # post_freeze_mutation = correction_record_only). Every other caller must
    # use the default False so a frozen shift blocks the write.
    def put_event(self, event, *, allow_when_frozen: bool = False, unit: Any = None): ...

    # --- tasks ---
    def add_task(self, task, *, unit: Any = None): ...
    def get_task(self, task_id: UUID, *, unit: Any = None): ...
    def put_task(self, task, *, allow_when_frozen: bool = False, unit: Any = None): ...

    # --- customer requests ---
    # shift_id on CustomerRequest is nullable (unlike Task.shift_id) - a
    # request not tied to any shift has no frozen-shift invariant to check.
    def add_customer_request(self, request, *, unit: Any = None): ...
    def get_customer_request(self, request_id: UUID, *, unit: Any = None): ...
    def put_customer_request(self, request, *, unit: Any = None): ...

    # --- corrections (append-only) ---
    def add_correction(self, correction, *, unit: Any = None): ...
    def corrections_for(self, record_id: UUID) -> list: ...

    # --- audit (append-only) ---
    def append_audit(self, record, *, unit: Any = None) -> None: ...
    def audit_entries_for(self, record_id: str) -> list: ...
