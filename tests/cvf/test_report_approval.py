"""Report approval receipt scoping and R2 quorum (SPEC R16-R17). Mirrors
test_incident_vertical.py's acknowledge-quorum coverage, applied to
report.approve.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application import approval_service
from workspace_api.application.report_service import ReportService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from operations_domain.models import ReportStatus, Shift
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")


def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'report_approval.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "report_approval.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _seed(ledger, shift_id, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _in_review_report(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    ledger.close_shift(shift.shift_id)
    svc = ReportService(ledger)
    report = svc.generate(shift.shift_id, _OPERATOR)
    return svc.submit_review(report.report_id, _OPERATOR)


def _add_approver(ledger, report, user_id="sup2", role="shift_supervisor"):
    _seed(ledger, report.shift_id, user_id, role)
    return Principal(user_id=user_id, role=role)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_receipt_creation_requires_current_in_review_report(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    report = _in_review_report(ledger)
    approver = _add_approver(ledger, report)

    receipt, created = approval_service.create_approval_receipt(
        ledger, approver, record_type="Report", action="report.approve", record_id=report.report_id,
    )
    assert created is True
    assert receipt.risk_class == "R2"
    assert receipt.target_version == report.version
    assert receipt.payload_digest == report.content.snapshot_digest


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_receipt_creation_refused_for_draft_report(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    ledger.close_shift(shift.shift_id)
    report = ReportService(ledger).generate(shift.shift_id, _OPERATOR)
    approver = _add_approver(ledger, report)

    with pytest.raises(CvfDenied) as exc:
        approval_service.create_approval_receipt(
            ledger, approver, record_type="Report", action="report.approve", record_id=report.report_id,
        )
    assert exc.value.http_status == 409


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_approve_requires_permission(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    report = _in_review_report(ledger)
    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).approve(report.report_id, _OPERATOR)
    assert exc.value.control == "permission"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_approve_requires_receipt(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    report = _in_review_report(ledger)
    _seed(ledger, report.shift_id, "sup1", "shift_supervisor")
    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).approve(report.report_id, _SUPERVISOR)
    assert exc.value.control == "approval"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_approve_actor_cannot_be_sole_receipt_approver(tmp_path, name):
    """R17: the approving transition actor cannot be the sole receipt
    approver - the existing confirmer-separation rule remains load-bearing."""
    ledger = dict(_backends(tmp_path))[name]
    report = _in_review_report(ledger)
    _seed(ledger, report.shift_id, "sup1", "shift_supervisor")
    approval_service.create_approval_receipt(
        ledger, _SUPERVISOR, record_type="Report", action="report.approve", record_id=report.report_id,
    )
    with pytest.raises(CvfDenied) as exc:
        ReportService(ledger).approve(report.report_id, _SUPERVISOR)
    assert exc.value.control == "approval"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_approve_succeeds_with_distinct_receipt_approver(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    report = _in_review_report(ledger)
    approver = _add_approver(ledger, report, "sup2")
    approval_service.create_approval_receipt(
        ledger, approver, record_type="Report", action="report.approve", record_id=report.report_id,
    )
    _seed(ledger, report.shift_id, "sup1", "shift_supervisor")

    approved = ReportService(ledger).approve(report.report_id, _SUPERVISOR)
    assert approved.status == ReportStatus.APPROVED
    entries = ledger.audit_entries_for(str(report.report_id))
    actions = [e.action if hasattr(e, "action") else e["action"] for e in entries]
    assert "report.approve" in actions


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_receipt_for_wrong_version_does_not_count(tmp_path, name):
    """A receipt bound to an older version cannot authorize approval of a
    successor - stale receipts never carry forward."""
    ledger = dict(_backends(tmp_path))[name]
    report = _in_review_report(ledger)
    approver = _add_approver(ledger, report, "sup2")
    approval_service.create_approval_receipt(
        ledger, approver, record_type="Report", action="report.approve", record_id=report.report_id,
    )

    # Wrong record id entirely - receipt scoped elsewhere never counts here.
    other_report = _in_review_report(ledger)
    _seed(ledger, other_report.shift_id, "sup1", "shift_supervisor")
    with pytest.raises(CvfDenied):
        ReportService(ledger).approve(other_report.report_id, _SUPERVISOR)


# --- F7 repair: submit-review/approve take no request body over HTTP -------

@pytest.fixture
def client():
    ledger = InMemoryLedger()
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def test_http_submit_review_accepts_empty_request(client):
    ledger, http = client
    report = _in_review_report_removing_status(ledger)
    resp = http.post(f"/reports/{report.report_id}/submit-review", headers=auth_headers("op1", "operator"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "IN_REVIEW"


def _in_review_report_removing_status(ledger):
    """DRAFT (not yet IN_REVIEW) report, so submit-review below is the real
    forward transition rather than a repeat rejected as 409-wrong-status."""
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    ledger.close_shift(shift.shift_id)
    return ReportService(ledger).generate(shift.shift_id, _OPERATOR)


def test_http_submit_review_rejects_caller_supplied_body(client):
    """F7: no requestBody is declared for this operation, so FastAPI ignores
    caller-supplied JSON entirely - a caller trying to smuggle `status` in
    cannot influence the transition; the server-derived IN_REVIEW still wins."""
    ledger, http = client
    report = _in_review_report_removing_status(ledger)
    resp = http.post(
        f"/reports/{report.report_id}/submit-review",
        json={"status": "APPROVED"},
        headers=auth_headers("op1", "operator"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "IN_REVIEW"


def test_http_approve_accepts_empty_request(client):
    ledger, http = client
    report = _in_review_report(ledger)
    _add_approver(ledger, report, "sup2")
    approval_service.create_approval_receipt(
        ledger, Principal(user_id="sup2", role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    _seed(ledger, report.shift_id, "sup1", "shift_supervisor")
    resp = http.post(f"/reports/{report.report_id}/approve", headers=auth_headers("sup1", "shift_supervisor"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "APPROVED"


# --- Finding 1: canonical model must reject 4 independent-review probes ----

def _real_content():
    from operations_domain.models import Task
    from workspace_api.application import report_snapshot

    shift_id = uuid4()
    now = datetime.now(timezone.utc)
    task = Task(shift_id=shift_id, title="Check pumps", created_at=now)
    return report_snapshot.build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[task],
        customer_requests=[], incidents=[], handovers=[],
    )


def test_build_snapshot_output_is_accepted_by_the_canonical_model():
    """Positive control: genuine build_snapshot output validates - the four
    probes below prove TAMPERED variants of it are rejected."""
    assert _real_content().sections[2].section_type == "tasks"


def test_probe_wrong_field_types_rejected():
    from operations_domain.models import ReportContent

    bad = _real_content().model_dump(mode="json")
    bad["sections"][2]["records"][0]["version"] = "not-an-int"
    with pytest.raises(Exception):
        ReportContent(**bad)


def test_probe_source_version_mismatch_rejected():
    from operations_domain.models import ReportContent

    bad = _real_content().model_dump(mode="json")
    bad["source_manifest"][0]["source_version"] = 999
    with pytest.raises(Exception):
        ReportContent(**bad)


def test_probe_source_digest_mismatch_rejected():
    from operations_domain.models import ReportContent

    bad = _real_content().model_dump(mode="json")
    bad["source_manifest"][0]["source_digest"] = "f" * 64
    with pytest.raises(Exception):
        ReportContent(**bad)


def test_probe_reversed_canonical_order_rejected():
    from operations_domain.models import ReportContent, Task
    from workspace_api.application import report_snapshot

    shift_id = uuid4()
    now = datetime.now(timezone.utc)
    old = Task(shift_id=shift_id, title="old", created_at=now)
    new = Task(shift_id=shift_id, title="new", created_at=now.replace(year=now.year + 1))
    content = report_snapshot.build_snapshot(
        shift_id=shift_id, events=[], corrections=[], tasks=[old, new],
        customer_requests=[], incidents=[], handovers=[],
    )
    bad = content.model_dump(mode="json")
    bad["sections"][2]["records"] = list(reversed(bad["sections"][2]["records"]))
    bad["source_manifest"] = list(reversed(bad["source_manifest"]))
    with pytest.raises(Exception):
        ReportContent(**bad)
