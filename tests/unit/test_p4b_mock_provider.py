"""P4-B SPEC R7 - MockProviderAdapter is test-only and evidence-ineligible.

Proves construction structurally requires a valid TEST_ONLY_COMPONENT_TEST /
evidence_eligible=False authorization, responses are fixed/bounded/deep-copy
isolated, call/cancel tracking is deterministic, and no network is ever
performed.
"""

from __future__ import annotations

import asyncio

import pytest
from ai_gateway.models import ProviderRequest
from pydantic import ValidationError

from ai_providers.errors import DuplicateProviderRegistrationError
from ai_providers.mock_provider import MockProviderAdapter
from ai_providers.models import MockAuthorizationV1, ProviderKind, ProviderMetadataV1
from ai_providers.registry import ProviderAdapterRegistry

VALID_AUTH = MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=False)


def _metadata(**overrides):
    from ai_gateway.models import Placement

    fields = dict(
        provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.LOCAL,
        model_ids=("m1",), evidence_eligible=True,
    )
    fields.update(overrides)
    return ProviderMetadataV1(**fields)


def _provider_request(**overrides) -> ProviderRequest:
    fields = dict(
        task_type="t1", model_id="m1", context={}, output_schema={"type": "object"},
    )
    fields.update(overrides)
    return ProviderRequest(**fields)


class TestAuthorizationIsStructurallyRequired:
    def test_missing_authorization_purpose_fails_construction(self):
        with pytest.raises(ValidationError):
            MockAuthorizationV1(purpose="", evidence_eligible=False)

    def test_wrong_purpose_fails_construction(self):
        with pytest.raises(ValidationError):
            MockAuthorizationV1(purpose="PRODUCTION_USE", evidence_eligible=False)

    def test_evidence_eligible_true_fails_construction(self):
        with pytest.raises(ValidationError):
            MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=True)

    def test_adapter_rejects_non_model_authorization(self):
        with pytest.raises(TypeError):
            MockProviderAdapter(
                provider_id="mock1",
                authorization={"purpose": "TEST_ONLY_COMPONENT_TEST", "evidence_eligible": False},  # type: ignore[arg-type]
                fixed_output={"status": "ok"},
            )

    def test_adapter_rejects_model_construct_bypassed_authorization(self):
        """P4B-REV-F4.1 - the reviewer's exact reproduction:
        MockAuthorizationV1.model_construct(purpose="PRODUCTION_USE",
        evidence_eligible=True) is an instance of MockAuthorizationV1 (so a
        naive isinstance check alone would wrongly accept it) but never ran
        the model's own validators. The adapter must force real field-level
        revalidation from the primitive dump and reject it."""
        bypassed = MockAuthorizationV1.model_construct(
            purpose="PRODUCTION_USE", evidence_eligible=True
        )
        with pytest.raises(ValueError):
            MockProviderAdapter(
                provider_id="mock1", authorization=bypassed, fixed_output={"status": "ok"}
            )

    def test_valid_authorization_constructs_successfully(self):
        adapter = MockProviderAdapter(
            provider_id="mock1", authorization=VALID_AUTH, fixed_output={"status": "ok"}
        )
        assert adapter.evidence_eligible is False
        assert adapter.authorization.purpose == "TEST_ONLY_COMPONENT_TEST"


class TestBoundedFixedOutput:
    def test_rejects_unbounded_fixed_output(self):
        with pytest.raises(ValueError):
            MockProviderAdapter(
                provider_id="mock1", authorization=VALID_AUTH,
                fixed_output={"payload": "x" * (20 * 1024)},
            )

    def test_rejects_non_json_fixed_output(self):
        with pytest.raises(ValueError):
            MockProviderAdapter(
                provider_id="mock1", authorization=VALID_AUTH, fixed_output={"x": object()}
            )


class TestResponseIsolation:
    def test_fixed_output_is_deep_copy_isolated_from_construction_input(self):
        source = {"status": "ok", "nested": {"a": 1}}
        adapter = MockProviderAdapter(provider_id="mock1", authorization=VALID_AUTH, fixed_output=source)
        source["nested"]["a"] = 999
        result = asyncio.run(adapter.generate_structured_output(_provider_request()))
        assert result.output["nested"]["a"] == 1

    def test_each_call_returns_a_fresh_deep_copy(self):
        adapter = MockProviderAdapter(
            provider_id="mock1", authorization=VALID_AUTH, fixed_output={"status": "ok", "nested": {"a": 1}}
        )
        first = asyncio.run(adapter.generate_structured_output(_provider_request()))
        first.output["nested"]["a"] = 999
        second = asyncio.run(adapter.generate_structured_output(_provider_request()))
        assert second.output["nested"]["a"] == 1


class TestDeterministicTracking:
    def test_calls_increment_deterministically(self):
        adapter = MockProviderAdapter(provider_id="mock1", authorization=VALID_AUTH, fixed_output={"status": "ok"})
        assert adapter.calls == 0
        asyncio.run(adapter.generate_structured_output(_provider_request()))
        assert adapter.calls == 1
        asyncio.run(adapter.generate_structured_output(_provider_request()))
        assert adapter.calls == 2

    def test_cancel_tracks_request_ids_in_order(self):
        adapter = MockProviderAdapter(provider_id="mock1", authorization=VALID_AUTH, fixed_output={"status": "ok"})
        asyncio.run(adapter.cancel_request("req-1"))
        asyncio.run(adapter.cancel_request("req-2"))
        assert adapter.cancels == 2
        assert adapter.cancelled_request_ids == ("req-1", "req-2")

    def test_result_reports_declared_provider_and_requested_model(self):
        adapter = MockProviderAdapter(provider_id="mock1", authorization=VALID_AUTH, fixed_output={"status": "ok"})
        result = asyncio.run(adapter.generate_structured_output(_provider_request(model_id="m-specific")))
        assert result.provider_id == "mock1"
        assert result.model_id == "m-specific"
        assert result.usage == {"total_tokens": 0, "cost_usd_millis": 0}


class TestNoNetwork:
    def test_source_has_no_network_capable_import_or_call(self):
        from pathlib import Path

        import ai_providers.mock_provider as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "socket" not in text
        assert "urllib" not in text
        assert "requests" not in text
        assert "httpx" not in text


class TestMockDefaultDenial:
    """SPEC R8 - relocated here from test_p4b_provider_registry.py (file-size
    budget) since it is fundamentally about mock exclusion."""

    def _mock_metadata(self) -> ProviderMetadataV1:
        return _metadata(provider_id="mock1", kind=ProviderKind.MOCK, evidence_eligible=False)

    def test_mock_registration_denied_by_default(self):
        registry = ProviderAdapterRegistry()
        with pytest.raises(DuplicateProviderRegistrationError):
            registry.register(self._mock_metadata())

    def test_mock_registration_denied_with_allow_test_only_false(self):
        registry = ProviderAdapterRegistry()
        with pytest.raises(DuplicateProviderRegistrationError):
            registry.register(self._mock_metadata(), allow_test_only=False)

    def test_mock_registration_admitted_with_explicit_allow_test_only(self):
        registry = ProviderAdapterRegistry()
        registry.register(self._mock_metadata(), allow_test_only=True)
        assert registry.resolve("mock1", "m1").kind is ProviderKind.MOCK


class TestProjectionsExcludeMock:
    """SPEC R8 - relocated here from test_p4b_provider_registry.py (file-size
    budget) since it is fundamentally about mock exclusion."""

    def test_production_projection_excludes_mock(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(provider_id="real1"))
        registry.register(
            _metadata(provider_id="mock1", kind=ProviderKind.MOCK, evidence_eligible=False),
            allow_test_only=True,
        )
        ids = [m.provider_id for m in registry.production_projection()]
        assert ids == ["real1"]

    def test_evidence_projection_excludes_mock_even_when_caller_claims_eligible(self):
        """A mock entry cannot claim evidence_eligible=True at all (the
        model itself rejects that combination), so this proves the registry
        projection is a structural kind-check, not a trust-based label
        check, by using the one shape that IS constructible."""
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(provider_id="real1", evidence_eligible=True))
        registry.register(
            _metadata(provider_id="mock1", kind=ProviderKind.MOCK, evidence_eligible=False),
            allow_test_only=True,
        )
        ids = [m.provider_id for m in registry.evidence_projection()]
        assert ids == ["real1"]
        assert "mock1" not in ids

    def test_evidence_projection_excludes_non_eligible_real_provider(self):
        registry = ProviderAdapterRegistry()
        registry.register(_metadata(provider_id="real1", evidence_eligible=False))
        assert registry.evidence_projection() == ()

    def test_registered_metadata_returns_none_for_unknown(self):
        registry = ProviderAdapterRegistry()
        assert registry.registered_metadata("nope") is None
