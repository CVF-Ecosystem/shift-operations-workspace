"""GovernedRetrievalResultV1 - the strict ten-variant union (SPEC R11).
Pure package module.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import Field, model_validator

from .enums import TOKEN_ESTIMATE_METHOD, FinalOutcome
from .evidence_models import EvidenceProjectionV1
from .hashing import citation_id, evidence_set_hash
from .model_base import StrictModel
from .projection import estimate_tokens, serialized_projection_bytes
from .receipt_models import FutureContextHandoffV1, RetrievalReceiptV1


class _BaseResult(StrictModel):
    contract_version: str = Field(default="1.0", pattern=r"^1\.0$")
    receipt: RetrievalReceiptV1
    provider_attempts: Annotated[int, Field(ge=0, le=0, strict=True)] = 0

    @model_validator(mode="after")
    def _outcome_matches_receipt(self) -> "_BaseResult":
        # RR1-F6 - the wrapper's own `outcome` discriminator (declared on
        # every concrete subclass below) must always equal the wrapped
        # receipt's `final_outcome` - a caller cannot construct e.g. an
        # AccessDeniedV1 carrying a NO_EVIDENCE receipt.
        outcome = getattr(self, "outcome", None)
        if outcome is not None and outcome != self.receipt.final_outcome:
            raise ValueError("outcome must equal receipt.final_outcome")
        return self


class EvidenceAvailableV1(_BaseResult):
    outcome: Literal[FinalOutcome.EVIDENCE_AVAILABLE] = FinalOutcome.EVIDENCE_AVAILABLE
    projections: tuple[EvidenceProjectionV1, ...] = Field(min_length=1, max_length=4)
    future_context_handoff: FutureContextHandoffV1

    @model_validator(mode="after")
    def _bindings(self) -> "EvidenceAvailableV1":
        # RR1-F6 - positive projection order maps one-to-one, by position, to
        # both the receipt's citation_ids AND the handoff's citation_ids -
        # each projection's own nested citation, recomputed independently via
        # the same citation_id() helper the application layer uses, never a
        # caller-trusted id list.
        recomputed_ids = tuple(citation_id(p.citation.model_dump(mode="python")) for p in self.projections)
        if recomputed_ids != self.receipt.citation_ids:
            raise ValueError("receipt.citation_ids must equal the projections' recomputed citation ids, in order")
        if recomputed_ids != self.future_context_handoff.citation_ids:
            raise ValueError("future_context_handoff.citation_ids must equal the projections' recomputed citation ids, in order")
        # RR2-F1 - independently recompute every positive fact from the exact
        # ordered projection tuple itself (never trusting receipt/handoff
        # caller-supplied values for any one of them individually), then
        # cross-check ALL of receipt AND handoff against each recomputed
        # value. Coordinated tampering that fixes only one side (e.g. only
        # the outer receipt hash) still fails on every other independent
        # check below.
        citation_dumps = [{"citation": p.citation.model_dump(mode="python")} for p in self.projections]
        projection_dumps = [p.model_dump(mode="python") for p in self.projections]
        recomputed_evidence_hash = evidence_set_hash([d["citation"] for d in citation_dumps], projection_dumps)
        recomputed_bytes = serialized_projection_bytes(projection_dumps)
        recomputed_tokens = estimate_tokens(recomputed_bytes)
        recomputed_codepoints = sum(p.snippet_end_codepoint - p.snippet_start_codepoint for p in self.projections)
        recomputed_count = len(self.projections)
        handoff = self.future_context_handoff
        if self.receipt.evidence_set_hash_sha256 != recomputed_evidence_hash:
            raise ValueError("receipt.evidence_set_hash_sha256 must equal the recomputed evidence-set hash")
        if handoff.evidence_set_hash_sha256 != recomputed_evidence_hash:
            raise ValueError("future_context_handoff.evidence_set_hash_sha256 must equal the recomputed evidence-set hash")
        if handoff.serialized_context_bytes != recomputed_bytes:
            raise ValueError("future_context_handoff.serialized_context_bytes must equal the recomputed serialized byte count")
        if handoff.estimated_input_tokens != recomputed_tokens:
            raise ValueError("future_context_handoff.estimated_input_tokens must equal the recomputed token estimate")
        if handoff.token_estimate_method != TOKEN_ESTIMATE_METHOD:
            raise ValueError("future_context_handoff.token_estimate_method must equal the declared estimate method")
        if handoff.projection_count != recomputed_count or self.receipt.counts.projections_emitted != recomputed_count:
            raise ValueError("handoff.projection_count and receipt.counts.projections_emitted must equal len(projections)")
        if handoff.snippet_codepoints != recomputed_codepoints:
            raise ValueError("future_context_handoff.snippet_codepoints must equal the summed projection snippet spans")
        if handoff.retrieval_receipt_hash_sha256 != self.receipt.receipt_hash_sha256:
            raise ValueError("future_context_handoff.retrieval_receipt_hash_sha256 must equal receipt.receipt_hash_sha256")
        if handoff.classifications != ("INTERNAL",):
            raise ValueError("future_context_handoff.classifications must be exactly ('INTERNAL',)")
        if set(handoff.sensitivities) != {p.sensitivity for p in self.projections}:
            raise ValueError("future_context_handoff.sensitivities must equal the positive projections' sensitivities")
        if handoff.applied_limits != self.receipt.applied_limits:
            raise ValueError("future_context_handoff.applied_limits must equal receipt.applied_limits")
        if handoff.elapsed_ms != self.receipt.elapsed_ms:
            raise ValueError("future_context_handoff.elapsed_ms must equal receipt.elapsed_ms")
        if handoff.configured_timeout_ms != self.receipt.termination.configured_timeout_ms:
            raise ValueError("future_context_handoff.configured_timeout_ms must equal receipt.termination.configured_timeout_ms")
        if handoff.timed_out != self.receipt.termination.timed_out or handoff.cancelled != self.receipt.termination.cancelled:
            raise ValueError("future_context_handoff timed_out/cancelled must equal receipt.termination facts")
        return self


class NoEvidenceV1(_BaseResult):
    outcome: Literal[FinalOutcome.NO_EVIDENCE] = FinalOutcome.NO_EVIDENCE


class AccessDeniedV1(_BaseResult):
    outcome: Literal[FinalOutcome.ACCESS_DENIED] = FinalOutcome.ACCESS_DENIED


class CorpusUnavailableV1(_BaseResult):
    outcome: Literal[FinalOutcome.CORPUS_UNAVAILABLE] = FinalOutcome.CORPUS_UNAVAILABLE


class StaleEvidenceV1(_BaseResult):
    outcome: Literal[FinalOutcome.STALE_EVIDENCE] = FinalOutcome.STALE_EVIDENCE


class RetrievalLimitExceededV1(_BaseResult):
    outcome: Literal[FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED] = FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED


class RetrievalStoppedV1(_BaseResult):
    outcome: Literal[FinalOutcome.RETRIEVAL_TIMEOUT, FinalOutcome.RETRIEVAL_CANCELLED]


class ContextBudgetExceededV1(_BaseResult):
    outcome: Literal[FinalOutcome.CONTEXT_BUDGET_EXCEEDED] = FinalOutcome.CONTEXT_BUDGET_EXCEEDED


class InvalidRequestV1(_BaseResult):
    outcome: Literal[FinalOutcome.INVALID_REQUEST] = FinalOutcome.INVALID_REQUEST


class InvariantFailureV1(_BaseResult):
    outcome: Literal[FinalOutcome.INVARIANT_FAILURE] = FinalOutcome.INVARIANT_FAILURE


GovernedRetrievalResultV1: TypeAlias = (
    EvidenceAvailableV1
    | NoEvidenceV1
    | AccessDeniedV1
    | CorpusUnavailableV1
    | StaleEvidenceV1
    | RetrievalLimitExceededV1
    | RetrievalStoppedV1
    | ContextBudgetExceededV1
    | InvalidRequestV1
    | InvariantFailureV1
)
