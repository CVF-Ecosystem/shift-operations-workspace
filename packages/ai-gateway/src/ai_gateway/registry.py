"""Explicit provider/model registry (SPEC R11).

Registration is explicit and deterministic: an unregistered provider id or an
unregistered model for a registered provider fails closed before dispatch, so a
typo can never silently route to an unintended model.

``placement`` (P4A2-REV-F3/Amendment 1) is a REQUIRED, strict keyword with no
default: the registry itself binds one immutable :class:`~ai_gateway.models.
Placement` fact to each registered provider, independent of anything a caller
later claims in a per-request ``GatewayRequest.placement`` field. This is the
registry-owned fact ``AIGateway.execute`` compares the incoming request
placement against before any context/data-scope work - the structural
enforcement that makes relabeling an external provider as local impossible,
not merely a naming convention callers are expected to honor.
"""

from __future__ import annotations

from .errors import ProviderNotRegisteredError
from .models import Placement
from .provider import AIProvider

_VALID_PLACEMENTS = frozenset(Placement)


class ProviderRegistry:
    """In-memory registry of provider implementations, allowed models, and
    each provider's one immutable registered placement."""

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}
        self._models: dict[str, tuple[str, ...]] = {}
        self._placements: dict[str, Placement] = {}

    def register(self, provider: AIProvider, models: tuple[str, ...], *, placement: Placement) -> None:
        """Register ``provider``, the exact model ids it may serve, and the
        one immutable ``placement`` it is truthfully deployed at. ``placement``
        has no default and must be an actual :class:`Placement` member - a
        missing, non-enum, or otherwise unrecognized value fails closed here,
        at registration time, before any request can ever be dispatched
        against this provider."""
        provider_id = getattr(provider, "provider_id", "")
        if not provider_id:
            raise ProviderNotRegisteredError("provider_id must be a non-empty string")
        if not models:
            raise ProviderNotRegisteredError("at least one model id is required")
        if any(not model for model in models):
            raise ProviderNotRegisteredError("model ids must be non-empty strings")
        if len(set(models)) != len(models):
            raise ProviderNotRegisteredError("model ids must be duplicate-free")
        if not isinstance(placement, Placement) or placement not in _VALID_PLACEMENTS:
            raise ProviderNotRegisteredError(
                "placement must be an explicit ai_gateway.models.Placement member"
            )
        self._providers[provider_id] = provider
        self._models[provider_id] = tuple(models)
        self._placements[provider_id] = placement

    def resolve(self, provider_id: str, model_id: str) -> AIProvider:
        """Return the provider for an explicitly registered (provider, model)."""
        provider = self._providers.get(provider_id)
        if provider is None:
            raise ProviderNotRegisteredError(f"provider not registered: {provider_id}")
        if model_id not in self._models.get(provider_id, ()):
            raise ProviderNotRegisteredError(
                f"model not registered for provider {provider_id}: {model_id}"
            )
        return provider

    def registered_models(self, provider_id: str) -> tuple[str, ...]:
        """Return the exact registered model ids, or empty when unknown."""
        return self._models.get(provider_id, ())

    def registered_placement(self, provider_id: str) -> Placement | None:
        """Return the provider's one immutable registered placement, or
        ``None`` when the provider id is not registered at all - a caller
        must not treat ``None`` as any particular placement; it means
        "unregistered", handled separately by the existing later
        ``resolve()`` refusal path (SPEC R11), never as an implicit match."""
        return self._placements.get(provider_id)
