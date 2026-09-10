import json

from fastapi import APIRouter, Header, HTTPException, Request

from integration_edge.invariants import emit_ingress_terminal_receipt
from integration_edge.models import SenderAwareIngressRequest

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/{endpoint_id}")
async def receive_webhook(
    endpoint_id: str, request: Request,
    x_channel_id: str = Header(default=""), x_external_message_id: str = Header(default=""),
    x_signature_version: str = Header(default="v1"), x_signature: str = Header(default=""),
    x_timestamp: str = Header(default=""), x_sender_aware: str = Header(default=""),
):
    """completion-rereview R1: ``p4e-sender-v1`` is the one integrated,
    version-selected sender-aware transport path - the closed
    ``SenderAwareIngressRequest`` envelope travels in the dedicated
    ``X-Sender-Aware`` header (JSON), never inside the untrusted candidate
    body, and unknown/extra/secret-bearing fields are rejected by the
    closed model itself (``extra=\"forbid\"``) before any verification
    runs. Every other signature version never constructs this object and
    therefore can never carry sender evidence."""
    service=getattr(request.app.state,"inbound_service",None)
    if service is None: raise HTTPException(status_code=503,detail="Ingress unavailable")
    peer=request.client.host if request.client else None
    try:length=int(request.headers.get("content-length","-1"))
    except ValueError:length=-1
    refused=service.preauthorize(peer=peer,endpoint_id=endpoint_id,content_length=length)
    if refused is not None:return refused.model_dump(exclude_none=True)
    body=await request.body()
    sender_aware_request=None
    if x_signature_version=="p4e-sender-v1":
        try:
            payload=json.loads(x_sender_aware) if x_sender_aware else {}
            sender_aware_request=SenderAwareIngressRequest(**payload)
        except (ValueError, TypeError):
            # pinned p4c-ingress-terminal-outcomes matrix: AUTH_REFUSED's
            # reason is closed to MISSING_SIGNATURE/INVALID_SIGNATURE/
            # STALE_SIGNATURE - a malformed sender-aware envelope is an
            # authentication failure, not a new reason literal.
            return emit_ingress_terminal_receipt(
                "AUTH_REFUSED",reason="INVALID_SIGNATURE",
                preauth_count=1,postauth_count=0,route_attempts=0,
            ).model_dump(exclude_none=True)
    receipt=service.process(endpoint_id=endpoint_id,channel_id=x_channel_id,external_message_id=x_external_message_id,timestamp=x_timestamp,signature_version=x_signature_version,signature=x_signature,body=body,sender_aware_request=sender_aware_request)
    return receipt.model_dump(exclude_none=True)
