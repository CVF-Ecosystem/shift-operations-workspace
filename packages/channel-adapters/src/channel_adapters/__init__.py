"""Bounded P4-D channel adapters."""

from .conformance import WhatsAppConformanceAdapter, ZaloConformanceAdapter, emit_adapter_result
from .egress import GenericWebhookConfig, authorize_endpoint
from .generic_webhook import GenericWebhookAdapter
from .transport import StdlibResolvedHttpsTransport

__all__ = [
    "GenericWebhookAdapter",
    "GenericWebhookConfig",
    "StdlibResolvedHttpsTransport",
    "WhatsAppConformanceAdapter",
    "ZaloConformanceAdapter",
    "authorize_endpoint",
    "emit_adapter_result",
]
