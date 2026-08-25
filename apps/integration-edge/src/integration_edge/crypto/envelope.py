"""AES-256-GCM envelope encryption with injected key and nonce authority."""

from __future__ import annotations

import hashlib
import hmac
import os
import threading
from collections.abc import Callable, Mapping

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel, ConfigDict, Field

from ..errors import EncryptionRefused, KeyUnavailable


class KeyRegistry:
    """Small in-process key authority; deployable registries implement this API."""

    def __init__(self, keys: Mapping[str, bytes], *, active_key_id: str) -> None:
        self._keys = dict(keys)
        self._active_key_id = active_key_id
        self._nonces: set[tuple[str, bytes]] = set()
        self._lock = threading.Lock()
        for key_id, key in self._keys.items():
            if not key_id or not isinstance(key, bytes) or len(key) != 32:
                raise ValueError("every envelope key must be identified AES-256 material")
        if active_key_id not in self._keys:
            raise ValueError("active envelope key is unavailable")

    def active_key(self) -> tuple[str, bytes]:
        try:
            return self._active_key_id, self._keys[self._active_key_id]
        except KeyError as exc:
            raise KeyUnavailable("active envelope key is unavailable") from exc

    def get_key(self, key_id: str) -> bytes:
        try:
            return self._keys[key_id]
        except KeyError as exc:
            raise KeyUnavailable("envelope key is unavailable") from exc

    def reserve_nonce(self, key_id: str, nonce: bytes) -> bool:
        identity = (key_id, bytes(nonce))
        with self._lock:
            if identity in self._nonces:
                return False
            self._nonces.add(identity)
            return True


class InMemoryKeyRegistry(KeyRegistry):
    """Explicit name for tests and local composition."""


class EncryptedEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(default="1", pattern=r"^1$")
    key_id: str = Field(min_length=1)
    nonce: bytes = Field(min_length=12, max_length=12)
    ciphertext: bytes
    tag: bytes = Field(min_length=16, max_length=16)
    aad_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    plaintext_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def encrypt_envelope(
    plaintext: bytes,
    *,
    aad: bytes,
    key_registry: KeyRegistry,
    nonce_factory: Callable[[int], bytes] = os.urandom,
    nonce: bytes | None = None,
) -> EncryptedEnvelope:
    if not isinstance(plaintext, bytes) or not isinstance(aad, bytes):
        raise EncryptionRefused("plaintext and AAD must be exact bytes")
    try:
        key_id, key = key_registry.active_key()
        selected_nonce = nonce if nonce is not None else nonce_factory(12)
    except Exception as exc:
        if isinstance(exc, KeyUnavailable):
            raise
        raise EncryptionRefused("key or nonce authority failed") from exc
    if not isinstance(selected_nonce, bytes) or len(selected_nonce) != 12:
        raise EncryptionRefused("AES-GCM nonce must be exactly 96 bits")
    if not key_registry.reserve_nonce(key_id, selected_nonce):
        raise EncryptionRefused("AES-GCM nonce reuse refused")
    try:
        combined = AESGCM(key).encrypt(selected_nonce, plaintext, aad)
    except Exception as exc:
        raise EncryptionRefused("envelope encryption failed") from exc
    return EncryptedEnvelope(
        key_id=key_id,
        nonce=selected_nonce,
        ciphertext=combined[:-16],
        tag=combined[-16:],
        aad_sha256=hashlib.sha256(aad).hexdigest(),
        plaintext_sha256=hashlib.sha256(plaintext).hexdigest(),
    )


def decrypt_envelope(
    envelope: EncryptedEnvelope,
    *,
    aad: bytes,
    key_registry: KeyRegistry,
) -> bytes:
    if not isinstance(aad, bytes):
        raise EncryptionRefused("AAD must be exact bytes")
    if not hmac.compare_digest(envelope.aad_sha256, hashlib.sha256(aad).hexdigest()):
        raise EncryptionRefused("envelope AAD mismatch")
    key = key_registry.get_key(envelope.key_id)
    try:
        plaintext = AESGCM(key).decrypt(
            envelope.nonce, envelope.ciphertext + envelope.tag, aad
        )
    except Exception as exc:
        raise EncryptionRefused("envelope authentication failed") from exc
    if not hmac.compare_digest(
        envelope.plaintext_sha256, hashlib.sha256(plaintext).hexdigest()
    ):
        raise EncryptionRefused("envelope plaintext digest mismatch")
    return plaintext
