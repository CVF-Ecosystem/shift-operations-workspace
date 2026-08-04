from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from .canonical import candidate_fingerprint
from .controls import ControlBundleV1
from .enums import (
    Disposition,
    FallbackReason,
    QuarantineReason,
    SENSITIVITY_ORDER,
    Sensitivity,
    Stage,
    StageOutcome,
    StageReason,
)
from .input_models import validate_safe_string

T = TypeVar("T")


class StageUnavailableError(Exception):
    """Typed local signal for a deterministic stage that cannot execute."""


def quarantine_reason(reason: StageReason) -> QuarantineReason:
    mapping = {
        StageReason.AMBIGUOUS_LOCAL_TIME: QuarantineReason.AMBIGUOUS_VALUE,
        StageReason.AMBIGUOUS_ACTION_STATE: QuarantineReason.AMBIGUOUS_VALUE,
        StageReason.INSUFFICIENT_CONTEXT: QuarantineReason.DEDUPE_CONTEXT_INVALID,
        StageReason.PROVENANCE_MISMATCH: QuarantineReason.PROVENANCE_MISMATCH,
        StageReason.UNSUPPORTED_TRANSFORM: QuarantineReason.UNSUPPORTED_TRANSFORM,
        StageReason.POLICY_DRIFT: QuarantineReason.POLICY_DRIFT,
        StageReason.REDACTION_FAILED: QuarantineReason.REDACTION_FAILED,
        StageReason.REDACTION_RESIDUE: QuarantineReason.REDACTION_RESIDUE,
        StageReason.CONFLICT_DETECTED: QuarantineReason.CONFLICT_DETECTED,
        StageReason.DEDUPE_CONTEXT_INVALID: QuarantineReason.DEDUPE_CONTEXT_INVALID,
        StageReason.DIGEST_COLLISION_SUSPECTED: QuarantineReason.DIGEST_COLLISION_SUSPECTED,
        StageReason.QUALITY_INCOMPLETE: QuarantineReason.QUALITY_INCOMPLETE,
        StageReason.STAGE_INVARIANT_ERROR: QuarantineReason.STAGE_INVARIANT_ERROR,
    }
    return mapping[reason]


def execute_stage(
    operation: Callable[[], T],
    known: tuple[tuple[type[Exception], StageReason], ...] = (),
) -> tuple[T | None, StageReason | None]:
    try:
        return operation(), None
    except Exception as exc:
        if isinstance(exc, StageUnavailableError):
            return None, StageReason.STAGE_UNAVAILABLE
        for error_type, reason in known:
            if isinstance(exc, error_type):
                return None, reason
        return None, StageReason.STAGE_INVARIANT_ERROR


def dedupe_preimage(
    text: str, sensitivity: Any, topics: tuple[str, ...], controls: ControlBundleV1
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "redacted_normalized_text": text,
        "sensitivity": sensitivity.value,
        "topic_labels": list(topics),
        "normalization_rules_version": controls.normalization_rules_version,
        "terminology_rules_version": controls.terminology_rules_version,
        "classification_rules_version": controls.classification_rules_version,
        "redaction_rules_version": controls.redaction_rules_version,
    }


def result_quality_is_bound(result: Any) -> bool:
    passed = {
        receipt.stage
        for receipt in result.stage_receipts
        if receipt.outcome == StageOutcome.PASS
    }
    conflict_ok = Stage.CONFLICT in passed
    expected = (
        25 if Stage.ENVELOPE in passed else 0,
        25 if {Stage.NORMALIZATION, Stage.TERMINOLOGY}.issubset(passed) and conflict_ok else 0,
        25 if {Stage.CLASSIFICATION, Stage.CONFLICT, Stage.REDACTION}.issubset(passed) else 0,
        25 if Stage.DEDUPE in passed and conflict_ok else 0,
    )
    quality = result.quality_receipt
    actual = (quality.provenance, quality.normalization, quality.protection, quality.integrity)
    return (
        actual == expected
        and quality.total == sum(expected)
        and quality.rules_version == result.stage_receipts[7].control_version
    )


def candidate_is_bound(result: Any) -> bool:
    candidate = result.context_candidate
    fingerprint = result.candidate_fingerprint
    return bool(
        candidate is not None
        and fingerprint is not None
        and candidate.source_owner_id == result.source_owner_id
        and candidate.source_link == result.source_link
        and candidate.source_fingerprint == result.source_fingerprint
        and candidate.normalization_rules_version == result.stage_receipts[1].control_version
        and candidate.terminology_rules_version == result.stage_receipts[2].control_version
        and candidate.classification_rules_version == result.stage_receipts[3].control_version
        and candidate.redaction_rules_version == result.stage_receipts[5].control_version
        and candidate.quality_rules_version == result.quality_receipt.rules_version
        and candidate.quality_score == result.quality_receipt.total
        and candidate.provenance == result.quality_receipt.provenance
        and candidate.normalization == result.quality_receipt.normalization
        and candidate.protection == result.quality_receipt.protection
        and candidate.integrity == result.quality_receipt.integrity
        and fingerprint == candidate_fingerprint(candidate.fingerprint_preimage())
    )


def failure_is_bound(result: Any, failed: Any) -> bool:
    reason = failed.reason_codes[0]
    if result.disposition == Disposition.NO_CANDIDATE_DUPLICATE:
        receipt = result.duplicate_receipt
        return bool(
            failed.stage == Stage.DEDUPE
            and reason == StageReason.EXACT_SOURCE_MATCH
            and receipt is not None
            and receipt.match_ids == failed.safe_ids
        )
    if result.disposition == Disposition.NO_CANDIDATE_FALLBACK:
        expected = {
            StageReason.STAGE_UNAVAILABLE: FallbackReason.STAGE_UNAVAILABLE,
            StageReason.STAGE_INVARIANT_ERROR: FallbackReason.STAGE_INVARIANT_ERROR,
        }.get(reason, FallbackReason.QUARANTINE_ROUTE_UNAVAILABLE)
        return result.fallback_receipt is not None and result.fallback_receipt.reason == expected
    reason_map = {
        StageReason.AMBIGUOUS_LOCAL_TIME: QuarantineReason.AMBIGUOUS_VALUE,
        StageReason.AMBIGUOUS_ACTION_STATE: QuarantineReason.AMBIGUOUS_VALUE,
        StageReason.INSUFFICIENT_CONTEXT: QuarantineReason.DEDUPE_CONTEXT_INVALID,
    }
    expected = reason_map.get(reason)
    if expected is None:
        try:
            expected = QuarantineReason(reason.value)
        except ValueError:
            return False
    receipt = result.quarantine_receipt
    return bool(
        receipt is not None
        and receipt.route.sink_available is True
        and receipt.reason == expected
        and receipt.source_owner_id == result.source_owner_id
        and receipt.source_link == result.source_link
        and receipt.source_fingerprint == result.source_fingerprint
    )

AMBIGUOUS_TIME = re.compile(r"(?<![\w:])(?:[01]?\d|2[0-3])h[0-5]\d(?![\w:])", re.IGNORECASE)
AMBIGUOUS_ACTION = re.compile(r"\b(?:đang xuống|dang xuong)\b", re.IGNORECASE)
SENSITIVE_RESIDUE = re.compile(
    r"\b(?:password|api[_-]?key|secret|credential)\s*[:=]\s*\S+", re.IGNORECASE
)


@dataclass(frozen=True)
class TerminologyResult:
    text: str
    rule_ids: tuple[str, ...]
    offsets: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class RedactionResult:
    text: str
    rule_ids: tuple[str, ...]
    offsets: tuple[tuple[int, int], ...]


def apply_terminology(text: str, controls: ControlBundleV1) -> TerminologyResult:
    matches: list[tuple[int, int, str, str]] = []
    for source, target in controls.terminology_map.items():
        pattern = re.compile(rf"(?<!\w){re.escape(source)}(?!\w)", re.IGNORECASE)
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), source.casefold(), target))
    matches.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
    if any(left[1] > right[0] for left, right in zip(matches, matches[1:])):
        raise ValueError("overlapping terminology matches")
    output = text
    for start, end, _, replacement in reversed(matches):
        output = output[:start] + replacement + output[end:]
    ids = tuple(sorted({item[2] for item in matches}))
    offsets = tuple((item[0], item[1]) for item in matches)
    return TerminologyResult(output, ids, offsets)


def classify(
    text: str, declared: Sensitivity, controls: ControlBundleV1
) -> tuple[Sensitivity, tuple[str, ...]]:
    folded = text.casefold()
    detected = declared
    for sensitivity, terms in controls.sensitivity_terms.items():
        if any(term.casefold() in folded for term in terms):
            if SENSITIVITY_ORDER[sensitivity] > SENSITIVITY_ORDER[detected]:
                detected = sensitivity
    topics = tuple(
        sorted(
            topic
            for topic, terms in controls.topic_terms.items()
            if any(term.casefold() in folded for term in terms)
        )
    )
    return detected, topics


def classification_is_valid(
    declared: Sensitivity, detected: object, topics: object
) -> bool:
    if not isinstance(detected, Sensitivity) or not isinstance(topics, tuple):
        return False
    if SENSITIVITY_ORDER[detected] < SENSITIVITY_ORDER[declared]:
        return False
    if tuple(sorted(topics)) != topics or len(set(topics)) != len(topics):
        return False
    try:
        return len(topics) <= 64 and all(
            isinstance(topic, str) and validate_safe_string(topic) == topic
            for topic in topics
        )
    except ValueError:
        return False


def conflict_reason(text: str, controls: ControlBundleV1) -> StageReason | None:
    if AMBIGUOUS_TIME.search(text):
        return StageReason.AMBIGUOUS_LOCAL_TIME
    action = AMBIGUOUS_ACTION.search(text)
    if action and action.group(0).casefold() not in {
        key.casefold() for key in controls.terminology_map
    }:
        return StageReason.AMBIGUOUS_ACTION_STATE
    if "<conflict>" in text.casefold():
        return StageReason.CONFLICT_DETECTED
    return None


def redact(text: str, controls: ControlBundleV1) -> RedactionResult:
    matches: list[tuple[int, int, str, str]] = []
    for rule in controls.redaction_rules:
        for match in re.finditer(rule.pattern, text):
            matches.append((match.start(), match.end(), rule.rule_id, rule.kind))
    matches.sort(key=lambda item: (item[0], item[1], item[2]))
    if any(left[1] > right[0] for left, right in zip(matches, matches[1:])):
        raise ValueError("overlapping redaction spans")
    output = text
    for start, end, _, kind in reversed(matches):
        output = output[:start] + f"<redacted:{kind}>" + output[end:]
    if SENSITIVE_RESIDUE.search(output):
        raise RuntimeError("redaction residue")
    return RedactionResult(
        output,
        tuple(sorted({item[2] for item in matches})),
        tuple((item[0], item[1]) for item in matches),
    )
