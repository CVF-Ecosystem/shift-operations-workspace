"""Sanitized receipt models and builder (SPEC R9).

Builds :class:`MemoryReceiptV1` from safe ids, enums, versions, timestamps,
counts and SHA-256 digests only - never content body, source body, token,
credential or provider output. ``receipt_hash_sha256`` is computed here from
the canonical dump of every OTHER field and independently re-verified by the
model itself, so a forged hash (or a ``model_construct`` bypass) is rejected.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, SafeId, StrictModel, utc_datetime

from .hashing import receipt_hash
from .models import (
    MemoryClassification,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryOperation,
    MemoryPurpose,
    TombstoneReason,
)

NonNegInt = Annotated[int, Field(ge=0, strict=True)]

_POSITIVE_OUTCOMES = {
    MemoryFinalOutcome.ADMITTED,
    MemoryFinalOutcome.READ_COMPLETE,
    MemoryFinalOutcome.CORRECTED,
    MemoryFinalOutcome.DELETED,
}

# P4A3-REV-F4 - the exact closed positive mapping: a positive outcome may only
# appear under its matching operation.
_POSITIVE_OPERATION_OUTCOME = {
    MemoryOperation.ADMIT: MemoryFinalOutcome.ADMITTED,
    MemoryOperation.READ: MemoryFinalOutcome.READ_COMPLETE,
    MemoryOperation.CORRECT: MemoryFinalOutcome.CORRECTED,
    MemoryOperation.DELETE: MemoryFinalOutcome.DELETED,
}


class MemoryReceiptV1(StrictModel):
    """SPEC R9 - the sanitized end-to-end receipt. Only safe ids, enums,
    versions, timestamps, counts and digests - no content/source/query/token/
    credential/provider output. Every digest is recomputed by tests rather
    than trusted from the builder."""

    contract_version: str = Field(default="1.0", pattern=r"^1\.0$")
    operation: MemoryOperation
    final_outcome: MemoryFinalOutcome
    reason_code: str = Field(default="", max_length=64)
    owner_id: SafeId
    shift_id: UUID
    authorization_scope_digest_sha256: Digest
    layer: MemoryLayer | None = None
    purpose: MemoryPurpose | None = None
    classification: MemoryClassification | None = None
    entry_id: UUID | None = None
    entry_digest_sha256: Digest | None = None
    predecessor_entry_id: UUID | None = None
    tombstoned_entry_id: UUID | None = None
    tombstone_reason: TombstoneReason | None = None
    source_content_digest_sha256: Digest | None = None
    provenance_digest_sha256: Digest | None = None
    expires_at_utc: datetime | None = None
    returned_entry_ids: tuple[UUID, ...] = Field(default=())
    returned_entry_digests: tuple[Digest, ...] = Field(default=())
    omitted_count: NonNegInt = 0
    appended_entries: NonNegInt = 0
    appended_tombstones: NonNegInt = 0
    created_at_utc: datetime
    receipt_hash_sha256: Digest

    @model_validator(mode="after")
    def _validate_invariants(self) -> "MemoryReceiptV1":
        utc_datetime(self.created_at_utc)
        if self.expires_at_utc is not None:
            utc_datetime(self.expires_at_utc)
        if len(self.returned_entry_ids) != len(self.returned_entry_digests):
            raise ValueError("returned_entry_ids and returned_entry_digests must have equal length")
        dump = self.model_dump(mode="python")
        dump.pop("receipt_hash_sha256")
        if receipt_hash(dump) != self.receipt_hash_sha256:
            raise ValueError("receipt_hash_sha256 must equal the recomputed canonical receipt hash")
        if self.final_outcome in _POSITIVE_OUTCOMES:
            if self.reason_code:
                raise ValueError("a positive outcome requires an empty reason_code")
            self._validate_positive_grammar()
        else:
            if not self.reason_code:
                raise ValueError("a negative outcome requires a non-empty reason_code")
            if self.appended_entries != 0 or self.appended_tombstones != 0:
                raise ValueError("a negative write must report zero mutations")
            self._validate_negative_payload()
        return self

    def _validate_positive_grammar(self) -> None:
        expected = _POSITIVE_OPERATION_OUTCOME.get(self.operation)
        if expected is None or self.final_outcome is not expected:
            raise ValueError(
                f"operation {self.operation} must map to {expected}, not {self.final_outcome}"
            )
        if self.operation is MemoryOperation.ADMIT:
            self._validate_admitted()
        elif self.operation is MemoryOperation.READ:
            self._validate_read_complete()
        elif self.operation is MemoryOperation.CORRECT:
            self._validate_corrected()
        elif self.operation is MemoryOperation.DELETE:
            self._validate_deleted()

    def _validate_admitted(self) -> None:
        if self.appended_entries != 1 or self.appended_tombstones != 0:
            raise ValueError("ADMITTED requires exactly one appended entry and no tombstone")
        if self.omitted_count != 0:
            raise ValueError("ADMITTED requires omitted_count == 0")
        self._require_entry_and_source_facts()
        self._require_no_lineage()
        self._require_no_read_payload()

    def _validate_read_complete(self) -> None:
        if self.appended_entries != 0 or self.appended_tombstones != 0:
            raise ValueError("READ_COMPLETE must not append entries or tombstones")
        self._require_no_entry_or_source_facts()
        self._require_no_lineage()

    def _validate_corrected(self) -> None:
        if self.appended_entries != 1 or self.appended_tombstones != 1:
            raise ValueError("CORRECTED requires one appended entry and one tombstone")
        if self.omitted_count != 0:
            raise ValueError("CORRECTED requires omitted_count == 0")
        self._require_entry_and_source_facts()
        if self.predecessor_entry_id is None or self.tombstoned_entry_id is None:
            raise ValueError("CORRECTED requires predecessor/tombstoned ids")
        if self.predecessor_entry_id != self.tombstoned_entry_id:
            raise ValueError("CORRECTED requires predecessor_entry_id == tombstoned_entry_id")
        if self.tombstone_reason is not TombstoneReason.CORRECTED:
            raise ValueError("CORRECTED requires a CORRECTED tombstone reason")
        self._require_no_read_payload()

    def _validate_deleted(self) -> None:
        if self.appended_entries != 0 or self.appended_tombstones != 1:
            raise ValueError("DELETED requires exactly one tombstone and no entry")
        if self.omitted_count != 0:
            raise ValueError("DELETED requires omitted_count == 0")
        if self.tombstoned_entry_id is None:
            raise ValueError("DELETED requires tombstoned_entry_id")
        if self.tombstone_reason is not TombstoneReason.DELETED:
            raise ValueError("DELETED requires a DELETED tombstone reason")
        if self.predecessor_entry_id is not None:
            raise ValueError("DELETED must not carry predecessor_entry_id")
        self._require_no_entry_or_source_facts()
        self._require_no_read_payload()

    def _require_entry_and_source_facts(self) -> None:
        if self.layer is None or self.purpose is None or self.classification is None:
            raise ValueError("a positive write requires layer/purpose/classification")
        if self.entry_id is None or self.entry_digest_sha256 is None:
            raise ValueError("a positive write requires entry_id and entry_digest_sha256")
        if self.source_content_digest_sha256 is None or self.provenance_digest_sha256 is None:
            raise ValueError("a positive write requires source/provenance digests")
        if self.expires_at_utc is None:
            raise ValueError("a positive write requires expires_at_utc")

    def _require_no_entry_or_source_facts(self) -> None:
        if self.entry_id is not None or self.entry_digest_sha256 is not None:
            raise ValueError("must not carry entry_id/entry_digest_sha256")
        if self.layer is not None or self.purpose is not None or self.classification is not None:
            raise ValueError("must not carry layer/purpose/classification")
        if self.source_content_digest_sha256 is not None or self.provenance_digest_sha256 is not None:
            raise ValueError("must not carry source/provenance digests")
        if self.expires_at_utc is not None:
            raise ValueError("must not carry expires_at_utc")

    def _require_no_lineage(self) -> None:
        if self.predecessor_entry_id is not None or self.tombstoned_entry_id is not None:
            raise ValueError("must not carry lineage ids")
        if self.tombstone_reason is not None:
            raise ValueError("must not carry a tombstone reason")

    def _require_no_read_payload(self) -> None:
        if self.returned_entry_ids or self.returned_entry_digests:
            raise ValueError("must not carry read payload")

    def _validate_negative_payload(self) -> None:
        positive_fields = (
            ("entry_id", self.entry_id),
            ("entry_digest_sha256", self.entry_digest_sha256),
            ("predecessor_entry_id", self.predecessor_entry_id),
            ("tombstoned_entry_id", self.tombstoned_entry_id),
            ("tombstone_reason", self.tombstone_reason),
            ("layer", self.layer),
            ("purpose", self.purpose),
            ("classification", self.classification),
            ("source_content_digest_sha256", self.source_content_digest_sha256),
            ("provenance_digest_sha256", self.provenance_digest_sha256),
            ("expires_at_utc", self.expires_at_utc),
        )
        for name, value in positive_fields:
            if value is not None:
                raise ValueError(f"a negative outcome must not carry a stale positive {name}")
        if self.returned_entry_ids or self.returned_entry_digests:
            raise ValueError("a negative outcome must not carry read payload")
        if self.omitted_count != 0:
            raise ValueError("a negative outcome must report omitted_count == 0")


def build_receipt(**fields) -> MemoryReceiptV1:
    """Construct the sanitized receipt, recomputing ``receipt_hash_sha256``
    from the canonical dump of every other field (never caller-trusted). The
    model's own ``_validate_invariants`` independently re-verifies this on
    every construction."""
    dump_fields = dict(fields)
    dump_fields["receipt_hash_sha256"] = "0" * 64
    model = MemoryReceiptV1.model_construct(**dump_fields)
    dump = model.model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    final_fields = dict(fields)
    final_fields["receipt_hash_sha256"] = receipt_hash(dump)
    return MemoryReceiptV1(**final_fields)


__all__ = ["MemoryReceiptV1", "build_receipt"]
