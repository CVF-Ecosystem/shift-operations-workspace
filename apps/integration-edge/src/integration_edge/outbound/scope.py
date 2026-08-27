"""Trusted, indivisible adapter scope binding."""

from __future__ import annotations

from typing import Literal

from channel_sdk import AdapterDeliveryRequestV1
from pydantic import BaseModel, ConfigDict, Field


class AdapterScopeBindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    workspace_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    channel_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_version: str = Field(min_length=1, max_length=128)
    required_prerequisite_receipt_ref: str = Field(min_length=1, max_length=256)
    adapter_id: Literal["generic-webhook"]

    def matches(self, request: AdapterDeliveryRequestV1) -> bool:
        return (
            self.workspace_digest == request.workspace_digest
            and self.channel_digest == request.channel_digest
            and self.policy_version == request.policy_version
            and self.required_prerequisite_receipt_ref
            in request.prerequisite_receipt_refs
        )


def has_exact_scope(
    request: AdapterDeliveryRequestV1, bindings: tuple[AdapterScopeBindingV1, ...]
) -> bool:
    return sum(binding.matches(request) for binding in bindings) == 1
