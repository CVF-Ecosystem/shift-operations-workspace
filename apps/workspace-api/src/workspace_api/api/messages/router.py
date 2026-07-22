from operations_ledger import Ledger
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from workspace_api.dependencies import get_ledger
from operations_domain.models import Message

router = APIRouter(prefix="/messages", tags=["messages"])
class MessageInput(BaseModel):
    shift_id: UUID
    sender_id: str
    text: str
    source: str = "INTERNAL"

@router.post("", response_model=Message)
def create_message(payload: MessageInput, ledger: Ledger = Depends(get_ledger)):
    try:
        return ledger.add_message(Message(**payload.model_dump()))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
