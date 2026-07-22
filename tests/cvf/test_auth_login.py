"""POST /auth/login (P2-B: real authentication).

Proves the login endpoint itself: correct credentials issue a usable token,
and wrong password / unknown username / inactive account are all refused with
the SAME generic 401 (no username-enumeration signal).
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from workspace_api.auth import router as auth_router
from workspace_api.auth.passwords import hash_password
from workspace_api.auth.tokens import decode_access_token
from workspace_api.dependencies import get_ledger
from workspace_api.domain.models import User
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app


def _ledger_with_user(username="op1", password="correct-horse", role="operator", is_active=True):
    ledger = InMemoryLedger()
    ledger.add_user(
        User(
            user_id=username,
            username=username,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )
    )
    return ledger


def _client_for(ledger):
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)


def _clear_overrides():
    app.dependency_overrides.pop(get_ledger, None)


def test_valid_login_returns_a_usable_token():
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        resp = client.post("/auth/login", json={"username": "op1", "password": "correct-horse"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["token_type"] == "bearer"
        assert body["expires_in"] > 0

        principal = decode_access_token(body["access_token"])
        assert principal.user_id == "op1"
        assert principal.role == "operator"
    finally:
        _clear_overrides()


def test_wrong_password_is_401():
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        resp = client.post("/auth/login", json={"username": "op1", "password": "wrong"})
        assert resp.status_code == 401, resp.text
    finally:
        _clear_overrides()


def test_unknown_username_is_401_with_same_message_as_wrong_password():
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        wrong_password = client.post("/auth/login", json={"username": "op1", "password": "wrong"})
        unknown_user = client.post(
            "/auth/login", json={"username": "no-such-user", "password": "whatever"}
        )
        assert unknown_user.status_code == 401 == wrong_password.status_code
        assert unknown_user.json()["detail"] == wrong_password.json()["detail"], (
            "response must not let a caller distinguish an unknown username "
            "from a wrong password (username enumeration)"
        )
    finally:
        _clear_overrides()


def test_inactive_user_login_is_401():
    ledger = _ledger_with_user(is_active=False)
    client = _client_for(ledger)
    try:
        resp = client.post("/auth/login", json={"username": "op1", "password": "correct-horse"})
        assert resp.status_code == 401, resp.text
    finally:
        _clear_overrides()


def test_unknown_username_still_runs_password_verification():
    """Independent review (2026-07-22): verify_password used to be skipped
    entirely for an unknown username (Python's `or` short-circuits), making
    that response ~18x faster than a wrong-password response - a timing
    side-channel enumerating valid usernames despite an identical response
    body. A mock-based spy is used here rather than a wall-clock timing
    assertion, which would be flaky in CI; it proves the fix's actual
    mechanism (verify_password always runs) rather than its side effect."""
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        with patch.object(
            auth_router, "verify_password", wraps=auth_router.verify_password
        ) as spy:
            resp = client.post(
                "/auth/login", json={"username": "no-such-user", "password": "whatever"}
            )
            assert resp.status_code == 401, resp.text
            assert spy.call_count == 1, (
                "verify_password must run even when no user is found, comparing "
                "against DUMMY_PASSWORD_HASH, to avoid a timing side-channel"
            )
            called_hash = spy.call_args.args[1]
            assert called_hash == auth_router.DUMMY_PASSWORD_HASH
    finally:
        _clear_overrides()
