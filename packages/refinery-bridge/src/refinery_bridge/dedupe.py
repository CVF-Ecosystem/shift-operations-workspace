from __future__ import annotations

from dataclasses import dataclass

from .canonical import collision_suspected, triples_equal
from .enums import DedupeStatus
from .input_models import (
    DedupeContentFingerprintV1,
    DedupeContextV1,
    SourceFingerprintV1,
)


@dataclass(frozen=True)
class DedupeAnalysis:
    status: DedupeStatus
    selected_prior_source_id: str | None
    match_ids: tuple[str, ...]


def analyze_dedupe(
    source: SourceFingerprintV1,
    content: DedupeContentFingerprintV1,
    context: DedupeContextV1 | None,
) -> DedupeAnalysis:
    if context is None:
        return DedupeAnalysis(DedupeStatus.INSUFFICIENT_CONTEXT, None, ())
    ordered = sorted(context.records, key=lambda item: (item.observed_at, item.prior_source_id))
    for record in ordered:
        if collision_suspected(source, record.source_fingerprint):
            return DedupeAnalysis(
                DedupeStatus.DIGEST_COLLISION_SUSPECTED, record.prior_source_id,
                (record.prior_source_id,),
            )
        if record.dedupe_content_fingerprint is not None and collision_suspected(
            content, record.dedupe_content_fingerprint
        ):
            return DedupeAnalysis(
                DedupeStatus.DIGEST_COLLISION_SUSPECTED, record.prior_source_id,
                (record.prior_source_id,),
            )
    source_matches = tuple(
        record.prior_source_id
        for record in ordered
        if triples_equal(source, record.source_fingerprint)
    )
    if source_matches:
        return DedupeAnalysis(DedupeStatus.EXACT_SOURCE_MATCH, source_matches[0], source_matches)
    content_matches = tuple(
        record.prior_source_id
        for record in ordered
        if record.dedupe_content_fingerprint is not None
        and triples_equal(content, record.dedupe_content_fingerprint)
    )
    if content_matches:
        return DedupeAnalysis(
            DedupeStatus.REDACTED_TEXT_MATCH, content_matches[0], content_matches
        )
    return DedupeAnalysis(DedupeStatus.UNIQUE, None, ())
