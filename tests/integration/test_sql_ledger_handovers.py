"""SqlLedger handover persistence (P2A-HANDOVER-VERTICAL) - SQLite-backed.

Mirrors the parity/atomicity guarantees already proven for incidents
(test_sql_ledger_incidents.py), scoped to handovers/handover_items: duplicate
id, missing id, copy-not-reference returns, item/evidence round-trip, open-work
snapshot derivation, and atomic mutation+audit rollback (P-FIX-2).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from cvf_runtime.audit import AuditRecord
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.handover_service import HandoverService
from workspace_api.domain import models as domain_models
from cvf_runtime.identity import Principal
from operations_domain.models import EvidenceRef, Handover, Shift, Task, TaskStatus
from workspace_api.infrastructure.repository import InMemoryLedger

_OPERATOR = Principal(user_id="op1", role="operator")
_SUPERVISOR = Principal(user_id="sup1", role="shift_supervisor")
_RECEIVER = Principal(user_id="sup2", role="shift_supervisor")


def _open_ledger(db_path: Path) -> SqlLedger:
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    return SqlLedger(str(db_path), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _open_ledger(tmp_path / "backends.sqlite3"))]


def _handover_with_one_task_item(ledger) -> Handover:
    """A real server-derived handover with exactly one evidence-bearing item,
    so an identical-duplicate item/evidence mutation can be isolated
    (HOV-REV-F11)."""
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    task = Task(
        shift_id=s1.shift_id, title="Inspect crane",
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    ledger.add_task(task)
    return HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)


def _shift(**kw) -> Shift:
    now = datetime.now(timezone.utc)
    return Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8), **kw)


def test_add_and_get_handover_round_trips(tmp_path):
    ledger = _open_ledger(tmp_path / "a.sqlite3")
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    task = Task(shift_id=s1.shift_id, title="Inspect crane", evidence=[EvidenceRef(source_type="message", source_id="m1")])
    ledger.add_task(task)

    created = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    fetched = ledger.get_handover(created.handover_id)
    assert fetched.from_shift_id == s1.shift_id and fetched.to_shift_id == s2.shift_id
    assert len(fetched.items) == 1
    assert fetched.items[0].source_record_id == task.task_id
    assert len(fetched.items[0].evidence) == 1


def test_get_handover_returns_copy_not_live_reference(tmp_path):
    ledger = _open_ledger(tmp_path / "b.sqlite3")
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    created = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)

    got = ledger.get_handover(created.handover_id)
    got.created_by = "mutated locally"
    assert ledger.get_handover(created.handover_id).created_by == "op1"


def test_get_missing_handover_raises_keyerror(tmp_path):
    ledger = _open_ledger(tmp_path / "c.sqlite3")
    with pytest.raises(KeyError):
        ledger.get_handover(uuid4())


def test_duplicate_handover_id_fails(tmp_path):
    ledger = _open_ledger(tmp_path / "d.sqlite3")
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    handover = Handover(from_shift_id=s1.shift_id, to_shift_id=s2.shift_id, created_by="op1")
    ledger.add_handover(handover)
    with pytest.raises(ValueError, match="duplicate handover_id"):
        ledger.add_handover(handover)


def test_put_missing_handover_raises_keyerror(tmp_path):
    ledger = _open_ledger(tmp_path / "e.sqlite3")
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    ghost = Handover(from_shift_id=s1.shift_id, to_shift_id=s2.shift_id, created_by="op1")
    with pytest.raises(KeyError):
        ledger.put_handover(ghost)


def test_list_handovers_for_shift_is_scoped_and_deterministic(tmp_path):
    ledger = _open_ledger(tmp_path / "f.sqlite3")
    s1, s2, s3 = _shift(), _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    ledger.create_shift(s3)
    h1 = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    h2 = HandoverService(ledger).create(s1.shift_id, s3.shift_id, _OPERATOR)
    HandoverService(ledger).create(s2.shift_id, s3.shift_id, _OPERATOR)

    got = ledger.list_handovers_for_shift(s1.shift_id)
    assert {h.handover_id for h in got} == {h1.handover_id, h2.handover_id}
    assert [h.handover_id for h in got] == [h.handover_id for h in ledger.list_handovers_for_shift(s1.shift_id)]


def test_open_work_snapshot_excludes_done_task_and_scopes_by_shift(tmp_path):
    ledger = _open_ledger(tmp_path / "g.sqlite3")
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    open_task = Task(shift_id=s1.shift_id, title="open")
    done_task = Task(shift_id=s1.shift_id, title="done", status=TaskStatus.DONE)
    other_shift_task = Task(shift_id=s2.shift_id, title="other shift")
    ledger.add_task(open_task)
    ledger.add_task(done_task)
    ledger.add_task(other_shift_task)

    snapshot = ledger.open_work_snapshot(s1.shift_id)
    ids = {t.task_id for t in snapshot["Task"]}
    assert ids == {open_task.task_id}


def test_review_then_acknowledge_persists_and_audits_through_reconnect(tmp_path):
    db_path = tmp_path / "h.sqlite3"
    ledger = _open_ledger(db_path)
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    svc = HandoverService(ledger)
    h = svc.create(s1.shift_id, s2.shift_id, _OPERATOR)
    h = svc.review(h.handover_id, _SUPERVISOR)
    h = svc.acknowledge(h.handover_id, _RECEIVER)
    ledger.engine.dispose()

    fresh = _open_ledger(db_path)
    got = fresh.get_handover(h.handover_id)
    audits = fresh.audit_entries_for(str(h.handover_id))
    assert got.status.value == "ACKNOWLEDGED" and got.acknowledged is True
    assert {"handover.create", "handover.review", "handover.acknowledge"} <= {a["action"] for a in audits}


def test_mutation_and_audit_roll_back_together_on_handover_failure(tmp_path):
    """P-FIX-2: handover mutation + audit must be atomic, same as every
    other domain vertical."""
    ledger = _open_ledger(tmp_path / "i.sqlite3")
    s1, s2 = _shift(), _shift()
    ledger.create_shift(s1)
    ledger.create_shift(s2)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with ledger.transaction() as unit:
            stored = ledger.get_handover(handover.handover_id, unit=unit)
            stored.status = "REVIEWED"
            stored.version = 2
            ledger.put_handover(stored, unit=unit)
            ledger.append_audit(
                AuditRecord(
                    actor_id="sup1", actor_role="shift_supervisor", action="handover.review",
                    record_type="Handover", record_id=str(handover.handover_id),
                    control_chain=["identity", "audit"], before_state="DRAFT", after_state="REVIEWED",
                ),
                unit=unit,
            )
            raise _Boom("simulated failure")

    restored = ledger.get_handover(handover.handover_id)
    assert restored.status.value == "DRAFT" and restored.version == 1
    # The prior "handover.create" write (committed before this failing
    # transaction began) is untouched; only the failed review's mutation +
    # audit roll back together.
    actions = {a["action"] for a in ledger.audit_entries_for(str(handover.handover_id))}
    assert actions == {"handover.create"}


# --- HOV-REV-F11: multiset collapse (set/frozenset discarding multiplicity) -

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_rejects_identical_duplicate_item(tmp_path, name):
    """Before the fix, ``_items_key`` was a plain ``set``, so appending an
    EXACT duplicate of an existing item hashed to the same set as the
    original (one distinct element either way) and the "immutable" check
    wrongly saw no difference. Doubling a real item must now be rejected."""
    ledger = dict(_backends(tmp_path))[name]
    handover = _handover_with_one_task_item(ledger)

    mutated = ledger.get_handover(handover.handover_id)
    mutated.items = mutated.items + [mutated.items[0].model_copy(deep=True)]
    with pytest.raises(ValueError, match="handover snapshot is immutable"):
        ledger.put_handover(mutated)

    unchanged = ledger.get_handover(handover.handover_id)
    assert len(unchanged.items) == 1


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_rejects_identical_duplicate_evidence(tmp_path, name):
    """Same collapse bug, one level down: ``_evidence_key`` was a
    ``frozenset``, so doubling one item's evidence entry hashed identically
    to the single original. Doubling a real evidence entry must now be
    rejected."""
    ledger = dict(_backends(tmp_path))[name]
    handover = _handover_with_one_task_item(ledger)

    mutated = ledger.get_handover(handover.handover_id)
    mutated.items[0].evidence = mutated.items[0].evidence + [mutated.items[0].evidence[0].model_copy(deep=True)]
    with pytest.raises(ValueError, match="handover snapshot is immutable"):
        ledger.put_handover(mutated)

    unchanged = ledger.get_handover(handover.handover_id)
    assert len(unchanged.items[0].evidence) == 1
