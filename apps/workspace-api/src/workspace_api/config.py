from pydantic_settings import BaseSettings, SettingsConfigDict

_MIN_JWT_SECRET_BYTES = 32

# P2B-AUTHENTICATION-REPAIR (T1): exact-match known example/placeholder
# values that must never be accepted as a real signing secret. Checked
# BEFORE the length rule - independent review found that checking length
# first made this set unreachable dead code, since every entry is shorter
# than the 32-byte minimum and so was always rejected by length instead.
# Order matters for the error message to be accurate, and so that a
# placeholder long enough to pass the length rule is still refused.
#
# Deliberately does NOT include this repo's own conftest.py test secret -
# the two must never collide, or the test suite would fail to boot (SI-5).
#
# KNOWN LIMITATION, deliberately not solved here: an exact-match denylist
# cannot catch every weak secret. A long-but-guessable value (e.g. a short
# word repeated to 32+ bytes) still passes. Length remains the primary bar;
# real entropy scoring was considered during DESIGN and rejected as
# disproportionate for an internal HS256 signing secret. Do not read this
# denylist as a general secret-strength guarantee.
_JWT_SECRET_DENYLIST = frozenset(
    {
        "replace-me-with-a-real-secret",
        "changeme",
        "change-me",
        "secret",
        "password",
        "your-secret-key",
        "your-secret-key-here",
        "supersecret",
        "test-secret",
        "dev-secret",
    }
)


class InsecureJwtSecretError(ValueError):
    """Raised when JWT_SECRET_KEY fails the minimum security policy.

    Deliberately NOT surfaced through pydantic's own validation machinery.
    Both a ``field_validator`` and ``model_post_init`` run inside
    pydantic-core's validation call, so whatever they raise is wrapped in a
    ``ValidationError`` whose string form echoes the rejected input
    (``input_value=...``) regardless of the message - which would leak the
    very secret this check exists to protect (SI-2). Reproduced directly
    while implementing this fix.

    The check therefore runs in ``Settings.__init__`` AFTER
    ``super().__init__()`` returns - plain Python, outside pydantic's
    error-collection - so this exception's message is exactly what this
    module writes, with no value echo."""


class Settings(BaseSettings):
    app_name: str = "Shift Operations Workspace"
    app_env: str = "development"
    ai_mode: str = "NO_AI"
    # When set, the API uses the durable SqlLedger; otherwise it falls back to
    # the in-memory ledger (tests, offline/degraded mode).
    database_url: str = ""
    # Comma-separated allowlist used outside development. Empty by default so a
    # non-dev deployment that forgets to set it fails closed (no origins) rather
    # than open.
    cors_allowed_origins: str = ""
    # No default (P2-B): the app must refuse to start without a real secret
    # rather than repeat the WEBHOOK_SHARED_SECRET "replace-me" fallback
    # mistake the EA review flagged. Signs/verifies JWT access tokens.
    jwt_secret_key: str
    jwt_access_token_ttl_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **kwargs) -> None:
        """Fail closed at startup (P2B-AUTHENTICATION-REPAIR, T1).

        A one-character or placeholder secret previously passed silently -
        reproduced directly during DESIGN: Settings(jwt_secret_key="x")
        signed a valid authorized_executive token that decoded
        successfully with the guessed one-character key.

        See InsecureJwtSecretError's docstring for why this runs here in
        plain Python rather than through a pydantic validator.

        KNOWN LIMITATION (independent review, 2026-07-22): this guards the
        constructor path only - which covers env vars, .env files, and
        direct construction, i.e. every way a deployment actually supplies
        the setting. It does NOT stop in-process code from bypassing it via
        ``Settings.model_construct(...)`` or by assigning
        ``settings.jwt_secret_key`` after import (tokens.py reads the value
        dynamically per call). Both require arbitrary code execution inside
        the process, which is a strictly larger compromise than a weak
        secret, so this is accepted rather than defended against here.
        """
        super().__init__(**kwargs)
        value = self.jwt_secret_key
        if not value or not value.strip():
            raise InsecureJwtSecretError("JWT_SECRET_KEY must not be blank")
        # Denylist BEFORE length: see _JWT_SECRET_DENYLIST on why order matters.
        if value in _JWT_SECRET_DENYLIST:
            raise InsecureJwtSecretError("JWT_SECRET_KEY must not be a known placeholder value")
        if len(value.encode("utf-8")) < _MIN_JWT_SECRET_BYTES:
            raise InsecureJwtSecretError(
                f"JWT_SECRET_KEY must be at least {_MIN_JWT_SECRET_BYTES} UTF-8 bytes"
            )

    @property
    def is_development(self) -> bool:
        return self.app_env.strip().lower() == "development"

    def allowed_origins(self) -> list[str]:
        """CORS origins. Wildcard only in development; allowlist otherwise."""
        if self.is_development:
            return ["*"]
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


settings = Settings()
