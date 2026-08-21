"""Process-local append-only store (SPEC R6/R7).

``InMemoryApplicationMemoryStore`` owns the single lock that makes every
admit/correct/delete atomic in-process. Entries and tombstones are append-only
and never mutated in place; because every stored model is frozen, a reader can
never mutate shared state through a returned reference (deep-copy isolation is
inherent). No durability or multi-process claim is made.

The store performs the structural atomicity guards (existence, active state,
duplicate id, lineage, scope, expiry) under the lock, so a correction/delete
race has exactly one winner and a losing operation raises with zero partial
write.
"""

from __future__ import annotations

import threading
from datetime import datetime
from uuid import UUID

from .errors import (
    AuthorizationScopeMismatchError,
    CorrectionLineageError,
    DuplicateEntryError,
    EntryExpiredError,
    EntryNotFoundError,
    EntryNotActiveError,
    RequestInvalidError,
)
from .models import MemoryEntryV1, TombstoneReason, TombstoneV1
from .policy import is_expired


class InMemoryApplicationMemoryStore:
    """One process-local append-only entry/tombstone map guarded by one lock."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: dict[str, MemoryEntryV1] = {}
        self._tombstones: dict[str, TombstoneV1] = {}

    def admit(self, entry: MemoryEntryV1) -> None:
        """SPEC R6 - append one immutable entry; a duplicate id changes zero
        state. The entry is reconstructed through normal validation first so a
        ``model_construct``-forged entry (bad digest/UTC/expiry/nested source)
        is rejected before any write."""
        entry = self._revalidate_entry(entry)
        key = str(entry.entry_id)
        with self._lock:
            if key in self._entries or key in self._tombstones:
                raise DuplicateEntryError(f"entry id already exists: {entry.entry_id}")
            self._entries[key] = entry.model_copy(deep=True)

    def correct(
        self,
        *,
        successor: MemoryEntryV1,
        owner_id: str,
        shift_id: UUID,
        scope_digest: str,
        now: datetime,
    ) -> None:
        """SPEC R7 - atomically append the successor and tombstone its active
        predecessor. Every refusal raises before any write."""
        successor = self._revalidate_entry(successor)
        with self._lock:
            self._require_correctable(successor, owner_id, shift_id, scope_digest, now)
            predecessor_id = str(successor.predecessor_id)
            self._entries[str(successor.entry_id)] = successor.model_copy(deep=True)
            self._tombstones[predecessor_id] = TombstoneV1(
                entry_id=successor.predecessor_id,
                reason=TombstoneReason.CORRECTED,
                created_at_utc=successor.created_at_utc,
            )

    def delete(
        self,
        *,
        entry_id: UUID,
        owner_id: str,
        shift_id: UUID,
        scope_digest: str,
        now: datetime,
        created_at_utc: datetime,
    ) -> None:
        """SPEC R7 - atomically append one tombstone; lineage is preserved."""
        with self._lock:
            self._require_deletable(entry_id, owner_id, shift_id, scope_digest, now)
            self._tombstones[str(entry_id)] = TombstoneV1(
                entry_id=entry_id, reason=TombstoneReason.DELETED, created_at_utc=created_at_utc
            )

    def get(self, entry_id: UUID) -> MemoryEntryV1 | None:
        with self._lock:
            entry = self._entries.get(str(entry_id))
            return entry.model_copy(deep=True) if entry is not None else None

    def is_tombstoned(self, entry_id: UUID) -> bool:
        with self._lock:
            return str(entry_id) in self._tombstones

    def snapshot(self) -> tuple[tuple[MemoryEntryV1, ...], tuple[TombstoneV1, ...]]:
        """A consistent read of every entry and tombstone (for tests/lineage).
        Returns independently deep-copied values so no returned alias can
        mutate internal state."""
        with self._lock:
            entries = tuple(e.model_copy(deep=True) for e in self._entries.values())
            tombstones = tuple(t.model_copy(deep=True) for t in self._tombstones.values())
            return entries, tombstones

    def _revalidate_entry(self, entry: MemoryEntryV1) -> MemoryEntryV1:
        """P4A3-REV-F3 - reconstruct an untrusted entry through normal
        Pydantic validation (a ``model_construct`` bypass carries no
        guarantee), rejecting a bad digest, invalid UTC/expiry, malformed
        nested source or forged lineage before any write."""
        try:
            primitive = (
                entry.model_dump(mode="python", warnings=False)
                if isinstance(entry, MemoryEntryV1)
                else entry
            )
            return MemoryEntryV1.model_validate(primitive)
        except Exception:
            raise RequestInvalidError("entry failed ingress validation") from None

    def _require_correctable(
        self, successor: MemoryEntryV1, owner_id: str, shift_id: UUID, scope_digest: str, now: datetime
    ) -> None:
        if successor.predecessor_id is None:
            raise CorrectionLineageError("correction requires a predecessor id")
        if str(successor.entry_id) in self._entries or str(successor.entry_id) in self._tombstones:
            raise DuplicateEntryError(f"successor id already exists: {successor.entry_id}")
        predecessor = self._entries.get(str(successor.predecessor_id))
        if predecessor is None:
            raise EntryNotFoundError(f"predecessor not found: {successor.predecessor_id}")
        if str(successor.predecessor_id) in self._tombstones:
            raise EntryNotActiveError(f"predecessor already tombstoned: {successor.predecessor_id}")
        self._require_scope(predecessor, owner_id, shift_id, scope_digest)
        self._require_active(predecessor, now)
        if (
            successor.owner_id != predecessor.owner_id
            or successor.shift_id != predecessor.shift_id
            or successor.authorization_scope_digest_sha256
            != predecessor.authorization_scope_digest_sha256
        ):
            raise AuthorizationScopeMismatchError("correction must not change owner/shift/scope")

    def _require_deletable(
        self, entry_id: UUID, owner_id: str, shift_id: UUID, scope_digest: str, now: datetime
    ) -> None:
        entry = self._entries.get(str(entry_id))
        if entry is None:
            raise EntryNotFoundError(f"entry not found: {entry_id}")
        if str(entry_id) in self._tombstones:
            raise EntryNotActiveError(f"entry already tombstoned: {entry_id}")
        self._require_scope(entry, owner_id, shift_id, scope_digest)
        self._require_active(entry, now)

    @staticmethod
    def _require_scope(entry: MemoryEntryV1, owner_id: str, shift_id: UUID, scope_digest: str) -> None:
        if (
            entry.owner_id != owner_id
            or entry.shift_id != shift_id
            or entry.authorization_scope_digest_sha256 != scope_digest
        ):
            raise AuthorizationScopeMismatchError("owner/shift/authorization-scope does not match")

    @staticmethod
    def _require_active(entry: MemoryEntryV1, now: datetime) -> None:
        if is_expired(now=now, expires_at_utc=entry.expires_at_utc):
            raise EntryExpiredError(f"entry expired: {entry.entry_id}")
