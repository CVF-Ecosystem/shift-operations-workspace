"""P4-E table builder (identity mapping, route binding, placement work).

Split out of ``tables.py`` (same 300-line file-size guard pattern as
``_incident_tables.py``/``_handover_tables.py``) - not a behavior change to
any other table. Mirrors ``database/migrations/011_p4e_identity_conversation_
routing.sql`` exactly, INCLUDING its foreign keys to ``users`` and
``identity_mappings`` (completion-review F8: SQLAlchemy and the migration
must agree). The caller passes in the shared ``metadata``, ``JSON_TYPE``,
and ``users`` table this module does not own.
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
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)


def build_p4e_tables(metadata, json_type, users) -> dict[str, Table]:
    external_identity_observations = Table(
        "external_identity_observations",
        metadata,
        Column("observation_id", Text, primary_key=True),
        Column("external_key_digest", String(64), nullable=False),
        Column("workspace_digest", String(64), nullable=False),
        Column("endpoint_id", Text, nullable=False),
        Column("channel_id", Text, nullable=False),
        Column("provider_account_digest", String(64), nullable=False),
        Column("subject_kind", Text, nullable=False),
        Column("extraction_policy_id", Text, nullable=False),
        Column("extraction_policy_version", Text, nullable=False),
        Column("raw_envelope_id", Text, nullable=False),
        Column("external_message_id", Text, nullable=False),
        Column("received_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        UniqueConstraint(
            "external_key_digest", "raw_envelope_id",
            name="external_identity_observations_key_envelope_unique",
        ),
    )

    identity_mappings = Table(
        "identity_mappings",
        metadata,
        Column("mapping_id", Text, primary_key=True),
        Column("external_key_digest", String(64), nullable=False),
        Column("target_kind", Text, nullable=False, server_default="INTERNAL_USER"),
        # completion-review F8: nullable - SPEC R19 privacy deletion sets
        # this to NULL (never a fake sentinel row a real FK would reject).
        Column("target_user_id", Text, ForeignKey(users.c.user_id), nullable=True),
        Column("proposal_evidence_digest", String(64), nullable=False),
        Column("proposer_id", Text, ForeignKey(users.c.user_id), nullable=False),
        Column("status", Text, nullable=False),
        Column("version", Integer, nullable=False, server_default="1"),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("confirmer_id", Text, ForeignKey(users.c.user_id)),
        Column("rejector_id", Text, ForeignKey(users.c.user_id)),
        Column("revoker_id", Text, ForeignKey(users.c.user_id)),
        Column("successor_mapping_id", Text),
        Column("predecessor_mapping_id", Text),
        Column("is_current", Boolean, nullable=False, server_default="0"),
        CheckConstraint(
            "status IN ('PROPOSED','CONFIRMED','REJECTED','REVOKED')",
            name="identity_mappings_status_check",
        ),
        CheckConstraint("version >= 1", name="identity_mappings_version_check"),
    )
    # SPEC R6: at most one current confirmed mapping per complete key,
    # enforced by both backends via the same partial-unique-index pattern
    # _assignment_tables.py already established (postgresql_where/
    # sqlite_where), not just a plain UniqueConstraint on the column alone.
    Index(
        "identity_mappings_current_unique", identity_mappings.c.external_key_digest,
        unique=True,
        postgresql_where=(identity_mappings.c.is_current == True),  # noqa: E712
        sqlite_where=(identity_mappings.c.is_current == True),  # noqa: E712
    )

    route_bindings = Table(
        "route_bindings",
        metadata,
        Column("binding_id", Text, primary_key=True),
        Column("mapping_id", Text, ForeignKey(identity_mappings.c.mapping_id), nullable=False),
        Column("mapping_version", Integer, nullable=False),
        Column("target_kind", Text, nullable=False),
        Column("target_id", Text, nullable=False),
        Column("target_version", Integer, nullable=False),
        Column("creator_id", Text, ForeignKey(users.c.user_id), nullable=False),
        Column("status", Text, nullable=False, server_default="ACTIVE"),
        Column("version", Integer, nullable=False, server_default="1"),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        Column("successor_binding_id", Text),
        Column("is_current", Boolean, nullable=False, server_default="1"),
        CheckConstraint("target_kind IN ('WORKSPACE','SHIFT','INCIDENT')", name="route_bindings_target_kind_check"),
        CheckConstraint("status IN ('ACTIVE','REVOKED')", name="route_bindings_status_check"),
        CheckConstraint("version >= 1", name="route_bindings_version_check"),
    )
    # SPEC R13: at most one current binding per confirmed mapping.
    Index(
        "route_bindings_current_unique", route_bindings.c.mapping_id,
        unique=True,
        postgresql_where=(route_bindings.c.is_current == True),  # noqa: E712
        sqlite_where=(route_bindings.c.is_current == True),  # noqa: E712
    )

    p4e_proposals = Table(
        "p4e_proposals",
        metadata,
        Column("proposal_id", Text, primary_key=True),
        Column("envelope_id", Text, nullable=False, unique=True),
        Column("channel", Text, nullable=False),
        Column("external_id", Text, nullable=False),
        Column("candidate", json_type, nullable=False),
        Column("provenance_digest", String(64), nullable=False),
        Column("sender_evidence", json_type),
        Column("idempotency_key", Text, nullable=False, unique=True),
        # SPEC R11/completion-review F3: the complete non-disclosing
        # semantic lineage digest, persisted so exact-replay-versus-
        # lineage-collision is a real stored-value comparison, not a
        # partial in-memory recomputation that only checks envelope_id.
        Column("lineage_digest", String(64), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    )

    p4e_placement_work = Table(
        "p4e_placement_work",
        metadata,
        Column("work_item_id", Text, primary_key=True),
        Column("proposal_id", Text, ForeignKey(p4e_proposals.c.proposal_id), nullable=False, unique=True),
        Column("state", Text, nullable=False, server_default="PENDING"),
        Column("attempt_count", Integer, nullable=False, server_default="0"),
        Column("claim_token", Text),
        Column("claimed_at", DateTime(timezone=True)),
        Column("version", Integer, nullable=False, server_default="1"),
        # SPEC R12/completion-review F6: the exact proposal-lineage digest
        # this work item was created against - completion CAS-compares it
        # against the proposal's CURRENT lineage digest, so a proposal
        # somehow mutated between admission and processing is caught as a
        # closed LINEAGE_DIGEST_MISMATCH rather than silently processed.
        Column("lineage_digest", String(64), nullable=False),
        CheckConstraint("state IN ('PENDING','CLAIMED','COMPLETE')", name="p4e_placement_work_state_check"),
    )

    p4e_placement_decisions = Table(
        "p4e_placement_decisions",
        metadata,
        Column("decision_id", Text, primary_key=True),
        Column("proposal_id", Text, ForeignKey(p4e_proposals.c.proposal_id), nullable=False, unique=True),
        Column("outcome", Text, nullable=False),
        Column("reason", Text),
        Column("mapping_id", Text),
        Column("binding_id", Text),
        Column("target_kind", Text),
        Column("target_id", Text),
        Column("conversation_key", String(64)),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
        CheckConstraint(
            "outcome IN ('PLACED','FALLBACK','REFUSED')",
            name="p4e_placement_decisions_outcome_check",
        ),
    )

    p4e_action_receipts = Table(
        "p4e_action_receipts",
        metadata,
        Column("idempotency_key", Text, primary_key=True),
        Column("action", Text, nullable=False),
        Column("payload_digest", String(64), nullable=False),
        Column("receipt", json_type, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    )

    return {
        "external_identity_observations": external_identity_observations,
        "identity_mappings": identity_mappings,
        "route_bindings": route_bindings,
        "p4e_proposals": p4e_proposals,
        "p4e_placement_work": p4e_placement_work,
        "p4e_placement_decisions": p4e_placement_decisions,
        "p4e_action_receipts": p4e_action_receipts,
    }
