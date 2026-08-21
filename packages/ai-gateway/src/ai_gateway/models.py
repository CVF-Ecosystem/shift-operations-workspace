"""Strict gateway contracts (SPEC R2/R10).

Every model rejects unknown fields, is frozen, and uses Pydantic strict mode, so
a typo in a policy fact fails closed instead of silently defaulting. Mutable
defaults are forbidden: sequence fields are tuples with immutable defaults.

This module performs no I/O, no clock reads, and no provider access. Timestamps
and digests are supplied by callers so receipts stay deterministic under test.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

DIGEST_PATTERN = r"^[0-9a-f]{64}$"
Digest = Annotated[str, Field(pattern=DIGEST_PATTERN)]


def canonical_json(value: Any) -> str:
    """Byte-deterministic JSON for digesting (sorted keys, tight separators)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_of(value: Any) -> str:
    """SHA-256 over the canonical JSON encoding of ``value``."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class StrictModel(BaseModel):
    """Closed schema: unknown fields rejected, immutable, strict coercion."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class AIMode(str, Enum):
    """Application AI mode. Only ``EXTERNAL_AI`` may reach a provider."""

    NO_AI = "NO_AI"
    RULES_ONLY = "RULES_ONLY"
    EXTERNAL_AI = "EXTERNAL_AI"


class Classification(str, Enum):
    """Data classification, matching cvf-runtime data-policy vocabulary."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class Placement(str, Enum):
    """Provider placement category (cvf_runtime.data_scope constants)."""

    EXTERNAL = "external"
    ENTERPRISE = "enterprise"
    LOCAL = "local"


class GateOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_REACHED = "NOT_REACHED"


class FinalOutcome(str, Enum):
    ACCEPTED = "ACCEPTED"
    REFUSED_PRE_DISPATCH = "REFUSED_PRE_DISPATCH"
    FAILED_POST_DISPATCH = "FAILED_POST_DISPATCH"
    FALLBACK_RULES = "FALLBACK_RULES"


class ProviderRequest(StrictModel):
    """What the gateway hands an injected provider. No credentials here."""

    task_type: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    context: dict[str, Any]
    output_schema: dict[str, Any]
    timeout_seconds: Annotated[int, Field(ge=1, le=300)] = 30
    max_output_tokens: Annotated[int, Field(ge=1, le=32000)] = 2000


class ProviderResult(StrictModel):
    """What a provider returns. ``usage`` holds integer token counts only."""

    output: dict[str, Any]
    provider_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    usage: dict[str, int] = Field(default_factory=dict)


class ContextFacts(StrictModel):
    """Caller-declared facts about the context being sent (SPEC R5).

    ``minimization_proven`` must be explicitly true for INTERNAL to reach an
    external placement. P4-A1's current handoff reports NOT_PROVEN, so it fails
    closed here without this module ever mutating or relabelling that handoff.
    """

    classification: Classification
    redaction_applied: bool
    minimization_proven: bool
    evidence_count: Annotated[int, Field(ge=0)]
    estimated_input_tokens: Annotated[int, Field(ge=0)]
    context_digest: Digest


class BudgetFacts(StrictModel):
    """Cost-policy facts plus current spend, supplied by the caller (R6)."""

    per_request_token_limit: Annotated[int, Field(ge=1)]
    daily_budget_usd_millis: Annotated[int, Field(ge=0)]
    monthly_budget_usd_millis: Annotated[int, Field(ge=0)]
    spent_today_usd_millis: Annotated[int, Field(ge=0)]
    spent_month_usd_millis: Annotated[int, Field(ge=0)]
    estimated_cost_usd_millis: Annotated[int, Field(ge=0)]
    on_budget_exceeded: str = Field(default="fallback_to_rules", min_length=1)
    kill_switch_enabled: bool = False


class TerminationFacts(StrictModel):
    """Observed stop-condition state at preflight and after dispatch (R7)."""

    terminate_when: tuple[str, ...] = ()
    elapsed_s: Annotated[int, Field(ge=0)] = 0
    timeout_s: Annotated[int, Field(ge=0)] = 0
    used_tokens: Annotated[int, Field(ge=0)] = 0
    token_limit: Annotated[int, Field(ge=0)] = 0
    consecutive_failures: Annotated[int, Field(ge=0)] = 0
    schema_failures: Annotated[int, Field(ge=0)] = 0
    kill_switch_active: bool = False


class GatewayRequest(StrictModel):
    """One governed execution request (SPEC R2)."""

    task_type: str = Field(min_length=1)
    ai_mode: AIMode
    provider_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    placement: Placement
    context: dict[str, Any]
    output_schema: dict[str, Any]
    context_facts: ContextFacts
    budget_facts: BudgetFacts
    termination_facts: TerminationFacts
    timeout_seconds: Annotated[int, Field(ge=1, le=300)] = 30
    max_output_tokens: Annotated[int, Field(ge=1, le=32000)] = 2000

    @model_validator(mode="after")
    def _schema_must_be_object(self) -> "GatewayRequest":
        if self.output_schema.get("type") != "object":
            raise ValueError("output_schema must declare type 'object'")
        return self


class UsageReservation(StrictModel):
    """An outstanding reservation held in the process-local ledger (R6)."""

    reservation_id: str = Field(min_length=1)
    estimated_tokens: Annotated[int, Field(ge=0)]
    estimated_cost_usd_millis: Annotated[int, Field(ge=0)]


class GateRecord(StrictModel):
    """One gate's outcome, in execution order, for the receipt (R10)."""

    gate: str = Field(min_length=1)
    outcome: GateOutcome
    reason_code: str = Field(default="", max_length=64)


class GatewayReceipt(StrictModel):
    """Sanitized evidence of one execution (SPEC R10).

    Contains digests and safe identifiers only: never prompt text, context body,
    output body, an authorization header, a credential, or raw provider error
    text that could echo a secret.
    """

    task_type: str = Field(min_length=1)
    provider_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    endpoint_origin: str = Field(default="", max_length=200)
    ai_mode: AIMode
    classification: Classification
    placement: Placement
    request_digest: Digest
    context_digest: Digest
    output_schema_digest: Digest
    output_digest: str = Field(default="", pattern=rf"^$|{DIGEST_PATTERN[1:-1]}")
    gates: tuple[GateRecord, ...]
    final_outcome: FinalOutcome
    reason_code: str = Field(default="", max_length=64)
    reserved_tokens: Annotated[int, Field(ge=0)] = 0
    reserved_cost_usd_millis: Annotated[int, Field(ge=0)] = 0
    actual_tokens: Annotated[int, Field(ge=0)] = 0
    actual_cost_usd_millis: Annotated[int, Field(ge=0)] = 0
    usage_committed: bool = False
    reservation_released: bool = False
    timed_out: bool = False
    cancel_attempted: bool = False
    provider_attempts: Annotated[int, Field(ge=0, le=1)] = 0
    started_at: str = Field(min_length=1)
    finished_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def _bounded_facts(self) -> "GatewayReceipt":
        if self.final_outcome is FinalOutcome.ACCEPTED:
            if self.provider_attempts != 1:
                raise ValueError("accepted result requires exactly one physical attempt")
            if not self.output_digest:
                raise ValueError("accepted result requires an output digest")
            if not self.usage_committed:
                raise ValueError("accepted result requires committed usage")
        if self.final_outcome is FinalOutcome.REFUSED_PRE_DISPATCH and self.provider_attempts != 0:
            raise ValueError("pre-dispatch refusal requires zero physical attempts")
        if self.usage_committed and self.reservation_released:
            raise ValueError("a reservation cannot be both committed and released")
        return self


class GatewayResult(StrictModel):
    """Execution result. ``output`` is present only when accepted."""

    accepted: bool
    output: dict[str, Any] | None = None
    receipt: GatewayReceipt

    @model_validator(mode="after")
    def _output_matches_acceptance(self) -> "GatewayResult":
        if self.accepted and self.output is None:
            raise ValueError("accepted result requires output")
        if not self.accepted and self.output is not None:
            raise ValueError("non-accepted result must not carry output")
        if self.accepted != (self.receipt.final_outcome is FinalOutcome.ACCEPTED):
            raise ValueError("accepted flag must match receipt final_outcome")
        return self
