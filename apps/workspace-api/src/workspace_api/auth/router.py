"""POST /auth/login (P2-B: real authentication).

Out of scope for this tranche, recorded as known limitations rather than
silently dropped: refresh tokens/revocation, self-service registration,
password reset, and login rate-limiting. User provisioning is
scripts/seed_dev_users.py (dev/test only) until a real admin flow exists.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.auth.passwords import DUMMY_PASSWORD_HASH, verify_password
from workspace_api.auth.tokens import create_access_token
from workspace_api.config import settings
from workspace_api.dependencies import get_ledger

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginInput, ledger: Ledger = Depends(get_ledger)):
    user = ledger.get_user_by_username(payload.username)
    # One generic failure message/status for unknown username, wrong
    # password, and inactive account - do not let the response distinguish
    # which of these happened (avoids username enumeration). Independent
    # review (2026-07-22): also always run verify_password, even when no
    # user was found, against DUMMY_PASSWORD_HASH - otherwise an unknown
    # username short-circuits past the bcrypt call entirely, making it
    # ~18x faster than a wrong-password response and enumerable by timing
    # alone despite the identical response body.
    password_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, password_hash)
    if user is None or not user.is_active or not password_ok:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    principal = Principal(user_id=user.user_id, role=user.role)
    token = create_access_token(principal)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_access_token_ttl_minutes * 60,
    )
