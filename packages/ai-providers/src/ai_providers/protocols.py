"""P4-B structural protocols (SPEC R2/R6/R10).

``ProviderModeService`` depends only on these structural protocols, never on
a concrete SDK, HTTP client, or vendor module - exactly the same discipline
``ai_gateway.provider.AIProvider`` already enforces for P4-A. The injected
gateway is P4-A's own ``ai_gateway.service.AIGateway`` (or any object
structurally matching this narrower protocol); this module never redefines
``ai_gateway.provider.AIProvider`` itself.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_gateway.models import GatewayRequest, GatewayResult


@runtime_checkable
class InjectedGateway(Protocol):
    """The exact shape ``ProviderModeService`` may call for ``EXTERNAL_AI``
    (SPEC R6): one awaitable ``execute`` taking a strict ``GatewayRequest``
    and returning a ``GatewayResult``. P4-B never calls an ``AIProvider``
    directly and never constructs a second gateway of its own."""

    async def execute(self, request: GatewayRequest) -> GatewayResult:
        """Perform at most one governed dispatch. Never called more than
        once per ``ProviderModeService.execute`` invocation."""
        ...


__all__ = ["InjectedGateway"]
