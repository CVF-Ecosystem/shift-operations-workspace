"""P2C-MUTATION-FULL-UI-C3B1 — approval-readiness matching semantics (SPEC
R35, AC-16).

Focused, backend-independent unit tests of
`workspace_api.application.approval_readiness.evaluate_readiness`: exact
role-name output, deterministic maximum bipartite matching with preserved
seat order/multiplicity, one-approver-one-seat, requester independence
(readiness never applies the confirmer/self-approval rule), and the current-
Report 409 boundary.
"""

from __future__ import annotations

import os
from uuid import uuid4

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application.approval_readiness import evaluate_readiness
from workspace_api.application.approval_service import create_approval_receipt
from workspace_api.infrastructure.repository import InMemoryLedger
from operations_domain.models import RiskClass

from _c3b_read_fixtures import (
    new_event,
    new_shift,
    new_task_creation_intent,
    seed_active_assignment,
    seed_user,
)


def _receipt_as(ledger, principal, *, record_type, action, record_id):
    return create_approval_receipt(ledger, principal, record_type=record_type, action=action, record_id=record_id)


def test_r3_quorum_matches_multiple_distinct_seats_in_order():
    """R3 requires [shift_supervisor, responsible_manager] - two receipts
    from two distinct approvers each holding sufficient authority must both
    be matched, in the declared seat order."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    seed_active_assignment(ledger, shift.shift_id, "mgr-1", "responsible_manager")
    event = new_event(shift.shift_id, risk_class=RiskClass.R3)
    ledger.add_event(event)

    _receipt_as(ledger, Principal(user_id="sup-1", role="shift_supervisor"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)
    _receipt_as(ledger, Principal(user_id="mgr-1", role="responsible_manager"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)

    result = evaluate_readiness(
        ledger, Principal(user_id="sup-1", role="shift_supervisor"),
        record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
    )
    assert result.required_roles == ["shift_supervisor", "responsible_manager"]
    assert result.satisfied_roles == ["shift_supervisor", "responsible_manager"]
    assert result.ready is True


def test_r3_quorum_matches_regardless_of_receipt_arrival_order():
    """C3B1-BUILD-REV-F1: storing the higher-authority responsible_manager
    receipt BEFORE the shift_supervisor receipt must still match both seats -
    a plain greedy left-to-right seat scan would let the manager's authority
    (which also satisfies the supervisor seat) get consumed by the earlier
    seat first, leaving the manager seat unmatched. Genuine maximum bipartite
    matching must find the augmenting path instead."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    seed_active_assignment(ledger, shift.shift_id, "mgr-1", "responsible_manager")
    event = new_event(shift.shift_id, risk_class=RiskClass.R3)
    ledger.add_event(event)

    _receipt_as(ledger, Principal(user_id="mgr-1", role="responsible_manager"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)
    _receipt_as(ledger, Principal(user_id="sup-1", role="shift_supervisor"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)

    result = evaluate_readiness(
        ledger, Principal(user_id="sup-1", role="shift_supervisor"),
        record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
    )
    assert result.required_roles == ["shift_supervisor", "responsible_manager"]
    assert result.satisfied_roles == ["shift_supervisor", "responsible_manager"]
    assert result.ready is True


def test_one_distinct_approver_fills_at_most_one_seat():
    """A single approver holding two receipts (or authority satisfying both
    seats) must not double-count toward a two-seat quorum."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    # authorized_executive outranks both R3 seats but is still one person.
    seed_active_assignment(ledger, shift.shift_id, "exec-1", "authorized_executive")
    event = new_event(shift.shift_id, risk_class=RiskClass.R3)
    ledger.add_event(event)

    _receipt_as(ledger, Principal(user_id="exec-1", role="authorized_executive"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)

    result = evaluate_readiness(
        ledger, Principal(user_id="exec-1", role="authorized_executive"),
        record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
    )
    assert result.ready is False
    assert result.satisfied_roles == ["shift_supervisor"]


def test_readiness_is_requester_independent_and_ignores_self_approval_rule():
    """Readiness must return the same result regardless of who is asking,
    and must not apply the later confirmer/self-approval rule (that
    remains mutation-only)."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    seed_active_assignment(ledger, shift.shift_id, "sup-2", "shift_supervisor")
    event = new_event(shift.shift_id, risk_class=RiskClass.R2)
    ledger.add_event(event)
    _receipt_as(ledger, Principal(user_id="sup-1", role="shift_supervisor"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)

    as_sup1 = evaluate_readiness(
        ledger, Principal(user_id="sup-1", role="shift_supervisor"),
        record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
    )
    as_sup2 = evaluate_readiness(
        ledger, Principal(user_id="sup-2", role="shift_supervisor"),
        record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
    )
    assert as_sup1.ready == as_sup2.ready is True
    assert as_sup1.satisfied_roles == as_sup2.satisfied_roles == ["shift_supervisor"]


def test_deactivated_approver_is_not_current_authority():
    """A stale receipt from a now-inactive user must not count toward
    readiness - authority is re-derived fresh, never trusted from the
    stored receipt."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    seed_active_assignment(ledger, shift.shift_id, "sup-2", "shift_supervisor")
    event = new_event(shift.shift_id, risk_class=RiskClass.R2)
    ledger.add_event(event)
    _receipt_as(ledger, Principal(user_id="sup-1", role="shift_supervisor"),
                record_type="OperationalEvent", action="event.confirm", record_id=event.event_id)

    user = ledger.get_user_by_id("sup-1")
    user.is_active = False
    ledger.users[user.user_id] = user  # direct deactivation, bypassing any service

    result = evaluate_readiness(
        ledger, Principal(user_id="sup-2", role="shift_supervisor"),
        record_type="OperationalEvent", action="event.confirm", record_id=event.event_id,
    )
    assert result.ready is False
    assert result.satisfied_roles == []


def test_r1_risk_class_has_no_required_seats_and_is_always_ready():
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_user(ledger, "viewer-1", "viewer")
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    intent = new_task_creation_intent(ledger, shift.shift_id, risk_class=RiskClass.R1)

    result = evaluate_readiness(
        ledger, Principal(user_id="sup-1", role="shift_supervisor"),
        record_type="Task", action="task.create", record_id=intent.intent_id,
    )
    assert result.required_roles == []
    assert result.satisfied_roles == []
    assert result.ready is True


def test_non_current_report_returns_409_after_permission_and_assignment():
    from workspace_api.application.report_service import ReportService

    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_active_assignment(ledger, shift.shift_id, "op-1", "operator")
    seed_active_assignment(ledger, shift.shift_id, "sup-1", "shift_supervisor")
    ledger.close_shift(shift.shift_id)
    svc = ReportService(ledger)
    report_v1 = svc.generate(shift.shift_id, Principal(user_id="op-1", role="operator"))
    successor = ledger.create_report_successor(
        report_v1.report_id,
        report_v1.model_copy(update={
            "report_id": uuid4(),
            "version": report_v1.version + 1,
            "status": "DRAFT",
            "is_current": True,
        }),
    )
    assert successor.is_current is True

    try:
        evaluate_readiness(
            ledger, Principal(user_id="sup-1", role="shift_supervisor"),
            record_type="Report", action="report.approve", record_id=report_v1.report_id,
        )
        raise AssertionError("expected CvfDenied for non-current report")
    except CvfDenied as exc:
        assert exc.http_status == 409


def test_coarse_permission_denied_before_target_lookup():
    """R37: require_action runs before target resolution - an unknown
    record_id under a denied action still returns 403, not 404."""
    ledger = InMemoryLedger()
    shift = new_shift(ledger)
    seed_user(ledger, "op-1", "operator")
    try:
        evaluate_readiness(
            ledger, Principal(user_id="op-1", role="operator"),
            record_type="OperationalEvent", action="event.confirm", record_id=uuid4(),
        )
        raise AssertionError("expected CvfDenied 403")
    except CvfDenied as exc:
        assert exc.http_status == 403
