"""Deterministic lexical normalization, tokenization, offset mapping, and
ranking (SPEC R6). Pure package module: standard library only.

No stemming, fuzzy match, transliteration, synonym, translation, embedding,
LLM, or locale-dependent collation. Evidence text is never rewritten for
matching; only a normalized *view* plus an explicit offset map back into the
unchanged, already-NFC P3-C text is produced.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

_MAX_TOTAL_OCCURRENCES = 255


def _is_letter_or_number(ch: str) -> bool:
    category = unicodedata.category(ch)
    return category[0] in ("L", "N")


@dataclass(frozen=True)
class NormalizedText:
    """A normalized matching view plus its offset map into the source text.

    ``text`` is the normalized string used for tokenization/matching.
    ``offsets[i]`` is the ``(start, end)`` interval in the *source* text
    (code-point indices) that produced ``text[i]``, for every index ``i`` in
    ``text``. A normalized substring ``[a, b)`` maps to source interval
    ``(min(offsets[a:b] starts), max(offsets[a:b] ends))``.
    """

    text: str
    offsets: tuple[tuple[int, int], ...]

    def source_span(self, start: int, end: int) -> tuple[int, int]:
        if start >= end:
            return (start, start)
        window = self.offsets[start:end]
        return (min(s for s, _ in window), max(e for _, e in window))


def normalize_with_offsets(source: str) -> NormalizedText:
    """R6 - normalize ``source`` (already Unicode NFC, e.g. P3-C evidence
    text) for matching, emitting an explicit offset map back into it.

    Algorithm (normative, SPEC R6 "Candidate normalization"):
    scan source code points left to right. CRLF emits one LF mapped to the
    consumed two-code-point interval; CR emits LF mapped to its interval;
    every code point emitted by one source code point's ``casefold`` maps to
    that source interval; each maximal whitespace run emits one ASCII space
    mapped to the union of its source intervals; trimmed edge whitespace
    emits nothing.
    """
    codepoints = list(source)
    n = len(codepoints)
    # Step 1: CRLF/CR -> LF, tracking each emitted LF's source interval.
    step1_chars: list[str] = []
    step1_spans: list[tuple[int, int]] = []
    i = 0
    while i < n:
        ch = codepoints[i]
        if ch == "\r" and i + 1 < n and codepoints[i + 1] == "\n":
            step1_chars.append("\n")
            step1_spans.append((i, i + 2))
            i += 2
            continue
        if ch == "\r":
            step1_chars.append("\n")
            step1_spans.append((i, i + 1))
            i += 1
            continue
        step1_chars.append(ch)
        step1_spans.append((i, i + 1))
        i += 1

    # Step 2: casefold each step1 character, expanding to 0+ output chars,
    # each mapped to that same source interval.
    step2_chars: list[str] = []
    step2_spans: list[tuple[int, int]] = []
    for ch, span in zip(step1_chars, step1_spans):
        folded = ch.casefold()
        for out_ch in folded:
            step2_chars.append(out_ch)
            step2_spans.append(span)

    # Step 3: collapse maximal whitespace runs to one ASCII space (union of
    # source intervals), drop leading/trailing whitespace entirely.
    result_chars: list[str] = []
    result_spans: list[tuple[int, int]] = []
    idx = 0
    total = len(step2_chars)
    while idx < total:
        ch = step2_chars[idx]
        if ch.isspace():
            run_start = idx
            run_end = idx
            while run_end < total and step2_chars[run_end].isspace():
                run_end += 1
            is_leading = run_start == 0
            is_trailing = run_end == total
            if not is_leading and not is_trailing:
                spans_in_run = step2_spans[run_start:run_end]
                union_start = min(s for s, _ in spans_in_run)
                union_end = max(e for _, e in spans_in_run)
                result_chars.append(" ")
                result_spans.append((union_start, union_end))
            idx = run_end
            continue
        result_chars.append(ch)
        result_spans.append(step2_spans[idx])
        idx += 1

    return NormalizedText(text="".join(result_chars), offsets=tuple(result_spans))


def tokenize(normalized_text: str) -> tuple[str, ...]:
    """Maximal contiguous runs whose Unicode category is Letter or Number."""
    tokens: list[str] = []
    current: list[str] = []
    for ch in normalized_text:
        if _is_letter_or_number(ch):
            current.append(ch)
        else:
            if current:
                tokens.append("".join(current))
                current = []
    if current:
        tokens.append("".join(current))
    return tuple(tokens)


def normalize_and_tokenize_query(query: str) -> tuple[str, ...]:
    """Normalize (NFC + casefold + whitespace collapse) and tokenize a query
    string. The query has already had CRLF/CR canonicalized and trimmed by
    request validation; NFC + casefold are applied here for token counting."""
    nfc = unicodedata.normalize("NFC", query)
    folded = nfc.casefold()
    collapsed: list[str] = []
    prev_space = False
    for ch in folded:
        if ch.isspace():
            if not prev_space:
                collapsed.append(" ")
            prev_space = True
        else:
            collapsed.append(ch)
            prev_space = False
    normalized = "".join(collapsed).strip(" ")
    return tokenize(normalized)


def normalize_query_for_matching(query: str) -> str:
    """The normalized matching form of an already request-validated query:
    NFC + casefold + whitespace collapse (no source offset map needed - the
    query itself is never cited)."""
    nfc = unicodedata.normalize("NFC", query)
    folded = nfc.casefold()
    collapsed: list[str] = []
    prev_space = False
    for ch in folded:
        if ch.isspace():
            if not prev_space:
                collapsed.append(" ")
            prev_space = True
        else:
            collapsed.append(ch)
            prev_space = False
    return "".join(collapsed).strip(" ")


@dataclass(frozen=True)
class MatchScore:
    phrase_hit: int
    distinct_query_tokens_matched: int
    total_token_occurrences: int

    @property
    def score(self) -> int:
        return (
            self.phrase_hit * 1_000_000
            + self.distinct_query_tokens_matched * 1_000
            + min(self.total_token_occurrences, _MAX_TOTAL_OCCURRENCES)
        )


def score_candidate(
    normalized_query: str, query_tokens: tuple[str, ...], candidate_normalized: str
) -> MatchScore | None:
    """R6 - compute the match score for one candidate's normalized text.

    Returns ``None`` if the candidate does not match (neither a phrase hit
    nor any distinct query token present).
    """
    q_set = frozenset(query_tokens)
    phrase_hit = 1 if normalized_query and normalized_query in candidate_normalized else 0
    candidate_tokens = tokenize(candidate_normalized)
    distinct_matched = len({t for t in candidate_tokens if t in q_set})
    total_occurrences = sum(1 for t in candidate_tokens if t in q_set)
    if phrase_hit == 0 and distinct_matched == 0:
        return None
    return MatchScore(
        phrase_hit=phrase_hit,
        distinct_query_tokens_matched=distinct_matched,
        total_token_occurrences=total_occurrences,
    )


def version_sort_key(kind: str, integer_version: int | None, source_version_string: str | None) -> str:
    """R6 tie-break "source_version_value": decimal ASCII for an integer
    version, the exact safe string for a source-string version, empty string
    for unversioned."""
    if kind == "INTEGER_VERSION":
        return str(integer_version)
    if kind == "SOURCE_VERSION_STRING":
        return source_version_string or ""
    return ""


@dataclass(frozen=True)
class TieBreakKey:
    """R6 - the exact seven-part ascending tie-break tuple."""

    truth_class: str
    record_type: str
    record_or_source_id: str
    source_version_kind: str
    source_version_value: str
    field_selector: str
    chunk_id: str

    def as_tuple(self) -> tuple[str, str, str, str, str, str, str]:
        return (
            self.truth_class,
            self.record_type,
            self.record_or_source_id,
            self.source_version_kind,
            self.source_version_value,
            self.field_selector,
            self.chunk_id,
        )


def rank_key(score: MatchScore, tie_break: TieBreakKey):
    """Sort key for descending score then ascending tie-break tuple."""
    return (-score.score, tie_break.as_tuple())


def best_match_span(
    normalized: NormalizedText, normalized_query: str, query_tokens: tuple[str, ...]
) -> tuple[int, int] | None:
    """R8 - the best lexical span in *normalized* coordinates: prefer a full
    phrase span over a token span, then the lowest starting offset. Returns
    ``None`` if there is no match span (the candidate did not actually
    match)."""
    text = normalized.text
    if normalized_query:
        idx = text.find(normalized_query)
        if idx != -1:
            return (idx, idx + len(normalized_query))
    q_set = frozenset(query_tokens)
    best: tuple[int, int] | None = None
    pos = 0
    current: list[str] = []
    start = 0
    n = len(text)
    i = 0
    while i <= n:
        ch = text[i] if i < n else None
        if ch is not None and _is_letter_or_number(ch):
            if not current:
                start = i
            current.append(ch)
        else:
            if current:
                token = "".join(current)
                if token in q_set:
                    span = (start, start + len(token))
                    if best is None or span[0] < best[0]:
                        best = span
                current = []
        i += 1
    return best
