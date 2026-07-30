"""Opt-in live PostgreSQL 16 message-admission suite
(MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC R12).

Every test below requires LIVE_POSTGRES_DATABASE_URL, set only by
scripts/run_postgres_live_roundtrip.py after applying migrations against a
disposable container; without it they skip. NEVER calls
metadata.create_all() and NEVER falls back to SQLite - the migration is the
schema authority.

Proves the real AUTHENTICATED API/service path required by SPEC R12: a
minted operator JWT through the real FastAPI POST /messages route
(get_ledger overridden to the live PostgreSQL-backed SqlLedger), mirroring
test_shift_create_postgres_live.py's SCR-BUILD-REV-F1 repair pattern - not a
bare MessageService(ledger).create(..., Principal(...)) call that bypasses
JWT verification.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine

from workspace_api.application.shift_service import ShiftService
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
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R12)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


@pytest.fixture()
def client(sql_ledger):
    app.dependency_overrides[get_ledger] = lambda: sql_ledger
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    return ShiftService(ledger).create(
        "Live PG shift", now, now + timedelta(hours=8), Principal(user_id="setup-op", role="operator")
    )


def _post_create(client_, shift_id, text_, headers=None):
    return client_.post(
        "/messages",
        json={"shift_id": str(shift_id), "text": text_},
        headers=headers if headers is not None else _OPERATOR_HEADERS,
    )


def _assert_exact_r6_audit(audit_row: dict, *, message_id: str) -> None:
    """MAR-BUILD-REV-F4 (SPEC R24): verify every exact R6 audit field, not
    just action/actor_id."""
    meta = audit_row["metadata"]
    assert audit_row["actor_id"] == "op1"
    assert meta["actor_role"] == "operator"
    assert audit_row["action"] == "message.create"
    assert audit_row["target_type"] == "Message"
    assert audit_row["target_id"] == message_id
    assert list(meta["control_chain"]) == ["identity", "permission", "create", "audit"]
    assert meta["before_state"] is None
    assert meta["after_state"] == "RAW"


def test_create_persists_message_and_actor_bound_audit(client, sql_ledger):
    shift = _new_shift(sql_ledger)
    res = _post_create(client, shift.shift_id, "hello live pg")
    assert res.status_code == 200
    body = res.json()
    assert body["sender_id"] == "op1"
    assert body["source"] == "INTERNAL"

    fetched = sql_ledger.get_message(body["message_id"])
    assert fetched.text == "hello live pg"

    audits = sql_ledger.audit_entries_for(body["message_id"])
    assert len(audits) == 1
    _assert_exact_r6_audit(audits[0], message_id=body["message_id"])


def test_message_and_audit_survive_reconnect(client, sql_ledger, live_database_url):
    shift = _new_shift(sql_ledger)
    res = _post_create(client, shift.shift_id, "night note")
    assert res.status_code == 200
    message_id = res.json()["message_id"]
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    fetched = fresh.get_message(message_id)
    audits = fresh.audit_entries_for(message_id)

    assert fetched.text == "night note"
    assert len(audits) == 1
    _assert_exact_r6_audit(audits[0], message_id=message_id)


def test_raw_payload_is_null_for_internal_writes(sql_ledger):
    shift = _new_shift(sql_ledger)
    from operations_domain.models import Message

    message = Message(shift_id=shift.shift_id, sender_id="op1", text="internal only")
    sql_ledger.add_message(message)

    with sql_ledger.engine.connect() as conn:
        from operations_ledger.tables import messages

        raw_payload = conn.execute(
            messages.select().where(messages.c.message_id == message.message_id)
        ).mappings().first()["raw_payload"]
    assert raw_payload is None


class _Boom(Exception):
    pass


def test_injected_audit_failure_rolls_back_message_creation(client, sql_ledger, live_database_url):
    from unittest.mock import patch

    shift = _new_shift(sql_ledger)
    with patch.object(SqlLedger, "append_audit", side_effect=_Boom("simulated audit sink failure")):
        with pytest.raises(_Boom):
            _post_create(client, shift.shift_id, "rollback text")

    fresh = _reconnected(live_database_url)
    with fresh.engine.connect() as conn:
        from operations_ledger.tables import messages

        rows = conn.execute(
            messages.select().where(messages.c.shift_id == shift.shift_id)
        ).mappings().all()
    assert rows == []


def test_frozen_shift_refusal_leaves_no_partial_rows(client, sql_ledger):
    """MAR-BUILD-REV-F4 (SPEC R24): asserts zero new message rows for this
    shift and zero NEW message.create audit rows (delta against a snapshot
    taken right before the refusal - audit_records has no shift_id column,
    and this live database is shared/cumulative across the whole test
    session, so a global post-hoc count would false-fail on unrelated
    messages already created by earlier tests), not just the status code."""
    from operations_ledger.tables import audit_records, messages

    shift = _new_shift(sql_ledger)
    sql_ledger.close_shift(shift.shift_id)
    sql_ledger.freeze_shift(shift.shift_id)

    with sql_ledger.engine.connect() as conn:
        audits_before = conn.execute(
            audit_records.select().where(audit_records.c.action == "message.create")
        ).mappings().all()

    res = _post_create(client, shift.shift_id, "too late")
    assert res.status_code == 409

    with sql_ledger.engine.connect() as conn:
        rows = conn.execute(messages.select().where(messages.c.shift_id == shift.shift_id)).mappings().all()
        audits_after = conn.execute(
            audit_records.select().where(audit_records.c.action == "message.create")
        ).mappings().all()
        assert conn.execute(text("SELECT 1")).scalar() == 1  # connection usable after refusal
    assert rows == []
    assert len(audits_after) == len(audits_before)


def test_duplicate_message_id_refusal_leaves_no_partial_rows(sql_ledger):
    """MAR-BUILD-REV-F4 (SPEC R24): exactly the original row remains, no
    extra audit (delta against a snapshot taken right before the duplicate
    attempt, since audit_records is shared/cumulative across the whole live
    test session), connection usable after the refusal."""
    from operations_domain.models import Message
    from operations_ledger.tables import audit_records, messages

    shift = _new_shift(sql_ledger)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="first")
    sql_ledger.add_message(message)

    with sql_ledger.engine.connect() as conn:
        audits_before = conn.execute(
            audit_records.select().where(audit_records.c.action == "message.create")
        ).mappings().all()

    with pytest.raises(ValueError, match="duplicate message_id"):
        sql_ledger.add_message(message)

    with sql_ledger.engine.connect() as conn:
        rows = conn.execute(messages.select().where(messages.c.shift_id == shift.shift_id)).mappings().all()
        audits_after = conn.execute(
            audit_records.select().where(audit_records.c.action == "message.create")
        ).mappings().all()
        assert conn.execute(text("SELECT 1")).scalar() == 1  # connection usable after refusal
    assert len(rows) == 1
    assert rows[0]["message_id"] == message.message_id
    assert rows[0]["text_content"] == "first"
    assert len(audits_after) == len(audits_before)


def test_connection_remains_usable_after_rollback_case(client, sql_ledger):
    from unittest.mock import patch

    shift = _new_shift(sql_ledger)
    with patch.object(SqlLedger, "append_audit", side_effect=_Boom("simulated audit sink failure")):
        with pytest.raises(_Boom):
            _post_create(client, shift.shift_id, "usability text")

    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1

    res2 = _post_create(client, shift.shift_id, "post-rollback text")
    assert res2.status_code == 200
    assert sql_ledger.get_message(res2.json()["message_id"]).text == "post-rollback text"
