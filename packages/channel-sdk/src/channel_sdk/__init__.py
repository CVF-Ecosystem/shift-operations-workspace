"""Public contracts for provider-neutral channel integration."""

from .delivery import AdapterDeliveryRequestV1, AdapterDeliveryResultV1, AdapterMode, AuthorizedEndpointV1
from .ports import AttachmentScanPort, CoreIngressPort, OutboundAdapterPort, ResolvedHttpsTransportPort
from .sender_evidence import (
    SenderEvidenceV1,
    canonical_timestamp,
    derive_sender_token,
    normalize_sender_bytes,
    sender_aware_signature_preimage,
)
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
    "SenderEvidenceV1",
    "ServiceAssertionV1",
    "canonical_timestamp",
    "derive_sender_token",
    "normalize_sender_bytes",
    "sender_aware_signature_preimage",
]
