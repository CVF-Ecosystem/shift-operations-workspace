from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.incident_service import IncidentService
from workspace_api.application.assignment_scope import AssignmentScope, require_active_assignment
from workspace_api.dependencies import get_ledger, get_principal
from operations_domain.models import EvidenceRef, Incident, IncidentStatus, RiskClass

router = APIRouter(prefix="/incidents", tags=["incidents"])


class IncidentInput(BaseModel):
    # extra="forbid": caller-supplied approvals, approver identity, target
    # version, status, or risk-derived authority are prohibited at the
    # request boundary, not just in the service (SPEC section 2.5).
    model_config = ConfigDict(extra="forbid")
    shift_id: UUID
    risk_class: RiskClass = RiskClass.R1
    summary: str
    description: str | None = None
    owner_id: str | None = None
    evidence: list[EvidenceRef] = []


class AcknowledgeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_status: IncidentStatus


@router.post("", response_model=Incident)
def report_incident(
    payload: IncidentInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    incident = Incident(
        shift_id=payload.shift_id,
        risk_class=payload.risk_class,
        summary=payload.summary,
        description=payload.description,
        owner_id=payload.owner_id,
        evidence=payload.evidence,
    )
    try:
        return IncidentService(ledger).report(incident, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        incident = ledger.get_incident(incident_id)
        return AssignmentScope(ledger).require_record(incident, principal)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Incident not found") from exc


@router.get("", response_model=list[Incident])
def list_incidents(
    shift_id: UUID = Query(...),
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        require_active_assignment(ledger, shift_id, principal)
        return ledger.list_incidents_for_shift(shift_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Incident not found") from exc


@router.post("/{incident_id}/acknowledge", response_model=Incident)
def acknowledge_incident(
    incident_id: UUID,
    payload: AcknowledgeInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return IncidentService(ledger).acknowledge(incident_id, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Incident not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{incident_id}/transition", response_model=Incident)
def transition_incident(
    incident_id: UUID,
    payload: TransitionInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return IncidentService(ledger).transition(incident_id, principal, payload.target_status)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Incident not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
