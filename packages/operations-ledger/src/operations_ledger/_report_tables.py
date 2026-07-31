"""Report Table builder (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).

Split out of ``tables.py`` (SPEC R23/R24) purely to keep that host module a
thin wiring surface under the hard 300-line file-size guard - not a behavior
change to any other table. This module never imports ``tables.py`` itself
(that would be circular, since ``tables.py`` calls
:func:`build_reports_table` to obtain the ``reports`` Table object); instead
the caller passes in the shared ``metadata`` and ``shifts`` table it already
owns, exactly the pattern ``_incident_tables.py``/``_handover_tables.py`` use.

Mirrors ``database/migrations/002_tasks_customers_reports.sql`` plus
migration 007's added ``is_current`` column, CHECK, unique constraint and
partial unique index exactly.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)


def build_reports_table(metadata, shifts, json_type) -> Table:
    """Mirrors migration 002 (reports) plus migration 007's additions."""
    reports = Table(
        "reports",
        metadata,
        Column("report_id", Uuid, primary_key=True),
        Column("shift_id", Uuid, ForeignKey(shifts.c.shift_id), nullable=False),
        Column("report_type", Text, nullable=False),
        Column("version", Integer, nullable=False, server_default="1"),
        Column("status", Text, nullable=False),
        Column("content", json_type, nullable=False),
        Column("generated_from_cutoff", DateTime(timezone=True), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("is_current", Boolean, nullable=False, server_default="true"),
        CheckConstraint(
            "status IN ('DRAFT','IN_REVIEW','APPROVED','FROZEN')",
            name="reports_status_check",
        ),
        CheckConstraint("version >= 1", name="reports_version_check"),
        UniqueConstraint(
            "shift_id", "report_type", "version",
            name="reports_shift_type_version_unique",
        ),
    )
    # Partial unique index: at most one current row per (shift_id,
    # report_type) - the real database-side guarantee backing SPEC R20's
    # "reject zero/multiple current candidates" freeze check. Both SQLite and
    # PostgreSQL support a partial index via `sqlite_where`/`postgresql_where`.
    Index(
        "reports_current_unique",
        reports.c.shift_id, reports.c.report_type,
        unique=True,
        postgresql_where=reports.c.is_current.is_(True),
        sqlite_where=reports.c.is_current.is_(True),
    )
    return reports
