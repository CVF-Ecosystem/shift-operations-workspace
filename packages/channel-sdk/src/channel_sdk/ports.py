"""Narrow ports shared by Integration Edge and the application core."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

from .delivery import AdapterDeliveryRequestV1, AdapterDeliveryResultV1, AdapterMode, AuthorizedEndpointV1
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

    adapter_mode: AdapterMode

    def deliver(
        self, *, request: AdapterDeliveryRequestV1, idempotency_key: str
    ) -> AdapterDeliveryResultV1: ...


@runtime_checkable
class ResolvedHttpsConnectionPort(Protocol):
    connected_peer_ip: str
    tls_server_name: str

    def send(
        self,
        *,
        method: str,
        path: str,
        headers: Mapping[str, str],
        body: bytes,
        total_timeout_seconds: float,
        max_response_bytes: int,
    ) -> tuple[int, int]: ...


@runtime_checkable
class ResolvedHttpsTransportPort(Protocol):
    trust_env: bool

    def connect(
        self,
        authorized_endpoint: AuthorizedEndpointV1,
        connect_timeout_seconds: float,
    ) -> ResolvedHttpsConnectionPort: ...


@runtime_checkable
class AttachmentScanPort(Protocol):
    def inspect(self, *, metadata: Mapping[str, Any]) -> Mapping[str, Any]: ...
