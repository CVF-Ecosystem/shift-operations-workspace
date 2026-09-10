"""Provider-neutral P4-E route-binding and placement contracts (SPEC R13-R16).

`WORKSPACE`, `SHIFT`, `INCIDENT` are the only supported positive target
kinds (SPEC section 1). `FALLBACK` is never a binding target - it is a
system terminal, non-privileged disposition (SPEC R13).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Digest = str
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"

TargetKind = Literal["WORKSPACE", "SHIFT", "INCIDENT"]
BindingStatus = Literal["ACTIVE", "REVOKED"]


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


class RouteBindingV1(ClosedModel):
    """SPEC R13: binds one confirmed mapping id/version to one target
    kind/id/version, creator, lifecycle, version, and successor lineage. At
    most one current binding may exist per current confirmed mapping."""

    binding_id: str = Field(min_length=1)
    mapping_id: str = Field(min_length=1)
    mapping_version: int = Field(ge=1)
    target_kind: TargetKind
    target_id: str = Field(min_length=1)
    target_version: int = Field(ge=1)
    creator_id: str = Field(min_length=1)
    status: BindingStatus
    version: int = Field(ge=1)
    created_at: datetime
    successor_binding_id: str | None = Field(default=None, min_length=1)

    @field_validator("created_at")
    @classmethod
    def _aware_created_at(cls, value: datetime) -> datetime:
        return _require_aware(value)


class PlacementDecisionReceipt(ClosedModel):
    """Conforms to `P4E-CONVERSATION-PLACEMENT-OUTCOMES` (validated on
    construction against the pinned matrix in ``invariants.py``)."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    outcome: str = Field(min_length=1)
    reason: str | None = None
    decision_id: str | None = Field(default=None, min_length=1)
    proposal_id: str = Field(min_length=1)
    mapping_id: str | None = Field(default=None, min_length=1)
    binding_id: str | None = Field(default=None, min_length=1)
    target_kind: TargetKind | None = None
    target_id: str | None = Field(default=None, min_length=1)
    conversation_key: str | None = Field(default=None, pattern=_DIGEST_PATTERN)
    decision_count: int = Field(ge=0)
    work_complete: bool

    def model_post_init(self, __context: Any) -> None:
        from .invariants import validate_placement_decision

        validate_placement_decision(self.model_dump(exclude_none=True))


def conversation_key(
    *,
    mapping_id: str,
    mapping_version: int,
    binding_id: str,
    binding_version: int,
    target_kind: str,
    target_id: str,
    target_version: int,
    workspace_digest: str,
) -> Digest:
    """SPEC R16: opaque SHA-256 digest over a domain-separated, length-
    prefixed tuple of mapping id/version, binding id/version, target
    kind/id/version, and workspace digest. Revoke, correction, remap, or
    rebind creates a new key (any input change changes the digest)."""
    import hashlib

    def _text(value: str) -> bytes:
        return value.encode("utf-8")

    def _framed(*fields: bytes) -> bytes:
        framed = bytearray(b"P4E-CONVERSATION-KEY\x00")
        for field in fields:
            framed.extend(len(field).to_bytes(8, "big"))
            framed.extend(field)
        return bytes(framed)

    preimage = _framed(
        _text(mapping_id),
        _text(str(mapping_version)),
        _text(binding_id),
        _text(str(binding_version)),
        _text(target_kind),
        _text(target_id),
        _text(str(target_version)),
        _text(workspace_digest),
    )
    return hashlib.sha256(preimage).hexdigest()
