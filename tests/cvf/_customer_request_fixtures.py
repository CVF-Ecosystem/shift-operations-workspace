"""Shared fixtures for the split customer-request test modules.

Split out of test_customer_request_vertical.py (HOV-REV-F5 repair,
P2A-HANDOVER-VERTICAL Amendment 2, SPEC R20) to bring that legacy 321-line
module under the hard 300-line limit alongside the new transition/atomicity
module it no longer needs. Not a behavior change to any existing test.

tests/cvf/test_customer_request_repair.py imports several of these names
directly from test_customer_request_vertical - that module re-imports (and so
re-exposes) them unchanged from here, so this split does not break that file,
which is outside this repair's authorized changed set.
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
from operations_domain.models import CustomerRequest, Shift
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app


def _sql_ledger(tmp_path, name="customer_requests.sqlite3") -> SqlLedger:
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)


def _operator() -> Principal:
    return Principal(user_id="op1", role="operator")


def _viewer() -> Principal:
    return Principal(user_id="v1", role="viewer")


def _new_shift(ledger) -> Shift:
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    return shift


def _request(shift=None, **overrides) -> CustomerRequest:
    kwargs = dict(customer_id="cust-1", summary="Container missing paperwork")
    if shift is not None:
        kwargs["shift_id"] = shift.shift_id
    kwargs.update(overrides)
    return CustomerRequest(**kwargs)


def _client_for(ledger) -> TestClient:
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)


def _clear_overrides() -> None:
    app.dependency_overrides.pop(get_ledger, None)


def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]


def _make_ready_handover(ledger, shift):
    """HOV-AUTH-F4: a genuine server-derived, reviewed and ACKNOWLEDGED
    (empty) handover via HandoverService - the real open_handover_items_linked
    freeze prerequisite - never a direct terminal-state insertion or mock."""
    dest = _new_shift(ledger)
    svc = HandoverService(ledger)
    handover = svc.create(shift.shift_id, dest.shift_id, _operator())
    handover = svc.review(handover.handover_id, Principal(user_id="sup1", role="shift_supervisor"))
    return svc.acknowledge(handover.handover_id, Principal(user_id="sup2", role="shift_supervisor"))


class _BoomOnAudit(Exception):
    pass


def _raise_on_audit(*args, **kwargs):
    raise _BoomOnAudit("simulated audit sink failure")
