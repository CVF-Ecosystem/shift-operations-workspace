"""Public contracts for provider-neutral channel integration."""

from .delivery import AdapterDeliveryRequestV1, AdapterDeliveryResultV1, AdapterMode, AuthorizedEndpointV1
from .ports import AttachmentScanPort, CoreIngressPort, OutboundAdapterPort, ResolvedHttpsTransportPort
from .service_assertion import ServiceAssertionV1

__all__ = [
    "AttachmentScanPort",
    "AdapterDeliveryRequestV1",
    "AdapterDeliveryResultV1",
    "AdapterMode",
    "AuthorizedEndpointV1",
    "CoreIngressPort",
    "OutboundAdapterPort",
    "ResolvedHttpsTransportPort",
    "ServiceAssertionV1",
]
