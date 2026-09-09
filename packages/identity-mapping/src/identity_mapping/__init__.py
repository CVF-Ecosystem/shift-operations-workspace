"""Provider-neutral P4-E external-identity and mapping contracts.

Owns identity-semantic key derivation, the mapping aggregate/lifecycle, and
the two pinned matrices (`P4E-MAPPING-ACTION-OUTCOMES`,
`P4E-IDENTITY-RESOLUTION-OUTCOMES`). Imports no Workspace API type.
"""

from .crypto import (
    derive_sender_token,
    external_identity_key_digest,
    normalize_sender_bytes,
)
from .models import (
    ExternalIdentityKeyV1,
    IdentityMappingV1,
    IdentityResolutionResult,
    MappingActionReceipt,
    SenderEvidenceV1,
    SenderObservationV1,
    mapping_transition_allowed,
)
from .ports import IdentityMappingReadPort, IdentityMappingRepositoryPort, SenderTokenKeyPort
from .retention import privacy_delete
from .service import IdentityMappingService, MappingActionRefused

__all__ = [
    "ExternalIdentityKeyV1",
    "IdentityMappingReadPort",
    "IdentityMappingRepositoryPort",
    "IdentityMappingService",
    "IdentityMappingV1",
    "IdentityResolutionResult",
    "MappingActionRefused",
    "MappingActionReceipt",
    "SenderEvidenceV1",
    "SenderObservationV1",
    "SenderTokenKeyPort",
    "derive_sender_token",
    "external_identity_key_digest",
    "mapping_transition_allowed",
    "normalize_sender_bytes",
    "privacy_delete",
]
