"""P4-B SPEC R8 - ProviderAdapterRegistry owns immutable provider metadata.

Covers duplicate/relabel rejection, default mock denial, allow_test_only
admission, (P4B-REV-F1/F1-R1) proof that ProviderModeService consults this
registry as a load-bearing zero-call gate before EXTERNAL_AI delegation
(exactly kind=EXTERNAL_GATEWAY AND evidence_eligible=True, or refuse), and
(P4B-REV-F4-R2) that untyped public-boundary input never raw-escapes.
Projection-exclusion tests live in test_p4b_mock_provider.py.
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
from pydantic import ValidationError

from ai_providers.errors import DuplicateProviderRegistrationError, ProviderNotRegisteredError
from ai_providers.models import ProviderKind, ProviderMetadataV1, ProviderModeOutcome, ProviderModeRequestV1
from ai_providers.registry import ProviderAdapterRegistry
from ai_providers.rules_only import RuleSetV1
from ai_providers.service import ProviderModeService

_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["status"], "properties": {"status": {"type": "string"}}}


class _NeverCalledGateway:
    async def execute(self, request):
        raise AssertionError("must never be called for a load-bearing-registry refusal case")


class _AcceptingGateway:
    """P4B-REV-F1-R1 inverse-positive fixture - a gateway that accepts."""

    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, request):
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


def _gw_request(**overrides) -> GatewayRequest:
    fields = dict(
        task_type="t1", ai_mode=AIMode.EXTERNAL_AI, provider_id="p1", model_id="m1",
        placement=Placement.LOCAL, context={}, output_schema=_SCHEMA,
        context_facts=ContextFacts(
            classification=Classification.PUBLIC, redaction_applied=True, minimization_proven=True,
            evidence_count=1, estimated_input_tokens=10, context_digest=digest_of({}),
        ),
        budget_facts=BudgetFacts(
            per_request_token_limit=1000, daily_budget_usd_millis=0, monthly_budget_usd_millis=0,
            spent_today_usd_millis=0, spent_month_usd_millis=0, estimated_cost_usd_millis=0,
        ),
        termination_facts=TerminationFacts(),
    )
    fields.update(overrides)
    return GatewayRequest(**fields)


def _mode_request(gw_req: GatewayRequest, **overrides) -> ProviderModeRequestV1:
    fields = dict(
        task_type="t1", ai_mode="EXTERNAL_AI", facts={}, output_schema=_SCHEMA,
        policy_version="v1", request_id="r1",
        nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )
    fields.update(overrides)
    return ProviderModeRequestV1(**fields)


def _metadata(**overrides) -> ProviderMetadataV1:
    fields = dict(
        provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.LOCAL,
        model_ids=("m1",), evidence_eligible=True,
    )
    fields.update(overrides)
    return ProviderMetadataV1(**fields)


class TestRegistration:
    def test_register_and_resolve(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata())
        resolved = registry.resolve("p1", "m1")
        assert resolved.provider_id == "p1"

    def test_resolve_unregistered_provider_fails_closed(self):
        registry = ProviderAdapterRegistry()
        with pytest.raises(ProviderNotRegisteredError):
            registry.resolve("nope", "m1")

    def test_resolve_unregistered_model_fails_closed(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata())
        with pytest.raises(ProviderNotRegisteredError):
            registry.resolve("p1", "other-model")

    def test_identical_reregistration_is_idempotent(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata())
        registry.register(_metadata())  # same metadata twice - allowed
        assert registry.resolve("p1", "m1").provider_id == "p1"

    def test_relabel_registration_fails_closed(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata())
        with pytest.raises(DuplicateProviderRegistrationError):
            registry.register(_metadata(placement=Placement.EXTERNAL))

    def test_rejects_arbitrary_placement_string_at_registration(self):
        """P4B-REV-F3 - the reviewer registered a nonsense placement 'mars'
        successfully; placement must be a real Placement enum member."""
        with pytest.raises(ValidationError):
            _metadata(placement="mars")

    def test_relabel_kind_fails_closed(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata())
        with pytest.raises(DuplicateProviderRegistrationError):
            registry.register(_metadata(kind=ProviderKind.RULES_ONLY))

    def test_model_construct_bypassed_metadata_is_rejected_without_mutation(self):
        """P4B-REV-F4-R1 - reviewer's exact repro: model_construct(kind=
        "BOGUS", placement="mars") skips validators; register() must
        reconstruct from the primitive dump, reject it, and leave the
        registry completely unchanged (no partial mutation)."""
        bypassed = ProviderMetadataV1.model_construct(
            provider_id="p1", kind="BOGUS", placement="mars", model_ids=("m1",), evidence_eligible=True,
        )
        registry = ProviderAdapterRegistry()
        with pytest.raises(DuplicateProviderRegistrationError):
            registry.register(bypassed)
        assert registry.registered_metadata("p1") is None

    @pytest.mark.parametrize("bad_input", [{"not": "valid"}, object()], ids=["primitive_mapping", "arbitrary_object"])
    def test_untyped_public_boundary_input_rejects_without_raw_attributeerror(self, bad_input):
        """P4B-REV-F4-R2 - a dict/object() has no .model_dump; must reach
        the typed error, not a raw AttributeError, registry unmutated."""
        registry = ProviderAdapterRegistry()
        with pytest.raises(DuplicateProviderRegistrationError):
            registry.register(bad_input)
        assert registry.registered_metadata("p1") is None
        registry.register(_metadata())  # positive control: still works after rejection
        assert registry.registered_metadata("p1") is not None

    def test_primitive_mapping_with_valid_typed_values_registers_normally(self):
        """P4B-REV-F4-R2 positive - a correctly-typed plain dict (not a
        ProviderMetadataV1 instance) registers normally via model_validate."""
        registry = ProviderAdapterRegistry()
        mapping = dict(provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.LOCAL, model_ids=("m1",), evidence_eligible=True)
        registry.register(mapping)
        assert registry.registered_metadata("p1").provider_id == "p1"


class TestRegistryIsLoadBearingInService:
    """P4B-REV-F1 - the registry check happens before any gateway/provider
    call, independent of any P4-A ProviderRegistry the injected gateway
    itself may hold, and independent of caller-supplied labels."""

    def test_unregistered_provider_is_zero_call_refusal(self):
        gw_req = _gw_request()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=ProviderAdapterRegistry(), gateway=_NeverCalledGateway())
        result = asyncio.run(service.execute(request=_mode_request(gw_req), started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "PROVIDER_NOT_REGISTERED"
        assert result.receipt.gateway_calls == 0

    def test_default_registry_refuses_everything_as_unregistered(self):
        """Omitting the registry constructor argument must NOT widen back
        to the old non-load-bearing behavior - it defaults to an empty
        registry that refuses every EXTERNAL_AI target as unregistered."""
        gw_req = _gw_request()
        service = ProviderModeService(rule_set=RuleSetV1(()), gateway=_NeverCalledGateway())
        result = asyncio.run(service.execute(request=_mode_request(gw_req), started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "PROVIDER_NOT_REGISTERED"

    def test_registered_mock_kind_is_refused_zero_call_even_though_registered(self):
        """The reviewer's exact reproduction: a MockProviderAdapter-shaped
        target, registered validly (allow_test_only=True) in P4-B's own
        registry, must still be refused for EXTERNAL_AI - being registered
        is not the same as being an evidence-eligible external target."""
        gw_req = _gw_request(provider_id="mock1")
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(provider_id="mock1", kind=ProviderKind.MOCK, evidence_eligible=False), allow_test_only=True)
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=_NeverCalledGateway())
        request = _mode_request(gw_req, provider_id="mock1")
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        # P4B-REV-F1-R1: the general "not exactly EXTERNAL_GATEWAY +
        # evidence_eligible=True" refusal covers MOCK too (doubly excluded).
        assert result.receipt.reason_code == "PROVIDER_NOT_EXTERNAL_GATEWAY_EVIDENCE_ELIGIBLE"
        assert result.receipt.gateway_calls == 0
        assert result.receipt.provider_attempts == 0

    def test_a_mock_adapter_registered_only_in_a_different_p4a_registry_is_still_refused(self):
        """Reviewer's exact reproduction: a valid MockProviderAdapter
        registered in P4-A's own ProviderRegistry (never P4-B's), submitted
        under EXTERNAL_AI - refused PROVIDER_NOT_REGISTERED, zero calls,
        regardless of what the injected gateway's own registry contains."""
        from ai_providers.mock_provider import MockProviderAdapter
        from ai_providers.models import MockAuthorizationV1

        auth = MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=False)
        mock_adapter = MockProviderAdapter(
            provider_id="mock-in-p4a-registry-only", authorization=auth, fixed_output={"status": "ok"}
        )
        assert mock_adapter.evidence_eligible is False  # sanity: genuinely a mock

        class _GatewayBackedByP4AMockRegistration:
            """A gateway whose OWN P4-A registry has this mock registered -
            must never be reached since P4-B's own (empty) registry refuses
            first."""

            async def execute(self, request):
                raise AssertionError(
                    "P4-B must refuse an unregistered-in-P4-B provider before ever "
                    "delegating to a gateway, even one whose own P4-A registry has it"
                )

        gw_req = _gw_request(provider_id="mock-in-p4a-registry-only")
        p4b_registry = ProviderAdapterRegistry()  # deliberately does NOT know this provider_id
        service = ProviderModeService(
            rule_set=RuleSetV1(()), registry=p4b_registry, gateway=_GatewayBackedByP4AMockRegistration()
        )
        request = _mode_request(gw_req, provider_id="mock-in-p4a-registry-only")
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "PROVIDER_NOT_REGISTERED"
        assert result.receipt.gateway_calls == 0
        assert result.receipt.provider_attempts == 0
        assert mock_adapter.calls == 0

    def test_registry_placement_mismatch_is_zero_call_refusal(self):
        gw_req = _gw_request(placement=Placement.EXTERNAL)
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(placement=Placement.LOCAL))
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=_NeverCalledGateway())
        request = _mode_request(gw_req, placement=Placement.EXTERNAL)
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "REGISTRY_PLACEMENT_MISMATCH"

    @pytest.mark.parametrize(
        "kind,evidence_eligible",
        [(ProviderKind.EXTERNAL_GATEWAY, False), (ProviderKind.RULES_ONLY, True), (ProviderKind.NO_AI, True)],
        ids=["external_gateway_not_eligible", "rules_only_eligible", "no_ai_eligible"],
    )
    def test_wrong_kind_or_eligibility_combination_is_zero_call_refusal(self, kind, evidence_eligible):
        """P4B-REV-F1-R1 - the reviewer's exact three probes: otherwise-
        valid registered metadata for the requested pair must still refuse
        BEFORE the gateway unless kind is EXACTLY EXTERNAL_GATEWAY AND
        evidence_eligible is EXACTLY True - both conditions, both exact."""
        gw_req = _gw_request()
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(kind=kind, evidence_eligible=evidence_eligible))
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=_NeverCalledGateway())
        result = asyncio.run(service.execute(request=_mode_request(gw_req), started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH
        assert result.receipt.reason_code == "PROVIDER_NOT_EXTERNAL_GATEWAY_EVIDENCE_ELIGIBLE"
        assert result.receipt.gateway_calls == 0
        assert result.receipt.provider_attempts == 0

    def test_exact_external_gateway_and_evidence_eligible_true_proceeds_to_gateway(self):
        """P4B-REV-F1-R1 inverse-positive - the one combination that must
        actually reach the gateway: kind=EXTERNAL_GATEWAY AND
        evidence_eligible=True, both exact."""
        gw_req = _gw_request()
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(kind=ProviderKind.EXTERNAL_GATEWAY, evidence_eligible=True))
        gateway = _AcceptingGateway()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        result = asyncio.run(service.execute(request=_mode_request(gw_req), started_at="t0", finished_at="t1"))
        assert result.receipt.outcome is ProviderModeOutcome.EXTERNAL_ACCEPTED
        assert gateway.calls == 1
        assert result.receipt.gateway_calls == 1
