"""JWT access tokens (P2-B: real authentication).

The token carries only two claims: ``sub`` (user_id) and ``role``. This module
is the ONLY place a :class:`Principal` is built from a token, and it verifies
the signature and expiry via PyJWT first - role can never come from anything a
caller supplies directly, unlike the old header-trusting ``get_principal``
(see docs/cvf/CVF_CONTROL_MAPPING.md's identity row before this tranche).

``algorithms=[_ALGORITHM]`` is passed explicitly to ``jwt.decode`` so a token
claiming ``alg: none`` (or any algorithm other than the one this service
signs with) is rejected outright, not silently accepted.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from pydantic import ValidationError

from cvf_runtime.identity import Principal

from workspace_api.config import settings

_ALGORITHM = "HS256"


class TokenError(Exception):
    """Raised for any invalid, expired, malformed, or mis-signed token."""


def create_access_token(principal: Principal, *, ttl_minutes: int | None = None) -> str:
    ttl = timedelta(
        minutes=ttl_minutes if ttl_minutes is not None else settings.jwt_access_token_ttl_minutes
    )
    now = datetime.now(timezone.utc)
    payload = {
        "sub": principal.user_id,
        "role": principal.role,
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> Principal:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    try:
        return Principal(user_id=payload.get("sub", ""), role=payload.get("role", ""))
    except ValidationError as exc:
        raise TokenError(str(exc)) from exc
