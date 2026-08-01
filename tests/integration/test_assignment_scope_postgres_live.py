"""Opt-in live PostgreSQL 16 assignment-scope suite (P2C-MUTATION-FULL-UI-C3A2
WO section 3.6). Same opt-in contract as test_assignment_postgres_live.py:
every test below requires LIVE_POSTGRES_DATABASE_URL, set only by
scripts/run_postgres_live_roundtrip.py after applying database/migrations
against a disposable container; without it they skip. NEVER falls back to
SQLite. Proves the SAME assignment-scope admission/refusal behavior holds
against the real DB-backed ledger for a representative read, mutation and
cross-shift route, via the real FastAPI TestClient + dependency override."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tests" / "cvf"))

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_domain.models import Shift

from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.main import app

from _auth_test_helpers import auth_headers
from _assignment_scope_fixtures import seed_active_assignment

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"

_OP = ("pg-scope-op", "operator")
_OUTSIDER = ("pg-scope-outsider", "operator")
_SUP = ("pg-scope-sup", "shift_supervisor")


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (WO section 3.6)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


@pytest.fixture()
def client(sql_ledger):
    for user_id, role in (_OP, _OUTSIDER, _SUP):
        if sql_ledger.get_user_by_id(user_id) is None:
            sql_ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    app.dependency_overrides[get_ledger] = lambda: sql_ledger
    try:
        yield sql_ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _shift(ledger, **kw) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Live PG scope shift", starts_at=now, ends_at=now + timedelta(hours=8), **kw)
    ledger.create_shift(shift)
    return shift


# --- read route: GET /shifts/{id}/open-work -----------------------------

def test_live_open_work_requires_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)

    res = http.get(f"/shifts/{shift.shift_id}/open-work", headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 404

    seed_active_assignment(ledger, shift.shift_id, *_OP)
    res = http.get(f"/shifts/{shift.shift_id}/open-work", headers=auth_headers(*_OP))
    assert res.status_code == 200


# --- mutation route: POST /messages -------------------------------------

def test_live_message_create_requires_active_assignment(client):
    ledger, http = client
    shift = _shift(ledger)

    res = http.post(
        "/messages", json={"shift_id": str(shift.shift_id), "text": "hi"}, headers=auth_headers(*_OUTSIDER)
    )
    assert res.status_code == 404

    seed_active_assignment(ledger, shift.shift_id, *_OP)
    res = http.post(
        "/messages", json={"shift_id": str(shift.shift_id), "text": "hi"}, headers=auth_headers(*_OP)
    )
    assert res.status_code == 200


# --- cross-shift route: handover create needs SOURCE-shift assignment ----

def test_live_handover_create_requires_source_assignment_not_destination(client):
    ledger, http = client
    src, dst = _shift(ledger), _shift(ledger)
    seed_active_assignment(ledger, dst.shift_id, *_OP)

    payload = {"from_shift_id": str(src.shift_id), "to_shift_id": str(dst.shift_id)}
    res = http.post("/handovers", json=payload, headers=auth_headers(*_OP))
    assert res.status_code == 404

    seed_active_assignment(ledger, src.shift_id, *_OP)
    res = http.post("/handovers", json=payload, headers=auth_headers(*_OP))
    assert res.status_code == 200


# --- supervisor-bar mutation: incident acknowledge ------------------------

def test_live_incident_acknowledge_requires_active_assignment_for_sufficient_role(client):
    ledger, http = client
    shift = _shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, *_OP)
    incident_id = http.post(
        "/incidents", json={"shift_id": str(shift.shift_id), "summary": "s"}, headers=auth_headers(*_OP)
    ).json()["incident_id"]

    ack_body = {"expected_version": 1}
    res = http.post(f"/incidents/{incident_id}/acknowledge", json=ack_body, headers=auth_headers(*_OUTSIDER))
    assert res.status_code == 403  # insufficient role fires before assignment

    seed_active_assignment(ledger, shift.shift_id, *_SUP)
    res = http.post(f"/incidents/{incident_id}/acknowledge", json=ack_body, headers=auth_headers(*_SUP))
    assert res.status_code != 404
