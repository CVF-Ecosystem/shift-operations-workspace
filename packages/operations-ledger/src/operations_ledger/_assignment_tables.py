"""ShiftAssignment table builder (P2C-MUTATION-FULL-UI-C3A1).

Split out of ``tables.py`` (same split-module pattern as
``_incident_tables.py``/``_handover_tables.py``) purely to keep that host
module a thin wiring surface under the hard 300-line file-size guard. Never
imports ``tables.py`` itself (circular); the caller passes in the shared
``metadata`` and ``shifts``/``users`` tables it already owns.

The partial unique index (at most one ACTIVE assignment per (shift_id,
user_id)) mirrors ``tables.py``'s ``reports_current_unique`` pattern via
SQLAlchemy's ``postgresql_where``/``sqlite_where`` Index kwargs so both
backends enforce the SAME invariant, not just PostgreSQL.
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Table,
    Text,
    Uuid,
    func,
)


def build_shift_assignments_table(metadata, shifts, users) -> Table:
    """Mirrors database/migrations/008_shift_assignments.sql exactly."""
    table = Table(
        "shift_assignments",
        metadata,
        Column("assignment_id", Uuid, primary_key=True),
        Column("shift_id", Uuid, ForeignKey(shifts.c.shift_id), nullable=False),
        Column("user_id", Text, ForeignKey(users.c.user_id), nullable=False),
        Column("status", Text, nullable=False, server_default="ACTIVE"),
        Column("assigned_by", Text, ForeignKey(users.c.user_id), nullable=False),
        Column("assigned_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("revoked_by", Text, ForeignKey(users.c.user_id)),
        Column("revoked_at", DateTime(timezone=True)),
        Column("version", Integer, nullable=False, server_default="1"),
        CheckConstraint("status IN ('ACTIVE','REVOKED')", name="shift_assignments_status_check"),
        CheckConstraint("version >= 1", name="shift_assignments_version_check"),
    )
    Index(
        "shift_assignments_active_unique",
        table.c.shift_id,
        table.c.user_id,
        unique=True,
        postgresql_where=(table.c.status == "ACTIVE"),
        sqlite_where=(table.c.status == "ACTIVE"),
    )
    return table
