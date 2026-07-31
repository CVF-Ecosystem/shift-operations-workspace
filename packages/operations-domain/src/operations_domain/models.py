"""Canonical operational domain models (tranche P1B-OPERATIONS-DOMAIN-EXTRACTION).

This module is the SINGLE canonical definition of every operational model and
lifecycle enum in this workspace. `workspace_api.domain.models` re-exports these
same class objects; it does not redefine them, so
`workspace_api.domain.models.Shift is operations_domain.models.Shift` holds.
Never re-declare or subclass one of these types elsewhere to "re-export" it -
that would produce two classes that fail each other's isinstance checks and
diverge in Pydantic schema output.

Dependency direction is one-way and this package is a sink: it imports only the
standard library and pydantic. It must never import `workspace_api`,
`operations_ledger`, `cvf_runtime`, `fastapi` or `sqlalchemy`.

`User` deliberately does NOT live here. It mirrors migration 003 and belongs to
the authentication boundary; its canonical home stays
`workspace_api.domain.models`. The known-principals.yaml <-> users
reconciliation (P2B-APPROVER-IDENTITY-RECONCILIATION) resolved this: `users`
is now the single runtime authority for approver identity/role/active-status,
`known-principals.yaml` is retired, and `User` still does not move here - that
was a deliberate outcome of the reconciliation, not left undecided.
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, computed_field, model_validator

class DataState(StrEnum):
    RAW = "RAW"
    NORMALIZED = "NORMALIZED"
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CORRECTED = "CORRECTED"
    FROZEN = "FROZEN"

class RiskClass(StrEnum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"

class ShiftStatus(StrEnum):
    OPEN = "OPEN"
    HANDOVER_PENDING = "HANDOVER_PENDING"
    CLOSED = "CLOSED"
    FROZEN = "FROZEN"

class EvidenceRef(BaseModel):
    evidence_id: UUID = Field(default_factory=uuid4)
    source_type: str
    source_id: str
    sha256: str | None = None

class Shift(BaseModel):
    shift_id: UUID = Field(default_factory=uuid4)
    name: str
    starts_at: datetime
    ends_at: datetime
    status: ShiftStatus = ShiftStatus.OPEN
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_window(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self

class Message(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    source: str = "INTERNAL"
    sender_id: str
    text: str
    state: DataState = DataState.RAW
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: list[EvidenceRef] = Field(default_factory=list)

class OperationalEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    event_type: str
    title: str
    description: str | None = None
    risk_class: RiskClass = RiskClass.R1
    state: DataState = DataState.PROPOSED
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    owner_id: str | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)
    version: int = 1

    @model_validator(mode="after")
    def validate_time(self):
        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            raise ValueError("ends_at cannot be before starts_at")
        return self

class Correction(BaseModel):
    correction_id: UUID = Field(default_factory=uuid4)
    record_type: str
    record_id: UUID
    reason: str
    requested_by: str
    previous_version: int
    new_version: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    CARRY_OVER = "CARRY_OVER"
    CANCELLED = "CANCELLED"


class Task(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.OPEN
    owner_id: str | None = None
    due_at: datetime | None = None
    risk_class: RiskClass = RiskClass.R1
    state: DataState = DataState.CONFIRMED
    evidence: list[EvidenceRef] = Field(default_factory=list)
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CustomerRequestStatus(StrEnum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING = "WAITING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class CustomerRequest(BaseModel):
    # Mirrors database/migrations/002_tasks_customers_reports.sql exactly: no
    # version/risk_class/state/evidence columns on this table (unlike
    # Task/OperationalEvent) - this is a simpler record type by design, not an
    # omission. Do not add those fields without first adding the matching
    # migration columns (the schema-parity test enforces exact column match).
    request_id: UUID = Field(default_factory=uuid4)
    customer_id: str
    shift_id: UUID | None = None
    summary: str
    details: str | None = None
    status: CustomerRequestStatus = CustomerRequestStatus.NEW
    source_message_id: UUID | None = None
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    promised_at: datetime | None = None
    owner_id: str | None = None


class ApprovalReceipt(BaseModel):
    """An authenticated, scope-bound approval (P2B-APPROVER-IDENTITY-RECONCILIATION).

    Created by a request authenticated as the approver: ``approver_id`` and
    ``approver_role`` are server-derived from the authenticated principal and
    a fresh `users` lookup, never from a request payload. ``payload_digest``
    is null for event actions and set only for ``task.create`` (bound to a
    `TaskCreationIntent`). ``approver_role`` is evidence only - current
    authority is always re-derived fresh at evaluation time, never trusted
    from this stored value (see cvf_runtime.approval).
    """

    receipt_id: UUID = Field(default_factory=uuid4)
    record_type: str
    record_id: UUID
    action: str
    target_version: int
    risk_class: str
    payload_digest: str | None = None
    approver_id: str
    approver_role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IncidentStatus(StrEnum):
    REPORTED = "REPORTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Incident(BaseModel):
    # Mirrors database/migrations/005_incidents.sql. Report is immediate
    # (identity -> permission -> domain_lock -> persist -> audit); the
    # protected decision is the separate incident.acknowledge action, which
    # binds a durable approval receipt to (record_id=incident_id,
    # target_version=version) - the same receipt architecture Task/
    # OperationalEvent already use, not a second creation-intent mechanism.
    incident_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    risk_class: RiskClass = RiskClass.R1
    summary: str
    description: str | None = None
    status: IncidentStatus = IncidentStatus.REPORTED
    owner_id: str | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)
    # INC-REV-F4: version >= 1, matching migration 005's CHECK exactly - a
    # canonical-model invariant, not just a database-side one, so a
    # constructed-in-Python Incident can never violate it either.
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HandoverStatus(StrEnum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


class HandoverItem(BaseModel):
    # Mirrors database/migrations/006_handovers.sql (handover_items). One
    # server-derived carry-over line from an open Task/CustomerRequest/
    # Incident on the source shift - never caller-supplied (P2A-HANDOVER-
    # VERTICAL, ADR section 3.2). `source_digest` is a canonical SHA-256 over
    # the server-derived source snapshot (SPEC R3); it is what review/
    # acknowledge/freeze revalidate to detect a stale handover.
    item_id: UUID = Field(default_factory=uuid4)
    handover_id: UUID
    source_record_type: str
    source_record_id: UUID
    source_digest: str
    summary: str
    owner_id: str | None = None
    due_at: datetime | None = None
    risk_class: RiskClass = RiskClass.R1
    evidence: list[EvidenceRef] = Field(default_factory=list)


class Handover(BaseModel):
    # Mirrors database/migrations/006_handovers.sql (handovers). Lifecycle is
    # DRAFT -> REVIEWED -> ACKNOWLEDGED (ACKNOWLEDGED terminal); review and
    # acknowledgement are separate authenticated actions and the acknowledging
    # receiver must differ from the reviewer (ADR section 3.1). `acknowledged`
    # is a computed field derived from `status` so it can never contradict it
    # while still satisfying the pre-existing public contract name (SPEC R1).
    handover_id: UUID = Field(default_factory=uuid4)
    from_shift_id: UUID
    to_shift_id: UUID
    status: HandoverStatus = HandoverStatus.DRAFT
    items: list[HandoverItem] = Field(default_factory=list)
    created_by: str
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    received_by: str | None = None
    acknowledged_at: datetime | None = None
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_shift_pair(self):
        if self.from_shift_id == self.to_shift_id:
            raise ValueError("from_shift_id and to_shift_id must differ")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def acknowledged(self) -> bool:
        return self.status == HandoverStatus.ACKNOWLEDGED


from .report_models import Report, ReportContent, ReportSection, ReportSourceRef, ReportStatus, ReportType  # noqa: E402,F401


class TaskCreationIntent(BaseModel):
    """A durable, approver-visible target for `task.create` approvals.

    `Task.create` has no pre-existing record to bind a receipt to (unlike
    event.confirm/event.correct, whose target already exists) - this intent is
    the durable stand-in, created before any approval, with a server-computed
    payload digest that `POST /tasks` later re-verifies bit-for-bit before
    consuming it (defeats TOCTOU/payload substitution). Immutable: exactly one
    version, `target_version` is always `1` when a receipt binds to it.
    """

    intent_id: UUID = Field(default_factory=uuid4)
    shift_id: UUID
    risk_class: str
    payload_snapshot: dict
    payload_digest: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
