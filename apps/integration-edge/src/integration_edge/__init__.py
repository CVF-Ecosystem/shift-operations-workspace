"""Provider-neutral P4-C Integration Edge contracts."""

from .crypto import (
    EncryptedEnvelope,
    InMemoryKeyRegistry,
    KeyRegistry,
    decrypt_envelope,
    encrypt_envelope,
)
from .invariants import (
    emit_ingress_terminal_receipt,
    emit_outbound_terminal_receipt,
)
from .models import (
    CandidateProposal,
    IngressReceipt,
    OutboundCommand,
    OutboundReceipt,
    RawEnvelope,
)
from .verification.service_assertion import (
    InMemoryNonceStore,
    ServiceAssertionKey,
    ServiceKeyRegistry,
    sign_service_assertion,
    verify_service_assertion,
)

__all__ = [
    "CandidateProposal",
    "EncryptedEnvelope",
    "IngressReceipt",
    "InMemoryKeyRegistry",
    "InMemoryNonceStore",
    "KeyRegistry",
    "OutboundCommand",
    "OutboundReceipt",
    "RawEnvelope",
    "ServiceAssertionKey",
    "ServiceKeyRegistry",
    "decrypt_envelope",
    "emit_ingress_terminal_receipt",
    "emit_outbound_terminal_receipt",
    "encrypt_envelope",
    "sign_service_assertion",
    "verify_service_assertion",
]
