from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from cvf_runtime.audit import AuditLog
from cvf_runtime.domain_lock import assert_event_type_in_scope
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from cvf_runtime.policy_loader import load_profile

from workspace_api.application.services import EventService
from workspace_api.application.assignment_scope import require_active_assignment
from operations_ledger import Ledger

from workspace_api.dependencies import get_audit_log, get_ledger, get_principal
from operations_domain.models import EvidenceRef, OperationalEvent, RiskClass

router = APIRouter(prefix="/events", tags=["events"])

# P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R4): hard maximum per returned array.
_MAX_EVENTS = 500


class EventInput(BaseModel):
    shift_id: UUID
    event_type: str
    title: str
    description: str | None = None
    risk_class: RiskClass = RiskClass.R1
    evidence: list[EvidenceRef] = []


class ConfirmInput(BaseModel):
    # P2B-APPROVER-IDENTITY-RECONCILIATION (R7.1): approvals are no longer
    # caller-supplied - the server auto-collects authenticated receipts. This
    # is now an empty body, and extra="forbid" turns a stray legacy
    # `approvals` field into a 422 instead of a silently-ignored no-op.
    model_config = ConfigDict(extra="forbid")


@router.post("", response_model=OperationalEvent)
def create_event(
    payload: EventInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        require_action(principal, "event.create")
        assert_event_type_in_scope(load_profile(), payload.event_type)
        require_active_assignment(ledger, payload.shift_id, principal)
        return ledger.add_event(OperationalEvent(**payload.model_dump()))
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc


@router.post("/{event_id}/confirm", response_model=OperationalEvent)
def confirm_event(
    event_id: UUID,
    payload: ConfirmInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
    audit: AuditLog = Depends(get_audit_log),
):
    try:
        return EventService(ledger, audit).confirm(event_id, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[OperationalEvent])
def list_events(
    shift_id: UUID = Query(..., description="Filter events by shift"),
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    """P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R3/R4/R5): authenticated
    event-list query. Requires a valid JWT via get_principal — identity-only
    read admission, not per-shift assignment or data-scope enforcement.
    Returns events for the given shift in deterministic order with evidence
    preserved. Enforces a 500-record hard maximum (HTTP 422 on overflow, no
    partial result). Missing shift returns 404."""
    try:
        require_active_assignment(ledger, shift_id, principal)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    events = ledger.list_events_for_shift(shift_id)
    if len(events) > _MAX_EVENTS:
        raise HTTPException(
            status_code=422,
            detail=f"Event list exceeds {_MAX_EVENTS}-record maximum; pagination not yet implemented",
        )
    return events
