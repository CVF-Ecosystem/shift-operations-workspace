from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ExternalIngressProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    envelope_id: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    candidate: dict[str, Any]
    provenance_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class ExternalIngressProposal(ExternalIngressProposalInput):
    model_config = ConfigDict(extra="forbid")
    proposal_id: UUID = Field(default_factory=uuid4)
    trust_class: Literal["UNTRUSTED_EXTERNAL"] = "UNTRUSTED_EXTERNAL"
    content_class: Literal["RAW"] = "RAW"
    actor_id: None = None
    assignment_id: None = None
    approval_id: None = None
    conversation_id: None = None
    confirmed: Literal[False] = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
