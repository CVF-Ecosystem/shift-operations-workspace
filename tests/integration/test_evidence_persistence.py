"""P-FIX-3: evidence must survive a SqlLedger round-trip.

A 2026-07-22 independent review (Critical Finding #2) proved SqlLedger silently
dropped OperationalEvent.evidence: a probe stored an R2 event with one
evidence item, read it back with zero evidence items, and EventService.confirm
then refused with "[evidence] R2 requires at least 1 evidence link(s); found
0" - on a record that DID have evidence when it was written. These tests
reproduce that exact scenario and assert the opposite outcome.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cvf_runtime.approval import Approval
from cvf_runtime.audit import AuditLog
from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.services import EventService
from workspace_api.domain import models as domain_models
from operations_domain.models import EvidenceRef, OperationalEvent, RiskClass, Shift


def _open_ledger(db_path: Path) -> SqlLedger:
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    return SqlLedger(str(db_path), models=domain_models, engine=engine)


def test_evidence_round_trips_through_sql_ledger(tmp_path):
    db = tmp_path / "evidence.sqlite3"
    ledger = _open_ledger(db)
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)

    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=RiskClass.R2,
        evidence=[EvidenceRef(source_type="message", source_id="m1", sha256="abc123")],
    )
    ledger.add_event(event)
    ledger.engine.dispose()

    reopened = SqlLedger(str(db), models=domain_models, engine=make_engine(f"sqlite:///{db}"))
    fetched = reopened.get_event(event.event_id)
    assert len(fetched.evidence) == 1, "evidence must not be dropped on read-back"
    assert fetched.evidence[0].source_id == "m1"
    assert fetched.evidence[0].sha256 == "abc123"


def test_r2_event_confirm_succeeds_on_sql_ledger_with_evidence(tmp_path):
    """Reproduces the exact Codex probe: this must now PASS, not refuse."""
    db = tmp_path / "evidence_confirm.sqlite3"
    ledger = _open_ledger(db)
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)

    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=RiskClass.R2,
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    ledger.add_event(event)

    supervisor = Principal(user_id="sup1", role="shift_supervisor")
    confirmed = EventService(ledger, AuditLog()).confirm(
        event.event_id,
        supervisor,
        approvals=[Approval(approver_id="sup2", role="shift_supervisor")],
    )
    assert confirmed.state.value == "CONFIRMED"


def test_event_without_evidence_still_refused_on_sql_ledger(tmp_path):
    """Guards against over-correcting: R2 with NO evidence must still be denied."""
    from cvf_runtime.errors import CvfDenied

    db = tmp_path / "evidence_missing.sqlite3"
    ledger = _open_ledger(db)
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)

    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="No evidence provided",
        risk_class=RiskClass.R2,
    )
    ledger.add_event(event)

    supervisor = Principal(user_id="sup1", role="shift_supervisor")
    with pytest.raises(CvfDenied) as exc:
        EventService(ledger, AuditLog()).confirm(event.event_id, supervisor, approvals=[])
    assert exc.value.control == "evidence"


def test_multiple_evidence_links_all_persist(tmp_path):
    db = tmp_path / "evidence_multi.sqlite3"
    ledger = _open_ledger(db)
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)

    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Major incident",
        risk_class=RiskClass.R4,
        evidence=[
            EvidenceRef(source_type="message", source_id="m1"),
            EvidenceRef(source_type="image", source_id="photo1"),
        ],
    )
    ledger.add_event(event)

    fetched = ledger.get_event(event.event_id)
    assert len(fetched.evidence) == 2
    assert {e.source_id for e in fetched.evidence} == {"m1", "photo1"}
