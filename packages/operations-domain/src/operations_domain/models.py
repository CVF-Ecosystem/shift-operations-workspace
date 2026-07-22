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
`workspace_api.domain.models` until the known-principals.yaml <-> users
reconciliation tranche decides where it belongs.
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator

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
