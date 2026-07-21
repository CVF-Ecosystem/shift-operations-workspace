from __future__ import annotations
from collections.abc import Iterable
from threading import RLock
from uuid import UUID
from cvf_runtime.audit import AuditLog

from workspace_api.domain.models import Shift, Message, OperationalEvent, ShiftStatus, Correction

class InMemoryLedger:
    def __init__(self):
        self._lock = RLock()
        self.shifts: dict[UUID, Shift] = {}
        self.messages: dict[UUID, Message] = {}
        self.events: dict[UUID, OperationalEvent] = {}
        self.corrections: dict[UUID, Correction] = {}
        self._audit = AuditLog()

    def create_shift(self, shift: Shift) -> Shift:
        with self._lock:
            self.shifts[shift.shift_id] = shift
        return shift

    def get_shift(self, shift_id: UUID) -> Shift:
        return self.shifts[shift_id]

    def list_shifts(self) -> Iterable[Shift]:
        return list(self.shifts.values())

    def freeze_shift(self, shift_id: UUID) -> Shift:
        with self._lock:
            shift = self.shifts[shift_id]
            if shift.status == ShiftStatus.FROZEN:
                return shift
            shift.status = ShiftStatus.FROZEN
            shift.version += 1
            self.shifts[shift_id] = shift
            return shift

    def add_message(self, message: Message) -> Message:
        shift = self.get_shift(message.shift_id)
        if shift.status == ShiftStatus.FROZEN:
            raise ValueError("Cannot add message to a frozen shift")
        self.messages[message.message_id] = message
        return message

    def add_event(self, event: OperationalEvent) -> OperationalEvent:
        shift = self.get_shift(event.shift_id)
        if shift.status == ShiftStatus.FROZEN:
            raise ValueError("Cannot add event to a frozen shift")
        self.events[event.event_id] = event
        return event

    def get_event(self, event_id: UUID) -> OperationalEvent:
        return self.events[event_id]

    def put_event(self, event: OperationalEvent) -> OperationalEvent:
        self.events[event.event_id] = event
        return event

    def add_correction(self, correction: Correction) -> Correction:
        # Corrections are append-only: a correction record is the permitted way
        # to change confirmed/frozen data and must never be overwritten.
        with self._lock:
            if correction.correction_id in self.corrections:
                raise ValueError("Correction already recorded")
            self.corrections[correction.correction_id] = correction
        return correction

    def corrections_for(self, record_id: UUID) -> list[Correction]:
        with self._lock:
            return [c for c in self.corrections.values() if c.record_id == record_id]

    # --- audit (append-only) ---
    def append_audit(self, record) -> None:
        self._audit.append(record)

    def audit_entries_for(self, record_id: str) -> list:
        return self._audit.entries_for(record_id)

ledger = InMemoryLedger()
