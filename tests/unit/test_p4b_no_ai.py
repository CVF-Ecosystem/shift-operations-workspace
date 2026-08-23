"""P4-B SPEC R3 - NO_AI is a zero-call refusal.

Proves ``evaluate_no_ai`` returns the fixed outcome with no way to pass in a
rule set or gateway, and that ``ProviderModeService.execute`` for NO_AI never
touches working rule/gateway dependencies supplied elsewhere on the service.
Also covers P4B-REV-F4.2's fail-closed guarantee for ``execute``'s top-level
request-digest step, which runs before any mode dispatch (including NO_AI),
and (P4B-REV-F5-R2) the complete receipt-grammar matrix - relocated here for
file-size budget, not because it is thematically NO_AI-specific.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from ai_providers.models import ProviderModeOutcome, ProviderModeRequestV1, RuleDefinitionV1, build_receipt
from ai_providers.no_ai import evaluate_no_ai
from ai_providers.rules_only import RuleSetV1
from ai_providers.service import ProviderModeService

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {"status": {"type": "string"}}}


class _NeverCalledGateway:
    async def execute(self, request):
        raise AssertionError("must never be called for a request-invalid case")


def test_evaluate_no_ai_returns_fixed_outcome():
    outcome, reason = evaluate_no_ai()
    assert outcome is ProviderModeOutcome.AI_MODE_DISABLED
    assert reason == ""


def test_evaluate_no_ai_takes_no_arguments():
    """Structural proof: the function signature has no rule-set or gateway
    parameter at all, so NO_AI cannot even be handed something to evaluate."""
    import inspect

    sig = inspect.signature(evaluate_no_ai)
    assert list(sig.parameters) == []


class _WorkingGateway:
    """A gateway that would succeed if ever called - NO_AI must never call
    it."""

    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, request):
        self.calls += 1
        raise AssertionError("NO_AI must never call the gateway")


def test_no_ai_ignores_working_rules_and_gateway_dependencies():
    """SPEC R3 - even when the service is constructed with a rule that
    WOULD match, and a gateway that WOULD succeed, a NO_AI request must
    still resolve to AI_MODE_DISABLED with zero rules/gateway/provider
    evaluation."""
    matching_rule = RuleDefinitionV1(
        rule_id="r1", task_type="t1", priority=1, required_facts={}, output={"status": "ok"}
    )
    rule_set = RuleSetV1((matching_rule,))
    gateway = _WorkingGateway()
    service = ProviderModeService(rule_set=rule_set, gateway=gateway)

    request = ProviderModeRequestV1(
        task_type="t1", ai_mode="NO_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="r1",
    )
    result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))

    assert result.receipt.outcome is ProviderModeOutcome.AI_MODE_DISABLED
    assert result.receipt.rules_evaluated == 0
    assert result.receipt.gateway_calls == 0
    assert result.receipt.provider_attempts == 0
    assert result.receipt.rule_id == ""
    assert result.receipt.output_digest == ""
    assert result.output is None
    assert gateway.calls == 0


def test_no_ai_receipt_has_no_provider_or_model_id():
    service = ProviderModeService(rule_set=RuleSetV1(()))
    request = ProviderModeRequestV1(
        task_type="t1", ai_mode="NO_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="r2",
    )
    result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
    assert result.receipt.provider_id == ""
    assert result.receipt.model_id == ""
    assert result.output is None


class TestFailClosedOnUnexpectedException:
    """P4B-REV-F4.2 - the reviewer's exact reproduction: a top-level
    constructed request containing a raw ``object()`` somewhere in its
    structure (reachable only via a model_construct bypass, since real
    ProviderModeRequestV1 construction already rejects non-JSON facts) must
    reach the typed REQUEST_INVALID terminal outcome, never an unhandled
    TypeError bubbling out of execute()."""

    def test_model_construct_bypassed_non_json_facts_is_request_invalid_not_a_raw_typeerror(self):
        bypassed = ProviderModeRequestV1.model_construct(
            task_type="t1", ai_mode="RULES_ONLY", facts={"x": object()}, output_schema=SCHEMA,
            nested_gateway_request=None, policy_version="v1", request_id="r1",
            provider_id="", model_id="", placement=None, context_digest=None,
        )
        service = ProviderModeService(rule_set=RuleSetV1(()), gateway=_NeverCalledGateway())
        result = asyncio.run(service.execute(request=bypassed, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.REQUEST_INVALID
        assert result.output is None
        assert (result.receipt.rules_evaluated, result.receipt.gateway_calls, result.receipt.provider_attempts) == (0, 0, 0)

    def test_model_construct_bypassed_tuple_facts_is_request_invalid_not_ai_mode_disabled(self):
        """P4B-REV-F4-R1 - the reviewer's exact reproduction: a
        model_construct-bypassed request with the JSON-invalid tuple
        facts={"x": (1, 2)} stayed "digestible" (json.dumps happily
        serializes a tuple as if it were a list) but was not genuinely
        valid, so round 1's digest-only guard let it fall through to
        AI_MODE_DISABLED instead of REQUEST_INVALID. The fix fully
        reconstructs/revalidates the whole request from its primitive dump
        before any mode dispatch, so this must now be caught here too."""
        bypassed = ProviderModeRequestV1.model_construct(
            task_type="t1", ai_mode="NO_AI", facts={"x": (1, 2)}, output_schema=SCHEMA,
            nested_gateway_request=None, policy_version="v1", request_id="r1",
            provider_id="", model_id="", placement=None, context_digest=None,
        )
        service = ProviderModeService(rule_set=RuleSetV1(()), gateway=_NeverCalledGateway())
        result = asyncio.run(service.execute(request=bypassed, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.REQUEST_INVALID
        assert result.receipt.ai_mode == "UNKNOWN"
        assert result.output is None
        assert (result.receipt.rules_evaluated, result.receipt.gateway_calls, result.receipt.provider_attempts) == (0, 0, 0)


_DIGEST = "d" * 64
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "packages" / "ai-providers" / "contracts" / "provider_modes.schema.json"


def _grammar_receipt(**overrides):
    base = dict(
        request_id="r1", policy_version="v1", request_digest=_DIGEST, output_schema_digest=_DIGEST,
        ai_mode="NO_AI", outcome=ProviderModeOutcome.AI_MODE_DISABLED,
        started_at="t0", finished_at="t1",
    )
    base.update(overrides)
    return build_receipt(**base)


_F5R2_CASES = [
    ("mismatch_output_digest", dict(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH), "output_digest", _DIGEST),
    ("mismatch_rule_facts", dict(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH), "rules_evaluated", 7),
    ("accepted_rule_facts", dict(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_ACCEPTED, provider_id="p1", model_id="m1", output_digest=_DIGEST, gateway_calls=1, provider_attempts=1), "rules_evaluated", 3),
    ("not_accepted_output_digest", dict(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED, provider_id="p1", model_id="m1", gateway_calls=1), "output_digest", _DIGEST),
    ("no_match_missing_ruleset_digest", dict(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_NO_MATCH, ruleset_digest=_DIGEST, rules_evaluated=1), "ruleset_digest", ""),
    ("schema_invalid_missing_ruleset_digest", dict(ai_mode="RULES_ONLY", outcome=ProviderModeOutcome.RULES_SCHEMA_INVALID, rule_id="r1", ruleset_digest=_DIGEST, rules_evaluated=1), "ruleset_digest", ""),
    # P4B-REV-F5-R3 (Amendment 2): otherwise-valid EXTERNAL_ACCEPTED with
    # provider_attempts=0 must be rejected by both layers. EXTERNAL_NOT_ACCEPTED
    # deliberately stays untightened - see TestExternalNotAcceptedAllowsEitherProviderAttempts.
    ("accepted_zero_provider_attempts", dict(ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_ACCEPTED, provider_id="p1", model_id="m1", output_digest=_DIGEST, gateway_calls=1, provider_attempts=1), "provider_attempts", 0),
]


class TestF5R2CompleteGrammarMatrix:
    """P4B-REV-F5-R2/F5-R3 - reviewer-reproduced impossible shapes, each
    rejected by BOTH the general Pydantic grammar
    (``ai_providers.errors.assert_receipt_grammar``) AND the mirrored Draft
    2020-12 schema conditionals - not merely one layer. Relocated here (not
    test_p4b_provider_modes_schema.py) for file-size budget only."""

    @pytest.fixture(scope="class")
    @staticmethod
    def schema():
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("name,base,field,bad", _F5R2_CASES, ids=[c[0] for c in _F5R2_CASES])
    def test_shape_rejected_by_pydantic(self, name, base, field, bad):
        with pytest.raises(Exception):
            _grammar_receipt(**{**base, field: bad})

    @pytest.mark.parametrize("name,base,field,bad", _F5R2_CASES, ids=[c[0] for c in _F5R2_CASES])
    def test_shape_rejected_by_schema(self, schema, name, base, field, bad):
        jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")
        payload = json.loads(_grammar_receipt(**base).model_dump_json())
        payload[field] = bad
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)


class TestF5R3AcceptedProviderAttemptsExact:
    """P4B-REV-F5-R3 (Amendment 2) - EXTERNAL_ACCEPTED requires exactly one
    provider attempt; EXTERNAL_NOT_ACCEPTED deliberately stays untightened
    since P4-A may refuse before or after the physical attempt."""

    _ACCEPTED_BASE = dict(
        ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_ACCEPTED,
        provider_id="p1", model_id="m1", output_digest=_DIGEST, gateway_calls=1,
    )

    def test_accepted_with_one_provider_attempt_is_valid(self):
        jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        receipt = _grammar_receipt(**self._ACCEPTED_BASE, provider_attempts=1)
        jsonschema.validate(json.loads(receipt.model_dump_json()), schema)

    @pytest.mark.parametrize("provider_attempts", [0, 1])
    def test_not_accepted_permits_either_provider_attempts(self, provider_attempts):
        _grammar_receipt(
            ai_mode="EXTERNAL_AI", outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
            provider_id="p1", model_id="m1", gateway_calls=1, provider_attempts=provider_attempts,
        )
