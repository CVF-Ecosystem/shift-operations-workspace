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
    SenderAwareIngressRequest,
)
from .verification.hmac import verify_sender_aware_signature
from .verification.sender_keys import (
    SenderTokenKeyAuthority,
    TokenKeyRetirementReadinessV1,
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
    "SenderAwareIngressRequest",
    "SenderTokenKeyAuthority",
    "ServiceAssertionKey",
    "ServiceKeyRegistry",
    "TokenKeyRetirementReadinessV1",
    "decrypt_envelope",
    "emit_ingress_terminal_receipt",
    "emit_outbound_terminal_receipt",
    "encrypt_envelope",
    "sign_service_assertion",
    "verify_sender_aware_signature",
    "verify_service_assertion",
]
