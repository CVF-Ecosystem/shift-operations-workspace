"""``POST /approvals`` — create an authenticated approval receipt.

P2B-APPROVER-IDENTITY-RECONCILIATION (SPEC R2, R9.2). The request carries only
``record_type``/``action``/``record_id``; the approver's identity comes solely
from the verified JWT (``get_principal``), never a payload field, and
``risk_class``/``target_version``/``payload_digest`` are always derived from
the stored target (event or creation intent), never accepted from the caller.

F17 (SPEC §5.4): the response uses a dedicated ``ApprovalReceiptResponse``
model — 9 mandated fields, no ``payload_digest``. Both 200 (idempotent repeat)
and 201 (new receipt) are documented in the OpenAPI schema.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application import approval_service
from workspace_api.dependencies import get_ledger, get_principal

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalReceiptResponse(BaseModel):
    """POST /approvals 200 (idempotent repeat) and 201 (new) response — SPEC §5.4.

    Fields: receipt_id, record_type, record_id, action, target_version,
    risk_class, approver_id, approver_role, created_at.
    payload_digest is deliberately excluded from this response.
    """

    receipt_id: UUID
    record_type: str
    record_id: UUID
    action: str
    target_version: int
    risk_class: str
    approver_id: str
    approver_role: str
    created_at: datetime


class ApprovalCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_type: str
    action: str
    record_id: UUID


@router.post(
    "",
    response_model=ApprovalReceiptResponse,
    status_code=201,
    responses={
        200: {"model": ApprovalReceiptResponse, "description": "Idempotent repeat — receipt already exists"},
        201: {"model": ApprovalReceiptResponse, "description": "New receipt created"},
    },
)
def create_approval(
    payload: ApprovalCreateInput,
    response: Response,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        receipt, created = approval_service.create_approval_receipt(
            ledger,
            principal,
            record_type=payload.record_type,
            action=payload.action,
            record_id=payload.record_id,
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    # R2.4: 201 for a newly created receipt, 200 for an exact idempotent repeat.
    response.status_code = 201 if created else 200
    return ApprovalReceiptResponse.model_validate(receipt, from_attributes=True)


class ReadinessResponse(BaseModel):
    """GET /approvals/readiness 200 response — SPEC R35: never exposes
    payload digest, receipt id, approver identity or credential."""

    record_type: str
    record_id: UUID
    action: str
    target_version: int
    risk_class: str
    ready: bool
    required_roles: list[str]
    satisfied_roles: list[str]


@router.get("/readiness", response_model=ReadinessResponse)
def get_readiness(
    record_type: str = Query(...),
    record_id: UUID = Query(...),
    action: str = Query(...),
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    """SPEC R11/R35/R37: sanitized current-binding approval-readiness for
    exactly the four canonical pairs. Read-only — never authorizes."""
    try:
        result = approval_service.evaluate_readiness(
            ledger, principal, record_type=record_type, action=action, record_id=record_id,
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    return ReadinessResponse(
        record_type=result.record_type,
        record_id=result.record_id,
        action=result.action,
        target_version=result.target_version,
        risk_class=result.risk_class,
        ready=result.ready,
        required_roles=result.required_roles,
        satisfied_roles=result.satisfied_roles,
    )
