"""P4-A SPEC R11 - explicit, deterministic provider/model registry.

NOT GOVERNANCE PROOF: mechanical tests with a fake provider. Governance claims
require the R13 live run.
"""

from __future__ import annotations

import pytest

from ai_gateway.errors import ProviderNotRegisteredError
from ai_gateway.models import Placement, ProviderRequest, ProviderResult
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
    registry.register(provider, ("model-a", "model-b"), placement=Placement.LOCAL)
    assert registry.resolve("fake", "model-a") is provider


def test_unknown_provider_fails_closed():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.resolve("nope", "model-a")


def test_unregistered_model_fails_closed():
    """A registered provider must not serve an unregistered model id."""
    registry = ProviderRegistry()
    registry.register(_FakeProvider(), ("model-a",), placement=Placement.LOCAL)
    with pytest.raises(ProviderNotRegisteredError):
        registry.resolve("fake", "model-typo")


def test_empty_provider_id_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(provider_id=""), ("model-a",), placement=Placement.LOCAL)


def test_empty_model_tuple_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), (), placement=Placement.LOCAL)


def test_duplicate_model_ids_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ("model-a", "model-a"), placement=Placement.LOCAL)


def test_empty_model_id_rejected():
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ("model-a", ""), placement=Placement.LOCAL)


def test_registered_models_returns_exact_tuple():
    registry = ProviderRegistry()
    registry.register(_FakeProvider(), ("model-a", "model-b"), placement=Placement.LOCAL)
    assert registry.registered_models("fake") == ("model-a", "model-b")
    assert registry.registered_models("unknown") == ()


def test_replacing_provider_does_not_require_core_change():
    """R11: swapping the implementation is a registry operation only."""
    registry = ProviderRegistry()
    first, second = _FakeProvider("p"), _FakeProvider("p")
    registry.register(first, ("m",), placement=Placement.LOCAL)
    registry.register(second, ("m",), placement=Placement.LOCAL)
    assert registry.resolve("p", "m") is second


# ---------------------------------------------------------------------------
# Amendment 1 / A1-F3 - registry-owned provider placement: register()
# requires an explicit, strict Placement keyword with NO default, binding one
# immutable placement per registered provider.
# ---------------------------------------------------------------------------


def test_register_requires_placement_keyword_with_no_default():
    """Calling register() without the placement keyword must fail with a
    TypeError (missing required keyword-only argument) - there is no default
    to silently fall back on."""
    registry = ProviderRegistry()
    with pytest.raises(TypeError):
        registry.register(_FakeProvider(), ("model-a",))  # type: ignore[call-arg]


def test_register_rejects_missing_placement_value():
    """An explicit but falsy/None placement is not a valid Placement member
    and must be rejected at registration time, before any dispatch."""
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ("model-a",), placement=None)  # type: ignore[arg-type]


def test_register_rejects_non_enum_placement_string():
    """A raw string that happens to match a Placement value's text is not an
    actual Placement enum member and must still be rejected - proving the
    check is type-strict, not merely a value/string comparison."""
    registry = ProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.register(_FakeProvider(), ("model-a",), placement="external")  # type: ignore[arg-type]


@pytest.mark.parametrize("placement", [Placement.LOCAL, Placement.ENTERPRISE, Placement.EXTERNAL])
def test_register_accepts_every_valid_placement_member(placement):
    registry = ProviderRegistry()
    registry.register(_FakeProvider(), ("model-a",), placement=placement)
    assert registry.registered_placement("fake") is placement


def test_registered_placement_returns_none_for_unregistered_provider():
    registry = ProviderRegistry()
    assert registry.registered_placement("never-registered") is None


def test_duplicate_provider_replacement_binds_the_new_placement():
    """Re-registering the same provider id with a DIFFERENT placement must
    replace the old binding exactly - the registry never keeps a stale
    placement fact for a provider id after a fresh registration call."""
    registry = ProviderRegistry()
    registry.register(_FakeProvider("p"), ("m",), placement=Placement.LOCAL)
    assert registry.registered_placement("p") is Placement.LOCAL
    registry.register(_FakeProvider("p"), ("m",), placement=Placement.EXTERNAL)
    assert registry.registered_placement("p") is Placement.EXTERNAL
