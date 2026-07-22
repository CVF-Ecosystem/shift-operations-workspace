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


# --- T2: password byte-length boundary (P2B-AUTHENTICATION-REPAIR) ----------
#
# Reproduced directly during DESIGN, before this fix: a 73-byte password
# returned an uncaught HTTP 500 for BOTH an existing username and an unknown
# one, because bcrypt 5.0.0 raises ValueError above 72 bytes and nothing
# caught it. AC-6..AC-10 of docs/specs/P2B_AUTHENTICATION_REPAIR_SPEC.md.

_OVER_LIMIT_ASCII = "a" * 73
# 25 x 3-byte characters = 75 UTF-8 bytes in only 25 characters: over the
# byte limit while well under 72 *characters*. This is why the check must
# measure bytes - a character-count check would wrongly accept this and
# still crash bcrypt.
_OVER_LIMIT_MULTIBYTE = "日" * 25


def test_password_at_exactly_72_bytes_still_logs_in():
    """AC-6 boundary guard: the limit must reject only what bcrypt cannot
    handle. Exactly 72 bytes is bcrypt's maximum accepted input, so it must
    still work - this repair must not narrow the legitimate path."""
    password = "a" * 72
    assert len(password.encode("utf-8")) == 72
    ledger = _ledger_with_user(password=password)
    client = _client_for(ledger)
    try:
        resp = client.post("/auth/login", json={"username": "op1", "password": password})
        assert resp.status_code == 200, resp.text
        assert decode_access_token(resp.json()["access_token"]).user_id == "op1"
    finally:
        _clear_overrides()


def test_over_limit_ascii_password_existing_username_is_422_not_500():
    """AC-7."""
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/auth/login", json={"username": "op1", "password": _OVER_LIMIT_ASCII}
        )
        assert resp.status_code == 422, resp.text
        assert resp.status_code != 500
    finally:
        _clear_overrides()


def test_over_limit_ascii_password_unknown_username_is_422_not_500():
    """AC-8. The unknown-username path also reached bcrypt (via
    DUMMY_PASSWORD_HASH), so it crashed too before this fix."""
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/auth/login", json={"username": "no-such-user", "password": _OVER_LIMIT_ASCII}
        )
        assert resp.status_code == 422, resp.text
        assert resp.status_code != 500
    finally:
        _clear_overrides()


def test_over_limit_multibyte_password_is_422_not_500():
    """AC-9: fewer than 72 characters but more than 72 UTF-8 bytes."""
    assert len(_OVER_LIMIT_MULTIBYTE) < 72
    assert len(_OVER_LIMIT_MULTIBYTE.encode("utf-8")) > 72
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/auth/login", json={"username": "op1", "password": _OVER_LIMIT_MULTIBYTE}
        )
        assert resp.status_code == 422, resp.text
        assert resp.status_code != 500
    finally:
        _clear_overrides()


def test_over_limit_rejection_is_identical_for_existing_and_unknown_username():
    """AC-10 / SI-4: the length rejection must not become a NEW username
    -enumeration oracle. Status and error shape must be indistinguishable
    between an existing and a non-existent username."""
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        existing = client.post(
            "/auth/login", json={"username": "op1", "password": _OVER_LIMIT_ASCII}
        )
        unknown = client.post(
            "/auth/login", json={"username": "no-such-user", "password": _OVER_LIMIT_ASCII}
        )
        assert existing.status_code == unknown.status_code == 422

        # The 422 body is a flat {"detail": "..."} (see F8 note below) that
        # never mentions the username - compare the full structure, which
        # must be byte-identical here.
        assert existing.json() == unknown.json(), (
            "an over-length password must produce an identical response "
            "whether or not the username exists"
        )
    finally:
        _clear_overrides()


def test_over_limit_password_is_not_echoed_in_the_response():
    """F8 (independent review, 2026-07-22): a pydantic field_validator's
    rejection is rendered by FastAPI's default request-validation-error
    body, which echoes the offending value back in an "input" field - so
    the caller's own over-length password would appear in the 422 response
    body, and from there in any access log or error tracker that captures
    response bodies. The check now runs as a plain HTTPException in the
    route body instead, which has no such field. Assert the submitted
    password value does not appear anywhere in the response."""
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/auth/login", json={"username": "op1", "password": _OVER_LIMIT_ASCII}
        )
        assert resp.status_code == 422
        assert _OVER_LIMIT_ASCII not in resp.text
        assert resp.json() == {
            "detail": "password must not exceed 72 UTF-8 bytes"
        }
    finally:
        _clear_overrides()


def test_over_limit_password_never_reaches_bcrypt_or_the_ledger():
    """SI-4 mechanism proof: rejection happens at the request-validation
    boundary, so neither the ledger lookup nor bcrypt runs at all. Proving
    the mechanism (not just the status code) is what shows the uniformity
    is structural rather than incidental."""
    ledger = _ledger_with_user()
    client = _client_for(ledger)
    try:
        with patch.object(
            auth_router, "verify_password", wraps=auth_router.verify_password
        ) as spy:
            resp = client.post(
                "/auth/login", json={"username": "op1", "password": _OVER_LIMIT_ASCII}
            )
            assert resp.status_code == 422
            assert spy.call_count == 0, (
                "an over-length password must be rejected before any bcrypt "
                "call - that call is exactly what raised the uncaught 500"
            )
    finally:
        _clear_overrides()
