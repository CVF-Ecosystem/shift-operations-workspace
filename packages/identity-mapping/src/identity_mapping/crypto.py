"""Deterministic byte/digest helpers for P4-E identity (SPEC R1, R2, R4).

Raw sender bytes and token key bytes are accepted here only transiently as
function arguments; nothing in this module persists, logs, or returns them.

``normalize_sender_bytes``/``derive_sender_token`` are owned by channel-sdk
(SPEC R18: shared by Integration Edge and identity-mapping without either
importing the other's package) and re-exported here so existing internal
callers (``service.py``) keep one stable import path.
"""

from __future__ import annotations

import hashlib

from channel_sdk import derive_sender_token, normalize_sender_bytes

__all__ = [
    "canonical_sender_evidence_preimage",
    "derive_sender_token",
    "external_identity_key_digest",
    "normalize_sender_bytes",
    "proposal_evidence_digest",
]


def _length_prefixed(*fields: bytes) -> bytes:
    framed = bytearray()
    for field in fields:
        framed.extend(len(field).to_bytes(8, "big"))
        framed.extend(field)
    return bytes(framed)


def _text(value: str) -> bytes:
    return value.encode("utf-8")


def canonical_sender_evidence_preimage(
    *,
    signature_version: str,
    workspace_digest: str,
    endpoint_id: str,
    channel_id: str,
    provider_account_digest: str,
    subject_kind: str,
    extraction_policy_id: str,
    extraction_policy_version: str,
    verification_scheme: str,
    verification_version: str,
    external_message_id: str,
    timestamp: str,
    normalized_sender_bytes: bytes,
    body_sha256: str,
) -> bytes:
    """SPEC R1: the authenticated preimage for the versioned sender-aware
    ingress signature, length-prefixed UTF-8 fields in this exact order."""
    return _length_prefixed(
        _text(signature_version),
        _text(workspace_digest),
        _text(endpoint_id),
        _text(channel_id),
        _text(provider_account_digest),
        _text(subject_kind),
        _text(extraction_policy_id),
        _text(extraction_policy_version),
        _text(verification_scheme),
        _text(verification_version),
        _text(external_message_id),
        _text(timestamp),
        normalized_sender_bytes,
        _text(body_sha256),
    )


def external_identity_key_digest(key) -> str:
    """SPEC R4: deterministic SHA-256 over the complete, indivisible key
    tuple - the storage lookup identity for a complete external identity
    key. ``key`` is an ``ExternalIdentityKeyV1``."""
    preimage = _length_prefixed(
        _text(key.workspace_digest),
        _text(key.endpoint_id),
        _text(key.channel_id),
        _text(key.provider_account_digest),
        _text(key.subject_kind),
        _text(key.extraction_policy_id),
        _text(key.extraction_policy_version),
        _text(key.verification_scheme),
        _text(key.verification_version),
        _text(key.sender_token),
        _text(key.token_key_id),
        _text(key.token_key_version),
    )
    return hashlib.sha256(preimage).hexdigest()


def proposal_evidence_digest(*, observation_id: str, external_key_digest: str) -> str:
    """SPEC section 4/R8: the mapping proposal command digest binds only the
    observation/key digest and target user (target user is bound by the
    caller into the persisted mapping row, not into this evidence digest,
    which is scoped to the sender-evidence lineage alone)."""
    return hashlib.sha256(
        _length_prefixed(_text(observation_id), _text(external_key_digest))
    ).hexdigest()
