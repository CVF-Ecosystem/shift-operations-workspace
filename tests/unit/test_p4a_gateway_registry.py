"""P4-A SPEC R11 - explicit, deterministic provider/model registry.

NOT GOVERNANCE PROOF: mechanical tests with a fake provider. Governance claims
require the R13 live run.
"""

from __future__ import annotations

import pytest

from ai_gateway.errors import ProviderNotRegisteredError
from ai_gateway.models import ProviderRequest, ProviderResult
from ai_gateway.registry import ProviderRegistry


class _FakeProvider:
    """Non-governance fake: records calls, performs no I/O."""

    def __init__(self, provider_id: str = "fake") -> None:
        self.provider_id = provider_id

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        return ProviderResult(output={}, provider_id=self.provider_id, model_id=request.model_id)

    async def health_check(self) -> dict:
        return {}

    async def cancel_request(self, request_id: str) -> None:
        return None


def test_resolves_registered_provider_and_model():
    registry = ProviderRegistry()
    provider = _FakeProvider()
    registry.register(provider, ("model-a", "model-b"))
    assert registry.resolve("fake", "model-a") is provider


def test_unknown_provider_fails_closed():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.resolve("nope", "model-a")


def test_unregistered_model_fails_closed():
    """A registered provider must not serve an unregistered model id."""
    registry = ProviderRegistry()
    registry.register(_FakeProvider(), ("model-a",))
    with pytest.raises(ProviderNotRegisteredError):
        registry.resolve("fake", "model-typo")


def test_empty_provider_id_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(provider_id=""), ("model-a",))


def test_empty_model_tuple_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ())


def test_duplicate_model_ids_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ("model-a", "model-a"))


def test_empty_model_id_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ("model-a", ""))


def test_registered_models_returns_exact_tuple():
    registry = ProviderRegistry()
    registry.register(_FakeProvider(), ("model-a", "model-b"))
    assert registry.registered_models("fake") == ("model-a", "model-b")
    assert registry.registered_models("unknown") == ()


def test_replacing_provider_does_not_require_core_change():
    """R11: swapping the implementation is a registry operation only."""
    registry = ProviderRegistry()
    first, second = _FakeProvider("p"), _FakeProvider("p")
    registry.register(first, ("m",))
    registry.register(second, ("m",))
    assert registry.resolve("p", "m") is second
