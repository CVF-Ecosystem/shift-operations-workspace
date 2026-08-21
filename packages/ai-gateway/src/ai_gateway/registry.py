"""Explicit provider/model registry (SPEC R11).

Registration is explicit and deterministic: an unregistered provider id or an
unregistered model for a registered provider fails closed before dispatch, so a
typo can never silently route to an unintended model.
"""

from __future__ import annotations

from .errors import ProviderNotRegisteredError
from .provider import AIProvider


class ProviderRegistry:
    """In-memory registry of provider implementations and allowed models."""

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}
        self._models: dict[str, tuple[str, ...]] = {}

    def register(self, provider: AIProvider, models: tuple[str, ...]) -> None:
        """Register ``provider`` and the exact model ids it may serve."""
        provider_id = getattr(provider, "provider_id", "")
        if not provider_id:
            raise ProviderNotRegisteredError("provider_id must be a non-empty string")
        if not models:
            raise ProviderNotRegisteredError("at least one model id is required")
        if any(not model for model in models):
            raise ProviderNotRegisteredError("model ids must be non-empty strings")
        if len(set(models)) != len(models):
            raise ProviderNotRegisteredError("model ids must be duplicate-free")
        self._providers[provider_id] = provider
        self._models[provider_id] = tuple(models)

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
