"""Shared HTTP-test helper for the JWT bearer auth boundary (P2-B).

Mints a real signed token directly via workspace_api.auth.tokens - the same
function get_principal uses to verify one - rather than going through
POST /auth/login. These tests exercise governance chains (permission/audit/
freeze/etc.), not the login endpoint itself (see test_auth_login.py for that).
"""

from __future__ import annotations

from cvf_runtime.identity import Principal

from workspace_api.auth.tokens import create_access_token


def auth_headers(user_id: str, role: str) -> dict[str, str]:
    token = create_access_token(Principal(user_id=user_id, role=role))
    return {"Authorization": f"Bearer {token}"}
