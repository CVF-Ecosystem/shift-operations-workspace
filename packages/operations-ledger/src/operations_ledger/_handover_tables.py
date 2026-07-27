"""Handover table builders (P2A-HANDOVER-VERTICAL).

Split out of ``tables.py`` (SPEC R13 / ADR section 3.8) purely to keep that
host module a thin wiring surface under the hard 300-line file-size guard -
not a behavior change to any other table. Mirrors
``database/migrations/006_handovers.sql`` exactly. Builds its own native
``handover_status`` enum column the same portable-String-with-PostgreSQL-
variant way ``tables.py``'s own ``_enum_type`` helper does (duplicated here,
not imported, exactly like ``_incident_tables.py`` takes ``risk_class_type``
as a parameter rather than importing ``tables.py`` - that import direction
would be circular, since ``tables.py`` calls this module to obtain the
``handovers``/``handover_items`` Table objects).
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM as PostgresEnum

HANDOVER_STATUS_ENUM_NAME = "handover_status"
HANDOVER_STATUS_VALUES = ("DRAFT", "REVIEWED", "ACKNOWLEDGED")


def _enum_type(pg_name: str, *values: str):
    return String().with_variant(
        PostgresEnum(*values, name=pg_name, create_type=False), "postgresql"
    )


def build_handover_tables(metadata: MetaData, shifts: Table, risk_class_type) -> tuple[Table, Table]:
    """Mirrors database/migrations/006_handovers.sql exactly."""
    handover_status_type = _enum_type(HANDOVER_STATUS_ENUM_NAME, *HANDOVER_STATUS_VALUES)

    handovers = Table(
        "handovers",
        metadata,
        Column("handover_id", Uuid, primary_key=True),
        Column("from_shift_id", Uuid, ForeignKey(shifts.c.shift_id), nullable=False),
        Column("to_shift_id", Uuid, ForeignKey(shifts.c.shift_id), nullable=False),
        Column("status", handover_status_type, nullable=False, server_default="DRAFT"),
        Column("created_by", Text, nullable=False),
        Column("reviewed_by", Text),
        Column("reviewed_at", DateTime(timezone=True)),
        Column("received_by", Text),
        Column("acknowledged_at", DateTime(timezone=True)),
        Column("version", Integer, nullable=False, server_default="1"),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        CheckConstraint("version >= 1", name="handovers_version_check"),
        CheckConstraint("from_shift_id <> to_shift_id", name="handovers_shift_pair_check"),
    )

    handover_items = Table(
        "handover_items",
        metadata,
        Column("item_id", Uuid, primary_key=True),
        Column("handover_id", Uuid, ForeignKey(handovers.c.handover_id), nullable=False),
        Column("source_record_type", Text, nullable=False),
        Column("source_record_id", Uuid, nullable=False),
        Column("source_digest", Text, nullable=False),
        Column("summary", Text, nullable=False),
        Column("owner_id", Text),
        Column("due_at", DateTime(timezone=True)),
        Column("risk", risk_class_type, nullable=False, server_default="R1"),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        CheckConstraint(
            "source_record_type IN ('Task','CustomerRequest','Incident')",
            name="handover_items_source_type_check",
        ),
        UniqueConstraint(
            "handover_id", "source_record_type", "source_record_id",
            name="handover_items_unique_source",
        ),
    )
    return handovers, handover_items
