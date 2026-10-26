"""Actual JWT/current-user and strict request denial over HTTP."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import jwt
import pytest

from workspace_api.auth.tokens import create_access_token
from workspace_api.config import settings
from cvf_runtime.identity import Principal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "unit"))
from p5a2_source_api_helpers import (  # noqa: E402
    api_oracle, assert_private_headers, headers, params, source_client,
)

CASE = api_oracle()["cases"][0]
PATH = "/proactive/source"


@pytest.mark.parametrize("variant", ["missing", "bad_signature", "expired",
                                      "missing_exp", "malformed_exp"])
def test_authentication_precedes_even_malformed_query(variant):
    token = None
    if variant == "bad_signature":
        token = create_access_token(Principal(user_id="PUBLIC_ACTOR", role="viewer")) + "wrong"
    elif variant == "expired":
        token = create_access_token(Principal(user_id="PUBLIC_ACTOR", role="viewer"),
                                    ttl_minutes=-1)
    elif variant in {"missing_exp", "malformed_exp"}:
        payload = {"sub": "PUBLIC_ACTOR", "role": "viewer"}
        if variant == "malformed_exp":
            payload["exp"] = "not-time"
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    auth = {"Authorization": f"Bearer {token}"} if token else {}
    with source_client() as (client, ledger):
        response = client.get(PATH, params={"surprise": "private"}, headers=auth)
        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication required"}
        assert_private_headers(response)


@pytest.mark.parametrize("condition", ["missing", "inactive", "role_changed",
                                       "unknown_role", "privileged_unassigned"])
def test_current_user_and_assignment_refuse_without_source_fields(condition):
    role = "authorized_executive" if condition == "privileged_unassigned" else "viewer"
    actor = "OTHER" if condition == "privileged_unassigned" else "PUBLIC_ACTOR"
    with source_client(actor=actor, role=role) as (client, ledger):
        if condition == "missing":
            ledger.users.pop(actor)
        elif condition == "inactive":
            ledger.users[actor].is_active = False
        elif condition == "role_changed":
            ledger.users[actor].role = "operator"
        elif condition == "unknown_role":
            ledger.users[actor].role = "invalid-role"
        response = client.get(PATH, params=params(CASE), headers=headers(actor, role))
        assert response.status_code == (200 if condition == "privileged_unassigned" else 403)
        if condition == "privileged_unassigned":
            assert response.json()["reason"] == "ACCESS_DENIED"
        else:
            assert response.json() == {"detail": "Access denied"}
        assert "canonical_manifest" not in response.json()
        assert_private_headers(response)


@pytest.mark.parametrize("change", ["unknown", "duplicate", "missing", "body",
                                     "too_long", "invalid", "invalid_utf8"])
def test_strict_request_shape_is_generic_422(change):
    with source_client() as (client, _):
        query = params(CASE)
        content = None
        if change == "unknown":
            query["actor_id"] = "OTHER"
        elif change == "duplicate":
            query = list(query.items()) + [("query_start", query["query_start"])]
        elif change == "missing":
            query.pop("query_end")
        elif change == "body":
            content = b"hidden"
        elif change == "too_long":
            query["query_start"] = "x" * 129
        elif change == "invalid":
            query["query_start"] = "sensitive-invalid-time"
        elif change == "invalid_utf8":
            query["query_start"] = "\ufffd"
        response = client.request("GET", PATH, params=query, content=content,
                                  headers=headers())
        assert response.status_code == 422
        assert response.json() == {"detail": "Invalid request"}
        assert_private_headers(response)


def test_spoofed_identity_headers_have_no_authority():
    with source_client(actor="OTHER") as (client, _):
        response = client.get(PATH, params=params(CASE), headers={
            **headers("OTHER"), "X-User-Id": "PUBLIC_ACTOR",
            "X-User-Role": "authorized_executive", "X-Source-Scope": "PUBLIC_SCOPE",
        })
        assert response.status_code == 200
        assert response.json()["reason"] == "ACCESS_DENIED"
        assert_private_headers(response)


@pytest.mark.parametrize("window,reason", [
    ({"query_start": "2026-01-01T00:00:00"}, "TIME_AMBIGUOUS"),
    ({"query_end": "2026-01-01T00:00:00Z"}, "INVALID_WINDOW"),
    ({"run_as_of": "2999-01-01T00:00:00Z"}, "INVALID_WINDOW"),
])
def test_window_refusal_uses_native_bare_receipt(window, reason):
    with source_client() as (client, _):
        response = client.get(PATH, params={**params(CASE), **window}, headers=headers())
        assert response.status_code == 200
        assert response.json()["reason"] == reason
        assert_private_headers(response)
