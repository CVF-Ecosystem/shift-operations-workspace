"""Cross-backend handover ledger parity and immutability (HOV-REV-F7/F9,
P2A-HANDOVER-VERTICAL Amendment 2, SPEC R21/R22).

Fresh probes proved InMemoryLedger accepted duplicate handover items and
missing shift IDs, SqlLedger leaked/mislabeled raw integrity errors, and
``put_handover`` was not immutable on either backend. This module proves both
backends now reject the exact same controlled cases with the same
``ValueError`` reason fragments, with no partial write and no raw
``IntegrityError`` ever escaping.

HOV-REV-F9: the immutability comparator originally covered only
``(record_type, record_id, digest)`` per item, so ``summary``, ``evidence``,
``owner_id``, ``due_at``, ``risk_class``, ``item_id``, an item's own
``handover_id``, and the aggregate's ``created_at``/``created_by`` could all
be silently mutated through ``put_handover``. Every one of those fields now
has a dedicated, parametrized, cross-backend test proving rejection with no
partial write, isolating exactly one field at a time so a comparator that
only checked a subset could not pass.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.handover_service import HandoverService
from workspace_api.domain import models as domain_models
from cvf_runtime.identity import Principal
from operations_domain.models import EvidenceRef, Handover, HandoverItem, Shift
from workspace_api.infrastructure.repository import InMemoryLedger

_OPERATOR = Principal(user_id="op1", role="operator")


def _sql_ledger(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'parity.sqlite3'}")
    metadata.create_all(engine)
    return SqlLedger(str(tmp_path / "parity.sqlite3"), models=domain_models, engine=engine)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _shift(ledger, **kw) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8), **kw)
    ledger.create_shift(shift)
    if ledger.get_user_by_id("op1") is None:
        ledger.add_user(domain_models.User(user_id="op1", username="op1", password_hash="x", role="operator"))
    ledger.add_assignment(domain_models.ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="op1"))
    return shift


def _bare_handover(from_shift_id, to_shift_id, **kw) -> Handover:
    return Handover(from_shift_id=from_shift_id, to_shift_id=to_shift_id, created_by="op1", **kw)


def _handover_with_one_task_item(ledger) -> Handover:
    """A real server-derived handover with exactly one item, so single-field
    mutations on that item can be isolated (HOV-REV-F9)."""
    from operations_domain.models import EvidenceRef, Task

    s1, s2 = _shift(ledger), _shift(ledger)
    task = Task(
        shift_id=s1.shift_id, title="Inspect crane", owner_id="op9",
        due_at=datetime.now(timezone.utc) + timedelta(hours=2),
        evidence=[EvidenceRef(source_type="message", source_id="m1")],
    )
    ledger.add_task(task)
    return HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)


# --- R21: source/destination shift existence --------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_missing_source_shift_rejected_with_no_partial_write(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    dest = _shift(ledger)
    handover = _bare_handover(uuid4(), dest.shift_id)

    with pytest.raises(ValueError, match="source shift not found"):
        ledger.add_handover(handover)
    with pytest.raises(KeyError):
        ledger.get_handover(handover.handover_id)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_missing_destination_shift_rejected_with_no_partial_write(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    source = _shift(ledger)
    handover = _bare_handover(source.shift_id, uuid4())

    with pytest.raises(ValueError, match="destination shift not found"):
        ledger.add_handover(handover)
    with pytest.raises(KeyError):
        ledger.get_handover(handover.handover_id)


# --- R21: duplicate aggregate id ---------------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_aggregate_id_rejected_with_no_partial_write(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    handover = _bare_handover(s1.shift_id, s2.shift_id)
    ledger.add_handover(handover)

    duplicate = handover.model_copy(deep=True)
    with pytest.raises(ValueError, match="duplicate handover_id"):
        ledger.add_handover(duplicate)
    # The original persisted handover is untouched (not doubled, not corrupted).
    assert ledger.get_handover(handover.handover_id).handover_id == handover.handover_id


# --- R21: duplicate item source within one handover --------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_duplicate_item_source_within_handover_rejected_with_no_partial_write(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    handover_id = uuid4()
    same_task_id = uuid4()
    items = [
        HandoverItem(
            handover_id=handover_id, source_record_type="Task", source_record_id=same_task_id,
            source_digest="digest-a", summary="first copy",
        ),
        HandoverItem(
            handover_id=handover_id, source_record_type="Task", source_record_id=same_task_id,
            source_digest="digest-b", summary="duplicate copy",
        ),
    ]
    handover = _bare_handover(s1.shift_id, s2.shift_id, handover_id=handover_id, items=items)

    with pytest.raises(ValueError, match="duplicate handover item source"):
        ledger.add_handover(handover)
    with pytest.raises(KeyError):
        ledger.get_handover(handover_id)


# --- R21: item/aggregate mismatch --------------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_item_aggregate_mismatch_rejected_with_no_partial_write(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    handover_id = uuid4()
    item = HandoverItem(
        handover_id=uuid4(),  # deliberately NOT handover_id
        source_record_type="Task", source_record_id=uuid4(),
        source_digest="digest-x", summary="orphaned item",
    )
    handover = _bare_handover(s1.shift_id, s2.shift_id, handover_id=handover_id, items=[item])

    with pytest.raises(ValueError, match="handover item aggregate mismatch"):
        ledger.add_handover(handover)
    with pytest.raises(KeyError):
        ledger.get_handover(handover_id)


# --- R21: no raw IntegrityError ever escapes ---------------------------------

def test_sql_backend_never_leaks_raw_integrity_error(tmp_path):
    from sqlalchemy.exc import IntegrityError

    ledger = _sql_ledger(tmp_path)
    s1, s2 = _shift(ledger), _shift(ledger)
    handover = _bare_handover(s1.shift_id, s2.shift_id)
    ledger.add_handover(handover)

    duplicate = handover.model_copy(deep=True)
    try:
        ledger.add_handover(duplicate)
    except IntegrityError:
        pytest.fail("raw SQLAlchemy IntegrityError escaped add_handover")
    except ValueError:
        pass


# --- R22: immutable snapshot on put ------------------------------------------

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_rejects_shift_pair_change(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2, s3 = _shift(ledger), _shift(ledger), _shift(ledger)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)

    mutated = ledger.get_handover(handover.handover_id)
    mutated.to_shift_id = s3.shift_id
    with pytest.raises(ValueError, match="handover snapshot is immutable"):
        ledger.put_handover(mutated)

    unchanged = ledger.get_handover(handover.handover_id)
    assert unchanged.to_shift_id == s2.shift_id


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_rejects_items_change(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)

    mutated = ledger.get_handover(handover.handover_id)
    mutated.items = [
        HandoverItem(
            handover_id=handover.handover_id, source_record_type="Task", source_record_id=uuid4(),
            source_digest="forged-digest", summary="injected item",
        )
    ]
    with pytest.raises(ValueError, match="handover snapshot is immutable"):
        ledger.put_handover(mutated)

    unchanged = ledger.get_handover(handover.handover_id)
    assert unchanged.items == []


# --- HOV-REV-F9: every item field individually, not just (type, id, digest) -

_ITEM_FIELD_MUTATIONS = {
    "summary": lambda item: setattr(item, "summary", "mutated summary"),
    "owner_id": lambda item: setattr(item, "owner_id", "someone-else"),
    "due_at": lambda item: setattr(item, "due_at", item.due_at + timedelta(days=1)),
    "risk_class": lambda item: setattr(item, "risk_class", "R3" if str(item.risk_class) != "R3" else "R2"),
    "item_id": lambda item: setattr(item, "item_id", uuid4()),
    "handover_id": lambda item: setattr(item, "handover_id", uuid4()),
    "evidence": lambda item: item.evidence.append(EvidenceRef(source_type="message", source_id="forged")),
}


@pytest.mark.parametrize("field", sorted(_ITEM_FIELD_MUTATIONS))
@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_rejects_single_item_field_mutation(tmp_path, name, field):
    ledger = dict(_backends(tmp_path))[name]
    handover = _handover_with_one_task_item(ledger)

    mutated = ledger.get_handover(handover.handover_id)
    _ITEM_FIELD_MUTATIONS[field](mutated.items[0])
    with pytest.raises(ValueError, match="handover snapshot is immutable"):
        ledger.put_handover(mutated)

    unchanged = ledger.get_handover(handover.handover_id)
    if field == "evidence":
        assert len(unchanged.items[0].evidence) == len(handover.items[0].evidence)
    else:
        assert getattr(unchanged.items[0], field) == getattr(handover.items[0], field)


# --- HOV-REV-F9: aggregate created_at/created_by are immutable -------------

_AGGREGATE_FIELD_MUTATIONS = {
    "created_at": lambda h: setattr(h, "created_at", h.created_at + timedelta(days=1)),
    "created_by": lambda h: setattr(h, "created_by", "someone-else"),
}


@pytest.mark.parametrize("field", sorted(_AGGREGATE_FIELD_MUTATIONS))
@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_rejects_single_aggregate_field_mutation(tmp_path, name, field):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    created = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)
    # Compare against a fresh get_handover() baseline, not the create() return
    # value: created_at is DB-generated (server_default=func.now()), not
    # persisted from the Python object, so SQLite's second-precision/naive
    # value never equals the microsecond-precision/tz-aware Python one.
    original = ledger.get_handover(created.handover_id)

    mutated = ledger.get_handover(created.handover_id)
    _AGGREGATE_FIELD_MUTATIONS[field](mutated)
    with pytest.raises(ValueError, match="handover snapshot is immutable"):
        ledger.put_handover(mutated)

    unchanged = ledger.get_handover(created.handover_id)
    assert getattr(unchanged, field) == getattr(original, field)


@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_put_handover_allows_lifecycle_only_change(tmp_path, name):
    ledger = dict(_backends(tmp_path))[name]
    s1, s2 = _shift(ledger), _shift(ledger)
    handover = HandoverService(ledger).create(s1.shift_id, s2.shift_id, _OPERATOR)

    reviewed = ledger.get_handover(handover.handover_id)
    reviewed.status = "REVIEWED"
    reviewed.reviewed_by = "sup1"
    reviewed.reviewed_at = datetime.now(timezone.utc)
    reviewed.version += 1
    stored = ledger.put_handover(reviewed)

    assert stored.status == "REVIEWED" or str(stored.status) == "REVIEWED"
    fetched = ledger.get_handover(handover.handover_id)
    assert str(fetched.status) == "REVIEWED"
    assert fetched.reviewed_by == "sup1"
    assert fetched.version == 2
