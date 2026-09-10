"""Private P4-E identity-mapping management API (SPEC R17).

Hidden from public OpenAPI (``include_in_schema=False``) until a UI and
operator-disclosure review exists (SPEC section 9), but uses the SAME real
JWT/permission/fresh-authority path as every other governed router - never
a relaxed check because the surface is hidden.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from fastapi import APIRouter, Depends, HTTPException
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from identity_mapping import MappingActionReceipt, SenderObservationV1

from workspace_api.application.p4e_commands import P4eMappingCommandService, _NoSuchActor
from workspace_api.dependencies import get_p4e_mapping_commands, get_principal

router = APIRouter(prefix="/external-identities", tags=["external_identities"])


class ProposeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str = Field(min_length=1)
    # completion-rereview2 F3/SPEC R8: propose creates a NEW aggregate, so
    # the only version it can legitimately expect is 1; the field is
    # still real and enforced (not decorative) - it is compared at write
    # time and any other value is a closed conflict.
    expected_version: int = Field(ge=1)
    target_user_id: str = Field(min_length=1)
    raw_sender: str = Field(min_length=1)
    key_id: str = Field(min_length=1)
    key_version: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class CorrectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    predecessor_mapping_id: str = Field(min_length=1)
    expected_predecessor_version: int = Field(ge=1)
    target_user_id: str = Field(min_length=1)
    raw_sender: str = Field(min_length=1)
    key_id: str = Field(min_length=1)
    key_version: str = Field(min_length=1)
    observation_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class ConfirmInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    raw_sender: str = Field(min_length=1)
    key_id: str = Field(min_length=1)
    key_version: str = Field(min_length=1)
    observation_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class VersionedActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1)


class PrivacyDeleteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


@router.get("/observations", response_model=list[SenderObservationV1], include_in_schema=False)
def list_observations(
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    """SPEC R17/completion-rereview R2: fresh-authority, permission-gated
    observation listing - selector metadata and received time only."""
    try:
        return commands.list_observations(principal)
    except _NoSuchActor:
        raise HTTPException(status_code=403, detail="actor is not a known, active user")
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc


@router.post("/mappings/propose", response_model=MappingActionReceipt, include_in_schema=False)
def propose_mapping(
    payload: ProposeInput,
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    return commands.propose(
        principal, observation_id=payload.observation_id, expected_version=payload.expected_version,
        target_user_id=payload.target_user_id, raw_sender=payload.raw_sender,
        key_id=payload.key_id, key_version=payload.key_version, idempotency_key=payload.idempotency_key,
    )


@router.post("/mappings/{mapping_id}/correct", response_model=MappingActionReceipt, include_in_schema=False)
def correct_mapping(
    mapping_id: str,
    payload: CorrectInput,
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    return commands.correct(
        principal, predecessor_mapping_id=mapping_id,
        expected_predecessor_version=payload.expected_predecessor_version,
        target_user_id=payload.target_user_id,
        raw_sender=payload.raw_sender, key_id=payload.key_id, key_version=payload.key_version,
        observation_id=payload.observation_id, idempotency_key=payload.idempotency_key,
    )


@router.post("/mappings/{mapping_id}/confirm", response_model=MappingActionReceipt, include_in_schema=False)
def confirm_mapping(
    mapping_id: str,
    payload: ConfirmInput,
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    return commands.confirm(
        principal, mapping_id=mapping_id, expected_version=payload.expected_version,
        raw_sender=payload.raw_sender, key_id=payload.key_id, key_version=payload.key_version,
        observation_id=payload.observation_id, idempotency_key=payload.idempotency_key,
    )


@router.post("/mappings/{mapping_id}/reject", response_model=MappingActionReceipt, include_in_schema=False)
def reject_mapping(
    mapping_id: str,
    payload: VersionedActionInput,
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    return commands.reject(
        principal, mapping_id=mapping_id, expected_version=payload.expected_version,
        idempotency_key=payload.idempotency_key,
    )


@router.post("/mappings/{mapping_id}/revoke", response_model=MappingActionReceipt, include_in_schema=False)
def revoke_mapping(
    mapping_id: str,
    payload: VersionedActionInput,
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    return commands.revoke(
        principal, mapping_id=mapping_id, expected_version=payload.expected_version,
        idempotency_key=payload.idempotency_key,
    )


@router.post("/mappings/{mapping_id}/privacy-delete", response_model=MappingActionReceipt, include_in_schema=False)
def privacy_delete_mapping(
    mapping_id: str,
    payload: PrivacyDeleteInput,
    principal: Principal = Depends(get_principal),
    commands: P4eMappingCommandService = Depends(get_p4e_mapping_commands),
):
    return commands.privacy_delete(
        principal, mapping_id=mapping_id, expected_version=payload.expected_version,
        reason=payload.reason, idempotency_key=payload.idempotency_key,
    )
