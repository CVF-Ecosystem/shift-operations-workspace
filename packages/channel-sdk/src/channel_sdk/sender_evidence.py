"""Closed, provider-neutral SenderEvidenceV1 carrier plus its normalization/
token-derivation primitives (SPEC R1-R3).

Owned by channel-sdk so both Integration Edge (producer) and identity-mapping
(the SPEC R4 key digest consumer) share one implementation without either
side importing the other's package (SPEC R18: Integration Edge may emit
sender evidence but shall not import identity-mapping or conversation-
routing). Contains no raw sender value, principal, assignment, permission,
approval, confirmation, or conversation field.
"""

from __future__ import annotations

import hmac
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

Digest = str
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_MAX_NORMALIZED_SENDER_BYTES = 512


def normalize_sender_bytes(raw_sender: str) -> bytes:
    """SPEC R1 normalization profile: require valid UTF-8, reject empty
    input and NUL/control characters other than horizontal space, preserve
    case, perform no phone/display-name/fuzzy canonicalization, and cap the
    normalized value at 512 UTF-8 bytes."""
    if not isinstance(raw_sender, str):
        raise ValueError("raw sender value must be a string")
    encoded = raw_sender.encode("utf-8")
    if len(encoded) == 0:
        raise ValueError("raw sender value must not be empty")
    for codepoint in raw_sender:
        if codepoint == "\x00" or (ord(codepoint) < 0x20 and codepoint not in (" ",)):
            raise ValueError("raw sender value contains a forbidden control character")
    if len(encoded) > _MAX_NORMALIZED_SENDER_BYTES:
        raise ValueError("normalized sender value exceeds the 512 UTF-8 byte cap")
    return encoded


def _length_prefixed(*fields: bytes) -> bytes:
    framed = bytearray()
    for field in fields:
        framed.extend(len(field).to_bytes(8, "big"))
        framed.extend(field)
    return bytes(framed)


def canonical_timestamp(value: datetime) -> str:
    """One canonical timestamp text form for every P4-E sender-aware
    preimage - microsecond-precision UTC ISO-8601 with a literal ``Z``."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _text(value: str) -> bytes:
    return value.encode("utf-8")


def sender_aware_signature_preimage(
    *, signature_version: str, workspace_digest: str, endpoint_id: str, channel_id: str,
    provider_account_digest: str, subject_kind: str, extraction_policy_id: str,
    extraction_policy_version: str, verification_scheme: str, verification_version: str,
    external_message_id: str, timestamp: datetime, normalized_sender_bytes: bytes, body_sha256: str,
) -> bytes:
    """SPEC R1: THE single canonical preimage contract for the sender-aware
    ingress signature - length-prefixed UTF-8 fields, in the exact order the
    SPEC declares, using the SAME 8-byte length-prefixed framing
    (``_length_prefixed``) as ``derive_sender_token`` below. There is
    exactly one framing scheme in this codebase for P4-E sender-aware
    bytes; nothing else may define a second one."""
    texts = (
        signature_version, workspace_digest, endpoint_id, channel_id,
        provider_account_digest, subject_kind, extraction_policy_id,
        extraction_policy_version, verification_scheme, verification_version,
        external_message_id, canonical_timestamp(timestamp),
    )
    if any(not value for value in texts):
        raise ValueError("all sender-aware signature fields are required")
    framed = bytearray(b"P4E-SENDER-SIG\x00")
    framed.extend(_length_prefixed(*(_text(v) for v in texts)))
    framed.extend(_length_prefixed(normalized_sender_bytes))
    framed.extend(_length_prefixed(_text(body_sha256)))
    return bytes(framed)


def derive_sender_token(
    *, key_id: str, key_secret: bytes, workspace_digest: str, endpoint_id: str, channel_id: str,
    provider_account_digest: str, subject_kind: str, extraction_policy_id: str,
    extraction_policy_version: str, verification_scheme: str, verification_version: str,
    normalized_sender_bytes: bytes,
) -> str:
    """SPEC R2: HMAC-SHA-256 over a domain-separated, length-prefixed tuple
    of all R1 identity-semantic fields except message id, timestamp, and
    body digest."""
    import hashlib

    if not isinstance(key_secret, bytes) or len(key_secret) < 32:
        raise ValueError("sender token key must contain at least 256 bits")

    preimage = bytearray(b"P4E-SENDER-TOKEN\x00")
    preimage.extend(_length_prefixed(_text(key_id)))
    preimage.extend(_length_prefixed(
        _text(workspace_digest), _text(endpoint_id), _text(channel_id),
        _text(provider_account_digest), _text(subject_kind), _text(extraction_policy_id),
        _text(extraction_policy_version), _text(verification_scheme), _text(verification_version),
        normalized_sender_bytes,
    ))
    return hmac.new(key_secret, bytes(preimage), hashlib.sha256).hexdigest()


class SenderEvidenceV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(default="1", pattern=r"^1$")
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
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("received_at must be timezone-aware")
        return value.astimezone(timezone.utc)
