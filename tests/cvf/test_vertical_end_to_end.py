"""End-to-end golden-vertical test: an event through the full CVF chain.

Proves the chain holds together at the service layer: permission, evidence,
approval, state transition, audit write, and freeze — for the Operational
Event domain.
"""

from datetime import datetime, timedelta, timezone

import pytest

from cvf_runtime.approval import Approval
from cvf_runtime.audit import AuditLog
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application.services import EventService
from workspace_api.domain.models import (
    DataState,
    EvidenceRef,
    OperationalEvent,
    RiskClass,
    Shift,
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _fresh_ledger() -> tuple[InMemoryLedger, Shift]:
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
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


def test_r3_full_chain_confirms_and_audits():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R3, evidence_count=1)
    supervisor = Principal(user_id="sup1", role="shift_supervisor")

    confirmed = EventService(ledger, audit).confirm(
        event.event_id,
        supervisor,
        approvals=[
            Approval(approver_id="sup2", role="shift_supervisor"),
            Approval(approver_id="mgr1", role="responsible_manager"),
        ],
    )

    assert confirmed.state == DataState.CONFIRMED
    entries = ledger.audit_entries_for(str(event.event_id))
    assert len(entries) == 1
    assert entries[0].actor_id == "sup1"
    assert entries[0].action == "event.confirm"
    assert entries[0].before_state == "PROPOSED"
    assert entries[0].after_state == "CONFIRMED"


def test_operator_confirm_denied_by_permission():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R2, evidence_count=1)
    operator = Principal(user_id="op1", role="operator")

    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit).confirm(event.event_id, operator, approvals=[])
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
        EventService(ledger, audit).confirm(
            event.event_id,
            supervisor,
            approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
        )
    assert exc.value.control == "evidence"


def test_r3_denied_when_quorum_not_met():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R3, evidence_count=1)
    supervisor = Principal(user_id="sup1", role="shift_supervisor")

    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, audit).confirm(
            event.event_id,
            supervisor,
            approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
        )
    assert exc.value.control == "approval"


def test_confirm_blocked_on_frozen_shift():
    ledger, shift = _fresh_ledger()
    audit = AuditLog()
    event = _add_event(ledger, shift, risk=RiskClass.R1, evidence_count=0)
    # Freeze the event's state path by first confirming then freezing.
    supervisor = Principal(user_id="sup1", role="shift_supervisor")
    EventService(ledger, audit).confirm(event.event_id, supervisor, approvals=[])
    # Move to FROZEN directly to simulate a frozen record.
    ledger.events[event.event_id].state = DataState.FROZEN

    with pytest.raises((CvfDenied, ValueError)):
        EventService(ledger, audit).confirm(event.event_id, supervisor, approvals=[])
