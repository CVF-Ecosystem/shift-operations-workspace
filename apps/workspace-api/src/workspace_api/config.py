from pydantic_settings import BaseSettings, SettingsConfigDict

# P2B-AUTHENTICATION-REPAIR (T1): exact-match known example/placeholder
# values that must never be accepted as a real signing secret, even though
# they satisfy a bare length check. Deliberately does not include this
# repo's own conftest.py test secret - the two must never collide, or the
# test suite would fail to boot (see SPEC SI-5).
_JWT_SECRET_DENYLIST = frozenset(
    {
        "replace-me-with-a-real-secret",
        "changeme",
        "change-me",
        "secret",
        "password",
    }
)


class InsecureJwtSecretError(ValueError):
    """Raised when JWT_SECRET_KEY fails the minimum security policy.

    Deliberately NOT surfaced through a pydantic field_validator: pydantic's
    ValidationError always echoes the rejected input value in its string
    representation (`input_value=...`), regardless of what message the
    validator raises - reproduced directly while writing this fix. Raising
    this plain exception from model_post_init (which runs after validation,
    outside pydantic-core's error-collection machinery) keeps the message
    exactly what this module writes, with no value echo (SI-2)."""


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
        signed a valid authorized_executive token that decoded successfully
        with the guessed one-character key.

        The strength check runs here, AFTER super().__init__() returns,
        rather than in a field_validator or model_post_init - both of those
        run inside pydantic-core's validation call and get wrapped into a
        ValidationError whose default string representation echoes the
        rejected input value (`input_value=...`) regardless of the message
        raised, which SI-2 forbids. Reproduced directly while implementing
        this fix. Running the check here, in plain Python after
        construction has already completed, means InsecureJwtSecretError's
        message is exactly what this module writes - no value echo.
        """
        super().__init__(**kwargs)
        value = self.jwt_secret_key
        if not value or not value.strip():
            raise InsecureJwtSecretError("JWT_SECRET_KEY must not be blank")
        if len(value.encode("utf-8")) < 32:
            raise InsecureJwtSecretError("JWT_SECRET_KEY must be at least 32 UTF-8 bytes")
        if value in _JWT_SECRET_DENYLIST:
            raise InsecureJwtSecretError("JWT_SECRET_KEY must not be a known placeholder value")

    @property
    def is_development(self) -> bool:
        return self.app_env.strip().lower() == "development"

    def allowed_origins(self) -> list[str]:
        """CORS origins. Wildcard only in development; allowlist otherwise."""
        if self.is_development:
            return ["*"]
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


settings = Settings()
