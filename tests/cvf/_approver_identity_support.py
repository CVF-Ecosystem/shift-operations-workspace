"""Shared fixtures/helpers for the P2B-APPROVER-IDENTITY-RECONCILIATION AC
suite (CVF-FILE-SPLIT-GUARD-HARDENING split of
`test_approver_identity_reconciliation.py`).

Every helper below is byte-identical to the original module; only its home
changed, so the three test modules that import it
(`test_approver_identity_reconciliation.py`, `test_approver_identity_receipts.py`,
`test_approver_identity_task_intents.py`) exercise the exact same fixtures.
"""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from workspace_api.application import approval_service
from workspace_api.application.task_service import TaskService
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger
from workspace_api.main import app
from operations_domain.models import DataState, EvidenceRef, OperationalEvent, RiskClass, Shift, Task

_R3_PAIRS = (("sup2", "shift_supervisor"), ("mgr1", "responsible_manager"))
_R4_PAIRS = (("mgr1", "responsible_manager"), ("exec1", "authorized_executive"))

def _sql_ledger(tmp_path, name="approver_identity.sqlite3"):
    db = tmp_path / name
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)

def _backends(tmp_path): return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]
def _client_for(ledger):
    app.dependency_overrides[get_ledger] = lambda: ledger
    return TestClient(app)
def _clear_overrides(): app.dependency_overrides.pop(get_ledger, None)

def _assign(ledger, shift_id, user_id, role="operator", *, is_active=True):
    if ledger.get_user_by_id(user_id) is None:
        _user(ledger, user_id, role, is_active=is_active)
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _new_shift(ledger):
    now = datetime.now(timezone.utc)
    shift = Shift(name="Day", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    _assign(ledger, shift.shift_id, "sup1", "shift_supervisor")
    return shift

def _new_event(ledger, *, risk=RiskClass.R3, evidence_count=1):
    event = OperationalEvent(
        shift_id=_new_shift(ledger).shift_id,
        event_type="equipment_downtime",
        title="Crane 3 stopped",
        risk_class=risk,
        state=DataState.PROPOSED,
        evidence=[EvidenceRef(source_type="message", source_id=f"m{i}") for i in range(evidence_count)],
    )
    ledger.add_event(event)
    return event

def _user(ledger, user_id: str, role: str, *, is_active: bool = True) -> None:
    if ledger.get_user_by_id(user_id) is not None:
        return
    ledger.add_user(User(user_id=user_id, username=user_id, password_hash="x", role=role, is_active=is_active))

def _shift_id_of(ledger, record_type, record_id):
    if record_type == "Task":
        return ledger.get_task_creation_intent(record_id).shift_id
    return ledger.get_event(record_id).shift_id

def _receipt(ledger, *, record_type, action, record_id, approver_id, role):
    _assign(ledger, _shift_id_of(ledger, record_type, record_id), approver_id, role)
    return approval_service.create_approval_receipt(
        ledger, Principal(user_id=approver_id, role=role), record_type=record_type, action=action, record_id=record_id
    )[0]

def _seat(ledger, record_id, approver_id, role, *, record_type="OperationalEvent", action="event.confirm", is_active=True):
    _user(ledger, approver_id, role, is_active=is_active)
    _assign(ledger, _shift_id_of(ledger, record_type, record_id), approver_id, role, is_active=is_active)
    return _receipt(ledger, record_type=record_type, action=action, record_id=record_id, approver_id=approver_id, role=role)

def _fill_seats(ledger, record_id, pairs=_R3_PAIRS, *, record_type="OperationalEvent", action="event.confirm"):
    for approver_id, role in pairs:
        _seat(ledger, record_id, approver_id, role, record_type=record_type, action=action)

def _confirmer():
    return Principal(user_id="sup1", role="shift_supervisor")

def _action(a):
    return a.action if hasattr(a, "action") else a["action"]

def _r3_task_intent(ledger, *, with_receipts=True):
    _user(ledger, "sup1", "shift_supervisor")
    svc = TaskService(ledger)
    task = Task(shift_id=_new_shift(ledger).shift_id, title="Inspect crane", risk_class=RiskClass.R3, evidence=[EvidenceRef(source_type="message", source_id="m1")])
    intent = svc.create_creation_intent(task, _confirmer())
    if with_receipts:
        _fill_seats(ledger, intent.intent_id, record_type="Task", action="task.create")
    return svc, task, intent
