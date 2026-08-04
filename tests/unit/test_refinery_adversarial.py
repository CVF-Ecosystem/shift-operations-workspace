from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

import refinery_bridge.pipeline as pipeline_module
from refinery_bridge.canonical import dedupe_content_fingerprint, source_fingerprint
from refinery_bridge.controls import ControlBundleV1, RedactionRuleV1
from refinery_bridge.enums import (
    DedupeStatus,
    Disposition,
    Sensitivity,
    StageOutcome,
    StageReason,
)
from refinery_bridge.input_models import DedupeContextV1, DedupeRecordV1
from refinery_bridge.normalization import normalize_syntax
from refinery_bridge.output_models import PreAdmissionRejectionV1, RefineryResultV1
from refinery_bridge.pipeline import StageUnavailableError, _dedupe_preimage, refine

from _refinery_fixtures import MATRIX_CASES, controls, empty_context, payload, route

ROOT = Path(__file__).resolve().parents[2]


def run(
    current: object | None = None,
    *,
    bundle: ControlBundleV1 | None = None,
    context: object | None = None,
    quarantine: object | None = None,
) -> PreAdmissionRejectionV1 | RefineryResultV1:
    return refine(
        payload() if current is None else current,
        controls() if bundle is None else bundle,
        dedupe_context=empty_context() if context is None else context,
        quarantine_route=route() if quarantine is None else quarantine,
    )


@pytest.mark.parametrize("case_id", MATRIX_CASES, ids=MATRIX_CASES)
def test_r27_executable_matrix(
    case_id: str, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    if case_id == "non-mapping":
        assert isinstance(run([]), PreAdmissionRejectionV1)
    elif case_id == "missing-field":
        current = payload()
        current.pop("source_id")
        assert isinstance(run(current), PreAdmissionRejectionV1)
    elif case_id == "extra-field":
        assert isinstance(run({**payload(), "extra": "x"}), PreAdmissionRejectionV1)
    elif case_id == "unpaired-surrogate":
        assert isinstance(run({**payload(), "raw_text": "\ud800"}), PreAdmissionRejectionV1)
    elif case_id == "unsafe-link":
        current = {**payload(), "source_link": "https://u:p@example/x"}
        assert isinstance(run(current), PreAdmissionRejectionV1)
    elif case_id == "malformed-fingerprint":
        current = {**payload(), "source_fingerprint": {"sha256": "bad"}}
        assert isinstance(run(current), PreAdmissionRejectionV1)
    elif case_id == "fingerprint-mismatch":
        current = payload()
        current["source_fingerprint"] = source_fingerprint("different").model_dump()
        result = run(current)
        assert isinstance(result, RefineryResultV1)
        assert result.source_fingerprint == source_fingerprint(str(current["raw_text"]))
    elif case_id == "control-version-substitution":
        data = controls().model_dump()
        data["dedupe_rules_version"] = data["quality_rules_version"]
        with pytest.raises(ValidationError):
            ControlBundleV1.model_validate(data)
    elif case_id == "ready":
        result = run()
        assert isinstance(result, RefineryResultV1)
        assert result.disposition == Disposition.CANDIDATE_READY
    elif case_id == "nfc-idempotence":
        once = normalize_syntax("e\u0301\r\n  ready   now ")
        assert once == normalize_syntax(once) and "é" in once
    elif case_id == "qualified-time":
        fixture = json.loads(
            (ROOT / "fixtures/refinery/qualified_time_message.json").read_text(encoding="utf-8")
        )
        result = run(payload(fixture["input"]["raw_text"], source_id="qualified"))
        assert isinstance(result, RefineryResultV1)
        assert result.disposition.value == fixture["expected_disposition"]
    elif case_id == "ambiguous-time":
        result = run(payload("QC03 stopped hồi 11h40"))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[4].reason_codes == (StageReason.AMBIGUOUS_LOCAL_TIME,)
    elif case_id == "ambiguous-action":
        result = run(payload("tech đang xuống"))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[4].reason_codes == (StageReason.AMBIGUOUS_ACTION_STATE,)
    elif case_id == "terminology":
        result = run(payload("tech stopped at 2026-07-21T23:40:00Z"))
        assert isinstance(result, RefineryResultV1) and result.context_candidate is not None
        assert "technical" in result.context_candidate.redacted_normalized_text
    elif case_id == "terminology-overlap":
        data = controls().model_dump()
        data["terminology_map"] = {"a": "b", "b": "a"}
        with pytest.raises(ValidationError):
            ControlBundleV1.model_validate(data)
    elif case_id == "sensitivity-retention":
        result = run(payload(sensitivity=Sensitivity.CONFIDENTIAL))
        assert isinstance(result, RefineryResultV1) and result.context_candidate is not None
        assert result.context_candidate.sensitivity == Sensitivity.CONFIDENTIAL
    elif case_id == "sensitivity-escalation":
        result = run(payload("QC03 stopped confidential"))
        assert isinstance(result, RefineryResultV1) and result.context_candidate is not None
        assert result.context_candidate.sensitivity == Sensitivity.CONFIDENTIAL
    elif case_id == "policy-drift":
        monkeypatch.setattr(
            pipeline_module, "classify", lambda *_: (Sensitivity.PUBLIC, ())
        )
        result = run(payload(sensitivity=Sensitivity.RESTRICTED))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[3].reason_codes == (StageReason.POLICY_DRIFT,)
    elif case_id == "redaction":
        result = run(payload("QC03 stopped password=hunter2"))
        assert isinstance(result, RefineryResultV1) and result.context_candidate is not None
        assert "hunter2" not in result.model_dump_json()
    elif case_id == "redaction-overlap":
        overlapping = controls().model_copy(
            update={
                "redaction_rules": (
                    RedactionRuleV1(rule_id="a", kind="secret", pattern="secret"),
                    RedactionRuleV1(rule_id="b", kind="secret", pattern="cret"),
                )
            }
        )
        result = run(payload("QC03 stopped secret"), bundle=overlapping)
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[5].reason_codes == (StageReason.REDACTION_FAILED,)
    elif case_id == "redaction-residue":
        result = run(payload("QC03 stopped password=hunter2"), bundle=controls().model_copy(update={"redaction_rules": ()}))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[5].reason_codes == (StageReason.REDACTION_RESIDUE,)
    elif case_id == "conflict":
        result = run(payload("QC03 stopped <conflict>"))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[4].reason_codes == (StageReason.CONFLICT_DETECTED,)
    elif case_id == "source-duplicate":
        current = payload()
        record = DedupeRecordV1(
            scope_id="scope-1", prior_source_id="prior", observed_at=datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            source_fingerprint=source_fingerprint(str(current["raw_text"])),
        )
        result = run(current, context=empty_context().model_copy(update={"records": (record,)}))
        assert isinstance(result, RefineryResultV1)
        assert result.disposition == Disposition.NO_CANDIDATE_DUPLICATE
    elif case_id == "content-match":
        first = run(payload(source_id="one"))
        assert isinstance(first, RefineryResultV1) and first.context_candidate is not None
        candidate = first.context_candidate
        content = dedupe_content_fingerprint(
            _dedupe_preimage(candidate.redacted_normalized_text, candidate.sensitivity, candidate.topic_labels, controls())
        )
        record = DedupeRecordV1(
            scope_id="scope-1", prior_source_id="prior", observed_at=datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            source_fingerprint=source_fingerprint("different"), dedupe_content_fingerprint=content,
        )
        result = run(payload(source_id="two"), context=empty_context().model_copy(update={"records": (record,)}))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[6].dedupe_status == DedupeStatus.REDACTED_TEXT_MATCH
    elif case_id == "collision":
        current = payload()
        source = source_fingerprint(str(current["raw_text"]))
        record = DedupeRecordV1(
            scope_id="scope-1", prior_source_id="collision", observed_at=datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            source_fingerprint=source.model_copy(update={"byte_length": source.byte_length + 1}),
        )
        result = run(current, context=empty_context().model_copy(update={"records": (record,)}))
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[6].dedupe_status == DedupeStatus.DIGEST_COLLISION_SUSPECTED
    elif case_id == "invalid-context":
        result = run(context={"scope_id": "scope-1", "window_start": "bad", "window_end": "bad", "records": []})
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[6].reason_codes == (StageReason.DEDUPE_CONTEXT_INVALID,)
    elif case_id == "unavailable-route":
        result = refine(payload(), controls(), dedupe_context=None, quarantine_route=route(available=False))
        assert isinstance(result, RefineryResultV1)
        assert result.disposition == Disposition.NO_CANDIDATE_FALLBACK
    elif case_id == "invariant":
        caplog.set_level(logging.DEBUG)
        monkeypatch.setattr(
            pipeline_module,
            "conflict_reason",
            lambda *_: (_ for _ in ()).throw(RuntimeError("raw-secret")),
        )
        result = run()
        assert isinstance(result, RefineryResultV1)
        assert result.stage_receipts[4].reason_codes == (StageReason.STAGE_INVARIANT_ERROR,)
        assert "raw-secret" not in result.model_dump_json() + caplog.text
    else:
        raise AssertionError(f"unbound R27 case: {case_id}")


def test_stage_unavailable_is_typed_and_fail_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pipeline_module,
        "normalize_syntax",
        lambda *_: (_ for _ in ()).throw(StageUnavailableError()),
    )
    result = run()
    assert isinstance(result, RefineryResultV1)
    assert result.stage_receipts[1].reason_codes == (StageReason.STAGE_UNAVAILABLE,)
    assert result.stage_receipts[2].outcome == StageOutcome.NOT_RUN
    assert result.disposition == Disposition.NO_CANDIDATE_FALLBACK


def test_disclosure_matrix_excludes_values_from_union_receipt_log_and_snapshot(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    secret = "ac07-matched-secret"
    invalid = {**payload(secret), "source_link": " unsafe "}
    first = run(invalid)
    second = run(invalid)
    assert isinstance(first, PreAdmissionRejectionV1)
    assert first.model_dump_json() == second.model_dump_json()
    assert secret not in first.model_dump_json()

    broken = controls().model_dump()
    broken["terminology_map"] = {"a": "b", "b": "a"}
    with pytest.raises(ValidationError):
        ControlBundleV1.model_validate(broken)
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(
        pipeline_module, "conflict_reason",
        lambda *_: (_ for _ in ()).throw(RuntimeError(secret)),
    )
    failed = run(payload(secret))
    assert isinstance(failed, RefineryResultV1)
    surfaces = (
        failed.model_dump_json(), failed.stage_receipts[4].model_dump_json(),
        json.dumps(failed.model_dump(mode="json"), sort_keys=True), caplog.text,
    )
    assert all(secret not in surface for surface in surfaces)
