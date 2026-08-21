"""Provider protocol (SPEC R11).

The gateway depends only on this structural protocol, never on a concrete SDK,
HTTP client, or vendor module. Replacing the injected implementation must not
require editing gateway core. The evidence runner supplies an evidence-only
adapter; that adapter is not a production provider adapter and does not close
P4-B.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .models import ProviderRequest, ProviderResult


@runtime_checkable
class AIProvider(Protocol):
    """Structural contract for a dispatchable provider.

    Implementations must not raise credentials, authorization headers, or raw
    upstream error bodies through these methods; the gateway records only safe
    identifiers and typed reason codes.
    """

    provider_id: str

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        """Perform exactly one provider request. Must not retry internally."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Liveness probe. Not authorized during this tranche's evidence run."""
        ...

    async def cancel_request(self, request_id: str) -> None:
        """Best-effort cancellation after a timeout (SPEC R7)."""
        ...
