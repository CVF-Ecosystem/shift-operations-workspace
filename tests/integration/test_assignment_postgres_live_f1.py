"""P2C-C3A1 Amendment 2 companion to test_assignment_postgres_live.py: the
F1-amendment duplicate-assignment_id-vs-duplicate-active real-PostgreSQL
tests, split out purely to keep the host file at or under the 300-line hard
file-size limit. Same opt-in LIVE_POSTGRES_DATABASE_URL contract; reuses the
host module's own `live_database_url`/`sql_ledger` fixtures and
`_shift`/`_user` helpers rather than duplicating them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import insert, text
from sqlalchemy.exc import IntegrityError

from operations_ledger import tables as t

from workspace_api.domain import models as domain_models

from test_assignment_postgres_live import live_database_url, sql_ledger, _shift, _user  # noqa: F401


# --- P2C-C3A1-BUILD-REV-F1 amendment: duplicate assignment_id vs duplicate-active,
# classified via the real server-reported constraint identity (diag.constraint_name)


def test_live_duplicate_assignment_id_rejected_distinct_from_duplicate_active(sql_ledger):
    """F1: an assignment_id colliding with an existing row's real PK
    (shift_assignments_pkey) is rejected distinctly from the SEPARATE
    partial-unique-index (shift_assignments_active_unique) violation, and
    does not overwrite that row's history."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-idcollide-{uuid4().hex[:8]}"
    sup_id = f"pg-live-idcollidesup-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    original = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    sql_ledger.add_assignment(original)
    sql_ledger.revoke_assignment(original.assignment_id, revoked_by=sup_id, expected_version=1)

    colliding = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    colliding.assignment_id = original.assignment_id

    with pytest.raises(ValueError) as exc_info:
        sql_ledger.add_assignment(colliding)
    assert "duplicate assignment_id" in str(exc_info.value)
    assert "duplicate active assignment" not in str(exc_info.value)

    # No partial write: history retained exactly as it was.
    unchanged = sql_ledger.get_assignment(original.assignment_id)
    assert unchanged.status.value == "REVOKED"
    assert unchanged.version == 2

    # Connection/backend still fully usable afterward.
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_live_genuine_duplicate_active_error_distinct_from_id_collision(sql_ledger):
    """F1: duplicate-ACTIVE-assignment (the partial unique index) keeps its
    own message and is never reported as a duplicate assignment_id -
    classified via PostgreSQL's own diag.constraint_name, not a blanket
    remap."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-activedistinct-{uuid4().hex[:8]}"
    sup_id = f"pg-live-activedistinctsup-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")
    sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id))

    with pytest.raises(ValueError) as exc_info:
        sql_ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id))
    assert "duplicate active assignment" in str(exc_info.value)
    assert "duplicate assignment_id" not in str(exc_info.value)


def test_live_check_constraint_violation_never_reported_as_duplicate_active(sql_ledger):
    """F1: an unrelated failure (status CHECK constraint, via a raw insert
    bypassing prevalidation) is never folded into either duplicate-*
    message - the classifier only recognizes the two known unique
    constraints and re-raises anything else unchanged. This raw-insert form
    proves the migration's own CHECK constraint fires as defense in depth;
    it does NOT exercise add_assignment or the classifier - see the
    add_assignment-path tests below for that proof."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-checkdistinct-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)

    with pytest.raises(IntegrityError) as exc_info:
        with sql_ledger.engine.begin() as conn:
            conn.execute(insert(t.shift_assignments).values(
                assignment_id=uuid4(), shift_id=shift.shift_id, user_id=op_id, status="NOT_A_REAL_STATUS",
                assigned_by=op_id, version=1,
            ))
    assert "duplicate" not in str(exc_info.value).lower()
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


# --- P2C-C3A1-BUILD-REV-F4: invalid lifecycle through the real ledger path --
# (sql_ledger.add_assignment, NOT a raw conn.execute - proves
# assert_assignment_lifecycle_valid actually runs on the real backend,
# never reaching the INSERT/classifier at all for this class of failure)


def test_live_add_assignment_rejects_invalid_status_before_reaching_insert(sql_ledger):
    """F4: an invalid status mutated after construction is rejected by
    add_assignment itself, through the real ledger path - never reaching
    the INSERT/classifier, and never a raw IntegrityError."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-f4status-{uuid4().hex[:8]}"
    sup_id = f"pg-live-f4statussup-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    bad = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    bad.status = "NOT_A_REAL_STATUS"

    with pytest.raises(ValueError) as exc_info:
        sql_ledger.add_assignment(bad)
    assert "invalid assignment status" in str(exc_info.value)

    # No partial write, and the backend remains fully usable afterward.
    assert sql_ledger.list_assignments_for_shift(shift.shift_id) == []
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_live_add_assignment_rejects_version_below_one_before_reaching_insert(sql_ledger):
    """F4: version < 1 mutated after construction is rejected by
    add_assignment itself, through the real ledger path - never reaching
    the INSERT/classifier, and never a raw IntegrityError."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    op_id = f"pg-live-f4version-{uuid4().hex[:8]}"
    sup_id = f"pg-live-f4versionsup-{uuid4().hex[:8]}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    bad = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    bad.version = 0

    with pytest.raises(ValueError) as exc_info:
        sql_ledger.add_assignment(bad)
    assert "invalid assignment version" in str(exc_info.value)

    # No partial write, and a subsequent valid assignment still succeeds.
    assert sql_ledger.list_assignments_for_shift(shift.shift_id) == []
    good = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    sql_ledger.add_assignment(good)
    active = sql_ledger.get_active_assignment(shift.shift_id, op_id)
    assert active.assignment_id == good.assignment_id


@pytest.mark.parametrize(
    "changes",
    [
        {"status": domain_models.AssignmentStatus.REVOKED},
        {"status": domain_models.AssignmentStatus.REVOKED, "version": 2, "revoked_by": "sup", "revoked_at": datetime.now(timezone.utc)},
        {"version": 2},
        {"revoked_by": "sup"},
        {"revoked_at": datetime.now(timezone.utc)},
    ],
    ids=["revoked-v1", "direct-revoked-v2", "active-v2", "active-with-revoker", "active-with-revoked-at"],
)
def test_live_add_rejects_non_initial_lifecycle_shapes(sql_ledger, changes):
    """F5: real PostgreSQL ledger path admits only the initial lifecycle
    shape and stays usable after every controlled rejection."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    suffix = uuid4().hex[:8]
    op_id, sup_id = f"pg-live-f5op-{suffix}", f"pg-live-f5sup-{suffix}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")
    bad = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    for field, value in changes.items():
        setattr(bad, field, sup_id if value == "sup" else value)

    with pytest.raises(ValueError, match="invalid initial assignment"):
        sql_ledger.add_assignment(bad)
    assert sql_ledger.list_assignments_for_shift(shift.shift_id) == []

    good = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    sql_ledger.add_assignment(good)
    assert sql_ledger.get_active_assignment(shift.shift_id, op_id).assignment_id == good.assignment_id


@pytest.mark.parametrize("field", ["assignment_id", "assigned_at"])
def test_live_add_strictly_revalidates_mutated_required_fields(sql_ledger, field):
    """F6: PostgreSQL receives the same controlled pre-write ValueError as
    InMemory/SQLite, never a raw NOT NULL IntegrityError."""
    shift = _shift()
    sql_ledger.create_shift(shift)
    suffix = uuid4().hex[:8]
    op_id, sup_id = f"pg-live-f6op-{suffix}", f"pg-live-f6sup-{suffix}"
    _user(sql_ledger, op_id)
    _user(sql_ledger, sup_id, "shift_supervisor")
    bad = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    setattr(bad, field, None)

    with pytest.raises(ValueError, match=f"invalid assignment record fields: {field}"):
        sql_ledger.add_assignment(bad)
    assert sql_ledger.list_assignments_for_shift(shift.shift_id) == []

    good = domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id=op_id, assigned_by=sup_id)
    sql_ledger.add_assignment(good)
    assert sql_ledger.get_active_assignment(shift.shift_id, op_id).assignment_id == good.assignment_id
