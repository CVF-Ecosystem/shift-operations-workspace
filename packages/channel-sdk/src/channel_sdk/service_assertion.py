"""Closed, provider-neutral contract for authenticated service-to-service calls."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _utc_text(value: datetime) -> str:
    value = value.astimezone(timezone.utc)
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


class ServiceAssertionV1(BaseModel):
    """Signed claim set. ``signature`` is excluded from the canonical preimage."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal["1"] = "1"
    key_id: str = Field(min_length=1, max_length=128)
    issuer: str = Field(min_length=1, max_length=128)
    subject: str = Field(min_length=1, max_length=128)
    audience: str = Field(min_length=1, max_length=128)
    operation: Literal["external_ingress.propose", "outbound.deliver"]
    method: str = Field(min_length=1, max_length=16)
    path: str = Field(pattern=r"^/", max_length=512)
    issued_at: datetime
    expires_at: datetime
    nonce: str = Field(min_length=16, max_length=256)
    body_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: str = Field(min_length=1, max_length=256)
    correlation_id: str = Field(min_length=1, max_length=256)
    signature: str = Field(default="", pattern=r"^(?:|[0-9a-f]{64})$")

    @field_validator("issued_at", "expires_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("service assertion timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError("unsupported service assertion method")
        return normalized

    @model_validator(mode="after")
    def validate_lifetime(self) -> "ServiceAssertionV1":
        lifetime = (self.expires_at - self.issued_at).total_seconds()
        if lifetime <= 0 or lifetime > 60:
            raise ValueError("service assertion lifetime must be in (0, 60] seconds")
        return self

    def canonical_bytes(self) -> bytes:
        values = self.model_dump(exclude={"signature"})
        values["issued_at"] = _utc_text(self.issued_at)
        values["expires_at"] = _utc_text(self.expires_at)
        return json.dumps(
            values, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
