"""Request-scoped dependencies, including the CVF identity boundary."""

from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from cvf_runtime.audit import audit_log
from cvf_runtime.identity import Principal

from workspace_api.auth.tokens import TokenError, decode_access_token, decode_access_token_with_expiry
from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.infrastructure.ledger_factory import build_ledger

_bearer_scheme = HTTPBearer(auto_error=False)


def get_ledger():
    return build_ledger()


def get_audit_log():
    return audit_log


def get_assignment_scope(ledger=Depends(get_ledger)) -> AssignmentScope:
    """Return the request ledger's canonical operational-scope evaluator."""
    return AssignmentScope(ledger)


def get_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> Principal:
    """Resolve the calling :class:`Principal` from a verified JWT bearer token.

    P2-B (2026-07-22): replaces the previous header-trusting implementation,
    which built a Principal directly from client-supplied X-User-Id/
    X-User-Role headers with no verification at all (see
    docs/cvf/CVF_CONTROL_MAPPING.md's identity row before this change). A
    missing, malformed, expired, or mis-signed token is refused (401), not
    defaulted - and role always comes from the verified token, never from a
    client-supplied field.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return decode_access_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc


def get_principal_with_expiry(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> tuple[Principal, datetime]:
    """P2C-MUTATION-FULL-UI-C3A1 (GET /auth/me only): identical verification
    to get_principal, plus the real verified token expiry. A separate
    dependency rather than changing get_principal's return type, so every
    existing Depends(get_principal) call site remains untouched."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return decode_access_token_with_expiry(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc
