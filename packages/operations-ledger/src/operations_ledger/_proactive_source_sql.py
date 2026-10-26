"""Single-unit PostgreSQL scoped metadata reads and independent fresh view."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from operations_ledger import _proactive_source_sql_content as content
from operations_ledger._proactive_source_types import (
    CandidateKey, CohortKey, FreshCohort, SourceReadFailure,
)
from operations_ledger.tables import reports, shift_assignments, shifts


def _cohort(conn, user_id: str, start: datetime, end: datetime) -> tuple[CohortKey, ...]:
    stmt = (
        select(shifts.c.shift_id, shifts.c.ends_at,
               shift_assignments.c.assignment_id, shift_assignments.c.version)
        .join(shift_assignments, shift_assignments.c.shift_id == shifts.c.shift_id)
        .where(shift_assignments.c.user_id == user_id,
               shift_assignments.c.status == "ACTIVE",
               shifts.c.ends_at >= start, shifts.c.ends_at < end)
        .order_by(shifts.c.shift_id).limit(501)
    )
    return tuple(CohortKey(*row) for row in conn.execute(stmt).all())


class SqlSourceUnit:
    def __init__(self, conn, models, user_id: str, start: datetime, end: datetime, as_of: datetime):
        self.conn, self.models, self.user_id = conn, models, user_id
        self.start, self.end, self.as_of = start, end, as_of

    def cohort(self) -> tuple[CohortKey, ...]:
        return _cohort(self.conn, self.user_id, self.start, self.end)

    def candidates(self, shift_ids: tuple[UUID, ...]) -> tuple[CandidateKey, ...]:
        if not shift_ids:
            return ()
        stmt = (
            select(reports.c.shift_id, reports.c.report_id, reports.c.version,
                   reports.c.generated_from_cutoff, reports.c.created_at,
                   reports.c.content["snapshot_digest"].as_string())
            .where(reports.c.shift_id.in_(shift_ids), reports.c.report_type == "END_SHIFT",
                   reports.c.created_at <= self.as_of)
            .order_by(reports.c.shift_id, reports.c.version, reports.c.report_id).limit(501)
        )
        return tuple(CandidateKey(*row) for row in self.conn.execute(stmt).all())

    def incident_ref_counts(self, report_ids: tuple[UUID, ...]) -> dict[UUID, tuple[int, int]]:
        return content.incident_ref_counts(self.conn, report_ids)

    def load_reports(self, report_ids: tuple[UUID, ...]) -> tuple:
        return content.load_reports(self.conn, self.models, report_ids)


def _sqlite_naive_diagnostic(ledger, user_id: str, start: datetime, end: datetime) -> None:
    with ledger.engine.connect() as conn:
        row = conn.execute(
            select(shifts.c.ends_at)
            .join(shift_assignments, shift_assignments.c.shift_id == shifts.c.shift_id)
            .where(shift_assignments.c.user_id == user_id,
                   shift_assignments.c.status == "ACTIVE",
                   shifts.c.ends_at >= start, shifts.c.ends_at < end)
            .limit(1)
        ).first()
    if row is not None and (row[0].tzinfo is None or row[0].utcoffset() is None):
        raise SourceReadFailure("TIME_AMBIGUOUS")
    raise SourceReadFailure("SNAPSHOT_UNAVAILABLE")


@contextmanager
def _read_only_rr(ledger, *, fresh: bool = False):
    try:
        conn = ledger.engine.connect()
    except Exception as exc:
        raise SourceReadFailure("SNAPSHOT_UNAVAILABLE" if fresh else "SOURCE_UNAVAILABLE") from exc
    with conn:
        try:
            conn = conn.execution_options(isolation_level="REPEATABLE READ")
            transaction = conn.begin()
            transaction.__enter__()
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
        except Exception as exc:
            if 'transaction' in locals():
                transaction.__exit__(type(exc), exc, exc.__traceback__)
            raise SourceReadFailure("SNAPSHOT_UNAVAILABLE") from exc
        try:
            yield conn
        except BaseException as exc:
            transaction.__exit__(type(exc), exc, exc.__traceback__)
            raise
        else:
            transaction.__exit__(None, None, None)


@contextmanager
def scoped_source_read(ledger, user_id: str, start: datetime, end: datetime, as_of: datetime):
    if ledger.engine.dialect.name == "sqlite":
        _sqlite_naive_diagnostic(ledger, user_id, start, end)
    if ledger.engine.dialect.name != "postgresql":
        raise SourceReadFailure("SNAPSHOT_UNAVAILABLE")
    with _read_only_rr(ledger) as conn:
        yield SqlSourceUnit(conn, ledger.models, user_id, start, end, as_of)


def fresh_scoped_cohort(ledger, user_id: str, start: datetime, end: datetime,
                        prior_shift_ids: tuple[UUID, ...]) -> FreshCohort:
    if ledger.engine.dialect.name != "postgresql":
        raise SourceReadFailure("SNAPSHOT_UNAVAILABLE")
    with _read_only_rr(ledger, fresh=True) as conn:
        cohort = _cohort(conn, user_id, start, end)
        active = frozenset(row[0] for row in conn.execute(
            select(shift_assignments.c.shift_id).where(
                shift_assignments.c.user_id == user_id,
                shift_assignments.c.status == "ACTIVE",
                shift_assignments.c.shift_id.in_(prior_shift_ids),
            )
        ).all())
        return FreshCohort(cohort, active)
