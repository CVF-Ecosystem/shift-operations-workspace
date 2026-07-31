"""Opt-in live PostgreSQL 16 shift-assignment suite (P2C-MUTATION-FULL-UI-C3A1).

Same opt-in contract as test_incident_postgres_live.py: every test below
requires LIVE_POSTGRES_DATABASE_URL, set only by
scripts/run_postgres_live_roundtrip.py after applying database/migrations/
001-008 against a disposable container; without it they skip. NEVER calls
metadata.create_all(), NEVER falls back to SQLite - the migration is the
schema authority (SPEC R2)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect as sa_inspect, insert, text
from sqlalchemy.exc import IntegrityError

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger import tables as t

from workspace_api.application.assignment_service import AssignmentService
from workspace_api.application.shift_service import ShiftService
from workspace_api.domain import models as domain_models
from cvf_runtime.identity import Principal
from operations_domain.models import Shift

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R2)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Live PG assignment shift", starts_at=now, ends_at=now + timedelta(hours=8), **kw)


def _user(ledger, user_id, role="operator"):
    ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))


def test_live_shift_assignments_table_present(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    assert "shift_assignments" in inspector.get_table_names()


def test_live_shift_assignments_column_and_fk_parity(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("shift_assignments")}
    code_cols = {c.name for c in t.shift_assignments.columns}
    assert live_cols == code_cols
    live_pk = set(inspector.get_pk_constraint("shift_assignments")["constrained_columns"])
    assert live_pk == {"assignment_id"}
    live_fks = {(fk["referred_table"], fk["referred_columns"][0]) for fk in inspector.get_foreign_keys("shift_assignments")}
    assert live_fks == {("shifts", "shift_id"), ("users", "user_id")}
    assert len(inspector.get_check_constraints("shift_assignments")) >= 2


def test_bootstrap_assignment_round_trip_survives_reconnect(sql_ledger, live_database_url):
    user_id = f"pg-live-assign-{uuid4().hex[:8]}"
    _user(sql_ledger, user_id)
    shift = ShiftService(sql_ledger).create(
        "Live PG bootstrap", datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(hours=8),
        Principal(user_id=user_id, role="operator"),
    )
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    active = fresh.get_active_assignment(shift.shift_id, user_id)
    assert active is not None
    assert active.status.value == "ACTIVE"
    assert active.assigned_by == user_id


def test_staffing_assign_and_revoke_persists_through_reconnect(sql_ledger, live_database_url):
    shift = _shift()
    sql_ledger.create_shift(shift)
    sup_id = f"pg-live-sup-{uuid4().hex[:8]}"
    op_id = f"pg-live-op-{uuid4().hex[:8]}"
    _user(sql_ledger, sup_id, "shift_supervisor")
    _user(sql_ledger, op_id)

    created = AssignmentService(sql_ledger).assign(shift.shift_id, op_id, Principal(user_id=sup_id, role="shift_supervisor"))
    revoked = AssignmentService(sql_ledger).revoke(shift.shift_id, created.assignment_id, 1, Principal(user_id=sup_id, role="shift_supervisor"))
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_assignment(created.assignment_id)
    assert got.status.value == "REVOKED"
    assert got.version == 2 == revoked.version
    audits = fresh.audit_entries_for(str(created.assignment_id))
    assert {"shift.assignment.manage"} <= {a["action"] for a in audits}


def _rejected_then_usable(engine, values_builder):
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(values_builder(conn))
    with engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_duplicate_active_assignment_rejected_by_live_partial_unique_index(sql_ledger):
    """R2: the partial unique index (not just application logic) enforces at
    most one ACTIVE assignment per (shift_id, user_id) on real PostgreSQL."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-dup-{uuid4().hex[:8]}"
    sup_id = f"pg-live-dupsup-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    AssignmentService(sql_ledger).assign(shift.shift_id, op_id, Principal(user_id=sup_id, role="shift_supervisor"))
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.shift_assignments).values(
        assignment_id=uuid4(), shift_id=shift.shift_id, user_id=op_id, status="ACTIVE",
        assigned_by=sup_id, version=1,
    ))


# Raw conn.execute - CHECK-constraint proof only; see _f1.py's test_live_add_assignment_rejects_* for the real ledger-path (F4) proof.
def test_assignment_status_outside_check_constraint_rejected(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-badstatus-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.shift_assignments).values(
        assignment_id=uuid4(), shift_id=shift.shift_id, user_id=op_id, status="NOT_A_REAL_STATUS",
        assigned_by=op_id, version=1,
    ))


def test_assignment_version_below_one_rejected_by_live_database_check(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-badversion-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _rejected_then_usable(sql_ledger.engine, lambda conn: insert(t.shift_assignments).values(
        assignment_id=uuid4(), shift_id=shift.shift_id, user_id=op_id, status="ACTIVE",
        assigned_by=op_id, version=0,
    ))


def test_assignment_transaction_rollback_removes_all_writes(sql_ledger, live_database_url):
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-rollback-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    assignment = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=op_id)

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with sql_ledger.transaction() as unit:
            sql_ledger.add_assignment(assignment, unit=unit)
            raise _Boom("simulated failure")

    fresh = _reconnected(live_database_url)
    with pytest.raises(KeyError):
        fresh.get_assignment(assignment.assignment_id)


# --- P2C-C3A1-BUILD-REV-F1: controlled reference validation on real PostgreSQL

def test_add_assignment_rejects_unknown_shift_with_controlled_error_not_raw_fk(sql_ledger):
    sup_id = f"pg-live-refsup-{uuid4().hex[:8]}"
    _user(sql_ledger, sup_id, "shift_supervisor")
    with pytest.raises(ValueError, match="unknown shift"):
        sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=uuid4(), user_id=sup_id, assigned_by=sup_id))
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_add_assignment_rejects_unknown_target_user_with_controlled_error(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    sup_id = f"pg-live-refsup2-{uuid4().hex[:8]}"
    _user(sql_ledger, sup_id, "shift_supervisor")
    with pytest.raises(ValueError, match="unknown target user"):
        sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="ghost-user", assigned_by=sup_id))
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_add_assignment_rejects_unknown_assigned_by_actor_with_controlled_error(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-refop-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    with pytest.raises(ValueError, match="unknown assigned_by actor"):
        sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by="ghost-actor"))
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_revoke_rejects_unknown_revoked_by_actor_with_controlled_error_and_no_partial_write(sql_ledger):
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-revby-{uuid4().hex[:8]}"
    sup_id = f"pg-live-revbysup-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")
    assignment = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    sql_ledger.add_assignment(assignment)

    with pytest.raises(ValueError, match="unknown revoked_by actor"):
        sql_ledger.revoke_assignment(assignment.assignment_id, revoked_by="ghost-revoker", expected_version=1)

    unchanged = sql_ledger.get_assignment(assignment.assignment_id)
    assert unchanged.status.value == "ACTIVE"
    assert unchanged.version == 1


# F1 amendment (duplicate assignment_id vs duplicate-active, classified via
# the real server-reported constraint identity) live tests moved to
# test_assignment_postgres_live_f1.py (Amendment 2 companion); reuse this
# module's `live_database_url`/`sql_ledger` fixtures and `_shift`/`_user`.

# --- P2C-C3A1-BUILD-REV-F3: atomic CAS revoke under real concurrency --------

def test_concurrent_revoke_exactly_one_winner_and_exactly_one_audit(live_database_url):
    """F3: two GENUINELY concurrent revoke attempts against the SAME
    assignment/version must resolve to exactly one winner (rowcount==1) and
    one controlled-409 loser (rowcount==0) - never two successes, never a
    silently-accepted loser re-reading the winner's row as its own, and never
    a second audit for the loser.

    Real threads with independent SqlLedger connections and a barrier force
    both to enter AssignmentService.revoke's read-then-write window at the
    same instant; PostgreSQL row-level locking on the UPDATE serializes the
    two writers, and the CAS `WHERE version = :expected` predicate is what
    decides the loser once its stale WHERE clause matches zero rows - this is
    the exact race the pre-repair SELECT-then-UPDATE code could lose."""
    import threading

    from workspace_api.application.assignment_service import AssignmentService

    ledger_setup = _reconnected(live_database_url)
    shift = _shift()
    ledger_setup.create_shift(shift)
    sup_id = f"pg-live-race-sup-{uuid4().hex[:8]}"
    op_id = f"pg-live-race-op-{uuid4().hex[:8]}"
    _user(ledger_setup, sup_id, "shift_supervisor")
    _user(ledger_setup, op_id)

    principal = Principal(user_id=sup_id, role="shift_supervisor")
    created = AssignmentService(ledger_setup).assign(shift.shift_id, op_id, principal)

    barrier = threading.Barrier(2)
    outcomes: list[tuple[str, str | None]] = []
    outcomes_lock = threading.Lock()

    def _attempt():
        ledger = _reconnected(live_database_url)
        barrier.wait(timeout=10)
        try:
            AssignmentService(ledger).revoke(shift.shift_id, created.assignment_id, 1, principal)
            outcome = ("won", None)
        except ValueError as exc:
            outcome = ("lost", str(exc))
        finally:
            ledger.engine.dispose()
        with outcomes_lock:
            outcomes.append(outcome)

    threads = [threading.Thread(target=_attempt) for _ in range(2)]
    for t_ in threads:
        t_.start()
    for t_ in threads:
        t_.join(timeout=30)

    labels = sorted(label for label, _ in outcomes)
    assert labels == ["lost", "won"], outcomes

    fresh = _reconnected(live_database_url)
    final = fresh.get_assignment(created.assignment_id)
    assert final.status.value == "REVOKED"
    assert final.version == 2

    audits = fresh.audit_entries_for(str(created.assignment_id))
    revoke_audits = [
        a for a in audits if a["action"] == "shift.assignment.manage" and a["metadata"]["before_state"] == "ACTIVE"
    ]
    assert len(revoke_audits) == 1, revoke_audits
