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
