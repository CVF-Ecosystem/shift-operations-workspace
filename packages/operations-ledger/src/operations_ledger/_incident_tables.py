"""Incident Table builder (fifth vertical, P2-A).

Split out of ``tables.py`` (SPEC R11 / ADR section 2.4) purely to keep that
host module a thin wiring surface under the hard 300-line file-size guard -
not a behavior change to any other table. This module never imports
``tables.py`` itself (that would be circular, since ``tables.py`` calls
:func:`build_incidents_table` to obtain the ``incidents`` Table object);
instead the caller passes in the shared ``metadata``, the ``shifts`` table
(for the FK) and the native risk-class column type, exactly the objects
``tables.py`` already owns.
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    Text,
    Uuid,
    func,
)


def build_incidents_table(metadata, shifts, risk_class_type) -> Table:
    """Mirrors database/migrations/005_incidents.sql exactly."""
    return Table(
        "incidents",
        metadata,
        Column("incident_id", Uuid, primary_key=True),
        Column("shift_id", Uuid, ForeignKey(shifts.c.shift_id), nullable=False),
        Column("risk", risk_class_type, nullable=False, server_default="R1"),
        Column("summary", Text, nullable=False),
        Column("description", Text),
        Column("status", Text, nullable=False, server_default="REPORTED"),
        Column("owner_id", Text),
        Column("version", Integer, nullable=False, server_default="1"),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        CheckConstraint(
            "status IN ('REPORTED','ACKNOWLEDGED','MITIGATING','RESOLVED','CLOSED')",
            name="incidents_status_check",
        ),
        # INC-REV-F4: mirrors migration 005's `CHECK (version >= 1)` exactly.
        CheckConstraint("version >= 1", name="incidents_version_check"),
    )
