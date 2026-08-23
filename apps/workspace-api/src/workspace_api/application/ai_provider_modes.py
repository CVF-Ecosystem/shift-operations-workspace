"""P4-B provider-mode foundation - no-route application composition (SPEC
R10).

Builds a pure ``ai_providers.service.ProviderModeService`` from explicit,
caller-supplied dependencies only: an immutable ``RuleSetV1`` and an
optional, already-configured injected gateway. Opens no HTTP route, reads no
environment, and persists nothing.

Per DESIGN's "Application composition" section: existing P4-A2/P4-A3
composition may call this only in a future, separately authorized wiring
tranche. This module performs no implicit rewiring of any existing caller and
is not itself invoked by any route in this tranche.
"""

from __future__ import annotations

from ai_providers.registry import ProviderAdapterRegistry
from ai_providers.rules_only import RuleSetV1
from ai_providers.service import ProviderModeService


def build_provider_mode_service(
    *,
    rule_set: RuleSetV1,
    registry: ProviderAdapterRegistry | None = None,
    gateway: object | None = None,
) -> ProviderModeService:
    """SPEC R10 - construct a ``ProviderModeService`` from explicit
    dependency injection only. ``registry``, when supplied, must already be
    a fully configured ``ai_providers.registry.ProviderAdapterRegistry``
    (P4B-REV-F1: the load-bearing registry ``ProviderModeService`` consults
    before any EXTERNAL_AI delegation; omitting it defaults to an empty
    registry that refuses every EXTERNAL_AI target as unregistered, never to
    "no check at all"). ``gateway``, when supplied, must already be a fully
    configured object matching ``ai_providers.protocols.InjectedGateway``
    (e.g. a real ``ai_gateway.service.AIGateway`` instance); this function
    never constructs a gateway, provider, registry, or ledger of its own,
    never reads an environment variable, and never opens a database
    connection or HTTP route.
    """
    return ProviderModeService(rule_set=rule_set, registry=registry, gateway=gateway)


__all__ = ["build_provider_mode_service"]
