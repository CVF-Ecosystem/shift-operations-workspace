from __future__ import annotations

import hashlib
from uuid import uuid4


class RoutingService:
    operation = "external_ingress.propose"

    def __init__(self, core_port, assertion_signer, store) -> None:
        self.core_port, self.assertion_signer, self.store = core_port, assertion_signer, store

    def route(self, *, envelope_id: str, channel: str, external_id: str, candidate: dict):
        proposal = {
            "proposal_id": str(uuid4()), "envelope_id": envelope_id,
            "channel": channel, "external_id": external_id, "candidate": candidate,
            "provenance_digest": hashlib.sha256(envelope_id.encode()).hexdigest(),
            "trust_class": "UNTRUSTED_EXTERNAL", "content_class": "RAW",
            "actor_id": None, "assignment_id": None, "approval_id": None,
            "conversation_id": None, "confirmed": False,
        }
        body = _canonical_body(proposal)
        assertion = self.assertion_signer(
            audience="workspace-api", operation=self.operation, body=body,
            idempotency_key=proposal["proposal_id"],
        )
        self.store.save_proposal(proposal)
        return self.core_port.propose_external_ingress(assertion=assertion,proposal=proposal,idempotency_key=proposal["proposal_id"])


def _canonical_body(value: dict) -> bytes:
    import json
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
