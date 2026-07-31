"""Opt-in live PostgreSQL 16 shift-create admission suite
(SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29, SPEC R8).

Every test below requires LIVE_POSTGRES_DATABASE_URL, set only by
scripts/run_postgres_live_roundtrip.py after applying migrations against a
disposable container; without it they skip. NEVER calls
metadata.create_all() and NEVER falls back to SQLite - the migration is the
schema authority.

SCR-BUILD-REV-F1 repair: proves the real AUTHENTICATED API/service path
required by SPEC R8 - a minted operator JWT through the real FastAPI
POST /shifts route (get_ledger overridden to the live PostgreSQL-backed
SqlLedger), not a bare ShiftService(ledger).create(..., Principal(...)) call
that bypasses JWT verification. Covers create, actor-bound audit, reconnect
survival, and injected-audit rollback plus post-rollback connection
usability.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine

from workspace_api.auth.tokens import create_access_token
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.main import app

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"
_OPERATOR_HEADERS = {"Authorization": f"Bearer {create_access_token(Principal(user_id='op1', role='operator'))}"}


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R8)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


@pytest.fixture()
def client(sql_ledger):
    """The real FastAPI app, with only get_ledger overridden to the live
    PostgreSQL-backed SqlLedger - JWT verification, permission checks and
    ShiftService routing all run for real (SPEC R8's authenticated API/
    service path), exactly as production traffic would.

    P2C-MUTATION-FULL-UI-C3A1 (SPEC R4): ShiftService.create now requires
    the creator to be a persisted active user - seeded here once per test."""
    if sql_ledger.get_user_by_id("op1") is None:
        sql_ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    app.dependency_overrides[get_ledger] = lambda: sql_ledger
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _window():
    now = datetime.now(timezone.utc)
    return now, now + timedelta(hours=8)


def _post_create(client_, name: str, headers=None):
    starts_at, ends_at = _window()
    return client_.post(
        "/shifts",
        params={"name": name, "starts_at": starts_at.isoformat(), "ends_at": ends_at.isoformat()},
        headers=headers if headers is not None else _OPERATOR_HEADERS,
    )


def test_create_persists_shift_and_actor_bound_audit(client, sql_ledger):
    res = _post_create(client, "Live PG shift")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "OPEN"
    assert body["version"] == 1

    fetched = sql_ledger.get_shift(body["shift_id"])
    assert fetched.name == "Live PG shift"

    audits = sql_ledger.audit_entries_for(body["shift_id"])
    assert len(audits) == 1
    assert audits[0]["action"] == "shift.create"
    assert audits[0]["actor_id"] == "op1"


def test_create_and_audit_survive_reconnect(client, sql_ledger, live_database_url):
    res = _post_create(client, "Reconnect PG shift")
    assert res.status_code == 200
    shift_id = res.json()["shift_id"]
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    fetched_shift = fresh.get_shift(shift_id)
    audits = fresh.audit_entries_for(shift_id)

    assert str(fetched_shift.shift_id) == shift_id
    assert fetched_shift.name == "Reconnect PG shift"
    assert len(audits) == 1
    assert audits[0]["action"] == "shift.create"


class _Boom(Exception):
    pass


def test_injected_audit_failure_rolls_back_creation(client, sql_ledger, live_database_url):
    with patch.object(SqlLedger, "append_audit", side_effect=_Boom("simulated audit sink failure")):
        with pytest.raises(_Boom):
            _post_create(client, "Rollback PG shift")

    fresh = _reconnected(live_database_url)
    assert [s for s in fresh.list_shifts() if s.name == "Rollback PG shift"] == []


def test_connection_remains_usable_after_rollback_case(client, sql_ledger):
    with patch.object(SqlLedger, "append_audit", side_effect=_Boom("simulated audit sink failure")):
        with pytest.raises(_Boom):
            _post_create(client, "Usability PG shift")

    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1

    res2 = _post_create(client, "Post-rollback PG shift")
    assert res2.status_code == 200
    assert sql_ledger.get_shift(res2.json()["shift_id"]).name == "Post-rollback PG shift"
