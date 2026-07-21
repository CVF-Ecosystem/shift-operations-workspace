"""SQLAlchemy Core table definitions mirroring database/migrations/001_foundation.sql.

Core (not ORM) keeps the ledger a thin, explicit mapping over the SQL schema
that already exists, so the migration remains the single schema authority.
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

shifts = Table(
    "shifts",
    metadata,
    Column("shift_id", UUID(as_uuid=True), primary_key=True),
    Column("name", Text, nullable=False),
    Column("starts_at", DateTime(timezone=True), nullable=False),
    Column("ends_at", DateTime(timezone=True), nullable=False),
    Column("status", String, nullable=False, server_default="OPEN"),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

operational_events = Table(
    "operational_events",
    metadata,
    Column("event_id", UUID(as_uuid=True), primary_key=True),
    Column("shift_id", UUID(as_uuid=True), nullable=False),
    Column("event_type", Text, nullable=False),
    Column("title", Text, nullable=False),
    Column("description", Text),
    Column("risk", String, nullable=False, server_default="R1"),
    Column("state", String, nullable=False, server_default="PROPOSED"),
    Column("starts_at", DateTime(timezone=True)),
    Column("ends_at", DateTime(timezone=True)),
    Column("owner_id", Text),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

corrections = Table(
    "corrections",
    metadata,
    Column("correction_id", UUID(as_uuid=True), primary_key=True),
    Column("record_type", Text, nullable=False),
    Column("record_id", UUID(as_uuid=True), nullable=False),
    Column("previous_version", Integer, nullable=False),
    Column("new_version", Integer, nullable=False),
    Column("reason", Text, nullable=False),
    Column("requested_by", Text, nullable=False),
    Column("before_data", JSONB, nullable=False),
    Column("after_data", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    CheckConstraint("new_version > previous_version", name="corrections_version_check"),
)

audit_records = Table(
    "audit_records",
    metadata,
    Column("audit_id", UUID(as_uuid=True), primary_key=True),
    Column("actor_id", Text),
    Column("action", Text, nullable=False),
    Column("target_type", Text, nullable=False),
    Column("target_id", Text, nullable=False),
    Column("metadata", JSONB, nullable=False, server_default="{}"),
    Column("occurred_at", DateTime(timezone=True), server_default=func.now()),
)
