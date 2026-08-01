"""P2B-APPROVER-IDENTITY-RECONCILIATION (R6.2): the interim
known-principals.yaml registry check is retired.

A 2026-07-22 independent review (High Finding #4.1) proved the approval gate
checked only quorum SHAPE, accepting any caller-supplied approver_id/role.
P-FIX-3's fix was an interim YAML registry lookup - not real authentication.
This tranche closes that finding for real: `users` is now the single runtime
authority for approver identity/role/active-status, and an approval receipt
can only ever be created through an authenticated request (never a
caller-supplied approver_id/role pair). These tests prove that: the YAML file
and its API surface are gone, and a fabricated/unregistered/under-authorized
approver still cannot get a counted receipt - the same governance property
the original tests proved, now through the real mechanism instead of the
interim one.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.policy_loader import CvfProfile, load_profile

from operations_domain.models import OperationalEvent, RiskClass, Shift
from workspace_api.application import approval_service
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_known_principals_yaml_no_longer_exists():
    """R6.1: the interim registry file is deleted outright, not demoted to a
    fixture."""
    assert not (
        _REPO_ROOT / "packages" / "cvf-application-profile" / "known-principals.yaml"
    ).is_file()


def test_cvf_profile_has_no_known_principals_field_or_method():
    """R6.1: CvfProfile no longer carries known_principals or known_role_for."""
    profile = load_profile()
    assert not hasattr(profile, "known_principals")
    assert not hasattr(profile, "known_role_for")
    assert "known_principals" not in CvfProfile.__dataclass_fields__


def _r3_event(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=RiskClass.R3,
    )
    ledger.add_event(event)
    return event


def _active_user(ledger, user_id: str, role: str, *, shift_id=None) -> None:
    ledger.add_user(
        User(user_id=user_id, username=user_id, password_hash="x", role=role, is_active=True)
    )
    if shift_id is not None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def test_fabricated_approver_id_cannot_create_a_receipt():
    """The exact Codex probe intent, through the new mechanism: an
    approver_id that is not a real, known user cannot be turned into a
    counted approval seat - there is no request shape left that lets a
    caller invent one (High Finding #4). P2C-C3A2 (F1 repair): coarse
    identity/role denial must fire before the enumeration-safe operational-
    scope guard, so an unknown principal is refused by the identity check
    first - still a controlled refusal, never a counted receipt."""
    ledger = InMemoryLedger()
    event = _r3_event(ledger)
    fabricated = Principal(user_id="totally-made-up", role="shift_supervisor")

    with pytest.raises(CvfDenied) as exc:
        approval_service.create_approval_receipt(
            ledger,
            fabricated,
            record_type="OperationalEvent",
            action="event.confirm",
            record_id=event.event_id,
        )
    assert exc.value.http_status == 403


def test_known_id_with_inflated_role_cannot_fill_a_higher_seat():
    """A real, active user registered as 'operator' cannot receive a receipt
    that counts toward a shift_supervisor/responsible_manager seat - their
    CURRENT role (from `users`, not a claimed one) is checked."""
    ledger = InMemoryLedger()
    event = _r3_event(ledger)
    _active_user(ledger, "op1", "operator", shift_id=event.shift_id)

    with pytest.raises(CvfDenied) as exc:
        approval_service.create_approval_receipt(
            ledger,
            Principal(user_id="op1", role="operator"),
            record_type="OperationalEvent",
            action="event.confirm",
            record_id=event.event_id,
        )
    assert exc.value.control == "approval"
    assert exc.value.http_status == 403


def test_known_active_users_with_correct_roles_create_receipts_and_pass_quorum():
    ledger = InMemoryLedger()
    event = _r3_event(ledger)
    _active_user(ledger, "sup2", "shift_supervisor", shift_id=event.shift_id)
    _active_user(ledger, "mgr1", "responsible_manager", shift_id=event.shift_id)

    receipt1, created1 = approval_service.create_approval_receipt(
        ledger,
        Principal(user_id="sup2", role="shift_supervisor"),
        record_type="OperationalEvent",
        action="event.confirm",
        record_id=event.event_id,
    )
    receipt2, created2 = approval_service.create_approval_receipt(
        ledger,
        Principal(user_id="mgr1", role="responsible_manager"),
        record_type="OperationalEvent",
        action="event.confirm",
        record_id=event.event_id,
    )
    assert created1 and created2
    assert receipt1.approver_id == "sup2"
    assert receipt2.approver_id == "mgr1"


def test_unregistered_or_random_uuid_approver_is_not_a_known_user():
    """No `users` row exists for a random id - receipt creation is refused,
    not silently accepted (the old `known_role_for` behaviour retired).
    P2C-C3A2 (F1 repair): refused by the coarse identity/role check, which
    now runs before the enumeration-safe operational-scope guard - still a
    controlled refusal."""
    ledger = InMemoryLedger()
    event = _r3_event(ledger)
    with pytest.raises(CvfDenied) as exc:
        approval_service.create_approval_receipt(
            ledger,
            Principal(user_id=str(uuid4()), role="shift_supervisor"),
            record_type="OperationalEvent",
            action="event.confirm",
            record_id=event.event_id,
        )
    assert exc.value.http_status == 403
