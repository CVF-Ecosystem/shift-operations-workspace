"""Request-scoped dependencies, including the CVF identity boundary."""

from fastapi import Header, HTTPException
from pydantic import ValidationError

from cvf_runtime.audit import audit_log
from cvf_runtime.identity import Principal

from workspace_api.infrastructure.ledger_factory import build_ledger


def get_ledger():
    return build_ledger()


def get_audit_log():
    return audit_log


def get_principal(
    x_user_id: str = Header(default=""),
    x_user_role: str = Header(default=""),
) -> Principal:
    """Resolve the calling :class:`Principal` from request headers.

    Header-based identity boundary: no anonymous governed action is allowed.
    A missing or invalid identity is refused (401), not defaulted.
    """
    try:
        return Principal(user_id=x_user_id, role=x_user_role)
    except ValidationError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid identity: {exc.errors()[0]['msg']}") from exc
