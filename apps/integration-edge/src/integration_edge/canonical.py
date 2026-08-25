"""Canonical byte and digest helpers; all functions are deterministic."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping


def canonical_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("canonical timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def envelope_aad(
    *,
    envelope_id: str,
    endpoint_id: str,
    channel_id: str,
    external_message_id: str,
    body_sha256: str,
    received_at: datetime,
) -> bytes:
    return canonical_json_bytes(
        {
            "body_sha256": body_sha256,
            "channel_id": channel_id,
            "endpoint_id": endpoint_id,
            "envelope_id": envelope_id,
            "external_message_id": external_message_id,
            "received_at": canonical_datetime(received_at),
            "version": "1",
        }
    )
