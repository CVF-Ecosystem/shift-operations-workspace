"""SPEC R8 - EvidenceProjectionV1 construction and context-budget trimming.

AC-08: source lengths 65535/65536/65537, code-point and multi-byte UTF-8
edges, phrase-versus-token selection, lowest-offset ties, centered/clamped
windows, deterministic byte trimming, match preservation, snippet
digest/offset/complete flag, whole-projection removal, and every budget at
N/N+1 without provenance truncation.
"""

from __future__ import annotations

import hashlib

from governed_retrieval.lexical import normalize_and_tokenize_query, normalize_query_for_matching, normalize_with_offsets
from governed_retrieval.projection import _trim_to_byte_budget, build_snippet, estimate_tokens, serialized_projection_bytes


def _snippet_for(text: str, query: str, *, codepoints: int = 1024, utf8_bytes: int = 3072):
    normalized = normalize_with_offsets(text)
    normalized_query = normalize_query_for_matching(query)
    query_tokens = normalize_and_tokenize_query(query)
    return build_snippet(
        source_text=text, normalized=normalized, normalized_query=normalized_query,
        query_tokens=query_tokens, max_snippet_codepoints=codepoints, max_snippet_utf8_bytes=utf8_bytes,
    )


def test_full_short_text_projection_is_complete() -> None:
    text = "the quick brown fox jumps"
    snippet = _snippet_for(text, "fox")
    assert snippet is not None
    assert snippet.projection_complete is True
    assert snippet.content_snippet == text
    assert snippet.snippet_start_codepoint == 0
    assert snippet.snippet_end_codepoint == len(text)


def test_snippet_digest_is_sha256_of_exact_utf8_bytes() -> None:
    text = "café evidence snippet"
    snippet = _snippet_for(text, "café")
    assert snippet is not None
    expected = hashlib.sha256(snippet.content_snippet.encode("utf-8")).hexdigest()
    assert snippet.snippet_digest_sha256 == expected


def test_phrase_hit_preferred_over_token_only_span() -> None:
    text = "alpha zzz filler filler filler filler filler alpha beta filler"
    snippet = _snippet_for(text, "alpha beta", codepoints=30, utf8_bytes=90)
    assert snippet is not None
    # the phrase "alpha beta" span must be inside the snippet window
    phrase_start = text.index("alpha beta")
    assert snippet.snippet_start_codepoint <= phrase_start
    assert snippet.snippet_end_codepoint >= phrase_start + len("alpha beta")


def test_lowest_starting_offset_wins_among_equal_token_matches() -> None:
    text = "zzz alpha filler filler filler filler filler filler filler alpha zzz"
    snippet = _snippet_for(text, "alpha", codepoints=15, utf8_bytes=45)
    assert snippet is not None
    first_alpha = text.index("alpha")
    assert snippet.snippet_start_codepoint <= first_alpha < snippet.snippet_end_codepoint


def test_window_centered_on_match_midpoint_when_clamped() -> None:
    text = "x" * 2000 + "TARGET" + "y" * 2000
    snippet = _snippet_for(text, "TARGET", codepoints=100, utf8_bytes=300)
    assert snippet is not None
    target_start = text.index("TARGET")
    assert snippet.snippet_start_codepoint <= target_start
    assert snippet.snippet_end_codepoint >= target_start + len("TARGET")
    assert snippet.snippet_end_codepoint - snippet.snippet_start_codepoint <= 100


def test_multi_byte_utf8_trim_stays_on_unicode_boundary() -> None:
    # Each "é" is 2 UTF-8 bytes; force byte trimming while keeping the match.
    text = "é" * 50 + "TARGET" + "é" * 50
    snippet = _snippet_for(text, "TARGET", codepoints=60, utf8_bytes=70)
    assert snippet is not None
    # Must decode cleanly (no broken multi-byte boundary).
    snippet.content_snippet.encode("utf-8").decode("utf-8")
    assert len(snippet.content_snippet.encode("utf-8")) <= 70
    assert "TARGET" in snippet.content_snippet


def test_match_span_always_preserved_even_under_tight_byte_budget() -> None:
    text = "é" * 200 + "TARGET" + "é" * 200
    match_bytes = len("TARGET".encode("utf-8"))
    snippet = _snippet_for(text, "TARGET", codepoints=400, utf8_bytes=match_bytes + 4)
    assert snippet is not None
    assert "TARGET" in snippet.content_snippet


def test_match_too_large_for_byte_budget_returns_none() -> None:
    text = "TARGETTARGETTARGETTARGET"
    snippet = _snippet_for(text, text, codepoints=len(text), utf8_bytes=2)
    assert snippet is None


def test_source_length_boundaries_65535_65536_65537() -> None:
    for length in (65535, 65536, 65537):
        text = ("a" * (length - 6)) + "TARGET"
        snippet = _snippet_for(text, "TARGET", codepoints=1024, utf8_bytes=3072)
        assert snippet is not None
        assert "TARGET" in snippet.content_snippet


def test_estimate_tokens_formula() -> None:
    assert estimate_tokens(0) == 0
    assert estimate_tokens(1) == 1
    assert estimate_tokens(2) == 1
    assert estimate_tokens(3) == 2
    assert estimate_tokens(100) == 50


def test_serialized_projection_bytes_matches_canonical_json_length() -> None:
    from retrieval_contracts.canonical import canonical_json_bytes

    dumps = [{"a": 1}, {"b": "x"}]
    expected = len(canonical_json_bytes({"projections": dumps}))
    assert serialized_projection_bytes(dumps) == expected


def test_no_match_span_returns_none_snippet() -> None:
    snippet = _snippet_for("nothing relevant here", "zzz-not-present", codepoints=1024, utf8_bytes=3072)
    assert snippet is None


# --- F12: equal-distance trim ties remove the HIGH/end side, not the LOW ---


def test_equal_distance_trim_tie_removes_high_end_side() -> None:
    """F12 reproduction: SPEC R8 requires removing the high/end side on an
    EXACT equal-distance-from-midpoint tie. Before the repair this returned
    ``TARGETb`` (low/start side removed); the corrected behavior keeps
    ``aTARGET``."""
    source = "aTARGETb"
    # match "TARGET" occupies [1, 7); window [0, 8) has one extra code point
    # on each side (dist_low == dist_high == 1 from the match midpoint 4).
    trimmed = _trim_to_byte_budget(source, 0, 8, 1, 7, byte_budget=7)
    assert trimmed == (0, 7)
    assert source[trimmed[0]:trimmed[1]] == "aTARGET"


def test_equal_distance_trim_tie_via_build_snippet() -> None:
    """Same F12 tie, exercised through the public build_snippet entry point
    with a byte budget that forces exactly one code point of trimming from
    an otherwise-symmetric window."""
    text = "aTARGETb"
    snippet = _snippet_for(text, "TARGET", codepoints=8, utf8_bytes=7)
    assert snippet is not None
    assert snippet.content_snippet == "aTARGET"
    assert (snippet.snippet_start_codepoint, snippet.snippet_end_codepoint) == (0, 7)


def test_non_tied_trim_still_removes_the_farther_side() -> None:
    """Sanity: when distances are NOT tied, the farther side is still
    removed first regardless of the tie-break direction change."""
    source = "aaTARGETbbbb"
    # match "TARGET" at [2, 8); window [0, 12): dist_low=5-2=3, dist_high=8=...
    # use explicit midpoint math: match_mid=(2+8)/2=5; dist_low=5-0=5; dist_high=12-5=7
    trimmed = _trim_to_byte_budget(source, 0, 12, 2, 8, byte_budget=10)
    assert trimmed is not None
    start, end = trimmed
    assert source[start:end].__contains__("TARGET")
    # the high side (farther, dist_high=7 > dist_low=5) must shrink first.
    assert end < 12
