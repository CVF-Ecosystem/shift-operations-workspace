"""P4-A AI Gateway - pure, provider-neutral governed dispatch (bounded).

``AIGateway.execute`` is the only authorized provider-dispatch point in this
project. It calls the three CVF gates - ``assert_placement_allowed``,
``assert_within_budget``, ``assert_not_terminated`` - before any provider I/O.

Bounded claim: this package proves a library call site where those gates precede
dispatch. It does NOT prove an application API uses the gateway, durable usage
accounting, a production provider adapter, RAG, deployment, or production
readiness. Usage accounting is process-local and non-durable.
"""

from __future__ import annotations

from .context import assert_context_admissible
from .errors import (
    AIModeDisabledError,
    BudgetUnavailableError,
    ContextInadmissibleError,
    GatewayError,
    InvalidRequestError,
    NoEvidenceError,
    OutputSchemaError,
    PlacementDeniedError,
    ProviderDispatchError,
    ProviderNotRegisteredError,
    ProviderTimeoutError,
    TerminatedError,
    UsageLedgerError,
)
from .fallback import build_rules_fallback
from .models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    FinalOutcome,
    GateOutcome,
    GateRecord,
    GatewayReceipt,
    GatewayRequest,
    GatewayResult,
    Placement,
    ProviderRequest,
    ProviderResult,
    TerminationFacts,
    UsageReservation,
    canonical_json,
    digest_of,
)
from .provider import AIProvider
from .registry import ProviderRegistry
from .service import AIGateway
from .usage import UsageLedger
from .validation import validate_output

__all__ = [
    "AIGateway",
    "AIMode",
    "AIModeDisabledError",
    "AIProvider",
    "BudgetFacts",
    "BudgetUnavailableError",
    "Classification",
    "ContextFacts",
    "ContextInadmissibleError",
    "FinalOutcome",
    "GateOutcome",
    "GateRecord",
    "GatewayError",
    "GatewayReceipt",
    "GatewayRequest",
    "GatewayResult",
    "InvalidRequestError",
    "NoEvidenceError",
    "OutputSchemaError",
    "Placement",
    "PlacementDeniedError",
    "ProviderDispatchError",
    "ProviderNotRegisteredError",
    "ProviderRegistry",
    "ProviderRequest",
    "ProviderResult",
    "ProviderTimeoutError",
    "TerminatedError",
    "TerminationFacts",
    "UsageLedger",
    "UsageLedgerError",
    "UsageReservation",
    "assert_context_admissible",
    "build_rules_fallback",
    "canonical_json",
    "digest_of",
    "validate_output",
]
