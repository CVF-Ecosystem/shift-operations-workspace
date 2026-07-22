from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.shift_service import ShiftService
from workspace_api.dependencies import get_ledger, get_principal
from workspace_api.domain.models import Shift

router = APIRouter(prefix="/shifts", tags=["shifts"])


class FreezeInput(BaseModel):
    override_unimplemented_prerequisites: bool = False
    override_reason: str | None = None


@router.post("", response_model=Shift)
def create_shift(name: str, starts_at: datetime, ends_at: datetime, ledger: Ledger = Depends(get_ledger)):
    return ledger.create_shift(Shift(name=name, starts_at=starts_at, ends_at=ends_at))

@router.get("", response_model=list[Shift])
def list_shifts(ledger: Ledger = Depends(get_ledger)):
    return list(ledger.list_shifts())

@router.post("/{shift_id}/close", response_model=Shift)
def close_shift(
    shift_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    # P-FIX-6: previously called ledger.close_shift(shift_id) directly with no
    # identity/permission/audit at all (second independent review, 2026-07-22:
    # anonymous close -> 200 CLOSED, audit_count=0). Governed through
    # ShiftService.close the same way freeze_shift is governed through
    # ShiftService.freeze.
    try:
        return ShiftService(ledger).close(shift_id, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc

@router.post("/{shift_id}/freeze", response_model=Shift)
def freeze_shift(
    shift_id: UUID,
    payload: FreezeInput = FreezeInput(),
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return ShiftService(ledger).freeze(
            shift_id,
            principal,
            override_unimplemented_prerequisites=payload.override_unimplemented_prerequisites,
            override_reason=payload.override_reason,
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
