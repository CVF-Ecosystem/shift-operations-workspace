"""P2C-OPERATIONS-CONSOLE-READ-SLICE Amendment 3 — live PostgreSQL 500/501
read-limit matrix (SPEC R27/AC-27, P2C-C3A-REV-F20/F21).

Moved out of tests/integration/test_postgres_live_runner.py (Amendment 3),
which had grown to 315 lines after Amendment 2 repair added this matrix -
not a behavior change to the matrix itself, purely a file-size split. This
module owns only the P2C read-limit matrix; it is not part of
scripts/run_postgres_live_roundtrip.py's LIVE_SUITE_TARGETS and must be
invoked separately against a disposable PostgreSQL 16 container using the
same orchestration primitives that runner uses.

Every surface/group is proven independently through the real authenticated
HTTP route via TestClient, the application's get_ledger dependency, and a
live-PostgreSQL-backed SqlLedger - not a bare row-count check. The shifts
table is truncated before the shift-list case (its only global, unscoped
surface); every other case uses its own fresh shift instead, since events
and each open-work group are shift_id-scoped and truncation is unnecessary.
For the three open-work groups, only the named group is filled to `count`;
the other two get exactly 1 record each, so one group's limit cannot mask
another group's behavior (F21).

Opt-in: skips without LIVE_POSTGRES_DATABASE_URL, gated the same way
test_sql_ledger_postgres_live.py's tests are (SPEC R1).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tests" / "cvf"))

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


def _live_seed(ledger, surface, count):
    """Seed exactly one surface/group to `count`; for the three open-work
    groups, the other two get exactly 1 record each (F21 independence).
    Returns the shift used (None for the global, unscoped `shifts` case)."""
    from operations_domain.models import CustomerRequest, Incident, OperationalEvent, RiskClass, Shift, Task
    from sqlalchemy import text

    now = datetime.now(timezone.utc)
    if surface == "shifts":
        with ledger.engine.begin() as conn:
            conn.execute(text("TRUNCATE shifts CASCADE"))
        for _ in range(count):
            ledger.create_shift(Shift(name="live-limit", starts_at=now, ends_at=now + timedelta(hours=1)))
        return None
    shift = Shift(name="live-limit", starts_at=now, ends_at=now + timedelta(hours=1))
    ledger.create_shift(shift)
    if surface == "events":
        for i in range(count):
            ledger.add_event(OperationalEvent(shift_id=shift.shift_id, event_type="x", title=f"E{i}"))
        return shift
    groups = {
        "tasks": lambda i: ledger.add_task(Task(shift_id=shift.shift_id, title=f"T{i}", risk_class=RiskClass.R1)),
        "customer_requests": lambda i: ledger.add_customer_request(
            CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary=f"R{i}")
        ),
        "incidents": lambda i: ledger.add_incident(
            Incident(shift_id=shift.shift_id, summary=f"I{i}", risk_class=RiskClass.R2)
        ),
    }
    for name, add in groups.items():
        for i in range(count if name == surface else 1):
            add(i)
    return shift


def _live_path_params(surface, shift):
    if surface == "shifts":
        return "/shifts", None
    if surface == "events":
        return "/events", {"shift_id": str(shift.shift_id)}
    return f"/shifts/{shift.shift_id}/open-work", None


@pytest.mark.parametrize("surface", ("shifts", "events", "tasks", "customer_requests", "incidents"))
@pytest.mark.parametrize("count,expected", [(500, 200), (501, 422)])
def test_live_read_surface_ceiling(surface, count, expected):
    """F17/F20/F21: shifts, events and each open-work group, both 500-admit
    and 501-refuse, through the real API/SqlLedger dependency chain."""
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R1)")
    from fastapi.testclient import TestClient
    from operations_ledger.sql_ledger import SqlLedger, make_engine
    from workspace_api.dependencies import get_ledger
    from workspace_api.domain import models as domain_models
    from workspace_api.main import app

    from _auth_test_helpers import auth_headers

    ledger = SqlLedger(url, models=domain_models, engine=make_engine(url))
    shift = _live_seed(ledger, surface, count)
    path, params = _live_path_params(surface, shift)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        res = TestClient(app).get(path, params=params, headers=auth_headers("viewer-1", "viewer"))
    finally:
        app.dependency_overrides.pop(get_ledger, None)
        ledger.engine.dispose()

    assert res.status_code == expected
    if expected != 200:
        return
    if surface in ("shifts", "events"):
        assert len(res.json()) == count
    else:
        body = res.json()
        assert len(body[surface]) == count
        for other in ("tasks", "customer_requests", "incidents"):
            if other != surface:
                assert len(body[other]) == 1
