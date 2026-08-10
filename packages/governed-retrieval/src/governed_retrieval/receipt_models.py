"""RetrievalReceiptV1 and FutureContextHandoffV1 (SPEC R9/R10, receipt
contract appendix). Pure package module.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, utc_datetime

from .enums import (
    RETRIEVAL_STAGE_ORDER,
    TOKEN_ESTIMATE_METHOD,
    CorpusId,
    FinalOutcome,
    RetrievalStage,
    StageOutcome,
    StageReasonCode,
)
from .evidence_models import RetrievalCountsV1, RetrievalLimitsV1, RetrievalStageReceiptV1, TerminationFactsV1
from .hashing import receipt_hash
from .model_base import StrictModel

_DENY, _FAIL = StageOutcome.DENY, StageOutcome.FAIL
_AUTH_FAILED, _ACCESS_DENIED = StageReasonCode.AUTHENTICATION_FAILED, StageReasonCode.ACCESS_DENIED

# RR2-F4/Amendment 3 5.4 - the exact (stage, final_outcome) -> (stage
# outcome, reason_code) grammar every negative receipt's single terminal
# stage must match. Access-denial stages are DENY with a fixed reason;
# every other terminal stage is FAIL with its own outcome-specific reason.
_EXPECTED_TERMINAL: dict[tuple[RetrievalStage, FinalOutcome], tuple[StageOutcome, StageReasonCode]] = {
    (RetrievalStage.AUTHENTICATED, FinalOutcome.ACCESS_DENIED): (_DENY, _AUTH_FAILED),
    (RetrievalStage.PERMISSION_AUTHORIZED, FinalOutcome.ACCESS_DENIED): (_DENY, _ACCESS_DENIED),
    (RetrievalStage.ASSIGNMENT_AUTHORIZED, FinalOutcome.ACCESS_DENIED): (_DENY, _ACCESS_DENIED),
    (RetrievalStage.REVALIDATED, FinalOutcome.ACCESS_DENIED): (_DENY, _ACCESS_DENIED),
    (RetrievalStage.MATCHED_AND_RANKED, FinalOutcome.NO_EVIDENCE): (_FAIL, StageReasonCode.NO_EVIDENCE),
    (RetrievalStage.REVALIDATED, FinalOutcome.STALE_EVIDENCE): (_FAIL, StageReasonCode.STALE_EVIDENCE),
    (RetrievalStage.PROJECTED, FinalOutcome.CONTEXT_BUDGET_EXCEEDED): (_FAIL, StageReasonCode.CONTEXT_BUDGET_EXCEEDED),
}
# REQUEST_VALIDATED=FAIL carries any of the eight closed R2 request-failure
# codes; CORPUS_RESOLVED=FAIL for INVALID_REQUEST carries either post-
# authorization corpus code - both are matched by reason-code set below
# rather than one fixed pair (see _matches_invalid_request_terminal).
_R2_CODES = frozenset(
    {
        StageReasonCode.REQUEST_SHAPE_INVALID, StageReasonCode.QUERY_INVALID,
        StageReasonCode.QUERY_LIMIT_EXCEEDED, StageReasonCode.CORPUS_ID_INVALID,
        StageReasonCode.FILTER_INVALID, StageReasonCode.FILTER_WIDENS_SCOPE,
        StageReasonCode.RESULT_LIMIT_INVALID, StageReasonCode.CONTEXT_BUDGET_INVALID,
    }
)
_CORPUS_STAGE_CODES = frozenset({StageReasonCode.CORPUS_ID_INVALID, StageReasonCode.FILTER_WIDENS_SCOPE})
for _stage in (RetrievalStage.CORPUS_RESOLVED, RetrievalStage.SOURCES_READ, RetrievalStage.P3C_ADMITTED):
    # RR3-F2 - an ordinary P3-A/P3-C construction exception during initial
    # candidate admission also terminates at P3C_ADMITTED as CORPUS_UNAVAILABLE.
    _EXPECTED_TERMINAL[(_stage, FinalOutcome.CORPUS_UNAVAILABLE)] = (_FAIL, StageReasonCode.CORPUS_UNAVAILABLE)
for _stage in (RetrievalStage.SOURCES_READ, RetrievalStage.P3C_ADMITTED):
    _EXPECTED_TERMINAL[(_stage, FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED)] = (
        _FAIL, StageReasonCode.RETRIEVAL_LIMIT_EXCEEDED,
    )
_EXPECTED_TERMINAL[(RetrievalStage.P3C_ADMITTED, FinalOutcome.INVARIANT_FAILURE)] = (
    _FAIL, StageReasonCode.INVARIANT_FAILURE,
)
for _stage in RetrievalStage:
    if _stage == RetrievalStage.RECEIPT_EMITTED:
        continue
    _EXPECTED_TERMINAL[(_stage, FinalOutcome.RETRIEVAL_TIMEOUT)] = (_FAIL, StageReasonCode.RETRIEVAL_TIMEOUT)
    _EXPECTED_TERMINAL[(_stage, FinalOutcome.RETRIEVAL_CANCELLED)] = (_FAIL, StageReasonCode.RETRIEVAL_CANCELLED)


class RetrievalReceiptV1(StrictModel):
    """SPEC R9 / receipt contract appendix - exact receipt field set."""

    contract_version: str = Field(default="1.0", pattern=r"^1\.0$")
    receipt_id: UUID
    retrieval_correlation_id: UUID
    started_at_utc: datetime
    finished_at_utc: datetime
    source_cutoff_utc: datetime | None
    elapsed_ms: Annotated[int, Field(ge=0, strict=True)]
    corpus_id: CorpusId | None
    authorization_scope_digest_sha256: Digest | None
    stages: tuple[RetrievalStageReceiptV1, ...] = Field(min_length=11, max_length=11)
    final_outcome: FinalOutcome
    requested_limits: RetrievalLimitsV1 | None
    applied_limits: RetrievalLimitsV1 | None
    counts: RetrievalCountsV1
    termination: TerminationFactsV1
    citation_ids: tuple[Digest, ...]
    evidence_set_hash_sha256: Digest | None
    receipt_hash_sha256: Digest

    @model_validator(mode="after")
    def _stage_order_and_time(self) -> "RetrievalReceiptV1":
        stage_names = tuple(s.stage for s in self.stages)
        if stage_names != RETRIEVAL_STAGE_ORDER:
            raise ValueError("stages must appear in the exact eleven-stage order")
        if self.receipt_id.version != 4:
            raise ValueError("receipt_id must be a UUIDv4")
        if self.retrieval_correlation_id.version != 4:
            raise ValueError("retrieval_correlation_id must be a UUIDv4")
        # RR2-F3 - the two service-allocated identities must be distinct.
        if self.receipt_id == self.retrieval_correlation_id:
            raise ValueError("receipt_id and retrieval_correlation_id must be distinct")
        receipt_emitted = next(s for s in self.stages if s.stage == RetrievalStage.RECEIPT_EMITTED)
        if receipt_emitted.outcome != StageOutcome.PASS:
            raise ValueError("RECEIPT_EMITTED must be PASS for every returned receipt")
        if self.corpus_id is not None:
            corpus_resolved = next(s for s in self.stages if s.stage == RetrievalStage.CORPUS_RESOLVED)
            if corpus_resolved.outcome != StageOutcome.PASS:
                raise ValueError("corpus_id must be null unless CORPUS_RESOLVED passed")
        utc_datetime(self.started_at_utc)
        utc_datetime(self.finished_at_utc)
        if self.source_cutoff_utc is not None:
            utc_datetime(self.source_cutoff_utc)
        if self.finished_at_utc < self.started_at_utc:
            raise ValueError("finished_at_utc must not precede started_at_utc")
        # RR3-F4 - positive elapsed_ms requires a strictly later finish; an
        # equal wall-clock interval is only valid for elapsed_ms == 0.
        if self.elapsed_ms > 0 and self.finished_at_utc <= self.started_at_utc:
            raise ValueError("elapsed_ms > 0 requires finished_at_utc strictly later than started_at_utc")
        if self.source_cutoff_utc is not None:
            if self.source_cutoff_utc < self.started_at_utc or self.source_cutoff_utc > self.finished_at_utc:
                raise ValueError("source_cutoff_utc must fall between started_at_utc and finished_at_utc")
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("citation_ids must be duplicate-free")
        self._require_valid_stage_grammar()
        if self.final_outcome == FinalOutcome.EVIDENCE_AVAILABLE:
            if self.evidence_set_hash_sha256 is None:
                raise ValueError("evidence_set_hash_sha256 required for EVIDENCE_AVAILABLE")
        else:
            if self.citation_ids:
                raise ValueError("citation_ids must be empty for a negative outcome")
            if self.evidence_set_hash_sha256 is not None:
                raise ValueError("evidence_set_hash_sha256 must be null for a negative outcome")
        # RR1-F6 - receipt_hash_sha256 is never trusted from the caller: it
        # is independently recomputed here from the canonical dump of every
        # OTHER field (only receipt_hash_sha256 itself omitted, exactly as
        # the appendix requires) using the same explicit `hashing.receipt_hash`
        # preimage helper the builder uses - no recursive self-reference,
        # since this validator runs once at construction over already-built
        # field values, never re-entering model construction.
        canonical_dump = self.model_dump(mode="python")
        canonical_dump.pop("receipt_hash_sha256")
        if receipt_hash(canonical_dump) != self.receipt_hash_sha256:
            raise ValueError("receipt_hash_sha256 must equal the recomputed canonical receipt hash")
        return self

    def _require_valid_stage_grammar(self) -> None:
        """RR2-F4/RR2-F5/Amendment 3 5.4 - the eleven-stage history must be
        one of exactly two shapes: EVIDENCE_AVAILABLE has the first ten PASS
        plus RECEIPT_EMITTED=PASS; every negative outcome has exactly one
        terminal DENY/FAIL among the first ten (stages before it PASS,
        stages after it NOT_RUN) with the exact stage/reason pairing this
        outcome requires, then RECEIPT_EMITTED=PASS."""
        operational = self.stages[:10]
        if self.final_outcome == FinalOutcome.EVIDENCE_AVAILABLE:
            if any(s.outcome != StageOutcome.PASS for s in operational):
                raise ValueError("EVIDENCE_AVAILABLE requires PASS for all ten operational stages")
            return
        terminal_index = next((i for i, s in enumerate(operational) if s.outcome != StageOutcome.PASS), None)
        if terminal_index is None:
            raise ValueError("a negative receipt must have exactly one terminal FAIL/DENY stage")
        terminal = operational[terminal_index]
        for s in operational[terminal_index + 1 :]:
            if s.outcome != StageOutcome.NOT_RUN:
                raise ValueError("stages after the terminal stage must be NOT_RUN")
        if self.final_outcome == FinalOutcome.INVALID_REQUEST:
            valid = (
                (terminal.stage == RetrievalStage.REQUEST_VALIDATED and terminal.reason_code in _R2_CODES)
                or (terminal.stage == RetrievalStage.CORPUS_RESOLVED and terminal.reason_code in _CORPUS_STAGE_CODES)
            )
            if not valid or terminal.outcome != StageOutcome.FAIL:
                raise ValueError("INVALID_REQUEST terminal stage/reason does not match the required grammar")
            return
        expected = _EXPECTED_TERMINAL.get((terminal.stage, self.final_outcome))
        if expected is None or terminal.outcome != expected[0] or terminal.reason_code != expected[1]:
            raise ValueError("terminal stage outcome/reason does not match the required grammar for this outcome")


class FutureContextHandoffV1(StrictModel):
    """SPEC R10 - exact fields; evidence for a future context builder, not
    P3-B satisfaction."""

    retrieval_receipt_hash_sha256: Digest
    evidence_set_hash_sha256: Digest
    citation_ids: tuple[Digest, ...] = Field(min_length=1)
    classifications: tuple[str, ...]
    sensitivities: tuple[str, ...]
    serialized_context_bytes: Annotated[int, Field(ge=0, strict=True)]
    snippet_codepoints: Annotated[int, Field(ge=0, strict=True)]
    projection_count: Annotated[int, Field(ge=1, strict=True)]
    estimated_input_tokens: Annotated[int, Field(ge=0, strict=True)]
    token_estimate_method: str = Field(default=TOKEN_ESTIMATE_METHOD, pattern=rf"^{TOKEN_ESTIMATE_METHOD}$")
    applied_limits: RetrievalLimitsV1
    elapsed_ms: Annotated[int, Field(ge=0, strict=True)]
    configured_timeout_ms: Annotated[int, Field(ge=1, strict=True)]
    timed_out: bool
    cancelled: bool
    minimization_evidence_status: str = Field(default="NOT_PROVEN", pattern=r"^NOT_PROVEN$")
    placement_enforcement_status: str = Field(default="NOT_EVALUATED", pattern=r"^NOT_EVALUATED$")
    runtime_caller_status: str = Field(
        default="NO_LOAD_BEARING_CALLER", pattern=r"^NO_LOAD_BEARING_CALLER$"
    )
    provider_attempt_authorized: bool = Field(default=False)
    provider_attempts: Annotated[int, Field(ge=0, le=0, strict=True)] = 0

    @model_validator(mode="after")
    def _closed_facts(self) -> "FutureContextHandoffV1":
        if tuple(sorted(set(self.classifications))) != tuple(sorted(self.classifications)):
            raise ValueError("classifications must be duplicate-free")
        if tuple(sorted(set(self.sensitivities))) != tuple(sorted(self.sensitivities)):
            raise ValueError("sensitivities must be duplicate-free")
        if self.classifications != tuple(sorted(self.classifications)):
            raise ValueError("classifications must be sorted")
        if self.sensitivities != tuple(sorted(self.sensitivities)):
            raise ValueError("sensitivities must be sorted")
        if len(set(self.citation_ids)) != len(self.citation_ids):
            raise ValueError("citation_ids must be duplicate-free")
        if self.provider_attempt_authorized is not False:
            raise ValueError("provider_attempt_authorized must be false")
        if self.provider_attempts != 0:
            raise ValueError("provider_attempts must be zero")
        if self.timed_out and self.cancelled:
            raise ValueError("timed_out and cancelled cannot both be true")
        return self
