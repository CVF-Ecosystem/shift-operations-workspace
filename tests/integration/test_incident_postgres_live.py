"""Opt-in live PostgreSQL 16 incident suite (fifth vertical, P2-A).

Split from test_sql_ledger_postgres_live.py (INC-AUTH-F2): that module is
already at the file-size guard's ceiling, so incident live coverage lives
here instead. Same opt-in contract: every test below requires
LIVE_POSTGRES_DATABASE_URL, set only by scripts/run_postgres_live_roundtrip.py
after applying database/migrations/001-005 against a disposable container;
without it they skip. NEVER calls metadata.create_all() and NEVER falls back
to SQLite - the migration is the schema authority (SPEC R13).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect as sa_inspect, insert, text
from sqlalchemy.exc import IntegrityError

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger import tables as t

from workspace_api.application import approval_service
from workspace_api.application.incident_service import IncidentService
from workspace_api.domain import models as domain_models
from operations_domain.models import EvidenceRef, Incident, RiskClass, Shift

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R13)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Live PG shift", starts_at=now, ends_at=now + timedelta(hours=8), **kw)


def test_live_incidents_table_and_enum_present(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    assert "incidents" in inspector.get_table_names()
    with sql_ledger.engine.connect() as conn:
        enums = {r[0] for r in conn.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e'"))}
    assert "risk_class" in enums


def test_live_incidents_column_and_check_parity(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("incidents")}
    code_cols = {c.name for c in t.incidents.columns}
    assert live_cols == code_cols
    live_pk = set(inspector.get_pk_constraint("incidents")["constrained_columns"])
    assert live_pk == {"incident_id"}
    live_fks = {(fk["referred_table"], fk["referred_columns"][0]) for fk in inspector.get_foreign_keys("incidents")}
    assert live_fks == {("shifts", "shift_id")}
    assert len(inspector.get_check_constraints("incidents")) >= 1


def test_incident_round_trip_survives_reconnect(sql_ledger, live_database_url):
    shift = _shift()
    sql_ledger.create_shift(shift)
    incident = Incident(
        shift_id=shift.shift_id, summary="Crane stopped", risk_class=RiskClass.R2,
        evidence=[EvidenceRef(source_type="message", source_id="m1", sha256="ab" * 32)],
    )
    sql_ledger.add_incident(incident)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_incident(incident.incident_id)
    assert got.summary == "Crane stopped" and got.status.value == "REPORTED"
    assert len(got.evidence) == 1 and got.evidence[0].sha256 == "ab" * 32


def test_incident_acknowledge_persists_and_audits_through_reconnect(sql_ledger, live_database_url):
    # P2C-MUTATION-FULL-UI-C3A2 (WO section 3.5): incident.report/acknowledge
    # now require the caller's persisted ACTIVE assignment on the shift.
    shift = _shift()
    sql_ledger.create_shift(shift)
    sql_ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))
    incident = Incident(
        shift_id=shift.shift_id, summary="Crane stopped", risk_class=RiskClass.R2,
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    reported = IncidentService(sql_ledger).report(incident, Principal(user_id="op1", role="operator"))

    approver_id = f"pg-live-inc-{uuid4().hex[:8]}"
    sql_ledger.add_user(domain_models.User(user_id=approver_id, username=approver_id, password_hash="x", role="shift_supervisor"))
    sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=approver_id, assigned_by=approver_id))
    approval_service.create_approval_receipt(
        sql_ledger, Principal(user_id=approver_id, role="shift_supervisor"),
        record_type="Incident", action="incident.acknowledge", record_id=reported.incident_id,
    )
    confirmer = Principal(user_id="pg-live-inc-confirmer", role="shift_supervisor")
    sql_ledger.add_user(domain_models.User(user_id=confirmer.user_id, username=confirmer.user_id, password_hash="x", role="shift_supervisor"))
    sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=confirmer.user_id, assigned_by=confirmer.user_id))
    IncidentService(sql_ledger).acknowledge(reported.incident_id, confirmer)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_incident(reported.incident_id)
    audits = fresh.audit_entries_for(str(reported.incident_id))
    assert got.status.value == "ACKNOWLEDGED" and got.version == 2
    assert {"incident.report", "incident.acknowledge"} <= {a["action"] for a in audits}


def _rejected_then_usable(engine, values_builder):
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(values_builder(conn))
    with engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_incident_with_unknown_shift_rejected(sql_ledger):
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.incidents).values(
        incident_id=uuid4(), shift_id=uuid4(), summary="orphan", status="REPORTED", version=1))


def test_incident_status_outside_check_constraint_rejected(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.incidents).values(
        incident_id=uuid4(), shift_id=shift.shift_id, summary="bad", status="NOT_A_REAL_STATUS", version=1))


def test_incident_version_below_one_rejected_by_live_database_check(sql_ledger):
    """INC-REV-F4: the real PostgreSQL CHECK, not just SQLite's, must reject
    version < 1 - even bypassing the Pydantic model via a raw INSERT."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.incidents).values(
        incident_id=uuid4(), shift_id=shift.shift_id, summary="bad", status="REPORTED", version=0))


def test_incident_transaction_rollback_removes_all_writes(sql_ledger, live_database_url):
    shift = _shift()
    sql_ledger.create_shift(shift)
    incident = Incident(shift_id=shift.shift_id, summary="s")

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with sql_ledger.transaction() as unit:
            sql_ledger.add_incident(incident, unit=unit)
            raise _Boom("simulated failure")

    fresh = _reconnected(live_database_url)
    with pytest.raises(KeyError):
        fresh.get_incident(incident.incident_id)
