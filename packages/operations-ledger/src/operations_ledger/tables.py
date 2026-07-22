"""SQLAlchemy Core table definitions mirroring database/migrations/001_foundation.sql.

Core (not ORM) keeps the ledger a thin, explicit mapping over the SQL schema
that already exists, so the migration remains the single schema authority.

Dual-backend by design: ``Uuid`` is SQLAlchemy's generic UUID type - it renders
as native ``uuid`` on PostgreSQL and as CHAR(32) on SQLite, so the same table
definition works against both without a hand-written branch. ``JSON_TYPE``
does the same for JSONB (native on PostgreSQL, plain JSON text elsewhere via
``with_variant``). This lets the workspace ship with a zero-setup SQLite
backend for evaluation/dev and switch to PostgreSQL for production by changing
only ``DATABASE_URL`` - no schema or code change.
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    MetaData,
    String,
    Table,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()

# Generic JSON column: native JSONB on PostgreSQL, JSON text elsewhere (SQLite).
JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")

shifts = Table(
    "shifts",
    metadata,
    Column("shift_id", Uuid, primary_key=True),
    Column("name", Text, nullable=False),
    Column("starts_at", DateTime(timezone=True), nullable=False),
    Column("ends_at", DateTime(timezone=True), nullable=False),
    Column("status", String, nullable=False, server_default="OPEN"),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Matches migration 001_foundation.sql: CHECK (ends_at > starts_at)
    CheckConstraint("ends_at > starts_at", name="shifts_window_check"),
)

operational_events = Table(
    "operational_events",
    metadata,
    Column("event_id", Uuid, primary_key=True),
    # Matches migration: shift_id uuid NOT NULL REFERENCES shifts(shift_id)
    Column("shift_id", Uuid, ForeignKey("shifts.shift_id"), nullable=False),
    Column("event_type", Text, nullable=False),
    Column("title", Text, nullable=False),
    Column("description", Text),
    Column("risk", String, nullable=False, server_default="R1"),
    Column("state", String, nullable=False, server_default="PROPOSED"),
    Column("starts_at", DateTime(timezone=True)),
    Column("ends_at", DateTime(timezone=True)),
    Column("owner_id", Text),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Matches migration: CHECK (ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at)
    CheckConstraint(
        "ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at",
        name="operational_events_window_check",
    ),
)

# Mirrors migration 001_foundation.sql (messages table). Minimal mapping: no
# add_message/get_message SqlLedger methods exist yet (add_message still
# raises NotImplementedError - message persistence is a separate vertical),
# but customer_requests.source_message_id REFERENCES messages(message_id), so
# this Table object must exist for that foreign key to resolve against this
# MetaData (SQLAlchemy raises NoReferencedTableError otherwise, which breaks
# every metadata.create_all(engine) call across the test suite).
messages = Table(
    "messages",
    metadata,
    Column("message_id", Uuid, primary_key=True),
    Column("shift_id", Uuid, ForeignKey("shifts.shift_id"), nullable=False),
    Column("source", Text, nullable=False),
    Column("sender_id", Text, nullable=False),
    Column("text_content", Text),
    Column("state", String, nullable=False, server_default="RAW"),
    Column("raw_payload", JSON_TYPE),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

corrections = Table(
    "corrections",
    metadata,
    Column("correction_id", Uuid, primary_key=True),
    Column("record_type", Text, nullable=False),
    Column("record_id", Uuid, nullable=False),
    Column("previous_version", Integer, nullable=False),
    Column("new_version", Integer, nullable=False),
    Column("reason", Text, nullable=False),
    Column("requested_by", Text, nullable=False),
    Column("before_data", JSON_TYPE, nullable=False),
    Column("after_data", JSON_TYPE, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("new_version > previous_version", name="corrections_version_check"),
)

evidence_links = Table(
    "evidence_links",
    metadata,
    Column("evidence_link_id", Uuid, primary_key=True),
    Column("record_type", Text, nullable=False),
    Column("record_id", Uuid, nullable=False),
    Column("source_type", Text, nullable=False),
    Column("source_id", Text, nullable=False),
    Column("sha256", Text),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

audit_records = Table(
    "audit_records",
    metadata,
    Column("audit_id", Uuid, primary_key=True),
    Column("actor_id", Text),
    Column("action", Text, nullable=False),
    Column("target_type", Text, nullable=False),
    Column("target_id", Text, nullable=False),
    Column("metadata", JSON_TYPE, nullable=False, server_default="{}"),
    Column("occurred_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

# Mirrors migration 002_tasks_customers_reports.sql (tasks table).
tasks = Table(
    "tasks",
    metadata,
    Column("task_id", Uuid, primary_key=True),
    Column("shift_id", Uuid, ForeignKey("shifts.shift_id"), nullable=False),
    Column("title", Text, nullable=False),
    Column("description", Text),
    Column("status", Text, nullable=False),
    Column("owner_id", Text),
    Column("due_at", DateTime(timezone=True)),
    Column("risk", String, nullable=False, server_default="R1"),
    Column("state", String, nullable=False, server_default="CONFIRMED"),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "status IN ('OPEN','IN_PROGRESS','BLOCKED','DONE','CARRY_OVER','CANCELLED')",
        name="tasks_status_check",
    ),
)

# Mirrors migration 002_tasks_customers_reports.sql (customer_requests table).
# Unlike tasks, shift_id here is NULLABLE (a customer request can exist
# without being tied to a specific shift) and there is no version/risk/state
# column - this table is intentionally simpler than tasks/operational_events.
customer_requests = Table(
    "customer_requests",
    metadata,
    Column("request_id", Uuid, primary_key=True),
    Column("customer_id", Text, nullable=False),
    Column("shift_id", Uuid, ForeignKey("shifts.shift_id"), nullable=True),
    Column("summary", Text, nullable=False),
    Column("details", Text),
    Column("status", Text, nullable=False),
    Column("source_message_id", Uuid, ForeignKey("messages.message_id"), nullable=True),
    Column("received_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("promised_at", DateTime(timezone=True)),
    Column("owner_id", Text),
    CheckConstraint(
        "status IN ('NEW','ACKNOWLEDGED','IN_PROGRESS','WAITING','RESOLVED','CLOSED')",
        name="customer_requests_status_check",
    ),
)
