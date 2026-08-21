"""P4-A3 SPEC R5/R6/R7/R8 - ApplicationMemory service behavior.

Covers admit/read/correct/delete happy paths and every negative write's
zero-mutation guarantee, plus read ordering/limit/omission and scope isolation.
Fake revalidators are mechanics only - not governance proof.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from application_memory.hashing import content_digest, provenance_digest
from application_memory.models import (
    AdmissionRequestV1,
    MemoryClassification,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryPurpose,
    SourceRefV1,
    SourceRevalidationOutcome,
    SourceRevalidationV1,
    SourceType,
)
from application_memory.service import ApplicationMemory
from application_memory.store import InMemoryApplicationMemoryStore

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
OWNER = "op1"
SHIFT = uuid4()
SCOPE = "a" * 64


class _Clock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


def _source(text: str = "source text", *, source_id: str = "src-1", version: str = "1") -> SourceRefV1:
    return SourceRefV1(
        source_type=SourceType.PROJECT_KNOWLEDGE, source_id=source_id, source_version=version,
        source_content_digest_sha256=content_digest(text),
        provenance_digest_sha256=provenance_digest(
            source_type=SourceType.PROJECT_KNOWLEDGE.value, source_id=source_id,
            source_version=version, owner_scope="",
        ),
    )


def _request(*, content: str = "advisory note", ttl: int = 3600, source: SourceRefV1 | None = None) -> AdmissionRequestV1:
    return AdmissionRequestV1(
        layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
        classification=MemoryClassification.INTERNAL, content=content,
        source=source or _source(), requested_ttl_seconds=ttl,
    )


def _valid_revalidator():
    def revalidate(source: SourceRefV1) -> SourceRevalidationV1:
        return SourceRevalidationV1(source=source, outcome=SourceRevalidationOutcome.VALID, checked_at_utc=NOW)

    return revalidate


def _revalidator_with(outcome: SourceRevalidationOutcome):
    def revalidate(source: SourceRefV1) -> SourceRevalidationV1:
        return SourceRevalidationV1(source=source, outcome=outcome, checked_at_utc=NOW)

    return revalidate


def _service(*, clock=None, revalidator=None):
    clock = clock or _Clock(NOW)
    revalidator = revalidator or _valid_revalidator()
    store = InMemoryApplicationMemoryStore()
    return ApplicationMemory(store, clock=clock, revalidator=revalidator), store


class TestAdmit:
    def test_admit_positive(self):
        service, store = _service()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.ADMITTED
        assert outcome.receipt.appended_entries == 1
        assert len(outcome.entries) == 1
        assert len(store.snapshot()[0]) == 1

    def test_stale_source_zero_mutation(self):
        service, store = _service(revalidator=_revalidator_with(SourceRevalidationOutcome.STALE))
        before = store.snapshot()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
        assert outcome.receipt.appended_entries == 0
        assert store.snapshot() == before

    def test_revalidation_source_binding_mismatch_zero_mutation(self):
        def bad(source):
            return SourceRevalidationV1(source=_source(text="other"), outcome=SourceRevalidationOutcome.VALID, checked_at_utc=NOW)

        service, store = _service(revalidator=bad)
        before = store.snapshot()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
        assert store.snapshot() == before

    def test_ttl_over_ceiling_zero_mutation(self):
        service, store = _service()
        before = store.snapshot()
        outcome = service.admit(request=_request(ttl=24 * 3600), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.REQUEST_INVALID
        assert store.snapshot() == before

    def test_budget_breach_zero_mutation(self):
        service, store = _service()
        before = store.snapshot()
        oversized = "\U0001f600" * 3000
        outcome = service.admit(request=_request(content=oversized), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.BUDGET_BREACH
        assert store.snapshot() == before


class TestRead:
    def test_read_returns_admitted_entry(self):
        service, _ = _service()
        service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        outcome = service.read(owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=10)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.READ_COMPLETE
        assert len(outcome.entries) == 1

    def test_read_cross_scope_returns_nothing(self):
        service, _ = _service()
        service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        outcome = service.read(owner_id="other", shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=10)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.READ_COMPLETE
        assert outcome.entries == ()
        assert outcome.receipt.omitted_count == 0

    def test_read_invalid_limit(self):
        service, _ = _service()
        outcome = service.read(owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=0)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.RESULT_LIMIT_INVALID

    def test_read_expired_entry_omitted(self):
        clock = _Clock(NOW)
        service, _ = _service(clock=clock)
        service.admit(request=_request(ttl=60), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        clock.now = NOW + timedelta(hours=1)  # now past the 60s TTL
        outcome = service.read(owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=10)
        assert outcome.entries == ()
        assert outcome.receipt.omitted_count == 1

    def test_read_deterministic_order_and_limit(self):
        clock = _Clock(NOW)
        service, _ = _service(clock=clock)
        for i in range(5):
            service.admit(request=_request(content=f"note {i}"), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        outcome = service.read(owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=3)
        assert len(outcome.entries) == 3
        ids = [str(e.entry_id) for e in outcome.entries]
        assert ids == sorted(ids)  # equal created_at -> ascending entry_id


class TestCorrectAndDelete:
    def test_correct_tombstones_predecessor_and_reads_successor(self):
        service, store = _service()
        admitted = service.admit(request=_request(content="v1"), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        entry_id = admitted.entries[0].entry_id
        outcome = service.correct(
            entry_id=entry_id, request=_request(content="v2"), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE,
        )
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.CORRECTED
        assert outcome.receipt.appended_entries == 1
        assert outcome.receipt.appended_tombstones == 1
        assert store.is_tombstoned(entry_id)
        read = service.read(owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=10)
        assert len(read.entries) == 1
        assert read.entries[0].entry_id != entry_id

    def test_correct_unknown_zero_mutation(self):
        service, store = _service()
        before = store.snapshot()
        outcome = service.correct(
            entry_id=uuid4(), request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE,
        )
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.ENTRY_NOT_FOUND
        assert store.snapshot() == before

    def test_delete_reads_nothing(self):
        service, store = _service()
        admitted = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        entry_id = admitted.entries[0].entry_id
        outcome = service.delete(entry_id=entry_id, owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.DELETED
        assert outcome.receipt.appended_tombstones == 1
        assert store.is_tombstoned(entry_id)
        read = service.read(owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE, limit=10)
        assert read.entries == ()
        assert read.receipt.omitted_count == 1

    def test_delete_expired_zero_mutation(self):
        clock = _Clock(NOW)
        service, store = _service(clock=clock)
        admitted = service.admit(request=_request(ttl=60), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        entry_id = admitted.entries[0].entry_id
        clock.now = NOW + timedelta(hours=1)
        before = store.snapshot()
        outcome = service.delete(entry_id=entry_id, owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.ENTRY_EXPIRED
        assert store.snapshot() == before


class TestAdversarialRevalidation:
    """P4A3-REV-F2 - untrusted revalidation results/requests are reconstructed
    through normal Pydantic validation and fail closed with zero mutation."""

    def test_forged_model_construct_revalidation_naive_timestamp_rejected(self):
        def bad(source):
            return SourceRevalidationV1.model_construct(
                source=source, outcome=SourceRevalidationOutcome.VALID,
                checked_at_utc=datetime(2026, 8, 21, 12, 0),  # naive (not UTC)
            )

        service, store = _service(revalidator=bad)
        before = store.snapshot()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
        assert outcome.receipt.appended_entries == 0
        assert store.snapshot() == before

    def test_revalidation_malformed_nested_source_rejected(self):
        bad_source = SourceRefV1.model_construct(
            source_type=SourceType.PROJECT_KNOWLEDGE, source_id="bad id",  # invalid SafeId
            source_version="1", source_content_digest_sha256="a" * 64, provenance_digest_sha256="b" * 64,
        )

        def bad(source):
            return SourceRevalidationV1.model_construct(
                source=bad_source, outcome=SourceRevalidationOutcome.VALID, checked_at_utc=NOW,
            )

        service, store = _service(revalidator=bad)
        before = store.snapshot()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
        assert store.snapshot() == before

    def test_revalidation_wrong_result_type_rejected(self):
        def bad(source):
            return "not a revalidation result"

        service, store = _service(revalidator=bad)
        before = store.snapshot()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
        assert store.snapshot() == before

    def test_revalidation_callback_exception_fail_closed(self):
        def bad(source):
            raise RuntimeError("boom")

        service, store = _service(revalidator=bad)
        before = store.snapshot()
        outcome = service.admit(request=_request(), owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
        assert store.snapshot() == before

    def test_forged_model_construct_request_rejected(self):
        forged = AdmissionRequestV1.model_construct(
            layer=MemoryLayer.SESSION, purpose=MemoryPurpose.OPERATOR_WORKING_NOTE,
            classification=MemoryClassification.INTERNAL, content=12345,  # wrong type
            source=_source(), requested_ttl_seconds=3600,
        )
        service, store = _service()
        before = store.snapshot()
        outcome = service.admit(request=forged, owner_id=OWNER, shift_id=SHIFT, authorization_scope_digest=SCOPE)
        assert outcome.receipt.final_outcome is MemoryFinalOutcome.REQUEST_INVALID
        assert store.snapshot() == before
