"""Shared explicit C3a2 user/ACTIVE-assignment test setup."""

from workspace_api.domain.models import ShiftAssignment, User


def seed_active_assignment(ledger, shift_id, user_id="operator-1", role="operator"):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(
            User(
                user_id=user_id,
                username=user_id,
                password_hash="test-only",
                role=role,
            )
        )
    current = ledger.get_active_assignment(shift_id, user_id)
    if current is None:
        ledger.add_assignment(
            ShiftAssignment(
                shift_id=shift_id,
                user_id=user_id,
                assigned_by=user_id,
            )
        )
    return ledger.get_active_assignment(shift_id, user_id)


def seed_all_shift_assignments(ledger, user_id="operator-1", role="operator"):
    for shift in ledger.list_shifts():
        seed_active_assignment(ledger, shift.shift_id, user_id, role)
