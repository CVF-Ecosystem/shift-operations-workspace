"""Report HTTP API (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE, SPEC R26).

Routers validate/map errors only - they never construct snapshots, call
ledger mutations, open transactions or append audits directly (WO section
3.4). ``ReportResponse`` unpacks the packed database ``content`` JSON into
the flat public shape SPEC R2 requires - callers never see a nested
``content`` property.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from operations_domain.models import Report, ReportSection, ReportSourceRef, ReportStatus, ReportType
from workspace_api.application.report_service import ReportService
from workspace_api.application.assignment_scope import AssignmentScope, require_active_assignment
from workspace_api.dependencies import get_ledger, get_principal

router = APIRouter(prefix="/reports", tags=["reports"])

_MAX_HISTORY_ROWS = 100


class ReportCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    shift_id: UUID


class ReportPreconditionInput(BaseModel):
    # P2C-MUTATION-FULL-UI-C3B2 (SPEC R13): submit-review/approve are
    # status-only transitions - content version does not increment.
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    expected_status: ReportStatus


class ReportVersionInput(BaseModel):
    # P2C-MUTATION-FULL-UI-C3B2 (SPEC R13): expected_version/expected_status
    # are required; content version does not increment on a status-only move.
    model_config = ConfigDict(extra="forbid")
    reason: str | None = None
    expected_version: int = Field(ge=1)
    expected_status: ReportStatus


class ReportResponse(BaseModel):
    # SPEC R2: exact public shape. sections/source_manifest/snapshot_digest
    # are unpacked losslessly from the persisted content JSON - no nested
    # content object is exposed.
    model_config = ConfigDict(extra="forbid")
    report_id: UUID
    shift_id: UUID
    report_type: ReportType
    version: int
    status: ReportStatus
    is_current: bool
    sections: list[ReportSection]
    source_manifest: list[ReportSourceRef]
    snapshot_digest: str
    generated_from_cutoff: datetime
    created_at: datetime

    @classmethod
    def from_report(cls, report: Report) -> "ReportResponse":
        return cls(
            report_id=report.report_id,
            shift_id=report.shift_id,
            report_type=report.report_type,
            version=report.version,
            status=report.status,
            is_current=report.is_current,
            sections=report.content.sections,
            source_manifest=report.content.source_manifest,
            snapshot_digest=report.content.snapshot_digest,
            generated_from_cutoff=report.generated_from_cutoff,
            created_at=report.created_at,
        )


@router.post("", response_model=ReportResponse, status_code=201)
def generate_report(
    payload: ReportCreateInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        report = ReportService(ledger).generate(payload.shift_id, principal)
        return ReportResponse.from_report(report)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        report = ledger.get_report(report_id)
        AssignmentScope(ledger).require_record(report, principal)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc
    return ReportResponse.from_report(report)


@router.get("", response_model=list[ReportResponse])
def list_reports(
    shift_id: UUID = Query(...),
    include_history: bool = Query(False),
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        require_active_assignment(ledger, shift_id, principal)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc
    if not include_history:
        try:
            current = ledger.get_current_report(shift_id, "END_SHIFT")
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return [ReportResponse.from_report(current)] if current is not None else []

    history = ledger.list_reports_for_shift(shift_id, "END_SHIFT")
    if len(history) > _MAX_HISTORY_ROWS:
        raise HTTPException(
            status_code=422,
            detail=f"Report history exceeds {_MAX_HISTORY_ROWS}-record maximum; pagination not yet implemented",
        )
    return [ReportResponse.from_report(r) for r in history]


@router.post("/{report_id}/versions", response_model=ReportResponse, status_code=201)
def create_report_version(
    report_id: UUID,
    payload: ReportVersionInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        report = ReportService(ledger).create_successor(
            report_id, principal, reason=payload.reason,
            expected_version=payload.expected_version, expected_status=payload.expected_status,
        )
        return ReportResponse.from_report(report)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{report_id}/submit-review", response_model=ReportResponse)
def submit_review(
    report_id: UUID,
    payload: ReportPreconditionInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        report = ReportService(ledger).submit_review(
            report_id, principal,
            expected_version=payload.expected_version, expected_status=payload.expected_status,
        )
        return ReportResponse.from_report(report)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{report_id}/approve", response_model=ReportResponse)
def approve_report(
    report_id: UUID,
    payload: ReportPreconditionInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        report = ReportService(ledger).approve(
            report_id, principal,
            expected_version=payload.expected_version, expected_status=payload.expected_status,
        )
        return ReportResponse.from_report(report)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
