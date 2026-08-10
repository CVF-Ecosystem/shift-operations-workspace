"""EvidenceProjectionV1 construction and context-budget trimming (SPEC R8).
Pure package module: standard library, Pydantic, and ``retrieval_contracts``
only. No I/O, clock, or id creation - every timestamp/digest is supplied by
the caller through already-admitted ``RetrievalReadyV1`` values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from retrieval_contracts.canonical import canonical_json_bytes, sha256_bytes

from .lexical import NormalizedText, best_match_span

# R8 server maxima (must stay identical to request_models.py's copies; a
# contract test cross-checks this).
MAX_PROJECTION_RECORDS = 4
MAX_SNIPPET_CODEPOINTS = 1024
MAX_SNIPPET_UTF8_BYTES = 3072
MAX_SERIALIZED_UTF8_BYTES = 16384
MAX_ESTIMATED_INPUT_TOKENS = 4096


class ContextBudgetExceeded(Exception):
    """Raised when no complete identity plus non-empty snippet can fit."""


@dataclass(frozen=True)
class SnippetResult:
    content_snippet: str
    snippet_start_codepoint: int
    snippet_end_codepoint: int
    snippet_digest_sha256: str
    projection_complete: bool


def _utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))


def _trim_to_byte_budget(
    source_text: str,
    window_start: int,
    window_end: int,
    match_start: int,
    match_end: int,
    byte_budget: int,
) -> tuple[int, int] | None:
    """Remove one code point at a time from the side farther from the match
    midpoint (equal distance removes from the high/end side) until the
    window's UTF-8 byte length fits ``byte_budget``. The match span must
    remain present throughout. Returns ``None`` if the match itself cannot
    fit."""
    match_mid = (match_start + match_end) / 2
    start, end = window_start, window_end
    window_text = source_text[start:end]
    if _utf8_len(window_text) <= byte_budget:
        return (start, end)
    if _utf8_len(source_text[match_start:match_end]) > byte_budget:
        return None
    while start < match_start or end > match_end:
        window_text = source_text[start:end]
        if _utf8_len(window_text) <= byte_budget:
            return (start, end)
        dist_low = match_mid - start
        dist_high = end - match_mid
        can_shrink_low = start < match_start
        can_shrink_high = end > match_end
        # SPEC R8: remove one code point from the side farther from the
        # match midpoint; on an EXACT tie, remove from the high/end side
        # (not the low/start side) - hence strict ``dist_high >= dist_low``
        # here, not ``dist_low >= dist_high``.
        if can_shrink_high and (not can_shrink_low or dist_high >= dist_low):
            end -= 1
        elif can_shrink_low:
            start += 1
        else:
            break
    window_text = source_text[start:end]
    if _utf8_len(window_text) <= byte_budget:
        return (start, end)
    return None


def build_snippet(
    *,
    source_text: str,
    normalized: NormalizedText,
    normalized_query: str,
    query_tokens: tuple[str, ...],
    max_snippet_codepoints: int,
    max_snippet_utf8_bytes: int,
) -> SnippetResult | None:
    """R8 - construct the best-effort snippet for one candidate.

    Returns ``None`` if the match span cannot be located (should not happen
    for an already-matched candidate) or cannot fit either ceiling - the
    caller then omits this candidate's whole projection.
    """
    span = best_match_span(normalized, normalized_query, query_tokens)
    if span is None:
        return None
    match_start_src, match_end_src = normalized.source_span(span[0], span[1])

    source_len = len(source_text)
    midpoint = (match_start_src + match_end_src) // 2
    half = max_snippet_codepoints // 2
    window_start = max(0, midpoint - half)
    window_end = min(source_len, window_start + max_snippet_codepoints)
    window_start = max(0, window_end - max_snippet_codepoints)

    # Ensure the match span is fully contained in the initial window; expand
    # minimally toward the match if the centered window clipped it (still
    # bounded by max_snippet_codepoints from the caller's contract - if the
    # match itself exceeds the code-point budget, byte trimming below will
    # detect the failure).
    window_start = min(window_start, match_start_src)
    window_end = max(window_end, match_end_src)
    if window_end - window_start > max_snippet_codepoints:
        # Re-center strictly on the match if it alone still fits.
        if match_end_src - match_start_src <= max_snippet_codepoints:
            window_start = max(0, midpoint - half)
            window_end = min(source_len, window_start + max_snippet_codepoints)
            window_start = max(0, window_end - max_snippet_codepoints)
            window_start = min(window_start, match_start_src)
            window_end = max(window_end, match_end_src)

    trimmed = _trim_to_byte_budget(
        source_text, window_start, window_end, match_start_src, match_end_src, max_snippet_utf8_bytes
    )
    if trimmed is None:
        return None
    start, end = trimmed
    if end - start > max_snippet_codepoints:
        return None
    snippet_text = source_text[start:end]
    if not snippet_text:
        return None
    digest = sha256_bytes(snippet_text.encode("utf-8"))
    complete = (start == 0 and end == source_len)
    return SnippetResult(
        content_snippet=snippet_text,
        snippet_start_codepoint=start,
        snippet_end_codepoint=end,
        snippet_digest_sha256=digest,
        projection_complete=complete,
    )


def estimate_tokens(serialized_utf8_bytes: int) -> int:
    """``(serialized_utf8_bytes + 1) // 2`` per the receipt appendix."""
    return (serialized_utf8_bytes + 1) // 2


def serialized_projection_bytes(projection_dumps: list[dict[str, Any]]) -> int:
    return len(canonical_json_bytes({"projections": projection_dumps}))
