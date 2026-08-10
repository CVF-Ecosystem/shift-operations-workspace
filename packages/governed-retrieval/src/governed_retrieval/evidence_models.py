"""CitationV1, EvidenceProjectionV1, and closed receipt nested models (SPEC
R8/R9, receipt contract appendix). Pure package module: standard library,
Pydantic, and ``retrieval_contracts`` only.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field, model_validator
from retrieval_contracts.canonical import sha256_bytes
from retrieval_contracts.common import Digest, SafeId, utc_datetime
from retrieval_contracts.contract_models import VersionBindingV1
from retrieval_contracts.enums import RecordType, TruthClass

from .enums import RetrievalStage, StageOutcome, StageReasonCode
from .model_base import StrictModel


class CitationV1(StrictModel):
    """Receipt contract appendix - rejects unknown fields; a path alone or a
    missing digest/version is invalid (enforced by required, non-optional
    fields below)."""

    chunk_id: Digest
    content_digest_sha256: Digest
    source_digest_sha256: Digest
    version: VersionBindingV1
    truth_class: TruthClass
    record_type: RecordType
    record_id: SafeId | None = None
    source_id: SafeId | None = None
    field_selector: SafeId
    revalidation_token: Digest
    source_cutoff_utc: datetime
    snippet_digest_sha256: Digest
    snippet_start_codepoint: Annotated[int, Field(ge=0, strict=True)]
    snippet_end_codepoint: Annotated[int, Field(ge=0, strict=True)]

    @model_validator(mode="after")
    def _exactly_one_id_and_valid_offsets(self) -> "CitationV1":
        has_record = self.record_id is not None
        has_source = self.source_id is not None
        if has_record == has_source:
            raise ValueError("exactly one of record_id or source_id required")
        if self.snippet_end_codepoint < self.snippet_start_codepoint:
            raise ValueError("snippet offsets inverted")
        utc_datetime(self.source_cutoff_utc)
        return self


class EvidenceProjectionV1(StrictModel):
    """SPEC R8 - rejects unknown fields; nested citation values must match
    the projection's own duplicated fields exactly."""

    citation: CitationV1
    truth_class: TruthClass
    field_selector: SafeId
    sensitivity: str
    content_snippet: str
    snippet_start_codepoint: Annotated[int, Field(ge=0, strict=True)]
    snippet_end_codepoint: Annotated[int, Field(ge=0, strict=True)]
    snippet_digest_sha256: Digest
    projection_complete: bool

    @model_validator(mode="after")
    def _matches_nested_citation(self) -> "EvidenceProjectionV1":
        if self.truth_class != self.citation.truth_class:
            raise ValueError("truth_class must equal nested citation value")
        if self.field_selector != self.citation.field_selector:
            raise ValueError("field_selector must equal nested citation value")
        if self.snippet_digest_sha256 != self.citation.snippet_digest_sha256:
            raise ValueError("snippet_digest_sha256 must equal nested citation value")
        if self.snippet_start_codepoint != self.citation.snippet_start_codepoint:
            raise ValueError("snippet_start_codepoint must equal nested citation value")
        if self.snippet_end_codepoint != self.citation.snippet_end_codepoint:
            raise ValueError("snippet_end_codepoint must equal nested citation value")
        if self.snippet_end_codepoint < self.snippet_start_codepoint:
            raise ValueError("snippet offsets inverted")
        # RR1-F6 - content_snippet is never empty, its code-point length
        # equals the declared offset range EXACTLY, and its independently
        # recomputed SHA-256 equals the declared digest - never a
        # tautological self-comparison and never trusted from the builder.
        if not self.content_snippet:
            raise ValueError("content_snippet must not be empty")
        if len(self.content_snippet) != self.snippet_end_codepoint - self.snippet_start_codepoint:
            raise ValueError("content_snippet code-point length must equal the declared offset range")
        recomputed_digest = sha256_bytes(self.content_snippet.encode("utf-8"))
        if recomputed_digest != self.snippet_digest_sha256:
            raise ValueError("snippet_digest_sha256 must equal the recomputed content_snippet digest")
        return self


class RetrievalCountsV1(StrictModel):
    """Receipt contract appendix - exactly these seven non-negative ints."""

    source_records_read: Annotated[int, Field(ge=0, strict=True)]
    candidates_admitted: Annotated[int, Field(ge=0, strict=True)]
    matches_ranked: Annotated[int, Field(ge=0, strict=True)]
    selected_for_revalidation: Annotated[int, Field(ge=0, strict=True)]
    stale_omitted: Annotated[int, Field(ge=0, strict=True)]
    projections_emitted: Annotated[int, Field(ge=0, strict=True)]
    projections_budget_omitted: Annotated[int, Field(ge=0, strict=True)]


class RetrievalLimitsV1(StrictModel):
    """Receipt contract appendix - result_limit plus the five R2
    context-budget fields."""

    result_limit: Annotated[int, Field(ge=1, le=20, strict=True)]
    max_projection_records: Annotated[int, Field(ge=1, strict=True)]
    max_snippet_codepoints: Annotated[int, Field(ge=1, strict=True)]
    max_snippet_utf8_bytes: Annotated[int, Field(ge=1, strict=True)]
    max_serialized_utf8_bytes: Annotated[int, Field(ge=1, strict=True)]
    max_estimated_input_tokens: Annotated[int, Field(ge=1, strict=True)]


class TerminationFactsV1(StrictModel):
    """Receipt contract appendix - positive timeout plus two booleans that
    cannot both be true."""

    configured_timeout_ms: Annotated[int, Field(ge=1, strict=True)]
    timed_out: bool
    cancelled: bool

    @model_validator(mode="after")
    def _not_both(self) -> "TerminationFactsV1":
        if self.timed_out and self.cancelled:
            raise ValueError("timed_out and cancelled cannot both be true")
        return self


class RetrievalStageReceiptV1(StrictModel):
    """Receipt contract appendix - one stage's outcome, reason, and safe
    cumulative counts."""

    stage: RetrievalStage
    outcome: StageOutcome
    reason_code: StageReasonCode | None
    safe_counts: RetrievalCountsV1

    @model_validator(mode="after")
    def _reason_matches_outcome(self) -> "RetrievalStageReceiptV1":
        if self.outcome in (StageOutcome.PASS, StageOutcome.NOT_RUN):
            if self.reason_code is not None:
                raise ValueError("reason_code must be null for PASS/NOT_RUN")
        else:
            if self.reason_code is None:
                raise ValueError("reason_code required for DENY/FAIL")
        return self
