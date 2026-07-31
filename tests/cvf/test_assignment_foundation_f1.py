"""P2C-C3A1 Amendment 2 companion to test_assignment_foundation.py: the F2
HTTP regressions for GET /auth/me, split out purely to keep the host file at
or under the 300-line hard file-size limit (SPEC R9, AC-07). Same `client`
fixture/backend pattern as the host file - not a new vertical.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from workspace_api.dependencies import get_ledger
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app


@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


# --- R9/AC-07: /auth/me returns 401, never 500, for any invalid exp claim ---


def test_auth_me_returns_401_not_500_for_correctly_signed_token_missing_exp(client):
    """F2: a correctly signed token omitting ``exp`` previously reached
    ``payload["exp"]`` uncaught and returned HTTP 500 - reproduced through
    the real FastAPI dependency chain, not just the token-decode unit."""
    import jwt

    from workspace_api.config import settings
    _, http = client
    no_exp_token = jwt.encode({"sub": "op1", "role": "operator"}, settings.jwt_secret_key, algorithm="HS256")
    res = http.get("/auth/me", headers={"Authorization": f"Bearer {no_exp_token}"})
    assert res.status_code == 401


@pytest.mark.parametrize(
    "exp",
    [10**30, 1e100],
    ids=["huge_positive_int", "huge_float"],
)
def test_auth_me_returns_401_not_500_for_out_of_range_numeric_exp(client, exp):
    """F2 amendment: a correctly signed token with an in-range-looking but
    platform-unrepresentable numeric exp (e.g. exp=10**30 or exp=1e100)
    previously raised an uncaught OverflowError from
    datetime.fromtimestamp() - reproduced through the real FastAPI
    dependency chain, not just the token-decode unit, exactly as an
    attacker-controlled token would reach it."""
    import jwt

    from workspace_api.config import settings
    _, http = client
    token = jwt.encode(
        {"sub": "op1", "role": "operator", "exp": exp}, settings.jwt_secret_key, algorithm="HS256"
    )
    res = http.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


@pytest.mark.parametrize(
    "exp",
    [float("inf"), float("-inf"), float("nan"), True],
    ids=["inf", "neg_inf", "nan", "bool_true"],
)
def test_auth_me_returns_401_not_500_for_non_finite_or_boolean_exp(client, exp):
    """F2 amendment: non-finite exp (inf/-inf/nan, which the JWT library
    permits constructing) and a bare boolean exp (an int subclass but never
    a real NumericDate) must both resolve to a controlled 401 through the
    real FastAPI dependency chain, never an uncaught 500."""
    import jwt

    from workspace_api.config import settings
    _, http = client
    token = jwt.encode(
        {"sub": "op1", "role": "operator", "exp": exp}, settings.jwt_secret_key, algorithm="HS256"
    )
    res = http.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
