"""P4-B SPEC R4/R5 - deterministic local RULES_ONLY evaluation.

Covers construction-time ambiguity rejection, deterministic winner order,
exact-scalar fact matching, deep-copy output isolation, real schema
validation, the RULES_SCHEMA_INVALID never-falls-through guarantee, and
(P4B-REV-F2) both the service-level and model-level ProviderModeResultV1
envelope proofs.
"""

from __future__ import annotations

import asyncio

import pytest
from ai_gateway.models import digest_of
from pydantic import ValidationError

from ai_providers.errors import AmbiguousRuleSignatureError, DuplicateRuleIdError
from ai_providers.models import (
    ProviderModeOutcome,
    ProviderModeReceiptV1,
    ProviderModeRequestV1,
    ProviderModeResultV1,
    RuleDefinitionV1,
    build_receipt,
    build_result,
)
from ai_providers.rules_only import RuleSetV1, evaluate_rules, select_winner
from ai_providers.service import ProviderModeService

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["status"], "properties": {"status": {"type": "string"}}}


def _rule(rule_id, task_type="t1", priority=1, required_facts=None, output=None) -> RuleDefinitionV1:
    return RuleDefinitionV1(
        rule_id=rule_id, task_type=task_type, priority=priority,
        required_facts=required_facts or {}, output=output if output is not None else {"status": "ok"},
    )


class TestRuleSetConstruction:
    def test_duplicate_rule_id_rejected_at_construction(self):
        with pytest.raises(DuplicateRuleIdError):
            RuleSetV1((_rule("r1"), _rule("r1", priority=2)))

    def test_duplicate_signature_rejected_at_construction(self):
        with pytest.raises(AmbiguousRuleSignatureError):
            RuleSetV1((
                _rule("r1", required_facts={"x": 1}),
                _rule("r2", required_facts={"x": 1}),
            ))

    def test_same_task_different_priority_is_allowed(self):
        rs = RuleSetV1((_rule("r1", priority=1), _rule("r2", priority=2)))
        assert len(rs.rules) == 2

    def test_same_priority_different_facts_is_allowed(self):
        rs = RuleSetV1((
            _rule("r1", required_facts={"x": 1}),
            _rule("r2", required_facts={"x": 2}),
        ))
        assert len(rs.rules) == 2

    def test_empty_rule_set_is_valid(self):
        assert RuleSetV1(()).rules == ()


class TestWinnerSelection:
    def test_highest_priority_wins(self):
        low = _rule("low", priority=1)
        high = _rule("high", priority=5)
        rs = RuleSetV1((low, high))
        winner = select_winner(rs, task_type="t1", facts={})
        assert winner.rule_id == "high"

    def test_tie_broken_by_rule_id_ascending(self):
        """Two distinct-signature rules (different required_facts, so
        construction is unambiguous) that both happen to match the same
        facts dict at the same priority - the lower rule_id wins."""
        rb = _rule("rb", priority=1, required_facts={"a": 1})
        ra = _rule("ra", priority=1, required_facts={"b": 2})
        rs = RuleSetV1((rb, ra))
        winner = select_winner(rs, task_type="t1", facts={"a": 1, "b": 2})
        assert winner.rule_id == "ra"

    def test_exact_scalar_fact_match_required(self):
        rule = _rule("r1", required_facts={"x": 1})
        rs = RuleSetV1((rule,))
        assert select_winner(rs, task_type="t1", facts={"x": 1}) is not None
        assert select_winner(rs, task_type="t1", facts={"x": 2}) is None
        assert select_winner(rs, task_type="t1", facts={}) is None

    def test_extra_facts_do_not_prevent_match(self):
        rule = _rule("r1", required_facts={"x": 1})
        rs = RuleSetV1((rule,))
        assert select_winner(rs, task_type="t1", facts={"x": 1, "y": 99}) is not None

    def test_no_match_returns_none(self):
        rs = RuleSetV1((_rule("r1", task_type="other"),))
        assert select_winner(rs, task_type="t1", facts={}) is None

    def test_string_vs_int_fact_does_not_coerce_match(self):
        rule = _rule("r1", required_facts={"x": 1})
        rs = RuleSetV1((rule,))
        assert select_winner(rs, task_type="t1", facts={"x": "1"}) is None


class TestEvaluateRules:
    def test_matched_output_is_deep_copy_isolated(self):
        nested_schema = {
            "type": "object", "additionalProperties": False, "required": ["status"],
            "properties": {"status": {"type": "string"}, "nested": {"type": "object"}},
        }
        original_output = {"status": "ok", "nested": {"a": 1}}
        rule = _rule("r1", output=original_output)
        rs = RuleSetV1((rule,))
        outcome, rule_id, winner, output = evaluate_rules(
            rs, task_type="t1", facts={}, output_schema=nested_schema
        )
        assert outcome is ProviderModeOutcome.RULES_MATCHED
        output["nested"]["a"] = 999
        assert winner.output["nested"]["a"] == 1  # rule's own output untouched
        assert original_output["nested"]["a"] == 1

    def test_no_match_outcome(self):
        rs = RuleSetV1((_rule("r1", task_type="other"),))
        outcome, rule_id, winner, output = evaluate_rules(
            rs, task_type="t1", facts={}, output_schema=SCHEMA
        )
        assert outcome is ProviderModeOutcome.RULES_NO_MATCH
        assert rule_id == ""
        assert winner is None
        assert output is None

    def test_schema_invalid_output_never_falls_through(self):
        bad_rule = _rule("r1", output={"wrong_key": "value"})
        rs = RuleSetV1((bad_rule,))
        outcome, rule_id, winner, output = evaluate_rules(
            rs, task_type="t1", facts={}, output_schema=SCHEMA
        )
        assert outcome is ProviderModeOutcome.RULES_SCHEMA_INVALID
        assert rule_id == "r1"
        assert output is None


class _GuardGateway:
    async def execute(self, request):
        raise AssertionError("RULES_ONLY must never call the gateway")


class TestServiceIntegration:
    def test_rules_only_never_calls_gateway(self):
        matching_rule = _rule("r1")
        rs = RuleSetV1((matching_rule,))
        gateway = _GuardGateway()
        service = ProviderModeService(rule_set=rs, gateway=gateway)
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.RULES_MATCHED
        assert result.receipt.gateway_calls == 0
        assert result.receipt.provider_attempts == 0
        assert result.output == {"status": "ok"}

    def test_rules_evaluated_counter_reflects_rule_set_size(self):
        rs = RuleSetV1((_rule("r1"), _rule("r2", task_type="other")))
        service = ProviderModeService(rule_set=rs)
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.rules_evaluated == 2

    def test_schema_invalid_receipt_has_zero_gateway_calls(self):
        bad_rule = _rule("r1", output={"wrong_key": "value"})
        rs = RuleSetV1((bad_rule,))
        service = ProviderModeService(rule_set=rs, gateway=_GuardGateway())
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.RULES_SCHEMA_INVALID
        assert result.receipt.gateway_calls == 0
        assert result.receipt.provider_attempts == 0
        assert result.output is None

    def test_output_digest_in_receipt_matches_returned_output(self):
        """P4B-REV-F2 - the receipt's own output_digest must equal a hash of
        the actually-returned output body; they can never silently diverge."""
        rs = RuleSetV1((_rule("r1"),))
        service = ProviderModeService(rule_set=rs)
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.RULES_MATCHED
        assert digest_of(result.output) == result.receipt.output_digest

    def test_rules_only_output_is_isolated_from_internal_ruleset_state(self):
        """P4B-REV-F2 - mutating the returned output must never mutate the
        rule's own stored output (no aliasing back to internal state)."""
        rule = _rule("r1", output={"status": "ok", "nested": {"a": 1}})
        rs = RuleSetV1((rule,))
        service = ProviderModeService(rule_set=rs)
        nested_schema = {
            "type": "object", "additionalProperties": False, "required": ["status"],
            "properties": {"status": {"type": "string"}, "nested": {"type": "object"}},
        }
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=nested_schema,
            policy_version="v1", request_id="r1",
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        result.output["nested"]["a"] = 999
        rule_again = rs.rules[0]
        assert rule_again.output["nested"]["a"] == 1


class TestProviderModeResultV1:
    """P4B-REV-F2 - the strict envelope: output presence is strictly bound
    to terminal outcome, and output_digest must equal a hash of the actual
    output body."""

    def _receipt(self, **overrides) -> ProviderModeReceiptV1:
        fields = dict(
            request_id="r1", policy_version="v1", request_digest="a" * 64,
            output_schema_digest="b" * 64, ai_mode="RULES_ONLY",
            outcome=ProviderModeOutcome.RULES_MATCHED, rule_id="r1",
            output_digest=digest_of({"status": "ok"}), ruleset_digest="d" * 64,
            rules_evaluated=1, started_at="t0", finished_at="t1",
        )
        fields.update(overrides)
        return build_receipt(**fields)

    def test_rules_matched_requires_non_null_output(self):
        receipt = self._receipt()
        with pytest.raises(ValidationError):
            ProviderModeResultV1(output=None, receipt=receipt)

    def test_rules_matched_accepts_matching_output(self):
        receipt = self._receipt()
        result = ProviderModeResultV1(output={"status": "ok"}, receipt=receipt)
        assert result.output == {"status": "ok"}

    def test_refusal_outcome_forbids_output_body(self):
        """A refusal/non-accepted outcome must never carry even a partial
        output - not the winning rule's output, not an attempted value."""
        receipt = build_receipt(
            request_id="r1", policy_version="v1", request_digest="a" * 64,
            output_schema_digest="b" * 64, ai_mode="RULES_ONLY",
            outcome=ProviderModeOutcome.RULES_NO_MATCH, ruleset_digest="c" * 64,
            rules_evaluated=1, started_at="t0", finished_at="t1",
        )
        with pytest.raises(ValidationError):
            ProviderModeResultV1(output={"status": "ok"}, receipt=receipt)

    def test_output_digest_mismatch_is_rejected(self):
        """The receipt's own output_digest must match a hash of the
        actually-returned output - they can never silently diverge."""
        receipt = self._receipt(output_digest="f" * 64)
        with pytest.raises(ValidationError):
            ProviderModeResultV1(output={"status": "ok"}, receipt=receipt)

    def test_build_result_deep_copy_isolates_output(self):
        source = {"status": "ok", "nested": {"a": 1}}
        receipt = self._receipt(output_digest=digest_of(source))
        result = build_result(output=source, receipt=receipt)
        source["nested"]["a"] = 999
        assert result.output["nested"]["a"] == 1

    def test_is_frozen(self):
        receipt = self._receipt()
        result = ProviderModeResultV1(output={"status": "ok"}, receipt=receipt)
        with pytest.raises(ValidationError):
            result.output = None
