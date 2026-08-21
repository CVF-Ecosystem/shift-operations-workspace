"""P4-A3 SPEC R6/R7/R11 - append-only store atomicity, isolation, concurrency."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from application_memory.errors import (
    AuthorizationScopeMismatchError,
    DuplicateEntryError,
    EntryExpiredError,
    EntryNotFoundError,
    EntryNotActiveError,
    RequestInvalidError,
)
from application_memory.hashing import content_digest, entry_digest
from application_memory.models import (
    MemoryClassification,
    MemoryEntryV1,
    MemoryLayer,
    MemoryPurpose,
    SourceRefV1,
    SourceType,
)
from application_memory.store import InMemoryApplicationMemoryStore

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
OWNER = "op1"
SCOPE = "a" * 64


def _source() -> SourceRefV1:
    return SourceRefV1(
        source_type=SourceType.PROJECT_KNOWLEDGE, source_id="s", source_version="1",
        source_content_digest_sha256=content_digest("text"), provenance_digest_sha256="b" * 64,
    )


def _entry(*, shift_id=uuid4(), owner_id=OWNER, scope_digest=SCOPE, **overrides) -> MemoryEntryV1:
    fields = dict(
        entry_id=uuid4(), layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
        owner_id=owner_id, shift_id=shift_id, authorization_scope_digest_sha256=scope_digest,
        classification=MemoryClassification.INTERNAL, source=_source(), content="hello",
        content_digest_sha256=content_digest("hello"), created_at_utc=NOW,
        expires_at_utc=NOW + timedelta(hours=1), policy_version="1.0", predecessor_id=None,
    )
    fields.update(overrides)
    dump = MemoryEntryV1.model_construct(**fields, entry_digest_sha256="0" * 64).model_dump(mode="python")
    dump.pop("entry_digest_sha256")
    fields["entry_digest_sha256"] = entry_digest(dump)
    return MemoryEntryV1(**fields)


class TestAdmit:
    def test_admit_and_get(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        assert store.get(entry.entry_id) == entry

    def test_duplicate_id_changes_zero_state(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        before = store.snapshot()
        with pytest.raises(DuplicateEntryError):
            store.admit(entry)
        assert store.snapshot() == before

    def test_store_is_deep_copy_isolated(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        retrieved = store.get(entry.entry_id)
        assert retrieved == entry
        # Frozen models cannot be mutated in place.
        with pytest.raises(Exception):
            retrieved.content = "mutated"  # type: ignore[misc]


class TestCorrect:
    def test_correct_appends_successor_and_tombstone(self):
        store = InMemoryApplicationMemoryStore()
        pred = _entry()
        store.admit(pred)
        successor = _entry(entry_id=uuid4(), predecessor_id=pred.entry_id)
        store.correct(
            successor=successor, owner_id=OWNER, shift_id=pred.shift_id,
            scope_digest=SCOPE, now=NOW,
        )
        entries, tombstones = store.snapshot()
        assert len(entries) == 2
        assert store.is_tombstoned(pred.entry_id)
        assert len(tombstones) == 1

    def test_correct_unknown_predecessor_rejected(self):
        store = InMemoryApplicationMemoryStore()
        successor = _entry(predecessor_id=uuid4())
        with pytest.raises(EntryNotFoundError):
            store.correct(successor=successor, owner_id=OWNER, shift_id=successor.shift_id, scope_digest=SCOPE, now=NOW)

    def test_cross_scope_correction_rejected_zero_state(self):
        store = InMemoryApplicationMemoryStore()
        pred = _entry()
        store.admit(pred)
        before = store.snapshot()
        successor = _entry(predecessor_id=pred.entry_id, owner_id="other")
        with pytest.raises(AuthorizationScopeMismatchError):
            store.correct(successor=successor, owner_id=OWNER, shift_id=pred.shift_id, scope_digest=SCOPE, now=NOW)
        assert store.snapshot() == before


class TestDelete:
    def test_delete_appends_tombstone(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        store.delete(entry_id=entry.entry_id, owner_id=OWNER, shift_id=entry.shift_id, scope_digest=SCOPE, now=NOW, created_at_utc=NOW)
        assert store.is_tombstoned(entry.entry_id)

    def test_delete_unknown_rejected(self):
        store = InMemoryApplicationMemoryStore()
        with pytest.raises(EntryNotFoundError):
            store.delete(entry_id=uuid4(), owner_id=OWNER, shift_id=uuid4(), scope_digest=SCOPE, now=NOW, created_at_utc=NOW)

    def test_double_delete_rejected(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        store.delete(entry_id=entry.entry_id, owner_id=OWNER, shift_id=entry.shift_id, scope_digest=SCOPE, now=NOW, created_at_utc=NOW)
        with pytest.raises(EntryNotActiveError):
            store.delete(entry_id=entry.entry_id, owner_id=OWNER, shift_id=entry.shift_id, scope_digest=SCOPE, now=NOW, created_at_utc=NOW)

    def test_cross_scope_delete_rejected_zero_state(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        before = store.snapshot()
        with pytest.raises(AuthorizationScopeMismatchError):
            store.delete(entry_id=entry.entry_id, owner_id="other", shift_id=entry.shift_id, scope_digest=SCOPE, now=NOW, created_at_utc=NOW)
        assert store.snapshot() == before


class TestExpired:
    def test_expired_correct_rejected_zero_state(self):
        store = InMemoryApplicationMemoryStore()
        pred = _entry(
            created_at_utc=NOW - timedelta(hours=2),
            expires_at_utc=NOW - timedelta(hours=1),
        )
        store.admit(pred)
        before = store.snapshot()
        successor = _entry(predecessor_id=pred.entry_id)
        with pytest.raises(EntryExpiredError):
            store.correct(successor=successor, owner_id=OWNER, shift_id=pred.shift_id, scope_digest=SCOPE, now=NOW)
        assert store.snapshot() == before


class TestConcurrency:
    def test_concurrent_delete_has_one_winner(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        errors: list[Exception] = []
        lock = threading.Lock()

        def worker():
            try:
                store.delete(
                    entry_id=entry.entry_id, owner_id=OWNER, shift_id=entry.shift_id,
                    scope_digest=SCOPE, now=NOW, created_at_utc=NOW,
                )
            except Exception as exc:  # noqa: BLE001 - any controlled error is a losing race
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # Exactly one delete wins; every other thread raised EntryNotActive.
        assert len(errors) == 7
        assert all(isinstance(e, EntryNotActiveError) for e in errors)
        assert store.is_tombstoned(entry.entry_id)

    def test_concurrent_correct_has_one_winner(self):
        store = InMemoryApplicationMemoryStore()
        pred = _entry()
        store.admit(pred)
        errors: list[Exception] = []
        lock = threading.Lock()

        def worker():
            try:
                store.correct(
                    successor=_entry(predecessor_id=pred.entry_id),
                    owner_id=OWNER, shift_id=pred.shift_id, scope_digest=SCOPE, now=NOW,
                )
            except Exception as exc:  # noqa: BLE001
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 7
        assert all(isinstance(e, (EntryNotActiveError, DuplicateEntryError)) for e in errors)
        entries, _ = store.snapshot()
        assert len(entries) == 2  # predecessor + exactly one successor


class TestIngressAndOutputIsolation:
    """P4A3-REV-F3 - forged model_construct entries are rejected at ingress and
    get()/snapshot() return independently deep-copied values."""

    def test_forged_model_construct_entry_bad_digest_rejected(self):
        store = InMemoryApplicationMemoryStore()
        valid = _entry()
        dump = valid.model_dump(mode="python")
        dump["entry_digest_sha256"] = "0" * 64
        forged = MemoryEntryV1.model_construct(**dump)
        before = store.snapshot()
        with pytest.raises(RequestInvalidError):
            store.admit(forged)
        assert store.snapshot() == before

    def test_forged_model_construct_entry_expiry_before_creation_rejected(self):
        store = InMemoryApplicationMemoryStore()
        valid = _entry()
        dump = valid.model_dump(mode="python")
        dump["expires_at_utc"] = NOW - timedelta(hours=1)
        forged = MemoryEntryV1.model_construct(**dump)
        before = store.snapshot()
        with pytest.raises(RequestInvalidError):
            store.admit(forged)
        assert store.snapshot() == before

    def test_forged_model_construct_entry_ttl_over_ceiling_rejected(self):
        """P4A3-REV-F3a - a SESSION entry with a 9-hour TTL is rejected even
        with a correctly recomputed digest (proving the TTL invariant, not a
        stale digest)."""
        store = InMemoryApplicationMemoryStore()
        fields = dict(
            entry_id=uuid4(), layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
            owner_id=OWNER, shift_id=uuid4(), authorization_scope_digest_sha256=SCOPE,
            classification=MemoryClassification.INTERNAL, source=_source(), content="hello",
            content_digest_sha256=content_digest("hello"), created_at_utc=NOW,
            expires_at_utc=NOW + timedelta(hours=9), policy_version="1.0", predecessor_id=None,
        )
        dump = MemoryEntryV1.model_construct(**fields, entry_digest_sha256="0" * 64).model_dump(mode="python")
        dump.pop("entry_digest_sha256")
        fields["entry_digest_sha256"] = entry_digest(dump)
        forged = MemoryEntryV1.model_construct(**fields)
        before = store.snapshot()
        with pytest.raises(RequestInvalidError):
            store.admit(forged)
        assert store.snapshot() == before

    def test_get_returns_isolated_copy(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        returned = store.get(entry.entry_id)
        assert returned is not None
        object.__setattr__(returned, "content_digest_sha256", "0" * 64)
        fresh = store.get(entry.entry_id)
        assert fresh is not None
        assert fresh.content_digest_sha256 == entry.content_digest_sha256

    def test_snapshot_returns_isolated_copies(self):
        store = InMemoryApplicationMemoryStore()
        entry = _entry()
        store.admit(entry)
        entries, _ = store.snapshot()
        object.__setattr__(entries[0], "entry_digest_sha256", "0" * 64)
        fresh, _ = store.snapshot()
        assert fresh[0].entry_digest_sha256 == entry.entry_digest_sha256
