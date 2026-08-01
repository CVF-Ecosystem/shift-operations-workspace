"""P2C-OPERATIONS-CONSOLE-READ-SLICE — API integration tests (SPEC R2-R5/AC-01-AC-04,
Amendment 2 R27/AC-27).

Exercises authenticated, explicitly assigned read access, ordering, 404
refusal and 500-record ceilings through the real API/backend chain.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tests" / "cvf"))

import pytest
from fastapi.testclient import TestClient

from operations_domain.models import (
    CustomerRequest,
    EvidenceRef,
    Incident,
    OperationalEvent,
    RiskClass,
    Shift,
    Task,
    TaskStatus,
)
from operations_ledger.sql_ledger import SqlLedger, make_engine
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app

from _auth_test_helpers import auth_headers
from _assignment_scope_fixtures import seed_all_shift_assignments


def _shift() -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="API shift", starts_at=now, ends_at=now + timedelta(hours=8))


def _event(shift_id, *, starts_at=None, title="E1") -> OperationalEvent:
    return OperationalEvent(
        shift_id=shift_id,
        event_type="equipment_downtime",
        title=title,
        risk_class=RiskClass.R2,
        starts_at=starts_at,
        evidence=[EvidenceRef(source_type="message", source_id="m1", sha256="ab" * 32)],
    )


def _with_ledger(ledger, fn):
    seed_all_shift_assignments(ledger, "viewer-1", "viewer")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        return fn(TestClient(app))
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _make_inmemory() -> InMemoryLedger:
    return InMemoryLedger()


def _make_sqlite() -> SqlLedger:
    from sqlalchemy.pool import StaticPool

    from operations_ledger.tables import metadata

    # StaticPool + check_same_thread=False: TestClient executes the route
    # handler in a worker thread (anyio.to_thread.run_sync), a different
    # thread than this fixture - the default SQLite in-memory pool is one
    # connection per thread, which would otherwise make the route see an
    # empty, table-less database.
    engine = make_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    metadata.create_all(engine)
    return SqlLedger("sqlite://", models=domain_models, engine=engine)


_BACKENDS = pytest.mark.parametrize("make_ledger", [_make_inmemory, _make_sqlite], ids=["inmemory", "sqlite"])


# --- GET /shifts ---

def test_get_shifts_anonymous_returns_401():
    ledger = InMemoryLedger()
    def _run(client):
        res = client.get("/shifts")
        assert res.status_code == 401
    _with_ledger(ledger, _run)


def test_get_shifts_malformed_token_returns_401():
    ledger = InMemoryLedger()
    def _run(client):
        res = client.get("/shifts", headers={"Authorization": "Bearer not-a-jwt"})
        assert res.status_code == 401
    _with_ledger(ledger, _run)


def test_get_shifts_viewer_returns_200():
    shift = _shift()
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    def _run(client):
        res = client.get("/shifts", headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["shift_id"] == str(shift.shift_id)
    _with_ledger(ledger, _run)


# --- GET /events?shift_id=... ---

def test_get_events_anonymous_returns_401():
    shift = _shift()
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    def _run(client):
        res = client.get("/events", params={"shift_id": str(shift.shift_id)})
        assert res.status_code == 401
    _with_ledger(ledger, _run)


def test_get_events_viewer_returns_200_with_order():
    shift = _shift()
    e1 = _event(shift.shift_id, starts_at=datetime(2026, 7, 28, 10, tzinfo=timezone.utc), title="A")
    e2 = _event(shift.shift_id, starts_at=datetime(2026, 7, 28, 9, tzinfo=timezone.utc), title="B")
    e3 = _event(shift.shift_id, starts_at=None, title="C")
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    for e in (e1, e2, e3):
        ledger.add_event(e)
    def _run(client):
        res = client.get("/events", params={"shift_id": str(shift.shift_id)},
                         headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 200
        events = res.json()
        assert len(events) == 3
        assert events[0]["title"] == "B"
        assert events[1]["title"] == "A"
        assert events[2]["title"] == "C"
        # Evidence preserved
        assert len(events[0]["evidence"]) == 1
    _with_ledger(ledger, _run)


def test_get_events_missing_shift_returns_404():
    ledger = InMemoryLedger()
    def _run(client):
        res = client.get("/events", params={"shift_id": str(uuid4())},
                         headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 404
    _with_ledger(ledger, _run)


# --- GET /shifts/{shift_id}/open-work ---

def test_get_open_work_anonymous_returns_401():
    shift = _shift()
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    def _run(client):
        res = client.get(f"/shifts/{shift.shift_id}/open-work")
        assert res.status_code == 401
    _with_ledger(ledger, _run)


def test_get_open_work_viewer_returns_exact_shape():
    shift = _shift()
    task = Task(shift_id=shift.shift_id, title="T1", risk_class=RiskClass.R1)
    task.status = TaskStatus.IN_PROGRESS
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="R1")
    incident = Incident(shift_id=shift.shift_id, summary="I1", risk_class=RiskClass.R2)
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    ledger.add_task(task)
    ledger.add_customer_request(request)
    ledger.add_incident(incident)
    def _run(client):
        res = client.get(f"/shifts/{shift.shift_id}/open-work",
                         headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 200
        body = res.json()
        assert set(body.keys()) == {"shift_id", "tasks", "customer_requests", "incidents"}
        assert body["shift_id"] == str(shift.shift_id)
        assert len(body["tasks"]) == 1
        assert len(body["customer_requests"]) == 1
        assert len(body["incidents"]) == 1
    _with_ledger(ledger, _run)


def test_get_open_work_missing_shift_returns_404():
    ledger = InMemoryLedger()
    def _run(client):
        res = client.get(f"/shifts/{uuid4()}/open-work",
                         headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == 404
    _with_ledger(ledger, _run)


# --- SPEC R4/Amendment 2 R27/AC-27: 500/501 ceiling, full matrix, both
# backends, driven through the real API/backend dependency chain (not a
# bare row-count check). P2C-C3A-REV-F16/F17/F18.

_LIMIT = 500
_LIMIT_CASES = pytest.mark.parametrize("count,expected", [(_LIMIT, 200), (_LIMIT + 1, 422)])

_OPEN_WORK_GROUPS = {
    "tasks": lambda ledger, shift, i: ledger.add_task(
        Task(shift_id=shift.shift_id, title=f"T{i}", risk_class=RiskClass.R1)
    ),
    "customer_requests": lambda ledger, shift, i: ledger.add_customer_request(
        CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary=f"R{i}")
    ),
    "incidents": lambda ledger, shift, i: ledger.add_incident(
        Incident(shift_id=shift.shift_id, summary=f"I{i}", risk_class=RiskClass.R2)
    ),
}


def _fill_one_group(ledger, shift, group, count):
    """Fill only `group` to `count`; the other two groups get exactly 1
    record each, well under the ceiling - proving the route checks each
    group independently rather than only ever tripping on a combined total."""
    for name, add in _OPEN_WORK_GROUPS.items():
        n = count if name == group else 1
        for i in range(n):
            add(ledger, shift, i)


@_BACKENDS
@_LIMIT_CASES
def test_shift_list_ceiling(make_ledger, count, expected):
    ledger = make_ledger()
    for _ in range(count):
        ledger.create_shift(_shift())
    def _run(client):
        res = client.get("/shifts", headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == expected
        if expected == 200:
            assert len(res.json()) == count
        else:
            assert res.json() is not None  # controlled body, not a partial list
    _with_ledger(ledger, _run)


@_BACKENDS
@_LIMIT_CASES
def test_event_list_ceiling(make_ledger, count, expected):
    ledger = make_ledger()
    shift = _shift()
    ledger.create_shift(shift)
    for i in range(count):
        ledger.add_event(_event(shift.shift_id, title=f"E{i}"))
    def _run(client):
        res = client.get("/events", params={"shift_id": str(shift.shift_id)},
                         headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == expected
        if expected == 200:
            assert len(res.json()) == count
    _with_ledger(ledger, _run)


@_BACKENDS
@pytest.mark.parametrize("group", ["tasks", "customer_requests", "incidents"])
@_LIMIT_CASES
def test_open_work_group_ceiling(make_ledger, group, count, expected):
    """P2C-C3A-REV-F21: each of the three open-work groups is checked
    INDEPENDENTLY - only `group` is filled to `count`, the other two get
    exactly 1 record each. A route that only checked one group (or only the
    combined total) would fail this for the groups it does not check."""
    ledger = make_ledger()
    shift = _shift()
    ledger.create_shift(shift)
    _fill_one_group(ledger, shift, group, count)
    def _run(client):
        res = client.get(f"/shifts/{shift.shift_id}/open-work",
                         headers=auth_headers("viewer-1", "viewer"))
        assert res.status_code == expected
        if expected == 200:
            body = res.json()
            assert len(body[group]) == count
            for other in _OPEN_WORK_GROUPS:
                if other != group:
                    assert len(body[other]) == 1
    _with_ledger(ledger, _run)
