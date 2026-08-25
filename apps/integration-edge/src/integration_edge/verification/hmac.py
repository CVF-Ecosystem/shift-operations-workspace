"""Versioned inbound HMAC over exact metadata and body bytes."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone


def _text(value: str) -> bytes:
    return value.encode("utf-8")


def _timestamp_text(value: str | datetime) -> str:
    if isinstance(value, str):
        if not value:
            raise ValueError("timestamp is required")
        return value
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def canonical_hmac_preimage(
    *,
    signature_version: str,
    endpoint_id: str,
    channel_id: str,
    external_message_id: str,
    timestamp: str | datetime,
    body: bytes,
) -> bytes:
    if not isinstance(body, bytes):
        raise TypeError("body must be exact bytes")
    values = (
        signature_version,
        endpoint_id,
        channel_id,
        external_message_id,
        _timestamp_text(timestamp),
    )
    if any(not value for value in values):
        raise ValueError("all HMAC binding fields are required")
    framed = bytearray(b"P4C-HMAC\x00")
    for value in values:
        encoded = _text(value)
        framed.extend(len(encoded).to_bytes(4, "big"))
        framed.extend(encoded)
    framed.extend(len(body).to_bytes(8, "big"))
    framed.extend(body)
    return bytes(framed)


def _secret_bytes(secret: str | bytes) -> bytes:
    value = secret.encode("utf-8") if isinstance(secret, str) else secret
    if not isinstance(value, bytes) or len(value) < 32:
        raise ValueError("HMAC secret must contain at least 256 bits")
    if value.lower() in {b"change-me", b"changeme", b"placeholder"}:
        raise ValueError("placeholder HMAC secret is forbidden")
    return value


def sign_hmac(
    body: bytes,
    secret: str | bytes,
    *,
    signature_version: str = "v1",
    endpoint_id: str,
    channel_id: str,
    external_message_id: str,
    timestamp: str | datetime,
) -> str:
    preimage = canonical_hmac_preimage(
        signature_version=signature_version,
        endpoint_id=endpoint_id,
        channel_id=channel_id,
        external_message_id=external_message_id,
        timestamp=timestamp,
        body=body,
    )
    return hmac.new(_secret_bytes(secret), preimage, hashlib.sha256).hexdigest()


def verify_hmac(
    body: bytes,
    supplied_signature: str,
    secret: str | bytes,
    *,
    signature_version: str = "v1",
    endpoint_id: str,
    channel_id: str,
    external_message_id: str,
    timestamp: str | datetime,
) -> bool:
    try:
        expected = sign_hmac(
            body,
            secret,
            signature_version=signature_version,
            endpoint_id=endpoint_id,
            channel_id=channel_id,
            external_message_id=external_message_id,
            timestamp=timestamp,
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(expected, supplied_signature.lower())
