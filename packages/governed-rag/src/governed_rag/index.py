"""Ephemeral semantic index build and stale-detection (SPEC R8).

The index is rebuilt in memory for every execution from the exact granted
P4-A1 projections; no database or persistent vector store is used. Every
entry binds the DESIGN identity set (corpus/authorization-scope, citation and
content/source/version identity, field selector/truth class/cutoff, encoder/
lexicon identity, and the sparse feature-vector digest), so a caller-supplied
prebuilt index can be independently re-validated against the *current*
projections before any ranking happens. Missing, extra, duplicate, partial,
altered, incompatible or stale entries are rejected as ``STALE_INDEX`` with
zero downstream work - there is no silent lexical-only fallback here.
"""

from __future__ import annotations

from governed_retrieval.evidence_models import EvidenceProjectionV1
from governed_retrieval.hashing import citation_id as compute_citation_id
from governed_retrieval.hashing import evidence_set_hash as compute_evidence_set_hash
from governed_retrieval.hashing import receipt_hash as compute_retrieval_receipt_hash
from governed_retrieval.projection import estimate_tokens as compute_estimated_tokens
from governed_retrieval.projection import serialized_projection_bytes as compute_serialized_bytes
from governed_retrieval.result_models import EvidenceAvailableV1
from retrieval_contracts.canonical import sha256_bytes

from .errors import BindingMismatchError, ScopeMismatchError, ScopeWideningError, StaleIndexError
from .hashing import feature_vector_digest, index_build_digest, index_entry_digest, ordered_evidence_set_hash
from .models import EphemeralIndexV1, IndexEntryV1
from .semantic import ENCODER_ID, ENCODER_VERSION, LEXICON_DIGEST_SHA256, feature_ids


def verify_request_scope(
    *, result: EvidenceAvailableV1, request_corpus_id: str, authorization_scope_digest_sha256: str
) -> None:
    """P4A2-REV-F4 - independently verify EXACT equality between the
    caller-supplied request/authorization facts and the P4-A1 receipt/
    handoff for corpus identity and authorization-scope digest, before any
    index/minimization/context/gateway work. This package never relies
    solely on the application-composition caller to enforce this - a
    mismatched or relabeled corpus/scope is rejected here, independently,
    with zero downstream work, regardless of what the caller claims.
    """
    receipt = result.receipt
    handoff = result.future_context_handoff
    receipt_corpus = str(receipt.corpus_id) if receipt.corpus_id is not None else None
    if receipt_corpus is None or receipt_corpus != request_corpus_id:
        raise ScopeMismatchError("request corpus_id does not equal the P4-A1 receipt's corpus_id")
    if receipt.authorization_scope_digest_sha256 != authorization_scope_digest_sha256:
        raise ScopeMismatchError(
            "authorization_scope_digest_sha256 does not equal the P4-A1 receipt's authorization-scope digest"
        )
    # The handoff itself carries no independent corpus/scope field to compare
    # (SPEC R10's FutureContextHandoffV1 contract), so the receipt is the
    # binding source of truth here; verify_bindings already re-verifies the
    # handoff's own hash linkage back to this exact receipt (retrieval_
    # receipt_hash_sha256 == receipt.receipt_hash_sha256), which is what
    # makes trusting the receipt for this check sound - a caller cannot
    # substitute an unrelated receipt without also breaking that linkage.
    if handoff.retrieval_receipt_hash_sha256 != receipt.receipt_hash_sha256:
        raise ScopeMismatchError("handoff is not bound to the exact supplied P4-A1 receipt")


def verify_bindings(result: EvidenceAvailableV1) -> None:
    """SPEC R5/P4A2-REV-F7 - treat every nested P4-A1 model as UNTRUSTED
    input and independently reconstruct/recompute everything needed from the
    raw underlying data, never trusting the P4-A1 object's own fields
    (including its own hash/digest fields) even though
    ``EvidenceAvailableV1``/``EvidenceProjectionV1``/``RetrievalReceiptV1``
    already run equivalent checks as their own Pydantic ``model_validator``s
    at construction (see ``governed_retrieval.result_models``/
    ``evidence_models``/``receipt_models``) - those upstream guarantees are
    bypassable by a caller that constructs any nested model via
    ``model_construct``. A coordinated adversary that updates every
    shallow-equality-checked field consistently (so a naive equality check
    would pass) must still be rejected here, because the checks below
    recompute facts from raw text/bytes the adversary cannot simultaneously
    forge without changing the very data being hashed.
    """
    projections = result.projections
    receipt, handoff = result.receipt, result.future_context_handoff

    # Per-projection: recompute the snippet digest from the RAW
    # content_snippet text (never trust CitationV1.snippet_digest_sha256 or
    # EvidenceProjectionV1.snippet_digest_sha256 themselves) and cross-check
    # codepoint span/length against the raw text length.
    for p in projections:
        recomputed_snippet_digest = sha256_bytes(p.content_snippet.encode("utf-8"))
        if recomputed_snippet_digest != p.citation.snippet_digest_sha256:
            raise BindingMismatchError("citation.snippet_digest_sha256 does not match the recomputed raw-text digest")
        if recomputed_snippet_digest != p.snippet_digest_sha256:
            raise BindingMismatchError("projection.snippet_digest_sha256 does not match the recomputed raw-text digest")
        if len(p.content_snippet) != p.snippet_end_codepoint - p.snippet_start_codepoint:
            raise BindingMismatchError("content_snippet length does not match the declared codepoint span")

    recomputed_ids = tuple(compute_citation_id(p.citation.model_dump(mode="python")) for p in projections)
    if recomputed_ids != receipt.citation_ids:
        raise BindingMismatchError("receipt.citation_ids do not match recomputed projection citation ids")
    if recomputed_ids != handoff.citation_ids:
        raise BindingMismatchError("handoff.citation_ids do not match recomputed projection citation ids")

    citation_dumps = [p.citation.model_dump(mode="python") for p in projections]
    projection_dumps = [p.model_dump(mode="python") for p in projections]
    recomputed_evidence_hash = compute_evidence_set_hash(citation_dumps, projection_dumps)
    if receipt.evidence_set_hash_sha256 != recomputed_evidence_hash:
        raise BindingMismatchError("receipt.evidence_set_hash_sha256 does not match recomputed evidence-set hash")
    if handoff.evidence_set_hash_sha256 != recomputed_evidence_hash:
        raise BindingMismatchError("handoff.evidence_set_hash_sha256 does not match recomputed evidence-set hash")

    # P4A2-REV-F7 - independently recompute the RECEIPT's own integrity hash
    # from the canonical dump of its OTHER fields (the same preimage helper
    # governed_retrieval itself uses), rather than trusting
    # receipt.receipt_hash_sha256 as an opaque caller-supplied value. A
    # model_construct adversary that sets a self-consistent-looking hash
    # without it actually covering the receipt's real field values is caught
    # here, independently of RetrievalReceiptV1's own (bypassable) validator.
    receipt_dump = receipt.model_dump(mode="python")
    receipt_dump.pop("receipt_hash_sha256")
    if compute_retrieval_receipt_hash(receipt_dump) != receipt.receipt_hash_sha256:
        raise BindingMismatchError("receipt.receipt_hash_sha256 does not match its own recomputed canonical hash")
    if handoff.retrieval_receipt_hash_sha256 != receipt.receipt_hash_sha256:
        raise BindingMismatchError("handoff retrieval_receipt_hash_sha256 does not match receipt hash")

    # P4A2-REV-F7 - recompute serialized bytes/token estimate/snippet
    # codepoints/sensitivities from the raw projection set, never trusted
    # from the handoff's own declared facts.
    recomputed_bytes = compute_serialized_bytes(projection_dumps)
    if handoff.serialized_context_bytes != recomputed_bytes:
        raise BindingMismatchError("handoff.serialized_context_bytes does not match the recomputed byte count")
    if handoff.estimated_input_tokens != compute_estimated_tokens(recomputed_bytes):
        raise BindingMismatchError("handoff.estimated_input_tokens does not match the recomputed token estimate")
    recomputed_codepoints = sum(p.snippet_end_codepoint - p.snippet_start_codepoint for p in projections)
    if handoff.snippet_codepoints != recomputed_codepoints:
        raise BindingMismatchError("handoff.snippet_codepoints does not match the summed projection spans")
    if handoff.projection_count != len(projections) or receipt.counts.projections_emitted != len(projections):
        raise BindingMismatchError("handoff/receipt projection counts do not match len(projections)")
    if set(handoff.sensitivities) != {p.sensitivity for p in projections}:
        raise BindingMismatchError("handoff.sensitivities does not match the recomputed projection sensitivities")
    if handoff.applied_limits != receipt.applied_limits:
        raise BindingMismatchError("handoff.applied_limits does not match receipt.applied_limits")
    if handoff.elapsed_ms != receipt.elapsed_ms:
        raise BindingMismatchError("handoff.elapsed_ms does not match receipt.elapsed_ms")
    if handoff.configured_timeout_ms != receipt.termination.configured_timeout_ms:
        raise BindingMismatchError("handoff.configured_timeout_ms does not match receipt.termination facts")
    if handoff.timed_out != receipt.termination.timed_out or handoff.cancelled != receipt.termination.cancelled:
        raise BindingMismatchError("handoff timed_out/cancelled does not match receipt.termination facts")

    # P4A2-REV-F7/Amendment 1 - terminal grammar: a genuine EVIDENCE_AVAILABLE
    # receipt must show ALL ELEVEN positive P4-A1 stages PASS - the first ten
    # operational stages AND stage 11 (RECEIPT_EMITTED) - never trust
    # final_outcome alone without checking the complete stage history it
    # claims to summarize. The prior check only inspected stages[:10],
    # missing exactly the gap a coordinated model_construct adversary
    # exploited: a receipt with a recomputed public hash, a matching
    # handoff, and every one of the first ten stages PASS, but stage 11
    # RECEIPT_EMITTED forged to NOT_RUN - now rejected here.
    if any(s.outcome.value != "PASS" for s in receipt.stages):
        raise BindingMismatchError("receipt stage history is not all-PASS across all eleven stages for an EVIDENCE_AVAILABLE receipt")

    # SPEC R5 - never widen: classifications must remain exactly ("INTERNAL",)
    # as P4-A1 always emits for a positive result; a caller-relabeled handoff
    # would be a scope-widening attempt.
    if handoff.classifications != ("INTERNAL",):
        raise ScopeWideningError("handoff classification is not exactly ('INTERNAL',)")
    if handoff.minimization_evidence_status != "NOT_PROVEN":
        raise ScopeWideningError("caller relabeled P4-A1's immutable NOT_PROVEN minimization status")
    if handoff.placement_enforcement_status != "NOT_EVALUATED":
        raise ScopeWideningError("caller relabeled P4-A1's immutable placement_enforcement_status")


def build_index(
    *, authorization_scope_digest_sha256: str, corpus_id: str, projections: tuple[EvidenceProjectionV1, ...]
) -> EphemeralIndexV1:
    """SPEC R8 - build a fresh, in-memory index over exactly the granted
    projections. Deterministic: identical projections always produce an
    identical index (same entry order as ``projections``, same digests)."""
    entries: list[IndexEntryV1] = []
    for projection in projections:
        citation = projection.citation
        # A citation_id is not a stored field on CitationV1 itself; recompute
        # it the same way governed_retrieval.hashing.citation_id does, via
        # the shared canonical-hash helper, so the index never trusts a
        # caller-declared id.
        cid = compute_citation_id(citation.model_dump(mode="python"))
        features = feature_ids(projection.content_snippet)
        fv_digest = feature_vector_digest(features)
        version_dump = citation.version.model_dump(mode="python")
        entry_digest = index_entry_digest(
            citation_id=cid,
            content_digest_sha256=citation.content_digest_sha256,
            source_digest_sha256=citation.source_digest_sha256,
            version_dump=version_dump,
            field_selector=str(citation.field_selector),
            truth_class=citation.truth_class.value,
            source_cutoff_utc=citation.source_cutoff_utc.isoformat(),
            encoder_id=ENCODER_ID,
            encoder_version=ENCODER_VERSION,
            lexicon_digest_sha256=LEXICON_DIGEST_SHA256,
            feature_vector_digest_sha256=fv_digest,
        )
        entries.append(
            IndexEntryV1(
                citation_id=cid,
                content_digest_sha256=citation.content_digest_sha256,
                source_digest_sha256=citation.source_digest_sha256,
                version_dump=version_dump,
                field_selector=str(citation.field_selector),
                truth_class=citation.truth_class.value,
                source_cutoff_utc=citation.source_cutoff_utc,
                encoder_id=ENCODER_ID,
                encoder_version=ENCODER_VERSION,
                lexicon_digest_sha256=LEXICON_DIGEST_SHA256,
                feature_vector_digest_sha256=fv_digest,
                feature_ids=features,
                entry_digest_sha256=entry_digest,
            )
        )
    entry_digests = tuple(e.entry_digest_sha256 for e in entries)
    build_digest = index_build_digest(
        authorization_scope_digest_sha256=authorization_scope_digest_sha256,
        corpus_id=corpus_id,
        entry_digests=entry_digests,
    )
    evidence_hash = ordered_evidence_set_hash(tuple(e.citation_id for e in entries))
    return EphemeralIndexV1(
        authorization_scope_digest_sha256=authorization_scope_digest_sha256,
        corpus_id=corpus_id,
        entries=tuple(entries),
        index_build_digest_sha256=build_digest,
        evidence_set_hash_sha256=evidence_hash,
    )


def validate_index(
    index: EphemeralIndexV1,
    *,
    authorization_scope_digest_sha256: str,
    corpus_id: str,
    projections: tuple[EvidenceProjectionV1, ...],
) -> None:
    """SPEC R8 - recompute the expected fresh index from the current granted
    projections and require the supplied ``index`` to match it exactly
    (same authorization scope, corpus, entry set and every entry's identity
    digest). Raises :class:`StaleIndexError` fail-closed on any mismatch,
    including missing/extra/duplicate/partial/altered entries or an unknown
    encoder/version/lexicon."""
    if index.authorization_scope_digest_sha256 != authorization_scope_digest_sha256:
        raise StaleIndexError("index authorization scope does not match the current execution")
    if index.corpus_id != corpus_id:
        raise StaleIndexError("index corpus_id does not match the current execution")

    expected = build_index(
        authorization_scope_digest_sha256=authorization_scope_digest_sha256,
        corpus_id=corpus_id,
        projections=projections,
    )
    if index.index_build_digest_sha256 != expected.index_build_digest_sha256:
        raise StaleIndexError("index build digest does not match the current granted projections")
    if index.evidence_set_hash_sha256 != expected.evidence_set_hash_sha256:
        raise StaleIndexError("index evidence-set hash does not match the current granted projections")

    expected_by_id = {e.citation_id: e for e in expected.entries}
    actual_by_id = {e.citation_id: e for e in index.entries}
    if set(actual_by_id) != set(expected_by_id):
        raise StaleIndexError("index entries do not exactly match the current granted projection set")
    for citation_id, expected_entry in expected_by_id.items():
        actual_entry = actual_by_id[citation_id]
        if actual_entry.entry_digest_sha256 != expected_entry.entry_digest_sha256:
            raise StaleIndexError(f"index entry altered/incompatible for citation {citation_id}")
        if actual_entry.encoder_id != ENCODER_ID or actual_entry.encoder_version != ENCODER_VERSION:
            raise StaleIndexError("index entry uses an unknown encoder id/version")
        if actual_entry.lexicon_digest_sha256 != LEXICON_DIGEST_SHA256:
            raise StaleIndexError("index entry uses an unknown lexicon digest")
