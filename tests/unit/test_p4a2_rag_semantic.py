"""P4-A2 SPEC R6 - PROJECT_CONCEPT_FEATURE_VECTOR_V1 semantic substrate.

Deterministic, dependency-free, versioned. Includes the mandatory
zero-exact-token-overlap synonym-pair proof: two words sharing no lexical
token must still change semantic ranking through the reviewed concept
lexicon, and the claim is explicitly bounded to that lexicon (not a general
embeddings claim).
"""

from __future__ import annotations

from governed_rag.semantic import (
    ENCODER_ID,
    ENCODER_VERSION,
    LEXICON_DIGEST_SHA256,
    PROJECT_CONCEPT_LEXICON,
    feature_ids,
    semantic_score,
    tokenize,
)


def test_encoder_identity_is_fixed_and_versioned():
    assert ENCODER_ID == "PROJECT_CONCEPT_FEATURE_VECTOR_V1"
    assert ENCODER_VERSION
    assert isinstance(LEXICON_DIGEST_SHA256, str)
    assert len(LEXICON_DIGEST_SHA256) == 64


def test_lexicon_digest_is_deterministic_across_import():
    # re-import path check: the module-level constant must be stable.
    import importlib

    import governed_rag.semantic as semantic_module

    reloaded = importlib.reload(semantic_module)
    assert reloaded.LEXICON_DIGEST_SHA256 == LEXICON_DIGEST_SHA256
    importlib.reload(semantic_module)  # restore normal module state for later tests


def test_tokenize_is_deterministic_and_case_insensitive():
    a = tokenize("Shift Handover")
    b = tokenize("shift handover")
    assert a == b == ("shift", "handover")


def test_feature_ids_are_sorted_and_deduplicated():
    features = feature_ids("shift shift handover")
    assert list(features) == sorted(set(features))


def test_zero_exact_token_overlap_synonym_pair_changes_semantic_ranking():
    """SPEC R6/DESIGN mandatory proof: 'turnover' and 'handover' share no
    exact lexical token, yet both map to the same reviewed CONCEPT_HANDOVER
    lexicon entry, so their semantic score must be strictly greater than an
    unrelated pair's semantic score. The claim is bounded to this project
    lexicon - not a general synonym/embeddings capability."""
    query_features = feature_ids("turnover")
    handover_features = feature_ids("handover")
    unrelated_features = feature_ids("completely different topic entirely")

    query_tokens = {f for f in query_features if f.startswith("TOK_")}
    handover_tokens = {f for f in handover_features if f.startswith("TOK_")}
    assert not (query_tokens & handover_tokens), "fixture must have zero exact token overlap"

    query_concepts = {f for f in query_features if f.startswith("CONCEPT_")}
    handover_concepts = {f for f in handover_features if f.startswith("CONCEPT_")}
    assert query_concepts & handover_concepts, "reviewed synonym pair must share a concept feature"

    synonym_score = semantic_score(query_features, handover_features)
    unrelated_score = semantic_score(query_features, unrelated_features)
    assert synonym_score > unrelated_score
    assert synonym_score > 0
    assert unrelated_score == 0


def test_concept_lexicon_removal_lowers_the_synonym_score():
    """Proves the concept lexicon is load-bearing: stripping CONCEPT_ features
    from both sides must strictly lower the synonym pair's score relative to
    the with-concepts score (never merely equal), confirming the semantic
    component is not simply duplicating the lexical/trigram score."""
    query_features = feature_ids("turnover")
    handover_features = feature_ids("handover")
    with_concepts = semantic_score(query_features, handover_features)

    query_without = tuple(f for f in query_features if not f.startswith("CONCEPT_"))
    handover_without = tuple(f for f in handover_features if not f.startswith("CONCEPT_"))
    without_concepts = semantic_score(query_without, handover_without)

    assert with_concepts > without_concepts


def test_semantic_score_is_symmetric_for_jaccard_overlap():
    a = feature_ids("shift handover checklist")
    b = feature_ids("handover checklist review")
    assert semantic_score(a, b) == semantic_score(b, a)


def test_semantic_score_bounds():
    a = feature_ids("shift handover")
    identical_score = semantic_score(a, a)
    assert identical_score == 1_000_000
    empty_score = semantic_score((), a)
    assert empty_score == 0


def test_semantic_score_is_deterministic_repeat_calls():
    a = feature_ids("incident escalation procedure")
    b = feature_ids("escalation for incidents")
    first = semantic_score(a, b)
    second = semantic_score(a, b)
    assert first == second


def test_lexicon_every_concept_has_multiple_reviewed_terms():
    for concept, terms in PROJECT_CONCEPT_LEXICON.items():
        assert concept.startswith("CONCEPT_")
        assert len(terms) >= 2, f"{concept} should have at least two reviewed synonym terms"


def test_feature_ids_bounded_and_namespaced():
    features = feature_ids("shift handover incident escalation report")
    for f in features:
        assert f.startswith("TOK_") or f.startswith("TRI_") or f.startswith("CONCEPT_")
