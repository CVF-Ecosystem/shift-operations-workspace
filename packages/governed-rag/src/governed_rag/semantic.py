"""``PROJECT_CONCEPT_FEATURE_VECTOR_V1`` - the local, deterministic,
dependency-free semantic substrate (SPEC R6/R7).

This is deliberately NOT a general-purpose embedding claim. It produces a
sparse binary feature vector from three feature families:

1. normalized word tokens (lowercased, ASCII-folded where practical);
2. bounded character trigrams over the normalized token stream (bridges
   small spelling/inflection variance without any external model);
3. canonical project-domain *concepts* resolved through a small, versioned,
   reviewed synonym lexicon - the piece that lets a synonym pair with zero
   exact-token overlap still collide on a shared concept feature.

The encoder id/version and the lexicon each have a canonical SHA-256 digest
(``ENCODER_ID``/``ENCODER_VERSION``/``lexicon_digest()``) so the ephemeral
index can bind and later detect drift (SPEC R8). Everything here is pure
stdlib string processing: no network, no external model, no randomness.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Mapping

from .hashing import lexicon_digest

ENCODER_ID = "PROJECT_CONCEPT_FEATURE_VECTOR_V1"
ENCODER_VERSION = "1.0"
LEXICON_VERSION = "1.0"

_TOKEN_RE = re.compile(r"[0-9a-z]+")
_TRIGRAM_MIN_TOKEN_LEN = 3
_MAX_FEATURES_PER_DOCUMENT = 512

# SPEC R6 - a small, reviewed, versioned mapping of project-operations
# synonyms to one canonical concept id each. Every term maps to exactly one
# concept; concept ids are their own feature family, distinct from raw
# token/trigram features, so a synonym pair with zero exact-token overlap
# still shares a concept feature. Bounded and hand-reviewed, not learned.
PROJECT_CONCEPT_LEXICON: Mapping[str, tuple[str, ...]] = {
    "CONCEPT_HANDOVER": ("handover", "handoff", "shift change", "turnover", "changeover"),
    "CONCEPT_INCIDENT": ("incident", "outage", "disruption", "fault", "breakdown"),
    "CONCEPT_ESCALATION": ("escalation", "escalate", "priority bump", "raise urgency"),
    "CONCEPT_MAINTENANCE": ("maintenance", "upkeep", "servicing", "preventive check"),
    "CONCEPT_SAFETY": ("safety", "hazard", "risk control", "protective measure"),
    "CONCEPT_CUSTOMER_REQUEST": ("customer request", "client request", "service request", "ticket"),
    "CONCEPT_ASSIGNMENT": ("assignment", "roster", "staffing", "shift coverage"),
    "CONCEPT_REPORT": ("report", "summary record", "shift report", "log entry"),
    "CONCEPT_APPROVAL": ("approval", "sign-off", "authorization", "clearance"),
    "CONCEPT_QUALITY": ("quality", "compliance", "standard adherence", "audit finding"),
}


def _canonical_lexicon_terms() -> dict[str, tuple[str, ...]]:
    """Frozen, sorted-within-concept copy used consistently for digesting and
    matching, independent of the source dict's own iteration order."""
    return {concept: tuple(sorted(terms)) for concept, terms in sorted(PROJECT_CONCEPT_LEXICON.items())}


_CANONICAL_LEXICON = _canonical_lexicon_terms()
LEXICON_DIGEST_SHA256 = lexicon_digest(_CANONICAL_LEXICON)

# term -> concept id, built once, for exact multi-word/single-word phrase
# lookup against normalized token windows.
_TERM_TO_CONCEPT: dict[str, str] = {
    term: concept for concept, terms in _CANONICAL_LEXICON.items() for term in terms
}
_MAX_TERM_WORDS = max((len(term.split()) for term in _TERM_TO_CONCEPT), default=1)


def normalize_text(text: str) -> str:
    """NFC-normalize, casefold, and collapse to ASCII letters/digits/spaces
    for deterministic, locale-independent matching."""
    folded = unicodedata.normalize("NFC", text).casefold()
    ascii_only = unicodedata.normalize("NFKD", folded).encode("ascii", "ignore").decode("ascii")
    return ascii_only


def tokenize(text: str) -> tuple[str, ...]:
    """Bounded, deterministic word tokenization over normalized text."""
    return tuple(_TOKEN_RE.findall(normalize_text(text)))


def _char_trigrams(token: str) -> tuple[str, ...]:
    if len(token) < _TRIGRAM_MIN_TOKEN_LEN:
        return ()
    return tuple(f"TRI_{token[i : i + 3]}" for i in range(len(token) - 2))


def _concept_features(tokens: tuple[str, ...]) -> tuple[str, ...]:
    """Slide a bounded window over the token stream, matching the longest
    lexicon phrase first at each position, deterministically."""
    concepts: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for width in range(min(_MAX_TERM_WORDS, n - i), 0, -1):
            phrase = " ".join(tokens[i : i + width])
            concept = _TERM_TO_CONCEPT.get(phrase)
            if concept is not None:
                concepts.append(concept)
                i += width
                matched = True
                break
        if not matched:
            i += 1
    return tuple(concepts)


def feature_ids(text: str) -> tuple[str, ...]:
    """Deterministic sparse binary feature-id set for one text (SPEC R6/R7).

    Feature families are namespaced (``TOK_``/``TRI_``/``CONCEPT_``) so they
    never collide with each other. Duplicate features collapse (binary
    presence, not frequency) and the result is sorted for determinism. Bounded
    to ``_MAX_FEATURES_PER_DOCUMENT`` distinct features to keep the substrate
    dependency-free and cheap; excess features are dropped in sorted order
    (a documented, deterministic ceiling, never a silent truncation of the
    match itself).
    """
    tokens = tokenize(text)
    features: set[str] = set()
    for token in tokens:
        features.add(f"TOK_{token}")
        features.update(_char_trigrams(token))
    features.update(_concept_features(tokens))
    ordered = tuple(sorted(features))
    return ordered[:_MAX_FEATURES_PER_DOCUMENT]


def semantic_score(query_features: tuple[str, ...], document_features: tuple[str, ...]) -> int:
    """SPEC R7 - integer semantic component score in ``[0, 1_000_000]``.

    Jaccard-style overlap over the two feature-id sets, scaled to the fixed
    integer range using integer arithmetic only (no floats anywhere in the
    scoring path).
    """
    query_set = set(query_features)
    document_set = set(document_features)
    if not query_set or not document_set:
        return 0
    intersection = len(query_set & document_set)
    union = len(query_set | document_set)
    if union == 0:
        return 0
    return (intersection * 1_000_000) // union
