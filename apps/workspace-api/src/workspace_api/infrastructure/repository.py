from __future__ import annotations
import copy
from collections.abc import Iterable
from contextlib import contextmanager
from threading import RLock
from uuid import UUID
from cvf_runtime.audit import AuditLog

from workspace_api.domain.models import Shift, Message, OperationalEvent, ShiftStatus, Correction, Task

class InMemoryLedger:
    def __init__(self):
        self._lock = RLock()
        self.shifts: dict[UUID, Shift] = {}
        self.messages: dict[UUID, Message] = {}
        self.events: dict[UUID, OperationalEvent] = {}
        self.corrections: dict[UUID, Correction] = {}
        self.tasks: dict[UUID, Task] = {}
        self._audit = AuditLog()

    @contextmanager
    def transaction(self):
        """Unit-of-work: snapshot state, roll back if the block raises.

        InMemoryLedger has no real database transaction, so this simulates
        one: every dict this ledger owns is DEEP-copied on entry (a shallow
        copy is not enough — callers mutate Pydantic model objects in place,
        e.g. ``event.state = CONFIRMED``, before calling ``put_event``; a
        shallow dict copy would still hold a reference to that same mutated
        object). Any exception inside the block restores the deep-copied
        snapshot before propagating. This is what makes "state change
        committed, audit write failed" an impossible outcome for
        InMemoryLedger, matching SqlLedger's real transaction (P-FIX-2 / High
        Finding #5).
        """
        with self._lock:
            snapshot = copy.deepcopy(
                (
                    self.shifts,
                    self.messages,
                    self.events,
                    self.corrections,
                    self.tasks,
                    self._audit.all(),
                )
            )
            try:
                yield self
            except BaseException:
                (
                    self.shifts,
                    self.messages,
                    self.events,
                    self.corrections,
                    self.tasks,
                    entries,
                ) = snapshot
                self._audit = AuditLog()
                for entry in entries:
                    self._audit.append(entry)
                raise

    def create_shift(self, shift: Shift, *, unit=None) -> Shift:
        with self._lock:
            self.shifts[shift.shift_id] = shift
        return shift

    def get_shift(self, shift_id: UUID, *, unit=None) -> Shift:
        # Return a COPY, not the stored object. SqlLedger always reconstructs
        # a fresh object from a row, so callers can safely mutate what they
        # get back before calling put_*(); if this returned the live
        # reference, mutating it would silently change stored state before
        # any transaction/audit step ran (found while adding P-FIX-2 atomic
        # unit-of-work tests: EventService mutates `event.state` before
        # entering `transaction()`, which must not touch stored state yet).
        return self.shifts[shift_id].model_copy()

    def list_shifts(self) -> Iterable[Shift]:
        return list(self.shifts.values())

    def close_shift(self, shift_id: UUID, *, unit=None) -> Shift:
        with self._lock:
            shift = self.shifts[shift_id]
            if shift.status == ShiftStatus.FROZEN:
                raise ValueError("Cannot close a frozen shift")
            shift.status = ShiftStatus.CLOSED
            shift.version += 1
            self.shifts[shift_id] = shift
            return shift

    def freeze_shift(self, shift_id: UUID, *, unit=None) -> Shift:
        with self._lock:
            shift = self.shifts[shift_id]
            if shift.status == ShiftStatus.FROZEN:
                return shift
            shift.status = ShiftStatus.FROZEN
            shift.version += 1
            self.shifts[shift_id] = shift
            return shift

    def _assert_shift_not_frozen(self, shift_id: UUID, what: str) -> None:
        # Post-freeze, the ONLY permitted change is a correction record
        # (freeze-policy.yaml: post_freeze_mutation = correction_record_only).
        # Every direct mutation path must be blocked here, not just at "create".
        shift = self.get_shift(shift_id)
        if shift.status == ShiftStatus.FROZEN:
            raise ValueError(f"Cannot {what}: shift is frozen")

    def add_message(self, message: Message, *, unit=None) -> Message:
        self._assert_shift_not_frozen(message.shift_id, "add message to a frozen shift")
        self.messages[message.message_id] = message
        return message

    def add_event(self, event: OperationalEvent, *, unit=None) -> OperationalEvent:
        self._assert_shift_not_frozen(event.shift_id, "add event to a frozen shift")
        self.events[event.event_id] = event
        return event

    def get_event(self, event_id: UUID, *, unit=None) -> OperationalEvent:
        # Copy, not the live reference — see get_shift() for why.
        return self.events[event_id].model_copy()

    def put_event(self, event: OperationalEvent, *, allow_when_frozen: bool = False, unit=None) -> OperationalEvent:
        if not allow_when_frozen:
            self._assert_shift_not_frozen(event.shift_id, "modify event in a frozen shift")
        self.events[event.event_id] = event
        return event

    def add_task(self, task: Task, *, unit=None) -> Task:
        self._assert_shift_not_frozen(task.shift_id, "add task to a frozen shift")
        self.tasks[task.task_id] = task
        return task

    def get_task(self, task_id: UUID, *, unit=None) -> Task:
        # Copy, not the live reference — see get_shift() for why.
        return self.tasks[task_id].model_copy()

    def put_task(self, task: Task, *, allow_when_frozen: bool = False, unit=None) -> Task:
        if not allow_when_frozen:
            self._assert_shift_not_frozen(task.shift_id, "modify task in a frozen shift")
        self.tasks[task.task_id] = task
        return task

    def add_correction(self, correction: Correction, *, unit=None) -> Correction:
        # Corrections are append-only and are explicitly ALLOWED post-freeze:
        # a correction record is the permitted way to change confirmed/frozen
        # data and must never be overwritten. No shift-frozen guard here.
        with self._lock:
            if correction.correction_id in self.corrections:
                raise ValueError("Correction already recorded")
            self.corrections[correction.correction_id] = correction
        return correction

    def corrections_for(self, record_id: UUID) -> list[Correction]:
        with self._lock:
            return [c for c in self.corrections.values() if c.record_id == record_id]

    # --- audit (append-only) ---
    def append_audit(self, record, *, unit=None) -> None:
        self._audit.append(record)

    def audit_entries_for(self, record_id: str) -> list:
        return self._audit.entries_for(record_id)

ledger = InMemoryLedger()
