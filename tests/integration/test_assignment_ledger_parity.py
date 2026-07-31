"""Cross-backend (InMemory/SQLite) parity for shift-assignment persistence
(P2C-MUTATION-FULL-UI-C3A1, SPEC R2/R3, AC-01). Both backends must agree on
add/get/list/revoke/current-membership behavior, duplicate-active rejection,
exact revoke version/idempotency semantics, and rollback of a mid-transaction
failure - the same class of proof test_ledger_protocol.py already applies to
every other vertical.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from operations_domain.models import Shift
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger


def _sql_ledger(tmp_path, name="assignment_parity.sqlite3"):
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _user(ledger, user_id, role="operator"):
    ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_get_list_active_assignment_roundtrip(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    a = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(a)

    fetched = ledger.get_assignment(a.assignment_id)
    assert fetched.assignment_id == a.assignment_id
    assert fetched.status.value == "ACTIVE"

    active = ledger.get_active_assignment(shift.shift_id, "op1")
    assert active is not None
    assert active.assignment_id == a.assignment_id

    listed = ledger.list_assignments_for_shift(shift.shift_id)
    assert [x.assignment_id for x in listed] == [a.assignment_id]


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_active_assignment_rejected_same_shape_both_backends(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))

    with pytest.raises(ValueError):
        ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_revoke_exact_version_and_idempotency_semantics(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    a = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(a)

    revoked = ledger.revoke_assignment(a.assignment_id, revoked_by="sup1", expected_version=1)
    assert revoked.status.value == "REVOKED"
    assert revoked.version == 2
    assert revoked.revoked_by == "sup1"
    assert revoked.revoked_at is not None

    idempotent = ledger.revoke_assignment(a.assignment_id, revoked_by="sup1", expected_version=2)
    assert idempotent.version == 2
    assert idempotent.status.value == "REVOKED"

    with pytest.raises(ValueError):
        ledger.revoke_assignment(a.assignment_id, revoked_by="sup1", expected_version=1)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_revoked_assignment_is_retained_as_history_not_deleted(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    a = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(a)
    ledger.revoke_assignment(a.assignment_id, revoked_by="sup1", expected_version=1)

    listed = ledger.list_assignments_for_shift(shift.shift_id)
    assert len(listed) == 1
    assert listed[0].status.value == "REVOKED"
    assert ledger.get_active_assignment(shift.shift_id, "op1") is None


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_reassignment_after_revoke_is_allowed(tmp_path, name):
    """Revoking frees the (shift_id, user_id) pair for a fresh ACTIVE grant -
    the partial unique index only blocks a SECOND simultaneous ACTIVE row."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    first = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(first)
    ledger.revoke_assignment(first.assignment_id, revoked_by="sup1", expected_version=1)

    second = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(second)
    active = ledger.get_active_assignment(shift.shift_id, "op1")
    assert active.assignment_id == second.assignment_id

    listed = ledger.list_assignments_for_shift(shift.shift_id)
    assert len(listed) == 2


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_active_users_excludes_inactive(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    _user(ledger, "op1")
    ledger.add_user(User(user_id="inactive1", username="inactive1", password_hash="x", role="operator", is_active=False))

    active_ids = {u["user_id"] for u in ledger.list_active_users()}
    assert "op1" in active_ids
    assert "inactive1" not in active_ids


# --- P2C-C3A1-BUILD-REV-F1: controlled reference validation, both backends -

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_assignment_rejects_unknown_shift(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    import uuid

    with pytest.raises(ValueError, match="unknown shift"):
        ledger.add_assignment(ShiftAssignment(shift_id=uuid.uuid4(), user_id="op1", assigned_by="sup1"))
    assert ledger.list_assignments_for_shift(uuid.uuid4()) == []


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_assignment_rejects_unknown_target_user(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "sup1", "shift_supervisor")

    with pytest.raises(ValueError, match="unknown target user"):
        ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="ghost", assigned_by="sup1"))
    assert ledger.list_assignments_for_shift(shift.shift_id) == []


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_assignment_rejects_unknown_assigned_by_actor(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")

    with pytest.raises(ValueError, match="unknown assigned_by actor"):
        ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="ghost"))
    assert ledger.list_assignments_for_shift(shift.shift_id) == []


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_add_assignment_missing_reference_error_is_distinct_from_duplicate_active(tmp_path, name):
    """F1: a missing-reference failure must never be mislabeled as the
    genuine duplicate-active-assignment error, and vice versa."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    with pytest.raises(ValueError) as missing_exc:
        ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="ghost", assigned_by="sup1"))
    assert "duplicate" not in str(missing_exc.value)

    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    with pytest.raises(ValueError) as dup_exc:
        ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    assert "duplicate active assignment" in str(dup_exc.value)
    assert "unknown" not in str(dup_exc.value)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_revoke_rejects_unknown_revoked_by_actor(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    a = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(a)

    with pytest.raises(ValueError, match="unknown revoked_by actor"):
        ledger.revoke_assignment(a.assignment_id, revoked_by="ghost", expected_version=1)

    # No partial write: the assignment must still be ACTIVE at version 1.
    unchanged = ledger.get_assignment(a.assignment_id)
    assert unchanged.status.value == "ACTIVE"
    assert unchanged.version == 1


# F1 amendment (duplicate assignment_id vs duplicate-active) parity tests
# moved to test_assignment_ledger_parity_f1.py (Amendment 2 companion) to
# keep this host at/under the 300-line hard limit; they import the same
# _backends/_shift/_user helpers from this module.


def test_in_memory_transaction_rollback_restores_assignment_snapshot():
    """SPEC R3: assignment state participates in InMemoryLedger's deep-copy
    transaction rollback, matching every other vertical's dict."""
    ledger = InMemoryLedger()
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with ledger.transaction() as unit:
            ledger.add_assignment(
                ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"), unit=unit
            )
            raise _Boom("simulated failure mid-transaction")

    assert ledger.list_assignments_for_shift(shift.shift_id) == []
