from __future__ import annotations

from threading import RLock
from typing import Protocol

from .models import ExternalIngressProposal


class ExternalIngressRepository(Protocol):
    def add(self, proposal: ExternalIngressProposal) -> ExternalIngressProposal: ...


class InMemoryExternalIngressRepository:
    """Test/local-only store. SPEC R10: retired from production
    composition - see ``LedgerExternalIngressRepository`` below and
    ``workspace_api.main``'s composition root, which no longer wires this
    class into the live app."""

    def __init__(self) -> None:
        self._lock = RLock()
        self.records: dict[str, ExternalIngressProposal] = {}

    def add(self, proposal: ExternalIngressProposal) -> ExternalIngressProposal:
        with self._lock:
            key = str(proposal.proposal_id)
            if key in self.records:
                raise ValueError("proposal already exists")
            self.records[key] = proposal
            return proposal


class LedgerExternalIngressRepository:
    """SPEC R10/R11/completion-review F3: durable, idempotent Workspace
    external-proposal repository backed by Operations Ledger - the sole
    live proposal store. Transaction A: idempotently persists the
    immutable proposal, the derived sender observation when evidence is
    present, and exactly one pending placement-work item. On exact replay
    (same idempotency key, same complete lineage), returns the ORIGINAL
    persisted admission and its original proposal id - never the caller's
    freshly generated one. Reused key with any changed lineage dimension
    is a closed collision (raised as ``ValueError``, never silently
    accepted)."""

    def __init__(self, ledger, *, idempotency_key_field: str = "envelope_id") -> None:
        self._ledger = ledger
        self._idempotency_key_field = idempotency_key_field

    def add(self, proposal: ExternalIngressProposal) -> ExternalIngressProposal:
        row = {
            "proposal_id": str(proposal.proposal_id),
            "envelope_id": proposal.envelope_id,
            "channel": proposal.channel,
            "external_id": proposal.external_id,
            "candidate": proposal.candidate,
            "provenance_digest": proposal.provenance_digest,
            "sender_evidence": proposal.sender_evidence.model_dump(mode="json") if proposal.sender_evidence else None,
            "idempotency_key": getattr(proposal, self._idempotency_key_field),
        }
        with self._ledger.transaction() as unit:
            stored, _replayed = self._ledger.add_p4e_proposal(row, unit=unit)
        from uuid import UUID as _UUID

        return proposal.model_copy(update={
            "proposal_id": _UUID(stored["proposal_id"]),
            "envelope_id": stored["envelope_id"],
            "channel": stored["channel"],
            "external_id": stored["external_id"],
            "candidate": stored["candidate"],
            "provenance_digest": stored["provenance_digest"],
        })
