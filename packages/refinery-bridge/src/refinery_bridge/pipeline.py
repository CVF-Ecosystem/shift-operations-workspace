from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .canonical import candidate_fingerprint, dedupe_content_fingerprint, source_fingerprint
from .controls import ControlBundleV1
from .dedupe import DedupeAnalysis, analyze_dedupe
from .enums import (
    DedupeStatus,
    Disposition,
    FallbackReason,
    Stage,
    StageOutcome,
    StageReason,
)
from .input_models import DedupeContextV1, QuarantineRouteV1, RefineryEnvelopeV1
from .normalization import normalize_syntax
from .output_models import (
    ContextCandidateV1,
    PreAdmissionRejectionV1,
    RefineryBoundaryOutputV1,
    RefineryResultV1,
    pre_admit,
)
from .protection import (
    StageUnavailableError,
    apply_terminology,
    classification_is_valid,
    classify,
    conflict_reason,
    dedupe_preimage as _dedupe_preimage,
    execute_stage as _execute,
    quarantine_reason as _quarantine_reason,
    redact,
)
from .receipt_models import (
    DuplicateReceiptV1,
    FallbackReceiptV1,
    QualityReceiptV1,
    QuarantineReceiptV1,
    StageReceiptV1,
    complete_receipts,
    make_receipt,
    quality_receipt,
)

def _failed_result(
    envelope: RefineryEnvelopeV1,
    local_source: Any,
    controls: ControlBundleV1,
    receipts: list[StageReceiptV1],
    reason: StageReason,
    route: QuarantineRouteV1 | None,
    analysis: DedupeAnalysis | None = None,
) -> RefineryResultV1:
    completed = complete_receipts(controls, receipts)
    quality = quality_receipt(controls, receipts)
    common = dict(
        source_owner_id=envelope.source_owner_id,
        source_link=envelope.source_link,
        source_fingerprint=local_source,
        stage_receipts=completed,
        quality_receipt=quality,
    )
    if reason == StageReason.EXACT_SOURCE_MATCH and analysis is not None:
        return RefineryResultV1(
            disposition=Disposition.NO_CANDIDATE_DUPLICATE,
            duplicate_receipt=DuplicateReceiptV1(
                dedupe_status=DedupeStatus.EXACT_SOURCE_MATCH,
                selected_prior_source_id=analysis.selected_prior_source_id or "unreachable",
                match_ids=tuple(sorted(set(analysis.match_ids))),
                match_count=len(set(analysis.match_ids)),
            ),
            **common,
        )
    if reason in (StageReason.STAGE_UNAVAILABLE, StageReason.STAGE_INVARIANT_ERROR):
        fallback_reason = FallbackReason(reason.value)
    elif route is None or not route.sink_available or (
        route.policy_version != controls.current_quarantine_policy_version
    ):
        fallback_reason = FallbackReason.QUARANTINE_ROUTE_UNAVAILABLE
    else:
        return RefineryResultV1(
            disposition=Disposition.NO_CANDIDATE_QUARANTINED,
            quarantine_receipt=QuarantineReceiptV1(
                reason=_quarantine_reason(reason),
                source_owner_id=envelope.source_owner_id,
                source_link=envelope.source_link,
                source_fingerprint=local_source,
                route=route,
            ),
            **common,
        )
    return RefineryResultV1(
        disposition=Disposition.NO_CANDIDATE_FALLBACK,
        fallback_receipt=FallbackReceiptV1(reason=fallback_reason),
        **common,
    )


def refine(
    payload: Any,
    controls: ControlBundleV1,
    *,
    dedupe_context: DedupeContextV1 | dict[str, Any] | None,
    quarantine_route: QuarantineRouteV1 | None,
) -> RefineryBoundaryOutputV1:
    admitted = pre_admit(payload)
    if isinstance(admitted, PreAdmissionRejectionV1):
        return admitted
    envelope = admitted
    local_source = source_fingerprint(envelope.raw_text)
    receipts: list[StageReceiptV1] = []
    if local_source != envelope.source_fingerprint:
        reason = StageReason.PROVENANCE_MISMATCH
        receipts.append(make_receipt(controls, Stage.ENVELOPE, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    receipts.append(make_receipt(controls, Stage.ENVELOPE, StageOutcome.PASS, StageReason.STAGE_PASS))
    normalized, reason = _execute(lambda: normalize_syntax(envelope.raw_text))
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.NORMALIZATION, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert normalized is not None
    receipts.append(make_receipt(controls, Stage.NORMALIZATION, StageOutcome.PASS, StageReason.STAGE_PASS))
    terminology, reason = _execute(
        lambda: apply_terminology(normalized, controls),
        ((ValueError, StageReason.UNSUPPORTED_TRANSFORM),),
    )
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.TERMINOLOGY, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert terminology is not None
    receipts.append(
        make_receipt(controls, Stage.TERMINOLOGY, StageOutcome.PASS, StageReason.STAGE_PASS,
                 counts={"matches": len(terminology.offsets)}, offsets=terminology.offsets,
                 ids=terminology.rule_ids)
    )
    classified, reason = _execute(
        lambda: classify(terminology.text, envelope.declared_sensitivity, controls)
    )
    if reason is None and classified is not None:
        try:
            sensitivity, topics = classified
        except Exception:
            reason = StageReason.STAGE_INVARIANT_ERROR
        else:
            if not classification_is_valid(
                envelope.declared_sensitivity, sensitivity, topics
            ):
                reason = StageReason.POLICY_DRIFT
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.CLASSIFICATION, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    receipts.append(
        make_receipt(controls, Stage.CLASSIFICATION, StageOutcome.PASS, StageReason.STAGE_PASS,
                 counts={"topics": len(topics)}, ids=topics)
    )
    conflict, reason = _execute(lambda: conflict_reason(terminology.text, controls))
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.CONFLICT, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    if conflict is not None:
        receipts.append(make_receipt(controls, Stage.CONFLICT, StageOutcome.FAIL, conflict))
        return _failed_result(envelope, local_source, controls, receipts, conflict, quarantine_route)
    receipts.append(make_receipt(controls, Stage.CONFLICT, StageOutcome.PASS, StageReason.STAGE_PASS))
    redaction, reason = _execute(
        lambda: redact(terminology.text, controls),
        (
            (RuntimeError, StageReason.REDACTION_RESIDUE),
            (ValueError, StageReason.REDACTION_FAILED),
        ),
    )
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.REDACTION, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert redaction is not None
    receipts.append(
        make_receipt(controls, Stage.REDACTION, StageOutcome.PASS, StageReason.STAGE_PASS,
                 counts={"redactions": len(redaction.offsets)}, offsets=redaction.offsets,
                 ids=redaction.rule_ids)
    )
    content_fp, reason = _execute(
        lambda: dedupe_content_fingerprint(
            _dedupe_preimage(redaction.text, sensitivity, topics, controls)
        )
    )
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.DEDUPE, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    if isinstance(dedupe_context, dict):
        try:
            dedupe_context = DedupeContextV1.model_validate(dedupe_context)
        except ValidationError:
            reason = StageReason.DEDUPE_CONTEXT_INVALID
            receipts.append(make_receipt(controls, Stage.DEDUPE, StageOutcome.FAIL, reason))
            return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    analysis, reason = _execute(
        lambda: analyze_dedupe(local_source, content_fp, dedupe_context)
    )
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.DEDUPE, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert analysis is not None
    public_match_ids = tuple(sorted(set(analysis.match_ids)))
    failures = {
        DedupeStatus.EXACT_SOURCE_MATCH: StageReason.EXACT_SOURCE_MATCH,
        DedupeStatus.DIGEST_COLLISION_SUSPECTED: StageReason.DIGEST_COLLISION_SUSPECTED,
        DedupeStatus.INSUFFICIENT_CONTEXT: StageReason.INSUFFICIENT_CONTEXT,
    }
    if analysis.status in failures:
        reason = failures[analysis.status]
        receipts.append(
            make_receipt(controls, Stage.DEDUPE, StageOutcome.FAIL, reason,
                     status=analysis.status, counts={"matches": len(analysis.match_ids)},
                     ids=public_match_ids)
        )
        return _failed_result(
            envelope, local_source, controls, receipts, reason, quarantine_route, analysis
        )
    receipts.append(
        make_receipt(controls, Stage.DEDUPE, StageOutcome.PASS, StageReason.STAGE_PASS,
                 status=analysis.status, counts={"matches": len(analysis.match_ids)},
                 ids=public_match_ids)
    )
    quality, reason = _execute(lambda: quality_receipt(controls, receipts))
    if reason is not None:
        receipts.append(make_receipt(controls, Stage.QUALITY, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert quality is not None
    if quality.total != 100:
        reason = StageReason.QUALITY_INCOMPLETE
        receipts.append(make_receipt(controls, Stage.QUALITY, StageOutcome.FAIL, reason))
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    receipts.append(make_receipt(controls, Stage.QUALITY, StageOutcome.PASS, StageReason.STAGE_PASS))
    receipts.append(
        make_receipt(controls, Stage.CANDIDATE_ADMISSION, StageOutcome.PASS, StageReason.STAGE_PASS)
    )
    candidate, reason = _execute(
        lambda: ContextCandidateV1(
            redacted_normalized_text=redaction.text,
            sensitivity=sensitivity,
            topic_labels=topics,
            source_id=envelope.source_id,
            source_version=envelope.source_version,
            source_owner_id=envelope.source_owner_id,
            source_link=envelope.source_link,
            source_fingerprint=local_source,
            normalization_rules_version=controls.normalization_rules_version,
            terminology_rules_version=controls.terminology_rules_version,
            classification_rules_version=controls.classification_rules_version,
            redaction_rules_version=controls.redaction_rules_version,
            quality_rules_version=controls.quality_rules_version,
            quality_score=quality.total,
            provenance=quality.provenance,
            normalization=quality.normalization,
            protection=quality.protection,
            integrity=quality.integrity,
        )
    )
    if reason is not None:
        receipts[-1] = make_receipt(
            controls, Stage.CANDIDATE_ADMISSION, StageOutcome.FAIL, reason
        )
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert candidate is not None
    fingerprint, reason = _execute(
        lambda: candidate_fingerprint(candidate.fingerprint_preimage())
    )
    if reason is not None:
        receipts[-1] = make_receipt(
            controls, Stage.CANDIDATE_ADMISSION, StageOutcome.FAIL, reason
        )
        return _failed_result(envelope, local_source, controls, receipts, reason, quarantine_route)
    assert fingerprint is not None
    return RefineryResultV1(
        disposition=Disposition.CANDIDATE_READY,
        source_owner_id=envelope.source_owner_id,
        source_link=envelope.source_link,
        source_fingerprint=local_source,
        stage_receipts=tuple(receipts),
        quality_receipt=quality,
        context_candidate=candidate,
        candidate_fingerprint=fingerprint,
    )
