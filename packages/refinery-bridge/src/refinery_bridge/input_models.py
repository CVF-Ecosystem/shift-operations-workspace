from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import Sensitivity, SourceType

SafeId = Annotated[str, Field(min_length=1, max_length=128)]
SafeLink = Annotated[str, Field(min_length=1, max_length=512)]


def validate_safe_string(value: str) -> str:
    if value != value.strip() or ".." in value.split("/"):
        raise ValueError("unsafe identifier")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("control character")
    if "@" in value.partition("://")[2].partition("/")[0]:
        raise ValueError("URI userinfo forbidden")
    return value


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class FingerprintV1(StrictModel):
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    sha512: Annotated[str, Field(pattern=r"^[0-9a-f]{128}$")]
    byte_length: Annotated[int, Field(ge=0, strict=True)]


class SourceFingerprintV1(FingerprintV1):
    pass


class DedupeContentFingerprintV1(FingerprintV1):
    pass


class CandidateFingerprintV1(FingerprintV1):
    pass


class RefineryEnvelopeV1(StrictModel):
    schema_version: Annotated[str, Field(pattern=r"^1\.0$")]
    source_id: SafeId
    source_version: SafeId
    source_link: SafeLink
    source_type: SourceType
    raw_text: Annotated[str, Field(min_length=1, max_length=65536)]
    received_at: datetime
    declared_sensitivity: Sensitivity
    source_owner_id: SafeId
    source_fingerprint: SourceFingerprintV1

    @field_validator("source_id", "source_version", "source_link", "source_owner_id")
    @classmethod
    def safe_strings(cls, value: str) -> str:
        return validate_safe_string(value)

    @field_validator("raw_text")
    @classmethod
    def encodable_text(cls, value: str) -> str:
        value.encode("utf-8", errors="strict")
        return value

    @field_validator("received_at")
    @classmethod
    def utc_only(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
            raise ValueError("UTC datetime required")
        return value


class DedupeRecordV1(StrictModel):
    scope_id: SafeId
    prior_source_id: SafeId
    observed_at: datetime
    source_fingerprint: SourceFingerprintV1
    dedupe_content_fingerprint: DedupeContentFingerprintV1 | None = None

    @field_validator("scope_id", "prior_source_id")
    @classmethod
    def safe_ids(cls, value: str) -> str:
        return validate_safe_string(value)

    @field_validator("observed_at")
    @classmethod
    def utc_only(cls, value: datetime) -> datetime:
        return RefineryEnvelopeV1.utc_only(value)


class DedupeContextV1(StrictModel):
    scope_id: SafeId
    window_start: datetime
    window_end: datetime
    records: tuple[DedupeRecordV1, ...] = Field(max_length=500)

    @field_validator("scope_id")
    @classmethod
    def safe_scope(cls, value: str) -> str:
        return validate_safe_string(value)

    @field_validator("window_start", "window_end")
    @classmethod
    def utc_only(cls, value: datetime) -> datetime:
        return RefineryEnvelopeV1.utc_only(value)

    @model_validator(mode="after")
    def valid_records(self) -> "DedupeContextV1":
        if self.window_start > self.window_end:
            raise ValueError("inverted dedupe window")
        ids: set[str] = set()
        for record in self.records:
            if record.scope_id != self.scope_id:
                raise ValueError("scope mismatch")
            if not self.window_start <= record.observed_at <= self.window_end:
                raise ValueError("record outside inclusive window")
            if record.prior_source_id in ids:
                raise ValueError("duplicate prior source id")
            ids.add(record.prior_source_id)
        return self


class QuarantineRouteV1(StrictModel):
    owner_id: SafeId
    sink_id: SafeId
    policy_version: SafeId
    retention_days: Annotated[int, Field(strict=True)]
    sink_available: bool

    @field_validator("owner_id", "sink_id", "policy_version")
    @classmethod
    def safe_ids(cls, value: str) -> str:
        return validate_safe_string(value)

    @model_validator(mode="after")
    def exact_retention(self) -> "QuarantineRouteV1":
        if self.retention_days != 30:
            raise ValueError("retention must be 30 days")
        return self
