from __future__ import annotations

from datetime import datetime

from pydantic import Field, field_validator, model_validator

from operations_domain.models import Shift

from .common import SafeId, SafeIdentifierModel, utc_datetime


class ProjectKnowledgeSourceV1(SafeIdentifierModel):
    source_id: SafeId
    source_pin: SafeId
    current_source_pin: SafeId
    source_owner_id: SafeId


class ScopeInputV1(SafeIdentifierModel):
    shift_ids: tuple[SafeId, ...] = Field(max_length=2)
    parent_shifts: tuple[Shift, ...] = Field(max_length=2)
    effective_from_utc: datetime | None = None
    effective_to_utc: datetime | None = None

    @field_validator("effective_from_utc", "effective_to_utc")
    @classmethod
    def utc_only(cls, value: datetime | None) -> datetime | None:
        return None if value is None else utc_datetime(value)

    @model_validator(mode="after")
    def sorted_unique(self) -> "ScopeInputV1":
        if tuple(sorted(self.shift_ids)) != self.shift_ids:
            raise ValueError("shift_ids must be sorted")
        if len(set(self.shift_ids)) != len(self.shift_ids):
            raise ValueError("shift_ids must be unique")
        parent_ids = tuple(sorted(str(item.shift_id) for item in self.parent_shifts))
        if parent_ids != self.shift_ids or len(parent_ids) != len(set(parent_ids)):
            raise ValueError("parent shifts must match shift_ids")
        if (
            self.effective_from_utc is not None
            and self.effective_to_utc is not None
            and self.effective_from_utc > self.effective_to_utc
        ):
            raise ValueError("effective window inverted")
        return self
