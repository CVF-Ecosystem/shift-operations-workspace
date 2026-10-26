from __future__ import annotations

from dataclasses import replace
from datetime import timedelta

from tests.unit.proactive_helpers import START, history, report
from operations_domain.report_digest import aggregate_digest
from operations_domain.report_models import ReportContent
from reporting_engine.proactive_analysis import analyze


def test_full_aggregate_manifest_and_record_bytes_are_revalidated():
    source = history([0] * 17 + [1])
    original = source.candidates[-1]
    bad_digest = original.content.model_copy(update={"snapshot_digest": "0" * 64})
    assert analyze(replace(source, candidates=(*source.candidates[:-1],
                                             original.model_copy(update={"content": bad_digest}))))["reason"] == "LINEAGE_INVALID"
    sections = list(original.content.sections)
    incident = sections[4]
    changed = dict(incident.records[0], summary="changed after snapshot")
    sections[4] = incident.model_copy(update={"records": [changed]})
    bad_record = original.content.model_copy(update={"sections": sections})
    assert analyze(replace(source, candidates=(*source.candidates[:-1],
                                             original.model_copy(update={"content": bad_record}))))["reason"] == "LINEAGE_INVALID"
    bad_ref = original.content.source_manifest[0].model_copy(update={"source_digest": "a" * 64})
    ref_content = original.content.model_copy(update={"source_manifest": [bad_ref]})
    ref_content = ref_content.model_copy(update={"snapshot_digest": aggregate_digest(original.shift_id, "END_SHIFT", ref_content)})
    assert analyze(replace(source, candidates=(*source.candidates[:-1],
                                             original.model_copy(update={"content": ref_content}))))["reason"] == "LINEAGE_INVALID"
    naive_event = dict(incident.records[0], created_at="2026-01-01T17:00:00")
    sections[4] = incident.model_copy(update={"records": [naive_event]})
    naive_content = original.content.model_copy(update={"sections": sections})
    assert analyze(replace(source, candidates=(*source.candidates[:-1],
                                             original.model_copy(update={"content": naive_content}))))["reason"] == "TIME_AMBIGUOUS"


def test_conflicting_same_version_and_out_of_manifest_are_refused():
    source = history([0] * 18)
    conflict = source.candidates[0].model_copy(update={"report_id": source.candidates[1].report_id})
    assert analyze(replace(source, candidates=source.candidates + (conflict,)))["reason"] == "LINEAGE_INVALID"
    extra = report(99, 0)
    assert analyze(replace(source, candidates=source.candidates + (extra,)))["reason"] == "SCOPE_INCOMPLETE"


def test_same_identity_and_digest_with_changed_immutable_bytes_refuses_both_orders():
    source = history([1] * 18)
    original = source.candidates[0]
    sections = list(original.content.sections)
    incident = sections[4]
    sections[4] = incident.model_copy(update={"records": [dict(incident.records[0], summary="conflict")]})
    altered = original.model_copy(update={"content": original.content.model_copy(update={"sections": sections})})
    for pair in ((original, altered), (altered, original)):
        answer = analyze(replace(source, candidates=(*source.candidates[1:], *pair)))
        assert answer["outcome"] == "ABSTAINED" and answer["reason"] == "LINEAGE_INVALID"
    lifecycle = original.model_copy(update={"is_current": False})
    assert analyze(replace(source, candidates=source.candidates + (lifecycle,)))["outcome"] == "READY"


def test_bad_assertion_and_copied_model_shapes_are_controlled_refusals():
    source = history([1] * 18)
    assert analyze(replace(source, complete="no"))["reason"] == "SCOPE_INCOMPLETE"
    assert analyze(replace(source, retention_complete=1))["reason"] == "SCOPE_INCOMPLETE"
    malformed = source.candidates[0].model_copy(update={"content": {"bad": "shape"}})
    assert analyze(replace(source, candidates=(malformed, *source.candidates[1:])))["reason"] == "INPUT_INVALID"
    nested = source.candidates[0].content.model_copy(update={"sections": [{"bad": "section"}]})
    malformed_nested = source.candidates[0].model_copy(update={"content": nested})
    assert analyze(replace(source, candidates=(malformed_nested, *source.candidates[1:])))["reason"] == "LINEAGE_INVALID"
    mixed_version = source.candidates[0].model_copy(update={"version": "2"})
    assert analyze(replace(source, candidates=(mixed_version, *source.candidates[1:])))["reason"] == "INPUT_INVALID"


def test_visible_oversized_first_candidate_refuses_before_content_serialization(monkeypatch):
    source = history([0] * 18)
    oversized = report(0, 501, version=2, created_offset=timedelta(hours=1))
    future = report(0, 501, version=2, created_offset=timedelta(hours=20))
    calls = []
    original_dump = ReportContent.model_dump

    def observed_dump(self, *args, **kwargs):
        calls.append(max(len(section.records) for section in self.sections))
        return original_dump(self, *args, **kwargs)

    monkeypatch.setattr(ReportContent, "model_dump", observed_dump)
    answer = analyze(replace(source, candidates=(oversized, *source.candidates)))
    assert answer["outcome"] == "ABSTAINED" and answer["reason"] == "SCOPE_INCOMPLETE"
    assert calls == []  # The 501-record candidate is rejected before immutable-byte comparison.
    assert analyze(replace(source, candidates=(future, *source.candidates)))["outcome"] == "READY"
    assert all(size <= 500 for size in calls)


def test_stale_and_late_source_fail_closed_without_mutating_inputs():
    source = history([0] * 18)
    before = tuple(r.model_dump_json() for r in source.candidates)
    assert analyze(source)["outcome"] == "READY"
    assert tuple(r.model_dump_json() for r in source.candidates) == before
    stale = replace(source, run_as_of=source.run_as_of + timedelta(days=2))
    answer = analyze(stale)
    assert answer["outcome"] == "ABSTAINED" and answer["reason"] == "STALE"
    assert "forecast_count" not in answer and "signals" not in answer
    late = report(6, 0, version=2, created_offset=timedelta(hours=12))
    revised = replace(source, candidates=source.candidates + (late,))
    assert analyze(revised)["outcome"] in {"READY", "ABSTAINED"}
    assert tuple(r.model_dump_json() for r in source.candidates) == before
    assert tuple(r.model_dump_json() for r in revised.candidates[:-1]) == before
