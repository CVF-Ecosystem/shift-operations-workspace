"""Identity boundary.

CVF control: ``identity``. Every governed action must run as a known
:class:`Principal` (a user id plus a role), not an anonymous string field.

The workspace API constructs this principal only after verifying a signed JWT
bearer token. This module remains provider-neutral: it defines the shared
principal and role vocabulary consumed by permission, approval, and audit
gates, while token issuance and verification live in ``workspace_api.auth``.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator

# Roles recognised by the workspace. Kept in one place so permission and
# approval policy validate role names against a single vocabulary.
KNOWN_ROLES: frozenset[str] = frozenset(
    {
        "operator",
        "shift_supervisor",
        "responsible_manager",
        "authorized_executive",
        "viewer",
    }
)


class Principal(BaseModel):
    """The authenticated actor for a request."""

    user_id: str
    role: str

    @field_validator("user_id")
    @classmethod
    def _non_empty_user(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("user_id must not be empty")
        return value.strip()

    @field_validator("role")
    @classmethod
    def _known_role(cls, value: str) -> str:
        role = (value or "").strip()
        if role not in KNOWN_ROLES:
            raise ValueError(f"unknown role: {value!r}")
        return role
