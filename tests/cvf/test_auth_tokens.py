"""JWT access token encode/decode (P2-B: real authentication).

Proves decode_access_token is a real verification boundary, not a
pass-through: tampering, expiry, wrong signing key, and wrong algorithm must
all be rejected, and only a validly-signed, unexpired token yields a
Principal.
"""

from datetime import timedelta
from unittest.mock import patch

import jwt
import pytest

from cvf_runtime.identity import Principal

from workspace_api.auth.tokens import (
    TokenError,
    create_access_token,
    decode_access_token,
    decode_access_token_with_expiry,
)
from workspace_api.config import settings


def test_round_trip_decodes_to_the_same_principal():
    principal = Principal(user_id="op1", role="operator")
    token = create_access_token(principal)
    decoded = decode_access_token(token)
    assert decoded == principal


def test_tampered_signature_is_rejected():
    token = create_access_token(Principal(user_id="op1", role="operator"))
    tampered = token[:-4] + "abcd"
    with pytest.raises(TokenError):
        decode_access_token(tampered)


def test_expired_token_is_rejected():
    token = create_access_token(Principal(user_id="op1", role="operator"), ttl_minutes=-1)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_token_signed_with_wrong_secret_is_rejected():
    wrong_secret_token = jwt.encode(
        {"sub": "op1", "role": "operator"}, "a-completely-different-secret", algorithm="HS256"
    )
    with pytest.raises(TokenError):
        decode_access_token(wrong_secret_token)


def test_malformed_token_is_rejected():
    with pytest.raises(TokenError):
        decode_access_token("not-a-jwt-at-all")


def test_token_claiming_alg_none_is_rejected():
    """A classic JWT bypass: a token with `alg: none` and no signature at
    all. decode_access_token pins algorithms=["HS256"], so PyJWT must refuse
    this outright rather than accept an unsigned token."""
    forged = jwt.encode(
        {"sub": "op1", "role": "authorized_executive"}, key="", algorithm="none"
    )
    with pytest.raises(TokenError):
        decode_access_token(forged)


def test_token_with_unknown_role_claim_is_rejected():
    """The token payload is attacker-observable (JWTs are signed, not
    encrypted) but must still be *authored* by this service - a forged
    payload with a role outside KNOWN_ROLES must not construct a Principal."""
    forged = jwt.encode(
        {"sub": "op1", "role": "superadmin"}, settings.jwt_secret_key, algorithm="HS256"
    )
    with pytest.raises(TokenError):
        decode_access_token(forged)


def test_default_ttl_comes_from_settings():
    with patch.object(settings, "jwt_access_token_ttl_minutes", 5):
        token = create_access_token(Principal(user_id="op1", role="operator"))
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        assert payload["exp"] - payload["iat"] == timedelta(minutes=5).total_seconds()


# --- P2C-MUTATION-FULL-UI-C3A1 (SPEC R9): decode_access_token_with_expiry ---


def test_decode_with_expiry_returns_the_same_principal_as_decode_access_token():
    principal = Principal(user_id="op1", role="operator")
    token = create_access_token(principal)
    decoded, _ = decode_access_token_with_expiry(token)
    assert decoded == principal


def test_decode_with_expiry_returns_the_real_token_exp_claim_not_a_recalculation():
    with patch.object(settings, "jwt_access_token_ttl_minutes", 5):
        token = create_access_token(Principal(user_id="op1", role="operator"))
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        _, expires_at = decode_access_token_with_expiry(token)
        assert int(expires_at.timestamp()) == payload["exp"]


def test_decode_with_expiry_rejects_tampered_signature():
    token = create_access_token(Principal(user_id="op1", role="operator"))
    tampered = token[:-4] + "abcd"
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(tampered)


def test_decode_with_expiry_rejects_expired_token():
    token = create_access_token(Principal(user_id="op1", role="operator"), ttl_minutes=-1)
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(token)


def test_decode_with_expiry_rejects_correctly_signed_token_missing_exp_claim():
    """P2C-C3A1-BUILD-REV-F2: a correctly signed token that simply omits
    ``exp`` (e.g. from an incompatible issuer, or a hand-crafted forgery)
    previously reached ``payload["exp"]`` directly and raised an uncaught
    ``KeyError``, surfacing as HTTP 500 from /auth/me instead of a controlled
    401. This must now be the same TokenError category as any other
    malformed/invalid token."""
    no_exp = jwt.encode({"sub": "op1", "role": "operator"}, settings.jwt_secret_key, algorithm="HS256")
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(no_exp)


def test_decode_with_expiry_rejects_non_numeric_exp_claim():
    """F2: a non-numeric exp (e.g. a string) must not reach
    datetime.fromtimestamp() and raise an uncaught TypeError."""
    bad_exp = jwt.encode(
        {"sub": "op1", "role": "operator", "exp": "not-a-number"}, settings.jwt_secret_key, algorithm="HS256"
    )
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(bad_exp)


# --- P2C-C3A1-BUILD-REV-F2 amendment: OverflowError must never escape --------


@pytest.mark.parametrize(
    "exp",
    [10**30, -(10**30), 1e100, float("inf"), float("-inf")],
    ids=["huge_positive_int", "huge_negative_int", "huge_float", "inf", "neg_inf"],
)
def test_decode_with_expiry_rejects_out_of_range_numeric_exp_without_overflow_escaping(exp):
    """F2: a correctly signed token whose exp is numeric but exceeds what
    datetime.fromtimestamp()/the platform time_t can represent previously
    raised an uncaught OverflowError (or OSError/ValueError), surfacing as
    HTTP 500 from /auth/me. Must now be the same controlled TokenError
    category as any other invalid exp."""
    token = jwt.encode({"sub": "op1", "role": "operator", "exp": exp}, settings.jwt_secret_key, algorithm="HS256")
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(token)


def test_decode_with_expiry_rejects_nan_exp_claim():
    """F2: exp=NaN is a float the JWT library permits constructing, but a
    non-finite NumericDate is never valid."""
    token = jwt.encode(
        {"sub": "op1", "role": "operator", "exp": float("nan")}, settings.jwt_secret_key, algorithm="HS256"
    )
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(token)


def test_decode_with_expiry_rejects_boolean_exp_claim():
    """F2: bool is an int subclass (isinstance(True, int) is True) but was
    never a real JWT NumericDate and must be rejected explicitly."""
    token = jwt.encode(
        {"sub": "op1", "role": "operator", "exp": True}, settings.jwt_secret_key, algorithm="HS256"
    )
    with pytest.raises(TokenError):
        decode_access_token_with_expiry(token)
