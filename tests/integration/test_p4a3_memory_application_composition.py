"""P4-A3 SPEC R5/R10 - build_application_memory composition integration.

Exercises the real assignment boundary + InMemoryLedger + a real
ledger-bound source revalidator through the pure ``ApplicationMemory`` service,
proving admission, read, and stale-source omission on read. The source is a
real ``Task`` record; no provider, network, route or persistence is involved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from application_memory.hashing import content_digest, provenance_digest
from application_memory.models import (
    AdmissionRequestV1,
    MemoryClassification,
    MemoryFinalOutcome,
    MemoryLayer,
    MemoryPurpose,
    SourceRefV1,
    SourceType,
)
from cvf_runtime.identity import Principal
from operations_domain.models import Shift, Task
from workspace_api.application.application_memory import build_application_memory
from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _seeded_workspace():
    ledger = InMemoryLedger()
    shift = Shift(name="Day", starts_at=NOW, ends_at=NOW.replace(hour=20))
    ledger.create_shift(shift)
    task = Task(shift_id=shift.shift_id, title="Escalation follow-up required")
    ledger.add_task(task)
    ledger.add_user(User(user_id="op1", username="op1", password_hash="x", role="viewer"))
    ledger.add_user(User(user_id="sup1", username="sup1", password_hash="x", role="shift_supervisor"))
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    principal = Principal(user_id="op1", role="viewer")
    scope = AssignmentScope(ledger)
    return ledger, shift, task, principal, scope


def _task_source(task: Task) -> SourceRefV1:
    return SourceRefV1(
        source_type=SourceType.TASK, source_id=str(task.task_id), source_version=str(task.version),
        source_content_digest_sha256=content_digest(task.title),
        provenance_digest_sha256=provenance_digest(
            source_type=SourceType.TASK.value, source_id=str(task.task_id),
            source_version=str(task.version), owner_scope=str(task.shift_id),
        ),
    )


def _request(source: SourceRefV1) -> AdmissionRequestV1:
    return AdmissionRequestV1(
        layer=MemoryLayer.SESSION, purpose=MemoryPurpose.ACTIVE_TASK_CONTEXT,
        classification=MemoryClassification.INTERNAL, content="remember the escalation",
        source=source, requested_ttl_seconds=3600,
    )


def test_admit_and_read_through_real_ledger_revalidator():
    ledger, shift, task, principal, scope = _seeded_workspace()
    bound = build_application_memory(
        ledger=ledger, principal=principal, shift=shift, assignment_scope=scope,
        clock=lambda: NOW,
    )
    outcome = bound.admit(request=_request(_task_source(task)))
    assert outcome.receipt.final_outcome is MemoryFinalOutcome.ADMITTED

    read = bound.read(limit=10)
    assert read.receipt.final_outcome is MemoryFinalOutcome.READ_COMPLETE
    assert len(read.entries) == 1
    assert read.entries[0].purpose is MemoryPurpose.ACTIVE_TASK_CONTEXT


def test_stale_source_omitted_on_read():
    ledger, shift, task, principal, scope = _seeded_workspace()
    bound = build_application_memory(
        ledger=ledger, principal=principal, shift=shift, assignment_scope=scope,
        clock=lambda: NOW,
    )
    bound.admit(request=_request(_task_source(task)))

    # Mutate the source record: a new title and version make the admitted
    # source digest stale at read time (use-time source revalidation).
    ledger.put_task(Task(task_id=task.task_id, shift_id=shift.shift_id, title="Resolved - no longer escalation", version=2))
    read = bound.read(limit=10)
    assert read.entries == ()
    assert read.receipt.omitted_count == 1


def test_admission_with_wrong_content_digest_fails_closed():
    ledger, shift, task, principal, scope = _seeded_workspace()
    bound = build_application_memory(
        ledger=ledger, principal=principal, shift=shift, assignment_scope=scope,
        clock=lambda: NOW,
    )
    source = _task_source(task)
    forged = source.model_copy(update={"source_content_digest_sha256": "0" * 64})
    outcome = bound.admit(request=_request(forged))
    assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
    assert outcome.receipt.appended_entries == 0


def test_unassigned_principal_is_denied():
    ledger, shift, task, principal, scope = _seeded_workspace()
    outsider = Principal(user_id="op2", role="viewer")
    with pytest.raises(Exception):
        build_application_memory(
            ledger=ledger, principal=outsider, shift=shift, assignment_scope=scope,
            clock=lambda: NOW,
        )


def test_composition_never_persists_or_opens_a_route():
    import workspace_api.application.application_memory as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "APIRouter" not in source
    assert "@router" not in source
    assert ".add_route(" not in source
    assert "INSERT INTO" not in source
    assert "ledger.append_audit" not in source
    assert "add_task" not in source and "put_task" not in source and "add_event" not in source


def test_same_shift_source_admitted():
    """P4A3-REV-F1 - a shift-owned source belonging to the bound shift is
    admitted normally."""
    ledger, shift, task, principal, scope = _seeded_workspace()
    bound = build_application_memory(
        ledger=ledger, principal=principal, shift=shift, assignment_scope=scope,
        clock=lambda: NOW,
    )
    outcome = bound.admit(request=_request(_task_source(task)))
    assert outcome.receipt.final_outcome is MemoryFinalOutcome.ADMITTED
    assert outcome.receipt.appended_entries == 1


def test_cross_shift_source_rejected_zero_mutation():
    """P4A3-REV-F1 - a correctly described task from another shift must fail
    closed as SOURCE_REVALIDATION_FAILED with zero store mutation."""
    ledger, shift, task, principal, scope = _seeded_workspace()
    bound = build_application_memory(
        ledger=ledger, principal=principal, shift=shift, assignment_scope=scope,
        clock=lambda: NOW,
    )
    other_shift = Shift(name="Other", starts_at=NOW, ends_at=NOW.replace(hour=20))
    ledger.create_shift(other_shift)
    other_task = Task(shift_id=other_shift.shift_id, title="Other shift escalation")
    ledger.add_task(other_task)
    outcome = bound.admit(request=_request(_task_source(other_task)))
    assert outcome.receipt.final_outcome is MemoryFinalOutcome.SOURCE_REVALIDATION_FAILED
    assert outcome.receipt.appended_entries == 0
    assert outcome.receipt.appended_tombstones == 0
