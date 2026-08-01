from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.handover_service import HandoverService
from workspace_api.application.assignment_scope import require_active_assignment
from workspace_api.dependencies import get_ledger, get_principal
from operations_domain.models import Handover

router = APIRouter(prefix="/handovers", tags=["handovers"])


class HandoverCreateInput(BaseModel):
    # extra="forbid": items, digests, status, actor identity and version are
    # always server-derived (SPEC section 2.5/R8) - the caller supplies only
    # the two shift ids.
    model_config = ConfigDict(extra="forbid")
    from_shift_id: UUID
    to_shift_id: UUID


class ReviewInput(BaseModel):
    # P2C-MUTATION-FULL-UI-C3B2 (SPEC R13): expected_version is required.
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)


class AcknowledgeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)


@router.post("", response_model=Handover)
def create_handover(
    payload: HandoverCreateInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return HandoverService(ledger).create(payload.from_shift_id, payload.to_shift_id, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{handover_id}", response_model=Handover)
def get_handover(
    handover_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        handover = ledger.get_handover(handover_id)
        require_active_assignment(ledger, handover.from_shift_id, principal)
        return handover
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Handover not found") from exc


@router.get("", response_model=list[Handover])
def list_handovers(
    from_shift_id: UUID = Query(...),
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        require_active_assignment(ledger, from_shift_id, principal)
        return ledger.list_handovers_for_shift(from_shift_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Handover not found") from exc


@router.post("/{handover_id}/review", response_model=Handover)
def review_handover(
    handover_id: UUID,
    payload: ReviewInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return HandoverService(ledger).review(handover_id, principal, expected_version=payload.expected_version)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Handover not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{handover_id}/acknowledge", response_model=Handover)
def acknowledge_handover(
    handover_id: UUID,
    payload: AcknowledgeInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return HandoverService(ledger).acknowledge(handover_id, principal, expected_version=payload.expected_version)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Handover not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
