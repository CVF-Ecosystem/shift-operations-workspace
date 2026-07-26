"""SqlLedger incident persistence (fifth vertical, P2-A) — SQLite-backed.

Mirrors the parity/atomicity guarantees already proven for events/tasks
(test_evidence_persistence.py) and customer_requests, scoped to incidents:
duplicate id, missing id, copy-not-reference returns, frozen-parent blocking
on both add and put, and atomic mutation+audit rollback (P-FIX-2).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import insert, text
from sqlalchemy.exc import IntegrityError

from cvf_runtime.audit import AuditRecord
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import incidents as inc_table
from operations_ledger.tables import metadata

from workspace_api.domain import models as domain_models
from operations_domain.models import EvidenceRef, Incident, RiskClass, Shift


def _open_ledger(db_path: Path) -> SqlLedger:
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    return SqlLedger(str(db_path), models=domain_models, engine=engine)


def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8), **kw)


def test_add_and_get_incident_round_trips(tmp_path):
    ledger = _open_ledger(tmp_path / "a.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(shift_id=shift.shift_id, summary="Crane stopped", risk_class=RiskClass.R2)
    ledger.add_incident(incident)

    fetched = ledger.get_incident(incident.incident_id)
    assert fetched.summary == "Crane stopped"
    assert fetched.status.value == "REPORTED"
    assert fetched.version == 1


def test_get_incident_returns_copy_not_live_reference(tmp_path):
    ledger = _open_ledger(tmp_path / "b.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(shift_id=shift.shift_id, summary="s")
    ledger.add_incident(incident)

    got = ledger.get_incident(incident.incident_id)
    got.summary = "mutated locally"
    assert ledger.get_incident(incident.incident_id).summary == "s"


def test_get_missing_incident_raises_keyerror(tmp_path):
    ledger = _open_ledger(tmp_path / "c.sqlite3")
    with pytest.raises(KeyError):
        ledger.get_incident(Incident(shift_id=_shift().shift_id, summary="s").incident_id)


def test_duplicate_incident_id_fails(tmp_path):
    ledger = _open_ledger(tmp_path / "d.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(shift_id=shift.shift_id, summary="s")
    ledger.add_incident(incident)
    with pytest.raises(Exception):
        ledger.add_incident(incident)


def test_list_incidents_for_shift_is_scoped_and_deterministic(tmp_path):
    """Scoped to the exact shift, and repeatable across calls. Ordering is
    (created_at, incident_id) (SPEC R6-A) - SQLite's server-side ``now()``
    has only second resolution, so two inserts in the same test can tie on
    created_at; test_incident_vertical.py's
    test_list_incidents_orders_by_created_at_then_incident_id_when_tied
    forces an exact tie and proves the incident_id tie-break directly."""
    ledger = _open_ledger(tmp_path / "e.sqlite3")
    shift_a = _shift()
    shift_b = _shift()
    ledger.create_shift(shift_a)
    ledger.create_shift(shift_b)
    i1 = Incident(shift_id=shift_a.shift_id, summary="first")
    i2 = Incident(shift_id=shift_a.shift_id, summary="second")
    i3 = Incident(shift_id=shift_b.shift_id, summary="other shift")
    ledger.add_incident(i1)
    ledger.add_incident(i2)
    ledger.add_incident(i3)

    got = ledger.list_incidents_for_shift(shift_a.shift_id)
    assert {i.incident_id for i in got} == {i1.incident_id, i2.incident_id}
    assert [i.incident_id for i in got] == [i.incident_id for i in ledger.list_incidents_for_shift(shift_a.shift_id)]


def test_add_incident_to_frozen_shift_blocked(tmp_path):
    ledger = _open_ledger(tmp_path / "f.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    ledger.freeze_shift(shift.shift_id)
    with pytest.raises(ValueError, match="frozen"):
        ledger.add_incident(Incident(shift_id=shift.shift_id, summary="s"))


def test_put_incident_on_frozen_shift_blocked(tmp_path):
    ledger = _open_ledger(tmp_path / "g.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(shift_id=shift.shift_id, summary="s")
    ledger.add_incident(incident)
    ledger.freeze_shift(shift.shift_id)
    with pytest.raises(ValueError, match="frozen"):
        ledger.put_incident(incident)


def test_incident_evidence_round_trips(tmp_path):
    ledger = _open_ledger(tmp_path / "h.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(
        shift_id=shift.shift_id, summary="s",
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    ledger.add_incident(incident)
    fetched = ledger.get_incident(incident.incident_id)
    assert len(fetched.evidence) == 1 and fetched.evidence[0].source_id == "m1"


def test_incident_list_evidence_matches_get_evidence(tmp_path):
    """INC-REV-F3: SQL list previously silently returned incidents with ZERO
    evidence even though get_incident correctly reconstructed it (get=1,
    list=0). Both must now agree."""
    ledger = _open_ledger(tmp_path / "h2.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(
        shift_id=shift.shift_id, summary="s",
        evidence=[EvidenceRef(source_type="message", source_id="m1"), EvidenceRef(source_type="image", source_id="p1")],
    )
    ledger.add_incident(incident)

    via_get = ledger.get_incident(incident.incident_id)
    via_list = ledger.list_incidents_for_shift(shift.shift_id)[0]
    assert len(via_list.evidence) == len(via_get.evidence) == 2
    assert {e.source_id for e in via_list.evidence} == {e.source_id for e in via_get.evidence} == {"m1", "p1"}


def test_incident_version_below_one_rejected_by_database_check(tmp_path):
    """INC-REV-F4: even bypassing the Pydantic model (raw INSERT), the
    database-level CHECK must reject version < 1."""
    ledger = _open_ledger(tmp_path / "h3.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    with pytest.raises(IntegrityError):
        with ledger.engine.begin() as conn:
            conn.execute(insert(inc_table).values(
                incident_id=uuid4(), shift_id=shift.shift_id, risk="R1", summary="bad",
                status="REPORTED", version=0,
            ))
    with ledger.engine.begin() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_mutation_and_audit_roll_back_together_on_incident_failure(tmp_path):
    """P-FIX-2: incident mutation + audit must be atomic, same as every other
    domain vertical."""
    ledger = _open_ledger(tmp_path / "i.sqlite3")
    shift = _shift()
    ledger.create_shift(shift)
    incident = Incident(shift_id=shift.shift_id, summary="s")
    ledger.add_incident(incident)

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with ledger.transaction() as unit:
            incident.status = "ACKNOWLEDGED"
            incident.version = 2
            ledger.put_incident(incident, unit=unit)
            ledger.append_audit(
                AuditRecord(
                    actor_id="sup1", actor_role="shift_supervisor", action="incident.acknowledge",
                    record_type="Incident", record_id=str(incident.incident_id),
                    control_chain=["identity", "audit"], before_state="REPORTED", after_state="ACKNOWLEDGED",
                ),
                unit=unit,
            )
            raise _Boom("simulated failure")

    restored = ledger.get_incident(incident.incident_id)
    assert restored.status.value == "REPORTED" and restored.version == 1
    assert ledger.audit_entries_for(str(incident.incident_id)) == []
