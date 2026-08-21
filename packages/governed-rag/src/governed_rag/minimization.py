"""``MINIMIZATION_EXTRACTIVE_V1`` deterministic extractive minimization
(SPEC R10).

Independently of P4-A1's own ``NOT_PROVEN`` minimization-evidence handoff
(which this package never mutates or relabels), P4-A2 produces its own
extractive minimization proof over the clean (post-injection-screening)
evidence snippets: select only sentences that contain a query token or a
matched semantic-concept feature, apply fixed per-record and total size
ceilings, and reject secret/credential/PII-like patterns and Unicode control
characters. Every step is pure stdlib text processing - deterministic,
reproducible, and independently recomputable by tests from the same
preimage helpers this module uses.
"""

from __future__ import annotations

import re
import unicodedata
from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, StrictModel

from .hashing import minimization_input_digest, minimization_output_digest, minimization_ruleset_digest
from .models import (
    MAX_MINIMIZED_RECORD_CODEPOINTS,
    MAX_MINIMIZED_RECORD_TOKENS,
    MAX_MINIMIZED_RECORD_UTF8_BYTES,
    MAX_MINIMIZED_TOTAL_CODEPOINTS,
    MAX_MINIMIZED_TOTAL_TOKENS,
    MAX_MINIMIZED_TOTAL_UTF8_BYTES,
    MINIMIZATION_ALGORITHM_LITERAL,
    NonNegInt,
)
from .semantic import feature_ids, tokenize


class MinimizationOmissionReason(StrEnum):
    """SPEC R10 - closed set of safe minimization-omission reason codes."""

    NO_QUERY_OR_CONCEPT_MATCH = "NO_QUERY_OR_CONCEPT_MATCH"
    SECRET_OR_PII_PATTERN = "SECRET_OR_PII_PATTERN"
    UNICODE_CONTROL_PRESENT = "UNICODE_CONTROL_PRESENT"
    RECORD_SIZE_CEILING = "RECORD_SIZE_CEILING"
    TOTAL_SIZE_CEILING = "TOTAL_SIZE_CEILING"


class MinimizationRecordProofV1(StrictModel):
    """SPEC R10 - one record's independently recomputable minimization
    proof. Never carries the input or output body itself - only digests,
    counts and omissions."""

    citation_id: Digest
    input_digest_sha256: Digest
    output_digest_sha256: Digest | None
    ruleset_digest_sha256: Digest
    algorithm: Annotated[str, Field(pattern=rf"^{MINIMIZATION_ALGORITHM_LITERAL}$")]
    sentence_count_in: NonNegInt
    sentence_count_out: NonNegInt
    output_codepoints: NonNegInt
    output_utf8_bytes: NonNegInt
    output_estimated_tokens: NonNegInt
    omitted: bool
    omission_reasons: tuple[MinimizationOmissionReason, ...] = Field(max_length=5)

    @model_validator(mode="after")
    def _omission_consistency(self) -> "MinimizationRecordProofV1":
        if self.omitted:
            if self.output_digest_sha256 is not None:
                raise ValueError("an omitted record must not carry an output digest")
            if not self.omission_reasons:
                raise ValueError("an omitted record requires at least one omission reason")
            if self.sentence_count_out != 0 or self.output_codepoints != 0:
                raise ValueError("an omitted record must have zero output counts")
        else:
            if self.output_digest_sha256 is None:
                raise ValueError("a retained record requires an output digest")
            if self.omission_reasons:
                raise ValueError("a retained record must carry no omission reasons")
            if self.sentence_count_out < 1:
                raise ValueError("a retained record requires at least one output sentence")
        if tuple(sorted(set(self.omission_reasons))) != tuple(sorted(self.omission_reasons)):
            raise ValueError("omission_reasons must be duplicate-free")
        return self


class MinimizationProofV1(StrictModel):
    """SPEC R10 - the whole minimization pass's independently recomputable
    proof across every screened-in candidate record."""

    ruleset_digest_sha256: Digest
    records: tuple[MinimizationRecordProofV1, ...] = Field(max_length=4)
    retained_count: NonNegInt
    omitted_count: NonNegInt

    @model_validator(mode="after")
    def _counts_match(self) -> "MinimizationProofV1":
        retained = sum(1 for r in self.records if not r.omitted)
        omitted = sum(1 for r in self.records if r.omitted)
        if retained != self.retained_count or omitted != self.omitted_count:
            raise ValueError("retained_count/omitted_count must equal the records' actual split")
        ids = tuple(r.citation_id for r in self.records)
        if len(set(ids)) != len(ids):
            raise ValueError("minimization records must be duplicate-free by citation_id")
        return self


class MinimizedEvidenceRecordV1(StrictModel):
    """SPEC R10/R11 - one retained, minimized evidence record eligible for
    context assembly. Carries the actual minimized text (never the P4-A1
    original snippet body)."""

    citation_id: Digest
    minimized_text: Annotated[str, Field(min_length=1, max_length=MAX_MINIMIZED_RECORD_CODEPOINTS)]

RULESET_ID = "GOVERNED_RAG_MINIMIZATION_RULESET_V1"
RULESET_VERSION = "1.0"
RULESET_DIGEST_SHA256 = minimization_ruleset_digest(ruleset_id=RULESET_ID, version=RULESET_VERSION)

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# SPEC R10 - reject secret/credential/PII-like patterns outright.
_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_ -]?key|secret|password|token|credential)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-shaped
    re.compile(r"\b(?:\d[ -]?){13,19}\b"),  # long digit runs (card-shaped)
    re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"),  # email
)


def _estimate_tokens(utf8_bytes: int) -> int:
    return (utf8_bytes + 1) // 2


def _utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))


def split_sentences(text: str) -> tuple[str, ...]:
    """Deterministic sentence splitting on terminal punctuation or newlines."""
    normalized = unicodedata.normalize("NFC", text)
    pieces = [p.strip() for p in _SENTENCE_SPLIT_RE.split(normalized) if p.strip()]
    return tuple(pieces)


def _has_secret_pattern(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)


def _relevant(sentence: str, query_features: tuple[str, ...], query_tokens: tuple[str, ...]) -> bool:
    sentence_tokens = set(tokenize(sentence))
    if sentence_tokens & set(query_tokens):
        return True
    sentence_features = set(feature_ids(sentence))
    query_concepts = {f for f in query_features if f.startswith("CONCEPT_")}
    return bool(sentence_features & query_concepts)


def _omitted_proof(
    *, citation_id: str, input_digest: str, sentence_count_in: int,
    reasons: tuple[MinimizationOmissionReason, ...],
) -> MinimizationRecordProofV1:
    """Shared constructor for every omitted-record proof shape (SPEC R10):
    always zero output digest/counts, only the reasons and input facts vary."""
    return MinimizationRecordProofV1(
        citation_id=citation_id, input_digest_sha256=input_digest, output_digest_sha256=None,
        ruleset_digest_sha256=RULESET_DIGEST_SHA256, algorithm=MINIMIZATION_ALGORITHM_LITERAL,
        sentence_count_in=sentence_count_in, sentence_count_out=0, output_codepoints=0,
        output_utf8_bytes=0, output_estimated_tokens=0, omitted=True, omission_reasons=reasons,
    )


def minimize_record(
    *, citation_id: str, source_snippet: str, query: str
) -> tuple[MinimizationRecordProofV1, MinimizedEvidenceRecordV1 | None]:
    """SPEC R10 - minimize one clean evidence snippet.

    Selects only sentences containing a query token or a matched semantic
    concept feature, then applies the fixed per-record codepoint/UTF-8/token
    ceilings and rejects secret/PII/control-character content. Returns the
    independently recomputable proof plus the retained record (``None`` when
    omitted).
    """
    input_digest = minimization_input_digest(citation_id=citation_id, source_snippet=source_snippet)
    sentences_in = split_sentences(source_snippet)
    query_features = feature_ids(query)
    query_tokens = tokenize(query)

    if _CONTROL_RE.search(source_snippet):
        reasons = (MinimizationOmissionReason.UNICODE_CONTROL_PRESENT,)
        return _omitted_proof(
            citation_id=citation_id, input_digest=input_digest,
            sentence_count_in=len(sentences_in), reasons=reasons,
        ), None

    selected: list[str] = []
    total_codepoints = 0
    total_bytes = 0
    for sentence in sentences_in:
        if not _relevant(sentence, query_features, query_tokens) or _has_secret_pattern(sentence):
            continue
        candidate_codepoints = total_codepoints + len(sentence) + (1 if selected else 0)
        candidate_bytes = total_bytes + _utf8_len(sentence) + (1 if selected else 0)
        if (
            candidate_codepoints > MAX_MINIMIZED_RECORD_CODEPOINTS
            or candidate_bytes > MAX_MINIMIZED_RECORD_UTF8_BYTES
            or _estimate_tokens(candidate_bytes) > MAX_MINIMIZED_RECORD_TOKENS
        ):
            break
        selected.append(sentence)
        total_codepoints, total_bytes = candidate_codepoints, candidate_bytes

    if not selected:
        has_secret_anywhere = any(_has_secret_pattern(s) for s in sentences_in)
        reasons = (
            (MinimizationOmissionReason.SECRET_OR_PII_PATTERN,)
            if has_secret_anywhere
            else (MinimizationOmissionReason.NO_QUERY_OR_CONCEPT_MATCH,)
        )
        return _omitted_proof(
            citation_id=citation_id, input_digest=input_digest,
            sentence_count_in=len(sentences_in), reasons=reasons,
        ), None

    minimized_text = " ".join(selected)
    output_digest = minimization_output_digest(citation_id=citation_id, minimized_text=minimized_text)
    proof = MinimizationRecordProofV1(
        citation_id=citation_id,
        input_digest_sha256=input_digest,
        output_digest_sha256=output_digest,
        ruleset_digest_sha256=RULESET_DIGEST_SHA256,
        algorithm=MINIMIZATION_ALGORITHM_LITERAL,
        sentence_count_in=len(sentences_in),
        sentence_count_out=len(selected),
        output_codepoints=len(minimized_text),
        output_utf8_bytes=_utf8_len(minimized_text),
        output_estimated_tokens=_estimate_tokens(_utf8_len(minimized_text)),
        omitted=False,
        omission_reasons=(),
    )
    return proof, MinimizedEvidenceRecordV1(citation_id=citation_id, minimized_text=minimized_text)


def minimize_all(
    *, records: tuple[tuple[str, str], ...], query: str
) -> tuple[MinimizationProofV1, tuple[MinimizedEvidenceRecordV1, ...]]:
    """SPEC R10 - minimize every ``(citation_id, source_snippet)`` clean
    record, enforcing the fixed TOTAL codepoint/UTF-8/token ceiling across
    the whole retained set (records that would push the running total over
    the ceiling are omitted with ``TOTAL_SIZE_CEILING``, in input order).
    Returns the whole-pass proof plus the ordered retained records.
    """
    proofs: list[MinimizationRecordProofV1] = []
    retained: list[MinimizedEvidenceRecordV1] = []
    total_codepoints = 0
    total_bytes = 0
    total_tokens = 0

    for citation_id, snippet in records:
        proof, record = minimize_record(citation_id=citation_id, source_snippet=snippet, query=query)
        if record is None:
            proofs.append(proof)
            continue

        projected_codepoints = total_codepoints + proof.output_codepoints
        projected_bytes = total_bytes + proof.output_utf8_bytes
        projected_tokens = total_tokens + proof.output_estimated_tokens
        if (
            projected_codepoints > MAX_MINIMIZED_TOTAL_CODEPOINTS
            or projected_bytes > MAX_MINIMIZED_TOTAL_UTF8_BYTES
            or projected_tokens > MAX_MINIMIZED_TOTAL_TOKENS
        ):
            proofs.append(_omitted_proof(
                citation_id=citation_id, input_digest=proof.input_digest_sha256,
                sentence_count_in=proof.sentence_count_in,
                reasons=(MinimizationOmissionReason.TOTAL_SIZE_CEILING,),
            ))
            continue

        proofs.append(proof)
        retained.append(record)
        total_codepoints = projected_codepoints
        total_bytes = projected_bytes
        total_tokens = projected_tokens

    retained_count = sum(1 for p in proofs if not p.omitted)
    omitted_count = sum(1 for p in proofs if p.omitted)
    whole_proof = MinimizationProofV1(
        ruleset_digest_sha256=RULESET_DIGEST_SHA256,
        records=tuple(proofs),
        retained_count=retained_count,
        omitted_count=omitted_count,
    )
    return whole_proof, tuple(retained)
