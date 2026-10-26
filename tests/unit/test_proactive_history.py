from __future__ import annotations

from dataclasses import replace
from datetime import timedelta, timezone
from hashlib import sha256
import json
from uuid import NAMESPACE_DNS, uuid5

from proactive_helpers import START, history, report
from operations_domain.report_models import ReportStatus
from reporting_engine.proactive_analysis import analyze
from reporting_engine.proactive_history import lineage_digest, lineage_payload, select_history
from reporting_engine.proactive_evaluation import evaluate


def _stamp(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _hash(payload):
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _expected_item(report):
    return {"shift_id": str(report.shift_id), "report_id": str(report.report_id),
            "version": report.version, "generated_from_cutoff": _stamp(report.generated_from_cutoff),
            "created_at": _stamp(report.created_at), "snapshot_digest": report.content.snapshot_digest,
            "source_manifest": []}


def test_late_successor_is_excluded_at_older_origin_and_current_flag_is_ignored():
    source = history([0] * 18)
    first = source.candidates[0].model_copy(update={"is_current": False, "status": ReportStatus.FROZEN})
    late = report(0, 4, version=2, created_offset=timedelta(hours=16))
    source = replace(source, candidates=(first, *source.candidates[1:], late))
    old = select_history(source, START + timedelta(hours=12), require_complete=False)
    assert next(o for o in old if o.shift_id == first.shift_id).version == 1
    current = select_history(source, source.run_as_of, require_complete=True)
    assert next(o for o in current if o.shift_id == first.shift_id).version == 2
    base = history([0] * 18)
    base_selected = select_history(base, base.run_as_of, require_complete=True)
    base_folds = evaluate(base, base_selected, lineage_digest(base, base_selected, as_of=base.run_as_of))["folds"]
    revised = evaluate(source, current, lineage_digest(source, current, as_of=source.run_as_of))
    revised_folds = revised["folds"]
    assert revised_folds[0]["training_lineage_digest"] == base_folds[0]["training_lineage_digest"]
    assert revised_folds[-1]["training_lineage_digest"] != base_folds[-1]["training_lineage_digest"]
    first_refs = revised["training_lineage_payloads"][0]["selected_reports"]
    last_refs = revised["training_lineage_payloads"][-1]["selected_reports"]
    assert next(item for item in first_refs if item["shift_id"] == str(first.shift_id))["version"] == 1
    assert next(item for item in last_refs if item["shift_id"] == str(first.shift_id))["version"] == 2
    assert [fold["target_shift_id"] for fold in revised_folds] == [str(r.shift_id) for r in source.candidates[6:18]]
    assert all(fold["prediction_numerator"] == 0 for fold in revised_folds)
    for fold, training in zip(revised_folds, revised["training_lineage_payloads"]):
        assert fold["target_shift_id"] not in training["eligible_shift_ids"]


def test_missing_expected_shift_and_incomplete_attestation_are_refusals():
    source = history([0] * 18)
    for changed in (replace(source, candidates=source.candidates[:-1]),
                    replace(source, complete=False), replace(source, retention_complete=False)):
        answer = analyze(changed)
        assert answer["outcome"] == "ABSTAINED" and answer["reason"] == "SCOPE_INCOMPLETE"
        assert "forecast_count" not in answer


def test_candidate_and_shift_caps_refuse_before_truncation():
    source = history([0] * 18)
    oversized = replace(source, candidates=source.candidates + (source.candidates[0],) * 483)
    assert analyze(oversized)["reason"] == "SCOPE_INCOMPLETE"
    ids = tuple(sorted((uuid5(NAMESPACE_DNS, f"cap-{i}") for i in range(501)), key=str))
    assert analyze(replace(source, eligible_shift_ids=ids))["reason"] == "SCOPE_INCOMPLETE"
    many_refs = report(0, 501, version=2, created_offset=timedelta(hours=1))
    assert analyze(replace(source, candidates=source.candidates + (many_refs,)))["reason"] == "SCOPE_INCOMPLETE"


def test_aware_half_open_window_naive_time_and_future_revision():
    source = history([0] * 18)
    assert analyze(replace(source, query_end=source.candidates[-1].generated_from_cutoff))["reason"] == "SCOPE_INCOMPLETE"
    assert analyze(replace(source, query_start=source.candidates[0].generated_from_cutoff + timedelta(microseconds=1)))["reason"] == "SCOPE_INCOMPLETE"
    assert analyze(replace(source, query_end=source.run_as_of + timedelta(microseconds=1)))["reason"] == "TIME_AMBIGUOUS"
    naive = source.candidates[0].model_copy(update={"created_at": START.replace(tzinfo=None)})
    assert analyze(replace(source, candidates=(naive, *source.candidates[1:])))["reason"] == "TIME_AMBIGUOUS"
    offset = timezone(timedelta(hours=7))
    shifted = replace(source, query_start=source.query_start.astimezone(offset),
                      query_end=source.query_end.astimezone(offset), run_as_of=source.run_as_of.astimezone(offset))
    assert analyze(shifted)["lineage_digest"] == analyze(source)["lineage_digest"]
    future = report(0, 4, version=2, created_offset=timedelta(hours=20))
    assert analyze(replace(source, candidates=source.candidates + (future,)))["lineage_digest"] == analyze(source)["lineage_digest"]


def test_lineage_digest_reorder_stable_but_window_scope_and_version_sensitive():
    source = history([0] * 18)
    original = analyze(source)
    assert original["outcome"] == "READY"
    assert analyze(replace(source, candidates=tuple(reversed(source.candidates))))["lineage_digest"] == original["lineage_digest"]
    assert analyze(replace(source, scope_id="OTHER_PUBLIC_SCOPE"))["lineage_digest"] != original["lineage_digest"]
    assert analyze(replace(source, query_end=source.query_end + timedelta(minutes=1),
                           run_as_of=source.run_as_of + timedelta(minutes=1)))["lineage_digest"] != original["lineage_digest"]
    later = report(0, 0, version=2, created_offset=timedelta(hours=1))
    assert analyze(replace(source, candidates=source.candidates + (later,)))["lineage_digest"] != original["lineage_digest"]


def test_independent_outer_training_and_evaluation_digest_preimages():
    source = history([0] * 18)
    result = analyze(source)
    context = result["history_context"]
    reports = list(source.candidates)
    outer = {"scope_id": "PUBLIC_SCOPE", "query_start": _stamp(source.query_start),
             "query_end": _stamp(source.query_end), "run_as_of": _stamp(source.run_as_of),
             "policy_version": "P5A2-INITIAL-1", "eligible_shift_ids": [str(i) for i in source.eligible_shift_ids],
             "selected_reports": [_expected_item(r) for r in reports]}
    assert context["actor_assertion"] == "PUBLIC_ACTOR"
    assert context["outer_lineage_payload"] == outer
    assert result["lineage_digest"] == _hash(outer)
    expected_folds = []
    for target_index in range(6, 18):
        target = reports[target_index]
        origin = target.generated_from_cutoff - timedelta(microseconds=1)
        training = reports[:target_index]
        train_payload = {**outer, "run_as_of": _stamp(origin),
                         "eligible_shift_ids": sorted(str(r.shift_id) for r in training),
                         "selected_reports": [_expected_item(r) for r in training]}
        assert context["training_lineage_payloads"][target_index - 6] == train_payload
        expected_folds.append({"origin_cutoff": _stamp(origin), "target_shift_id": str(target.shift_id),
                               "target_report_id": str(target.report_id), "target_version": 1,
                               "target_digest": target.content.snapshot_digest,
                               "target_availability": _stamp(target.created_at),
                               "training_lineage_digest": _hash(train_payload),
                               "prediction_numerator": 0, "prediction_denominator": 1,
                               "comparator": "0/1", "target_count": 0, "absolute_residual": "0/1"})
    evaluation_payload = {"lineage_digest": _hash(outer), "policy_version": "P5A2-INITIAL-1", "folds": expected_folds}
    assert context["evaluation_payload"] == evaluation_payload
    assert result["evaluation_digest"] == _hash(evaluation_payload)


def test_latest_twelve_targets_and_insufficient_historical_training():
    source = history([0] * 20)
    folds = analyze(source)["history_context"]["evaluation_payload"]["folds"]
    assert [fold["target_shift_id"] for fold in folds] == [str(r.shift_id) for r in source.candidates[8:]]
    assert all(fold["prediction_numerator"] == 0 for fold in folds)
    late = tuple(r.model_copy(update={"created_at": r.created_at + timedelta(hours=8)}) if i < 6 else r
                 for i, r in enumerate(source.candidates))
    answer = analyze(replace(source, candidates=late))
    assert answer["outcome"] == "ABSTAINED" and answer["reason"] == "CALIBRATION_UNAVAILABLE"
    assert answer["diagnostics"]["available_training"] < 6
    assert answer["diagnostics"]["required_training"] == 6


def test_equal_origin_cutoff_is_visible_and_preserves_original_window():
    source = history([0] * 18)
    origin = START + timedelta(hours=6) - timedelta(microseconds=1)
    aligned = source.candidates[5].model_copy(update={"generated_from_cutoff": origin, "created_at": origin})
    changed = replace(source, candidates=(*source.candidates[:5], aligned, *source.candidates[6:]))
    chosen = select_history(changed, origin, require_complete=False,
                            before=(START + timedelta(hours=6), str(source.candidates[6].shift_id)))
    assert any(o.report_id == aligned.report_id and o.cutoff == origin for o in chosen)
    payload = lineage_payload(changed, chosen, as_of=origin, training=True)
    assert payload["query_end"] == _stamp(source.query_end)
    assert payload["run_as_of"] == _stamp(origin)
