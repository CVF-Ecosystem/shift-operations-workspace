"""Typed governed-RAG errors and their stable reason codes (SPEC R4/R8/R9/
R10/R13/R14). Pure package module: standard library only.

Every error carries a fixed ``reason_code`` string so receipts and tests can
assert an outcome without parsing prose. No error message may ever embed
query text, evidence/context body, provider output, a credential or raw
exception text - callers build messages from safe identifiers only.
"""

from __future__ import annotations


class GovernedRagError(RuntimeError):
    """Base class. ``reason_code`` is the stable, assertable outcome name."""

    reason_code = "GOVERNED_RAG_ERROR"

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail or self.reason_code)
        self.detail = detail


class RequestInvalidError(GovernedRagError):
    """The strict RAG request/policy/execution facts failed validation."""

    reason_code = "REQUEST_INVALID"


class RetrievalNotPositiveError(GovernedRagError):
    """P4-A1 did not return ``EvidenceAvailableV1`` (SPEC R4)."""

    reason_code = "RETRIEVAL_NOT_POSITIVE"


class BindingMismatchError(GovernedRagError):
    """A recomputed P4-A1 receipt/handoff/projection/citation/evidence-set
    binding did not match the caller-supplied positive result (SPEC R5)."""

    reason_code = "BINDING_MISMATCH"


class ScopeWideningError(GovernedRagError):
    """P4-A2 output would widen corpus, authorization scope, source, record,
    chunk, citation, truth class or field selector beyond the exact granted
    P4-A1 projection set (SPEC R5)."""

    reason_code = "SCOPE_WIDENING_REJECTED"


class StaleIndexError(GovernedRagError):
    """The ephemeral index is missing/extra/duplicate/partial/altered, or its
    encoder/version/lexicon/build digest does not match (SPEC R8)."""

    reason_code = "STALE_INDEX"


class InjectionBlockedError(GovernedRagError):
    """Every evidence projection was omitted as contaminated (SPEC R9)."""

    reason_code = "INJECTION_BLOCKED"


class MinimizationFailedError(GovernedRagError):
    """Extractive minimization produced no output record, or its recomputed
    proof does not match (SPEC R10)."""

    reason_code = "MINIMIZATION_FAILED"


class ContextBudgetExceededError(GovernedRagError):
    """Assembled context exceeds P4-A1 handoff limits or P4-A policy budget,
    or the declared ``context_digest`` does not equal the actual assembled
    context (SPEC R11)."""

    reason_code = "CONTEXT_BUDGET_EXCEEDED"


class OutputValidationFailedError(GovernedRagError):
    """Gateway output violated the strict answer schema, cited an unknown or
    duplicate citation, left a claim uncited, or otherwise broke the
    ANSWER/ABSTAIN invariants (SPEC R13)."""

    reason_code = "OUTPUT_VALIDATION_FAILED"


class GatewayNotAcceptedError(GovernedRagError):
    """The injected ``AIGateway.execute`` call returned a non-accepted
    result (refused pre-dispatch, failed post-dispatch, or fallback) (SPEC
    R14)."""

    reason_code = "GATEWAY_NOT_ACCEPTED"


class PlacementRefusedError(GovernedRagError):
    """The engine's bound placement is EXTERNAL but this execution's
    minimization proof does not allow external placement - refused before
    any gateway/provider dispatch (P4A2-REV-F3)."""

    reason_code = "PLACEMENT_REFUSED"


class ScopeMismatchError(GovernedRagError):
    """The request's declared corpus identity or authorization-scope digest
    does not exactly equal the independently verified P4-A1 receipt/handoff
    value for this execution (P4A2-REV-F4)."""

    reason_code = "SCOPE_MISMATCH"
