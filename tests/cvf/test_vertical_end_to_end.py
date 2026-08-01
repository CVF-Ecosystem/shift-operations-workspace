"""End-to-end golden-vertical test: an event through the full CVF chain.

Proves the chain holds together at the service layer: permission, evidence,
approval, state transition, audit write, and freeze — for the Operational
Event domain.

P2B-APPROVER-IDENTITY-RECONCILIATION: a satisfied quorum is now proved with
authenticated approval receipts (``approval_service.create_approval_receipt``
under each approver's own ``Principal``), not caller-supplied
``Approval(...)`` objects.
"""

from datetime import datetime, timedelta, timezone

import pytest

from cvf_runtime.audit import AuditLog
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application import approval_service
from workspace_api.application.services import EventService
from workspace_api.domain.models import ShiftAssignment, User
from operations_domain.models import (
    DataState,
    EvidenceRef,
    OperationalEvent,
    RiskClass,
    Shift,
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _seed(ledger, shift_id, user_id, role):
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _fresh_ledger() -> tuple[InMemoryLedger, Shift]:
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _seed(ledger, shift.shift_id, "sup1", "shift_supervisor")
    _seed(ledger, shift.shift_id, "op1", "operator")
    return ledger, shift


def _add_event(ledger, shift, *, risk, evidence_count):
    evidence = [
        EvidenceRef(source_type="message", source_id=f"m{i}")
        for i in range(evidence_count)
    ]
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=risk,
        state=DataState.PROPOSED,
        evidence=evidence,
    )
    return ledger.add_event(event)


def _approve_confirm(ledger, event, approver_id, role):
    _seed(ledger, event.shift_id, approver_id, role)
    approval_service.create_approval_receipt(
        ledger,
        Principal(user_id=approver_id, role=role),
        record_type="OperationalEvent",
        action="event.confirm",
        record_id=event.event_id,
    )


def test_r3_full_chain_confirms_and_audits():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R3, evidence_count=1)
    supervisor = Principal(user_id="sup1", role="shift_supervisor")
    _approve_confirm(ledger, event, "sup2", "shift_supervisor")
    _approve_confirm(ledger, event, "mgr1", "responsible_manager")

    confirmed = EventService(ledger, audit).confirm(event.event_id, supervisor, expected_version=event.version)

    assert confirmed.state == DataState.CONFIRMED
    # Both the two receipt creations (AC-19: each atomically audited as
    # "approval.create") and the confirm itself append audit entries scoped
    # to this event id - isolate the confirm's own entry.
    entries = ledger.audit_entries_for(str(event.event_id))
    confirm_entries = [e for e in entries if e.action == "event.confirm"]
    assert len(confirm_entries) == 1
    assert confirm_entries[0].actor_id == "sup1"
    assert confirm_entries[0].before_state == "PROPOSED"
    assert confirm_entries[0].after_state == "CONFIRMED"
    receipt_entries = [e for e in entries if e.action == "approval.create"]
    assert len(receipt_entries) == 2


def test_operator_confirm_denied_by_permission():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R2, evidence_count=1)
    operator = Principal(user_id="op1", role="operator")

    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit).confirm(event.event_id, operator)
    assert exc.value.control == "permission"
    # Nothing confirmed, nothing audited.
    assert ledger.events[event.event_id].state == DataState.PROPOSED
    assert ledger.audit_entries_for(str(event.event_id)) == []


def test_r2_denied_when_evidence_missing():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R2, evidence_count=0)
    supervisor = Principal(user_id="sup1", role="shift_supervisor")

    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit).confirm(event.event_id, supervisor, expected_version=event.version)
    assert exc.value.control == "evidence"


def test_r3_denied_when_quorum_not_met():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R3, evidence_count=1)
    supervisor = Principal(user_id="sup1", role="shift_supervisor")
    _approve_confirm(ledger, event, "sup2", "shift_supervisor")

    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit).confirm(event.event_id, supervisor, expected_version=event.version)
    assert exc.value.control == "approval"


def test_confirm_blocked_on_frozen_shift():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R1, evidence_count=0)
    # Freeze the event's state path by first confirming then freezing.
    supervisor = Principal(user_id="sup1", role="shift_supervisor")
    confirmed = EventService(ledger, audit).confirm(event.event_id, supervisor, expected_version=event.version)
    # Move to FROZEN directly to simulate a frozen record.
    ledger.events[event.event_id].state = DataState.FROZEN

    with pytest.raises((CvfDenied, ValueError)):
        EventService(ledger, audit).confirm(event.event_id, supervisor, expected_version=confirmed.version)
