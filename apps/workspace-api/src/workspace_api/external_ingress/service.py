from __future__ import annotations

from .models import ExternalIngressProposal, ExternalIngressProposalInput


class ExternalIngressService:
    """Actor-neutral proposal boundary. P4-E SPEC section 6/9: after
    transaction A (``repository.add``) commits, makes one synchronous local
    placement-processing attempt if a ``placement_processor`` was injected -
    a transient failure there leaves the item pending for bounded retry
    (SPEC R12), never erasing the admitted proposal or its receipt."""

    operation = "external_ingress.propose"

    def __init__(self, repository, assertion_verifier, placement_processor=None) -> None:
        self.repository = repository
        self.assertion_verifier = assertion_verifier
        self.placement_processor = placement_processor

    def propose(self, payload: ExternalIngressProposalInput, assertion: str) -> ExternalIngressProposal:
        self.assertion_verifier(
            assertion,
            audience="workspace-api",
            operation=self.operation,
            body=payload.model_dump_json(exclude_none=True).encode(),
        )
        stored = self.repository.add(ExternalIngressProposal(**payload.model_dump()))
        if self.placement_processor is not None:
            try:
                self.placement_processor.process(str(stored.proposal_id))
            except Exception:
                # Transaction B failure never erases the transaction-A
                # admission or its receipt; the work item is left pending
                # for bounded idempotent retry (SPEC R11/R12).
                pass
        return stored
