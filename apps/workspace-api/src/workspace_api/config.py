from pydantic_settings import BaseSettings, SettingsConfigDict


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
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_development(self) -> bool:
        return self.app_env.strip().lower() == "development"

    def allowed_origins(self) -> list[str]:
        """CORS origins. Wildcard only in development; allowlist otherwise."""
        if self.is_development:
            return ["*"]
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


settings = Settings()
