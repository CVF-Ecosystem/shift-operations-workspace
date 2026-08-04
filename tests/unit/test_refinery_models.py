from datetime import datetime

import pytest
from pydantic import ValidationError

from refinery_bridge.canonical import candidate_fingerprint
from refinery_bridge.controls import ControlBundleV1
from refinery_bridge.enums import (
    DedupeStatus,
    Disposition,
    SafeErrorCode,
    Stage,
    StageOutcome,
    StageReason,
)
from refinery_bridge.input_models import CandidateFingerprintV1, DedupeContextV1
from refinery_bridge.output_models import PreAdmissionRejectionV1, RefineryResultV1
from refinery_bridge.pipeline import refine
from refinery_bridge.receipt_models import QualityReceiptV1, StageReceiptV1

from _refinery_fixtures import NOW, controls, empty_context, payload, route


def test_pre_admission_codes_are_closed_sorted_unique() -> None:
    result = PreAdmissionRejectionV1(
        safe_error_codes=(SafeErrorCode.FIELD_SET_MISMATCH,)
    )
    assert result.model_dump(mode="json") == {
        "schema_version": "1.0",
        "kind": "PRE_ADMISSION_REJECTION",
        "reason": "INVALID_ENVELOPE",
        "safe_error_codes": ["FIELD_SET_MISMATCH"],
        "caller_action": "USE_EXISTING_NON_AI_RULE_WORKFLOW",
    }
    with pytest.raises(ValidationError):
        PreAdmissionRejectionV1(
            safe_error_codes=(
                SafeErrorCode.INVALID_SOURCE_ID,
                SafeErrorCode.FIELD_SET_MISMATCH,
            )
        )


def test_control_bundle_rejects_missing_and_cyclic_rules() -> None:
    data = controls().model_dump()
    del data["dedupe_rules_version"]
    with pytest.raises(ValidationError):
        ControlBundleV1.model_validate(data)
    data = controls().model_dump()
    data["terminology_map"] = {"a": "b", "b": "a"}
    with pytest.raises(ValidationError):
        ControlBundleV1.model_validate(data)


def test_receipt_reason_and_dedupe_status_matrix() -> None:
    receipt = StageReceiptV1(
        stage=Stage.DEDUPE,
        control_version="dedupe-v1",
        outcome=StageOutcome.PASS,
        reason_codes=(StageReason.STAGE_PASS,),
        dedupe_status=DedupeStatus.UNIQUE,
    )
    assert receipt.dedupe_status == DedupeStatus.UNIQUE
    with pytest.raises(ValidationError):
        StageReceiptV1(
            stage=Stage.DEDUPE,
            control_version="dedupe-v1",
            outcome=StageOutcome.PASS,
            reason_codes=(StageReason.STAGE_PASS,),
            dedupe_status=DedupeStatus.EXACT_SOURCE_MATCH,
        )
    with pytest.raises(ValidationError):
        StageReceiptV1(
            stage=Stage.QUALITY,
            control_version="quality-v1",
            outcome=StageOutcome.NOT_RUN,
            reason_codes=(StageReason.PRIOR_STAGE_FAILED,),
            safe_counts={"fabricated": 1},
        )


def test_dedupe_context_rejects_naive_inverted_and_duplicate() -> None:
    with pytest.raises(ValidationError):
        DedupeContextV1(
            scope_id="scope",
            window_start=datetime(2026, 1, 2),
            window_end=datetime(2026, 1, 1),
            records=(),
        )
    valid = empty_context()
    assert valid.window_start <= NOW <= valid.window_end


def test_models_forbid_unknown_fields() -> None:
    data = controls().model_dump()
    data["unknown"] = "forbidden"
    with pytest.raises(ValidationError):
        ControlBundleV1.model_validate(data)


def test_receipt_rejects_unsafe_ids_and_invalid_offsets() -> None:
    for offsets in (((9, 2),), ((-1, 2),), ((1, 70000),), ((1, 4), (3, 5))):
        with pytest.raises(ValidationError):
            StageReceiptV1(
                stage=Stage.NORMALIZATION,
                control_version="normalization-v1",
                outcome=StageOutcome.PASS,
                reason_codes=(StageReason.STAGE_PASS,),
                safe_offsets=offsets,
            )
    with pytest.raises(ValidationError):
        StageReceiptV1(
            stage=Stage.NORMALIZATION,
            control_version=" unsafe ",
            outcome=StageOutcome.PASS,
            reason_codes=(StageReason.STAGE_PASS,),
        )


def test_ready_result_binds_quality_candidate_and_fingerprint() -> None:
    ready = refine(
        payload(), controls(), dedupe_context=empty_context(), quarantine_route=route()
    )
    assert isinstance(ready, RefineryResultV1)
    dumped = ready.model_dump()
    dumped["quality_receipt"] = QualityReceiptV1(
        rules_version="quality-v1",
        provenance=0,
        normalization=0,
        protection=0,
        integrity=0,
        total=0,
    ).model_dump()
    with pytest.raises(ValidationError):
        RefineryResultV1.model_validate(dumped)
    dumped = ready.model_dump()
    dumped["candidate_fingerprint"] = CandidateFingerprintV1(
        sha256="0" * 64, sha512="0" * 128, byte_length=0
    ).model_dump()
    with pytest.raises(ValidationError):
        RefineryResultV1.model_validate(dumped)


def test_no_candidate_disposition_binds_first_failure() -> None:
    duplicate = refine(
        payload(), controls(), dedupe_context=None, quarantine_route=route()
    )
    assert isinstance(duplicate, RefineryResultV1)
    dumped = duplicate.model_dump()
    dumped["disposition"] = Disposition.NO_CANDIDATE_DUPLICATE
    dumped["quarantine_receipt"] = None
    dumped["duplicate_receipt"] = {
        "dedupe_status": DedupeStatus.EXACT_SOURCE_MATCH,
        "selected_prior_source_id": "invented",
        "match_ids": ("invented",),
        "match_count": 1,
    }
    with pytest.raises(ValidationError):
        RefineryResultV1.model_validate(dumped)


def test_public_results_reject_version_route_and_provenance_drift() -> None:
    ready = refine(payload(), controls(), dedupe_context=empty_context(), quarantine_route=route())
    assert isinstance(ready, RefineryResultV1)
    dumped = ready.model_dump()
    dumped["context_candidate"]["normalization_rules_version"] = "normalization-v2"
    dumped["candidate_fingerprint"] = candidate_fingerprint(
        dumped["context_candidate"]
    ).model_dump()
    with pytest.raises(ValidationError):
        RefineryResultV1.model_validate(dumped)

    quarantined = refine(payload("QC03 stopped hồi 11h40"), controls(), dedupe_context=empty_context(), quarantine_route=route())
    assert isinstance(quarantined, RefineryResultV1)
    dumped = quarantined.model_dump()
    dumped["quarantine_receipt"]["route"]["sink_available"] = False
    with pytest.raises(ValidationError):
        RefineryResultV1.model_validate(dumped)

    fallback = refine(payload(), controls(), dedupe_context=None, quarantine_route=route(available=False))
    assert isinstance(fallback, RefineryResultV1)
    for field, unsafe in (("source_owner_id", " owner "), ("source_link", "https://u:p@example/x")):
        dumped = fallback.model_dump()
        dumped[field] = unsafe
        with pytest.raises(ValidationError):
            RefineryResultV1.model_validate(dumped)
