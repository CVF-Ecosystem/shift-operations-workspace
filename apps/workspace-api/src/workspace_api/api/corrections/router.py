from operations_ledger import Ledger
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.approval import Approval
from cvf_runtime.audit import AuditLog
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application.correction_service import CorrectionService
from workspace_api.dependencies import get_audit_log, get_ledger, get_principal
from operations_domain.models import Correction

router = APIRouter(prefix="/corrections", tags=["corrections"])


class CorrectEventInput(BaseModel):
    reason: str
    approvals: list[Approval] = []


@router.post("/events/{event_id}", response_model=Correction)
def correct_event(
    event_id: UUID,
    payload: CorrectEventInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
    audit: AuditLog = Depends(get_audit_log),
):
    try:
        return CorrectionService(ledger, audit).correct_event(
            event_id, principal, payload.reason, payload.approvals
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Event not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
