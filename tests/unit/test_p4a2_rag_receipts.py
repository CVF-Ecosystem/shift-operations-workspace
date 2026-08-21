"""P4-A2 SPEC R15 - sanitized receipt construction and hash recomputation.

Only safe ids/hashes/versions/counts/outcomes/reason codes; every digest is
independently recomputable by tests rather than trusted from caller input.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from governed_rag.hashing import receipt_hash
from governed_rag.receipts import (
    RAG_STAGE_ORDER,
    GovernedRagReceiptV1,
    RagFinalOutcome,
    RagStage,
    RagStageOutcome,
    RagStageReceiptV1,
    build_receipt,
    build_stages,
)

DIGEST = "a" * 64


def _base_kwargs(**overrides):
    fields = dict(
        normalized_query_digest_sha256=DIGEST,
        retrieval_receipt_hash_sha256=DIGEST,
        retrieval_evidence_set_hash_sha256=DIGEST,
        authorization_scope_digest_sha256=DIGEST,
        corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        index_build_digest_sha256=DIGEST,
        encoder_version="1.0",
        lexicon_digest_sha256=DIGEST,
        score_policy_digest_sha256=DIGEST,
        pre_injection_citation_ids=(DIGEST,),
        post_injection_citation_ids=(DIGEST,),
        injection_omissions=(),
        minimization_ruleset_digest_sha256=DIGEST,
        minimization_input_digest_sha256=DIGEST,
        minimization_output_digest_sha256=DIGEST,
        minimization_retained_count=1,
        minimization_omitted_count=0,
        context_digest_sha256=DIGEST,
        output_schema_digest_sha256=DIGEST,
        gateway_request_digest_sha256=DIGEST,
        gateway_receipt_output_digest_sha256=DIGEST,
        provider_response_digest_sha256=DIGEST,
        validated_answer_digest_sha256=DIGEST,
        stages=build_stages(terminal_stage=None),
        final_outcome=RagFinalOutcome.ANSWERED,
        reason_code="",
        physical_attempt_count=1,
    )
    fields.update(overrides)
    return fields


def test_build_stages_all_pass_for_none_terminal():
    stages = build_stages(terminal_stage=None)
    assert len(stages) == 9
    assert all(s.outcome is RagStageOutcome.PASS for s in stages)
    assert tuple(s.stage for s in stages) == RAG_STAGE_ORDER


def test_build_stages_fail_then_not_run():
    stages = build_stages(terminal_stage=RagStage.INJECTION_SCREENED, terminal_reason="INJECTION_BLOCKED")
    outcomes = [s.outcome for s in stages]
    idx = list(RAG_STAGE_ORDER).index(RagStage.INJECTION_SCREENED)
    assert all(o is RagStageOutcome.PASS for o in outcomes[:idx])
    assert outcomes[idx] is RagStageOutcome.FAIL
    assert all(o is RagStageOutcome.NOT_RUN for o in outcomes[idx + 1 :])
    assert stages[idx].reason_code == "INJECTION_BLOCKED"


def test_build_stages_earliest_terminal_stage():
    stages = build_stages(terminal_stage=RagStage.REQUEST_VALIDATED, terminal_reason="REQUEST_INVALID")
    assert stages[0].outcome is RagStageOutcome.FAIL
    assert all(s.outcome is RagStageOutcome.NOT_RUN for s in stages[1:])


def test_receipt_hash_is_recomputable_by_caller():
    receipt = build_receipt(**_base_kwargs())
    dump = receipt.model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    assert receipt_hash(dump) == receipt.receipt_hash_sha256


def test_receipt_hash_changes_when_any_field_changes():
    receipt_a = build_receipt(**_base_kwargs())
    receipt_b = build_receipt(**_base_kwargs(corpus_id="SHIFT_ADVISORY_MESSAGES_V1"))
    assert receipt_a.receipt_hash_sha256 != receipt_b.receipt_hash_sha256


def test_negative_receipt_requires_zero_physical_attempts():
    receipt = build_receipt(
        **_base_kwargs(
            final_outcome=RagFinalOutcome.INJECTION_BLOCKED,
            reason_code="INJECTION_BLOCKED",
            physical_attempt_count=0,
            stages=build_stages(terminal_stage=RagStage.INJECTION_SCREENED, terminal_reason="INJECTION_BLOCKED"),
        )
    )
    assert receipt.physical_attempt_count == 0
    assert receipt.final_outcome is RagFinalOutcome.INJECTION_BLOCKED


def test_answered_receipt_requires_exactly_one_attempt():
    receipt = build_receipt(**_base_kwargs())
    assert receipt.final_outcome is RagFinalOutcome.ANSWERED
    assert receipt.physical_attempt_count == 1


def test_receipt_contains_no_query_or_body_text():
    receipt = build_receipt(**_base_kwargs())
    dump = receipt.model_dump(mode="python")
    # Digest-shaped or safe-id-shaped fields only - never free-form prose;
    # bounded to a small length ceiling even for the exempted safe fields.
    safe_short_fields = {"corpus_id", "encoder_id", "encoder_version", "reason_code", "contract_version"}
    for key, value in dump.items():
        if isinstance(value, str) and key not in safe_short_fields and key != "final_outcome":
            assert value == "" or len(value) == 64, f"{key} is not digest-shaped: {value!r}"
        elif isinstance(value, str):
            assert len(value) <= 64, f"{key} exceeds the safe short-field bound: {value!r}"

    assert "query" not in dump
    assert "prompt" not in dump
    assert "evidence" not in dump
    assert "output_body" not in dump


def test_post_injection_ids_must_be_subset_of_pre_injection_ids():
    with pytest.raises(ValidationError):
        build_receipt(
            **_base_kwargs(pre_injection_citation_ids=(DIGEST,), post_injection_citation_ids=("b" * 64,))
        )


def test_stage_receipt_requires_reason_code_only_on_fail():
    with pytest.raises(ValidationError):
        RagStageReceiptV1(stage=RagStage.RANKED, outcome=RagStageOutcome.PASS, reason_code="SHOULD_NOT_BE_HERE")
    with pytest.raises(ValidationError):
        RagStageReceiptV1(stage=RagStage.RANKED, outcome=RagStageOutcome.FAIL, reason_code="")


# ---------------------------------------------------------------------------
# P4A2-REV-F6 - receipt integrity must not fail open. The model's OWN
# validator recomputes the hash / enforces terminal grammar, so direct
# construction and model_construct bypass attempts are caught, not just the
# builder's own (bypassable) computation.
# ---------------------------------------------------------------------------


def test_direct_construction_with_forged_hash_rejected():
    """Directly constructing GovernedRagReceiptV1 (not via build_receipt)
    with an arbitrary forged receipt_hash_sha256 must be rejected by the
    model's own validator, not just by the builder computing it correctly."""
    fields = _base_kwargs()
    fields["receipt_hash_sha256"] = "f" * 64  # forged, does not cover the real fields
    with pytest.raises(ValidationError):
        GovernedRagReceiptV1(**fields)


def test_model_construct_bypass_with_forged_hash_still_rejected_on_reconstruction():
    """model_construct itself skips validators (a caller programming-error
    escape hatch), but any REAL construction of the model from that same
    forged data must still fail - proving the hash check is a model
    validator, not solely a builder-time computation the model would
    otherwise trust."""
    fields = _base_kwargs()
    fields["receipt_hash_sha256"] = "f" * 64
    bypassed = GovernedRagReceiptV1.model_construct(**fields)
    assert bypassed.receipt_hash_sha256 == "f" * 64  # bypass succeeded, as expected
    with pytest.raises(ValidationError):
        GovernedRagReceiptV1(**dict(bypassed))


def test_frozen_model_rejects_single_field_mutation_after_construction():
    receipt = build_receipt(**_base_kwargs())
    with pytest.raises(ValidationError):
        receipt.corpus_id = "SHIFT_ADVISORY_MESSAGES_V1"


def test_answered_outcome_with_a_fail_stage_rejected_as_contradictory():
    """ANSWERED requires every stage PASS; a receipt claiming ANSWERED while
    also carrying a FAIL stage is a contradictory terminal-state
    construction and must be rejected by the model's own grammar check."""
    with pytest.raises(ValidationError):
        build_receipt(**_base_kwargs(
            final_outcome=RagFinalOutcome.ANSWERED,
            stages=build_stages(terminal_stage=RagStage.MINIMIZED, terminal_reason="MINIMIZATION_FAILED"),
        ))


def test_terminal_stage_must_match_the_outcome_specific_mapped_stage():
    """A FAIL at the wrong stage for the declared outcome (e.g. STALE_INDEX
    failing at INJECTION_SCREENED instead of INDEX_VALIDATED) is rejected -
    proving the check binds outcome to the SPECIFIC stage, not just "some"
    FAIL stage anywhere in the sequence."""
    with pytest.raises(ValidationError):
        build_receipt(**_base_kwargs(
            final_outcome=RagFinalOutcome.STALE_INDEX, reason_code="STALE_INDEX", physical_attempt_count=0,
            stages=build_stages(terminal_stage=RagStage.INJECTION_SCREENED, terminal_reason="STALE_INDEX"),
        ))


def test_answered_with_null_aggregate_minimization_digest_rejected():
    """A positive receipt can never carry a null aggregate minimization
    input/output digest - fail-open would otherwise let an ANSWERED outcome
    through with no provable minimization lineage."""
    with pytest.raises(ValidationError):
        build_receipt(**_base_kwargs(minimization_input_digest_sha256=None))
    with pytest.raises(ValidationError):
        build_receipt(**_base_kwargs(minimization_output_digest_sha256=None))


def test_gateway_request_digest_binds_more_than_just_context_digest():
    """Two receipts built from a different provider_id/placement but the
    SAME context digest must have different gateway_request_digest_sha256 -
    proving it binds a safe projection of the real request, not just the
    context digest alone."""
    from governed_rag.hashing import gateway_request_safe_digest

    a = gateway_request_safe_digest(
        context_digest_sha256=DIGEST, provider_id="p1", model_id="m1", placement="local",
        output_schema_digest_sha256=DIGEST, per_request_token_limit=100,
        terminate_when=(), timeout_seconds=30, max_output_tokens=2000,
    )
    b = gateway_request_safe_digest(
        context_digest_sha256=DIGEST, provider_id="p1", model_id="m1", placement="external",
        output_schema_digest_sha256=DIGEST, per_request_token_limit=100,
        terminate_when=(), timeout_seconds=30, max_output_tokens=2000,
    )
    assert a != b
