"""P4-A2 SPEC R10 - MINIMIZATION_EXTRACTIVE_V1 deterministic minimization.

Proof binds input/output/ruleset digests, exact counts and omissions and is
independently recomputable. External placement is impossible unless this
proof recomputes positively and non-empty.
"""

from __future__ import annotations

from governed_rag.hashing import minimization_input_digest, minimization_output_digest
from governed_rag.minimization import RULESET_DIGEST_SHA256, minimize_all, minimize_record

C1 = "1" * 64
C2 = "2" * 64


def test_relevant_sentence_is_retained():
    snippet = "Shift handover requires a written summary of open incidents. The weather was mild."
    proof, record = minimize_record(citation_id=C1, source_snippet=snippet, query="handover procedure")
    assert record is not None
    assert not proof.omitted
    assert "handover" in record.minimized_text.lower()
    assert "weather" not in record.minimized_text.lower()


def test_irrelevant_snippet_is_omitted_with_no_query_match_reason():
    snippet = "The weather today is mild with a light breeze from the north."
    proof, record = minimize_record(citation_id=C1, source_snippet=snippet, query="handover procedure")
    assert record is None
    assert proof.omitted
    assert "NO_QUERY_OR_CONCEPT_MATCH" in [r.value for r in proof.omission_reasons]


def test_secret_pattern_sentence_is_rejected():
    snippet = "The handover api_key: sk-abcdef123456 must not be shared."
    proof, record = minimize_record(citation_id=C1, source_snippet=snippet, query="handover procedure")
    # the only sentence contains a secret pattern, so it is excluded even
    # though it is otherwise topically relevant, leaving nothing retained.
    assert record is None
    assert proof.omitted


def test_control_character_snippet_is_rejected_outright():
    snippet = "Handover notes\x07 contain a stray control character."
    proof, record = minimize_record(citation_id=C1, source_snippet=snippet, query="handover")
    assert record is None
    assert "UNICODE_CONTROL_PRESENT" in [r.value for r in proof.omission_reasons]


def test_proof_input_digest_matches_recomputation():
    snippet = "Shift handover requires a written summary of open incidents."
    proof, _ = minimize_record(citation_id=C1, source_snippet=snippet, query="handover")
    expected = minimization_input_digest(citation_id=C1, source_snippet=snippet)
    assert proof.input_digest_sha256 == expected


def test_proof_output_digest_matches_recomputation():
    snippet = "Shift handover requires a written summary of open incidents."
    proof, record = minimize_record(citation_id=C1, source_snippet=snippet, query="handover")
    assert record is not None
    expected = minimization_output_digest(citation_id=C1, minimized_text=record.minimized_text)
    assert proof.output_digest_sha256 == expected


def test_ruleset_digest_is_fixed_and_shared():
    snippet = "Shift handover requires a written summary of open incidents."
    proof, _ = minimize_record(citation_id=C1, source_snippet=snippet, query="handover")
    assert proof.ruleset_digest_sha256 == RULESET_DIGEST_SHA256


def test_minimization_is_deterministic():
    snippet = "Shift handover requires a written summary of open incidents. Escalate if unresolved."
    proof1, record1 = minimize_record(citation_id=C1, source_snippet=snippet, query="handover escalation")
    proof2, record2 = minimize_record(citation_id=C1, source_snippet=snippet, query="handover escalation")
    assert proof1 == proof2
    assert record1 == record2


def test_per_record_codepoint_ceiling_enforced():
    long_sentence = "Handover " + ("detail " * 200) + "concludes here."
    proof, record = minimize_record(citation_id=C1, source_snippet=long_sentence, query="handover")
    if record is not None:
        assert len(record.minimized_text) <= 480


def test_minimize_all_never_produces_output_body_only_proof_and_records():
    records = (
        (C1, "Shift handover requires a written summary of open incidents."),
        (C2, "The weather today is mild with a light breeze."),
    )
    proof, minimized = minimize_all(records=records, query="handover procedure")
    assert proof.retained_count == 1
    assert proof.omitted_count == 1
    assert len(minimized) == 1
    assert minimized[0].citation_id == C1


def test_minimize_all_counts_match_records_split():
    records = (
        (C1, "Shift handover requires a written summary of open incidents."),
        (C2, "Escalation policy requires supervisor sign-off within limits."),
    )
    proof, minimized = minimize_all(records=records, query="handover escalation")
    assert proof.retained_count == len(minimized)
    assert proof.retained_count + proof.omitted_count == len(records)


def test_minimize_all_returns_empty_when_all_omitted():
    records = ((C1, "Nothing here relates to the query at all whatsoever."),)
    proof, minimized = minimize_all(records=records, query="handover procedure")
    assert minimized == ()
    assert proof.retained_count == 0
    assert proof.omitted_count == 1


def test_minimize_all_proof_is_independently_recomputable():
    records = ((C1, "Shift handover requires a written summary of open incidents."),)
    proof1, minimized1 = minimize_all(records=records, query="handover")
    proof2, minimized2 = minimize_all(records=records, query="handover")
    assert proof1 == proof2
    assert minimized1 == minimized2


def test_no_record_bodies_leak_into_proof_only_digests():
    records = ((C1, "Shift handover requires a written summary of open incidents."),)
    proof, _ = minimize_all(records=records, query="handover")
    dump = proof.model_dump(mode="python")
    assert "handover requires a written summary" not in str(dump)
