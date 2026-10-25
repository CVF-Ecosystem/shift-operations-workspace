"""Internal bounded source-read metadata shared by native ledger backends."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


class SourceReadFailure(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class CohortKey:
    shift_id: UUID
    ends_at: datetime
    assignment_id: UUID
    assignment_version: int


@dataclass(frozen=True)
class CandidateKey:
    shift_id: UUID
    report_id: UUID
    version: int
    cutoff: datetime
    created_at: datetime
    snapshot_digest: str


@dataclass(frozen=True)
class FreshCohort:
    cohort: tuple[CohortKey, ...]
    prior_active: frozenset[UUID]


class ScopedSourceUnit(Protocol):
    def cohort(self) -> tuple[CohortKey, ...]: ...
    def candidates(self, shift_ids: tuple[UUID, ...]) -> tuple[CandidateKey, ...]: ...
    def incident_ref_counts(self, report_ids: tuple[UUID, ...]) -> dict[UUID, tuple[int, int]]: ...
    def load_reports(self, report_ids: tuple[UUID, ...]) -> tuple[Any, ...]: ...
