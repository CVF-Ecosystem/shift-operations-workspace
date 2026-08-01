from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, ValidationError

from pydantic import Field

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.shift_service import ShiftService
from workspace_api.application.assignment_scope import assigned_shifts, require_active_assignment
from workspace_api.dependencies import get_ledger, get_principal
from operations_domain.models import CustomerRequest, Incident, Shift, Task

router = APIRouter(prefix="/shifts", tags=["shifts"])

# P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R4): hard maximum per returned array.
_MAX_OPEN_WORK_PER_GROUP = 500


class CloseInput(BaseModel):
    # P2C-MUTATION-FULL-UI-C3B2 (SPEC R13): missing expected_version fails at
    # this HTTP boundary with 422 (Pydantic required-field enforcement, no
    # service call); a stale value fails controlled 409 inside ShiftService.
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)


class FreezeInput(BaseModel):
    # P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE (SPEC R19): report_approved
    # is now a real, checked freeze prerequisite - these two fields are
    # DEPRECATED (OpenAPI marks them via json_schema_extra, not Field's
    # deprecated=True, which would emit a DeprecationWarning on every plain
    # attribute read including legitimate default-value freeze calls) and
    # accepted only at their defaults; any attempt to set either one is
    # refused with 422 by ShiftService.freeze before any mutation.
    # extra="forbid" additionally rejects any undeclared field.
    # P2C-MUTATION-FULL-UI-C3B2 (SPEC R13): expected_version is required.
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    override_unimplemented_prerequisites: bool = Field(
        default=False,
        json_schema_extra={"deprecated": True},
        description="Deprecated and refused if set true: report_approved is now a real, checked prerequisite.",
    )
    override_reason: str | None = Field(
        default=None,
        json_schema_extra={"deprecated": True},
        description="Deprecated and refused if non-null: report_approved is now a real, checked prerequisite.",
    )


class OpenWorkResponse(BaseModel):
    """P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R2/R7): exact open-work
    response contract. The three arrays come from Ledger.open_work_snapshot,
    mapped from its canonical Task, CustomerRequest and Incident groups -
    typed against the same domain models used everywhere else, not a forked
    or generic shape."""
    shift_id: UUID
    tasks: list[Task] = Field(default_factory=list)
    customer_requests: list[CustomerRequest] = Field(default_factory=list)
    incidents: list[Incident] = Field(default_factory=list)


@router.post("", response_model=Shift)
def create_shift(
    name: str,
    starts_at: datetime,
    ends_at: datetime,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    # SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29: previously called
    # ledger.create_shift(...) directly with no identity/permission/audit at
    # all (INTAKE probe: anonymous create -> 200). Governed through
    # ShiftService.create the same way close/freeze are governed.
    try:
        return ShiftService(ledger).create(name, starts_at, ends_at, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("", response_model=list[Shift])
def list_shifts(
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    # P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R4/R5): GET /shifts now
    # requires a valid JWT via get_principal — identity-only read admission,
    # not per-shift assignment or data-scope enforcement. Also enforces the
    # same 500-record hard maximum as /events and open-work (P2C-C3A-REV-F16:
    # this route previously had no limit check at all).
    shifts = assigned_shifts(ledger, principal)
    if len(shifts) > _MAX_OPEN_WORK_PER_GROUP:
        raise HTTPException(
            status_code=422,
            detail=f"Shift list exceeds {_MAX_OPEN_WORK_PER_GROUP}-record maximum; pagination not yet implemented",
        )
    return shifts

@router.post("/{shift_id}/close", response_model=Shift)
def close_shift(
    shift_id: UUID,
    payload: CloseInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    # P-FIX-6: previously called ledger.close_shift(shift_id) directly with no
    # identity/permission/audit at all (second independent review, 2026-07-22:
    # anonymous close -> 200 CLOSED, audit_count=0). Governed through
    # ShiftService.close the same way freeze_shift is governed through
    # ShiftService.freeze. P2C-MUTATION-FULL-UI-C3B2: requires expected_version.
    try:
        return ShiftService(ledger).close(shift_id, principal, expected_version=payload.expected_version)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc


@router.get("/{shift_id}/open-work", response_model=OpenWorkResponse)
def get_open_work(
    shift_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    """P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R2/R4/R5): authenticated
    open-work read. Reuses Ledger.open_work_snapshot — does NOT reimplement
    open predicates. Requires a valid JWT via get_principal — identity-only
    read admission. Enforces a 500-record hard maximum per group (HTTP 422
    on overflow, no partial result). Missing shift returns 404."""
    try:
        require_active_assignment(ledger, shift_id, principal)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    snapshot = ledger.open_work_snapshot(shift_id)
    tasks = snapshot.get("Task", [])
    customer_requests = snapshot.get("CustomerRequest", [])
    incidents = snapshot.get("Incident", [])
    if (
        len(tasks) > _MAX_OPEN_WORK_PER_GROUP
        or len(customer_requests) > _MAX_OPEN_WORK_PER_GROUP
        or len(incidents) > _MAX_OPEN_WORK_PER_GROUP
    ):
        raise HTTPException(
            status_code=422,
            detail=f"Open-work group exceeds {_MAX_OPEN_WORK_PER_GROUP}-record maximum; pagination not yet implemented",
        )
    return OpenWorkResponse(
        shift_id=shift_id,
        tasks=tasks,
        customer_requests=customer_requests,
        incidents=incidents,
    )

@router.post("/{shift_id}/freeze", response_model=Shift)
def freeze_shift(
    shift_id: UUID,
    payload: FreezeInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return ShiftService(ledger).freeze(
            shift_id,
            principal,
            override_unimplemented_prerequisites=payload.override_unimplemented_prerequisites,
            override_reason=payload.override_reason,
            expected_version=payload.expected_version,
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
