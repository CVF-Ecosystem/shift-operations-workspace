"""P4-B SPEC R10 - build_provider_mode_service application composition
integration.

Exercises the real composition function with a real immutable RuleSetV1 and
a real ai_gateway.service.AIGateway (registry + usage ledger), backed by a
fake in-process provider adapter (mechanics only, not governance proof).
Proves the composition opens no route, persists nothing, and produces a real
end-to-end EXTERNAL_ACCEPTED outcome with exactly one gateway/provider call.
"""

from __future__ import annotations

import asyncio

from ai_gateway.models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    GatewayRequest,
    Placement,
    ProviderRequest,
    ProviderResult,
    TerminationFacts,
    digest_of,
)
from ai_gateway.registry import ProviderRegistry
from ai_gateway.service import AIGateway
from ai_gateway.usage import UsageLedger

from ai_providers.models import (
    ProviderKind,
    ProviderMetadataV1,
    ProviderModeOutcome,
    ProviderModeRequestV1,
    RuleDefinitionV1,
)
from ai_providers.registry import ProviderAdapterRegistry
from ai_providers.rules_only import RuleSetV1
from workspace_api.application.ai_provider_modes import build_provider_mode_service

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["status"], "properties": {"status": {"type": "string"}}}


class _FakeAcceptingProvider:
    provider_id = "test_provider"

    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        self.calls += 1
        return ProviderResult(
            output={"status": "ok"}, provider_id=self.provider_id, model_id=request.model_id,
            usage={"total_tokens": 5, "cost_usd_millis": 0},
        )

    async def health_check(self) -> dict:
        return {}

    async def cancel_request(self, request_id: str) -> None:
        return None


def _real_gateway(provider) -> AIGateway:
    registry = ProviderRegistry()
    registry.register(provider, ("m1",), placement=Placement.LOCAL)
    return AIGateway(registry, UsageLedger(), endpoint_origin="https://example.invalid")


def _p4b_registry(provider_id: str = "test_provider", model_id: str = "m1") -> ProviderAdapterRegistry:
    registry = ProviderAdapterRegistry()
    registry.register(
        ProviderMetadataV1(
            provider_id=provider_id, kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.LOCAL,
            model_ids=(model_id,), evidence_eligible=True,
        )
    )
    return registry


def _gateway_request() -> GatewayRequest:
    context_facts = ContextFacts(
        classification=Classification.PUBLIC, redaction_applied=True, minimization_proven=True,
        evidence_count=1, estimated_input_tokens=5, context_digest=digest_of({}),
    )
    budget_facts = BudgetFacts(
        per_request_token_limit=1000, daily_budget_usd_millis=0, monthly_budget_usd_millis=0,
        spent_today_usd_millis=0, spent_month_usd_millis=0, estimated_cost_usd_millis=0,
    )
    return GatewayRequest(
        task_type="t1", ai_mode=AIMode.EXTERNAL_AI, provider_id="test_provider", model_id="m1",
        placement=Placement.LOCAL, context={}, output_schema=SCHEMA,
        context_facts=context_facts, budget_facts=budget_facts, termination_facts=TerminationFacts(),
    )


def test_composition_builds_service_that_dispatches_real_gateway_once():
    provider = _FakeAcceptingProvider()
    gateway = _real_gateway(provider)
    registry = _p4b_registry()
    service = build_provider_mode_service(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)

    gw_req = _gateway_request()
    request = ProviderModeRequestV1(
        task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="req-1", nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )
    result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))

    assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_ACCEPTED
    assert provider.calls == 1
    assert gateway.physical_attempts == 1
    assert result.receipt.gateway_calls == 1
    assert result.receipt.provider_attempts == 1
    assert result.output == {"status": "ok"}


def test_composition_with_rules_only_never_touches_injected_gateway():
    provider = _FakeAcceptingProvider()
    gateway = _real_gateway(provider)
    rule = RuleDefinitionV1(
        rule_id="r1", task_type="t1", priority=1, required_facts={}, output={"status": "ok"}
    )
    service = build_provider_mode_service(rule_set=RuleSetV1((rule,)), gateway=gateway)

    request = ProviderModeRequestV1(
        task_type="t1", ai_mode="RULES_ONLY", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="req-2",
    )
    result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))

    assert result.receipt.outcome is ProviderModeOutcome.RULES_MATCHED
    assert provider.calls == 0
    assert gateway.physical_attempts == 0
    assert result.output == {"status": "ok"}


def test_composition_without_gateway_still_supports_no_ai_and_rules_only():
    service = build_provider_mode_service(rule_set=RuleSetV1(()), gateway=None)
    request = ProviderModeRequestV1(
        task_type="t1", ai_mode="NO_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="req-3",
    )
    result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
    assert result.receipt.outcome is ProviderModeOutcome.AI_MODE_DISABLED


def test_composition_without_registry_refuses_external_ai_as_unregistered():
    """P4B-REV-F1 - omitting registry from the composition function must
    not widen back to the old non-load-bearing behavior."""
    provider = _FakeAcceptingProvider()
    gateway = _real_gateway(provider)
    service = build_provider_mode_service(rule_set=RuleSetV1(()), gateway=gateway)
    gw_req = _gateway_request()
    request = ProviderModeRequestV1(
        task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="req-4", nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )
    result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
    assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
    assert result.receipt.reason_code == "PROVIDER_NOT_REGISTERED"
    assert provider.calls == 0


def test_composition_module_has_no_http_route_or_persistence():
    from pathlib import Path

    import workspace_api.application.ai_provider_modes as module

    text = Path(module.__file__).read_text(encoding="utf-8")
    assert "APIRouter" not in text
    assert "@app." not in text
    assert "INSERT INTO" not in text
    assert "session.commit" not in text
