"""P4-A2 SPEC R8 - ephemeral index build/validate, stale detection.

Missing/extra/duplicate/partial/altered index entries, mismatched
authorization scope/corpus, and unknown encoder/version/lexicon must all be
rejected as STALE_INDEX fail-closed, with no silent lexical-only fallback.
"""

from __future__ import annotations

import pytest

import _p4a2_rag_fixtures as fx
from governed_rag.errors import BindingMismatchError, ScopeMismatchError, StaleIndexError
from governed_rag.index import build_index, validate_index, verify_bindings, verify_request_scope

SCOPE_A = "a" * 64
SCOPE_B = "b" * 64


def _fixtures():
    return fx


def test_build_index_is_deterministic():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx1 = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    idx2 = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    assert idx1.index_build_digest_sha256 == idx2.index_build_digest_sha256
    assert idx1.evidence_set_hash_sha256 == idx2.evidence_set_hash_sha256


def test_build_index_one_entry_per_projection():
    fx = _fixtures()
    p2 = fx.make_projection(record_id="pk-002", snippet="Escalation policy requires supervisor sign-off.")
    ev = fx.evidence_available(projections=(fx.make_projection(), p2))
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    assert len(idx.entries) == 2
    ids = {e.citation_id for e in idx.entries}
    assert len(ids) == 2


def test_validate_index_accepts_freshly_built_index():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    validate_index(idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_validate_index_rejects_mismatched_authorization_scope():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    with pytest.raises(StaleIndexError):
        validate_index(idx, authorization_scope_digest_sha256=SCOPE_B, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_validate_index_rejects_mismatched_corpus():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    with pytest.raises(StaleIndexError):
        validate_index(idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="SHIFT_ADVISORY_MESSAGES_V1", projections=ev.projections)


def test_validate_index_rejects_when_projection_set_changed():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    other = fx.make_projection(record_id="pk-999", snippet="A completely different snippet of text.")
    ev2 = fx.evidence_available(projections=(other,))
    with pytest.raises(StaleIndexError):
        validate_index(idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev2.projections)


def test_validate_index_rejects_extra_entry():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    p2 = fx.make_projection(record_id="pk-002", snippet="Escalation policy requires supervisor sign-off.")
    idx_extra = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections + (p2,))
    with pytest.raises(StaleIndexError):
        validate_index(idx_extra, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_validate_index_rejects_partial_missing_entry():
    fx = _fixtures()
    p2 = fx.make_projection(record_id="pk-002", snippet="Escalation policy requires supervisor sign-off.")
    ev = fx.evidence_available(projections=(fx.make_projection(), p2))
    idx_full = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    partial_entries = idx_full.entries[:1]
    from governed_rag.models import EphemeralIndexV1

    partial_idx = EphemeralIndexV1(
        authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        entries=partial_entries, index_build_digest_sha256=idx_full.index_build_digest_sha256,
        evidence_set_hash_sha256=idx_full.evidence_set_hash_sha256,
    )
    with pytest.raises(StaleIndexError):
        validate_index(partial_idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_validate_index_rejects_altered_entry_digest():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    altered_entry = idx.entries[0].model_copy(update={"entry_digest_sha256": "f" * 64})
    from governed_rag.models import EphemeralIndexV1

    altered_idx = EphemeralIndexV1(
        authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        entries=(altered_entry,), index_build_digest_sha256=idx.index_build_digest_sha256,
        evidence_set_hash_sha256=idx.evidence_set_hash_sha256,
    )
    with pytest.raises(StaleIndexError):
        validate_index(altered_idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_validate_index_rejects_unknown_encoder_version():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    stale_entry = idx.entries[0].model_copy(update={"encoder_version": "0.0-old"})
    from governed_rag.models import EphemeralIndexV1

    stale_idx = EphemeralIndexV1(
        authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        entries=(stale_entry,), index_build_digest_sha256=idx.index_build_digest_sha256,
        evidence_set_hash_sha256=idx.evidence_set_hash_sha256,
    )
    with pytest.raises(StaleIndexError):
        validate_index(stale_idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_validate_index_rejects_unknown_lexicon_digest():
    fx = _fixtures()
    ev = fx.evidence_available()
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    stale_entry = idx.entries[0].model_copy(update={"lexicon_digest_sha256": "9" * 64})
    from governed_rag.models import EphemeralIndexV1

    stale_idx = EphemeralIndexV1(
        authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        entries=(stale_entry,), index_build_digest_sha256=idx.index_build_digest_sha256,
        evidence_set_hash_sha256=idx.evidence_set_hash_sha256,
    )
    with pytest.raises(StaleIndexError):
        validate_index(stale_idx, authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)


def test_index_entries_are_a_strict_subset_of_granted_projections():
    fx = _fixtures()
    p2 = fx.make_projection(record_id="pk-002", snippet="Escalation policy requires supervisor sign-off.")
    ev = fx.evidence_available(projections=(fx.make_projection(), p2))
    idx = build_index(authorization_scope_digest_sha256=SCOPE_A, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", projections=ev.projections)
    granted_ids = set(ev.receipt.citation_ids)
    index_ids = {e.citation_id for e in idx.entries}
    assert index_ids <= granted_ids


# ---------------------------------------------------------------------------
# P4A2-REV-F4 - verify_request_scope: exact corpus/authorization-scope
# equality against the P4-A1 receipt, independently re-verified inside
# governed_rag itself (never trusting the application caller alone).
# ---------------------------------------------------------------------------


def test_verify_request_scope_accepts_exact_match():
    ev = fx.evidence_available(corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", authorization_scope_digest_sha256=SCOPE_A)
    verify_request_scope(result=ev, request_corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", authorization_scope_digest_sha256=SCOPE_A)


def test_verify_request_scope_rejects_corpus_mismatch():
    ev = fx.evidence_available(corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", authorization_scope_digest_sha256=SCOPE_A)
    with pytest.raises(ScopeMismatchError):
        verify_request_scope(result=ev, request_corpus_id="SHIFT_ADVISORY_MESSAGES_V1", authorization_scope_digest_sha256=SCOPE_A)


def test_verify_request_scope_rejects_authorization_scope_digest_mismatch():
    ev = fx.evidence_available(corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", authorization_scope_digest_sha256=SCOPE_A)
    with pytest.raises(ScopeMismatchError):
        verify_request_scope(result=ev, request_corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", authorization_scope_digest_sha256=SCOPE_B)


def test_verify_request_scope_rejects_combined_relabel_attempt():
    """A caller that relabels BOTH corpus_id and scope digest consistently
    must still be rejected - each is checked independently."""
    ev = fx.evidence_available(corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", authorization_scope_digest_sha256=SCOPE_A)
    with pytest.raises(ScopeMismatchError):
        verify_request_scope(result=ev, request_corpus_id="SHIFT_ADVISORY_MESSAGES_V1", authorization_scope_digest_sha256=SCOPE_B)


# ---------------------------------------------------------------------------
# P4A2-REV-F7 - verify_bindings deep recomputation: a model_construct
# adversary that updates every shallow-equality-checked field consistently
# must still be rejected because raw text/byte-derived facts are
# independently recomputed here, not trusted from the P4-A1 object.
# ---------------------------------------------------------------------------


def test_verify_bindings_rejects_forged_snippet_digest_via_model_construct():
    """A coordinated adversary using model_construct to relabel
    snippet_digest_sha256 without changing content_snippet (so a naive
    equality check between citation/projection fields would still pass)
    must be rejected by the independent raw-text recomputation."""
    ev = fx.evidence_available()
    p = ev.projections[0]
    forged_citation = p.citation.model_construct(**{**p.citation.model_dump(mode="python"), "snippet_digest_sha256": "9" * 64})
    forged_projection = p.model_construct(**{**p.model_dump(mode="python"), "citation": forged_citation})
    forged = ev.model_copy(update={"projections": (forged_projection,) + ev.projections[1:]})
    with pytest.raises(BindingMismatchError):
        verify_bindings(forged)


def test_verify_bindings_rejects_receipt_hash_not_covering_real_fields():
    """A model_construct adversary sets a self-consistent-looking
    receipt_hash_sha256 that does not actually cover the receipt's real
    field values (here: a tampered corpus_id) - independently recomputed
    and rejected, not trusted as an opaque caller-supplied value."""
    from governed_retrieval.enums import CorpusId

    ev = fx.evidence_available()
    tampered_fields = dict(ev.receipt)
    tampered_fields["corpus_id"] = CorpusId("SHIFT_ADVISORY_MESSAGES_V1")
    tampered_receipt = ev.receipt.model_construct(**tampered_fields)
    forged = ev.model_copy(update={"receipt": tampered_receipt})
    with pytest.raises(BindingMismatchError):
        verify_bindings(forged)


def test_verify_bindings_rejects_forged_serialized_bytes_and_token_estimate():
    """handoff.serialized_context_bytes/estimated_input_tokens are
    recomputed from the raw projection set, never trusted from the
    handoff's own declared facts."""
    ev = fx.evidence_available()
    forged_handoff = ev.future_context_handoff.model_construct(
        **{**ev.future_context_handoff.model_dump(mode="python"), "serialized_context_bytes": 999999, "estimated_input_tokens": 500000}
    )
    forged = ev.model_copy(update={"future_context_handoff": forged_handoff})
    with pytest.raises(BindingMismatchError):
        verify_bindings(forged)


# ---------------------------------------------------------------------------
# Amendment 1 / A1-F7 - verify_bindings must require ALL ELEVEN positive
# P4-A1 stages PASS, including stage 11 (RECEIPT_EMITTED), not just the
# first ten operational stages. This is the exact reviewer probe: a
# coordinated model_construct receipt with stage 11 RECEIPT_EMITTED=NOT_RUN,
# a recomputed public hash, and a matching handoff was wrongly accepted by
# the prior (stages[:10]-only) check.
# ---------------------------------------------------------------------------


def test_verify_bindings_rejects_stage_11_receipt_emitted_not_run_with_recomputed_hash():
    """A coordinated adversary: every one of the first ten operational
    stages stays PASS, only stage 11 (RECEIPT_EMITTED) is forged to
    NOT_RUN, the receipt's own public hash is recomputed to cover that
    exact tampered stage list (so the hash self-check alone would pass),
    and the handoff is left correctly bound to that recomputed hash. Only
    the independent all-eleven-stage recomputation in verify_bindings
    catches this - constructed via model_construct on the receipt to
    bypass RetrievalReceiptV1's own (bypassable) validator, and via
    model_copy on the wrapper (which does not re-run EvidenceAvailableV1's
    own validators either)."""
    from governed_retrieval.enums import RetrievalStage, StageOutcome
    from governed_retrieval.hashing import receipt_hash as compute_retrieval_receipt_hash

    ev = fx.evidence_available()
    receipt = ev.receipt

    tampered_stages = list(receipt.stages)
    last_index = len(tampered_stages) - 1
    assert tampered_stages[last_index].stage == RetrievalStage.RECEIPT_EMITTED
    tampered_stages[last_index] = tampered_stages[last_index].model_copy(
        update={"outcome": StageOutcome.NOT_RUN, "reason_code": None}
    )

    tampered_fields = dict(receipt)
    tampered_fields["stages"] = tuple(tampered_stages)
    # Recompute the public receipt hash to cover the tampered stage list, so
    # a bare hash-recomputation check alone would NOT catch this adversary -
    # only the independent all-eleven-stage-PASS check below does.
    hash_input = dict(tampered_fields)
    hash_input.pop("receipt_hash_sha256")
    tampered_fields["receipt_hash_sha256"] = compute_retrieval_receipt_hash(hash_input)

    tampered_receipt = receipt.model_construct(**tampered_fields)
    # Keep the handoff correctly bound to the NEW recomputed hash, so this
    # probe is caught SPECIFICALLY by the all-eleven-stage check below, not
    # incidentally by the (already-covered) handoff/receipt hash-linkage
    # check.
    rebound_handoff = ev.future_context_handoff.model_copy(
        update={"retrieval_receipt_hash_sha256": tampered_fields["receipt_hash_sha256"]}
    )
    forged = ev.model_copy(update={"receipt": tampered_receipt, "future_context_handoff": rebound_handoff})

    with pytest.raises(BindingMismatchError):
        verify_bindings(forged)
