"""Canonical signing and fail-closed verification of ServiceAssertionV1."""

from __future__ import annotations

import hashlib
import hmac
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from channel_sdk import ServiceAssertionV1

from ..errors import KeyUnavailable, ReplayRefused, VerificationRefused


@dataclass(frozen=True)
class ServiceAssertionKey:
    secret: bytes
    not_before: datetime
    not_after: datetime
    issuer: str
    subject: str

    def __post_init__(self) -> None:
        if len(self.secret) < 32:
            raise ValueError("service assertion secret must contain at least 256 bits")
        if self.not_before.tzinfo is None or self.not_after.tzinfo is None:
            raise ValueError("service assertion key windows must be timezone-aware")
        if self.not_after <= self.not_before:
            raise ValueError("invalid service assertion key window")


class ServiceKeyRegistry:
    def __init__(self, keys: Mapping[str, ServiceAssertionKey]) -> None:
        self._keys = dict(keys)

    def get_key(self, key_id: str) -> ServiceAssertionKey:
        try:
            return self._keys[key_id]
        except KeyError as exc:
            raise KeyUnavailable("service assertion key is unavailable") from exc


class InMemoryNonceStore:
    """Atomic nonce consume store; unavailable storage must not be substituted."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str, str], datetime] = {}
        self._lock = threading.Lock()

    def consume(
        self, *, key_id: str, issuer: str, nonce: str, expires_at: datetime
    ) -> bool:
        now = datetime.now(timezone.utc)
        identity = (key_id, issuer, nonce)
        with self._lock:
            self._entries = {key: expiry for key, expiry in self._entries.items() if expiry > now}
            if identity in self._entries:
                return False
            self._entries[identity] = expires_at
            return True


def _secret_bytes(secret: str | bytes) -> bytes:
    value = secret.encode("utf-8") if isinstance(secret, str) else secret
    if not isinstance(value, bytes) or len(value) < 32:
        raise ValueError("service assertion secret must contain at least 256 bits")
    return value


def sign_service_assertion(
    assertion: ServiceAssertionV1, secret: str | bytes
) -> ServiceAssertionV1:
    signature = hmac.new(
        _secret_bytes(secret), assertion.canonical_bytes(), hashlib.sha256
    ).hexdigest()
    return assertion.model_copy(update={"signature": signature})


def verify_service_assertion(
    assertion: ServiceAssertionV1,
    *,
    key_registry: ServiceKeyRegistry,
    nonce_store: InMemoryNonceStore,
    expected_audience: str,
    expected_operation: str,
    expected_method: str,
    expected_path: str,
    body: bytes,
    expected_idempotency_key: str | None = None,
    now: datetime | None = None,
    clock_skew_seconds: int = 5,
) -> ServiceAssertionV1:
    if key_registry is None or nonce_store is None:
        raise VerificationRefused("service assertion infrastructure unavailable")
    if not isinstance(body, bytes):
        raise VerificationRefused("service assertion body must be exact bytes")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    key = key_registry.get_key(assertion.key_id)
    if assertion.issuer != key.issuer or assertion.subject != key.subject:
        raise VerificationRefused("service identity refused")
    if not (key.not_before <= assertion.issued_at <= key.not_after):
        raise VerificationRefused("service assertion key inactive")
    if current > key.not_after:
        raise VerificationRefused("service assertion key expired")
    if assertion.audience != expected_audience or assertion.operation != expected_operation:
        raise VerificationRefused("service assertion audience or operation mismatch")
    if assertion.method != expected_method.upper() or assertion.path != expected_path:
        raise VerificationRefused("service assertion method or path mismatch")
    if expected_idempotency_key is not None and not hmac.compare_digest(
        assertion.idempotency_key, expected_idempotency_key
    ):
        raise VerificationRefused("service assertion idempotency mismatch")
    if not hmac.compare_digest(assertion.body_sha256, hashlib.sha256(body).hexdigest()):
        raise VerificationRefused("service assertion body mismatch")
    skew = timedelta(seconds=clock_skew_seconds)
    if assertion.issued_at > current + skew or assertion.expires_at < current - skew:
        raise VerificationRefused("service assertion outside its clock window")
    expected = hmac.new(key.secret, assertion.canonical_bytes(), hashlib.sha256).hexdigest()
    if not assertion.signature or not hmac.compare_digest(expected, assertion.signature):
        raise VerificationRefused("service assertion signature invalid")
    if not nonce_store.consume(
        key_id=assertion.key_id,
        issuer=assertion.issuer,
        nonce=assertion.nonce,
        expires_at=assertion.expires_at,
    ):
        raise ReplayRefused("service assertion nonce replay refused")
    return assertion
