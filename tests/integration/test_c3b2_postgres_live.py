"""Opt-in live PostgreSQL 16 CustomerRequest version/CAS suite
(P2C-MUTATION-FULL-UI-C3B2, SPEC R12/R13/R14, AC-12).

Coherent, separate module - joins the other live verticals in the same
disposable container/migration pass (scripts/run_postgres_live_roundtrip.py).
Same opt-in contract: every test below requires LIVE_POSTGRES_DATABASE_URL,
set only by that runner after applying database/migrations/001-009 against a
disposable container; without it they skip. NEVER calls metadata.create_all()
and NEVER falls back to SQLite - the migration is the schema authority.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import inspect as sa_inspect

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger import tables as t

from workspace_api.application.customer_request_service import CustomerRequestService
from workspace_api.domain import models as domain_models
from operations_domain.models import CustomerRequest, CustomerRequestStatus, Shift

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"

_OPERATOR = Principal(user_id="op1", role="operator")


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _seed_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Live PG C3b2 shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    if ledger.get_user_by_id("op1") is None:
        ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))
    return shift


def test_live_customer_requests_table_has_version_column(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("customer_requests")}
    assert "version" in live_cols
    code_cols = {c.name for c in t.customer_requests.columns}
    assert live_cols == code_cols


def test_live_customer_requests_version_check_constraint_present(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    checks = inspector.get_check_constraints("customer_requests")
    assert any("customer_requests_version_check" in (c.get("name") or "") for c in checks)


def test_create_persists_version_one_through_reconnect(sql_ledger, live_database_url):
    shift = _seed_shift(sql_ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(sql_ledger).create_customer_request(request, _OPERATOR)
    assert created.version == 1
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    fetched = fresh.get_customer_request(created.request_id)
    assert fetched.version == 1


def test_transition_increments_version_exactly_once_through_reconnect(sql_ledger, live_database_url):
    shift = _seed_shift(sql_ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(sql_ledger).create_customer_request(request, _OPERATOR)

    moved = CustomerRequestService(sql_ledger).transition(
        created.request_id, _OPERATOR, CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )
    assert moved.version == 2
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    fetched = fresh.get_customer_request(created.request_id)
    assert fetched.status.value == "ACKNOWLEDGED"
    assert fetched.version == 2


def test_stale_version_transition_is_409_with_zero_partial_write_on_live_postgres(sql_ledger):
    shift = _seed_shift(sql_ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(sql_ledger).create_customer_request(request, _OPERATOR)
    CustomerRequestService(sql_ledger).transition(
        created.request_id, _OPERATOR, CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
    )

    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(sql_ledger).transition(
            created.request_id, _OPERATOR, CustomerRequestStatus.IN_PROGRESS, expected_version=created.version
        )
    assert exc.value.http_status == 409

    fetched = sql_ledger.get_customer_request(created.request_id)
    assert fetched.status.value == "ACKNOWLEDGED", "stale transition must not have partially applied"
    assert fetched.version == 2


def test_missing_expected_version_transition_is_422_with_zero_write_on_live_postgres(sql_ledger):
    shift = _seed_shift(sql_ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(sql_ledger).create_customer_request(request, _OPERATOR)

    with pytest.raises(CvfDenied) as exc:
        CustomerRequestService(sql_ledger).transition(
            created.request_id, _OPERATOR, CustomerRequestStatus.ACKNOWLEDGED, expected_version=None
        )
    assert exc.value.http_status == 422

    fetched = sql_ledger.get_customer_request(created.request_id)
    assert fetched.status.value == "NEW"
    assert fetched.version == 1


def test_concurrent_transition_race_resolves_to_exactly_one_winner(sql_ledger, live_database_url):
    """A stale-reading second caller must observe a controlled 409, never a
    silently overwritten row - proven against real PostgreSQL, not SQLite."""
    shift = _seed_shift(sql_ledger)
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="s")
    created = CustomerRequestService(sql_ledger).create_customer_request(request, _OPERATOR)

    ledger_a = _reconnected(live_database_url)
    ledger_b = _reconnected(live_database_url)

    results = []
    for ledger in (ledger_a, ledger_b):
        try:
            moved = CustomerRequestService(ledger).transition(
                created.request_id, _OPERATOR, CustomerRequestStatus.ACKNOWLEDGED, expected_version=created.version
            )
            results.append(("ok", moved.version))
        except CvfDenied as exc:
            results.append(("denied", exc.http_status))

    successes = [r for r in results if r[0] == "ok"]
    denials = [r for r in results if r[0] == "denied"]
    assert len(successes) == 1
    assert len(denials) == 1 and denials[0][1] == 409

    fresh = _reconnected(live_database_url)
    assert fresh.get_customer_request(created.request_id).version == 2
