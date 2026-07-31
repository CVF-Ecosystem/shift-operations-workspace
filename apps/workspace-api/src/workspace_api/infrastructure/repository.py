from __future__ import annotations
import copy
from collections.abc import Iterable
from contextlib import contextmanager
from threading import RLock
from uuid import UUID
from cvf_runtime.audit import AuditLog

from operations_domain.models import (
    ApprovalReceipt,
    Correction,
    CustomerRequest,
    Handover,
    Incident,
    Message,
    OperationalEvent,
    Report,
    Shift,
    ShiftStatus,
    Task,
    TaskCreationIntent,
)

# Documented exception E2 (SPEC R5.2): User did NOT move to operations-domain;
# its canonical home stays the application package (auth boundary). The only
# model still imported from workspace_api.domain.models here.
from workspace_api.domain.models import User
from workspace_api.infrastructure._approval_store import _ApprovalStoreMixin
from workspace_api.infrastructure._handover_repository import _HandoverRepositoryMixin
from workspace_api.infrastructure._incident_repository import _IncidentRepositoryMixin
from workspace_api.infrastructure._report_repository import _ReportRepositoryMixin

class InMemoryLedger(_ApprovalStoreMixin, _IncidentRepositoryMixin, _HandoverRepositoryMixin, _ReportRepositoryMixin):
    def __init__(self):
        self._lock = RLock()
        self.shifts: dict[UUID, Shift] = {}
        self.messages: dict[UUID, Message] = {}
        self.events: dict[UUID, OperationalEvent] = {}
        self.corrections: dict[UUID, Correction] = {}
        self.tasks: dict[UUID, Task] = {}
        self.customer_requests: dict[UUID, CustomerRequest] = {}
        self.incidents: dict[UUID, Incident] = {}
        self.handovers: dict[UUID, Handover] = {}
        self.reports: dict[UUID, Report] = {}
        self.users: dict[str, User] = {}
        self.approval_receipts: dict[UUID, ApprovalReceipt] = {}
        self.task_creation_intents: dict[UUID, TaskCreationIntent] = {}
        self._audit = AuditLog()

    @contextmanager
    def transaction(self):
        """Unit-of-work: snapshot state, roll back if the block raises.

        InMemoryLedger has no real database transaction, so this simulates
        one: every dict this ledger owns is DEEP-copied on entry (a shallow
        copy is not enough — callers mutate Pydantic model objects in place,
        e.g. ``event.state = CONFIRMED``, before calling ``put_event``; a
        shallow dict copy would still hold a reference to that same mutated
        object). Any exception restores the snapshot before propagating -
        "state change committed, audit write failed" is impossible here,
        matching SqlLedger's real transaction (P-FIX-2 / High Finding #5).
        """
        with self._lock:
            snapshot = copy.deepcopy(
                (
                    self.shifts,
                    self.messages,
                    self.events,
                    self.corrections,
                    self.tasks,
                    self.customer_requests,
                    self.incidents,
                    self.handovers,
                    self.reports,
                    self.users,
                    self.approval_receipts,
                    self.task_creation_intents,
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
                    self.customer_requests,
                    self.incidents,
                    self.handovers,
                    self.reports,
                    self.users,
                    self.approval_receipts,
                    self.task_creation_intents,
                    entries,
                ) = snapshot
                self._audit = AuditLog()
                for entry in entries:
                    self._audit.append(entry)
                raise

    def report_mutation_transaction(self):
        return self.transaction()  # F6: self._lock is already a single-writer guarantee.

    def report_freeze_transaction(self):
        return self.transaction()  # SPEC R22: same single-writer guarantee.

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
        # SPEC R9: shift/freeze check, duplicate/evidence refusal, then
        # deep-copy in and out so caller mutation never touches stored truth.
        self._assert_shift_not_frozen(message.shift_id, "add message to a frozen shift")
        if message.message_id in self.messages:
            raise ValueError(f"duplicate message_id: {message.message_id}")
        if message.evidence:
            raise ValueError("message evidence is not supported by the persisted schema")
        stored = message.model_copy(deep=True)
        self.messages[message.message_id] = stored
        return stored.model_copy(deep=True)

    def get_message(self, message_id: UUID, *, unit=None) -> Message:
        # Deep copy, not the live reference — see get_shift() for why.
        return self.messages[message_id].model_copy(deep=True)

    def message_exists(self, message_id: UUID, *, unit=None) -> bool:
        return message_id in self.messages

    def add_event(self, event: OperationalEvent, *, unit=None) -> OperationalEvent:
        self._assert_shift_not_frozen(event.shift_id, "add event to a frozen shift")
        self.events[event.event_id] = event
        return event

    def get_event(self, event_id: UUID, *, unit=None) -> OperationalEvent:
        # Copy, not the live reference — see get_shift() for why.
        return self.events[event_id].model_copy()

    def list_events_for_shift(self, shift_id: UUID, *, unit=None) -> list[OperationalEvent]:
        # P2C-OPERATIONS-CONSOLE-READ-SLICE (SPEC R3): deterministic event-list
        # query. Order: starts_at non-null first, ascending starts_at, then
        # ascending str(event_id). Evidence preserved (model_copy includes it).
        events = [
            e.model_copy() for e in self.events.values() if e.shift_id == shift_id
        ]
        events.sort(
            key=lambda e: (
                e.starts_at is None,
                e.starts_at if e.starts_at is not None else "",
                str(e.event_id),
            )
        )
        return events

    def put_event(self, event: OperationalEvent, *, allow_when_frozen: bool = False, unit=None) -> OperationalEvent:
        if not allow_when_frozen:
            self._assert_shift_not_frozen(event.shift_id, "modify event in a frozen shift")
        self.events[event.event_id] = event
        return event

    def add_task(self, task: Task, *, unit=None) -> Task:
        self._assert_shift_not_frozen(task.shift_id, "add task to a frozen shift")
        # R9.6 (P2B-APPROVER-IDENTITY-RECONCILIATION): a second POST /tasks
        # against an already-consumed creation intent reuses
        # task_id := intent_id and must be refused, independent of receipt
        # state. Mirrors SqlLedger's primary-key-constraint behaviour so the
        # application layer maps both backends the same way.
        if task.task_id in self.tasks:
            raise ValueError(f"duplicate task_id: {task.task_id}")
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

    def add_customer_request(self, request: CustomerRequest, *, unit=None) -> CustomerRequest:
        # shift_id is nullable on CustomerRequest (unlike Task.shift_id): a
        # request not tied to any shift has no frozen-shift invariant to
        # check, so only guard when a shift_id is actually present.
        if request.shift_id is not None:
            self._assert_shift_not_frozen(
                request.shift_id, "add customer request to a frozen shift"
            )
        # Store and return COPIES, not the caller's live object — see
        # get_shift() for why. Independent review (2026-07-22) found that
        # add/get/put_customer_request were the one entity family that kept
        # the caller-owned object itself: `created = svc.create(...)` followed
        # by `created.status = CLOSED` silently rewrote persisted state with
        # no permission/lifecycle/transaction/audit involved at all.
        stored = request.model_copy()
        self.customer_requests[request.request_id] = stored
        return stored.model_copy()

    def get_customer_request(self, request_id: UUID, *, unit=None) -> CustomerRequest:
        # Copy, not the live reference — see get_shift() for why.
        return self.customer_requests[request_id].model_copy()

    def put_customer_request(self, request: CustomerRequest, *, unit=None) -> CustomerRequest:
        if request.shift_id is not None:
            self._assert_shift_not_frozen(
                request.shift_id, "modify customer request in a frozen shift"
            )
        stored = request.model_copy()
        self.customer_requests[request.request_id] = stored
        return stored.model_copy()

    def add_user(self, user: User, *, unit=None) -> User:
        with self._lock:
            if any(u.username == user.username for u in self.users.values()):
                raise ValueError(f"username already registered: {user.username!r}")
            stored = user.model_copy()
            self.users[user.user_id] = stored
            return stored.model_copy()

    def get_user_by_username(self, username: str, *, unit=None) -> User | None:
        with self._lock:
            for user in self.users.values():
                if user.username == username:
                    return user.model_copy()
        return None

    def get_user_by_id(self, user_id: str, *, unit=None) -> User | None:
        with self._lock:
            user = self.users.get(user_id)
            return user.model_copy() if user is not None else None

    # --- approval receipts / task creation intents: see _ApprovalStoreMixin ---

    def add_correction(self, correction: Correction, *, unit=None) -> Correction:
        # Append-only, explicitly ALLOWED post-freeze - no shift-frozen guard.
        with self._lock:
            if correction.correction_id in self.corrections:
                raise ValueError("Correction already recorded")
            self.corrections[correction.correction_id] = correction
        return correction

    def corrections_for(self, record_id: UUID, *, unit=None) -> list[Correction]:  # unit: F6 parity
        with self._lock:
            return [c for c in self.corrections.values() if c.record_id == record_id]

    # --- audit (append-only) ---
    def append_audit(self, record, *, unit=None) -> None:
        self._audit.append(record)

    def audit_entries_for(self, record_id: str) -> list:
        return self._audit.entries_for(record_id)

ledger = InMemoryLedger()
