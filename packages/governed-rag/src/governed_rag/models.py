"""Strict governed-RAG shared contracts (SPEC R2/R7/R8).

Every model here rejects unknown fields, is frozen, and reuses
``retrieval_contracts.common.StrictModel`` (extra="forbid", strict=True,
frozen=True, NFC-only strings) so canonical hashing stays byte-deterministic.
This module performs no I/O, no clock/id creation, and no provider access -
every timestamp/digest/id is supplied by the caller. Closed enums bound every
discriminated field so an unsupported/ambiguous shape fails closed at
construction rather than silently coercing.

Only the shared request/index/scoring models and constants live here; the
injection, minimization, context, answer and receipt models are colocated
with their owning modules (``injection.py``/``minimization.py``/
``context.py``/``validation.py``/``receipts.py``) so every file in this
package stays under the repository's file-size ceiling.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from governed_retrieval.evidence_models import EvidenceProjectionV1
from governed_retrieval.hashing import citation_id as compute_citation_id
from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, SafeId, StrictModel, utc_datetime

from .semantic import feature_ids, semantic_score, tokenize

ENCODER_ID_LITERAL = "PROJECT_CONCEPT_FEATURE_VECTOR_V1"
MINIMIZATION_ALGORITHM_LITERAL = "MINIMIZATION_EXTRACTIVE_V1"

# SPEC R7 - fixed integer fusion policy.
LEXICAL_WEIGHT = 45
SEMANTIC_WEIGHT = 55
SCORE_POLICY_ID = "GOVERNED_RAG_HYBRID_FUSION_V1"

# SPEC R11 - context/answer bounds.
MAX_CLAIMS = 8
MAX_CITATIONS_PER_CLAIM = 4
MAX_CLAIM_TEXT_CODEPOINTS = 512
MAX_ABSTENTION_REASON_CODEPOINTS = 256

# SPEC R10 - minimization ceilings.
MAX_MINIMIZED_RECORD_CODEPOINTS = 480
MAX_MINIMIZED_RECORD_UTF8_BYTES = 1440
MAX_MINIMIZED_TOTAL_CODEPOINTS = 1920
MAX_MINIMIZED_TOTAL_UTF8_BYTES = 5760
MAX_MINIMIZED_RECORD_TOKENS = 240
MAX_MINIMIZED_TOTAL_TOKENS = 960

ScoreInt = Annotated[int, Field(ge=0, le=1_000_000, strict=True)]
NonNegInt = Annotated[int, Field(ge=0, strict=True)]
PosInt = Annotated[int, Field(ge=1, strict=True)]


# ---------------------------------------------------------------------------
# Request / policy / execution facts (SPEC R2)
# ---------------------------------------------------------------------------


class ContextBudgetPolicyV1(StrictModel):
    """P4-A2 own context-budget policy; the effective budget is the minimum
    of this and the P4-A1 handoff's own applied limits (SPEC R11)."""

    max_minimized_records: PosInt = Field(le=4)
    max_context_codepoints: PosInt = Field(le=MAX_MINIMIZED_TOTAL_CODEPOINTS)
    max_context_utf8_bytes: PosInt = Field(le=MAX_MINIMIZED_TOTAL_UTF8_BYTES)
    max_context_estimated_tokens: PosInt = Field(le=MAX_MINIMIZED_TOTAL_TOKENS)


class GovernedRagRequestV1(StrictModel):
    """SPEC R2/R3 - the strict, closed request the application composition
    function validates before calling P4-A1. ``query`` is the original,
    normalized-once query text also passed unmodified to P4-A1, preserving
    query/result continuity (DESIGN 'Composition and dependency direction')."""

    contract_version: str = Field(default="1.0", pattern=r"^1\.0$")
    query: Annotated[str, Field(min_length=1, max_length=512)]
    corpus_id: SafeId
    provider_id: SafeId
    model_id: SafeId
    context_budget_policy: ContextBudgetPolicyV1
    max_output_tokens: Annotated[int, Field(ge=1, le=32000, strict=True)] = 2000
    timeout_seconds: Annotated[int, Field(ge=1, le=300, strict=True)] = 30


# ---------------------------------------------------------------------------
# Ephemeral index (SPEC R8)
# ---------------------------------------------------------------------------


class IndexEntryV1(StrictModel):
    """SPEC R8 - one immutable ephemeral index entry. Binds exactly the
    DESIGN identity set: corpus/authorization-scope, citation and
    content/source/version identity, field selector/truth class/cutoff,
    encoder/lexicon identity, the sparse feature-vector digest and this
    entry's own digest over all of the above."""

    citation_id: Digest
    content_digest_sha256: Digest
    source_digest_sha256: Digest
    version_dump: dict[str, str | int | None]
    field_selector: SafeId
    truth_class: SafeId
    source_cutoff_utc: datetime
    encoder_id: Annotated[str, Field(pattern=rf"^{ENCODER_ID_LITERAL}$")]
    encoder_version: SafeId
    lexicon_digest_sha256: Digest
    feature_vector_digest_sha256: Digest
    feature_ids: tuple[str, ...] = Field(min_length=0, max_length=512)
    entry_digest_sha256: Digest

    @model_validator(mode="after")
    def _valid_time(self) -> "IndexEntryV1":
        utc_datetime(self.source_cutoff_utc)
        if tuple(sorted(set(self.feature_ids))) != tuple(sorted(self.feature_ids)):
            raise ValueError("feature_ids must be duplicate-free")
        return self


class EphemeralIndexV1(StrictModel):
    """SPEC R8 - the whole in-memory index for one execution. Immutable once
    built; a strict subset of the granted P4-A1 projections, one entry per
    citation id, duplicate-free."""

    authorization_scope_digest_sha256: Digest
    corpus_id: SafeId
    entries: tuple[IndexEntryV1, ...] = Field(min_length=0, max_length=4)
    index_build_digest_sha256: Digest
    evidence_set_hash_sha256: Digest

    @model_validator(mode="after")
    def _entries_duplicate_free(self) -> "EphemeralIndexV1":
        ids = tuple(entry.citation_id for entry in self.entries)
        if len(set(ids)) != len(ids):
            raise ValueError("index entries must be duplicate-free by citation_id")
        return self


# ---------------------------------------------------------------------------
# Hybrid scoring (SPEC R7)
# ---------------------------------------------------------------------------


class ScoredCitationV1(StrictModel):
    """SPEC R7 - one citation's component scores and fused rank, in the
    exact deterministic ordering (descending fused score, ascending
    citation id tiebreak)."""

    citation_id: Digest
    lexical_score: ScoreInt
    semantic_score: ScoreInt
    fused_score: ScoreInt

    @model_validator(mode="after")
    def _fusion_is_exact(self) -> "ScoredCitationV1":
        expected = (self.lexical_score * LEXICAL_WEIGHT + self.semantic_score * SEMANTIC_WEIGHT) // 100
        if expected != self.fused_score:
            raise ValueError("fused_score must equal the exact 45/55 integer fusion")
        return self


@dataclass(frozen=True)
class RankedRecord:
    citation_id: str
    content_snippet: str
    scored: ScoredCitationV1


def rank_projections(
    query: str, projections: tuple[EvidenceProjectionV1, ...], built_index: EphemeralIndexV1
) -> tuple[RankedRecord, ...]:
    """DESIGN step 7 - deterministic lexical+semantic fusion and rerank.
    Lives here (not ``service.py`` or ``index.py``) purely to keep every
    file in this package under the repository's file-size ceiling - it is
    pure scoring over index entries, no pipeline control flow of its own.
    Lexical score reuses the same overlap-style scoring as semantic (integer
    Jaccard over token features) so both components share one deterministic
    integer scale; semantic additionally sees concept features."""
    query_tokens = tuple(f"TOK_{t}" for t in tokenize(query))
    query_features = feature_ids(query)
    entries_by_id = {e.citation_id: e for e in built_index.entries}
    records: list[RankedRecord] = []
    for projection in projections:
        cid = compute_citation_id(projection.citation.model_dump(mode="python"))
        entry = entries_by_id[cid]
        doc_tokens = tuple(f for f in entry.feature_ids if f.startswith("TOK_"))
        lexical = semantic_score(query_tokens, doc_tokens)
        semantic = semantic_score(query_features, entry.feature_ids)
        fused = (lexical * LEXICAL_WEIGHT + semantic * SEMANTIC_WEIGHT) // 100
        scored = ScoredCitationV1(citation_id=cid, lexical_score=lexical, semantic_score=semantic, fused_score=fused)
        records.append(RankedRecord(citation_id=cid, content_snippet=projection.content_snippet, scored=scored))
    # SPEC R7 - descending fused score, ascending citation id tiebreak.
    records.sort(key=lambda r: (-r.scored.fused_score, r.citation_id))
    return tuple(records)


__all__ = [
    "ENCODER_ID_LITERAL",
    "MINIMIZATION_ALGORITHM_LITERAL",
    "LEXICAL_WEIGHT",
    "SEMANTIC_WEIGHT",
    "SCORE_POLICY_ID",
    "MAX_CLAIMS",
    "MAX_CITATIONS_PER_CLAIM",
    "MAX_CLAIM_TEXT_CODEPOINTS",
    "MAX_ABSTENTION_REASON_CODEPOINTS",
    "MAX_MINIMIZED_RECORD_CODEPOINTS",
    "MAX_MINIMIZED_RECORD_UTF8_BYTES",
    "MAX_MINIMIZED_TOTAL_CODEPOINTS",
    "MAX_MINIMIZED_TOTAL_UTF8_BYTES",
    "MAX_MINIMIZED_RECORD_TOKENS",
    "MAX_MINIMIZED_TOTAL_TOKENS",
    "ScoreInt",
    "NonNegInt",
    "PosInt",
    "ContextBudgetPolicyV1",
    "GovernedRagRequestV1",
    "IndexEntryV1",
    "EphemeralIndexV1",
    "ScoredCitationV1",
    "RankedRecord",
    "rank_projections",
]
