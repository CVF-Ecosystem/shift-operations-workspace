from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/{endpoint_id}")
async def receive_webhook(
    endpoint_id: str, request: Request,
    x_channel_id: str = Header(default=""), x_external_message_id: str = Header(default=""),
    x_signature_version: str = Header(default="v1"), x_signature: str = Header(default=""),
    x_timestamp: str = Header(default=""),
):
    service=getattr(request.app.state,"inbound_service",None)
    if service is None: raise HTTPException(status_code=503,detail="Ingress unavailable")
    peer=request.client.host if request.client else None
    try:length=int(request.headers.get("content-length","-1"))
    except ValueError:length=-1
    refused=service.preauthorize(peer=peer,endpoint_id=endpoint_id,content_length=length)
    if refused is not None:return refused.model_dump(exclude_none=True)
    body=await request.body()
    receipt=service.process(endpoint_id=endpoint_id,channel_id=x_channel_id,external_message_id=x_external_message_id,timestamp=x_timestamp,signature_version=x_signature_version,signature=x_signature,body=body)
    return receipt.model_dump(exclude_none=True)
