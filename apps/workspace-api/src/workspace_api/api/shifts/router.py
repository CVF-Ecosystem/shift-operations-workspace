from operations_ledger import Ledger
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from workspace_api.dependencies import get_ledger
from workspace_api.domain.models import Shift

router = APIRouter(prefix="/shifts", tags=["shifts"])

@router.post("", response_model=Shift)
def create_shift(name: str, starts_at: datetime, ends_at: datetime, ledger: Ledger = Depends(get_ledger)):
    return ledger.create_shift(Shift(name=name, starts_at=starts_at, ends_at=ends_at))

@router.get("", response_model=list[Shift])
def list_shifts(ledger: Ledger = Depends(get_ledger)):
    return list(ledger.list_shifts())

@router.post("/{shift_id}/freeze", response_model=Shift)
def freeze_shift(shift_id: UUID, ledger: Ledger = Depends(get_ledger)):
    try:
        return ledger.freeze_shift(shift_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
