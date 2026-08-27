"""Closed, provider-neutral P4-D delivery contracts."""

from __future__ import annotations

import json
import hashlib
import ipaddress
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AdapterMode = Literal["DEPLOYABLE", "CONFORMANCE_ONLY"]
Digest = str


class _ClosedFrozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class AdapterDeliveryRequestV1(_ClosedFrozen):
    version: Literal["1"]
    command_id: str = Field(min_length=1, max_length=256)
    idempotency_key: str = Field(min_length=1, max_length=256)
    correlation_id: str = Field(min_length=1, max_length=256)
    workspace_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    record_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    action_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    content_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    recipient_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    channel_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    record_version: int = Field(ge=1)
    policy_version: str = Field(min_length=1, max_length=128)
    prerequisite_receipt_refs: tuple[str, ...] = Field(min_length=1)

    @field_validator("prerequisite_receipt_refs")
    @classmethod
    def normalize_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item or len(item) > 256 for item in value) or len(set(value)) != len(value):
            raise ValueError("prerequisite receipt references must be bounded, non-empty and unique")
        return tuple(sorted(value))

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


class AdapterDeliveryResultV1(_ClosedFrozen):
    status: str = Field(min_length=1)
    transport_attempted: bool
    reason: str | None = None
    delivery_id: str | None = None

    @model_validator(mode="after")
    def conform_to_matrix(self) -> "AdapterDeliveryResultV1":
        from .invariants import validate_adapter_result

        if (
            ("reason" in self.model_fields_set and self.reason is None)
            or ("delivery_id" in self.model_fields_set and self.delivery_id is None)
        ):
            raise ValueError("adapter result fields may not be explicit null")
        validate_adapter_result(self.model_dump(exclude_none=True))
        return self


class AuthorizedEndpointV1(_ClosedFrozen):
    hostname: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)
    path: str = Field(pattern=r"^/", max_length=2048)
    audience: str = Field(min_length=1)
    audience_digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    approved_ips: tuple[str, ...] = Field(min_length=1)

    @field_validator("approved_ips")
    @classmethod
    def unique_ips(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        try:
            parsed = tuple(ipaddress.ip_address(item) for item in value)
        except ValueError as exc:
            raise ValueError("approved IP addresses must be valid") from exc
        if any(not item.is_global for item in parsed):
            raise ValueError("approved IP addresses must be globally routable")
        normalized = tuple(
            str(item) for item in sorted(set(parsed), key=lambda item: (item.version, int(item)))
        )
        if value != normalized:
            raise ValueError("approved IP addresses must be unique and canonically ordered")
        return value

    @model_validator(mode="after")
    def consistent_audience(self) -> "AuthorizedEndpointV1":
        expected = f"https://{self.hostname}:{self.port}{self.path}"
        digest = hashlib.sha256(expected.encode("ascii")).hexdigest()
        if self.audience != expected or self.audience_digest != digest:
            raise ValueError("authorized endpoint audience is inconsistent")
        return self
