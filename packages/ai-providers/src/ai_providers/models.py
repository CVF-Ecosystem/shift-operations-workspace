"""Strict P4-B provider-mode contracts (SPEC R1/R4/R9). Reuses P4-A's
canonical ``ai_gateway.models`` types directly (never redefines/relaxes
them); every public model is strict/frozen/extra-forbid. Bounded-JSON
validation (depth/size/container bounds, non-finite floats rejected -
P4B-REV-F4) lives in :mod:`ai_providers.errors` (imported here), a leaf
module shared by every model/rule/mock module with no import cycle. No I/O,
clock read, or randomness in this module.
"""

from __future__ import annotations

import copy
from enum import Enum
from typing import Annotated, Any

from ai_gateway.models import Digest, Placement, StrictModel, canonical_json, digest_of
from pydantic import Field, model_validator

from .errors import (
    MAX_CONTAINER_ITEMS,
    MAX_JSON_BYTES,
    MAX_JSON_DEPTH,
    assert_bounded_json,
    assert_receipt_grammar,
)


class ProviderModeOutcome(str, Enum):
    """Every terminal outcome ``execute`` may return (SPEC R2); exactly one
    applies per execution."""

    AI_MODE_DISABLED = "AI_MODE_DISABLED"
    RULES_MATCHED = "RULES_MATCHED"
    RULES_NO_MATCH = "RULES_NO_MATCH"
    RULES_SCHEMA_INVALID = "RULES_SCHEMA_INVALID"
    EXTERNAL_IDENTITY_MISMATCH = "EXTERNAL_IDENTITY_MISMATCH"
    EXTERNAL_ACCEPTED = "EXTERNAL_ACCEPTED"
    EXTERNAL_NOT_ACCEPTED = "EXTERNAL_NOT_ACCEPTED"
    REQUEST_INVALID = "REQUEST_INVALID"


class ProviderModeRequestV1(StrictModel):
    """The one strict public request ``ProviderModeService.execute`` accepts
    (SPEC R2). ``nested_gateway_request`` (``EXTERNAL_AI`` only) is a plain
    JSON dump the service reconstructs into a real, strict
    ``ai_gateway.models.GatewayRequest`` before use (R1) - never trusted as
    an already-validated instance. ``provider_id``/``model_id``/
    ``placement``/``context_digest`` (P4B-REV-F3) are the outer request's
    own explicit binding facts the service compares against the nested
    request (SPEC R6) before any delegation - a caller cannot satisfy R6
    with a nested request alone."""

    task_type: str = Field(min_length=1)
    ai_mode: str = Field(min_length=1)
    facts: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any]
    nested_gateway_request: dict[str, Any] | None = None
    policy_version: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    provider_id: str = Field(default="", max_length=200)
    model_id: str = Field(default="", max_length=200)
    placement: Placement | None = None
    context_digest: Digest | None = None

    @model_validator(mode="after")
    def _facts_and_schema_are_bounded_json(self) -> "ProviderModeRequestV1":
        assert_bounded_json(self.facts, label="facts")
        assert_bounded_json(self.output_schema, label="output_schema")
        if self.output_schema.get("type") != "object":
            raise ValueError("output_schema must declare type 'object'")
        return self


class RuleDefinitionV1(StrictModel):
    """One deterministic local rule (SPEC R4/R5): exact-scalar
    ``required_facts`` match, fixed JSON-object ``output`` returned
    verbatim (deep-copy isolated) when this rule wins."""

    rule_id: str = Field(min_length=1)
    task_type: str = Field(min_length=1)
    priority: int
    required_facts: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any]

    @model_validator(mode="after")
    def _facts_and_output_are_bounded_scalar_json(self) -> "RuleDefinitionV1":
        assert_bounded_json(self.required_facts, label="required_facts")
        assert_bounded_json(self.output, label="output")
        for key, value in self.required_facts.items():
            if isinstance(value, (dict, list)):
                raise ValueError(f"required_facts[{key!r}]: must be an exact-match scalar, not a container")
        return self

    def signature(self) -> tuple[str, int, str]:
        """The ``(task_type, priority, required_facts)`` ambiguity signature
        RuleSetV1 construction rejects duplicates of (SPEC R5)."""
        return (self.task_type, self.priority, canonical_json(self.required_facts))


class MockAuthorizationV1(StrictModel):
    """Explicit, immutable authorization a mock adapter construction
    requires (SPEC R7): no default can accidentally satisfy it - a caller
    must spell out exactly this purpose and ``evidence_eligible=False``."""

    purpose: str = Field(min_length=1)
    evidence_eligible: bool

    @model_validator(mode="after")
    def _purpose_and_eligibility_are_test_only(self) -> "MockAuthorizationV1":
        if self.purpose != "TEST_ONLY_COMPONENT_TEST":
            raise ValueError("purpose must equal TEST_ONLY_COMPONENT_TEST")
        if self.evidence_eligible is not False:
            raise ValueError("evidence_eligible must be exactly False")
        return self


class ProviderKind(str, Enum):
    """Registry-owned provider kind (SPEC R8); ``MOCK`` is the only kind
    admitted without ``allow_test_only``."""

    NO_AI = "NO_AI"
    RULES_ONLY = "RULES_ONLY"
    EXTERNAL_GATEWAY = "EXTERNAL_GATEWAY"
    MOCK = "MOCK"


class ProviderMetadataV1(StrictModel):
    """Immutable metadata one registry entry owns (SPEC R8): kind,
    placement, exact model ids; never caller-relabelable after
    registration. ``placement`` reuses P4-A's canonical ``Placement`` enum,
    never a string like ``"mars"`` (P4B-REV-F3/SPEC R1)."""

    provider_id: str = Field(min_length=1)
    kind: ProviderKind
    placement: Placement
    model_ids: tuple[str, ...] = Field(min_length=1)
    evidence_eligible: bool

    @model_validator(mode="after")
    def _mock_is_never_evidence_eligible(self) -> "ProviderMetadataV1":
        if self.kind is ProviderKind.MOCK and self.evidence_eligible is not False:
            raise ValueError("a MOCK provider entry must have evidence_eligible=False")
        if len(set(self.model_ids)) != len(self.model_ids):
            raise ValueError("model_ids must be duplicate-free")
        return self


VALID_RECEIPT_AI_MODES = ("NO_AI", "RULES_ONLY", "EXTERNAL_AI", "UNKNOWN")
"""P4B-REV-F5: the closed set of ``ai_mode`` values a receipt may carry.
``UNKNOWN`` is the schema-permitted stand-in for any bogus mode string - the
raw string is never echoed, keeping this model and the published JSON
schema mutually exhaustive."""


def canonical_receipt_ai_mode(raw_ai_mode: str) -> str:
    """Map a request's raw ``ai_mode`` string to the receipt's closed
    4-value vocabulary (SPEC R9/P4B-REV-F5)."""
    return raw_ai_mode if raw_ai_mode in ("NO_AI", "RULES_ONLY", "EXTERNAL_AI") else "UNKNOWN"


class ProviderModeReceiptV1(StrictModel):
    """Sanitized evidence of one ``ProviderModeService.execute`` call (SPEC
    R9): digests, safe identifiers, mode, outcome/reason, exact counters -
    never facts, context, rule output, prompt, provider output, a
    credential, an authorization header, an endpoint query, or a raw
    exception. ``receipt_hash_sha256`` is independently recomputed by this
    model's own validator, so a forged/``model_construct``-bypassed hash is
    rejected here. ``ai_mode`` is restricted to :data:`VALID_RECEIPT_AI_MODES`
    (P4B-REV-F5), matching the published schema; every terminal ``outcome``
    requires an exact cross-field grammar so an impossible combination is
    rejected rather than merely Pydantic-valid while the schema disagreed."""

    request_id: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    request_digest: Digest
    output_schema_digest: Digest
    ruleset_digest: str = Field(default="", pattern=r"^$|^[0-9a-f]{64}$")
    output_digest: str = Field(default="", pattern=r"^$|^[0-9a-f]{64}$")
    ai_mode: str = Field(min_length=1)
    provider_id: str = Field(default="", max_length=200)
    model_id: str = Field(default="", max_length=200)
    rule_id: str = Field(default="", max_length=200)
    outcome: ProviderModeOutcome
    reason_code: str = Field(default="", max_length=64)
    rules_evaluated: Annotated[int, Field(ge=0)] = 0
    gateway_calls: Annotated[int, Field(ge=0, le=1)] = 0
    provider_attempts: Annotated[int, Field(ge=0, le=1)] = 0
    started_at: str = Field(min_length=1)
    finished_at: str = Field(min_length=1)
    receipt_hash_sha256: Digest

    @model_validator(mode="after")
    def _ai_mode_is_in_closed_vocabulary(self) -> "ProviderModeReceiptV1":
        if self.ai_mode not in VALID_RECEIPT_AI_MODES:
            raise ValueError(f"ai_mode must be one of {VALID_RECEIPT_AI_MODES}, matching the published schema")
        return self

    @model_validator(mode="after")
    def _counters_match_outcome(self) -> "ProviderModeReceiptV1":
        """P4B-REV-F5/F5-R1 exact cross-field grammar. The rule table itself
        lives in :func:`ai_providers.errors.assert_receipt_grammar` (a leaf
        module) to keep this model under the file-size guard; this validator
        is a thin field-forwarding call into it."""
        assert_receipt_grammar(
            outcome_value=self.outcome.value,
            ai_mode=self.ai_mode,
            provider_id=self.provider_id,
            model_id=self.model_id,
            rule_id=self.rule_id,
            output_digest=self.output_digest,
            ruleset_digest=self.ruleset_digest,
            rules_evaluated=self.rules_evaluated,
            gateway_calls=self.gateway_calls,
            provider_attempts=self.provider_attempts,
        )
        return self

    @model_validator(mode="after")
    def _hash_matches_canonical_body(self) -> "ProviderModeReceiptV1":
        dump = self.model_dump(mode="python")
        dump.pop("receipt_hash_sha256")
        if digest_of(dump) != self.receipt_hash_sha256:
            raise ValueError("receipt_hash_sha256 must equal the recomputed canonical receipt hash")
        return self


def build_receipt(**fields: Any) -> ProviderModeReceiptV1:
    """Build a :class:`ProviderModeReceiptV1` with its hash freshly computed
    (SPEC R9); the model's own validator independently re-verifies this."""
    dump_fields = dict(fields)
    dump_fields["receipt_hash_sha256"] = "0" * 64
    model = ProviderModeReceiptV1.model_construct(**dump_fields)
    dump = model.model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    final_fields = dict(fields)
    final_fields["receipt_hash_sha256"] = digest_of(dump)
    return ProviderModeReceiptV1(**final_fields)


_OUTPUTFUL_OUTCOMES = (ProviderModeOutcome.RULES_MATCHED, ProviderModeOutcome.EXTERNAL_ACCEPTED)


class ProviderModeResultV1(StrictModel):
    """P4B-REV-F2 - the strict envelope ``execute`` actually returns: the
    releasable ``output`` (only for :data:`_OUTPUTFUL_OUTCOMES`, never a
    partial/attempted value otherwise) alongside the sanitized
    :class:`ProviderModeReceiptV1`. Also proves ``output_digest``, when
    present, equals the digest of the actual ``output``."""

    output: dict[str, Any] | None
    receipt: ProviderModeReceiptV1

    @model_validator(mode="after")
    def _output_presence_matches_outcome(self) -> "ProviderModeResultV1":
        outcome = self.receipt.outcome
        if outcome in _OUTPUTFUL_OUTCOMES and self.output is None:
            raise ValueError(f"{outcome.value} requires a non-null output")
        if outcome not in _OUTPUTFUL_OUTCOMES and self.output is not None:
            raise ValueError(f"{outcome.value} must not carry an output body")
        return self

    @model_validator(mode="after")
    def _output_digest_matches_output_body(self) -> "ProviderModeResultV1":
        if self.output is not None and self.receipt.output_digest and digest_of(self.output) != self.receipt.output_digest:
            raise ValueError("receipt.output_digest must equal the digest of the actually-returned output")
        return self


def build_result(*, output: dict[str, Any] | None, receipt: ProviderModeReceiptV1) -> ProviderModeResultV1:
    """Deep-copy isolate ``output`` so the envelope never aliases internal
    rule-set/gateway-result state (SPEC R5/R9, P4B-REV-F2)."""
    isolated_output = copy.deepcopy(output) if output is not None else None
    return ProviderModeResultV1(output=isolated_output, receipt=receipt)


__all__ = [
    "MAX_JSON_DEPTH", "MAX_CONTAINER_ITEMS", "MAX_JSON_BYTES", "assert_bounded_json",
    "VALID_RECEIPT_AI_MODES", "canonical_receipt_ai_mode", "ProviderModeOutcome",
    "ProviderModeRequestV1", "RuleDefinitionV1", "MockAuthorizationV1", "ProviderKind",
    "ProviderMetadataV1", "ProviderModeReceiptV1", "build_receipt", "ProviderModeResultV1",
    "build_result",
]
