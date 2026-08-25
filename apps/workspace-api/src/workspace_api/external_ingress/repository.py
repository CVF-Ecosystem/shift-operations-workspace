from __future__ import annotations

from threading import RLock
from typing import Protocol

from .models import ExternalIngressProposal


class ExternalIngressRepository(Protocol):
    def add(self, proposal: ExternalIngressProposal) -> ExternalIngressProposal: ...


class InMemoryExternalIngressRepository:
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
