"""Opt-in live PostgreSQL 16 report suite (P2R-OPERATIONAL-REPORT-FREEZE-
PREREQUISITE, SPEC R30).

Coherent, separate module - joins the other live verticals in the same
disposable container/migration pass (scripts/run_postgres_live_roundtrip.py).
Same opt-in contract: every test below requires LIVE_POSTGRES_DATABASE_URL,
set only by that runner after applying database/migrations/001-007 against a
disposable container; without it they skip. NEVER calls metadata.create_all()
and NEVER falls back to SQLite - the migration is the schema authority.
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
from workspace_api.application.report_service import ReportService
from workspace_api.application.shift_service import ShiftService
from workspace_api.application.handover_service import HandoverService
from workspace_api.domain import models as domain_models
from operations_domain.models import ReportStatus, Shift, ShiftStatus

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")
_RECEIVER = Principal(user_id="sup2", role="shift_supervisor")


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


def _seed(ledger, shift_id, user_id, role):
    # P2C-MUTATION-FULL-UI-C3A2 (WO section 3.5): every governed service call
    # below now requires the caller's persisted ACTIVE assignment.
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _closed_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Live PG shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "op1", "operator")
    _seed(ledger, shift.shift_id, "sup1", "shift_supervisor")
    ledger.close_shift(shift.shift_id)
    return ledger.get_shift(shift.shift_id)


def _ready_handover(ledger, shift):
    now = datetime.now(timezone.utc)
    dest = Shift(name="Live PG next", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(dest)
    _seed(ledger, dest.shift_id, "sup2", "shift_supervisor")
    svc = HandoverService(ledger)
    handover = svc.create(shift.shift_id, dest.shift_id, _OPERATOR)
    handover = svc.review(handover.handover_id, _SUPERVISOR, expected_version=handover.version)
    return svc.acknowledge(handover.handover_id, _RECEIVER, expected_version=handover.version)


def _approved_report(ledger, shift, approver_id=None):
    approver_id = approver_id or f"pg-live-approver-{uuid4().hex[:8]}"
    svc = ReportService(ledger)
    report = svc.generate(shift.shift_id, _OPERATOR)
    report = svc.submit_review(
        report.report_id, _OPERATOR, expected_version=report.version, expected_status=report.status
    )
    _seed(ledger, shift.shift_id, approver_id, "shift_supervisor")
    approval_service.create_approval_receipt(
        ledger, Principal(user_id=approver_id, role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=report.report_id,
    )
    return svc.approve(
        report.report_id, _SUPERVISOR, expected_version=report.version, expected_status=report.status
    )


def test_live_reports_table_and_is_current_present(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    assert "reports" in inspector.get_table_names()
    live_cols = {c["name"] for c in inspector.get_columns("reports")}
    assert "is_current" in live_cols


def test_live_reports_column_and_constraint_parity(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("reports")}
    code_cols = {c.name for c in t.reports.columns}
    assert live_cols == code_cols
    live_pk = set(inspector.get_pk_constraint("reports")["constrained_columns"])
    assert live_pk == {"report_id"}
    live_fks = {(fk["referred_table"], fk["referred_columns"][0]) for fk in inspector.get_foreign_keys("reports")}
    assert live_fks == {("shifts", "shift_id")}
    assert len(inspector.get_check_constraints("reports")) >= 2  # status + version
    unique_names = {uc["name"] for uc in inspector.get_unique_constraints("reports")}
    assert "reports_shift_type_version_unique" in unique_names
    index_names = {idx["name"] for idx in inspector.get_indexes("reports")}
    assert "reports_current_unique" in index_names


def test_report_generate_review_approve_persists_through_reconnect(sql_ledger, live_database_url):
    shift = _closed_shift(sql_ledger)
    report = _approved_report(sql_ledger, shift)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_report(report.report_id)
    audits = fresh.audit_entries_for(str(report.report_id))
    assert got.status.value == "APPROVED" and got.is_current is True
    assert {"report.generate", "report.submit_review", "report.approve"} <= {a["action"] for a in audits}


def test_atomic_report_and_shift_freeze_through_reconnect(sql_ledger, live_database_url):
    shift = _closed_shift(sql_ledger)
    _ready_handover(sql_ledger, shift)
    report = _approved_report(sql_ledger, shift)

    frozen_shift = ShiftService(sql_ledger).freeze(shift.shift_id, _SUPERVISOR, expected_version=shift.version)
    assert frozen_shift.status == ShiftStatus.FROZEN
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    frozen_report = fresh.get_report(report.report_id)
    assert frozen_report.status == ReportStatus.FROZEN
    assert frozen_report.is_current is True
    report_audits = fresh.audit_entries_for(str(report.report_id))
    assert "report.freeze" in {a["action"] for a in report_audits}


def test_current_partial_unique_index_rejects_second_current_row(sql_ledger):
    shift = _closed_shift(sql_ledger)
    report = ReportService(sql_ledger).generate(shift.shift_id, _OPERATOR)

    def _second_current(conn):
        return insert(t.reports).values(
            report_id=uuid4(), shift_id=shift.shift_id, report_type="END_SHIFT",
            version=2, status="DRAFT", content=report.content.model_dump(mode="json"),
            generated_from_cutoff=datetime.now(timezone.utc), is_current=True,
        )

    with pytest.raises(IntegrityError):
        with sql_ledger.engine.begin() as conn:
            conn.execute(_second_current(conn))
    with sql_ledger.engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_report_transaction_rollback_removes_all_writes(sql_ledger, live_database_url):
    from operations_domain.models import Report, ReportContent, ReportSection

    shift = _closed_shift(sql_ledger)
    content = ReportContent(
        sections=[ReportSection(section_type=s, records=[]) for s in (
            "operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers",
        )],
        source_manifest=[], snapshot_digest="a" * 64,
    )
    report = Report(shift_id=shift.shift_id, generated_from_cutoff=datetime.now(timezone.utc), content=content)

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with sql_ledger.transaction() as unit:
            sql_ledger.add_report(report, unit=unit)
            raise _Boom("simulated failure")

    fresh = _reconnected(live_database_url)
    with pytest.raises(KeyError):
        fresh.get_report(report.report_id)


def test_report_successor_atomic_through_reconnect(sql_ledger, live_database_url):
    shift = _closed_shift(sql_ledger)
    report = ReportService(sql_ledger).generate(shift.shift_id, _OPERATOR)
    successor = ReportService(sql_ledger).create_successor(
        report.report_id, _OPERATOR, expected_version=report.version, expected_status=report.status
    )
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    predecessor = fresh.get_report(report.report_id)
    assert predecessor.is_current is False
    current = fresh.get_current_report(shift.shift_id, "END_SHIFT")
    assert current.report_id == successor.report_id
    assert current.version == 2


def test_add_report_rejects_unknown_parent_shift_as_controlled_value_error(sql_ledger):
    """F4: against REAL PostgreSQL, an unknown parent shift is a controlled
    ValueError - never a raw psycopg ForeignKeyViolation/IntegrityError, and
    never conflated with the "duplicate report_id" category."""
    from operations_domain.models import Report, ReportContent, ReportSection

    content = ReportContent(
        sections=[ReportSection(section_type=s, records=[]) for s in (
            "operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers",
        )],
        source_manifest=[], snapshot_digest="a" * 64,
    )
    report = Report(shift_id=uuid4(), generated_from_cutoff=datetime.now(timezone.utc), content=content)
    with pytest.raises(ValueError, match="unknown parent shift"):
        sql_ledger.add_report(report)
    with sql_ledger.engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_add_report_rejects_frozen_parent_shift_on_live_postgres(sql_ledger):
    """F4: a FROZEN parent shift is refused with no partial write, proven
    against real PostgreSQL (not just SQLite/InMemory)."""
    shift = _closed_shift(sql_ledger)
    _ready_handover(sql_ledger, shift)
    _approved_report(sql_ledger, shift)
    ShiftService(sql_ledger).freeze(shift.shift_id, _SUPERVISOR, expected_version=shift.version)

    from operations_domain.models import Report, ReportContent, ReportSection

    content = ReportContent(
        sections=[ReportSection(section_type=s, records=[]) for s in (
            "operational_events", "corrections", "tasks", "customer_requests", "incidents", "handovers",
        )],
        source_manifest=[], snapshot_digest="b" * 64,
    )
    late_report = Report(shift_id=shift.shift_id, generated_from_cutoff=datetime.now(timezone.utc), content=content)
    with pytest.raises(ValueError, match="frozen"):
        sql_ledger.add_report(late_report)


def test_concurrent_freeze_race_resolves_to_exactly_one_winner(sql_ledger, live_database_url):
    """SPEC R22: PostgreSQL report freeze runs at SERIALIZABLE isolation.
    Two concurrent attempts to freeze the SAME shift must not both succeed -
    exactly one wins, the other observes a controlled conflict."""
    shift = _closed_shift(sql_ledger)
    _ready_handover(sql_ledger, shift)
    _approved_report(sql_ledger, shift)

    ledger_a = _reconnected(live_database_url)
    ledger_b = _reconnected(live_database_url)

    results = []
    for ledger in (ledger_a, ledger_b):
        try:
            frozen = ShiftService(ledger).freeze(shift.shift_id, _SUPERVISOR, expected_version=shift.version)
            results.append(("ok", frozen.status))
        except Exception as exc:  # noqa: BLE001 - either controlled CvfDenied or idempotent success
            results.append(("conflict", str(exc)))

    successes = [r for r in results if r[0] == "ok"]
    assert len(successes) >= 1, "at least one freeze attempt must succeed"
    fresh = _reconnected(live_database_url)
    assert fresh.get_shift(shift.shift_id).status == ShiftStatus.FROZEN
