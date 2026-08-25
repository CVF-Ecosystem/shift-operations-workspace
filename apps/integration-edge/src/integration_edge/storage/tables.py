from sqlalchemy import JSON, CheckConstraint, Column, DateTime, Integer, LargeBinary, MetaData, String, Table, UniqueConstraint

metadata = MetaData()

raw_envelopes = Table(
    "edge_raw_envelopes", metadata,
    Column("envelope_id", String, primary_key=True), Column("channel", String, nullable=False),
    Column("endpoint", String, nullable=False), Column("external_id", String, nullable=False),
    Column("payload_digest", String(64), nullable=False), Column("key_id", String, nullable=False),
    Column("nonce", LargeBinary(12), nullable=False), Column("ciphertext", LargeBinary),
    Column("tag", LargeBinary(16)), Column("aad", LargeBinary, nullable=False),
    Column("tombstoned_at", DateTime(timezone=True)),
    UniqueConstraint("key_id", "nonce", name="uq_edge_raw_key_nonce"),
    CheckConstraint("length(payload_digest) = 64", name="ck_edge_raw_digest"),
)
reservations = Table(
    "edge_ingress_reservations", metadata,
    Column("channel", String, primary_key=True), Column("external_id", String, primary_key=True),
    Column("payload_digest", String(64), nullable=False), Column("envelope_id", String, nullable=False),
)
quarantines = Table(
    "edge_quarantines", metadata, Column("quarantine_id", String, primary_key=True),
    Column("envelope_id", String, nullable=False), Column("original_envelope_id", String),
    Column("reason", String, nullable=False), Column("released_at", DateTime(timezone=True)),
)
proposals = Table(
    "edge_external_proposals", metadata, Column("proposal_id", String, primary_key=True),
    Column("envelope_id", String, nullable=False, unique=True), Column("channel", String, nullable=False),
    Column("external_id", String, nullable=False), Column("proposal_json", JSON, nullable=False),
    Column("trust_class", String, nullable=False), Column("content_class", String, nullable=False),
)
rate_counters = Table(
    "edge_rate_counters", metadata, Column("budget", String, primary_key=True),
    Column("counter_key", String, primary_key=True), Column("count", Integer, nullable=False),
)
outbound_attempts = Table(
    "edge_outbound_attempts", metadata, Column("command_id", String, primary_key=True),
    Column("prerequisite_digest", String(64), nullable=False), Column("outcome", String, nullable=False),
    Column("reason", String), Column("delivery_id", String),
    Column("delivery_attempts", Integer, nullable=False), Column("receipt_json", JSON, nullable=False),
)
