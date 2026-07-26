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

P1-POSTGRESQL-LIVE-ROUNDTRIP Amendment 1 (PG-REV-F1): the three migration
``CREATE TYPE ... AS ENUM`` types (``data_state``, ``risk_class``,
``shift_status``) are now mapped with the same ``with_variant`` pattern as
``JSON_TYPE`` - portable ``String`` on SQLite, native ``postgresql.ENUM`` on
PostgreSQL. A live round-trip against real PostgreSQL 16 previously failed
with ``psycopg.errors.DatatypeMismatch`` because a bare ``String`` column
binds an explicit ``::VARCHAR`` cast that PostgreSQL refuses to implicitly
convert to a native enum type. ``create_type=False`` on every variant is
mandatory: the migrations already ran ``CREATE TYPE``, so SQLAlchemy must
never attempt to create (or drop) the type itself.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
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
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM as PostgresEnum
from sqlalchemy.dialects.postgresql import JSONB

from operations_ledger._incident_tables import build_incidents_table

metadata = MetaData()

# Generic JSON column: native JSONB on PostgreSQL, JSON text elsewhere (SQLite).
JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")


def _enum_type(pg_name: str, *values: str):
    """Portable ``String`` (SQLite) with a native PostgreSQL ``ENUM`` variant
    bound to the exact migration-owned type name. ``create_type=False``: the
    migration's ``CREATE TYPE`` already created it; SQLAlchemy must never
    attempt to (re)create or drop it."""
    return String().with_variant(
        PostgresEnum(*values, name=pg_name, create_type=False), "postgresql"
    )


# Exact name/value parity with database/migrations/001_foundation.sql and
# operations_domain.models.{DataState,RiskClass,ShiftStatus}. Any drift here
# must fail the static and live enum-parity tests, not silently diverge.
DATA_STATE_ENUM_NAME = "data_state"
DATA_STATE_VALUES = ("RAW", "NORMALIZED", "PROPOSED", "CONFIRMED", "REJECTED", "CORRECTED", "FROZEN")
RISK_CLASS_ENUM_NAME = "risk_class"
RISK_CLASS_VALUES = ("R0", "R1", "R2", "R3", "R4")
SHIFT_STATUS_ENUM_NAME = "shift_status"
SHIFT_STATUS_VALUES = ("OPEN", "HANDOVER_PENDING", "CLOSED", "FROZEN")

DATA_STATE_TYPE = _enum_type(DATA_STATE_ENUM_NAME, *DATA_STATE_VALUES)
RISK_CLASS_TYPE = _enum_type(RISK_CLASS_ENUM_NAME, *RISK_CLASS_VALUES)
SHIFT_STATUS_TYPE = _enum_type(SHIFT_STATUS_ENUM_NAME, *SHIFT_STATUS_VALUES)

shifts = Table(
    "shifts",
    metadata,
    Column("shift_id", Uuid, primary_key=True),
    Column("name", Text, nullable=False),
    Column("starts_at", DateTime(timezone=True), nullable=False),
    Column("ends_at", DateTime(timezone=True), nullable=False),
    Column("status", SHIFT_STATUS_TYPE, nullable=False, server_default="OPEN"),
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
    Column("risk", RISK_CLASS_TYPE, nullable=False, server_default="R1"),
    Column("state", DATA_STATE_TYPE, nullable=False, server_default="PROPOSED"),
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
    Column("state", DATA_STATE_TYPE, nullable=False, server_default="RAW"),
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
    Column("risk", RISK_CLASS_TYPE, nullable=False, server_default="R1"),
    Column("state", DATA_STATE_TYPE, nullable=False, server_default="CONFIRMED"),
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

# Mirrors migration 003_users.sql (P2-B: real authentication). user_id is a
# free-form text PRIMARY KEY (not uuid), reusing the same dev/test ids the
# now-retired known-principals.yaml registry used to list (e.g. "op1",
# "sup1") purely for fixture legibility. Since
# P2B-APPROVER-IDENTITY-RECONCILIATION, this table is the single runtime
# authority for approver identity/role/active-status (see approval_receipts
# below) - known-principals.yaml no longer exists.
users = Table(
    "users",
    metadata,
    Column("user_id", Text, primary_key=True),
    Column("username", Text, nullable=False, unique=True),
    Column("password_hash", Text, nullable=False),
    Column("role", Text, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "role IN ('operator','shift_supervisor','responsible_manager','authorized_executive','viewer')",
        name="users_role_check",
    ),
)

# Mirrors migration 004_approval_receipts.sql (P2B-APPROVER-IDENTITY-RECONCILIATION).
# The durable, approver-visible target `task.create` receipts bind to before
# any Task exists - see ApprovalReceipt/TaskCreationIntent in
# operations_domain.models and ADR section 4.4.
task_creation_intents = Table(
    "task_creation_intents",
    metadata,
    Column("intent_id", Uuid, primary_key=True),
    Column("shift_id", Uuid, ForeignKey("shifts.shift_id"), nullable=False),
    Column("risk_class", RISK_CLASS_TYPE, nullable=False),
    Column("payload_snapshot", JSON_TYPE, nullable=False),
    Column("payload_digest", Text, nullable=False),
    Column("created_by", Text, ForeignKey("users.user_id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

# Mirrors migration 004_approval_receipts.sql. `payload_digest` is nullable:
# NULL for event actions (event.confirm/event.correct), set only for
# task.create (bound to a task_creation_intents row). The unique constraint
# makes one approver's receipt for one target scope idempotent (SPEC R2.4)
# and blocks double-counting one approver into two seats.
approval_receipts = Table(
    "approval_receipts",
    metadata,
    Column("receipt_id", Uuid, primary_key=True),
    Column("record_type", Text, nullable=False),
    Column("record_id", Uuid, nullable=False),
    Column("action", Text, nullable=False),
    Column("target_version", Integer, nullable=False),
    Column("risk_class", RISK_CLASS_TYPE, nullable=False),
    Column("payload_digest", Text),
    Column("approver_id", Text, ForeignKey("users.user_id"), nullable=False),
    Column("approver_role", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint(
        "record_type", "record_id", "action", "target_version", "approver_id",
        name="approval_receipts_scope_approver_unique",
    ),
)

# Mirrors migration 005_incidents.sql (fifth vertical, P2-A). Table builder
# lives in _incident_tables.py (SPEC R11): this host module only wires the
# shared metadata/shifts/RISK_CLASS_TYPE objects it already owns into it.
incidents = build_incidents_table(metadata, shifts, RISK_CLASS_TYPE)
