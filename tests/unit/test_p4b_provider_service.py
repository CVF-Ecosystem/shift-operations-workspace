"""P4-B SPEC R2/R6 - ProviderModeService.execute is the sole entry point.

Covers unknown-mode refusal, exact-order execution, EXTERNAL_AI identity
binding/mismatch (zero-call, P4B-REV-F3), at-most-once gateway dispatch,
gateway exception/timeout handling, exact per-mode counters, the
P4B-REV-F2 result envelope, and (P4B-REV-F5-R2) real-emitted-shape grammar
proof. Registry-load-bearing (F1) coverage lives in
test_p4b_provider_registry.py; F4.2's test lives in test_p4b_no_ai.py.
"""

from __future__ import annotations

import asyncio

import pytest
from ai_gateway.models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    FinalOutcome,
    GatewayReceipt,
    GatewayRequest,
    GatewayResult,
    Placement,
    TerminationFacts,
    digest_of,
)

from ai_providers.models import ProviderKind, ProviderMetadataV1, ProviderModeOutcome, ProviderModeRequestV1
from ai_providers.registry import ProviderAdapterRegistry
from ai_providers.rules_only import RuleSetV1
from ai_providers.service import ProviderModeService

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["status"], "properties": {"status": {"type": "string"}}}
_CTX_FACTS = ContextFacts(
    classification=Classification.PUBLIC, redaction_applied=True, minimization_proven=True,
    evidence_count=1, estimated_input_tokens=10, context_digest=digest_of({}),
)
_BUDGET_FACTS = BudgetFacts(
    per_request_token_limit=1000, daily_budget_usd_millis=0, monthly_budget_usd_millis=0,
    spent_today_usd_millis=0, spent_month_usd_millis=0, estimated_cost_usd_millis=0,
)


def _gateway_request(**overrides) -> GatewayRequest:
    fields = dict(
        task_type="t1", ai_mode=AIMode.EXTERNAL_AI, provider_id="p1", model_id="m1",
        placement=Placement.LOCAL, context={}, output_schema=SCHEMA,
        context_facts=_CTX_FACTS, budget_facts=_BUDGET_FACTS, termination_facts=TerminationFacts(),
    )
    fields.update(overrides)
    return GatewayRequest(**fields)


def _external_request(gateway_request: GatewayRequest, **overrides) -> ProviderModeRequestV1:
    fields = dict(
        task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="r1",
        nested_gateway_request=gateway_request.model_dump(mode="python"),
        provider_id=gateway_request.provider_id, model_id=gateway_request.model_id,
        placement=gateway_request.placement, context_digest=gateway_request.context_facts.context_digest,
    )
    fields.update(overrides)
    return ProviderModeRequestV1(**fields)


def _registry_with(provider_id: str = "p1", model_id: str = "m1", *, placement: Placement = Placement.LOCAL) -> ProviderAdapterRegistry:
    registry = ProviderAdapterRegistry()
    registry.register(ProviderMetadataV1(
        provider_id=provider_id, kind=ProviderKind.EXTERNAL_GATEWAY, placement=placement,
        model_ids=(model_id,), evidence_eligible=True,
    ))
    return registry


class _AcceptingGateway:
    def __init__(self) -> None:
        self.calls = 0
        self.received: GatewayRequest | None = None

    async def execute(self, request: GatewayRequest) -> GatewayResult:
        self.calls += 1
        self.received = request
        receipt = GatewayReceipt(
            task_type=request.task_type, provider_id=request.provider_id, model_id=request.model_id,
            ai_mode=request.ai_mode, classification=request.context_facts.classification,
            placement=request.placement, request_digest="a" * 64, context_digest="b" * 64,
            output_schema_digest="c" * 64, output_digest="d" * 64, gates=(),
            final_outcome=FinalOutcome.ACCEPTED, reserved_tokens=0, reserved_cost_usd_millis=0,
            actual_tokens=1, actual_cost_usd_millis=0, usage_committed=True, provider_attempts=1,
            started_at="a", finished_at="b",
        )
        return GatewayResult(accepted=True, output={"status": "ok"}, receipt=receipt)


class _RefusingGateway:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, request: GatewayRequest) -> GatewayResult:
        self.calls += 1
        receipt = GatewayReceipt(
            task_type=request.task_type, provider_id=request.provider_id, model_id=request.model_id,
            ai_mode=request.ai_mode, classification=request.context_facts.classification,
            placement=request.placement, request_digest="a" * 64, context_digest="b" * 64,
            output_schema_digest="c" * 64, gates=(), final_outcome=FinalOutcome.REFUSED_PRE_DISPATCH,
            reason_code="BUDGET_UNAVAILABLE", provider_attempts=0, started_at="a", finished_at="b",
        )
        return GatewayResult(accepted=False, output=None, receipt=receipt)


class _NeverCalledGateway:
    async def execute(self, request):
        raise AssertionError("must never be called for a mismatch/refusal case")


class TestUnknownMode:
    def test_unknown_mode_string_is_refused_zero_call(self):
        service = ProviderModeService(rule_set=RuleSetV1(()), gateway=_NeverCalledGateway())
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="TOTALLY_UNKNOWN_MODE", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.output is None
        assert result.receipt.outcome is ProviderModeOutcome.REQUEST_INVALID
        assert result.receipt.ai_mode == "UNKNOWN"
        assert (result.receipt.rules_evaluated, result.receipt.gateway_calls, result.receipt.provider_attempts) == (0, 0, 0)


class TestExternalIdentityBinding:
    def test_matching_nested_request_is_accepted_and_dispatches_once(self):
        gw_req = _gateway_request()
        gateway = _AcceptingGateway()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(gw_req)
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_ACCEPTED
        assert gateway.calls == 1
        assert result.receipt.gateway_calls == 1
        assert result.receipt.provider_attempts == 1
        assert result.output == {"status": "ok"}

    def test_missing_nested_request_is_zero_call_refusal(self):
        gateway = _NeverCalledGateway()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1", nested_gateway_request=None,
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.gateway_calls == 0
        assert result.receipt.provider_attempts == 0
        assert result.output is None

    def test_malformed_nested_request_is_zero_call_refusal(self):
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=_NeverCalledGateway())
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1", nested_gateway_request={"not": "a valid gateway request"},
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.gateway_calls == 0

    def test_no_gateway_injected_is_zero_call_refusal(self):
        gw_req = _gateway_request()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=None)
        request = _external_request(gw_req)
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "NO_GATEWAY_INJECTED"

    _DIFF_SCHEMA = {
        "type": "object", "additionalProperties": False,
        "required": ["other"], "properties": {"other": {"type": "string"}},
    }

    @pytest.mark.parametrize(
        "gw_override,outer_override,expected_reason",
        [
            ({"task_type": "different_task"}, {}, "TASK_TYPE_MISMATCH"),
            ({"output_schema": _DIFF_SCHEMA}, {"output_schema": SCHEMA}, "OUTPUT_SCHEMA_MISMATCH"),
            ({}, {"provider_id": "different-provider"}, "PROVIDER_ID_MISMATCH"),
            ({}, {"model_id": "different-model"}, "MODEL_ID_MISMATCH"),
            ({}, {"placement": Placement.EXTERNAL}, "PLACEMENT_MISMATCH"),
            ({}, {"context_digest": "f" * 64}, "CONTEXT_DIGEST_MISMATCH"),
        ],
        ids=["task_type", "output_schema", "provider_id", "model_id", "placement", "context_digest"],
    )
    def test_identity_binding_fact_mismatch_is_zero_call_refusal(self, gw_override, outer_override, expected_reason):
        """P4B-REV-F3 - every nested/outer task_type/output_schema/provider_
        id/model_id/placement/context_digest must agree; any single
        disagreement is a zero-call refusal even though the rest of the
        request is otherwise entirely valid and registered."""
        gw_req = _gateway_request(**gw_override)
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=_NeverCalledGateway())
        request = _external_request(gw_req, **outer_override)
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == expected_reason
        assert result.receipt.gateway_calls == 0

    def test_outer_binding_facts_missing_entirely_is_zero_call_refusal(self):
        """A caller cannot satisfy SPEC R6 by supplying only a nested
        GatewayRequest without also declaring the outer provider/model/
        placement/context_digest facts - omission is itself a mismatch."""
        gw_req = _gateway_request()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=_NeverCalledGateway())
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
            nested_gateway_request=gw_req.model_dump(mode="python"),
        )
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "PROVIDER_ID_MISMATCH"
        assert result.receipt.gateway_calls == 0


class TestGatewayNotAccepted:
    def test_gateway_refusal_is_preserved_without_retry(self):
        gw_req = _gateway_request()
        gateway = _RefusingGateway()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(gw_req)
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED
        assert result.receipt.reason_code == "BUDGET_UNAVAILABLE"
        assert gateway.calls == 1  # exactly one attempt, never retried
        assert result.receipt.gateway_calls == 1
        assert result.receipt.provider_attempts == 0
        assert result.output is None


class TestGatewayExceptionHandling:
    def test_gateway_raising_propagates_and_service_makes_no_second_call(self):
        """The service does not swallow a raised exception into a fake
        success/fallback (no fail-open); it also never calls the gateway a
        second time to recover."""

        class _RaisingGateway:
            def __init__(self) -> None:
                self.calls = 0

            async def execute(self, request):
                self.calls += 1
                raise TimeoutError("simulated provider timeout")

        gw_req = _gateway_request()
        gateway = _RaisingGateway()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(gw_req)
        with pytest.raises(TimeoutError):
            asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert gateway.calls == 1


class TestNeverCallsProviderDirectly:
    def test_service_module_never_imports_or_calls_ai_provider_protocol(self):
        import ast
        from pathlib import Path

        import ai_providers.service as module

        path = Path(module.__file__)
        text = path.read_text(encoding="utf-8")
        assert "provider.generate_structured_output" not in text
        tree = ast.parse(text, filename=str(path))
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported_names.update(a.name for a in node.names)
        assert "AIProvider" not in imported_names


class TestRealExternalReceiptsSatisfyGrammar:
    """P4B-REV-F5-R2 - every receipt below is from a real ``execute()``
    call, never hand-constructed; the grammar must never reject it."""

    def _run(self, gateway, **override):
        svc = ProviderModeService(rule_set=RuleSetV1(()), registry=_registry_with(), gateway=gateway)
        req = _external_request(_gateway_request(**override))
        return asyncio.run(svc.execute(request=req, started_at="t0", finished_at="t1")).receipt

    def test_real_accepted_not_accepted_and_mismatch_receipts_carry_zero_rule_facts(self):
        receipts = [self._run(_AcceptingGateway()), self._run(_RefusingGateway()), self._run(_NeverCalledGateway(), task_type="x")]
        for receipt in receipts:
            assert (receipt.rules_evaluated, receipt.rule_id, receipt.ruleset_digest) == (0, "", "")
