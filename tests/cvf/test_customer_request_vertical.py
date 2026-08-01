"""Customer-request golden vertical: the CVF chain replicated to a fourth
operational domain (P2-A). Create/HTTP behavior only - transition/lifecycle
tests split into test_customer_request_transitions.py (HOV-REV-F5 repair,
P2A-HANDOVER-VERTICAL Amendment 2, SPEC R20); shared setup lives in
_customer_request_fixtures.py.

Proves the SAME cvf-runtime gates enforce CustomerRequest create, the
nullable-shift_id frozen-shift invariant (via a real acknowledged handover,
HOV-AUTH-F4), and atomic create+audit on both ledger backends.
"""

from unittest.mock import patch

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger

from workspace_api.application import approval_service
from workspace_api.application.customer_request_service import CustomerRequestService
from workspace_api.application.report_service import ReportService
from workspace_api.application.shift_service import ShiftService
from workspace_api.domain.models import User
from operations_domain.models import CustomerRequestStatus
from workspace_api.infrastructure.repository import InMemoryLedger

from _customer_request_fixtures import (  # noqa: F401 - re-exported for test_customer_request_repair.py
    _BoomOnAudit,
    _backends,
    _client_for,
    _clear_overrides,
    _make_ready_handover,
    _new_shift,
    _operator,
    _raise_on_audit,
    _request,
    _seed_assignment,
    _sql_ledger,
    _viewer,
)
from _auth_test_helpers import auth_headers


# --- service-level create --------------------------------------------------


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_without_shift_succeeds(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    created = CustomerRequestService(ledger).create_customer_request(
        _request(), _operator()
    )
    assert created.status == CustomerRequestStatus.NEW
    assert created.shift_id is None

    # InMemoryLedger.audit_entries_for returns AuditRecord objects;
    # SqlLedger.audit_entries_for returns plain dicts (existing dual-backend
    # asymmetry, also present for Task/Shift audit checks elsewhere in this
    # test suite - not something this tranche changes). Assert on the shape
    # each backend actually returns.
    audit = ledger.audit_entries_for(str(created.request_id))
    assert len(audit) == 1
    last = audit[-1]
    action = last.action if hasattr(last, "action") else last["action"]
    assert action == "customer_request.create"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_with_open_shift_succeeds(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    created = CustomerRequestService(ledger).create_customer_request(
        _request(shift), _operator()
    )
    assert created.shift_id == shift.shift_id


def test_viewer_cannot_create_customer_request():
    ledger = InMemoryLedger()
    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(ledger).create_customer_request(_request(), _viewer())
    assert exc.value.control == "permission"


def _make_ready_report(ledger, shift):
    """A current, APPROVED END_SHIFT report - the real `report_approved`
    freeze prerequisite (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE)."""
    svc = ReportService(ledger)
    report = svc.generate(shift.shift_id, _operator())
    report = svc.submit_review(report.report_id, _operator())
    _seed_assignment(ledger, shift.shift_id, "sup3", "shift_supervisor")
    approval_service.create_approval_receipt(
        ledger, Principal(user_id="sup3", role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    return svc.approve(report.report_id, Principal(user_id="sup1", role="shift_supervisor"))


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_create_customer_request_with_frozen_shift_is_rejected(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _new_shift(ledger)
    ShiftService(ledger).close(shift.shift_id, _operator())
    _make_ready_handover(ledger, shift)
    _make_ready_report(ledger, shift)
    ShiftService(ledger).freeze(shift.shift_id, Principal(user_id="sup1", role="shift_supervisor"))

    rejected_request = _request(shift)
    with pytest.raises(ValueError):
        CustomerRequestService(ledger).create_customer_request(rejected_request, _operator())
    with pytest.raises(KeyError):
        ledger.get_customer_request(rejected_request.request_id)


# --- HTTP-level round trip ---------------------------------------------------


def test_http_create_round_trip():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={"customer_id": "cust-9", "summary": "Late delivery"},
            headers=auth_headers("op1", "operator"),
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["customer_id"] == "cust-9"
        assert body["summary"] == "Late delivery"
        assert body["status"] == "NEW"
    finally:
        _clear_overrides()


def test_http_anonymous_create_is_401():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={"customer_id": "cust-9", "summary": "Late delivery"},
        )
        assert resp.status_code == 401, resp.text
        assert ledger.customer_requests == {}
    finally:
        _clear_overrides()


def test_http_insufficient_role_create_is_403():
    ledger = InMemoryLedger()
    client = _client_for(ledger)
    try:
        resp = client.post(
            "/customer-requests",
            json={"customer_id": "cust-9", "summary": "Late delivery"},
            headers=auth_headers("v1", "viewer"),
        )
        assert resp.status_code == 403, resp.text
    finally:
        _clear_overrides()


# --- atomicity: create only --------------------------------------------------


def test_create_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    request = _request()

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).create_customer_request(request, _operator())

    with pytest.raises(KeyError):
        ledger.get_customer_request(request.request_id)


def test_create_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    request = _request()

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).create_customer_request(request, _operator())

    with pytest.raises(KeyError):
        ledger.get_customer_request(request.request_id)
