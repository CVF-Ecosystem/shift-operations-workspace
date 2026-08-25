from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Any
from uuid import uuid4

from .protocol import QuarantineRecord, ReservationResult, StoredEnvelope


class InMemoryEdgeStore:
    """Thread-safe evidence store; raw bytes exist only as AEAD ciphertext."""

    def __init__(self, *, quarantine_available: bool = True) -> None:
        self._lock = RLock()
        self.quarantine_available = quarantine_available
        self.envelopes: dict[str, StoredEnvelope] = {}
        self.reservations: dict[tuple[str, str], tuple[str, str]] = {}
        self.quarantines: dict[str, QuarantineRecord] = {}
        self.proposals: dict[str, dict[str, Any]] = {}
        self.outbound: dict[str, dict[str, Any]] = {}
        self.rates: dict[tuple[str, str], int] = {}

    def consume_rate(self, budget: str, key: str, limit: int) -> tuple[bool, int]:
        if limit < 1:
            return False, 0
        with self._lock:
            token = (budget, key)
            count = self.rates.get(token, 0)
            if count >= limit:
                return False, count
            count += 1
            self.rates[token] = count
            return True, count

    def reserve(self, envelope: StoredEnvelope) -> ReservationResult:
        with self._lock:
            if any(e.key_id == envelope.key_id and e.nonce == envelope.nonce for e in self.envelopes.values()):
                raise ValueError("AEAD nonce already used for key")
            key = (envelope.channel, envelope.external_id)
            prior = self.reservations.get(key)
            if prior and prior[0] == envelope.payload_digest:
                return ReservationResult("DUPLICATE", self.envelopes[prior[1]], prior[1])
            self.envelopes[envelope.envelope_id] = envelope
            if prior:
                quarantine = self.quarantine(
                    envelope.envelope_id, "KEY_COLLISION", original_envelope_id=prior[1]
                )
                return ReservationResult("COLLISION", envelope, prior[1], quarantine)
            self.reservations[key] = (envelope.payload_digest, envelope.envelope_id)
            return ReservationResult("NEW", envelope)

    def quarantine(self, envelope_id: str, reason: str, *, original_envelope_id: str | None = None) -> QuarantineRecord:
        if not self.quarantine_available:
            raise RuntimeError("quarantine sink unavailable")
        with self._lock:
            record = QuarantineRecord(str(uuid4()), envelope_id, reason, original_envelope_id)
            self.quarantines[record.quarantine_id] = record
            return record

    def save_proposal(self, proposal: dict[str, Any]) -> None:
        with self._lock:
            self.proposals[str(proposal["proposal_id"])] = dict(proposal)

    def save_outbound(self, receipt: dict[str, Any], prerequisite_digest: str) -> None:
        with self._lock:
            command_id = str(receipt["command_id"])
            if command_id in self.outbound:
                raise ValueError("outbound command already terminal")
            self.outbound[command_id] = {**receipt, "prerequisite_digest": prerequisite_digest}

    def tombstone(self, envelope_id: str) -> None:
        with self._lock:
            current = self.envelopes[envelope_id]
            self.envelopes[envelope_id] = replace(
                current, ciphertext=None, tag=None, tombstoned=True
            )

    def get_envelope(self, envelope_id: str) -> StoredEnvelope | None:
        return self.envelopes.get(envelope_id)
