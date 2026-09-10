"""Provider-neutral P4-E identity contracts (SPEC R3, R4, R6).

These models never assert the real-world identity behind an external sender,
grant permission, or carry raw sender bytes/token key bytes. ``crypto.py``
computes the values placed into ``SenderEvidenceV1``/``ExternalIdentityKeyV1``
below; this module only defines the closed shapes, per SPEC section 2 (the
three invariant matrices remain the sole outcome-shape owners for receipts
and results emitted by ``service.py``, not for these carrier records).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Digest = str
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


class SenderEvidenceV1(ClosedModel):
    """SPEC R3: frozen, closed evidence object. Contains no raw sender,
    principal, assignment, permission, approval, confirmation, or
    conversation field."""

    version: Literal["1"] = "1"
    workspace_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    endpoint_id: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    provider_account_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    subject_kind: str = Field(min_length=1)
    extraction_policy_id: str = Field(min_length=1)
    extraction_policy_version: str = Field(min_length=1)
    verification_scheme: str = Field(min_length=1)
    verification_version: str = Field(min_length=1)
    sender_token: Digest = Field(pattern=_DIGEST_PATTERN)
    token_key_id: str = Field(min_length=1)
    token_key_version: str = Field(min_length=1)
    source_path_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    raw_envelope_id: str = Field(min_length=1)
    external_message_id: str = Field(min_length=1)
    body_sha256: Digest = Field(pattern=_DIGEST_PATTERN)
    received_at: datetime

    @field_validator("received_at")
    @classmethod
    def _aware_received_at(cls, value: datetime) -> datetime:
        return _require_aware(value)


class ExternalIdentityKeyV1(ClosedModel):
    """SPEC R4: the indivisible tuple. A change to any dimension produces a
    new key; no partial-key lookup, cross-workspace lookup, fuzzy match, or
    automatic carry-forward from an older key is permitted."""

    workspace_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    endpoint_id: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    provider_account_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    subject_kind: str = Field(min_length=1)
    extraction_policy_id: str = Field(min_length=1)
    extraction_policy_version: str = Field(min_length=1)
    verification_scheme: str = Field(min_length=1)
    verification_version: str = Field(min_length=1)
    sender_token: Digest = Field(pattern=_DIGEST_PATTERN)
    token_key_id: str = Field(min_length=1)
    token_key_version: str = Field(min_length=1)

    def digest(self) -> Digest:
        """Deterministic SHA-256 over this key's exact dimensions, used as
        the storage lookup identity (SPEC R5/R6)."""
        from .crypto import external_identity_key_digest

        return external_identity_key_digest(self)


class SenderObservationV1(ClosedModel):
    """SPEC R5: at most one immutable observation per complete external
    identity key plus envelope lineage. Management reads may expose only
    ``observation_id``, non-secret selector metadata, and ``received_at`` -
    never ``sender_token``, raw sender, candidate body, or operational
    content (enforced by omission: this shape has no such field)."""

    observation_id: str = Field(min_length=1)
    external_key_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    workspace_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    endpoint_id: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    provider_account_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    subject_kind: str = Field(min_length=1)
    extraction_policy_id: str = Field(min_length=1)
    extraction_policy_version: str = Field(min_length=1)
    raw_envelope_id: str = Field(min_length=1)
    external_message_id: str = Field(min_length=1)
    received_at: datetime

    @field_validator("received_at")
    @classmethod
    def _aware_received_at(cls, value: datetime) -> datetime:
        return _require_aware(value)


MappingStatus = Literal["PROPOSED", "CONFIRMED", "REJECTED", "REVOKED"]

# SPEC R6: PROPOSED -> CONFIRMED | REJECTED; CONFIRMED -> REVOKED. Terminal
# records (REJECTED, REVOKED) are immutable - absent from this map.
_MAPPING_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "PROPOSED": ("CONFIRMED", "REJECTED"),
    "CONFIRMED": ("REVOKED",),
}


def mapping_transition_allowed(current: str, target: str) -> bool:
    return target in _MAPPING_TRANSITIONS.get(current, ())


class IdentityMappingV1(ClosedModel):
    """SPEC R6: frozen and closed. A confirmed mapping stores a user
    reference only - never a copy of role, active status, JWT claims,
    permission, or assignment authority (consumers must re-read the user at
    use time; SPEC section 5)."""

    mapping_id: str = Field(min_length=1)
    external_key_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    target_kind: Literal["INTERNAL_USER"] = "INTERNAL_USER"
    # completion-review F8: nullable, not a sentinel string - SPEC R19
    # privacy deletion clears the actual user reference to NULL (a real
    # foreign key to users.user_id must never point at a fake row).
    target_user_id: str | None = Field(default=None, min_length=1)
    proposal_evidence_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    proposer_id: str = Field(min_length=1)
    status: MappingStatus
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    confirmer_id: str | None = None
    rejector_id: str | None = None
    revoker_id: str | None = None
    successor_mapping_id: str | None = Field(default=None, min_length=1)
    # SPEC section 4: correction creates a successor proposal referencing
    # the prior mapping; set only on a correction successor, never on an
    # original propose.
    predecessor_mapping_id: str | None = Field(default=None, min_length=1)

    @field_validator("created_at", "updated_at")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return _require_aware(value)


class MappingActionReceipt(ClosedModel):
    """Conforms to `P4E-MAPPING-ACTION-OUTCOMES` (validated on construction
    against the pinned matrix in ``invariants.py``)."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    outcome: str = Field(min_length=1)
    action: str = Field(min_length=1)
    reason: str | None = None
    aggregate_id: str | None = Field(default=None, min_length=1)
    aggregate_version: int | None = None
    audit_id: str | None = Field(default=None, min_length=1)
    command_application_count: int = Field(ge=0)
    audit_count: int = Field(ge=0)
    replayed: bool

    def model_post_init(self, __context: Any) -> None:
        from .invariants import validate_mapping_action_receipt

        validate_mapping_action_receipt(self.model_dump(exclude_none=True))


class IdentityResolutionResult(ClosedModel):
    """Conforms to `P4E-IDENTITY-RESOLUTION-OUTCOMES` (validated on
    construction against the pinned matrix in ``invariants.py``)."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    outcome: str = Field(min_length=1)
    reason: str | None = None
    mapping_id: str | None = Field(default=None, min_length=1)
    mapping_version: int | None = None
    target_user_id: str | None = Field(default=None, min_length=1)
    external_key_digest: str | None = Field(default=None, pattern=_DIGEST_PATTERN)
    resolution_count: int = Field(ge=0)

    def model_post_init(self, __context: Any) -> None:
        from .invariants import validate_identity_resolution_result

        validate_identity_resolution_result(self.model_dump(exclude_none=True))
