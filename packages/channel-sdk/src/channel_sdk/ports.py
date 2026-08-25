"""Narrow ports shared by Integration Edge and the application core."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

from .service_assertion import ServiceAssertionV1


@runtime_checkable
class CoreIngressPort(Protocol):
    """The sole edge-to-core operation; implementations create proposals only."""

    def propose_external_ingress(
        self,
        *,
        assertion: ServiceAssertionV1,
        proposal: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]: ...


@runtime_checkable
class OutboundAdapterPort(Protocol):
    """Provider-neutral delivery boundary implemented by P4-D adapters."""

    evidence_eligible: bool

    def deliver(
        self, *, command: Mapping[str, Any], idempotency_key: str
    ) -> Mapping[str, Any]: ...


@runtime_checkable
class AttachmentScanPort(Protocol):
    def inspect(self, *, metadata: Mapping[str, Any]) -> Mapping[str, Any]: ...
