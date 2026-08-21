"""Typed application-memory errors and stable reason codes (SPEC R4/R6/R7/R8).

Pure package module: standard library only. Every error carries a fixed
``reason_code`` so receipts and tests can assert an outcome without parsing
prose. No error message may ever embed content body, source body, a credential
or raw exception text - callers build messages from safe identifiers only.
"""

from __future__ import annotations


class ApplicationMemoryError(RuntimeError):
    """Base class. ``reason_code`` is the stable, assertable outcome name."""

    reason_code = "APPLICATION_MEMORY_ERROR"

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail or self.reason_code)
        self.detail = detail


class RequestInvalidError(ApplicationMemoryError):
    """The strict admission/correction request failed validation."""

    reason_code = "REQUEST_INVALID"


class UnsupportedPurposeError(ApplicationMemoryError):
    """The purpose code is outside the closed enum (SPEC R4)."""

    reason_code = "UNSUPPORTED_PURPOSE"


class ClassificationRejectedError(ApplicationMemoryError):
    """The classification is RESTRICTED/unknown and must fail closed (SPEC R4)."""

    reason_code = "CLASSIFICATION_REJECTED"


class AuthorizationScopeMismatchError(ApplicationMemoryError):
    """The caller's owner/shift/authorization-scope digest does not exactly
    match the target entry's bound scope (SPEC R5/R6)."""

    reason_code = "AUTHORIZATION_SCOPE_MISMATCH"


class SourceRevalidationFailedError(ApplicationMemoryError):
    """The injected revalidator did not return a positive, source-bound
    result (SPEC R5/R8)."""

    reason_code = "SOURCE_REVALIDATION_FAILED"


class DuplicateEntryError(ApplicationMemoryError):
    """An entry id already exists (append-only store never overwrites)."""

    reason_code = "DUPLICATE_ENTRY"


class EntryNotFoundError(ApplicationMemoryError):
    """The target entry id is unknown to the store."""

    reason_code = "ENTRY_NOT_FOUND"


class EntryNotActiveError(ApplicationMemoryError):
    """The target entry is already tombstoned (corrected/deleted)."""

    reason_code = "ENTRY_NOT_ACTIVE"


class EntryExpiredError(ApplicationMemoryError):
    """The target entry has expired (``now >= expires_at``)."""

    reason_code = "ENTRY_EXPIRED"


class CorrectionLineageError(ApplicationMemoryError):
    """A correction's predecessor binding is missing, self-referential, or
    otherwise invalid (SPEC R7)."""

    reason_code = "CORRECTION_LINEAGE_INVALID"


class BudgetBreachError(ApplicationMemoryError):
    """Admission would exceed a content/budget ceiling (SPEC R6)."""

    reason_code = "BUDGET_BREACH"


class ResultLimitError(ApplicationMemoryError):
    """The requested read limit is outside 1..50 (SPEC R8)."""

    reason_code = "RESULT_LIMIT_INVALID"
