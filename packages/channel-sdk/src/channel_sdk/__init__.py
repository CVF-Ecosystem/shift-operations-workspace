"""Public contracts for provider-neutral channel integration."""

from .ports import AttachmentScanPort, CoreIngressPort, OutboundAdapterPort
from .service_assertion import ServiceAssertionV1

__all__ = [
    "AttachmentScanPort",
    "CoreIngressPort",
    "OutboundAdapterPort",
    "ServiceAssertionV1",
]
