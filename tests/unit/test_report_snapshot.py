"""Placeholder smoke import + ledger round-trip + snapshot engine tests for
Report domain (P2R build in progress)."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

_TASK_ID = str(uuid4())


def _digest_of(record: dict) -> str:
    """Matches report_models._recompute_record_digest - a real digest."""
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _task_record(record_id=None):
    return {
        "record_type": "Task", "record_id": record_id or _TASK_ID, "shift_id": str(uuid4()),
        "title": "t", "description": None, "status": "OPEN", "owner_id": None, "due_at": None,
        "risk_class": "R1", "state": "CONFIRMED", "version": 1,
        "created_at": "2026-01-01T00:00:00Z", "evidence": [],
    }


def _empty_sections(overrides=None):
    from operations_domain.models import ReportSection

    overrides = overrides or {}
    order = ("operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers")
    return [ReportSection(section_type=s, records=overrides.get(s, [])) for s in order]


def _content(record_id=None):
    from operations_domain.models import ReportContent, ReportSourceRef

    rid = record_id or _TASK_ID
    record = _task_record(rid)
    return ReportContent(
        sections=_empty_sections({"tasks": [record]}),
        source_manifest=[
            ReportSourceRef(record_type="Task", record_id=rid, source_version=1, source_digest=_digest_of(record))
        ],
        snapshot_digest="b" * 64,
    )


def test_report_import_smoke():
    from operations_domain.models import Report, ReportContent, ReportSection, ReportSourceRef, ReportStatus, ReportType
    from operations_domain.lifecycle import assert_report_transition
    from workspace_api.domain.models import Report as R2
    from operations_ledger.tables import reports

    assert Report is R2
    assert {c.name for c in reports.c} >= {
        "report_id", "shift_id", "report_type", "version", "status",
        "content", "generated_from_cutoff", "created_at", "is_current",
    }


def test_in_memory_ledger_report_round_trip():
    from operations_domain.models import Report, Shift
    from workspace_api.infrastructure.repository import InMemoryLedger

    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)

    report = Report(shift_id=shift.shift_id, generated_from_cutoff=now, content=_content())
    stored = ledger.add_report(report)
    assert stored.report_id == report.report_id

    fetched = ledger.get_report(report.report_id)
    assert fetched.content.snapshot_digest == "b" * 64

    current = ledger.get_current_report(shift.shift_id, "END_SHIFT")
    assert current.report_id == report.report_id

    # duplicate current rejected
    try:
        ledger.add_report(Report(shift_id=shift.shift_id, generated_from_cutoff=now, content=_content()))
        assert False, "expected ValueError"
    except ValueError:
        pass

    # successor
    successor = Report(
        shift_id=shift.shift_id, version=2, generated_from_cutoff=now, content=_content(str(uuid4())),
    )
    ledger.create_report_successor(report.report_id, successor)
    assert ledger.get_report(report.report_id).is_current is False
    assert ledger.get_current_report(shift.shift_id, "END_SHIFT").report_id == successor.report_id

    history = ledger.list_reports_for_shift(shift.shift_id)
    assert [r.version for r in history] == [2, 1]


def test_build_snapshot_deterministic_and_matches_manual_digest():
    from workspace_api.application import report_snapshot

    shift_id = uuid4()
    content1 = report_snapshot.build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[], customer_requests=[], incidents=[], handovers=[],
    )
    content2 = report_snapshot.build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[], customer_requests=[], incidents=[], handovers=[],
    )
    assert content1.snapshot_digest == content2.snapshot_digest
    assert len(content1.snapshot_digest) == 64
    assert content1.sections[0].section_type == "operational_events"
    assert [s.section_type for s in content1.sections] == [
        "operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers",
    ]

    # Different shift_id must change the digest (shift_id is part of the hash input).
    content3 = report_snapshot.build_snapshot(
        shift_id=uuid4(), events=[], corrections=[], tasks=[], customer_requests=[], incidents=[], handovers=[],
    )
    assert content3.snapshot_digest != content1.snapshot_digest


def test_build_snapshot_with_task_produces_source_manifest():
    from workspace_api.application import report_snapshot
    from operations_domain.models import Task

    shift_id = uuid4()
    now = datetime.now(timezone.utc)
    task = Task(shift_id=shift_id, title="Check pumps", created_at=now)
    content = report_snapshot.build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[task], customer_requests=[], incidents=[], handovers=[],
    )
    tasks_section = next(s for s in content.sections if s.section_type == "tasks")
    assert len(tasks_section.records) == 1
    assert tasks_section.records[0]["record_id"] == str(task.task_id)
    assert len(content.source_manifest) == 1
    assert content.source_manifest[0].record_type == "Task"
    assert content.source_manifest[0].source_version == 1


def test_filter_eligible_events_and_corrections():
    from workspace_api.application import report_snapshot
    from operations_domain.models import OperationalEvent, Correction, DataState

    shift_id = uuid4()
    confirmed = OperationalEvent(shift_id=shift_id, event_type="x", title="a", state=DataState.CONFIRMED)
    raw = OperationalEvent(shift_id=shift_id, event_type="x", title="b", state=DataState.RAW)
    eligible = report_snapshot.filter_eligible_events([confirmed, raw])
    assert eligible == [confirmed]

    corr_for_confirmed = Correction(
        record_type="OperationalEvent", record_id=confirmed.event_id, reason="fix",
        requested_by="op1", previous_version=1, new_version=2,
    )
    corr_for_other = Correction(
        record_type="OperationalEvent", record_id=uuid4(), reason="fix",
        requested_by="op1", previous_version=1, new_version=2,
    )
    filtered = report_snapshot.filter_corrections_for_events(
        [corr_for_confirmed, corr_for_other], {confirmed.event_id}
    )
    assert filtered == [corr_for_confirmed]


def test_sql_ledger_report_round_trip(tmp_path):
    from operations_domain.models import Shift, Report
    from operations_ledger.sql_ledger import SqlLedger, make_engine
    from operations_ledger.tables import metadata
    import workspace_api.domain.models as domain_models

    db_path = tmp_path / "reports.sqlite3"
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    ledger = SqlLedger(str(db_path), models=domain_models, engine=engine)

    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)

    report = Report(shift_id=shift.shift_id, generated_from_cutoff=now, content=_content())
    ledger.add_report(report)

    fetched = ledger.get_report(report.report_id)
    assert fetched.content.snapshot_digest == "b" * 64
    assert fetched.is_current is True

    current = ledger.get_current_report(shift.shift_id, "END_SHIFT")
    assert current.report_id == report.report_id

    successor = Report(
        shift_id=shift.shift_id, version=2, generated_from_cutoff=now, content=_content(str(uuid4())),
    )
    ledger.create_report_successor(report.report_id, successor)
    assert ledger.get_report(report.report_id).is_current is False
    assert ledger.get_current_report(shift.shift_id, "END_SHIFT").report_id == successor.report_id

    history = ledger.list_reports_for_shift(shift.shift_id)
    assert [r.version for r in history] == [2, 1]


def test_freeze_input_openapi_marks_legacy_fields_deprecated():
    from workspace_api.main import app

    schema = app.openapi()
    freeze_schema = schema["components"]["schemas"]["FreezeInput"]
    assert freeze_schema.get("additionalProperties") is False
    assert freeze_schema["properties"]["override_unimplemented_prerequisites"].get("deprecated") is True
    assert freeze_schema["properties"]["override_reason"].get("deprecated") is True


# --- F5 (repair): SPEC R1-R4 strict canonical model validation --------------

def test_report_and_sub_models_forbid_extra_fields():
    from operations_domain.models import Report, ReportContent, ReportSection, ReportSourceRef

    good = _content()
    with pytest.raises(Exception):
        Report(shift_id=uuid4(), generated_from_cutoff=datetime.now(timezone.utc), content=good, bogus="x")
    with pytest.raises(Exception):
        ReportContent(sections=good.sections, source_manifest=good.source_manifest, snapshot_digest="b" * 64, bogus="x")
    with pytest.raises(Exception):
        ReportSourceRef(record_type="Task", record_id=uuid4(), source_version=1, source_digest="a" * 64, bogus="x")
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[], bogus="x")


def test_report_content_schema_version_must_be_exactly_one_point_zero():
    from operations_domain.models import ReportContent

    good = _content()
    assert good.schema_version == "1.0"
    with pytest.raises(Exception):
        ReportContent(schema_version="1.1", sections=good.sections, source_manifest=good.source_manifest, snapshot_digest="b" * 64)


@pytest.mark.parametrize("bad_digest", ["A" * 64, "g" * 64, "a" * 63, "a" * 65, ""])
def test_digest_fields_reject_non_lowercase_64_hex(bad_digest):
    from operations_domain.models import ReportContent, ReportSourceRef

    good = _content()
    with pytest.raises(Exception):
        ReportContent(sections=good.sections, source_manifest=good.source_manifest, snapshot_digest=bad_digest)
    with pytest.raises(Exception):
        ReportSourceRef(record_type="Task", record_id=uuid4(), source_version=1, source_digest=bad_digest)


def test_source_ref_and_section_reject_unknown_type():
    from operations_domain.models import ReportSection, ReportSourceRef

    with pytest.raises(Exception):
        ReportSourceRef(record_type="Bogus", record_id=uuid4(), source_version=1, source_digest="a" * 64)
    with pytest.raises(Exception):
        ReportSection(section_type="bogus_section", records=[])


@pytest.mark.parametrize("record_type", ["OperationalEvent", "Task", "Incident", "Handover"])
def test_versioned_record_types_require_source_version_gte_one(record_type):
    from operations_domain.models import ReportSourceRef

    with pytest.raises(Exception):
        ReportSourceRef(record_type=record_type, record_id=uuid4(), source_version=None, source_digest="a" * 64)
    with pytest.raises(Exception):
        ReportSourceRef(record_type=record_type, record_id=uuid4(), source_version=0, source_digest="a" * 64)
    assert ReportSourceRef(record_type=record_type, record_id=uuid4(), source_version=1, source_digest="a" * 64).source_version == 1


@pytest.mark.parametrize("record_type", ["Correction", "CustomerRequest"])
def test_unversioned_record_types_require_null_source_version(record_type):
    from operations_domain.models import ReportSourceRef

    with pytest.raises(Exception):
        ReportSourceRef(record_type=record_type, record_id=uuid4(), source_version=1, source_digest="a" * 64)
    assert ReportSourceRef(record_type=record_type, record_id=uuid4(), source_version=None, source_digest="a" * 64).source_version is None


def test_content_rejects_wrong_section_count_and_duplicate_manifest():
    from operations_domain.models import ReportContent

    good = _content()
    with pytest.raises(Exception):
        ReportContent(sections=list(reversed(good.sections)), source_manifest=good.source_manifest, snapshot_digest="b" * 64)
    with pytest.raises(Exception):
        ReportContent(sections=good.sections[:5], source_manifest=good.source_manifest, snapshot_digest="b" * 64)
    dup_ref = good.source_manifest[0]
    with pytest.raises(Exception):
        ReportContent(sections=good.sections, source_manifest=[dup_ref, dup_ref], snapshot_digest="b" * 64)


def test_content_accepts_exact_records_manifest_match():
    good = _content()
    assert len(good.source_manifest) == 1
    tasks_section = good.sections[2]
    assert tasks_section.section_type == "tasks" and tasks_section.records[0]["record_id"] == str(good.source_manifest[0].record_id)


# F5 (repair) record/manifest exact-set-equality and per-record-type shape
# closure tests live in tests/cvf/test_report_freeze.py (file-size budget).
