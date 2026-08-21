"""Deterministic, versioned prompt-injection / control-text detection
(SPEC R9).

Retrieved evidence text is untrusted data, never instructions. This detector
runs over each admitted evidence projection's snippet BEFORE minimization and
context assembly. Contaminated projections are omitted with safe reason
codes; if every projection is omitted the caller must fail closed as
``INJECTION_BLOCKED`` with zero gateway attempts. Detection is pure regex/
codepoint scanning - no model, no network, no randomness - so results are
exactly reproducible.
"""

from __future__ import annotations

import re
import unicodedata
from enum import StrEnum

from pydantic import Field, model_validator
from retrieval_contracts.common import Digest, StrictModel

DETECTOR_VERSION = "1.0"


class InjectionReasonCode(StrEnum):
    """SPEC R9 - closed set of safe injection-detection reason codes."""

    CONTROL_CHARACTER = "CONTROL_CHARACTER"
    ROLE_MARKER = "ROLE_MARKER"
    DELIMITER_ESCAPE = "DELIMITER_ESCAPE"
    TOOL_INSTRUCTION = "TOOL_INSTRUCTION"
    SECRET_EXFILTRATION = "SECRET_EXFILTRATION"
    PROMPT_OVERRIDE = "PROMPT_OVERRIDE"


class InjectionOmissionV1(StrictModel):
    """SPEC R9 - one omitted, contaminated projection's safe record."""

    citation_id: Digest
    reason_codes: tuple[InjectionReasonCode, ...] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def _reasons_duplicate_free(self) -> "InjectionOmissionV1":
        if tuple(sorted(set(self.reason_codes))) != tuple(sorted(self.reason_codes)):
            raise ValueError("reason_codes must be duplicate-free")
        return self

# Control characters other than the ordinary whitespace already tolerated
# elsewhere (tab/newline/carriage-return are still flagged - evidence text
# should never carry raw control bytes at all).
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_ROLE_MARKER_RE = re.compile(
    r"(?im)^\s*(system|assistant|user|developer)\s*:\s*|"
    r"<\|?\s*(system|assistant|user|developer)\s*\|?>"
)

_DELIMITER_ESCAPE_RE = re.compile(
    r"```|<\s*/?\s*(instructions?|system|prompt)\s*>|\[\[.*?\]\]|\{\{.*?\}\}"
)

_TOOL_INSTRUCTION_RE = re.compile(
    r"(?i)\b(ignore (all|the)? ?(previous|prior|above) (instructions|prompt|rules)\b"
    r"|disregard (all|the)? ?(previous|prior|above)\b"
    r"|you (are|must) now\b"
    r"|new instructions?:\s*"
    r"|call (the )?tool\b|invoke (the )?function\b|execute (the )?command\b)"
)

_SECRET_EXFILTRATION_RE = re.compile(
    r"(?i)\b(reveal|print|output|leak|exfiltrate|send)\b.{0,32}\b(api key|secret|password|token|credential|"
    r"system prompt|environment variable)\b"
)

_PROMPT_OVERRIDE_RE = re.compile(
    r"(?i)\bact as\b|\bpretend (you are|to be)\b|\bjailbreak\b|\bDAN mode\b|\boverride (your )?(instructions|rules)\b"
)

_DETECTORS: tuple[tuple[InjectionReasonCode, re.Pattern[str]], ...] = (
    (InjectionReasonCode.CONTROL_CHARACTER, _CONTROL_CHAR_RE),
    (InjectionReasonCode.ROLE_MARKER, _ROLE_MARKER_RE),
    (InjectionReasonCode.DELIMITER_ESCAPE, _DELIMITER_ESCAPE_RE),
    (InjectionReasonCode.TOOL_INSTRUCTION, _TOOL_INSTRUCTION_RE),
    (InjectionReasonCode.SECRET_EXFILTRATION, _SECRET_EXFILTRATION_RE),
    (InjectionReasonCode.PROMPT_OVERRIDE, _PROMPT_OVERRIDE_RE),
)


def detect_reason_codes(text: str) -> tuple[InjectionReasonCode, ...]:
    """Return every matched, closed reason code for ``text``, in the fixed
    detector-declaration order, duplicate-free. Empty when clean."""
    normalized = unicodedata.normalize("NFC", text)
    found: list[InjectionReasonCode] = []
    for reason, pattern in _DETECTORS:
        if pattern.search(normalized):
            found.append(reason)
    return tuple(found)


def screen(
    citation_texts: tuple[tuple[str, str], ...]
) -> tuple[tuple[str, ...], tuple[InjectionOmissionV1, ...]]:
    """SPEC R9 - screen ``((citation_id, text), ...)`` pairs.

    Returns ``(clean_citation_ids, omissions)`` where ``clean_citation_ids``
    preserves input order and ``omissions`` records the safe reason codes for
    every contaminated citation, also in input order. Never mutates or
    returns the evidence text itself.
    """
    clean: list[str] = []
    omissions: list[InjectionOmissionV1] = []
    for citation_id, text in citation_texts:
        reasons = detect_reason_codes(text)
        if reasons:
            omissions.append(InjectionOmissionV1(citation_id=citation_id, reason_codes=reasons))
        else:
            clean.append(citation_id)
    return tuple(clean), tuple(omissions)
