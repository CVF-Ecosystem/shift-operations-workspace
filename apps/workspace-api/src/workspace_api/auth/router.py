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

# bcrypt hard limit. bcrypt 5.0.0 raises ValueError (not a silent
# truncation) for any input longer than this, so an unbounded password
# field reaches the hashing call and escapes as an uncaught HTTP 500 -
# reproduced directly during DESIGN for BOTH an existing username and an
# unknown one (the latter via the DUMMY_PASSWORD_HASH timing-equalization
# path, which calls bcrypt too). P2B-AUTHENTICATION-REPAIR, T2.
_MAX_PASSWORD_BYTES = 72


class LoginInput(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginInput, ledger: Ledger = Depends(get_ledger)):
    # T2 length check runs first, manually, rather than as a pydantic
    # field_validator. Independent review (2026-07-22) found that a
    # field_validator's rejection is rendered by FastAPI's default
    # request-validation-error body, which echoes the offending value back
    # in an "input" field - meaning a caller's over-long password would be
    # echoed into the response body (and from there, into any access log or
    # error tracker that captures 422 bodies). Raising HTTPException here
    # instead produces a flat {"detail": "..."} body with no input echo,
    # while still running before any ledger lookup or bcrypt call - so the
    # response is identical for every username, exactly as before.
    if len(payload.password.encode("utf-8")) > _MAX_PASSWORD_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"password must not exceed {_MAX_PASSWORD_BYTES} UTF-8 bytes",
        )

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
