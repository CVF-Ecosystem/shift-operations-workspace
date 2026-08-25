"""Non-secret, closed configuration for the edge boundary."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EdgeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    service_name: str = "integration-edge"
    max_body_bytes: int = Field(default=1_048_576, gt=0)
    assertion_clock_skew_seconds: int = Field(default=5, ge=0, le=30)
    assertion_max_lifetime_seconds: int = Field(default=60, ge=1, le=60)
    raw_retention_days: int = Field(default=30, ge=1, le=30)
    ingress_operation: str = "external_ingress.propose"
    outbound_operation: str = "outbound.deliver"

    @field_validator("service_name")
    @classmethod
    def reject_placeholder(cls, value: str) -> str:
        if value.strip().lower() in {"", "change-me", "changeme", "placeholder"}:
            raise ValueError("placeholder configuration is forbidden")
        return value
