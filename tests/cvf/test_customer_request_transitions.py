"""Customer-request lifecycle/transition tests (split from
test_customer_request_vertical.py, HOV-REV-F5 repair, P2A-HANDOVER-VERTICAL
Amendment 2, SPEC R20). Shared setup lives in _customer_request_fixtures.py.

Proves the customer-request-specific status lifecycle and atomic
transition+audit on both ledger backends.
"""

from unittest.mock import patch

import pytest

from operations_ledger.sql_ledger import SqlLedger

from workspace_api.application.customer_request_service import CustomerRequestService
from operations_domain.models import CustomerRequestStatus
from workspace_api.infrastructure.repository import InMemoryLedger

from _customer_request_fixtures import _BoomOnAudit, _operator, _raise_on_audit, _request, _sql_ledger


# --- transition ---------------------------------------------------------


def test_valid_status_transition_sequence():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())

    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )
    assert moved.status == CustomerRequestStatus.ACKNOWLEDGED

    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=moved.version
    )
    assert moved.status == CustomerRequestStatus.IN_PROGRESS

    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.RESOLVED, expected_version=moved.version
    )
    assert moved.status == CustomerRequestStatus.RESOLVED

    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.CLOSED, expected_version=moved.version
    )
    assert moved.status == CustomerRequestStatus.CLOSED

    audit = ledger.audit_entries_for(str(created.request_id))
    assert audit[-1].action == "customer_request.transition"
    assert audit[-1].before_state == "RESOLVED"
    assert audit[-1].after_state == "CLOSED"


def test_waiting_cannot_go_directly_to_closed():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=moved.version
    )
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.WAITING, expected_version=moved.version
    )

    with pytest.raises(ValueError):
        svc.transition(
            created.request_id, _operator(), CustomerRequestStatus.CLOSED, expected_version=moved.version
        )

    # WAITING -> IN_PROGRESS remains a valid path back.
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=moved.version
    )
    assert moved.status == CustomerRequestStatus.IN_PROGRESS


def test_closed_is_terminal():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=moved.version
    )
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.RESOLVED, expected_version=moved.version
    )
    moved = svc.transition(
        created.request_id, _operator(), CustomerRequestStatus.CLOSED, expected_version=moved.version
    )

    with pytest.raises(ValueError):
        svc.transition(
            created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=moved.version
        )


def test_illegal_transition_skip_is_blocked():
    ledger = InMemoryLedger()
    svc = CustomerRequestService(ledger)
    created = svc.create_customer_request(_request(), _operator())
    # NEW -> IN_PROGRESS directly is not allowed (must go through ACKNOWLEDGED).
    with pytest.raises(ValueError):
        svc.transition(
            created.request_id, _operator(), CustomerRequestStatus.IN_PROGRESS, expected_version=created.version
        )


# --- atomicity: transition only ----------------------------------------------


def test_transition_rolls_back_when_audit_fails_in_memory():
    ledger = InMemoryLedger()
    created = CustomerRequestService(ledger).create_customer_request(_request(), _operator())

    with patch.object(InMemoryLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).transition(
                created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED,
                expected_version=created.version,
            )

    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.status == CustomerRequestStatus.NEW, "status must not advance"


def test_transition_rolls_back_when_audit_fails_sql(tmp_path):
    ledger = _sql_ledger(tmp_path)
    created = CustomerRequestService(ledger).create_customer_request(_request(), _operator())

    with patch.object(SqlLedger, "append_audit", side_effect=_raise_on_audit):
        with pytest.raises(_BoomOnAudit):
            CustomerRequestService(ledger).transition(
                created.request_id, _operator(), CustomerRequestStatus.ACKNOWLEDGED,
                expected_version=created.version,
            )

    fetched = ledger.get_customer_request(created.request_id)
    assert fetched.status == CustomerRequestStatus.NEW, "status must not advance"
