from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class StoredEnvelope:
    envelope_id: str
    channel: str
    endpoint: str
    external_id: str
    payload_digest: str
    key_id: str
    nonce: bytes
    ciphertext: bytes | None
    tag: bytes | None
    aad: bytes
    tombstoned: bool = False


@dataclass(frozen=True)
class QuarantineRecord:
    quarantine_id: str
    envelope_id: str
    reason: str
    original_envelope_id: str | None = None


@dataclass(frozen=True)
class ReservationResult:
    kind: str
    envelope: StoredEnvelope | None
    original_envelope_id: str | None = None
    quarantine: QuarantineRecord | None = None


class EdgeStore(Protocol):
    def consume_rate(self, budget: str, key: str, limit: int) -> tuple[bool, int]: ...
    def reserve(self, envelope: StoredEnvelope) -> ReservationResult: ...
    def quarantine(self, envelope_id: str, reason: str, *, original_envelope_id: str | None = None) -> QuarantineRecord: ...
    def save_proposal(self, proposal: dict[str, Any]) -> None: ...
    def save_outbound(self, receipt: dict[str, Any], prerequisite_digest: str) -> None: ...
    def tombstone(self, envelope_id: str) -> None: ...
    def get_envelope(self, envelope_id: str) -> StoredEnvelope | None: ...
