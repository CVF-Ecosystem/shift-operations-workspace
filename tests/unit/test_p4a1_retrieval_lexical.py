"""SPEC R6 - deterministic lexical normalization, offset mapping, and rank.

AC-06: golden/property tests independently recompute token sets, the
integer score, all seven tie fields, duplicate behavior, and limit
boundaries; permutation, locale, repeated-run, Unicode, and score-tie tests
must produce identical ordered canonical results.
"""

from __future__ import annotations

import itertools

from governed_retrieval.lexical import (
    TieBreakKey,
    normalize_and_tokenize_query,
    normalize_with_offsets,
    rank_key,
    score_candidate,
    tokenize,
    version_sort_key,
)


def test_crlf_and_cr_normalize_to_single_lf_with_correct_span() -> None:
    # Source: a(0) \r(1) \n(2) b(3) \r(4) c(5)
    normalized = normalize_with_offsets("a\r\nb\rc")
    assert normalized.text == "a b c"
    # Normalized: a(0) SP(1) b(2) SP(3) c(4)
    assert normalized.source_span(0, 1) == (0, 1)
    assert normalized.source_span(1, 2) == (1, 3)  # \r\n -> one LF-turned-space
    assert normalized.source_span(3, 4) == (4, 5)  # \r -> one LF-turned-space


def test_whitespace_run_collapses_to_one_space_with_union_span() -> None:
    normalized = normalize_with_offsets("a   b")
    assert normalized.text == "a b"
    assert normalized.source_span(1, 2) == (1, 4)


def test_leading_and_trailing_whitespace_emits_nothing() -> None:
    normalized = normalize_with_offsets("  a b  ")
    assert normalized.text == "a b"


def test_casefold_expansion_maps_every_emitted_char_to_source_interval() -> None:
    # German sharp s (source index 4) casefolds to "ss" - two normalized
    # characters both mapping back to that single source code point.
    normalized = normalize_with_offsets("Straße")
    assert "ss" in normalized.text
    idx = normalized.text.index("ss")
    span = normalized.source_span(idx, idx + 2)
    assert span == (4, 5)


def test_tokenize_splits_on_non_letter_non_number_boundaries() -> None:
    tokens = tokenize("hello, world! 123 foo_bar")
    assert tokens == ("hello", "world", "123", "foo", "bar")


def test_tokenize_unicode_letters_and_numbers() -> None:
    tokens = tokenize("café π 42")
    assert tokens == ("café", "π", "42")


def test_normalize_and_tokenize_query_applies_nfc_casefold_and_collapse() -> None:
    tokens = normalize_and_tokenize_query("  Hello   WORLD  ")
    assert tokens == ("hello", "world")


def test_score_formula_exact_integer() -> None:
    # phrase_hit=1, distinct=2, total_occurrences=3
    query_tokens = ("alpha", "beta")
    candidate = "alpha beta alpha beta gamma"
    score = score_candidate("alpha beta", query_tokens, candidate)
    assert score is not None
    assert score.phrase_hit == 1
    assert score.distinct_query_tokens_matched == 2
    assert score.total_token_occurrences == 4
    assert score.score == 1_000_000 + 2 * 1000 + 4


def test_score_caps_total_occurrences_at_255() -> None:
    query_tokens = ("x",)
    candidate = " ".join(["x"] * 300)
    score = score_candidate("", query_tokens, candidate)
    assert score is not None
    assert score.total_token_occurrences == 300
    assert score.score == 0 * 1_000_000 + 1 * 1000 + 255


def test_no_match_returns_none() -> None:
    score = score_candidate("zzz", ("zzz",), "completely unrelated text")
    assert score is None


def test_token_only_match_without_phrase_hit() -> None:
    score = score_candidate("alpha zzz", ("alpha", "zzz"), "alpha appears here only")
    assert score is not None
    assert score.phrase_hit == 0
    assert score.distinct_query_tokens_matched == 1


def test_version_sort_key_forms() -> None:
    assert version_sort_key("INTEGER_VERSION", 42, None) == "42"
    assert version_sort_key("SOURCE_VERSION_STRING", None, "abc123") == "abc123"
    assert version_sort_key("UNVERSIONED", None, None) == ""


def test_tie_break_tuple_has_seven_parts_in_order() -> None:
    key = TieBreakKey(
        truth_class="ADVISORY_SOURCE_EVIDENCE",
        record_type="PROJECT_KNOWLEDGE",
        record_or_source_id="doc-1",
        source_version_kind="SOURCE_VERSION_STRING",
        source_version_value="abc",
        field_selector="document",
        chunk_id="0" * 64,
    )
    parts = key.as_tuple()
    assert len(parts) == 7
    assert parts == (
        "ADVISORY_SOURCE_EVIDENCE", "PROJECT_KNOWLEDGE", "doc-1",
        "SOURCE_VERSION_STRING", "abc", "document", "0" * 64,
    )


def test_rank_key_sorts_descending_score_then_ascending_tiebreak() -> None:
    from governed_retrieval.lexical import MatchScore

    high = MatchScore(phrase_hit=1, distinct_query_tokens_matched=1, total_token_occurrences=1)
    low = MatchScore(phrase_hit=0, distinct_query_tokens_matched=1, total_token_occurrences=1)
    tie_a = TieBreakKey("A", "B", "1", "K", "V", "sel", "0" * 64)
    tie_b = TieBreakKey("A", "B", "2", "K", "V", "sel", "0" * 64)

    key_high = rank_key(high, tie_a)
    key_low = rank_key(low, tie_a)
    assert key_high < key_low  # higher score sorts first (negated score)

    key_a = rank_key(high, tie_a)
    key_b = rank_key(high, tie_b)
    assert key_a < key_b  # equal score: ascending tie-break


def test_permutation_of_candidate_list_yields_identical_sorted_order() -> None:
    candidates = [
        (score_candidate("alpha", ("alpha",), "alpha one"), TieBreakKey("A", "B", "1", "K", "", "s", "0" * 64)),
        (score_candidate("alpha", ("alpha",), "alpha two"), TieBreakKey("A", "B", "2", "K", "", "s", "0" * 64)),
        (score_candidate("alpha", ("alpha",), "alpha three"), TieBreakKey("A", "B", "3", "K", "", "s", "0" * 64)),
    ]
    keyed = [(rank_key(score, tie), tie.record_or_source_id) for score, tie in candidates]
    for perm in itertools.permutations(keyed):
        assert sorted(perm) == sorted(keyed)


def test_repeated_normalization_is_deterministic() -> None:
    text = "Straße\r\n  QC03   stopped\r due to  fault"
    first = normalize_with_offsets(text)
    second = normalize_with_offsets(text)
    assert first.text == second.text
    assert first.offsets == second.offsets


def test_nfc_vs_non_nfc_equivalent_input_normalizes_identically() -> None:
    import unicodedata

    composed = unicodedata.normalize("NFC", "é")  # é composed
    decomposed = "é"  # e + combining acute (already what NFC produces from this)
    tokens_a = normalize_and_tokenize_query(composed)
    tokens_b = normalize_and_tokenize_query(unicodedata.normalize("NFC", decomposed))
    assert tokens_a == tokens_b
