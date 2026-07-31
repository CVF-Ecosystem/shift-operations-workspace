"""P2C-C3A1 Amendment 2 companion to test_assignment_ledger_parity.py: the
F1-amendment duplicate-assignment_id-vs-duplicate-active parity tests, split
out purely to keep the host file at or under the 300-line hard file-size
limit. Reuses the host module's own `_backends`/`_shift`/`_user` helpers
rather than duplicating them - same fixture shape, same backends.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from workspace_api.domain.models import AssignmentStatus, ShiftAssignment

from test_assignment_ledger_parity import _backends, _shift, _user


# --- P2C-C3A1-BUILD-REV-F1 amendment: duplicate assignment_id vs duplicate-active -


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_assignment_id_is_rejected_and_does_not_overwrite_history(tmp_path, name):
    """F1: a caller presenting an assignment_id that collides with an
    EXISTING row (e.g. a previously revoked assignment's id reused) must
    never silently overwrite that row - InMemory previously had no primary
    key at all and accepted this unconditionally, destroying history."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    original = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(original)
    ledger.revoke_assignment(original.assignment_id, revoked_by="sup1", expected_version=1)

    colliding = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    colliding.assignment_id = original.assignment_id

    with pytest.raises(ValueError) as exc_info:
        ledger.add_assignment(colliding)
    assert "duplicate assignment_id" in str(exc_info.value)

    unchanged = ledger.get_assignment(original.assignment_id)
    assert unchanged.status.value == "REVOKED"
    assert unchanged.version == 2


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_assignment_id_error_is_not_labeled_duplicate_active(tmp_path, name):
    """F1: duplicate-assignment-id and duplicate-active-assignment are
    DISTINCT failures with distinct constraints/checks behind them and must
    never share a message - conflating them would mislead a caller into
    thinking the ACTIVE-assignment invariant, not the id itself, was hit."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    original = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(original)
    ledger.revoke_assignment(original.assignment_id, revoked_by="sup1", expected_version=1)

    colliding = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    colliding.assignment_id = original.assignment_id

    with pytest.raises(ValueError) as exc_info:
        ledger.add_assignment(colliding)
    assert "duplicate active assignment" not in str(exc_info.value)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_genuine_duplicate_active_still_raises_controlled_error_distinct_from_id_collision(tmp_path, name):
    """F1: the pre-existing duplicate-ACTIVE-assignment rejection (a
    DIFFERENT constraint from the primary key) must retain its own message
    and must never be reported as a duplicate assignment_id."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))

    with pytest.raises(ValueError) as exc_info:
        ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    assert "duplicate active assignment" in str(exc_info.value)
    assert "duplicate assignment_id" not in str(exc_info.value)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_rejected_duplicate_assignment_id_leaves_backend_usable(tmp_path, name):
    """F1: a rejected duplicate-assignment_id insert must leave no partial
    write and the ledger/connection fully usable for subsequent operations -
    same guarantee every other controlled-rejection path in this suite
    already proves."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    original = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(original)
    ledger.revoke_assignment(original.assignment_id, revoked_by="sup1", expected_version=1)

    colliding = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    colliding.assignment_id = original.assignment_id
    with pytest.raises(ValueError):
        ledger.add_assignment(colliding)

    # Backend still fully usable: a fresh, non-colliding assignment succeeds.
    fresh = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(fresh)
    active = ledger.get_active_assignment(shift.shift_id, "op1")
    assert active.assignment_id == fresh.assignment_id
    listed = ledger.list_assignments_for_shift(shift.shift_id)
    assert len(listed) == 2


# --- P2C-C3A1-BUILD-REV-F4: invalid lifecycle shape, both backends equivalent -


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_invalid_status_is_controlled_and_equivalent_both_backends(tmp_path, name):
    """F4: a ShiftAssignment mutated after construction to an invalid
    status (pydantic does not re-validate on plain attribute assignment)
    must be rejected with a controlled ValueError on BOTH backends -
    InMemory had no equivalent constraint at all and silently stored it;
    SQLite raised a raw, unclassified sqlalchemy.exc.IntegrityError."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    bad = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    bad.status = "NOT_A_REAL_STATUS"

    with pytest.raises(ValueError) as exc_info:
        ledger.add_assignment(bad)
    assert "invalid assignment status" in str(exc_info.value)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_version_below_one_is_controlled_and_equivalent_both_backends(tmp_path, name):
    """F4: version < 1 mutated after construction must be rejected with a
    controlled ValueError on both backends, same as invalid status."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    bad = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    bad.version = 0

    with pytest.raises(ValueError) as exc_info:
        ledger.add_assignment(bad)
    assert "invalid assignment version" in str(exc_info.value)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_invalid_lifecycle_rejection_leaves_no_partial_write(tmp_path, name):
    """F4: neither an invalid-status nor an invalid-version rejection may
    leave any row behind on either backend."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    bad_status = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    bad_status.status = "NOT_A_REAL_STATUS"
    with pytest.raises(ValueError):
        ledger.add_assignment(bad_status)

    bad_version = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    bad_version.version = 0
    with pytest.raises(ValueError):
        ledger.add_assignment(bad_version)

    assert ledger.list_assignments_for_shift(shift.shift_id) == []


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_backend_remains_usable_after_invalid_lifecycle_rejection(tmp_path, name):
    """F4: after rejecting an invalid-lifecycle insert, the backend must
    still accept a subsequent genuinely valid assignment - no connection
    poisoning, no lingering transaction state."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")

    bad = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    bad.status = "NOT_A_REAL_STATUS"
    with pytest.raises(ValueError):
        ledger.add_assignment(bad)

    good = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(good)
    active = ledger.get_active_assignment(shift.shift_id, "op1")
    assert active.assignment_id == good.assignment_id


@pytest.mark.parametrize("name", ["in_memory", "sql"])
@pytest.mark.parametrize(
    "changes",
    [
        {"status": AssignmentStatus.REVOKED},
        {"status": AssignmentStatus.REVOKED, "version": 2, "revoked_by": "sup1", "revoked_at": datetime.now(timezone.utc)},
        {"version": 2},
        {"revoked_by": "sup1"},
        {"revoked_at": datetime.now(timezone.utc)},
    ],
    ids=["revoked-v1", "direct-revoked-v2", "active-v2", "active-with-revoker", "active-with-revoked-at"],
)
def test_add_rejects_non_initial_lifecycle_shapes_without_partial_write(tmp_path, name, changes):
    """F5: add is creation-only: only ACTIVE/version-1 with no revoke
    metadata is admissible. REVOKED history must originate from revoke()."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    bad = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    for field, value in changes.items():
        setattr(bad, field, value)

    with pytest.raises(ValueError, match="invalid initial assignment"):
        ledger.add_assignment(bad)
    assert ledger.list_assignments_for_shift(shift.shift_id) == []

    good = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(good)
    assert ledger.get_active_assignment(shift.shift_id, "op1").assignment_id == good.assignment_id


@pytest.mark.parametrize("name", ["in_memory", "sql"])
@pytest.mark.parametrize("field", ["assignment_id", "assigned_at"])
def test_add_strictly_revalidates_mutated_required_fields(tmp_path, name, field):
    """F6: mutable Pydantic records are strictly revalidated before either
    backend writes, preventing dict acceptance vs SQL NOT NULL divergence."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    _user(ledger, "op1")
    _user(ledger, "sup1", "shift_supervisor")
    bad = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    setattr(bad, field, None)

    with pytest.raises(ValueError, match=f"invalid assignment record fields: {field}"):
        ledger.add_assignment(bad)
    assert ledger.list_assignments_for_shift(shift.shift_id) == []

    good = ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1")
    ledger.add_assignment(good)
    assert ledger.get_active_assignment(shift.shift_id, "op1").assignment_id == good.assignment_id
