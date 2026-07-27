"""Shared fixtures for the split shift-close governance test modules.

Split out of test_shift_close_governance.py (P2A-HANDOVER-VERTICAL, SPEC R13)
to bring that legacy 313-line module under the hard 300-line limit alongside
the new freeze-interaction tests it needs (real handover readiness changed
`ShiftService.freeze` - see test_shift_close_freeze_interaction.py). Not a
behavior change to any pre-existing test; mirrors the debt baseline's
required split: "two test modules plus a shared fixtures module."
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application.handover_service import HandoverService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from operations_domain.models import Shift
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app


def operator() -> Principal:
    return Principal(user_id="op1", role="operator")


def supervisor() -> Principal:
    return Principal(user_id="sup1", role="shift_supervisor")


def receiving_supervisor() -> Principal:
    return Principal(user_id="sup2", role="shift_supervisor")


def sql_ledger(tmp_path, name="close.sqlite3") -> SqlLedger:
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def new_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def client_for(ledger) -> TestClient:
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)


def clear_overrides() -> None:
    app.dependency_overrides.pop(get_ledger, None)


def make_ready_handover(ledger, shift):
    """An ACKNOWLEDGED handover whose (empty) snapshot matches current open
    work - the real `open_handover_items_linked` freeze prerequisite
    (P2A-HANDOVER-VERTICAL) instead of the prior unimplemented-prerequisite
    override that used to cover it."""
    dest = new_shift(ledger)
    svc = HandoverService(ledger)
    handover = svc.create(shift.shift_id, dest.shift_id, operator())
    handover = svc.review(handover.handover_id, supervisor())
    return svc.acknowledge(handover.handover_id, receiving_supervisor())


__all__ = [
    "InMemoryLedger",
    "client_for",
    "clear_overrides",
    "make_ready_handover",
    "new_shift",
    "operator",
    "receiving_supervisor",
    "sql_ledger",
    "supervisor",
]
