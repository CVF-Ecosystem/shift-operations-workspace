"""Staffing control plane + session/capability reads (P2C-MUTATION-FULL-UI-C3A1).

Two independent surfaces share this module to stay within the exact-path
ceiling: the five R5 staffing routes (`shift.assignment.manage`, supervisor-
only) and the two advisory session/capability reads (`/auth/me`,
`/shifts/{shift_id}/capabilities`). Neither returns operational
events/work/messages/handovers/Reports - this is not the operational read
endpoint (ADR section 4.2).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority, may_perform
from operations_ledger import Ledger

from workspace_api.application.assignment_service import AssignmentService
from workspace_api.dependencies import get_ledger, get_principal
from workspace_api.domain.models import ShiftAssignment

router = APIRouter(tags=["staffing"])


class StaffingShift(BaseModel):
    shift_id: UUID
    name: str
    status: str


class StaffingUser(BaseModel):
    user_id: str
    username: str
    role: str


class AssignInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str


class RevokeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int


class CapabilitiesResponse(BaseModel):
    shift_id: UUID
    actions: list[str]
    reasons: list[str]


def _handle(fn):
    try:
        return fn()
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/staffing/shifts", response_model=list[StaffingShift])
def list_staffing_shifts(
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    if not has_authority(principal.role, "shift_supervisor"):
        raise HTTPException(status_code=403, detail="requires shift_supervisor or higher")
    return [
        StaffingShift(shift_id=s.shift_id, name=s.name, status=str(s.status))
        for s in ledger.list_shifts()
    ]


@router.get("/staffing/users", response_model=list[StaffingUser])
def list_staffing_users(
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    if not has_authority(principal.role, "shift_supervisor"):
        raise HTTPException(status_code=403, detail="requires shift_supervisor or higher")
    return [StaffingUser(**u) for u in ledger.list_active_users()]


@router.get("/shifts/{shift_id}/assignments", response_model=list[ShiftAssignment])
def list_assignments(
    shift_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    return _handle(lambda: AssignmentService(ledger).list_for_shift(shift_id, principal))


@router.post("/shifts/{shift_id}/assignments", response_model=ShiftAssignment)
def create_assignment(
    shift_id: UUID,
    payload: AssignInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    return _handle(lambda: AssignmentService(ledger).assign(shift_id, payload.user_id, principal))


@router.post("/shifts/{shift_id}/assignments/{assignment_id}/revoke", response_model=ShiftAssignment)
def revoke_assignment(
    shift_id: UUID,
    assignment_id: UUID,
    payload: RevokeInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    return _handle(
        lambda: AssignmentService(ledger).revoke(shift_id, assignment_id, payload.expected_version, principal)
    )


_CAPABILITY_ACTIONS = (
    "event.create", "event.confirm", "event.correct",
    "task.create", "task.transition",
    "customer_request.create", "customer_request.transition",
    "incident.report", "incident.acknowledge", "incident.transition",
    "handover.create", "handover.review", "handover.acknowledge",
    "shift.close", "shift.freeze",
    "message.create",
    "report.generate", "report.submit_review", "report.approve", "report.revoke_approval",
    "shift.assignment.manage",
)


@router.get("/shifts/{shift_id}/capabilities", response_model=CapabilitiesResponse)
def capabilities(
    shift_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    """SPEC R9: requires ACTIVE assignment (or the bounded supervisor
    staffing exception is NOT sufficient here - this is the operational
    capability view, gated the same way C3a2 will gate operational routes).
    Returns advisory action names plus bounded reason categories only - no
    digest, credential or policy internal. Every mutation still re-runs every
    server gate; this is presentation-only and never authorizes."""
    try:
        ledger.get_shift(shift_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc

    assignment = ledger.get_active_assignment(shift_id, principal.user_id)
    if assignment is None:
        raise HTTPException(status_code=403, detail="requires an active assignment for this shift")

    allowed = [action for action in _CAPABILITY_ACTIONS if may_perform(principal.role, action)]
    return CapabilitiesResponse(
        shift_id=shift_id,
        actions=allowed,
        reasons=["active_assignment_required", "server_reauthorizes_every_mutation"],
    )
