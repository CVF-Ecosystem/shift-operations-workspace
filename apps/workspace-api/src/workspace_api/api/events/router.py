from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.approval import Approval
from cvf_runtime.audit import AuditLog
from cvf_runtime.domain_lock import assert_event_type_in_scope
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import load_profile

from workspace_api.application.services import EventService
from operations_ledger import Ledger

from workspace_api.dependencies import get_audit_log, get_ledger, get_principal
from workspace_api.domain.models import EvidenceRef, OperationalEvent, RiskClass

router = APIRouter(prefix="/events", tags=["events"])


class EventInput(BaseModel):
    shift_id: UUID
    event_type: str
    title: str
    description: str | None = None
    risk_class: RiskClass = RiskClass.R1
    evidence: list[EvidenceRef] = []


class ConfirmInput(BaseModel):
    approvals: list[Approval] = []


@router.post("", response_model=OperationalEvent)
def create_event(
    payload: EventInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        require_action(principal, "event.create")
        assert_event_type_in_scope(load_profile(), payload.event_type)
        return ledger.add_event(OperationalEvent(**payload.model_dump()))
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc


@router.post("/{event_id}/confirm", response_model=OperationalEvent)
def confirm_event(
    event_id: UUID,
    payload: ConfirmInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
    audit: AuditLog = Depends(get_audit_log),
):
    try:
        return EventService(ledger, audit).confirm(event_id, principal, payload.approvals)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Event not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
