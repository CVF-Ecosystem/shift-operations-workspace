"""Cross-backend Report ledger parity, immutability and successor rollback
(SPEC R25). Mirrors test_handover_ledger_parity.py's proof pattern."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.domain import models as domain_models
from operations_domain.models import Report, ReportContent, ReportSection, ReportSourceRef, Shift
from workspace_api.infrastructure.repository import InMemoryLedger


def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'report_parity.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "report_parity.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _content(digest="a" * 64) -> ReportContent:
    order = ("operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers")
    return ReportContent(
        sections=[ReportSection(section_type=s, records=[]) for s in order],
        source_manifest=[], snapshot_digest=digest,
    )


def _report(shift_id, **kw) -> Report:
    kw.setdefault("generated_from_cutoff", datetime.now(timezone.utc))
    kw.setdefault("content", _content())
    return Report(shift_id=shift_id, **kw)


# --- duplicate/conflict refusal, no partial write ---------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_report_id_rejected_with_no_partial_write(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    duplicate = report.model_copy(deep=True)
    with pytest.raises(ValueError, match="duplicate report_id"):
        ledger.add_report(duplicate)
    assert ledger.get_report(report.report_id).report_id == report.report_id


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_shift_type_version_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    first = _report(shift.shift_id, is_current=True)
    ledger.add_report(first)

    second = _report(shift.shift_id, is_current=False, version=1)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.add_report(second)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_second_current_report_for_same_shift_type_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    first = _report(shift.shift_id)
    ledger.add_report(first)

    second = _report(shift.shift_id, version=2)
    with pytest.raises(ValueError, match="current report already exists"):
        ledger.add_report(second)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_get_current_report_returns_none_when_absent(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    assert ledger.get_current_report(shift.shift_id, "END_SHIFT") is None


def test_sql_backend_never_leaks_raw_integrity_error(tmp_path):
    from sqlalchemy.exc import IntegrityError

    ledger = _sql_ledger(tmp_path)
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    duplicate = report.model_copy(deep=True)
    try:
        ledger.add_report(duplicate)
    except IntegrityError:
        pytest.fail("raw SQLAlchemy IntegrityError escaped add_report")
    except ValueError:
        pass


# --- R11: immutable snapshot fields on put ----------------------------------

def _digest_of(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _tampered_same_digest_content(original: ReportContent) -> ReportContent:
    """F2: sections differ from the persisted row but snapshot_digest was NOT
    recomputed - proves put_report compares content sub-fields, not just the
    aggregate digest. Kept internally valid (F5 record/manifest match + real
    per-record source_digest)."""
    task_id = str(uuid4())
    task_record = {
        "record_type": "Task", "record_id": task_id, "shift_id": str(uuid4()), "title": "tampered",
        "description": None, "status": "OPEN", "owner_id": None, "due_at": None, "risk_class": "R1",
        "state": "CONFIRMED", "version": 1, "created_at": "2026-01-01T00:00:00Z", "evidence": [],
    }
    order = ("operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers")
    sections = [ReportSection(section_type=s, records=[task_record] if s == "tasks" else []) for s in order]
    manifest = [ReportSourceRef(record_type="Task", record_id=task_id, source_version=1, source_digest=_digest_of(task_record))]
    return ReportContent(sections=sections, source_manifest=manifest, snapshot_digest=original.snapshot_digest)


_IMMUTABLE_FIELD_MUTATIONS = {
    "shift_id": lambda r, ledger: setattr(r, "shift_id", _shift(ledger).shift_id),
    "version": lambda r, ledger: setattr(r, "version", 99),
    "generated_from_cutoff": lambda r, ledger: setattr(r, "generated_from_cutoff", r.generated_from_cutoff + timedelta(days=1)),
    "content_digest": lambda r, ledger: setattr(r, "content", _content(digest="f" * 64)),
    "created_at": lambda r, ledger: setattr(r, "created_at", r.created_at + timedelta(days=1)),
    "is_current": lambda r, ledger: setattr(r, "is_current", not r.is_current),
    "sections_same_digest": lambda r, ledger: setattr(r, "content", _tampered_same_digest_content(r.content)),
}


# is_current is lifecycle-owned (F2/F3): distinct rejection message.
_EXPECTED_REJECTION_MESSAGE = {"is_current": "is_current is lifecycle-owned"}


@pytest.mark.parametrize("field", sorted(_IMMUTABLE_FIELD_MUTATIONS))
@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_report_rejects_immutable_field_mutation(tmp_path, name, field):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    mutated = ledger.get_report(report.report_id)
    _IMMUTABLE_FIELD_MUTATIONS[field](mutated, ledger)
    expected = _EXPECTED_REJECTION_MESSAGE.get(field, "report snapshot is immutable")
    with pytest.raises(ValueError, match=expected):
        ledger.put_report(mutated)

    unchanged = ledger.get_report(report.report_id)
    assert unchanged.content.snapshot_digest == report.content.snapshot_digest
    assert unchanged.version == report.version


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_report_allows_lifecycle_only_change(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    reviewed = ledger.get_report(report.report_id)
    reviewed.status = "IN_REVIEW"
    stored = ledger.put_report(reviewed)
    assert str(stored.status) == "IN_REVIEW"

    fetched = ledger.get_report(report.report_id)
    assert str(fetched.status) == "IN_REVIEW"


# --- R12: atomic successor generation ----------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_report_successor_atomically_flips_current(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    successor = _report(shift.shift_id, version=2, content=_content(digest="b" * 64))
    stored = ledger.create_report_successor(report.report_id, successor)
    assert stored.is_current is True
    assert stored.version == 2

    predecessor = ledger.get_report(report.report_id)
    assert predecessor.is_current is False
    assert predecessor.version == 1  # never rewritten

    history = ledger.list_reports_for_shift(shift.shift_id)
    assert [r.version for r in history] == [2, 1]

    current = ledger.get_current_report(shift.shift_id, "END_SHIFT")
    assert current.report_id == successor.report_id


# F3: successor must be a fresh current DRAFT; every other combo rejected.
_INVALID_SUCCESSOR_COMBOS = {
    "approved_non_current": dict(status="APPROVED", is_current=False),
    "approved_current": dict(status="APPROVED", is_current=True),
    "draft_non_current": dict(status="DRAFT", is_current=False),
    "frozen_current": dict(status="FROZEN", is_current=True),
}


@pytest.mark.parametrize("combo", sorted(_INVALID_SUCCESSOR_COMBOS))
@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_report_successor_rejects_invalid_status_current_combo(tmp_path, name, combo):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    bad_successor = _report(shift.shift_id, version=2, content=_content(digest="b" * 64), **_INVALID_SUCCESSOR_COMBOS[combo])
    with pytest.raises(ValueError, match="must be"):
        ledger.create_report_successor(report.report_id, bad_successor)

    # no-partial-write rollback: predecessor untouched, successor never inserted.
    predecessor = ledger.get_report(report.report_id)
    assert predecessor.is_current is True
    assert ledger.get_current_report(shift.shift_id, "END_SHIFT").report_id == report.report_id
    history = ledger.list_reports_for_shift(shift.shift_id)
    assert [r.version for r in history] == [1]


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_report_successor_rejects_non_current_predecessor(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)
    successor = _report(shift.shift_id, version=2, content=_content(digest="b" * 64))
    ledger.create_report_successor(report.report_id, successor)

    third = _report(shift.shift_id, version=3, content=_content(digest="c" * 64))
    with pytest.raises(ValueError, match="not current"):
        ledger.create_report_successor(report.report_id, third)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_report_successor_rejects_wrong_version(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)

    wrong_version = _report(shift.shift_id, version=5, content=_content(digest="b" * 64))
    with pytest.raises(ValueError, match="successor version must be exactly"):
        ledger.create_report_successor(report.report_id, wrong_version)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_history_ordering_is_version_desc(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    report = _report(shift.shift_id)
    ledger.add_report(report)
    for v in range(2, 5):
        prev_current = ledger.get_current_report(shift.shift_id, "END_SHIFT")
        successor = _report(shift.shift_id, version=v, content=_content(digest=f"{v}" * 64))
        ledger.create_report_successor(prev_current.report_id, successor)

    history = ledger.list_reports_for_shift(shift.shift_id)
    assert [r.version for r in history] == [4, 3, 2, 1]


# --- reconnect proof (SQL only) ----------------------------------------------

def test_sql_reconnect_reads_persisted_report(tmp_path):
    db_path = tmp_path / "reconnect.sqlite3"
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    ledger1 = SqlLedger(str(db_path), models=domain_models, engine=engine)
    shift = _shift(ledger1)
    report = _report(shift.shift_id)
    ledger1.add_report(report)

    # Fresh SqlLedger/engine against the same file - proves persistence
    # survives a new connection, not just the same in-process object.
    engine2 = make_engine(f"sqlite:///{db_path}")
    ledger2 = SqlLedger(str(db_path), models=domain_models, engine=engine2)
    fetched = ledger2.get_report(report.report_id)
    assert fetched.content.snapshot_digest == report.content.snapshot_digest
    assert fetched.shift_id == shift.shift_id
