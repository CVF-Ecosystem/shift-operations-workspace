"""governed-rag: pure P4-A2 governed RAG composition layer.

Consumes only a positive P4-A1 ``EvidenceAvailableV1`` result and calls an
injected, already-configured ``ai_gateway.service.AIGateway`` at most once.
Imports only the standard library, Pydantic, ``governed_retrieval``,
``retrieval_contracts`` and ``ai_gateway`` - see
docs/specs/P4A2_GOVERNED_RAG_SPEC.md R1. Performs no I/O, clock/id creation,
secret lookup, environment, database, network or hidden-Core access.
"""

from .errors import (
    BindingMismatchError,
    ContextBudgetExceededError,
    GatewayNotAcceptedError,
    GovernedRagError,
    InjectionBlockedError,
    MinimizationFailedError,
    OutputValidationFailedError,
    PlacementRefusedError,
    RequestInvalidError,
    RetrievalNotPositiveError,
    ScopeMismatchError,
    ScopeWideningError,
    StaleIndexError,
)
from .context import AssembledContextV1, ContextFactsV1, InstructionContractV1
from .injection import InjectionOmissionV1, InjectionReasonCode
from .minimization import (
    MinimizationOmissionReason,
    MinimizationProofV1,
    MinimizationRecordProofV1,
    MinimizedEvidenceRecordV1,
)
from .models import (
    ContextBudgetPolicyV1,
    EphemeralIndexV1,
    GovernedRagRequestV1,
    IndexEntryV1,
    RankedRecord,
    ScoredCitationV1,
    rank_projections,
)
from .receipts import GovernedRagReceiptV1, RagFinalOutcome, RagStage, RagStageOutcome, RagStageReceiptV1
from .service import GovernedRAG, GovernedRagOutcome
from .validation import AnswerStatus, ClaimV1, GovernedRagAnswerV1, ReceiptContext

__all__ = [
    "GovernedRAG",
    "GovernedRagOutcome",
    "GovernedRagError",
    "RequestInvalidError",
    "RetrievalNotPositiveError",
    "BindingMismatchError",
    "ScopeWideningError",
    "StaleIndexError",
    "InjectionBlockedError",
    "MinimizationFailedError",
    "ContextBudgetExceededError",
    "OutputValidationFailedError",
    "GatewayNotAcceptedError",
    "AnswerStatus",
    "AssembledContextV1",
    "ClaimV1",
    "ContextBudgetPolicyV1",
    "ContextFactsV1",
    "EphemeralIndexV1",
    "GovernedRagAnswerV1",
    "GovernedRagReceiptV1",
    "GovernedRagRequestV1",
    "IndexEntryV1",
    "InjectionOmissionV1",
    "InjectionReasonCode",
    "InstructionContractV1",
    "MinimizationOmissionReason",
    "MinimizationProofV1",
    "MinimizationRecordProofV1",
    "MinimizedEvidenceRecordV1",
    "PlacementRefusedError",
    "RagFinalOutcome",
    "RagStage",
    "RagStageOutcome",
    "RagStageReceiptV1",
    "RankedRecord",
    "ReceiptContext",
    "ScopeMismatchError",
    "ScoredCitationV1",
    "rank_projections",
]
