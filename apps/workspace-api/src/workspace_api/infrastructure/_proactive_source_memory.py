"""Count-first scoped source reads over the native in-memory ledger lock."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from operations_ledger._proactive_source_types import CandidateKey, CohortKey, FreshCohort
from operations_ledger._proactive_source_types import SourceReadFailure


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise SourceReadFailure("TIME_AMBIGUOUS")
    return value


def _cohort(ledger, user_id: str, start: datetime, end: datetime) -> tuple[CohortKey, ...]:
    active = {a.shift_id: a for a in ledger.assignments.values()
              if a.user_id == user_id and str(a.status) == "ACTIVE"}
    rows = (
        CohortKey(s.shift_id, s.ends_at, active[s.shift_id].assignment_id,
                  active[s.shift_id].version)
        for s in ledger.shifts.values()
        if s.shift_id in active and start <= _aware(s.ends_at) < end
    )
    return tuple(sorted(rows, key=lambda x: str(x.shift_id))[:501])


class MemorySourceUnit:
    def __init__(self, ledger, user_id: str, start: datetime, end: datetime, as_of: datetime):
        self.ledger, self.user_id = ledger, user_id
        self.start, self.end, self.as_of = start, end, as_of

    def cohort(self) -> tuple[CohortKey, ...]:
        return _cohort(self.ledger, self.user_id, self.start, self.end)

    def candidates(self, shift_ids: tuple[UUID, ...]) -> tuple[CandidateKey, ...]:
        wanted = set(shift_ids)
        rows = (
            CandidateKey(r.shift_id, r.report_id, r.version, r.generated_from_cutoff,
                         r.created_at, r.content.snapshot_digest)
            for r in self.ledger.reports.values()
            if r.shift_id in wanted and str(r.report_type) == "END_SHIFT"
            and _aware(r.created_at) <= self.as_of
        )
        return tuple(sorted(rows, key=lambda x: (str(x.shift_id), x.version, str(x.report_id)))[:501])

    def incident_ref_counts(self, report_ids: tuple[UUID, ...]) -> dict[UUID, tuple[int, int]]:
        return {
            rid: (
                sum(ref.record_type == "Incident" for ref in self.ledger.reports[rid].content.source_manifest),
                sum(len(section.records) for section in self.ledger.reports[rid].content.sections
                    if section.section_type == "incidents"),
            )
            for rid in report_ids
        }

    def load_reports(self, report_ids: tuple[UUID, ...]) -> tuple:
        return tuple(self.ledger.reports[rid].model_copy(deep=True) for rid in report_ids)


@contextmanager
def scoped_source_read(ledger, user_id: str, start: datetime, end: datetime, as_of: datetime):
    with ledger._lock:
        yield MemorySourceUnit(ledger, user_id, start, end, as_of)


def fresh_scoped_cohort(ledger, user_id: str, start: datetime, end: datetime,
                        prior_shift_ids: tuple[UUID, ...]) -> FreshCohort:
    with ledger._lock:
        active = frozenset(a.shift_id for a in ledger.assignments.values()
                           if a.user_id == user_id and str(a.status) == "ACTIVE"
                           and a.shift_id in prior_shift_ids)
        return FreshCohort(_cohort(ledger, user_id, start, end), active)
