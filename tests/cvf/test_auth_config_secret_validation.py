"""JWT secret strength validation (P2B-AUTHENTICATION-REPAIR, T1).

Independently reproduced during DESIGN: Settings(jwt_secret_key="x")
previously constructed without error, and a token forged with that guessed
one-character secret decoded successfully with role="authorized_executive".
These tests prove the fail-closed fix: AC-1..AC-5 from
docs/specs/P2B_AUTHENTICATION_REPAIR_SPEC.md SS6.
"""

import pytest

from workspace_api.config import InsecureJwtSecretError, Settings


def _settings(secret: str) -> Settings:
    # database_url/cors_allowed_origins have their own defaults; only
    # jwt_secret_key is under test here. env_file=".env" would otherwise
    # read a real .env if one existed in the repo root during a test run -
    # none does, but pass _env_file=None to make that explicit and immune
    # to a future stray .env file changing this test's outcome.
    return Settings(_env_file=None, jwt_secret_key=secret)


# --- AC-1: valid secret accepted ---------------------------------------------


def test_valid_strong_secret_is_accepted():
    strong = "a" * 32
    s = _settings(strong)
    assert s.jwt_secret_key == strong


def test_valid_strong_secret_at_exactly_32_bytes_is_accepted():
    exactly_32 = "b" * 32
    assert len(exactly_32.encode("utf-8")) == 32
    s = _settings(exactly_32)
    assert s.jwt_secret_key == exactly_32


# --- AC-2: blank secret rejected ---------------------------------------------


def test_blank_secret_is_rejected():
    with pytest.raises(InsecureJwtSecretError):
        _settings("")


def test_whitespace_only_secret_is_rejected():
    with pytest.raises(InsecureJwtSecretError):
        _settings("    ")


# --- AC-3: too-short secret rejected ------------------------------------------


def test_short_secret_is_rejected():
    with pytest.raises(InsecureJwtSecretError):
        _settings("short")


def test_one_character_secret_is_rejected():
    """The exact regression this tranche repairs: a one-character secret
    ("x") previously constructed without error and signed a valid token."""
    with pytest.raises(InsecureJwtSecretError):
        _settings("x")


def test_31_byte_secret_is_rejected_one_byte_under_the_line():
    thirty_one = "c" * 31
    assert len(thirty_one.encode("utf-8")) == 31
    with pytest.raises(InsecureJwtSecretError):
        _settings(thirty_one)


# --- AC-4: known placeholder values rejected, even if long enough -----------


@pytest.mark.parametrize(
    "placeholder",
    [
        "replace-me-with-a-real-secret",
        "changeme",
        "change-me",
        "secret",
        "password",
    ],
)
def test_known_placeholder_values_are_rejected(placeholder):
    with pytest.raises(InsecureJwtSecretError):
        _settings(placeholder)


def test_env_example_placeholder_is_rejected():
    """.env.example ships JWT_SECRET_KEY=replace-me-with-a-real-secret - a
    deployment that copies it verbatim must fail to start, not run with a
    guessable secret."""
    with pytest.raises(InsecureJwtSecretError):
        _settings("replace-me-with-a-real-secret")


# --- AC-5: no secret leakage --------------------------------------------------


@pytest.mark.parametrize("bad_secret", ["", "short", "x", "changeme"])
def test_rejected_secret_value_never_appears_in_the_error(bad_secret):
    with pytest.raises(InsecureJwtSecretError) as exc_info:
        _settings(bad_secret)
    rendered = str(exc_info.value)
    if bad_secret:
        assert bad_secret not in rendered


# --- SI-5: denylist must not collide with this repo's own test secret ------


def test_conftest_test_secret_is_not_on_the_denylist_and_is_accepted():
    """conftest.py sets JWT_SECRET_KEY to this value for the whole test
    suite. If it were ever added to the denylist, or otherwise rejected,
    every test that imports workspace_api.config would fail to collect."""
    test_secret = "test-only-secret-do-not-use-in-production"
    assert len(test_secret.encode("utf-8")) >= 32
    s = _settings(test_secret)
    assert s.jwt_secret_key == test_secret
