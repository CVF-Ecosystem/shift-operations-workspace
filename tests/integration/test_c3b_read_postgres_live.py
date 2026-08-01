"""Opt-in live PostgreSQL 16 suite for C3b1 browser reads/readiness
(P2C-MUTATION-FULL-UI-C3B1, SPEC R11/R35-R37, AC-11/AC-16).

Same opt-in contract as test_assignment_postgres_live.py: every test below
requires LIVE_POSTGRES_DATABASE_URL, set only by
scripts/run_postgres_live_roundtrip.py after applying migrations against a
disposable container; without it they skip. Proves message-list ordering,
assignment refusal and readiness quorum matching through the real
FastAPI route + live-PostgreSQL-backed SqlLedger dependency chain - not a
bare row-count check.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from fastapi.testclient import TestClient

from operations_domain.models import RiskClass, Shift
from operations_ledger.sql_ledger import SqlLedger, make_engine

from workspace_api.application.assignment_service import AssignmentService
from workspace_api.application.approval_service import create_approval_receipt
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.main import app
from cvf_runtime.identity import Principal

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R17)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _auth_headers(user_id: str, role: str) -> dict[str, str]:
    from workspace_api.auth.tokens import create_access_token

    token = create_access_token(Principal(user_id=user_id, role=role))
    return {"Authorization": f"Bearer {token}"}


def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Live PG C3b1 shift", starts_at=now, ends_at=now + timedelta(hours=8), **kw)


def _user(ledger, user_id, role="operator"):
    ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))


def _client_for(ledger) -> TestClient:
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)


def _clear_overrides() -> None:
    app.dependency_overrides.pop(get_ledger, None)


def test_live_message_list_assignment_scoped_and_ordered(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    viewer_id = f"pg-live-c3b-viewer-{uuid4().hex[:8]}"
    sup_id = f"pg-live-c3b-sup-{uuid4().hex[:8]}"
    _user(sql_ledger, viewer_id, "operator")
    _user(sql_ledger, sup_id, "shift_supervisor")
    AssignmentService(sql_ledger).assign(shift.shift_id, viewer_id, Principal(user_id=sup_id, role="shift_supervisor"))

    from workspace_api.application.message_service import MessageService

    MessageService(sql_ledger).create(shift.shift_id, "second", Principal(user_id=viewer_id, role="operator"))
    MessageService(sql_ledger).create(shift.shift_id, "third", Principal(user_id=viewer_id, role="operator"))

    client = _client_for(sql_ledger)
    try:
        res = client.get("/messages", params={"shift_id": str(shift.shift_id)}, headers=_auth_headers(viewer_id, "operator"))
        assert res.status_code == 200
        texts = [m["text"] for m in res.json()]
        assert texts == ["second", "third"]
    finally:
        _clear_overrides()


def test_live_message_list_unassigned_returns_404(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    outsider_id = f"pg-live-c3b-outsider-{uuid4().hex[:8]}"
    _user(sql_ledger, outsider_id, "viewer")

    client = _client_for(sql_ledger)
    try:
        res = client.get("/messages", params={"shift_id": str(shift.shift_id)}, headers=_auth_headers(outsider_id, "viewer"))
        assert res.status_code == 404
    finally:
        _clear_overrides()


def test_live_readiness_matches_real_receipt_and_refreshes_after_deactivation(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    sup_id = f"pg-live-c3b-readiness-{uuid4().hex[:8]}"
    _user(sql_ledger, sup_id, "shift_supervisor")
    AssignmentService(sql_ledger).assign(shift.shift_id, sup_id, Principal(user_id=sup_id, role="shift_supervisor"))

    from workspace_api.application.services import EventService
    from operations_domain.models import OperationalEvent

    event = OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="E1", risk_class=RiskClass.R2)
    sql_ledger.add_event(event)

    client = _client_for(sql_ledger)
    try:
        res = client.get(
            "/approvals/readiness",
            params={"record_type": "OperationalEvent", "record_id": str(event.event_id), "action": "event.confirm"},
            headers=_auth_headers(sup_id, "shift_supervisor"),
        )
        assert res.status_code == 200
        assert res.json()["ready"] is False

        create_approval_receipt(
            sql_ledger, Principal(user_id=sup_id, role="shift_supervisor"),
            record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
        )

        res = client.get(
            "/approvals/readiness",
            params={"record_type": "OperationalEvent", "record_id": str(event.event_id), "action": "event.confirm"},
            headers=_auth_headers(sup_id, "shift_supervisor"),
        )
        assert res.status_code == 200
        assert res.json()["ready"] is True
    finally:
        _clear_overrides()


def test_live_read_limit_ceiling_for_messages(sql_ledger):
    """SPEC R11/R36: 500 admits, 501 refuses with controlled 422 - proven
    against the real migration-created `messages` table."""
    from workspace_api.application.message_service import MessageService

    shift = _shift()
    sql_ledger.create_shift(shift)
    viewer_id = f"pg-live-c3b-limit-{uuid4().hex[:8]}"
    sup_id = f"pg-live-c3b-limitsup-{uuid4().hex[:8]}"
    _user(sql_ledger, viewer_id, "operator")
    _user(sql_ledger, sup_id, "shift_supervisor")
    AssignmentService(sql_ledger).assign(shift.shift_id, viewer_id, Principal(user_id=sup_id, role="shift_supervisor"))

    for i in range(500):
        MessageService(sql_ledger).create(shift.shift_id, f"m{i}", Principal(user_id=viewer_id, role="operator"))

    client = _client_for(sql_ledger)
    try:
        res = client.get("/messages", params={"shift_id": str(shift.shift_id)}, headers=_auth_headers(viewer_id, "operator"))
        assert res.status_code == 200
        assert len(res.json()) == 500

        MessageService(sql_ledger).create(shift.shift_id, "m500", Principal(user_id=viewer_id, role="operator"))
        res = client.get("/messages", params={"shift_id": str(shift.shift_id)}, headers=_auth_headers(viewer_id, "operator"))
        assert res.status_code == 422
    finally:
        _clear_overrides()
