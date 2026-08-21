"""P4-A2 SPEC R6/R7/R8/R10/R11/R15 - canonical digest determinism.

Every digest helper must be a pure function of its explicit preimage:
identical input always produces an identical digest, and a changed input
(including key order, since the underlying canonical JSON sorts keys)
must never silently produce the same digest.
"""

from __future__ import annotations

from governed_rag.hashing import (
    answer_digest,
    context_digest,
    feature_vector_digest,
    index_build_digest,
    index_entry_digest,
    lexicon_digest,
    minimization_input_digest,
    minimization_output_digest,
    minimization_ruleset_digest,
    normalized_query_digest,
    ordered_evidence_set_hash,
    output_schema_digest,
    receipt_hash,
    score_policy_digest,
)


def test_lexicon_digest_is_deterministic_and_order_independent_for_dict_construction():
    a = lexicon_digest({"X": ("a", "b"), "Y": ("c",)})
    b = lexicon_digest({"Y": ("c",), "X": ("a", "b")})
    assert a == b


def test_lexicon_digest_changes_with_content():
    a = lexicon_digest({"X": ("a", "b")})
    b = lexicon_digest({"X": ("a", "c")})
    assert a != b


def test_feature_vector_digest_is_order_independent():
    a = feature_vector_digest(("TOK_a", "TOK_b"))
    b = feature_vector_digest(("TOK_b", "TOK_a"))
    assert a == b


def test_feature_vector_digest_changes_with_membership():
    a = feature_vector_digest(("TOK_a",))
    b = feature_vector_digest(("TOK_a", "TOK_b"))
    assert a != b


def test_index_entry_digest_deterministic():
    kwargs = dict(
        citation_id="a" * 64, content_digest_sha256="b" * 64, source_digest_sha256="c" * 64,
        version_dump={"kind": "UNVERSIONED"}, field_selector="document", truth_class="ADVISORY_SOURCE_EVIDENCE",
        source_cutoff_utc="2026-08-21T00:00:00Z", encoder_id="PROJECT_CONCEPT_FEATURE_VECTOR_V1",
        encoder_version="1.0", lexicon_digest_sha256="d" * 64, feature_vector_digest_sha256="e" * 64,
    )
    assert index_entry_digest(**kwargs) == index_entry_digest(**kwargs)


def test_index_entry_digest_changes_with_any_identity_field():
    base = dict(
        citation_id="a" * 64, content_digest_sha256="b" * 64, source_digest_sha256="c" * 64,
        version_dump={"kind": "UNVERSIONED"}, field_selector="document", truth_class="ADVISORY_SOURCE_EVIDENCE",
        source_cutoff_utc="2026-08-21T00:00:00Z", encoder_id="PROJECT_CONCEPT_FEATURE_VECTOR_V1",
        encoder_version="1.0", lexicon_digest_sha256="d" * 64, feature_vector_digest_sha256="e" * 64,
    )
    original = index_entry_digest(**base)
    for field, new_value in (
        ("content_digest_sha256", "f" * 64),
        ("field_selector", "other"),
        ("encoder_version", "2.0"),
        ("lexicon_digest_sha256", "f" * 64),
    ):
        mutated = dict(base)
        mutated[field] = new_value
        assert index_entry_digest(**mutated) != original, f"digest did not change for {field}"


def test_index_build_digest_order_preserving_over_entry_digests():
    a = index_build_digest(authorization_scope_digest_sha256="a" * 64, corpus_id="C", entry_digests=("1" * 64, "2" * 64))
    b = index_build_digest(authorization_scope_digest_sha256="a" * 64, corpus_id="C", entry_digests=("2" * 64, "1" * 64))
    assert a != b, "entry order must be preserved, unlike lexicon digesting"


def test_ordered_evidence_set_hash_is_order_preserving():
    a = ordered_evidence_set_hash(("1" * 64, "2" * 64))
    b = ordered_evidence_set_hash(("2" * 64, "1" * 64))
    assert a != b


def test_score_policy_digest_changes_with_weights():
    a = score_policy_digest(lexical_weight=45, semantic_weight=55, policy_id="P")
    b = score_policy_digest(lexical_weight=50, semantic_weight=50, policy_id="P")
    assert a != b


def test_minimization_digests_bind_citation_and_text():
    a = minimization_input_digest(citation_id="a" * 64, source_snippet="hello world")
    b = minimization_input_digest(citation_id="a" * 64, source_snippet="hello there")
    assert a != b
    c = minimization_output_digest(citation_id="a" * 64, minimized_text="hello world")
    d = minimization_output_digest(citation_id="b" * 64, minimized_text="hello world")
    assert c != d


def test_minimization_ruleset_digest_deterministic():
    assert minimization_ruleset_digest(ruleset_id="R", version="1.0") == minimization_ruleset_digest(
        ruleset_id="R", version="1.0"
    )


def test_context_digest_binds_instructions_and_records():
    a = context_digest(instruction_contract_dump={"a": 1}, evidence_record_dumps=[{"citation_id": "x"}])
    b = context_digest(instruction_contract_dump={"a": 2}, evidence_record_dumps=[{"citation_id": "x"}])
    assert a != b
    c = context_digest(instruction_contract_dump={"a": 1}, evidence_record_dumps=[{"citation_id": "y"}])
    assert a != c


def test_normalized_query_digest_changes_with_text():
    assert normalized_query_digest("a") != normalized_query_digest("b")


def test_output_schema_digest_changes_with_schema():
    a = output_schema_digest({"type": "object", "properties": {}})
    b = output_schema_digest({"type": "object", "properties": {"x": {"type": "string"}}})
    assert a != b


def test_answer_digest_changes_with_content():
    a = answer_digest({"status": "ANSWER"})
    b = answer_digest({"status": "ABSTAIN"})
    assert a != b


def test_receipt_hash_is_independently_recomputable():
    dump = {"a": 1, "b": [1, 2, 3], "c": {"nested": "value"}}
    h1 = receipt_hash(dump)
    h2 = receipt_hash(dict(dump))
    assert h1 == h2


def test_receipt_hash_changes_with_any_field():
    dump = {"a": 1, "b": 2}
    mutated = {"a": 1, "b": 3}
    assert receipt_hash(dump) != receipt_hash(mutated)


def test_digests_are_lowercase_hex_sha256():
    value = normalized_query_digest("some query")
    assert len(value) == 64
    assert all(c in "0123456789abcdef" for c in value)
