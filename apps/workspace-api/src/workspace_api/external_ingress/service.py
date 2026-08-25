from __future__ import annotations

from .models import ExternalIngressProposal, ExternalIngressProposalInput


class ExternalIngressService:
    """Actor-neutral proposal boundary; deliberately has no Ledger dependency."""

    operation = "external_ingress.propose"

    def __init__(self, repository, assertion_verifier) -> None:
        self.repository = repository
        self.assertion_verifier = assertion_verifier

    def propose(self, payload: ExternalIngressProposalInput, assertion: str) -> ExternalIngressProposal:
        self.assertion_verifier(
            assertion,
            audience="workspace-api",
            operation=self.operation,
            body=payload.model_dump_json(exclude_none=True).encode(),
        )
        return self.repository.add(ExternalIngressProposal(**payload.model_dump()))
