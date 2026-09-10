"""Private P4-E route-binding management + placement-work retry API
(SPEC R13/R17). Hidden from public OpenAPI until a UI/disclosure review
exists; same real JWT/permission/fresh-authority path as every other
governed router."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from fastapi import APIRouter, Depends, HTTPException
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from identity_mapping import MappingActionReceipt

from workspace_api.application.p4e_placement import P4ePlacementCommandService, P4ePlacementProcessor
from workspace_api.dependencies import get_p4e_key_port, get_p4e_placement_commands, get_principal

router = APIRouter(prefix="/conversation-routes", tags=["conversation_routes"])


class BindInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mapping_id: str = Field(min_length=1)
    expected_mapping_version: int = Field(ge=1)
    target_kind: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class ReplaceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_binding_version: int = Field(ge=1)
    target_kind: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


@router.post("/bindings", response_model=MappingActionReceipt, include_in_schema=False)
def bind_route(
    payload: BindInput,
    principal: Principal = Depends(get_principal),
    commands: P4ePlacementCommandService = Depends(get_p4e_placement_commands),
):
    return commands.bind(
        principal, mapping_id=payload.mapping_id, expected_mapping_version=payload.expected_mapping_version,
        target_kind=payload.target_kind, target_id=payload.target_id, idempotency_key=payload.idempotency_key,
    )


@router.post("/bindings/{binding_id}/replace", response_model=MappingActionReceipt, include_in_schema=False)
def replace_binding_route(
    binding_id: str,
    payload: ReplaceInput,
    principal: Principal = Depends(get_principal),
    commands: P4ePlacementCommandService = Depends(get_p4e_placement_commands),
):
    return commands.replace_binding(
        principal, old_binding_id=binding_id, expected_binding_version=payload.expected_binding_version,
        target_kind=payload.target_kind, target_id=payload.target_id,
        idempotency_key=payload.idempotency_key,
    )


@router.post("/placement-work/{proposal_id}/retry", include_in_schema=False)
def retry_placement_work(
    proposal_id: str,
    principal: Principal = Depends(get_principal),
    commands: P4ePlacementCommandService = Depends(get_p4e_placement_commands),
    key_port=Depends(get_p4e_key_port),
):
    """SPEC R7/R12/completion-review F4: bounded local retry, not a
    background daemon - but still a governed action: reread the fresh
    actor and require ``conversation_route.retry_placement_work`` before
    triggering the processor, exactly like every other command here.
    Callers supply only the proposal identity; the processor recomputes
    everything else from durable state."""
    from cvf_runtime.permission import require_action
    from workspace_api.application.p4e_commands import _fresh_principal, _NoSuchActor

    try:
        actor = _fresh_principal(commands.ledger, principal)
    except _NoSuchActor:
        raise HTTPException(status_code=403, detail="actor is not a known, active user")
    try:
        require_action(actor, "conversation_route.retry_placement_work")
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc

    processor = P4ePlacementProcessor(commands.ledger, commands.workspace_digest, key_port)
    decision = processor.process(proposal_id)
    if decision is None:
        raise HTTPException(status_code=409, detail="placement work is not currently claimable")
    return decision
