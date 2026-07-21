"""Audit trail.

CVF control: ``audit``. Every governed mutation must leave an append-only
record of who did what, when, to which record, and the before/after state.
The EA review found no audit-write anywhere in the codebase; this makes the
"every report line is traceable to evidence and approval history" promise real
for the golden vertical.

The store here is in-memory to match the current persistence layer. It is
append-only by contract: :meth:`AuditLog.record` never mutates or deletes an
existing entry. Swapping the sink for an append-only Postgres table later does
not change the call sites.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditRecord(BaseModel):
    """One immutable audit entry."""

    audit_id: UUID = Field(default_factory=uuid4)
    actor_id: str
    actor_role: str
    action: str
    record_type: str
    record_id: str
    control_chain: list[str] = Field(default_factory=list)
    before_state: str | None = None
    after_state: str | None = None
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog:
    """Append-only, thread-safe in-memory audit log."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._entries: list[AuditRecord] = []

    def record(
        self,
        *,
        actor_id: str,
        actor_role: str,
        action: str,
        record_type: str,
        record_id: str,
        control_chain: list[str] | None = None,
        before_state: str | None = None,
        after_state: str | None = None,
    ) -> AuditRecord:
        entry = AuditRecord(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            record_type=record_type,
            record_id=record_id,
            control_chain=control_chain or [],
            before_state=before_state,
            after_state=after_state,
        )
        return self.append(entry)

    def append(self, entry: AuditRecord) -> AuditRecord:
        """Append an already-built record (append-only)."""
        with self._lock:
            self._entries.append(entry)
        return entry

    def entries_for(self, record_id: str) -> list[AuditRecord]:
        with self._lock:
            return [e for e in self._entries if e.record_id == record_id]

    def all(self) -> list[AuditRecord]:
        with self._lock:
            return list(self._entries)


# Process-wide audit log, mirroring the module-level ledger singleton pattern
# already used in infrastructure/repository.py.
audit_log = AuditLog()
