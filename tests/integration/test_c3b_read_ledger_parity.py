"""Cross-backend (InMemory/SQLite) parity for `list_messages_for_shift`
(P2C-MUTATION-FULL-UI-C3B1, SPEC R11/R36, AC-11). Both backends must agree
on ordering, per-shift scoping and empty-shift behavior - the same class of
proof `test_assignment_ledger_parity.py` already applies to shift assignment.

Task/CustomerRequest list parity is already proven by the existing
`list_tasks_for_shift`/`list_customer_requests_for_shift` (reused, not
duplicated); this module owns only the new Message method.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from operations_domain.models import Message, Shift
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger


def _sql_ledger(tmp_path, name="c3b_read_parity.sqlite3"):
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_messages_for_shift_ascending_created_at_then_id(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    base = datetime(2026, 8, 1, 9, tzinfo=timezone.utc)
    m1 = Message(shift_id=shift.shift_id, sender_id="op1", text="second", created_at=base + timedelta(minutes=5))
    m2 = Message(shift_id=shift.shift_id, sender_id="op1", text="first", created_at=base)
    ledger.add_message(m1)
    ledger.add_message(m2)

    result = ledger.list_messages_for_shift(shift.shift_id)
    assert [m.text for m in result] == ["first", "second"]


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_messages_for_shift_ties_break_on_message_id(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    same_time = datetime(2026, 8, 1, 9, tzinfo=timezone.utc)
    m1 = Message(shift_id=shift.shift_id, sender_id="op1", text="a", created_at=same_time)
    m2 = Message(shift_id=shift.shift_id, sender_id="op1", text="b", created_at=same_time)
    ledger.add_message(m1)
    ledger.add_message(m2)

    result = ledger.list_messages_for_shift(shift.shift_id)
    expected_order = sorted([m1, m2], key=lambda m: str(m.message_id))
    assert [m.message_id for m in result] == [m.message_id for m in expected_order]


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_messages_for_shift_scopes_to_one_shift(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift_a = _shift(ledger)
    shift_b = _shift(ledger)
    ledger.add_message(Message(shift_id=shift_a.shift_id, sender_id="op1", text="a-msg"))
    ledger.add_message(Message(shift_id=shift_b.shift_id, sender_id="op1", text="b-msg"))

    result_a = ledger.list_messages_for_shift(shift_a.shift_id)
    assert len(result_a) == 1
    assert result_a[0].text == "a-msg"


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_messages_for_shift_empty_shift_returns_empty_list(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    assert ledger.list_messages_for_shift(shift.shift_id) == []


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_list_messages_for_shift_returns_deep_copies_not_live_references(tmp_path, name):
    """Mutating a returned Message must never touch stored state - the same
    invariant every other list_*_for_shift method already proves."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _shift(ledger)
    ledger.add_message(Message(shift_id=shift.shift_id, sender_id="op1", text="original"))

    result = ledger.list_messages_for_shift(shift.shift_id)
    result[0].text = "mutated"

    fresh = ledger.list_messages_for_shift(shift.shift_id)
    assert fresh[0].text == "original"
