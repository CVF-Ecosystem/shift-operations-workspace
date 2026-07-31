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

import math
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
    except OverflowError as exc:
        # P2C-C3A1-BUILD-REV-F2: PyJWT's OWN internal exp check
        # (jwt.api_jwt.PyJWT._validate_exp) does `int(payload["exp"])`
        # before this function ever sees the payload, and raises a bare
        # OverflowError (not a PyJWTError subclass) for exp=inf/-inf - this
        # must be just as controlled as any other invalid-token case.
        raise TokenError("token exp claim is out of range") from exc
    try:
        return Principal(user_id=payload.get("sub", ""), role=payload.get("role", ""))
    except ValidationError as exc:
        raise TokenError(str(exc)) from exc


def decode_access_token_with_expiry(token: str) -> tuple[Principal, datetime]:
    """P2C-MUTATION-FULL-UI-C3A1 (SPEC R9, GET /auth/me): the SAME signature
    verification as decode_access_token, plus the real verified ``exp`` claim
    from THIS token - never a freshly recalculated TTL-from-now approximation,
    which would silently diverge from the token actually presented.

    P2C-C3A1-BUILD-REV-F2 repair: a correctly signed token missing ``exp``
    (or carrying a non-numeric one) previously reached ``payload["exp"]``
    directly and raised an uncaught ``KeyError``/``TypeError``, surfacing as
    HTTP 500 from ``/auth/me`` instead of a controlled 401. Every token this
    service itself issues always carries ``exp`` (see create_access_token),
    so a token reaching here without one is necessarily forged, tampered, or
    from an incompatible issuer - the same authentication-failure category
    every other malformed-token case already uses.

    P2C-C3A1-BUILD-REV-F2 amendment: an in-range numeric ``exp`` was not
    enough either - ``datetime.fromtimestamp`` raises ``OverflowError`` (or,
    on some platforms, ``OSError``/``ValueError``) for a value outside what
    the platform's ``time_t`` can represent (e.g. ``10**30`` or ``1e100``),
    which also escaped as an uncaught HTTP 500. ``exp`` is now only accepted
    once it is confirmed to actually round-trip through
    ``datetime.fromtimestamp`` - any exception that call raises is a token
    validity failure, not a server error. ``bool`` is rejected explicitly
    despite being an ``int`` subclass (``isinstance(True, int)`` is
    ``True``), since a boolean was never a real JWT NumericDate. PyJWT's OWN
    internal exp check (inside this same ``jwt.decode`` call) does
    ``int(payload["exp"])`` before this function ever sees the payload, and
    raises a bare ``OverflowError`` (not a ``PyJWTError`` subclass) for
    exp=inf/-inf - caught here for the identical reason."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    except OverflowError as exc:
        raise TokenError("token exp claim is out of range") from exc
    try:
        principal = Principal(user_id=payload.get("sub", ""), role=payload.get("role", ""))
    except ValidationError as exc:
        raise TokenError(str(exc)) from exc
    exp = payload.get("exp")
    if isinstance(exp, bool) or not isinstance(exp, (int, float)):
        raise TokenError("token is missing a valid exp claim")
    if isinstance(exp, float) and not math.isfinite(exp):
        raise TokenError("token exp claim is not a finite value")
    try:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise TokenError("token exp claim is out of range") from exc
    return principal, expires_at
