"""P4-A2 SPEC R2 - strict, frozen, closed-enum contract models.

Model adversary tests: unknown fields, non-frozen mutation attempts, bad
enum members, and cross-field invariant violations must all fail closed.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from governed_rag import (
    AnswerStatus,
    ClaimV1,
    EphemeralIndexV1,
    GovernedRagAnswerV1,
    GovernedRagRequestV1,
    IndexEntryV1,
    InjectionOmissionV1,
    InjectionReasonCode,
    MinimizationOmissionReason,
    MinimizationProofV1,
    MinimizationRecordProofV1,
    ScoredCitationV1,
)
from governed_rag.models import ContextBudgetPolicyV1

DIGEST = "a" * 64
DIGEST2 = "b" * 64


def _budget_policy(**overrides) -> ContextBudgetPolicyV1:
    fields = dict(
        max_minimized_records=4, max_context_codepoints=1000,
        max_context_utf8_bytes=3000, max_context_estimated_tokens=800,
    )
    fields.update(overrides)
    return ContextBudgetPolicyV1(**fields)


class TestGovernedRagRequestV1:
    def test_rejects_unknown_fields(self):
        with pytest.raises(ValidationError):
            GovernedRagRequestV1(
                query="q", corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", provider_id="p",
                model_id="m", context_budget_policy=_budget_policy(), unexpected="x",
            )

    def test_is_frozen(self):
        req = GovernedRagRequestV1(
            query="q", corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", provider_id="p",
            model_id="m", context_budget_policy=_budget_policy(),
        )
        with pytest.raises(ValidationError):
            req.query = "other"

    def test_rejects_empty_query(self):
        with pytest.raises(ValidationError):
            GovernedRagRequestV1(
                query="", corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", provider_id="p",
                model_id="m", context_budget_policy=_budget_policy(),
            )

    def test_rejects_oversized_query(self):
        with pytest.raises(ValidationError):
            GovernedRagRequestV1(
                query="x" * 513, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", provider_id="p",
                model_id="m", context_budget_policy=_budget_policy(),
            )

    def test_rejects_bad_timeout_bounds(self):
        with pytest.raises(ValidationError):
            GovernedRagRequestV1(
                query="q", corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1", provider_id="p",
                model_id="m", context_budget_policy=_budget_policy(), timeout_seconds=0,
            )


class TestContextBudgetPolicyV1:
    def test_rejects_records_above_server_ceiling(self):
        with pytest.raises(ValidationError):
            _budget_policy(max_minimized_records=5)

    def test_rejects_bytes_above_server_ceiling(self):
        with pytest.raises(ValidationError):
            _budget_policy(max_context_utf8_bytes=999999)

    def test_rejects_zero_or_negative(self):
        with pytest.raises(ValidationError):
            _budget_policy(max_minimized_records=0)


class TestScoredCitationV1:
    def test_fusion_must_be_exact_integer_arithmetic(self):
        with pytest.raises(ValidationError):
            ScoredCitationV1(citation_id=DIGEST, lexical_score=100000, semantic_score=200000, fused_score=999999)

    def test_valid_fusion_accepted(self):
        expected = (100000 * 45 + 200000 * 55) // 100
        scored = ScoredCitationV1(citation_id=DIGEST, lexical_score=100000, semantic_score=200000, fused_score=expected)
        assert scored.fused_score == expected

    def test_rejects_score_above_max(self):
        with pytest.raises(ValidationError):
            ScoredCitationV1(citation_id=DIGEST, lexical_score=1_000_001, semantic_score=0, fused_score=0)

    def test_rejects_negative_score(self):
        with pytest.raises(ValidationError):
            ScoredCitationV1(citation_id=DIGEST, lexical_score=-1, semantic_score=0, fused_score=0)


class TestInjectionOmissionV1:
    def test_requires_at_least_one_reason(self):
        with pytest.raises(ValidationError):
            InjectionOmissionV1(citation_id=DIGEST, reason_codes=())

    def test_rejects_duplicate_reasons(self):
        with pytest.raises(ValidationError):
            InjectionOmissionV1(
                citation_id=DIGEST,
                reason_codes=(InjectionReasonCode.ROLE_MARKER, InjectionReasonCode.ROLE_MARKER),
            )

    def test_accepts_multiple_distinct_reasons(self):
        omission = InjectionOmissionV1(
            citation_id=DIGEST,
            reason_codes=(InjectionReasonCode.ROLE_MARKER, InjectionReasonCode.TOOL_INSTRUCTION),
        )
        assert len(omission.reason_codes) == 2


class TestMinimizationRecordProofV1:
    def test_omitted_record_must_have_no_output_digest(self):
        with pytest.raises(ValidationError):
            MinimizationRecordProofV1(
                citation_id=DIGEST, input_digest_sha256=DIGEST2, output_digest_sha256=DIGEST,
                ruleset_digest_sha256=DIGEST, algorithm="MINIMIZATION_EXTRACTIVE_V1",
                sentence_count_in=1, sentence_count_out=0, output_codepoints=0,
                output_utf8_bytes=0, output_estimated_tokens=0, omitted=True,
                omission_reasons=(MinimizationOmissionReason.NO_QUERY_OR_CONCEPT_MATCH,),
            )

    def test_retained_record_requires_output_digest(self):
        with pytest.raises(ValidationError):
            MinimizationRecordProofV1(
                citation_id=DIGEST, input_digest_sha256=DIGEST2, output_digest_sha256=None,
                ruleset_digest_sha256=DIGEST, algorithm="MINIMIZATION_EXTRACTIVE_V1",
                sentence_count_in=1, sentence_count_out=1, output_codepoints=10,
                output_utf8_bytes=10, output_estimated_tokens=5, omitted=False, omission_reasons=(),
            )

    def test_retained_record_must_carry_no_omission_reasons(self):
        with pytest.raises(ValidationError):
            MinimizationRecordProofV1(
                citation_id=DIGEST, input_digest_sha256=DIGEST2, output_digest_sha256=DIGEST,
                ruleset_digest_sha256=DIGEST, algorithm="MINIMIZATION_EXTRACTIVE_V1",
                sentence_count_in=1, sentence_count_out=1, output_codepoints=10,
                output_utf8_bytes=10, output_estimated_tokens=5, omitted=False,
                omission_reasons=(MinimizationOmissionReason.NO_QUERY_OR_CONCEPT_MATCH,),
            )


class TestMinimizationProofV1:
    def test_counts_must_match_records(self):
        record = MinimizationRecordProofV1(
            citation_id=DIGEST, input_digest_sha256=DIGEST2, output_digest_sha256=DIGEST,
            ruleset_digest_sha256=DIGEST, algorithm="MINIMIZATION_EXTRACTIVE_V1",
            sentence_count_in=1, sentence_count_out=1, output_codepoints=10,
            output_utf8_bytes=10, output_estimated_tokens=5, omitted=False, omission_reasons=(),
        )
        with pytest.raises(ValidationError):
            MinimizationProofV1(
                ruleset_digest_sha256=DIGEST, records=(record,), retained_count=0, omitted_count=0
            )


class TestGovernedRagAnswerV1:
    def test_answer_requires_at_least_one_claim(self):
        with pytest.raises(ValidationError):
            GovernedRagAnswerV1(status=AnswerStatus.ANSWER, claims=(), abstention_reason="")

    def test_answer_must_not_carry_abstention_reason(self):
        with pytest.raises(ValidationError):
            GovernedRagAnswerV1(
                status=AnswerStatus.ANSWER,
                claims=(ClaimV1(text="x", citation_ids=(DIGEST,)),),
                abstention_reason="should not be here",
            )

    def test_abstain_requires_reason(self):
        with pytest.raises(ValidationError):
            GovernedRagAnswerV1(status=AnswerStatus.ABSTAIN, claims=(), abstention_reason="")

    def test_abstain_must_carry_no_claims(self):
        with pytest.raises(ValidationError):
            GovernedRagAnswerV1(
                status=AnswerStatus.ABSTAIN,
                claims=(ClaimV1(text="x", citation_ids=(DIGEST,)),),
                abstention_reason="insufficient",
            )

    def test_claim_rejects_duplicate_citations(self):
        with pytest.raises(ValidationError):
            ClaimV1(text="x", citation_ids=(DIGEST, DIGEST))

    def test_claim_requires_at_least_one_citation(self):
        with pytest.raises(ValidationError):
            ClaimV1(text="x", citation_ids=())

    def test_claim_rejects_more_than_four_citations(self):
        with pytest.raises(ValidationError):
            ClaimV1(text="x", citation_ids=tuple(f"{i}" * 64 for i in range(5)))

    def test_valid_answer_accepted(self):
        answer = GovernedRagAnswerV1(
            status=AnswerStatus.ANSWER, claims=(ClaimV1(text="x", citation_ids=(DIGEST,)),), abstention_reason=""
        )
        assert answer.status is AnswerStatus.ANSWER


class TestEphemeralIndexV1:
    def _entry(self, citation_id: str = DIGEST) -> IndexEntryV1:
        return IndexEntryV1(
            citation_id=citation_id, content_digest_sha256=DIGEST2, source_digest_sha256=DIGEST2,
            version_dump={"kind": "SOURCE_VERSION_STRING", "source_version_string": "v1"},
            field_selector="document", truth_class="ADVISORY_SOURCE_EVIDENCE",
            source_cutoff_utc=datetime(2026, 8, 21, tzinfo=timezone.utc), encoder_id="PROJECT_CONCEPT_FEATURE_VECTOR_V1",
            encoder_version="1.0", lexicon_digest_sha256=DIGEST2, feature_vector_digest_sha256=DIGEST2,
            feature_ids=("TOK_a", "TOK_b"), entry_digest_sha256=DIGEST2,
        )

    def test_rejects_duplicate_citation_entries(self):
        entry = self._entry()
        with pytest.raises(ValidationError):
            EphemeralIndexV1(
                authorization_scope_digest_sha256=DIGEST, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
                entries=(entry, entry), index_build_digest_sha256=DIGEST, evidence_set_hash_sha256=DIGEST,
            )

    def test_rejects_more_than_four_entries(self):
        entries = tuple(self._entry(citation_id=f"{i}" * 64) for i in range(5))
        with pytest.raises(ValidationError):
            EphemeralIndexV1(
                authorization_scope_digest_sha256=DIGEST, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
                entries=entries, index_build_digest_sha256=DIGEST, evidence_set_hash_sha256=DIGEST,
            )

    def test_valid_index_accepted(self):
        idx = EphemeralIndexV1(
            authorization_scope_digest_sha256=DIGEST, corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
            entries=(self._entry(),), index_build_digest_sha256=DIGEST, evidence_set_hash_sha256=DIGEST,
        )
        assert len(idx.entries) == 1


class TestIndexEntryV1:
    def test_rejects_duplicate_feature_ids(self):
        with pytest.raises(ValidationError):
            IndexEntryV1(
                citation_id=DIGEST, content_digest_sha256=DIGEST2, source_digest_sha256=DIGEST2,
                version_dump={"kind": "UNVERSIONED"}, field_selector="document",
                truth_class="ADVISORY_SOURCE_EVIDENCE", source_cutoff_utc=datetime(2026, 8, 21, tzinfo=timezone.utc),
                encoder_id="PROJECT_CONCEPT_FEATURE_VECTOR_V1", encoder_version="1.0",
                lexicon_digest_sha256=DIGEST2, feature_vector_digest_sha256=DIGEST2,
                feature_ids=("TOK_a", "TOK_a"), entry_digest_sha256=DIGEST2,
            )

    def test_rejects_wrong_encoder_id_literal(self):
        with pytest.raises(ValidationError):
            IndexEntryV1(
                citation_id=DIGEST, content_digest_sha256=DIGEST2, source_digest_sha256=DIGEST2,
                version_dump={"kind": "UNVERSIONED"}, field_selector="document",
                truth_class="ADVISORY_SOURCE_EVIDENCE", source_cutoff_utc=datetime(2026, 8, 21, tzinfo=timezone.utc),
                encoder_id="SOME_OTHER_ENCODER", encoder_version="1.0",
                lexicon_digest_sha256=DIGEST2, feature_vector_digest_sha256=DIGEST2,
                feature_ids=(), entry_digest_sha256=DIGEST2,
            )
