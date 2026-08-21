"""Strict application-memory shared contracts (SPEC R1/R2/R3/R4/R5).

Every model here rejects unknown fields, is frozen, and reuses
``retrieval_contracts.common.StrictModel`` (extra="forbid", strict=True,
frozen=True, NFC-only strings) so canonical hashing stays byte-deterministic.
Closed enums bound every discriminated field so an unsupported/ambiguous shape
fails closed at construction rather than silently coercing. This module
performs no I/O, no clock/id creation and no provider access - every
timestamp/digest/id is supplied by the caller.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, SafeId, StrictModel, utc_datetime

from .hashing import content_digest, entry_digest

# SPEC R2 - content bounds (codepoints and UTF-8 bytes).
MAX_CONTENT_CODEPOINTS = 4096
MAX_CONTENT_UTF8_BYTES = 8192


# ---------------------------------------------------------------------------
# Closed enums (SPEC R3/R4)
# ---------------------------------------------------------------------------


class MemoryLayer(StrEnum):
    """The exact two session/working layers."""

    SESSION = "SESSION"
    WORKING = "WORKING"


# SPEC R3 - layer TTL ceilings. Authoritative here so the entry invariant can
# enforce them without a models<->policy import cycle.
SESSION_MAX_TTL_SECONDS = 8 * 3600
WORKING_MAX_TTL_SECONDS = 24 * 3600
LAYER_MAX_TTL_SECONDS: dict[MemoryLayer, int] = {
    MemoryLayer.SESSION: SESSION_MAX_TTL_SECONDS,
    MemoryLayer.WORKING: WORKING_MAX_TTL_SECONDS,
}


class MemoryPurpose(StrEnum):
    """The exact closed purpose set (SPEC R4)."""

    ACTIVE_TASK_CONTEXT = "ACTIVE_TASK_CONTEXT"
    HANDOVER_CONTEXT = "HANDOVER_CONTEXT"
    OPERATOR_WORKING_NOTE = "OPERATOR_WORKING_NOTE"


class MemoryClassification(StrEnum):
    """PUBLIC|INTERNAL only; RESTRICTED and unknown strings fail closed."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"


class SourceType(StrEnum):
    """Closed source-type vocabulary for advisory source references."""

    OPERATIONAL_EVENT = "OPERATIONAL_EVENT"
    TASK = "TASK"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    INCIDENT = "INCIDENT"
    HANDOVER = "HANDOVER"
    REPORT = "REPORT"
    MESSAGE = "MESSAGE"
    PROJECT_KNOWLEDGE = "PROJECT_KNOWLEDGE"


class SourceRevalidationOutcome(StrEnum):
    """The closed revalidator result. Only VALID is positive."""

    VALID = "VALID"
    STALE = "STALE"
    NOT_FOUND = "NOT_FOUND"
    INVALID = "INVALID"


class TombstoneReason(StrEnum):
    """Why an entry left the active set (correction vs delete)."""

    CORRECTED = "CORRECTED"
    DELETED = "DELETED"


class MemoryOperation(StrEnum):
    ADMIT = "ADMIT"
    READ = "READ"
    CORRECT = "CORRECT"
    DELETE = "DELETE"


class MemoryFinalOutcome(StrEnum):
    """The closed terminal outcomes emitted into receipts."""

    ADMITTED = "ADMITTED"
    READ_COMPLETE = "READ_COMPLETE"
    CORRECTED = "CORRECTED"
    DELETED = "DELETED"
    REQUEST_INVALID = "REQUEST_INVALID"
    UNSUPPORTED_PURPOSE = "UNSUPPORTED_PURPOSE"
    CLASSIFICATION_REJECTED = "CLASSIFICATION_REJECTED"
    AUTHORIZATION_SCOPE_MISMATCH = "AUTHORIZATION_SCOPE_MISMATCH"
    SOURCE_REVALIDATION_FAILED = "SOURCE_REVALIDATION_FAILED"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    ENTRY_NOT_FOUND = "ENTRY_NOT_FOUND"
    ENTRY_NOT_ACTIVE = "ENTRY_NOT_ACTIVE"
    ENTRY_EXPIRED = "ENTRY_EXPIRED"
    CORRECTION_LINEAGE_INVALID = "CORRECTION_LINEAGE_INVALID"
    BUDGET_BREACH = "BUDGET_BREACH"
    RESULT_LIMIT_INVALID = "RESULT_LIMIT_INVALID"


# ---------------------------------------------------------------------------
# Source reference and revalidation (SPEC R5)
# ---------------------------------------------------------------------------


class SourceRefV1(StrictModel):
    """The caller-declared source identity: closed type/id/version plus the
    content and provenance digests the revalidator must independently confirm."""

    source_type: SourceType
    source_id: SafeId | None = None
    source_version: SafeId
    source_content_digest_sha256: Digest
    provenance_digest_sha256: Digest


class SourceRevalidationV1(StrictModel):
    """A revalidator result bound to the exact source facts it revalidated.
    ``outcome`` must be VALID and ``source`` must equal the caller's declared
    source before admission proceeds (SPEC R5)."""

    source: SourceRefV1
    outcome: SourceRevalidationOutcome
    checked_at_utc: datetime

    @model_validator(mode="after")
    def _valid_time(self) -> "SourceRevalidationV1":
        utc_datetime(self.checked_at_utc)
        return self


# ---------------------------------------------------------------------------
# Requests (SPEC R2/R4)
# ---------------------------------------------------------------------------


class AdmissionRequestV1(StrictModel):
    """The caller's declared admission/correction intent. Owner/shift/scope
    are deliberately absent - they come from the authenticated application
    boundary, never from the caller (SPEC R5)."""

    layer: MemoryLayer
    purpose: MemoryPurpose
    classification: MemoryClassification
    content: Annotated[str, Field(min_length=1, max_length=MAX_CONTENT_CODEPOINTS)]
    source: SourceRefV1
    requested_ttl_seconds: Annotated[int, Field(ge=1, strict=True)]


# ---------------------------------------------------------------------------
# Immutable entry and tombstone (SPEC R2/R7)
# ---------------------------------------------------------------------------


class MemoryEntryV1(StrictModel):
    """SPEC R2 - the immutable append-only entry. Contains only safe
    identity/scope/source/lifecycle fields plus bounded normalized advisory
    content. ``entry_digest_sha256`` is self-validated here so a forged hash
    (or a ``model_construct`` bypass) is rejected rather than trusted."""

    entry_id: UUID
    layer: MemoryLayer
    purpose: MemoryPurpose
    owner_id: SafeId
    shift_id: UUID
    authorization_scope_digest_sha256: Digest
    classification: MemoryClassification
    source: SourceRefV1
    content: Annotated[str, Field(min_length=1, max_length=MAX_CONTENT_CODEPOINTS)]
    content_digest_sha256: Digest
    created_at_utc: datetime
    expires_at_utc: datetime
    policy_version: str = Field(default="1.0", pattern=r"^1\.0$")
    predecessor_id: UUID | None = None
    entry_digest_sha256: Digest

    @model_validator(mode="after")
    def _validate_invariants(self) -> "MemoryEntryV1":
        utc_datetime(self.created_at_utc)
        utc_datetime(self.expires_at_utc)
        if self.expires_at_utc <= self.created_at_utc:
            raise ValueError("expires_at_utc must be strictly after created_at_utc")
        ttl_seconds = (self.expires_at_utc - self.created_at_utc).total_seconds()
        if ttl_seconds > LAYER_MAX_TTL_SECONDS[self.layer]:
            raise ValueError(f"TTL exceeds the {self.layer.value} ceiling")
        if len(self.content.encode("utf-8")) > MAX_CONTENT_UTF8_BYTES:
            raise ValueError("content exceeds UTF-8 byte bound")
        if content_digest(self.content) != self.content_digest_sha256:
            raise ValueError("content_digest_sha256 must equal the recomputed content digest")
        if self.predecessor_id is not None and self.predecessor_id == self.entry_id:
            raise ValueError("an entry may not be its own predecessor")
        dump = self.model_dump(mode="python")
        dump.pop("entry_digest_sha256")
        if entry_digest(dump) != self.entry_digest_sha256:
            raise ValueError("entry_digest_sha256 must equal the recomputed canonical entry digest")
        return self


class TombstoneV1(StrictModel):
    """SPEC R7 - an immutable tombstone event. Appended once per entry; never
    erases the entry itself (audit lineage is preserved)."""

    entry_id: UUID
    reason: TombstoneReason
    created_at_utc: datetime

    @model_validator(mode="after")
    def _valid_time(self) -> "TombstoneV1":
        utc_datetime(self.created_at_utc)
        return self


__all__ = [
    "MAX_CONTENT_CODEPOINTS",
    "MAX_CONTENT_UTF8_BYTES",
    "SESSION_MAX_TTL_SECONDS",
    "WORKING_MAX_TTL_SECONDS",
    "LAYER_MAX_TTL_SECONDS",
    "MemoryLayer",
    "MemoryPurpose",
    "MemoryClassification",
    "SourceType",
    "SourceRevalidationOutcome",
    "TombstoneReason",
    "MemoryOperation",
    "MemoryFinalOutcome",
    "SourceRefV1",
    "SourceRevalidationV1",
    "AdmissionRequestV1",
    "MemoryEntryV1",
    "TombstoneV1",
]
