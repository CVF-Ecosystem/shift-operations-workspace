from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from refinery_bridge.canonical import dedupe_content_fingerprint, source_fingerprint
from refinery_bridge.enums import DedupeStatus, Disposition, Sensitivity, StageOutcome
from refinery_bridge.input_models import DedupeContextV1, DedupeRecordV1
from refinery_bridge.output_models import PreAdmissionRejectionV1, RefineryResultV1
from refinery_bridge.pipeline import _dedupe_preimage, refine

from _refinery_fixtures import controls, empty_context, payload, route


def test_ready_candidate_has_nine_pass_receipts_and_exact_versions() -> None:
    bundle = controls()
    result = refine(
        payload(), bundle, dedupe_context=empty_context(), quarantine_route=route()
    )
    assert isinstance(result, RefineryResultV1)
    assert result.disposition == Disposition.CANDIDATE_READY
    assert result.context_candidate is not None
    assert result.candidate_fingerprint is not None
    assert all(item.outcome == StageOutcome.PASS for item in result.stage_receipts)
    assert result.stage_receipts[6].dedupe_status == DedupeStatus.UNIQUE
    assert [item.control_version for item in result.stage_receipts] == [
        bundle.version_for(item.stage) for item in result.stage_receipts
    ]


def test_arbitrary_invalid_input_returns_provenance_free_rejection() -> None:
    for invalid in (None, "raw secret", {}, {"raw_text": "\ud800"}):
        result = refine(
            invalid, controls(), dedupe_context=None, quarantine_route=None
        )
        assert isinstance(result, PreAdmissionRejectionV1)
        encoded = result.model_dump_json()
        assert "raw secret" not in encoded
        assert "source_link" not in encoded
        assert "source_fingerprint" not in encoded


def test_ambiguous_local_time_is_quarantined_without_invention() -> None:
    text = "qc3 stop hồi 11h40, sensơ lỗi, tech đang xuống"
    result = refine(
        payload(text), controls(), dedupe_context=empty_context(), quarantine_route=route()
    )
    assert isinstance(result, RefineryResultV1)
    assert result.disposition == Disposition.NO_CANDIDATE_QUARANTINED
    assert result.context_candidate is None
    serialized = result.model_dump_json()
    assert "23:40" not in serialized
    assert "đang xử lý" not in serialized
    assert result.stage_receipts[4].reason_codes[0].value == "AMBIGUOUS_LOCAL_TIME"


def test_exact_source_duplicate_fails_stage_and_cannot_be_upgraded() -> None:
    current = payload()
    record = DedupeRecordV1(
        scope_id="scope-1",
        prior_source_id="prior-1",
        observed_at=datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc),
        source_fingerprint=source_fingerprint(str(current["raw_text"])),
    )
    context = empty_context().model_copy(update={"records": (record,)})
    result = refine(current, controls(), dedupe_context=context, quarantine_route=route())
    assert isinstance(result, RefineryResultV1)
    assert result.disposition == Disposition.NO_CANDIDATE_DUPLICATE
    assert result.stage_receipts[6].outcome == StageOutcome.FAIL
    assert result.stage_receipts[6].dedupe_status == DedupeStatus.EXACT_SOURCE_MATCH
    assert result.stage_receipts[7].outcome == StageOutcome.NOT_RUN
    assert result.quality_receipt.integrity == 0
    assert result.context_candidate is None


def test_cross_source_redacted_content_match_is_advisory_and_typed() -> None:
    bundle = controls()
    first = refine(
        payload(source_id="one"), bundle,
        dedupe_context=empty_context(), quarantine_route=route(),
    )
    assert isinstance(first, RefineryResultV1) and first.context_candidate is not None
    candidate = first.context_candidate
    content = dedupe_content_fingerprint(
        _dedupe_preimage(
            candidate.redacted_normalized_text,
            candidate.sensitivity,
            candidate.topic_labels,
            bundle,
        )
    )
    record = DedupeRecordV1(
        scope_id="scope-1",
        prior_source_id="prior-content",
        observed_at=datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc),
        source_fingerprint=source_fingerprint("different source text"),
        dedupe_content_fingerprint=content,
    )
    context = DedupeContextV1(
        scope_id="scope-1",
        window_start=empty_context().window_start,
        window_end=empty_context().window_end,
        records=(record,),
    )
    second = refine(
        payload(source_id="two"), bundle,
        dedupe_context=context, quarantine_route=route(),
    )
    assert isinstance(second, RefineryResultV1)
    assert second.disposition == Disposition.CANDIDATE_READY
    assert second.stage_receipts[6].dedupe_status == DedupeStatus.REDACTED_TEXT_MATCH


def test_redaction_and_sensitivity_escalation_are_safe() -> None:
    text = "QC03 stopped at 2026-07-21T23:40:00Z password=hunter2 confidential"
    result = refine(
        payload(text), controls(), dedupe_context=empty_context(), quarantine_route=route()
    )
    assert isinstance(result, RefineryResultV1)
    assert result.context_candidate is not None
    assert result.context_candidate.sensitivity == Sensitivity.CONFIDENTIAL
    assert "hunter2" not in result.model_dump_json()
    assert "<redacted:credential>" in result.context_candidate.redacted_normalized_text


def test_dedupe_edges_selection_and_permutation_are_deterministic() -> None:
    current = payload()
    bounds = empty_context()
    source = source_fingerprint(str(current["raw_text"]))
    earlier = DedupeRecordV1(
        scope_id="scope-1", prior_source_id="z-earlier",
        observed_at=bounds.window_start, source_fingerprint=source,
    )
    later = DedupeRecordV1(
        scope_id="scope-1", prior_source_id="a-later",
        observed_at=bounds.window_end, source_fingerprint=source,
    )
    with pytest.raises(ValidationError):
        DedupeContextV1(
            scope_id="scope-1", window_start=bounds.window_start,
            window_end=bounds.window_end,
            records=(earlier.model_copy(update={"observed_at": bounds.window_start.replace(year=2025)}),),
        )
    with pytest.raises(ValidationError):
        DedupeContextV1(
            scope_id="scope-1", window_start=bounds.window_start,
            window_end=bounds.window_end,
            records=(later.model_copy(update={"observed_at": bounds.window_end.replace(year=2027)}),),
        )
    outputs = []
    for records in ((later, earlier), (earlier, later)):
        result = refine(
            current, controls(),
            dedupe_context=bounds.model_copy(update={"records": records}),
            quarantine_route=route(),
        )
        assert isinstance(result, RefineryResultV1)
        assert result.disposition == Disposition.NO_CANDIDATE_DUPLICATE
        assert result.duplicate_receipt is not None
        assert result.duplicate_receipt.selected_prior_source_id == "z-earlier"
        assert result.duplicate_receipt.match_ids == ("a-later", "z-earlier")
        outputs.append(result.model_dump_json())
    assert outputs[0] == outputs[1]
