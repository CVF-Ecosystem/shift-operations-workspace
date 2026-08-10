"""governed-retrieval: pure P4-A1 local governed retrieval foundation.

Owns V1 request/result models, immutable corpus descriptors, normalization,
lexical ranking, projection, and canonical receipt hashing. Imports only the
standard library, Pydantic, and the public ``retrieval_contracts`` package.
Performs no I/O, clock/id creation, secret lookup, environment, auth,
Ledger, API, network, provider, or audit access - see
docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md R1.
"""

from .corpus import CORPUS_REGISTRY, CorpusDescriptor, is_available, resolve_corpus
from .enums import CorpusId, CorpusState, FinalOutcome, RequestFailureCode, RetrievalStage, StageOutcome
from .evidence_models import (
    CitationV1,
    EvidenceProjectionV1,
    RetrievalCountsV1,
    RetrievalLimitsV1,
    RetrievalStageReceiptV1,
    TerminationFactsV1,
)
from .receipt_models import FutureContextHandoffV1, RetrievalReceiptV1
from .request_models import ContextBudgetV1, GovernedRetrievalRequestV1, RetrievalFiltersV1, RequestValidationError
from .result_models import (
    AccessDeniedV1,
    ContextBudgetExceededV1,
    CorpusUnavailableV1,
    EvidenceAvailableV1,
    GovernedRetrievalResultV1,
    InvalidRequestV1,
    InvariantFailureV1,
    NoEvidenceV1,
    RetrievalLimitExceededV1,
    RetrievalStoppedV1,
    StaleEvidenceV1,
)

__all__ = [
    "CORPUS_REGISTRY",
    "CorpusDescriptor",
    "CorpusId",
    "CorpusState",
    "FinalOutcome",
    "RequestFailureCode",
    "RetrievalStage",
    "StageOutcome",
    "is_available",
    "resolve_corpus",
    "CitationV1",
    "EvidenceProjectionV1",
    "RetrievalCountsV1",
    "RetrievalLimitsV1",
    "RetrievalStageReceiptV1",
    "TerminationFactsV1",
    "FutureContextHandoffV1",
    "RetrievalReceiptV1",
    "ContextBudgetV1",
    "GovernedRetrievalRequestV1",
    "RetrievalFiltersV1",
    "RequestValidationError",
    "AccessDeniedV1",
    "ContextBudgetExceededV1",
    "CorpusUnavailableV1",
    "EvidenceAvailableV1",
    "GovernedRetrievalResultV1",
    "InvalidRequestV1",
    "InvariantFailureV1",
    "NoEvidenceV1",
    "RetrievalLimitExceededV1",
    "RetrievalStoppedV1",
    "StaleEvidenceV1",
]
