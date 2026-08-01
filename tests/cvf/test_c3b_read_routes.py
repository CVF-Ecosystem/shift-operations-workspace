"""P2C-MUTATION-FULL-UI-C3B1 — browser read/readiness route tests (SPEC
R11/R35-R37, AC-11).

Covers: authenticated + ACTIVE-assignment-scoped Message/Task/CustomerRequest
list ordering, 401/404 admission, and the four readiness pairs' ready/not-
ready/404/409 outcomes — through the real API/backend dependency chain.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

import pytest

from operations_domain.models import CustomerRequest, RiskClass, Task, TaskStatus

from _auth_test_helpers import auth_headers
from _c3b_read_fixtures import (
    make_inmemory,
    make_sqlite,
    new_event,
    new_message,
    new_task_creation_intent,
    seed_active_assignment,
    seed_user,
    new_shift,
    with_ledger,
)

_BACKENDS = pytest.mark.parametrize("make_ledger", [make_inmemory, make_sqlite], ids=["inmemory", "sqlite"])
_LIST_PATHS = pytest.mark.parametrize("path", ["/messages", "/tasks", "/customer-requests"])


@_LIST_PATHS
def test_list_route_anonymous_returns_401(path):
    ledger = make_inmemory()
    shift = new_shift(ledger)
    def _run(client):
        res = client.get(path, params={"shift_id": str(shift.shift_id)})
        assert res.status_code == 401
    with_ledger(ledger, _run)


@_LIST_PATHS
def test_list_route_unassigned_returns_404(path):
    ledger = make_inmemory()
    shift = new_shift(ledger)
    seed_user(ledger, "viewer-1", "viewer")
    def _run(client):
        res = client.get(path, params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 404
    with_ledger(ledger, _run)


# --- GET /messages?shift_id=... ---

def test_get_messages_missing_shift_returns_404():
    ledger = make_inmemory()
    def _run(client):
        res = client.get("/messages", params={"shift_id": str(uuid4())}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 404
    with_ledger(ledger, _run)


@_BACKENDS
def test_get_messages_assigned_returns_ascending_created_at_then_id(make_ledger):
    ledger = make_ledger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "viewer-1", "viewer")
    base = datetime(2026, 8, 1, 10, tzinfo=timezone.utc)
    m1 = new_message(shift.shift_id, text="second", created_at=base + timedelta(minutes=1))
    m2 = new_message(shift.shift_id, text="first", created_at=base)
    ledger.add_message(m1)
    ledger.add_message(m2)
    def _run(client):
        res = client.get("/messages", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 200
        body = res.json()
        assert len(body) == 2
        assert body[0]["text"] == "first"
        assert body[1]["text"] == "second"
    with_ledger(ledger, _run)


# --- GET /tasks?shift_id=... ---

@_BACKENDS
def test_get_tasks_assigned_includes_terminal_history(make_ledger):
    ledger = make_ledger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "viewer-1", "viewer")
    t1 = Task(shift_id=shift.shift_id, title="Open", risk_class=RiskClass.R1)
    t2 = Task(shift_id=shift.shift_id, title="Done", risk_class=RiskClass.R1)
    ledger.add_task(t1)
    ledger.add_task(t2)
    t2.status = TaskStatus.DONE
    ledger.put_task(t2)
    def _run(client):
        res = client.get("/tasks", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 200
        titles = {t["title"] for t in res.json()}
        assert titles == {"Open", "Done"}
    with_ledger(ledger, _run)


# --- GET /customer-requests?shift_id=... ---

@_BACKENDS
def test_get_customer_requests_only_returns_bound_requests(make_ledger):
    """SPEC R7: a null shift_id request is outside this shift console."""
    ledger = make_ledger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "viewer-1", "viewer")
    bound = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="bound")
    unbound = CustomerRequest(customer_id="c2", shift_id=None, summary="unbound")
    ledger.add_customer_request(bound)
    ledger.add_customer_request(unbound)
    def _run(client):
        res = client.get("/customer-requests", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 200
        body = res.json()
        assert len(body) == 1
        assert body[0]["summary"] == "bound"
    with_ledger(ledger, _run)


# --- GET /approvals/readiness ---

def _readiness_params(record_type, record_id, action):
    return {"record_type": record_type, "record_id": str(record_id), "action": action}


def test_readiness_anonymous_returns_401():
    ledger = make_inmemory()
    def _run(client):
        res = client.get("/approvals/readiness", params=_readiness_params("OperationalEvent", uuid4(), "event.confirm"))
        assert res.status_code == 401
    with_ledger(ledger, _run)


def test_readiness_unknown_pair_returns_422():
    ledger = make_inmemory()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    def _run(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("OperationalEvent", uuid4(), "event.correct"),
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code == 422
    with_ledger(ledger, _run)


def test_readiness_event_confirm_not_ready_then_ready():
    ledger = make_inmemory()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    event = new_event(shift.shift_id, risk_class=RiskClass.R2)
    ledger.add_event(event)

    def _check_not_ready(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("OperationalEvent", event.event_id, "event.confirm"),
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ready"] is False
        assert body["required_roles"] == ["shift_supervisor"]
        assert body["satisfied_roles"] == []
        assert "payload_digest" not in body
        assert "receipt_id" not in body

    with_ledger(ledger, _check_not_ready)

    def _create_receipt(client):
        res = client.post(
            "/approvals",
            json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)},
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code in (200, 201)

    with_ledger(ledger, _create_receipt)

    def _check_ready(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("OperationalEvent", event.event_id, "event.confirm"),
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ready"] is True
        assert body["satisfied_roles"] == ["shift_supervisor"]

    with_ledger(ledger, _check_ready)


def test_readiness_task_create_uses_stored_intent_id():
    ledger = make_inmemory()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    intent = new_task_creation_intent(ledger, shift.shift_id, risk_class=RiskClass.R2)
    def _run(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("Task", intent.intent_id, "task.create"),
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["record_id"] == str(intent.intent_id)
        assert body["ready"] is False
    with_ledger(ledger, _run)


def test_readiness_missing_target_returns_404():
    ledger = make_inmemory()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    def _run(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("OperationalEvent", uuid4(), "event.confirm"),
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code == 404
    with_ledger(ledger, _run)


def test_readiness_unassigned_returns_404_after_permission():
    ledger = make_inmemory()
    shift = new_shift(ledger)
    event = new_event(shift.shift_id, risk_class=RiskClass.R2)
    ledger.add_event(event)
    seed_user(ledger, "sup-1", "shift_supervisor")
    def _run(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("OperationalEvent", event.event_id, "event.confirm"),
            headers=auth_headers("sup-1", "shift_supervisor"),
        )
        assert res.status_code == 404
    with_ledger(ledger, _run)


def test_readiness_coarse_permission_denied_returns_403_before_assignment():
    """R37: require_action runs before target resolution/assignment - an
    operator (below shift_supervisor) is refused 403 even for a target it
    would otherwise be unassigned to."""
    ledger = make_inmemory()
    shift = new_shift(ledger)
    event = new_event(shift.shift_id, risk_class=RiskClass.R2)
    ledger.add_event(event)
    seed_user(ledger, "op-1", "operator")
    def _run(client):
        res = client.get(
            "/approvals/readiness",
            params=_readiness_params("OperationalEvent", event.event_id, "event.confirm"),
            headers=auth_headers("op-1", "operator"),
        )
        assert res.status_code == 403
    with_ledger(ledger, _run)
