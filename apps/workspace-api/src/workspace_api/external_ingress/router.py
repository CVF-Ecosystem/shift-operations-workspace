from fastapi import APIRouter, Header, HTTPException, Request

from .models import ExternalIngressProposal, ExternalIngressProposalInput

router = APIRouter(prefix="/external-ingress", tags=["external_ingress"])


@router.post("/proposals", response_model=ExternalIngressProposal, status_code=202, include_in_schema=False)
def propose_external_ingress(
    payload: ExternalIngressProposalInput,
    request: Request,
    x_service_assertion: str = Header(default=""),
):
    service = getattr(request.app.state, "external_ingress_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="External ingress port unavailable")
    try:
        return service.propose(payload, x_service_assertion)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=401, detail="Service assertion refused") from exc
