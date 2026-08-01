"""Report golden vertical: model identity/serialization, lifecycle guards,
ledger parity on both backends, generation eligibility, snapshot
revalidation and successor generation (SPEC R1-R13). Approval quorum is in
test_report_approval.py; freeze integration in test_report_freeze.py."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata
from workspace_api.application.report_service import ReportService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import Report as WorkspaceReport
from operations_domain.models import Report, ReportStatus, Shift, Task
from operations_domain.lifecycle import assert_report_transition
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")

def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'reports.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "reports.sqlite3"), models=domain_models, engine=engine)

def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]

def _closed_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    if ledger.get_user_by_id("op1") is None:
        ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))
    ledger.close_shift(shift.shift_id); return ledger.get_shift(shift.shift_id)

@pytest.fixture
def client(request):
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)

# --- AC-01/02: model identity/serialization, R2-R4 public/content shapes ---

def test_report_model_identity_across_shims():
    assert Report is WorkspaceReport

def test_report_default_type_and_version():
    from workspace_api.application.report_snapshot import build_snapshot

    shift_id = __import__("uuid").uuid4()
    content = build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[], customer_requests=[], incidents=[], handovers=[],
    )
    r = Report(shift_id=shift_id, generated_from_cutoff=datetime.now(timezone.utc), content=content)
    assert str(r.report_type) == "END_SHIFT"
    assert r.version == 1
    assert r.is_current is True
    assert r.status == ReportStatus.DRAFT

# --- AC-05/06: R10 lifecycle/current guards -------------------------------

def test_lifecycle_forward_only_and_frozen_terminal():
    assert_report_transition(ReportStatus.DRAFT, ReportStatus.IN_REVIEW)
    assert_report_transition(ReportStatus.IN_REVIEW, ReportStatus.APPROVED)
    assert_report_transition(ReportStatus.APPROVED, ReportStatus.FROZEN)
    with pytest.raises(ValueError): assert_report_transition(ReportStatus.FROZEN, ReportStatus.DRAFT)
    with pytest.raises(ValueError): assert_report_transition(ReportStatus.DRAFT, ReportStatus.APPROVED)

# --- AC-01: generation eligibility (R5) ------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_generate_requires_closed_shift(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))

    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    assert exc.value.http_status == 409

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_generate_requires_permission(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    viewer = Principal(user_id="v1", role="viewer")
    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).generate(shift.shift_id, viewer)
    assert exc.value.control == "permission"

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_generate_unknown_shift_is_404(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    with pytest.raises(KeyError):
        ReportService(ledger).generate(__import__("uuid").uuid4(), _OPERATOR)

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_generate_produces_current_draft_with_audit(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    assert report.status == ReportStatus.DRAFT
    assert report.is_current is True
    assert report.version == 1
    entries = ledger.audit_entries_for(str(report.report_id))
    actions = [_action_of(e) for e in entries]
    assert "report.generate" in actions

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_generate_twice_without_successor_is_409(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    assert exc.value.http_status == 409

def _action_of(entry): return entry.action if hasattr(entry, "action") else entry["action"]

# --- AC-09/10: submit-review (R15) -----------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_submit_review_requires_current_draft(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    reviewed = ReportService(ledger).submit_review(
        report.report_id, _OPERATOR, expected_version=report.version, expected_status=report.status
    )
    assert reviewed.status == ReportStatus.IN_REVIEW

    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).submit_review(
            report.report_id, _OPERATOR,
            expected_version=reviewed.version, expected_status=reviewed.status,
        )
    assert exc.value.http_status == 409

# --- AC-19/20: successor generation (R12) ----------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_successor_generation_from_draft_needs_no_reason(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    successor = ReportService(ledger).create_successor(
        report.report_id, _OPERATOR, expected_version=report.version, expected_status=report.status
    )
    assert successor.version == 2
    assert successor.is_current is True
    predecessor = ledger.get_report(report.report_id)
    assert predecessor.is_current is False
    assert predecessor.version == 1  # immutable version never changes

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_successor_generation_from_frozen_report_refused(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    report = ledger.get_report(report.report_id)
    report.status = ReportStatus.FROZEN
    # bypass service to force a FROZEN row directly for the guard test
    if hasattr(ledger, "reports"):
        ledger.reports[report.report_id] = report
    else:
        from sqlalchemy import update
        from operations_ledger.tables import reports as reports_table
        with ledger.transaction() as unit:
            unit.execute(update(reports_table).where(reports_table.c.report_id == report.report_id).values(status="FROZEN"))

    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).create_successor(
            report.report_id, _OPERATOR,
            expected_version=report.version, expected_status=ReportStatus.FROZEN,
        )
    assert exc.value.http_status == 409

# --- AC-11/12: R11 immutability ---------------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_report_rejects_immutable_field_change(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    mutated = ledger.get_report(report.report_id)
    mutated.version = 99
    with pytest.raises(ValueError):
        ledger.put_report(mutated)

# --- Stale-snapshot revalidation (R9) ---------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_submit_review_refuses_when_snapshot_stale(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _closed_shift(ledger)
    task = Task(shift_id=shift.shift_id, title="Inspect crane")
    ledger.add_task(task)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)

    another_task = Task(shift_id=shift.shift_id, title="New task appears")
    ledger.add_task(another_task)

    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).submit_review(
            report.report_id, _OPERATOR, expected_version=report.version, expected_status=report.status
        )
    assert exc.value.http_status == 409
    assert "stale" in str(exc.value).lower()

# --- HTTP-level (AC-23/24: R26 endpoints) -----------------------------------

def test_http_generate_get_and_list(client):
    ledger, http = client
    shift = _closed_shift(ledger)

    resp = http.post("/reports", json={"shift_id": str(shift.shift_id)}, headers=auth_headers("op1", "operator"))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["report_type"] == "END_SHIFT"
    assert body["status"] == "DRAFT"
    assert "content" not in body
    assert body["sections"][0]["section_type"] == "operational_events"

    report_id = body["report_id"]
    get_resp = http.get(f"/reports/{report_id}", headers=auth_headers("op1", "operator"))
    assert get_resp.status_code == 200

    list_resp = http.get(f"/reports?shift_id={shift.shift_id}", headers=auth_headers("op1", "operator"))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

def test_http_generate_requires_auth(client):
    ledger, http = client
    shift = _closed_shift(ledger)
    resp = http.post("/reports", json={"shift_id": str(shift.shift_id)})
    assert resp.status_code == 401

def test_http_generate_rejects_extra_fields(client):
    ledger, http = client
    shift = _closed_shift(ledger)
    resp = http.post(
        "/reports",
        json={"shift_id": str(shift.shift_id), "status": "APPROVED"},
        headers=auth_headers("op1", "operator"),
    )
    assert resp.status_code == 422

def test_http_get_missing_report_is_404(client):
    _, http = client
    resp = http.get(f"/reports/{__import__('uuid').uuid4()}", headers=auth_headers("op1", "operator"))
    assert resp.status_code == 404

# --- F4 repair: parent-shift invariant surfaced correctly over HTTP --------

def test_http_generate_for_unknown_shift_is_404_not_500(client):
    _, http = client
    resp = http.post(
        "/reports", json={"shift_id": str(__import__("uuid").uuid4())},
        headers=auth_headers("op1", "operator"),
    )
    assert resp.status_code == 404

def test_http_list_current_maps_ambiguous_current_to_409(client, monkeypatch):
    """F7: ambiguous-current ValueError must be a controlled 409, not 500."""
    ledger, http = client
    shift = _closed_shift(ledger)

    def _boom(*a, **kw):
        raise ValueError("ambiguous current report: 2 current rows found")

    monkeypatch.setattr(ledger, "get_current_report", _boom)
    resp = http.get(f"/reports?shift_id={shift.shift_id}", headers=auth_headers("op1", "operator"))
    assert resp.status_code == 409
