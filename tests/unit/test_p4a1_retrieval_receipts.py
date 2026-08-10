"""SPEC R9 / receipt contract appendix - CitationV1, RetrievalReceiptV1, and
canonical hashes. AC-09: exact fields, safe id, eleven-stage order/grammar,
timing, canonical preimages, hash recomputation, tamper sensitivity."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from retrieval_contracts.canonical import canonical_json_bytes, sha256_bytes
from retrieval_contracts.contract_models import VersionBindingV1
from retrieval_contracts.enums import RecordType, TruthClass, VersionKind

from governed_retrieval.enums import RETRIEVAL_STAGE_ORDER, FinalOutcome, RetrievalStage, StageOutcome, StageReasonCode
from governed_retrieval.evidence_models import (
    CitationV1, RetrievalCountsV1, RetrievalLimitsV1, RetrievalStageReceiptV1, TerminationFactsV1,
)
from governed_retrieval.hashing import authorization_scope_digest, citation_id, evidence_set_hash, receipt_hash
from governed_retrieval.receipt_models import RetrievalReceiptV1

_D64 = "a" * 64

def _citation(**overrides) -> CitationV1:
    fields = dict(
        chunk_id=_D64, content_digest_sha256=_D64, source_digest_sha256=_D64,
        version=VersionBindingV1(kind=VersionKind.UNVERSIONED), truth_class=TruthClass.ADVISORY_SOURCE_EVIDENCE,
        record_type=RecordType.PROJECT_KNOWLEDGE, source_id="doc-1", field_selector="document",
        revalidation_token=_D64, source_cutoff_utc=datetime(2026, 8, 10, tzinfo=timezone.utc),
        snippet_digest_sha256=_D64, snippet_start_codepoint=0, snippet_end_codepoint=5,
    )
    fields.update(overrides)
    return CitationV1(**fields)

def test_citation_rejects_both_record_id_and_source_id() -> None:
    with pytest.raises(ValidationError):
        _citation(record_id="rec-1", source_id="doc-1")
    with pytest.raises(ValidationError):
        _citation(source_id=None)  # neither id supplied
    with pytest.raises(ValidationError):
        _citation(snippet_start_codepoint=5, snippet_end_codepoint=1)  # inverted offsets

def test_citation_id_is_sha256_of_canonical_wrapped_dump() -> None:
    citation = _citation()
    dump = citation.model_dump(mode="python")
    expected = sha256_bytes(canonical_json_bytes({"citation": dump}))
    assert citation_id(dump) == expected
    assert len(citation_id(dump)) == 64

def test_citation_id_is_deterministic_and_tamper_sensitive() -> None:
    citation = _citation()
    dump = citation.model_dump(mode="python")
    original = citation_id(dump)
    assert citation_id(dict(dump)) == original
    tampered = dict(dump, field_selector="tampered")
    assert citation_id(tampered) != original

def test_authorization_scope_digest_preimage_exact_shape() -> None:
    digest = authorization_scope_digest("shift-operations-workspace", "op1", ("shift-b", "shift-a"))
    preimage = {
        "workspace_id": "shift-operations-workspace", "principal_user_id": "op1",
        "admitted_shift_ids": ["shift-a", "shift-b"],
    }
    assert digest == sha256_bytes(canonical_json_bytes(preimage))

def test_evidence_set_hash_covers_citations_and_projections_and_is_tamper_sensitive() -> None:
    citations, projections = [{"a": 1}], [{"b": 2}]
    expected = sha256_bytes(canonical_json_bytes({"citations": citations, "projections": projections}))
    assert evidence_set_hash(citations, projections) == expected
    assert evidence_set_hash([{"a": 2}], projections) != expected

def test_receipt_hash_omits_only_the_hash_field() -> None:
    dump = {"a": 1, "b": 2}
    assert receipt_hash(dump) == sha256_bytes(canonical_json_bytes(dump))

def test_eleven_stage_order_is_exact() -> None:
    assert [s.value for s in RETRIEVAL_STAGE_ORDER] == [
        "REQUEST_VALIDATED", "AUTHENTICATED", "PERMISSION_AUTHORIZED", "ASSIGNMENT_AUTHORIZED",
        "CORPUS_RESOLVED", "SOURCES_READ", "P3C_ADMITTED", "MATCHED_AND_RANKED",
        "REVALIDATED", "PROJECTED", "RECEIPT_EMITTED",
    ]

def _counts(**overrides) -> RetrievalCountsV1:
    fields = dict(
        source_records_read=0, candidates_admitted=0, matches_ranked=0, selected_for_revalidation=0,
        stale_omitted=0, projections_emitted=0, projections_budget_omitted=0,
    )
    fields.update(overrides)
    return RetrievalCountsV1(**fields)

def test_stage_receipt_requires_reason_for_deny_and_fail() -> None:
    with pytest.raises(ValidationError):
        RetrievalStageReceiptV1(
            stage=RetrievalStage.PERMISSION_AUTHORIZED, outcome=StageOutcome.DENY,
            reason_code=None, safe_counts=_counts(),
        )

def test_stage_receipt_forbids_reason_for_pass_and_not_run() -> None:
    with pytest.raises(ValidationError):
        RetrievalStageReceiptV1(
            stage=RetrievalStage.PERMISSION_AUTHORIZED, outcome=StageOutcome.PASS,
            reason_code=StageReasonCode.ACCESS_DENIED, safe_counts=_counts(),
        )

def test_termination_facts_cannot_be_both_true() -> None:
    with pytest.raises(ValidationError):
        TerminationFactsV1(configured_timeout_ms=1000, timed_out=True, cancelled=True)

def _all_stages(positive: bool = False) -> tuple[RetrievalStageReceiptV1, ...]:
    """RR2-F5 - all-PASS for a positive receipt; else the default negative
    MATCHED_AND_RANKED=FAIL/NO_EVIDENCE terminal then NOT_RUN."""
    if positive:
        return tuple(
            RetrievalStageReceiptV1(stage=stage, outcome=StageOutcome.PASS, reason_code=None, safe_counts=_counts())
            for stage in RetrievalStage
        )
    return _stages_with({RetrievalStage.MATCHED_AND_RANKED: (StageOutcome.FAIL, StageReasonCode.NO_EVIDENCE)})

def _limits() -> RetrievalLimitsV1:
    return RetrievalLimitsV1(
        result_limit=10, max_projection_records=4, max_snippet_codepoints=1024,
        max_snippet_utf8_bytes=3072, max_serialized_utf8_bytes=16384, max_estimated_input_tokens=4096,
    )

def _unhashed_receipt_kwargs(**overrides) -> dict:
    """Every field except ``receipt_hash_sha256`` (RR1-F6). RR2-F5: default
    ``stages`` grammar matches the overridden ``final_outcome``."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
    outcome = overrides.get("final_outcome", FinalOutcome.NO_EVIDENCE)
    fields = dict(
        contract_version="1.0", receipt_id=uuid4(), retrieval_correlation_id=uuid4(),
        started_at_utc=now, finished_at_utc=now, source_cutoff_utc=None, elapsed_ms=0,
        corpus_id=None, authorization_scope_digest_sha256=None,
        stages=_all_stages(positive=outcome == FinalOutcome.EVIDENCE_AVAILABLE),
        final_outcome=FinalOutcome.NO_EVIDENCE, requested_limits=_limits(), applied_limits=None,
        counts=_counts(), termination=TerminationFactsV1(configured_timeout_ms=1000, timed_out=False, cancelled=False),
        citation_ids=(), evidence_set_hash_sha256=None,
    )
    fields.update(overrides)
    return fields

def _base_receipt_kwargs(**overrides) -> dict:
    """RR1-F6: the real, independently-recomputed receipt hash for the given
    field set, built the same way the application builder does."""
    fields = _unhashed_receipt_kwargs(**overrides)
    dump = RetrievalReceiptV1.model_construct(**fields, receipt_hash_sha256="0" * 64).model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    fields["receipt_hash_sha256"] = receipt_hash(dump)
    return fields

def test_receipt_requires_exact_eleven_stages_in_order() -> None:
    RetrievalReceiptV1(**_base_receipt_kwargs())  # sanity: valid case works
    bad_stages = tuple(reversed(_all_stages()))
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(stages=bad_stages))

# --- RR1-F6: receipt_hash_sha256 is independently recomputed, never trusted ---

def test_receipt_rejects_arbitrary_and_cross_outcome_hash() -> None:
    """RR1-F6: an arbitrary hash, and a valid hash whose outcome was swapped
    AFTER the hash was computed, must both be rejected."""
    fields = _unhashed_receipt_kwargs()
    fields["receipt_hash_sha256"] = _D64  # arbitrary, not the real hash
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**fields)
    valid = _base_receipt_kwargs(final_outcome=FinalOutcome.NO_EVIDENCE)
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**dict(valid, final_outcome=FinalOutcome.ACCESS_DENIED))

def test_receipt_finished_before_started_rejected() -> None:
    now = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
    earlier = datetime(2026, 8, 10, 11, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(started_at_utc=now, finished_at_utc=earlier))

def test_positive_elapsed_ms_requires_strictly_later_finish() -> None:
    """RR3-F4/Amendment 4 5.5.5: elapsed_ms > 0 with an equal wall-clock
    interval is rejected after recomputing the outer receipt hash; zero
    elapsed with an equal interval remains accepted."""
    now = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(started_at_utc=now, finished_at_utc=now, elapsed_ms=1))
    RetrievalReceiptV1(**_base_receipt_kwargs(started_at_utc=now, finished_at_utc=now, elapsed_ms=0))

def test_negative_outcome_receipt_has_no_citations_or_evidence_hash() -> None:
    denied = _stages_with({RetrievalStage.AUTHENTICATED: (StageOutcome.DENY, StageReasonCode.AUTHENTICATION_FAILED)})
    receipt = RetrievalReceiptV1(**_base_receipt_kwargs(final_outcome=FinalOutcome.ACCESS_DENIED, stages=denied))
    assert receipt.citation_ids == ()
    assert receipt.evidence_set_hash_sha256 is None

def test_positive_outcome_requires_evidence_hash() -> None:
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(final_outcome=FinalOutcome.EVIDENCE_AVAILABLE, citation_ids=(_D64,)))

def test_positive_outcome_with_evidence_hash_succeeds_and_rejects_duplicate_citations() -> None:
    kwargs = _base_receipt_kwargs(
        final_outcome=FinalOutcome.EVIDENCE_AVAILABLE, citation_ids=(_D64,),
        evidence_set_hash_sha256=_D64, applied_limits=_limits(),
    )
    receipt = RetrievalReceiptV1(**kwargs)
    assert receipt.final_outcome == FinalOutcome.EVIDENCE_AVAILABLE
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**dict(kwargs, citation_ids=(_D64, _D64)))

def test_receipt_reject_unknown_field() -> None:
    kwargs = _base_receipt_kwargs()
    kwargs["bogus_field"] = 1
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**kwargs)

# --- F8/F11: mandatory RECEIPT_EMITTED=PASS, corpus_id nullability timing,
# and UUIDv4 enforcement ---

def _stages_with(overrides: dict) -> tuple[RetrievalStageReceiptV1, ...]:
    """One PASS-then-terminal-then-NOT_RUN history: the single stage key in
    ``overrides`` becomes the terminal DENY/FAIL; later stages (except
    RECEIPT_EMITTED) are NOT_RUN; earlier stages stay PASS."""
    (terminal_stage, (terminal_outcome, terminal_reason)), = overrides.items()
    stages, seen = [], False
    for stage in RetrievalStage:
        if stage == terminal_stage:
            stages.append(RetrievalStageReceiptV1(stage=stage, outcome=terminal_outcome, reason_code=terminal_reason, safe_counts=_counts()))
            seen = True
        elif stage == RetrievalStage.RECEIPT_EMITTED:
            stages.append(RetrievalStageReceiptV1(stage=stage, outcome=StageOutcome.PASS, reason_code=None, safe_counts=_counts()))
        elif seen:
            stages.append(RetrievalStageReceiptV1(stage=stage, outcome=StageOutcome.NOT_RUN, reason_code=None, safe_counts=_counts()))
        else:
            stages.append(RetrievalStageReceiptV1(stage=stage, outcome=StageOutcome.PASS, reason_code=None, safe_counts=_counts()))
    return tuple(stages)

def test_receipt_requires_receipt_emitted_pass_on_every_returned_receipt() -> None:
    """F8: RECEIPT_EMITTED must be PASS on every returned receipt."""
    bad_stages = list(_all_stages(positive=True))
    bad_stages[-1] = RetrievalStageReceiptV1(
        stage=RetrievalStage.RECEIPT_EMITTED, outcome=StageOutcome.NOT_RUN, reason_code=None, safe_counts=_counts()
    )
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(stages=tuple(bad_stages), final_outcome=FinalOutcome.EVIDENCE_AVAILABLE))

def test_receipt_rejects_corpus_id_populated_before_corpus_resolved_passes() -> None:
    """F8: corpus_id must be null unless CORPUS_RESOLVED has recorded PASS
    (appendix nullability timing) - a receipt claiming a corpus_id while
    CORPUS_RESOLVED is still NOT_RUN/FAIL/DENY is invalid."""
    bad_stages = _stages_with({RetrievalStage.CORPUS_RESOLVED: (StageOutcome.FAIL, StageReasonCode.CORPUS_UNAVAILABLE)})
    kwargs = _base_receipt_kwargs(
        stages=bad_stages, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", final_outcome=FinalOutcome.CORPUS_UNAVAILABLE
    )
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**kwargs)

def test_receipt_allows_null_corpus_id_when_corpus_resolved_failed() -> None:
    bad_stages = _stages_with({RetrievalStage.CORPUS_RESOLVED: (StageOutcome.FAIL, StageReasonCode.CORPUS_UNAVAILABLE)})
    receipt = RetrievalReceiptV1(
        **_base_receipt_kwargs(stages=bad_stages, corpus_id=None, final_outcome=FinalOutcome.CORPUS_UNAVAILABLE)
    )
    assert receipt.corpus_id is None

def test_receipt_rejects_non_v4_or_identical_receipt_and_correlation_id() -> None:
    """RR2-F3/RR2-F6: each id must be UUIDv4 AND the two must be distinct
    even when each is individually valid."""
    import uuid

    v1_like = uuid.UUID("00000000-0000-1000-8000-000000000000")
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(receipt_id=v1_like))
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(retrieval_correlation_id=v1_like))
    shared = uuid4()
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(receipt_id=shared, retrieval_correlation_id=shared))

def test_every_negative_outcome_accepts_its_own_grammar_and_rejects_swapped() -> None:
    """RR2-F4/RR2-F5/RR2-F6/Amendment 4 5.5.10: all TEN negative FinalOutcome
    values (every literal but EVIDENCE_AVAILABLE) each construct a valid
    first-terminal-then-NOT_RUN grammar and reject an all-PASS history for
    that same outcome (including the pre-fix NO_EVIDENCE all-PASS shape the
    shared fixture used to fabricate); swapping ACCESS_DENIED's grammar onto
    NO_EVIDENCE, and AUTHENTICATED=FAIL (not DENY), are both rejected."""
    from _p4a1_retrieval_fixtures import _negative_terminal

    for outcome in FinalOutcome:
        if outcome == FinalOutcome.EVIDENCE_AVAILABLE:
            continue
        stage, out, reason = _negative_terminal(outcome)
        good = _stages_with({stage: (out, reason)})
        RetrievalReceiptV1(**_base_receipt_kwargs(final_outcome=outcome, stages=good))
        all_pass = tuple(
            RetrievalStageReceiptV1(stage=s, outcome=StageOutcome.PASS, reason_code=None, safe_counts=_counts())
            for s in RetrievalStage
        )
        with pytest.raises(ValidationError):
            RetrievalReceiptV1(**_base_receipt_kwargs(final_outcome=outcome, stages=all_pass))
    wrong_deny = _stages_with({RetrievalStage.AUTHENTICATED: (StageOutcome.FAIL, StageReasonCode.AUTHENTICATION_FAILED)})
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(final_outcome=FinalOutcome.ACCESS_DENIED, stages=wrong_deny))
    denied_stages = _stages_with({RetrievalStage.AUTHENTICATED: (StageOutcome.DENY, StageReasonCode.AUTHENTICATION_FAILED)})
    with pytest.raises(ValidationError):
        RetrievalReceiptV1(**_base_receipt_kwargs(final_outcome=FinalOutcome.NO_EVIDENCE, stages=denied_stages))
