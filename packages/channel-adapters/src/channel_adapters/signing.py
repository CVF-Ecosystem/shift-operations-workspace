"""Canonical HMAC v1 construction for the generic webhook sender."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Mapping

from channel_sdk import AdapterDeliveryRequestV1, AuthorizedEndpointV1


def utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return an aware datetime")
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def signing_preimage(
    *,
    endpoint: AuthorizedEndpointV1,
    body_sha256: str,
    idempotency_key: str,
    key_id: str,
    timestamp: str,
) -> bytes:
    value = {
        "audience": endpoint.audience,
        "body_sha256": body_sha256,
        "idempotency_key": idempotency_key,
        "key_id": key_id,
        "method": "POST",
        "timestamp": timestamp,
        "version": "v1",
    }
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def signed_headers(
    *,
    request: AdapterDeliveryRequestV1,
    endpoint: AuthorizedEndpointV1,
    key_id: str,
    key: bytes,
    now: datetime,
) -> Mapping[str, str]:
    body_digest = hashlib.sha256(request.canonical_bytes()).hexdigest()
    timestamp = utc_timestamp(now)
    preimage = signing_preimage(
        endpoint=endpoint,
        body_sha256=body_digest,
        idempotency_key=request.idempotency_key,
        key_id=key_id,
        timestamp=timestamp,
    )
    signature = hmac.new(key, preimage, hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-CVF-Signature-Version": "v1",
        "X-CVF-Key-Id": key_id,
        "X-CVF-Timestamp": timestamp,
        "Idempotency-Key": request.idempotency_key,
        "X-CVF-Body-SHA256": body_digest,
        "X-CVF-Audience-SHA256": endpoint.audience_digest,
        "X-CVF-Signature": signature,
    }
