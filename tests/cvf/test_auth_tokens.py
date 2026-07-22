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

from workspace_api.auth.tokens import TokenError, create_access_token, decode_access_token
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
