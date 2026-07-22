"""POST /auth/login (P2-B: real authentication).

Out of scope for this tranche, recorded as known limitations rather than
silently dropped: refresh tokens/revocation, self-service registration,
password reset, and login rate-limiting. User provisioning is
scripts/seed_dev_users.py (dev/test only) until a real admin flow exists.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

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

    @field_validator("password")
    @classmethod
    def _password_within_bcrypt_limit(cls, value: str) -> str:
        """Reject over-long passwords at the request boundary (T2).

        Measured in UTF-8 BYTES, not characters: bcrypt's limit is a byte
        limit, so a multibyte string well under 72 characters can still
        exceed 72 bytes.

        Rejecting (422) rather than silently truncating to 72 bytes is
        deliberate - silent truncation means the password actually checked
        is not the one the caller sent, an unobservable correctness
        surprise. This matches the existing request-boundary rejection
        precedent in this codebase (CustomerRequestInput.promised_at's
        str -> datetime fix).

        Because this runs during request-body validation, FastAPI returns
        422 before the route handler body executes - so no ledger lookup
        and no bcrypt call happen, identically for every username. That
        uniformity is what keeps this from reopening the username-
        enumeration side-channel the prior tranche closed: the rejection
        carries no information about whether the username exists.
        """
        if len(value.encode("utf-8")) > _MAX_PASSWORD_BYTES:
            raise ValueError(
                f"password must not exceed {_MAX_PASSWORD_BYTES} UTF-8 bytes"
            )
        return value


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
