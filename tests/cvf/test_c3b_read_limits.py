"""P2C-MUTATION-FULL-UI-C3B1 — 500/501 read-limit matrix (SPEC R11/R36,
AC-11).

Message, Task and CustomerRequest lists each independently enforce the exact
0-500 admit / 501+ controlled-422 boundary through the real API/backend
dependency chain - never a bare row-count check, never silent truncation.
"""

from __future__ import annotations

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

import pytest

from operations_domain.models import CustomerRequest, RiskClass, Task

from _auth_test_helpers import auth_headers
from _c3b_read_fixtures import make_inmemory, make_sqlite, new_message, new_shift, seed_active_assignment, with_ledger

_BACKENDS = pytest.mark.parametrize("make_ledger", [make_inmemory, make_sqlite], ids=["inmemory", "sqlite"])
_LIMIT = 500
_LIMIT_CASES = pytest.mark.parametrize("count,expected", [(_LIMIT, 200), (_LIMIT + 1, 422)])


@_BACKENDS
@_LIMIT_CASES
def test_message_list_ceiling(make_ledger, count, expected):
    ledger = make_ledger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "viewer-1", "viewer")
    for i in range(count):
        ledger.add_message(new_message(shift.shift_id, text=f"m{i}"))
    def _run(client):
        res = client.get("/messages", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == expected
        if expected == 200:
            assert len(res.json()) == count
        else:
            assert res.json() is not None
    with_ledger(ledger, _run)


@_BACKENDS
@_LIMIT_CASES
def test_task_list_ceiling(make_ledger, count, expected):
    ledger = make_ledger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "viewer-1", "viewer")
    for i in range(count):
        ledger.add_task(Task(shift_id=shift.shift_id, title=f"T{i}", risk_class=RiskClass.R1))
    def _run(client):
        res = client.get("/tasks", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == expected
        if expected == 200:
            assert len(res.json()) == count
    with_ledger(ledger, _run)


@_BACKENDS
@_LIMIT_CASES
def test_customer_request_list_ceiling(make_ledger, count, expected):
    ledger = make_ledger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "viewer-1", "viewer")
    for i in range(count):
        ledger.add_customer_request(CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary=f"R{i}"))
    def _run(client):
        res = client.get("/customer-requests", params={"shift_id": str(shift.shift_id)}, headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == expected
        if expected == 200:
            assert len(res.json()) == count
    with_ledger(ledger, _run)
