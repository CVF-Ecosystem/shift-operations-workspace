"""P4-B CVF governance boundary tests (SPEC R1/R3/R6/R7/R9/R10/R12).

No-network and no-persistence boundary tests, at-most-once gateway dispatch
proof at the object-identity level, and claim-boundary checks that this
tranche's evidence artifacts do not overclaim beyond the bounded
provider-mode foundation DESIGN/SPEC actually authorize.

Not governance proof by itself - a separately authorized live run through
``scripts/run_p4b_ai_providers_live_evidence.py`` (never executed during
this BUILD) is the only accepted governance proof surface for actual
provider dispatch. These tests prove the STRUCTURAL boundaries that make
such a future run meaningful.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

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

from ai_providers.mock_provider import MockProviderAdapter
from ai_providers.models import (
    MockAuthorizationV1,
    ProviderKind,
    ProviderMetadataV1,
    ProviderModeOutcome,
    ProviderModeRequestV1,
)
from ai_providers.registry import ProviderAdapterRegistry
from ai_providers.rules_only import RuleSetV1
from ai_providers.service import ProviderModeService

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["status"], "properties": {"status": {"type": "string"}}}


def _registry_with(provider_id: str = "p1", model_id: str = "m1", *, placement: Placement = Placement.LOCAL) -> ProviderAdapterRegistry:
    registry = ProviderAdapterRegistry()
    registry.register(
        ProviderMetadataV1(
            provider_id=provider_id, kind=ProviderKind.EXTERNAL_GATEWAY, placement=placement,
            model_ids=(model_id,), evidence_eligible=True,
        )
    )
    return registry


class _AnswerGateway:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, request: GatewayRequest) -> GatewayResult:
        self.calls += 1
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


def _gateway_request(**overrides) -> GatewayRequest:
    context_facts = ContextFacts(
        classification=Classification.PUBLIC, redaction_applied=True, minimization_proven=True,
        evidence_count=1, estimated_input_tokens=5, context_digest=digest_of({}),
    )
    budget_facts = BudgetFacts(
        per_request_token_limit=1000, daily_budget_usd_millis=0, monthly_budget_usd_millis=0,
        spent_today_usd_millis=0, spent_month_usd_millis=0, estimated_cost_usd_millis=0,
    )
    fields = dict(
        task_type="t1", ai_mode=AIMode.EXTERNAL_AI, provider_id="p1", model_id="m1",
        placement=Placement.LOCAL, context={}, output_schema=SCHEMA,
        context_facts=context_facts, budget_facts=budget_facts, termination_facts=TerminationFacts(),
    )
    fields.update(overrides)
    return GatewayRequest(**fields)


class TestNoNetworkBoundary:
    """SPEC R1/R10: the pure package's only reachable network-shaped call
    site is through the injected gateway. No ai_providers module performs
    any network I/O of its own."""

    def test_ai_providers_package_has_no_network_capable_import(self):
        import ai_providers

        package_root = Path(ai_providers.__file__).resolve().parent
        for path in sorted(package_root.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            assert "socket" not in text
            assert "urllib.request" not in text
            assert "http.client" not in text

    def test_application_composition_module_has_no_network_capable_import(self):
        import workspace_api.application.ai_provider_modes as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "urllib.request" not in text
        assert "http.client" not in text
        assert "socket" not in text


class TestNoPersistenceBoundary:
    """SPEC R10: no request/rule/output/receipt persistence anywhere in the
    request path."""

    def test_ai_providers_package_has_no_database_import(self):
        import ai_providers

        package_root = Path(ai_providers.__file__).resolve().parent
        for path in sorted(package_root.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            assert "sqlite3" not in text
            assert "sqlalchemy" not in text.lower()

    def test_application_composition_never_persists_anything(self):
        import workspace_api.application.ai_provider_modes as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "append_audit" not in text
        assert "INSERT INTO" not in text
        assert "session.add" not in text


def _external_request(gw_req: GatewayRequest, **overrides) -> ProviderModeRequestV1:
    fields = dict(
        task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="v1", request_id="r2",
        nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )
    fields.update(overrides)
    return ProviderModeRequestV1(**fields)


class TestAtMostOnceGatewayDispatch:
    """SPEC R6: ProviderModeService.execute calls the injected gateway's
    execute zero or one time, never more, and never a second gateway
    instance."""

    def test_no_ai_never_touches_gateway_object(self):
        gateway = _AnswerGateway()
        service = ProviderModeService(rule_set=RuleSetV1(()), gateway=gateway)
        request = ProviderModeRequestV1(
            task_type="t1", ai_mode="NO_AI", facts={}, output_schema=SCHEMA,
            policy_version="v1", request_id="r1",
        )
        asyncio.run(service.execute(request=request, started_at="a", finished_at="b"))
        assert gateway.calls == 0

    def test_external_ai_calls_gateway_exactly_once(self):
        gateway = _AnswerGateway()
        gw_req = _gateway_request()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(gw_req)
        asyncio.run(service.execute(request=request, started_at="a", finished_at="b"))
        assert gateway.calls == 1


class TestMockNeverGovernanceEvidence:
    """SPEC R7/R12: a mock adapter's output/receipt is never accepted as
    governance proof - structurally, not just by convention."""

    def test_mock_adapter_evidence_eligible_is_always_false(self):
        auth = MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=False)
        adapter = MockProviderAdapter(provider_id="mock1", authorization=auth, fixed_output={"status": "ok"})
        assert adapter.evidence_eligible is False

    def test_registry_evidence_projection_never_contains_a_mock_entry(self):
        registry = ProviderAdapterRegistry()
        registry.register(
            ProviderMetadataV1(
                provider_id="mock1", kind=ProviderKind.MOCK, placement=Placement.LOCAL,
                model_ids=("m1",), evidence_eligible=False,
            ),
            allow_test_only=True,
        )
        assert registry.evidence_projection() == ()

    def test_mock_registered_in_p4b_registry_is_still_refused_for_external_ai(self):
        """P4B-REV-F1 - being validly registered (allow_test_only=True) is
        not the same as being an evidence-eligible external target; the
        service must refuse it with zero calls even though it resolves."""
        gw_req = _gateway_request(provider_id="mock1")
        registry = ProviderAdapterRegistry()
        registry.register(
            ProviderMetadataV1(
                provider_id="mock1", kind=ProviderKind.MOCK, placement=Placement.LOCAL,
                model_ids=("m1",), evidence_eligible=False,
            ),
            allow_test_only=True,
        )
        gateway = _AnswerGateway()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(gw_req, provider_id="mock1")
        result = asyncio.run(service.execute(request=request, started_at="a", finished_at="b"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        # P4B-REV-F1-R1: the general "not exactly EXTERNAL_GATEWAY +
        # evidence_eligible=True" refusal now covers MOCK too.
        assert result.receipt.reason_code == "PROVIDER_NOT_EXTERNAL_GATEWAY_EVIDENCE_ELIGIBLE"
        assert gateway.calls == 0


class TestReceiptContainsNoRawBody:
    def test_external_accepted_receipt_has_no_facts_or_output_body(self):
        gateway = _AnswerGateway()
        gw_req = _gateway_request()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(
            gw_req, facts={"secret_looking_fact": "should never leak"}, request_id="r3",
        )
        result = asyncio.run(service.execute(request=request, started_at="a", finished_at="b"))
        dump_str = str(result.receipt.model_dump(mode="python"))
        assert "should never leak" not in dump_str


class TestClaimBoundary:
    """SPEC R12: this tranche proves a bounded provider-mode foundation -
    never a production/vendor adapter, automatic routing, durable usage/
    audit, a public API, or production readiness. These tests assert the
    DESIGN/SPEC/README documents actually declare that boundary."""

    def test_readme_declares_the_claim_boundary(self):
        readme = (REPO_ROOT / "packages" / "ai-providers" / "README.md").read_text(encoding="utf-8")
        assert "claim boundary" in readme.lower()
        assert "does not prove" in readme.lower()

    def test_spec_declares_exclusions(self):
        spec = (REPO_ROOT / "docs" / "specs" / "P4B_AI_PROVIDERS_SPEC.md").read_text(encoding="utf-8")
        assert "Exclusions" in spec

    def test_receipt_never_claims_external_accepted_without_one_gateway_call(self):
        gateway = _AnswerGateway()
        gw_req = _gateway_request()
        registry = _registry_with()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        request = _external_request(gw_req, request_id="r4")
        result = asyncio.run(service.execute(request=request, started_at="a", finished_at="b"))
        if result.receipt.outcome is ProviderModeOutcome.EXTERNAL_ACCEPTED:
            assert result.receipt.gateway_calls == 1
