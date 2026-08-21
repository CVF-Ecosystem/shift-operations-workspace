"""``ApplicationMemory`` - the P4-A3 pure-package orchestrator (SPEC R5/R6/R7/R8).

Owns admission/read/correct/delete over the injected store, clock and source-
revalidation callback; every refusal returns a sanitized zero-mutation receipt.
Performs no I/O, provider, environment, database or network access of its own.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from .errors import (
    ApplicationMemoryError,
    AuthorizationScopeMismatchError,
    BudgetBreachError,
    CorrectionLineageError,
    DuplicateEntryError,
    EntryExpiredError,
    EntryNotFoundError,
    EntryNotActiveError,
    RequestInvalidError,
    ResultLimitError,
    SourceRevalidationFailedError,
)
from .hashing import content_digest, entry_digest
from .models import (
    MAX_CONTENT_UTF8_BYTES,
    AdmissionRequestV1,
    MemoryEntryV1,
    MemoryFinalOutcome,
    MemoryOperation,
    SourceRefV1,
    SourceRevalidationOutcome,
    SourceRevalidationV1,
    TombstoneReason,
)
from .policy import compute_expiry, is_expired, normalize_content, validate_result_limit
from .receipts import MemoryReceiptV1, build_receipt

_ERROR_OUTCOME: dict[type[ApplicationMemoryError], MemoryFinalOutcome] = {
    RequestInvalidError: MemoryFinalOutcome.REQUEST_INVALID,
    AuthorizationScopeMismatchError: MemoryFinalOutcome.AUTHORIZATION_SCOPE_MISMATCH,
    SourceRevalidationFailedError: MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED,
    DuplicateEntryError: MemoryFinalOutcome.DUPLICATE_ENTRY,
    EntryNotFoundError: MemoryFinalOutcome.ENTRY_NOT_FOUND,
    EntryNotActiveError: MemoryFinalOutcome.ENTRY_NOT_ACTIVE,
    EntryExpiredError: MemoryFinalOutcome.ENTRY_EXPIRED,
    CorrectionLineageError: MemoryFinalOutcome.CORRECTION_LINEAGE_INVALID,
    BudgetBreachError: MemoryFinalOutcome.BUDGET_BREACH,
    ResultLimitError: MemoryFinalOutcome.RESULT_LIMIT_INVALID,
}


def _final_outcome(exc: ApplicationMemoryError) -> MemoryFinalOutcome:
    return _ERROR_OUTCOME.get(type(exc), MemoryFinalOutcome.REQUEST_INVALID)


class MemoryOutcome:
    """Content-bearing entries (when applicable) plus the sanitized receipt."""

    __slots__ = ("entries", "receipt")

    def __init__(self, *, entries: tuple[MemoryEntryV1, ...], receipt: MemoryReceiptV1) -> None:
        self.entries = entries
        self.receipt = receipt


class ApplicationMemory:
    """Holds an injected store, clock and source-revalidation callback."""

    def __init__(
        self,
        store,
        *,
        clock,
        revalidator,
    ) -> None:
        self._store = store
        self._clock = clock
        self._revalidator = revalidator

    @property
    def store(self):
        return self._store

    def admit(
        self, *, request: AdmissionRequestV1, owner_id: str, shift_id: UUID, authorization_scope_digest: str
    ) -> MemoryOutcome:
        now = self._clock()
        try:
            request = self._coerce_request(request)
            self._check_content_budget(request)
            self._check_revalidation(request.source)
            entry = self._build_entry(
                request, owner_id=owner_id, shift_id=shift_id,
                authorization_scope_digest=authorization_scope_digest, now=now, predecessor_id=None,
            )
            self._store.admit(entry)
        except ApplicationMemoryError as exc:
            return self._negative(MemoryOperation.ADMIT, exc, owner_id, shift_id, authorization_scope_digest, now)
        receipt = build_receipt(
            operation=MemoryOperation.ADMIT, final_outcome=MemoryFinalOutcome.ADMITTED, reason_code="",
            owner_id=owner_id, shift_id=shift_id, authorization_scope_digest_sha256=authorization_scope_digest,
            layer=entry.layer, purpose=entry.purpose, classification=entry.classification,
            entry_id=entry.entry_id, entry_digest_sha256=entry.entry_digest_sha256,
            source_content_digest_sha256=entry.source.source_content_digest_sha256,
            provenance_digest_sha256=entry.source.provenance_digest_sha256,
            expires_at_utc=entry.expires_at_utc, appended_entries=1, appended_tombstones=0,
            created_at_utc=now,
        )
        return MemoryOutcome(entries=(entry,), receipt=receipt)

    def correct(
        self,
        *,
        entry_id: UUID,
        request: AdmissionRequestV1,
        owner_id: str,
        shift_id: UUID,
        authorization_scope_digest: str,
    ) -> MemoryOutcome:
        now = self._clock()
        try:
            request = self._coerce_request(request)
            self._check_content_budget(request)
            self._check_revalidation(request.source)
            successor = self._build_entry(
                request, owner_id=owner_id, shift_id=shift_id,
                authorization_scope_digest=authorization_scope_digest, now=now, predecessor_id=entry_id,
            )
            self._store.correct(
                successor=successor, owner_id=owner_id, shift_id=shift_id,
                scope_digest=authorization_scope_digest, now=now,
            )
        except ApplicationMemoryError as exc:
            return self._negative(MemoryOperation.CORRECT, exc, owner_id, shift_id, authorization_scope_digest, now)
        receipt = build_receipt(
            operation=MemoryOperation.CORRECT, final_outcome=MemoryFinalOutcome.CORRECTED, reason_code="",
            owner_id=owner_id, shift_id=shift_id, authorization_scope_digest_sha256=authorization_scope_digest,
            layer=successor.layer, purpose=successor.purpose, classification=successor.classification,
            entry_id=successor.entry_id, entry_digest_sha256=successor.entry_digest_sha256,
            predecessor_entry_id=entry_id, tombstoned_entry_id=entry_id,
            tombstone_reason=TombstoneReason.CORRECTED,
            source_content_digest_sha256=successor.source.source_content_digest_sha256,
            provenance_digest_sha256=successor.source.provenance_digest_sha256,
            expires_at_utc=successor.expires_at_utc, appended_entries=1, appended_tombstones=1,
            created_at_utc=now,
        )
        return MemoryOutcome(entries=(successor,), receipt=receipt)

    def delete(
        self, *, entry_id: UUID, owner_id: str, shift_id: UUID, authorization_scope_digest: str
    ) -> MemoryOutcome:
        now = self._clock()
        try:
            self._store.delete(
                entry_id=entry_id, owner_id=owner_id, shift_id=shift_id,
                scope_digest=authorization_scope_digest, now=now, created_at_utc=now,
            )
        except ApplicationMemoryError as exc:
            return self._negative(MemoryOperation.DELETE, exc, owner_id, shift_id, authorization_scope_digest, now)
        receipt = build_receipt(
            operation=MemoryOperation.DELETE, final_outcome=MemoryFinalOutcome.DELETED, reason_code="",
            owner_id=owner_id, shift_id=shift_id, authorization_scope_digest_sha256=authorization_scope_digest,
            tombstoned_entry_id=entry_id, tombstone_reason=TombstoneReason.DELETED,
            appended_entries=0, appended_tombstones=1, created_at_utc=now,
        )
        return MemoryOutcome(entries=(), receipt=receipt)

    def read(
        self, *, owner_id: str, shift_id: UUID, authorization_scope_digest: str, limit: int
    ) -> MemoryOutcome:
        now = self._clock()
        try:
            validate_result_limit(limit)
        except ResultLimitError as exc:
            return self._negative(MemoryOperation.READ, exc, owner_id, shift_id, authorization_scope_digest, now)

        entries, tombstones = self._store.snapshot()
        tombstoned_ids = {t.entry_id for t in tombstones}
        retained: list[MemoryEntryV1] = []
        omitted = 0
        for entry in entries:
            if (
                entry.owner_id != owner_id
                or entry.shift_id != shift_id
                or entry.authorization_scope_digest_sha256 != authorization_scope_digest
            ):
                continue  # not in this caller's scope - not even a candidate
            if entry.entry_id in tombstoned_ids:
                omitted += 1
                continue
            if is_expired(now=now, expires_at_utc=entry.expires_at_utc):
                omitted += 1
                continue
            try:
                self._check_revalidation(entry.source)
            except ApplicationMemoryError:
                omitted += 1
                continue
            retained.append(entry)

        retained.sort(key=lambda e: (e.created_at_utc, str(e.entry_id)))
        selected = retained[:limit]
        receipt = build_receipt(
            operation=MemoryOperation.READ, final_outcome=MemoryFinalOutcome.READ_COMPLETE, reason_code="",
            owner_id=owner_id, shift_id=shift_id, authorization_scope_digest_sha256=authorization_scope_digest,
            returned_entry_ids=tuple(e.entry_id for e in selected),
            returned_entry_digests=tuple(e.entry_digest_sha256 for e in selected),
            omitted_count=omitted, appended_entries=0, appended_tombstones=0,
            created_at_utc=now,
        )
        return MemoryOutcome(entries=tuple(selected), receipt=receipt)

    # -- internals ---------------------------------------------------------

    def _negative(
        self, operation: MemoryOperation, exc: ApplicationMemoryError, owner_id: str, shift_id: UUID,
        scope_digest: str, now: datetime,
    ) -> MemoryOutcome:
        receipt = build_receipt(
            operation=operation, final_outcome=_final_outcome(exc), reason_code=exc.reason_code,
            owner_id=owner_id, shift_id=shift_id, authorization_scope_digest_sha256=scope_digest,
            appended_entries=0, appended_tombstones=0, created_at_utc=now,
        )
        return MemoryOutcome(entries=(), receipt=receipt)

    def _check_content_budget(self, request: AdmissionRequestV1) -> None:
        if len(request.content.encode("utf-8")) > MAX_CONTENT_UTF8_BYTES:
            raise BudgetBreachError("content exceeds the UTF-8 byte bound")

    def _check_revalidation(self, source: SourceRefV1) -> None:
        try:
            raw = self._revalidator(source)
        except Exception:
            raise SourceRevalidationFailedError("source revalidator raised") from None
        result = self._coerce_revalidation(raw)
        if result.outcome is not SourceRevalidationOutcome.VALID:
            raise SourceRevalidationFailedError(f"source revalidation outcome: {result.outcome.value}")
        if result.source != source:
            raise SourceRevalidationFailedError("revalidation source binding does not match the declared source")

    def _coerce_request(self, request) -> AdmissionRequestV1:
        """P4A3-REV-F2 - reconstruct an untrusted request through normal
        Pydantic validation; a malformed value fails closed."""
        return self._reconstruct(request, AdmissionRequestV1, RequestInvalidError)

    def _coerce_revalidation(self, raw) -> SourceRevalidationV1:
        """P4A3-REV-F2 - reconstruct an untrusted revalidation result through
        normal Pydantic validation; a forged/malformed value fails closed."""
        return self._reconstruct(raw, SourceRevalidationV1, SourceRevalidationFailedError)

    def _reconstruct(self, value, model_cls, error_cls):
        try:
            primitive = (
                value.model_dump(mode="python", warnings=False)
                if isinstance(value, model_cls)
                else value
            )
            return model_cls.model_validate(primitive)
        except ApplicationMemoryError:
            raise
        except Exception:
            raise error_cls("value failed validation") from None

    def _build_entry(
        self,
        request: AdmissionRequestV1,
        *,
        owner_id: str,
        shift_id: UUID,
        authorization_scope_digest: str,
        now: datetime,
        predecessor_id: UUID | None,
    ) -> MemoryEntryV1:
        normalized = normalize_content(request.content)
        expires_at_utc = compute_expiry(
            created_at_utc=now, layer=request.layer, requested_ttl_seconds=request.requested_ttl_seconds
        )
        fields = dict(
            entry_id=uuid4(), layer=request.layer, purpose=request.purpose,
            owner_id=owner_id, shift_id=shift_id,
            authorization_scope_digest_sha256=authorization_scope_digest,
            classification=request.classification, source=request.source,
            content=normalized, content_digest_sha256=content_digest(normalized),
            created_at_utc=now, expires_at_utc=expires_at_utc, policy_version="1.0",
            predecessor_id=predecessor_id,
        )
        dump = MemoryEntryV1.model_construct(**fields, entry_digest_sha256="0" * 64).model_dump(mode="python")
        dump.pop("entry_digest_sha256")
        fields["entry_digest_sha256"] = entry_digest(dump)
        return MemoryEntryV1(**fields)


__all__ = ["ApplicationMemory", "MemoryOutcome"]
