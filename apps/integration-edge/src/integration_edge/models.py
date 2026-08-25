"""Closed P4-C edge contracts. These records never assert operational truth."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Digest = str


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RawEnvelope(ClosedModel):
    version: Literal["1"] = "1"
    envelope_id: str = Field(min_length=1)
    endpoint_id: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    external_message_id: str = Field(min_length=1)
    key_id: str = Field(min_length=1)
    nonce_b64: str = Field(min_length=16)
    ciphertext_b64: str = Field(min_length=1)
    tag_b64: str = Field(min_length=16)
    aad_sha256: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    body_sha256: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    byte_length: int = Field(ge=0)
    received_at: datetime
    retention_class: Literal["EDGE_RAW_30D"] = "EDGE_RAW_30D"

    @field_validator("received_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("received_at must be timezone-aware")
        return value.astimezone(timezone.utc)


class CandidateProposal(ClosedModel):
    version: Literal["1"] = "1"
    proposal_id: str = Field(min_length=1)
    raw_envelope_id: str = Field(min_length=1)
    content_mode: Literal["RAW"] = "RAW"
    trust: Literal["UNTRUSTED_EXTERNAL"] = "UNTRUSTED_EXTERNAL"
    endpoint_id: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    external_message_id: str = Field(min_length=1)
    body_sha256: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    candidate_sha256: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    received_at: datetime
    correlation_id: str = Field(min_length=1)

    @field_validator("received_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("received_at must be timezone-aware")
        return value.astimezone(timezone.utc)


class OutboundCommand(ClosedModel):
    version: Literal["1"] = "1"
    command_id: str = Field(min_length=1)
    workspace_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    record_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    action_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    record_version: int = Field(ge=1)
    content_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    recipient_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    channel_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    prerequisite_receipt_refs: tuple[str, ...] = Field(min_length=1)
    correlation_id: str = Field(min_length=1)

    @field_validator("prerequisite_receipt_refs")
    @classmethod
    def require_unique_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item for item in value) or len(set(value)) != len(value):
            raise ValueError("prerequisite receipt references must be non-empty and unique")
        return value


class IngressReceipt(ClosedModel):
    outcome: str = Field(min_length=1)
    reason: str | None = None
    raw_envelope_id: str | None = Field(default=None, min_length=1)
    quarantine_id: str | None = Field(default=None, min_length=1)
    preauth_count: int = Field(ge=0)
    postauth_count: int = Field(ge=0)
    route_attempts: int = Field(ge=0)

    @model_validator(mode="after")
    def conform_to_matrix(self) -> "IngressReceipt":
        from .invariants import validate_ingress_terminal_receipt

        validate_ingress_terminal_receipt(self.model_dump(exclude_none=True))
        return self


class OutboundReceipt(ClosedModel):
    outcome: str = Field(min_length=1)
    reason: str | None = None
    command_id: str = Field(min_length=1)
    delivery_id: str | None = Field(default=None, min_length=1)
    delivery_attempts: int = Field(ge=0)

    @model_validator(mode="after")
    def conform_to_matrix(self) -> "OutboundReceipt":
        from .invariants import validate_outbound_terminal_receipt

        validate_outbound_terminal_receipt(self.model_dump(exclude_none=True))
        return self
