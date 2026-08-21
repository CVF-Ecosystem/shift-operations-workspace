"""P4-A SPEC R2 - strict contract models.

NOT GOVERNANCE PROOF: these are mechanical contract tests. Every governance
claim in R3-R9 requires the fresh live run described in R13.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_gateway.models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    FinalOutcome,
    GateOutcome,
    GateRecord,
    GatewayReceipt,
    GatewayRequest,
    GatewayResult,
    Placement,
    ProviderRequest,
    ProviderResult,
    TerminationFacts,
    canonical_json,
    digest_of,
)

DIGEST = "0" * 64
SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}


def _context_facts(**overrides) -> ContextFacts:
    base = dict(
        classification=Classification.PUBLIC,
        redaction_applied=True,
        minimization_proven=False,
        evidence_count=1,
        estimated_input_tokens=10,
        context_digest=DIGEST,
    )
    base.update(overrides)
    return ContextFacts(**base)


def _budget_facts(**overrides) -> BudgetFacts:
    base = dict(
        per_request_token_limit=1000,
        daily_budget_usd_millis=1000,
        monthly_budget_usd_millis=10000,
        spent_today_usd_millis=0,
        spent_month_usd_millis=0,
        estimated_cost_usd_millis=1,
    )
    base.update(overrides)
    return BudgetFacts(**base)


def _receipt(**overrides) -> GatewayReceipt:
    base = dict(
        task_type="canary",
        provider_id="p",
        model_id="m",
        ai_mode=AIMode.EXTERNAL_AI,
        classification=Classification.PUBLIC,
        placement=Placement.EXTERNAL,
        request_digest=DIGEST,
        context_digest=DIGEST,
        output_schema_digest=DIGEST,
        gates=(GateRecord(gate="g", outcome=GateOutcome.PASS),),
        final_outcome=FinalOutcome.REFUSED_PRE_DISPATCH,
        started_at="2026-08-20T00:00:00+00:00",
        finished_at="2026-08-20T00:00:01+00:00",
    )
    base.update(overrides)
    return GatewayReceipt(**base)


class TestStrictness:
    def test_unknown_field_rejected(self):
        with pytest.raises(ValidationError):
            _context_facts(surprise="x")

    def test_models_are_frozen(self):
        facts = _context_facts()
        with pytest.raises(ValidationError):
            facts.evidence_count = 5

    def test_strict_mode_rejects_coercion(self):
        # Strict mode: the string "1" must not silently become int 1.
        with pytest.raises(ValidationError):
            _context_facts(evidence_count="1")

    def test_negative_counts_rejected(self):
        with pytest.raises(ValidationError):
            _context_facts(evidence_count=-1)

    def test_digest_pattern_enforced(self):
        with pytest.raises(ValidationError):
            _context_facts(context_digest="not-a-digest")

    def test_provider_result_usage_default_is_not_shared(self):
        """Mutable defaults are forbidden (R2): each instance owns its dict."""
        first = ProviderResult(output={}, provider_id="p", model_id="m")
        second = ProviderResult(output={}, provider_id="p", model_id="m")
        assert first.usage == {} and second.usage == {}
        assert first.usage is not second.usage


class TestGatewayRequest:
    def test_output_schema_must_be_object(self):
        with pytest.raises(ValidationError):
            GatewayRequest(
                task_type="t",
                ai_mode=AIMode.EXTERNAL_AI,
                provider_id="p",
                model_id="m",
                placement=Placement.EXTERNAL,
                context={},
                output_schema={"type": "string"},
                context_facts=_context_facts(),
                budget_facts=_budget_facts(),
                termination_facts=TerminationFacts(),
            )

    def test_valid_request_constructs(self):
        request = GatewayRequest(
            task_type="t",
            ai_mode=AIMode.EXTERNAL_AI,
            provider_id="p",
            model_id="m",
            placement=Placement.EXTERNAL,
            context={},
            output_schema=SCHEMA,
            context_facts=_context_facts(),
            budget_facts=_budget_facts(),
            termination_facts=TerminationFacts(),
        )
        assert request.timeout_seconds == 30


class TestReceiptInvariants:
    def test_accepted_requires_one_attempt_and_output(self):
        with pytest.raises(ValidationError):
            _receipt(final_outcome=FinalOutcome.ACCEPTED, provider_attempts=0)

    def test_accepted_requires_committed_usage(self):
        with pytest.raises(ValidationError):
            _receipt(
                final_outcome=FinalOutcome.ACCEPTED,
                provider_attempts=1,
                output_digest=DIGEST,
                usage_committed=False,
            )

    def test_pre_dispatch_refusal_requires_zero_attempts(self):
        with pytest.raises(ValidationError):
            _receipt(final_outcome=FinalOutcome.REFUSED_PRE_DISPATCH, provider_attempts=1)

    def test_attempts_capped_at_one(self):
        with pytest.raises(ValidationError):
            _receipt(provider_attempts=2)

    def test_commit_and_release_are_mutually_exclusive(self):
        with pytest.raises(ValidationError):
            _receipt(usage_committed=True, reservation_released=True)

    def test_accepted_receipt_is_valid(self):
        receipt = _receipt(
            final_outcome=FinalOutcome.ACCEPTED,
            provider_attempts=1,
            output_digest=DIGEST,
            usage_committed=True,
        )
        assert receipt.final_outcome is FinalOutcome.ACCEPTED


class TestGatewayResult:
    def test_accepted_flag_must_match_receipt(self):
        with pytest.raises(ValidationError):
            GatewayResult(accepted=True, output={"ok": True}, receipt=_receipt())

    def test_non_accepted_must_not_carry_output(self):
        with pytest.raises(ValidationError):
            GatewayResult(accepted=False, output={"ok": True}, receipt=_receipt())


class TestDigests:
    def test_canonical_json_is_key_order_independent(self):
        assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})

    def test_digest_is_stable_and_hex64(self):
        value = {"a": [1, 2], "b": "x"}
        first, second = digest_of(value), digest_of(value)
        assert first == second and len(first) == 64
        assert all(character in "0123456789abcdef" for character in first)

    def test_digest_changes_with_content(self):
        assert digest_of({"a": 1}) != digest_of({"a": 2})


class TestProviderRequest:
    def test_timeout_bounds_enforced(self):
        with pytest.raises(ValidationError):
            ProviderRequest(
                task_type="t", model_id="m", context={}, output_schema=SCHEMA, timeout_seconds=0
            )
