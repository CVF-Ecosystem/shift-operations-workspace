"""application-memory: pure P4-A3 session/working application memory layer.

Imports only the standard library, Pydantic and ``retrieval_contracts`` - see
``pyproject.toml``. Performs no I/O, provider, environment, database, network
or hidden-Core access. See ``docs/specs/P4A3_APPLICATION_MEMORY_SPEC.md`` R1.
"""

from .errors import (
    ApplicationMemoryError,
    AuthorizationScopeMismatchError,
    BudgetBreachError,
    CorrectionLineageError,
    DuplicateEntryError,
    EntryExpiredError,
    EntryNotFoundError,
    EntryNotActiveError,
    RequestInvalidError,
    ResultLimitError,
    SourceRevalidationFailedError,
)
from .hashing import content_digest, entry_digest, provenance_digest, receipt_hash
from .models import (
    MAX_CONTENT_CODEPOINTS,
    MAX_CONTENT_UTF8_BYTES,
    AdmissionRequestV1,
    MemoryClassification,
    MemoryEntryV1,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryOperation,
    MemoryPurpose,
    SourceRefV1,
    SourceRevalidationOutcome,
    SourceRevalidationV1,
    SourceType,
    TombstoneReason,
    TombstoneV1,
)
from .policy import (
    MAX_RESULT_LIMIT,
    MIN_RESULT_LIMIT,
    SESSION_MAX_TTL_SECONDS,
    WORKING_MAX_TTL_SECONDS,
    compute_expiry,
    is_expired,
    max_ttl_seconds,
    normalize_content,
    validate_result_limit,
)
from .receipts import MemoryReceiptV1, build_receipt
from .service import ApplicationMemory, MemoryOutcome
from .store import InMemoryApplicationMemoryStore

__all__ = [
    "ApplicationMemory",
    "MemoryOutcome",
    "InMemoryApplicationMemoryStore",
    "ApplicationMemoryError",
    "RequestInvalidError",
    "AuthorizationScopeMismatchError",
    "SourceRevalidationFailedError",
    "DuplicateEntryError",
    "EntryNotFoundError",
    "EntryNotActiveError",
    "EntryExpiredError",
    "CorrectionLineageError",
    "BudgetBreachError",
    "ResultLimitError",
    "MemoryLayer",
    "MemoryPurpose",
    "MemoryClassification",
    "SourceType",
    "SourceRevalidationOutcome",
    "TombstoneReason",
    "MemoryOperation",
    "MemoryFinalOutcome",
    "SourceRefV1",
    "SourceRevalidationV1",
    "AdmissionRequestV1",
    "MemoryEntryV1",
    "TombstoneV1",
    "MemoryReceiptV1",
    "build_receipt",
    "content_digest",
    "entry_digest",
    "provenance_digest",
    "receipt_hash",
    "MAX_CONTENT_CODEPOINTS",
    "MAX_CONTENT_UTF8_BYTES",
    "SESSION_MAX_TTL_SECONDS",
    "WORKING_MAX_TTL_SECONDS",
    "MIN_RESULT_LIMIT",
    "MAX_RESULT_LIMIT",
    "max_ttl_seconds",
    "normalize_content",
    "compute_expiry",
    "is_expired",
    "validate_result_limit",
]
