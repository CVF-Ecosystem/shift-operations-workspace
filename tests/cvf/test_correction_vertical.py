"""Correction golden vertical: post-freeze changes go through a correction record.

Proves the SAME cvf-runtime gates enforce a second domain, plus the
correction-specific rules: only official facts are correctable, a reason is
mandatory, the record's risk quorum applies, and corrections are append-only.
"""

from datetime import datetime, timedelta, timezone

import pytest

from cvf_runtime.approval import Approval
from cvf_runtime.audit import AuditLog
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

from workspace_api.application.correction_service import CorrectionService
from workspace_api.domain.models import (
    DataState,
    EvidenceRef,
    OperationalEvent,
    RiskClass,
    Shift,
)
from workspace_api.infrastructure.repository import InMemoryLedger


def _ledger_with_event(*, state, risk=RiskClass.R2, evidence_count=1):
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=risk,
        state=state,
        evidence=[EvidenceRef(source_type="message", source_id="m1") for _ in range(evidence_count)],
    )
    ledger.add_event(event)
    return ledger, event


def _supervisor():
    return Principal(user_id="sup1", role="shift_supervisor")


def test_confirmed_event_corrected_with_record_and_audit():
    ledger, event = _ledger_with_event(state=DataState.CONFIRMED, risk=RiskClass.R2)
    audit = AuditLog()
    correction = CorrectionService(ledger, audit).correct_event(
        event.event_id,
        _supervisor(),
        reason="Downtime end time was mistyped",
        approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
    )
    assert correction.previous_version == 1
    assert correction.new_version == 2
    # Event moved CONFIRMED -> CORRECTED, version bumped.
    assert ledger.events[event.event_id].state == DataState.CORRECTED
    assert ledger.events[event.event_id].version == 2
    # Correction is stored and audited.
    assert len(ledger.corrections_for(event.event_id)) == 1
    entries = ledger.audit_entries_for(str(event.event_id))
    assert entries[-1].action == "event.correct"
    assert entries[-1].before_state == "CONFIRMED"
    assert entries[-1].after_state == "CORRECTED"


def test_frozen_event_not_silently_overwritten():
    ledger, event = _ledger_with_event(state=DataState.FROZEN, risk=RiskClass.R2)
    audit = AuditLog()
    correction = CorrectionService(ledger, audit).correct_event(
        event.event_id,
        _supervisor(),
        reason="Regulatory reclassification after review",
        approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
    )
    # Frozen record stays FROZEN (no silent overwrite); correction records the change.
    assert ledger.events[event.event_id].state == DataState.FROZEN
    assert correction.new_version == 2
    assert len(ledger.corrections_for(event.event_id)) == 1


def test_proposed_event_cannot_be_corrected():
    ledger, event = _ledger_with_event(state=DataState.PROPOSED)
    with pytest.raises(CvfDenied) as exc:
        CorrectionService(ledger, AuditLog()).correct_event(
            event.event_id, _supervisor(), reason="x", approvals=[]
        )
    assert exc.value.control == "freeze"


def test_correction_requires_reason():
    ledger, event = _ledger_with_event(state=DataState.CONFIRMED)
    with pytest.raises(CvfDenied) as exc:
        CorrectionService(ledger, AuditLog()).correct_event(
            event.event_id,
            _supervisor(),
            reason="   ",
            approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
        )
    assert exc.value.control == "audit"


def test_operator_cannot_correct():
    ledger, event = _ledger_with_event(state=DataState.CONFIRMED)
    operator = Principal(user_id="op1", role="operator")
    with pytest.raises(CvfDenied) as exc:
        CorrectionService(ledger, AuditLog()).correct_event(
            event.event_id, operator, reason="x", approvals=[]
        )
    assert exc.value.control == "permission"


def test_r3_correction_needs_dual_quorum():
    ledger, event = _ledger_with_event(state=DataState.CONFIRMED, risk=RiskClass.R3)
    with pytest.raises(CvfDenied) as exc:
        CorrectionService(ledger, AuditLog()).correct_event(
            event.event_id,
            _supervisor(),
            reason="Reclassify severity",
            approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
        )
    assert exc.value.control == "approval"
