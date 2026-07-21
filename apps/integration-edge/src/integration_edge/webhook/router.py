import json
import os
from fastapi import APIRouter, Header, HTTPException, Request
from integration_edge.deduplication.store import store
from integration_edge.verification.hmac import verify_hmac
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_PLACEHOLDER_SECRET = "replace-me"


def _resolve_secret() -> str:
    """Fail closed on the webhook secret.

    Outside development, a missing or placeholder secret is a hard error rather
    than a fallback to a public value that would still "verify" HMAC.
    """
    secret = os.getenv("WEBHOOK_SHARED_SECRET", "")
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    if app_env == "development":
        return secret or _PLACEHOLDER_SECRET
    if not secret or secret == _PLACEHOLDER_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Webhook secret is not configured; refusing to verify (fail-closed)",
        )
    return secret


@router.post("/generic")
async def generic_webhook(request: Request, x_signature: str = Header(default=""), x_message_id: str = Header(default="")):
    body = await request.body()
    secret = _resolve_secret()
    if not verify_hmac(body, x_signature, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    if not x_message_id or not store.first_seen(x_message_id):
        raise HTTPException(status_code=409, detail="Duplicate or missing message id")
    payload = json.loads(body.decode("utf-8"))
    return {"accepted": True, "provider": "generic-webhook", "provider_message_id": x_message_id, "raw_payload": payload}
