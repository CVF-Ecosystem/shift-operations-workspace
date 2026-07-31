"""Atomic Report+Shift freeze, idempotent frozen-read integrity, rollback
(SPEC R20-R21). Complements test_freeze_invariant.py's cross-record coverage
with Report-specific scenarios."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application import approval_service
from workspace_api.application.handover_service import HandoverService
from workspace_api.application.report_service import ReportService
from workspace_api.application.shift_service import ShiftService
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import User
from operations_domain.models import ReportStatus, Shift, ShiftStatus
from workspace_api.infrastructure.repository import InMemoryLedger

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")
_RECEIVING_SUPERVISOR = Principal(user_id="sup2", role="shift_supervisor")


def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'report_freeze.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "report_freeze.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _closed_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    ledger.close_shift(shift.shift_id)
    return ledger.get_shift(shift.shift_id)


def _ready_handover(ledger, shift):
    now = datetime.now(timezone.utc)
    dest = Shift(name="Next", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(dest)
    svc = HandoverService(ledger)
    handover = svc.create(shift.shift_id, dest.shift_id, _OPERATOR)
    handover = svc.review(handover.handover_id, _SUPERVISOR)
    return svc.acknowledge(handover.handover_id, _RECEIVING_SUPERVISOR)


def _approved_report(ledger, shift, approver_id="sup3"):
    svc = ReportService(ledger)
    report = svc.generate(shift.shift_id, _OPERATOR)
    report = svc.submit_review(report.report_id, _OPERATOR)
    ledger.add_user(User(user_id=approver_id, username=approver_id, password_hash="x", role="shift_supervisor"))
    approval_service.create_approval_receipt(
        ledger, Principal(user_id=approver_id, role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    return svc.approve(report.report_id, _SUPERVISOR)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_freeze_atomically_transitions_report_and_shift(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    _ready_handover(ledger, shift)
    report = _approved_report(ledger, shift)

    frozen_shift = ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR)
    assert frozen_shift.status == ShiftStatus.FROZEN

    frozen_report = ledger.get_report(report.report_id)
    assert frozen_report.status == ReportStatus.FROZEN
    assert frozen_report.is_current is True

    report_actions = [e.action if hasattr(e, "action") else e["action"] for e in ledger.audit_entries_for(str(report.report_id))]
    assert "report.freeze" in report_actions


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_freeze_refused_with_zero_current_reports(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    _ready_handover(ledger, shift)

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR)
    assert exc.value.control == "freeze"
    assert "report" in str(exc.value).lower()
    assert ledger.get_shift(shift.shift_id).status == ShiftStatus.CLOSED  # no partial mutation


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_freeze_refused_when_report_not_approved(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    _ready_handover(ledger, shift)
    ReportService(ledger).generate(shift.shift_id, _OPERATOR)  # still DRAFT

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR)
    assert exc.value.control == "freeze"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_idempotent_frozen_read_requires_frozen_report(tmp_path, name):
    """SPEC R21: an already-FROZEN shift is idempotent only if its paired
    current report is also FROZEN and unambiguous."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    _ready_handover(ledger, shift)
    report = _approved_report(ledger, shift)
    ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR)

    again = ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR)  # idempotent success
    assert again.status == ShiftStatus.FROZEN
    assert ledger.get_report(report.report_id).status == ReportStatus.FROZEN


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_freeze_rejects_stale_approved_report(tmp_path, name):
    """A source mutation between approval and freeze invalidates the
    approved snapshot - freeze must refuse, not silently freeze stale truth."""
    from operations_domain.models import Task

    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    _ready_handover(ledger, shift)
    _approved_report(ledger, shift)

    # A new task appears after approval, invalidating the approved snapshot.
    ledger.add_task(Task(shift_id=shift.shift_id, title="Late addition"))

    with pytest.raises(CvfDenied) as exc:
        ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR)
    assert exc.value.control == "freeze"
    assert ledger.get_shift(shift.shift_id).status == ShiftStatus.CLOSED


# --- F5: SPEC R2/R4 record/manifest exact-set-equality + field-set closure -

def _task_record(record_id, created_at="2026-01-01T00:00:00Z", title="t", evidence=()):
    return {
        "record_type": "Task", "record_id": record_id, "shift_id": str(uuid4()),
        "title": title, "description": None, "status": "OPEN", "owner_id": None, "due_at": None,
        "risk_class": "R1", "state": "CONFIRMED", "version": 1,
        "created_at": created_at, "evidence": list(evidence),
    }


def _evidence_item(evidence_id, source_type="doc", source_id="1", sha256=None):
    return {"evidence_id": evidence_id, "source_type": source_type, "source_id": source_id, "sha256": sha256}


def _digest_of(record: dict) -> str:
    """Matches operations_domain.report_models._recompute_record_digest."""
    import hashlib
    import json
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _six_sections(tasks_records=()):
    from operations_domain.models import ReportSection

    order = ("operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers")
    return [ReportSection(section_type=s, records=list(tasks_records) if s == "tasks" else []) for s in order]


def test_record_without_matching_manifest_entry_rejected():
    """The manifest must be the EXACT set of records, not a subset."""
    from operations_domain.models import ReportContent

    with pytest.raises(Exception):
        ReportContent(
            sections=_six_sections([_task_record(str(uuid4()))]),
            source_manifest=[], snapshot_digest="b" * 64,
        )


def test_manifest_entry_without_matching_record_rejected():
    """The manifest must never be a superset of the records either."""
    from operations_domain.models import ReportContent, ReportSourceRef

    with pytest.raises(Exception):
        ReportContent(
            sections=_six_sections(),
            source_manifest=[
                ReportSourceRef(record_type="Task", record_id=uuid4(), source_version=1, source_digest="a" * 64)
            ],
            snapshot_digest="b" * 64,
        )


def test_manifest_order_must_match_record_order_within_section():
    """Two Task records (distinct created_at) with reversed manifest order
    relative to the records' own order must be rejected."""
    from operations_domain.models import ReportContent, ReportSourceRef

    id_a, id_b = str(uuid4()), str(uuid4())
    record_a = _task_record(id_a, created_at="2026-01-01T00:00:00Z")
    record_b = _task_record(id_b, created_at="2026-01-02T00:00:00Z")
    sections = _six_sections([record_a, record_b])
    reversed_manifest = [
        ReportSourceRef(record_type="Task", record_id=id_b, source_version=1, source_digest=_digest_of(record_b)),
        ReportSourceRef(record_type="Task", record_id=id_a, source_version=1, source_digest=_digest_of(record_a)),
    ]
    with pytest.raises(Exception):
        ReportContent(sections=sections, source_manifest=reversed_manifest, snapshot_digest="b" * 64)

    forward_manifest = list(reversed(reversed_manifest))
    content = ReportContent(sections=sections, source_manifest=forward_manifest, snapshot_digest="b" * 64)
    assert len(content.source_manifest) == 2


def test_record_with_mismatched_record_type_for_its_section_rejected():
    from operations_domain.models import ReportSection

    bad = _task_record(str(uuid4()))
    bad["record_type"] = "Incident"
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[bad])


def test_record_with_wrong_field_set_rejected():
    """SPEC R2: a record's shape is pinned to its record_type's exact field set."""
    from operations_domain.models import ReportSection

    missing_field = _task_record(str(uuid4()))
    del missing_field["title"]
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[missing_field])

    extra_field = _task_record(str(uuid4()))
    extra_field["bogus_extra"] = "x"
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[extra_field])


def test_record_with_invalid_record_id_rejected():
    from operations_domain.models import ReportSection

    empty_id = _task_record("")
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[empty_id])

    non_string_id = _task_record(str(uuid4()))
    non_string_id["record_id"] = 12345
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[non_string_id])


# --- Finding 1 (second repair): no over-rejection, evidence R7 order -------

def _correction_record(record_id, previous_version, new_version):
    return {
        "record_type": "Correction", "record_id": record_id,
        "target_record_type": "Task", "target_record_id": str(uuid4()),
        "reason": "fix", "requested_by": "op1",
        "previous_version": previous_version, "new_version": new_version,
        "created_at": "2026-01-01T00:00:00Z",
    }


def test_empty_title_and_sorted_evidence_are_accepted():
    """Task.title is a plain `str` with no min_length domain-wide, and
    correctly R7-ordered evidence must remain accepted."""
    from operations_domain.models import ReportSection

    first, second = _evidence_item("1" * 8 + "-1111-1111-1111-" + "1" * 12), _evidence_item("2" * 8 + "-2222-2222-2222-" + "2" * 12)
    record = _task_record(str(uuid4()), title="", evidence=[first, second])
    ReportSection(section_type="tasks", records=[record])


def test_correction_zero_to_one_is_accepted():
    """DB CHECK is only `new_version > previous_version`, no lower bound."""
    from operations_domain.models import ReportSection

    record = _correction_record(str(uuid4()), previous_version=0, new_version=1)
    ReportSection(section_type="corrections", records=[record])


def test_correction_bad_order_and_reversed_evidence_rejected():
    from operations_domain.models import ReportSection

    with pytest.raises(Exception):
        ReportSection(section_type="corrections", records=[
            _correction_record(str(uuid4()), previous_version=2, new_version=2)
        ])

    first, second = _evidence_item("1" * 8 + "-1111-1111-1111-" + "1" * 12), _evidence_item("2" * 8 + "-2222-2222-2222-" + "2" * 12)
    with pytest.raises(Exception):
        ReportSection(section_type="tasks", records=[_task_record(str(uuid4()), evidence=[second, first])])
