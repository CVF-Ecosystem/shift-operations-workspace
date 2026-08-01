"""Shared fixtures for the split C3b1 read/readiness test modules
(P2C-MUTATION-FULL-UI-C3B1, SPEC R11/R35-R37).

Mirrors the pattern established by `_assignment_scope_fixtures.py` /
`_customer_request_fixtures.py`: real InMemory/SQLite backends through the
actual FastAPI dependency chain, never a mock.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for _rel in ("apps/workspace-api/src", "packages/operations-ledger/src", "packages/operations-domain/src"):
    if str(REPO_ROOT / _rel) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / _rel))

from fastapi.testclient import TestClient

from operations_domain.models import (
    CustomerRequest,
    Message,
    OperationalEvent,
    RiskClass,
    Shift,
    Task,
    TaskCreationIntent,
)
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app


def make_inmemory() -> InMemoryLedger:
    return InMemoryLedger()


def make_sqlite() -> SqlLedger:
    from sqlalchemy.pool import StaticPool

    # StaticPool + check_same_thread=False: TestClient runs the route handler
    # in a worker thread, matching the pattern test_p2c_read_api.py uses.
    engine = make_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    metadata.create_all(engine)
    return SqlLedger("sqlite://", models=domain_models, engine=engine)


def new_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="C3b1 shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def seed_user(ledger, user_id: str, role: str) -> None:
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(User(user_id=user_id, username=user_id, password_hash="test-only", role=role))


def seed_active_assignment(ledger, shift_id, user_id: str, role: str) -> None:
    seed_user(ledger, user_id, role)
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def new_message(shift_id, *, sender_id="operator-1", text="hello", created_at=None) -> Message:
    kwargs = dict(shift_id=shift_id, sender_id=sender_id, text=text)
    if created_at is not None:
        kwargs["created_at"] = created_at
    return Message(**kwargs)


def new_event(shift_id, *, risk_class=RiskClass.R2, title="E1") -> OperationalEvent:
    return OperationalEvent(shift_id=shift_id, event_type="equipment_downtime", title=title, risk_class=risk_class)


def new_task_creation_intent(ledger, shift_id, *, risk_class=RiskClass.R2, created_by="operator-1") -> TaskCreationIntent:
    intent = TaskCreationIntent(
        shift_id=shift_id,
        risk_class=risk_class,
        payload_snapshot={"title": "T1"},
        payload_digest="ab" * 32,
        created_by=created_by,
    )
    ledger.add_task_creation_intent(intent)
    return intent


def with_ledger(ledger, fn):
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        return fn(TestClient(app))
    finally:
        app.dependency_overrides.pop(get_ledger, None)
