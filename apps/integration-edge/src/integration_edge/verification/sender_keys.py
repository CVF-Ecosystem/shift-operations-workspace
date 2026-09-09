"""Sole owner of sender-token key activation, dual-read, and retirement
(Work Order Secret-Authority Ownership; SPEC R2/R19).

``SenderTokenKeyAuthority`` is the only runtime owner of key rotation and
sanitized retirement readiness. It defines ``TokenKeyRetirementReadinessV1``
and ``retire_previous``. Failure to erase or purge fails the rotation closed
and blocks retirement; it is never a mapping-action or Workspace management
API receipt (identity-mapping and conversation-routing must not import this
module).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

DUAL_READ_WINDOW = timedelta(hours=24)


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


class TokenKeyRetirementReadinessV1(BaseModel):
    """Sanitized retirement readiness/audit record. Only non-secret key
    id/version, attempted-at, closed reason, and an opaque correlation id -
    never a secret, raw sender value, or mapping-action/placement field."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: Literal["RETIRED", "TOKEN_KEY_RETIREMENT_BLOCKED"]
    key_id: str = Field(min_length=1)
    key_version: str = Field(min_length=1)
    attempted_at: datetime
    reason: str | None = None
    correlation_id: str = Field(min_length=1)

    @field_validator("attempted_at")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        return _require_aware(value)


class SecretStorePort(Protocol):
    """Injected port for wrapping-key reference and secret-material
    deletion; deterministic BUILD uses a disposable in-memory
    implementation, never a real secret store or credential."""

    def delete_wrapping_key(self, key_id: str, key_version: str) -> bool: ...

    def purge_cache(self, key_id: str, key_version: str) -> bool: ...


class SenderTokenKeyAuthority:
    """SPEC R19: accepts only the current key version and the immediately
    previous version for a 24-hour dual-read window measured from the
    persisted UTC activation time. A new token-key version derives a
    distinct key and never aliases an old mapping."""

    def __init__(self, secret_store: SecretStorePort, *, clock=lambda: datetime.now(timezone.utc)) -> None:
        self._secret_store = secret_store
        self._clock = clock
        self._keys: dict[tuple[str, str], bytes] = {}
        self._activated_at: dict[tuple[str, str], datetime] = {}
        self._active: tuple[str, str] | None = None
        self._previous: tuple[str, str] | None = None

    def activate(self, key_id: str, key_version: str, secret: bytes) -> None:
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("sender token key must contain at least 256 bits")
        self._previous = self._active
        self._active = (key_id, key_version)
        self._keys[(key_id, key_version)] = secret
        self._activated_at[(key_id, key_version)] = self._clock()

    def active_key(self) -> tuple[str, str, bytes]:
        if self._active is None:
            raise ValueError("no sender token key is active")
        key_id, key_version = self._active
        return key_id, key_version, self._keys[(key_id, key_version)]

    def resolve_key(self, key_id: str, key_version: str) -> bytes | None:
        target = (key_id, key_version)
        if target == self._active:
            return self._keys.get(target)
        if target == self._previous:
            activated_at = self._activated_at.get(target)
            if activated_at is None:
                return None
            if self._clock() - activated_at > DUAL_READ_WINDOW:
                return None
            return self._keys.get(target)
        return None

    def retire_previous(self) -> TokenKeyRetirementReadinessV1:
        """Cryptographically erases the previous secret by deleting its
        wrapping-key reference and secret material, then purging process
        caches; only this non-secret readiness record remains. Failure to
        erase or purge fails the rotation closed and blocks retirement."""
        now = self._clock()
        if self._previous is None:
            return TokenKeyRetirementReadinessV1(
                outcome="TOKEN_KEY_RETIREMENT_BLOCKED", key_id="NONE", key_version="NONE",
                attempted_at=now, reason="NO_PREVIOUS_KEY", correlation_id=str(uuid4()),
            )
        key_id, key_version = self._previous
        activated_at = self._activated_at.get(self._previous)
        if activated_at is not None and now - activated_at <= DUAL_READ_WINDOW:
            return TokenKeyRetirementReadinessV1(
                outcome="TOKEN_KEY_RETIREMENT_BLOCKED", key_id=key_id, key_version=key_version,
                attempted_at=now, reason="DUAL_READ_WINDOW_ACTIVE", correlation_id=str(uuid4()),
            )
        erased = self._secret_store.delete_wrapping_key(key_id, key_version)
        purged = self._secret_store.purge_cache(key_id, key_version)
        if not erased or not purged:
            return TokenKeyRetirementReadinessV1(
                outcome="TOKEN_KEY_RETIREMENT_BLOCKED", key_id=key_id, key_version=key_version,
                attempted_at=now, reason="SECRET_ERASURE_FAILED", correlation_id=str(uuid4()),
            )
        self._keys.pop(self._previous, None)
        self._activated_at.pop(self._previous, None)
        self._previous = None
        return TokenKeyRetirementReadinessV1(
            outcome="RETIRED", key_id=key_id, key_version=key_version,
            attempted_at=now, correlation_id=str(uuid4()),
        )
