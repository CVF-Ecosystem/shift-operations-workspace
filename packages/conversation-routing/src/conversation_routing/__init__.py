"""Provider-neutral P4-E route-binding and deterministic placement contracts.

Consumes an identity-mapping read port and never mutates mappings. Owns the
`P4E-CONVERSATION-PLACEMENT-OUTCOMES` pinned matrix.
"""

from .models import PlacementDecisionReceipt, RouteBindingV1, conversation_key
from .ports import PlacementWorkPort, RouteBindingRepositoryPort, TargetEligibilityPort
from .service import ConversationRoutingService

__all__ = [
    "ConversationRoutingService",
    "PlacementDecisionReceipt",
    "PlacementWorkPort",
    "RouteBindingRepositoryPort",
    "RouteBindingV1",
    "TargetEligibilityPort",
    "conversation_key",
]
