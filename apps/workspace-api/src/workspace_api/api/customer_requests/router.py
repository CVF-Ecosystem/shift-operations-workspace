from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.customer_request_service import CustomerRequestService
from workspace_api.dependencies import get_ledger, get_principal
from workspace_api.domain.models import CustomerRequest, CustomerRequestStatus

# Two-word path: no existing router in this repo maps a multi-word resource,
# so hyphen is chosen as the more common REST convention (matches how
# customer_requests would typically be exposed as a public API path).
router = APIRouter(prefix="/customer-requests", tags=["customer_requests"])


class CustomerRequestInput(BaseModel):
    customer_id: str
    shift_id: UUID | None = None
    summary: str
    details: str | None = None
    source_message_id: UUID | None = None
    promised_at: str | None = None
    owner_id: str | None = None
    # No evidence/approvals field: this domain has no evidence/risk_class
    # column in the migration, unlike TaskInput.


class TransitionInput(BaseModel):
    target_status: CustomerRequestStatus


@router.post("", response_model=CustomerRequest)
def create_customer_request(
    payload: CustomerRequestInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    request = CustomerRequest(
        customer_id=payload.customer_id,
        shift_id=payload.shift_id,
        summary=payload.summary,
        details=payload.details,
        source_message_id=payload.source_message_id,
        promised_at=payload.promised_at,
        owner_id=payload.owner_id,
    )
    try:
        return CustomerRequestService(ledger).create_customer_request(request, principal)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{request_id}/transition", response_model=CustomerRequest)
def transition_customer_request(
    request_id: UUID,
    payload: TransitionInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return CustomerRequestService(ledger).transition(
            request_id, principal, payload.target_status
        )
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Customer request not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
