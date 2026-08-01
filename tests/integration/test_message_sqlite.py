"""SqlLedger (SQLite) and InMemory parity for message admission
(MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC R9-R11, AC-09/AC-10).

Proves the same MessageService.create/Ledger.transaction path holds for a
real on-disk SQLite database: returned equals persisted, duplicate message_id
and non-empty evidence are refused with controlled errors (never a raw
IntegrityError), and both the message and its audit survive a connection
dispose/reopen. Also proves InMemoryLedger's deep-copy isolation, which
SQLite cannot demonstrate (mutating a caller/returned/read object must never
mutate stored truth).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from operations_domain.models import EvidenceRef, Message, Shift
from workspace_api.application.message_service import MessageService
from workspace_api.domain import models as domain_models
from workspace_api.infrastructure.repository import InMemoryLedger

_OPERATOR = Principal(user_id="op1", role="operator")


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "message_roundtrip.sqlite3"


def _open_ledger(db_path: Path) -> SqlLedger:
    engine = make_engine(f"sqlite:///{db_path}")
    metadata.create_all(engine)
    return SqlLedger(str(db_path), models=domain_models, engine=engine)


def _new_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    if ledger.get_user_by_id("op1") is None:
        ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))
    return shift


def test_create_returns_the_persisted_record(db_path: Path):
    ledger = _open_ledger(db_path)
    shift = _new_shift(ledger)
    returned = MessageService(ledger).create(shift.shift_id, "hello", _OPERATOR)

    fetched = ledger.get_message(returned.message_id)
    assert fetched.message_id == returned.message_id
    assert fetched.sender_id == returned.sender_id == "op1"
    assert fetched.source == returned.source == "INTERNAL"
    assert fetched.text == returned.text == "hello"
    assert fetched.state == returned.state


def test_message_and_audit_survive_reconnect(db_path: Path):
    ledger = _open_ledger(db_path)
    shift = _new_shift(ledger)
    created = MessageService(ledger).create(shift.shift_id, "night note", _OPERATOR)
    ledger.engine.dispose()

    reopened = SqlLedger(str(db_path), models=domain_models, engine=make_engine(f"sqlite:///{db_path}"))
    fetched = reopened.get_message(created.message_id)
    audits = reopened.audit_entries_for(str(created.message_id))

    assert fetched.message_id == created.message_id
    assert fetched.text == "night note"
    assert len(audits) == 1
    assert audits[0]["action"] == "message.create"
    assert audits[0]["actor_id"] == "op1"


def test_sql_duplicate_message_id_refused_with_controlled_error(db_path: Path):
    ledger = _open_ledger(db_path)
    shift = _new_shift(ledger)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="first")
    ledger.add_message(message)

    with pytest.raises(ValueError, match="duplicate message_id"):
        ledger.add_message(message)

    # connection remains usable after the controlled refusal
    assert ledger.get_message(message.message_id).text == "first"


def test_sql_non_empty_evidence_refused_not_silently_dropped(db_path: Path):
    ledger = _open_ledger(db_path)
    shift = _new_shift(ledger)
    message = Message(
        shift_id=shift.shift_id, sender_id="op1", text="with evidence",
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    with pytest.raises(ValueError, match="evidence"):
        ledger.add_message(message)

    with pytest.raises(KeyError):
        ledger.get_message(message.message_id)


def test_sql_unknown_shift_rejected(db_path: Path):
    import uuid

    ledger = _open_ledger(db_path)
    message = Message(shift_id=uuid.uuid4(), sender_id="op1", text="orphan")
    with pytest.raises(KeyError):
        ledger.add_message(message)


def test_sql_frozen_shift_rejected(db_path: Path):
    ledger = _open_ledger(db_path)
    shift = _new_shift(ledger)
    ledger.close_shift(shift.shift_id)
    ledger.freeze_shift(shift.shift_id)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="too late")
    with pytest.raises(ValueError, match="frozen"):
        ledger.add_message(message)


# --- InMemory deep-copy isolation (R9; SQLite cannot demonstrate this) -------


def test_in_memory_mutating_the_input_object_does_not_mutate_stored_truth():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="original")
    ledger.add_message(message)

    message.text = "mutated after add"

    assert ledger.get_message(message.message_id).text == "original"


def test_in_memory_mutating_the_returned_object_does_not_mutate_stored_truth():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="original")
    returned = ledger.add_message(message)

    returned.text = "mutated after return"

    assert ledger.get_message(message.message_id).text == "original"


def test_in_memory_mutating_the_read_object_does_not_mutate_stored_truth():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="original")
    ledger.add_message(message)

    fetched = ledger.get_message(message.message_id)
    fetched.text = "mutated after read"

    assert ledger.get_message(message.message_id).text == "original"


def test_in_memory_duplicate_message_id_refused():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = Message(shift_id=shift.shift_id, sender_id="op1", text="first")
    ledger.add_message(message)

    with pytest.raises(ValueError, match="duplicate message_id"):
        ledger.add_message(message)


def test_in_memory_non_empty_evidence_refused():
    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = Message(
        shift_id=shift.shift_id, sender_id="op1", text="with evidence",
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    with pytest.raises(ValueError, match="evidence"):
        ledger.add_message(message)


# --- R11: persisted message accepted as a customer-request source reference -


def test_persisted_message_accepted_as_customer_request_source_reference():
    from workspace_api.application.customer_request_service import CustomerRequestService
    from operations_domain.models import CustomerRequest

    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    message = MessageService(ledger).create(shift.shift_id, "customer note", _OPERATOR)

    request = CustomerRequest(customer_id="c1", summary="follow up", source_message_id=message.message_id)
    created = CustomerRequestService(ledger).create_customer_request(request, _OPERATOR)
    assert created.source_message_id == message.message_id
