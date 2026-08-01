from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from operations_domain.models import Message
from workspace_api.application.message_service import MessageService
from workspace_api.dependencies import get_ledger, get_principal

router = APIRouter(prefix="/messages", tags=["messages"])


class MessageInput(BaseModel):
    shift_id: UUID
    text: str
    # MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30 (SPEC R2): legacy compatibility
    # assertions only — never authority. sender_id/source are always
    # server-derived from the verified principal (see MessageService.create).
    sender_id: str | None = None
    source: str | None = None


@router.post("", response_model=Message)
def create_message(
    payload: MessageInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    # MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30: previously anonymous and
    # called ledger.add_message(...) directly from the router with no
    # identity/permission/audit at all (INTAKE probe: anonymous request ->
    # 200, forged sender_id/source accepted unchanged). Governed through
    # MessageService.create the same way ShiftService/IncidentService govern
    # their creation actions.
    try:
        return MessageService(ledger).create(
            payload.shift_id,
            payload.text,
            principal,
            sender_assertion=payload.sender_id,
            source_assertion=payload.source,
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
