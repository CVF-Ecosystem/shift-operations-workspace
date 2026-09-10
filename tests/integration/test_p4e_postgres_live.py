"""Opt-in live PostgreSQL P4-E suite (SPEC AC-05/AC-06/AC-07). Same opt-in
contract as test_assignment_postgres_live.py: every test below requires
LIVE_POSTGRES_DATABASE_URL, set only after applying
database/migrations/001-011 against a disposable container; without it
they skip. Never calls metadata.create_all() and never falls back to
SQLite - the migration is the schema authority (SPEC R10).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect as sa_inspect, insert, text

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger import tables as t
from workspace_api.domain import models as domain_models

from identity_mapping.models import IdentityMappingV1, SenderObservationV1

_DIGEST64 = "a" * 64
LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


@pytest.fixture(scope="module")
def live_database_url() -> str:
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite (SPEC R10)")
    return url


@pytest.fixture()
def sql_ledger(live_database_url) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _reconnected(live_database_url: str) -> SqlLedger:
    return SqlLedger(live_database_url, models=domain_models, engine=make_engine(live_database_url))


def _user(ledger, user_id, role="operator"):
    ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))


def _observation(observation_id, key_digest=_DIGEST64):
    now = datetime.now(timezone.utc)
    return SenderObservationV1(
        observation_id=observation_id, external_key_digest=key_digest, workspace_digest=_DIGEST64,
        endpoint_id="ep1", channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        raw_envelope_id=f"env-{observation_id}", external_message_id=f"msg-{observation_id}", received_at=now,
    )


def test_live_p4e_tables_present(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    names = set(inspector.get_table_names())
    for expected in ("external_identity_observations", "identity_mappings", "route_bindings",
                      "p4e_proposals", "p4e_placement_work", "p4e_placement_decisions", "p4e_action_receipts"):
        assert expected in names, expected


def test_live_identity_mappings_column_parity(sql_ledger):
    inspector = sa_inspect(sql_ledger.engine)
    live_cols = {c["name"] for c in inspector.get_columns("identity_mappings")}
    code_cols = {c.name for c in t.identity_mappings.columns}
    assert live_cols == code_cols


def test_live_mapping_round_trip_survives_reconnect(sql_ledger, live_database_url):
    user_id = f"pg-live-p4e-{uuid4().hex[:8]}"
    sup_id = f"pg-live-p4e-sup-{uuid4().hex[:8]}"
    _user(sql_ledger, user_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    observation_id = f"obs-{uuid4().hex[:8]}"
    key_digest = uuid4().hex + uuid4().hex[:32]
    sql_ledger.add_observation(_observation(observation_id, key_digest))
    now = datetime.now(timezone.utc)
    mapping_id = f"m-{uuid4().hex[:8]}"
    sql_ledger.propose_mapping(IdentityMappingV1(
        mapping_id=mapping_id, external_key_digest=key_digest, target_user_id=user_id,
        proposal_evidence_digest=_DIGEST64, proposer_id=sup_id, status="PROPOSED",
        version=1, created_at=now, updated_at=now,
    ))
    sql_ledger.confirm_mapping(mapping_id, expected_version=1, confirmer_id=sup_id)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_mapping(mapping_id)
    assert got.status == "CONFIRMED"
    assert got.version == 2


def test_live_duplicate_current_mapping_rejected_by_partial_unique_index(sql_ledger):
    """SPEC R6: the partial unique index (not just application logic)
    enforces at most one current confirmed mapping per key on real
    PostgreSQL."""
    key_digest = uuid4().hex + uuid4().hex[:32]
    with pytest.raises(Exception):
        with sql_ledger.engine.begin() as conn:
            conn.execute(insert(t.identity_mappings).values(
                mapping_id=f"dup-a-{uuid4().hex[:8]}", external_key_digest=key_digest,
                target_kind="INTERNAL_USER", target_user_id="ghost", proposal_evidence_digest=_DIGEST64,
                proposer_id="ghost", status="CONFIRMED", version=1, is_current=True,
            ))
            conn.execute(insert(t.identity_mappings).values(
                mapping_id=f"dup-b-{uuid4().hex[:8]}", external_key_digest=key_digest,
                target_kind="INTERNAL_USER", target_user_id="ghost", proposal_evidence_digest=_DIGEST64,
                proposer_id="ghost", status="CONFIRMED", version=1, is_current=True,
            ))
    with sql_ledger.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_live_transaction_rollback_removes_all_writes(sql_ledger, live_database_url):
    observation_id = f"obs-rb-{uuid4().hex[:8]}"
    key_digest = uuid4().hex + uuid4().hex[:32]

    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with sql_ledger.transaction() as unit:
            sql_ledger.add_observation(_observation(observation_id, key_digest), unit=unit)
            raise _Boom("simulated failure")

    fresh = _reconnected(live_database_url)
    with pytest.raises(KeyError):
        fresh.get_observation(observation_id)


def test_live_privacy_delete_clears_target_user_id_to_null_and_survives_reconnect(sql_ledger, live_database_url):
    """completion-rereview R4/F8: on REAL PostgreSQL, target_user_id is a
    genuine foreign key to users.user_id - privacy deletion must write
    NULL (not the prior 'PRIVACY_DELETED' sentinel, which the FK itself
    would reject) and that NULL must survive a fresh connection."""
    user_id = f"pg-live-privacy-{uuid4().hex[:8]}"
    sup_id = f"pg-live-privacy-sup-{uuid4().hex[:8]}"
    _user(sql_ledger, user_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    observation_id = f"obs-priv-{uuid4().hex[:8]}"
    key_digest = uuid4().hex + uuid4().hex[:32]
    sql_ledger.add_observation(_observation(observation_id, key_digest))
    now = datetime.now(timezone.utc)
    mapping_id = f"m-priv-{uuid4().hex[:8]}"
    sql_ledger.propose_mapping(IdentityMappingV1(
        mapping_id=mapping_id, external_key_digest=key_digest, target_user_id=user_id,
        proposal_evidence_digest=_DIGEST64, proposer_id=sup_id, status="PROPOSED",
        version=1, created_at=now, updated_at=now,
    ))
    sql_ledger.confirm_mapping(mapping_id, expected_version=1, confirmer_id=sup_id)
    sql_ledger.privacy_delete_mapping(mapping_id, expected_version=2)
    sql_ledger.engine.dispose()

    fresh = _reconnected(live_database_url)
    got = fresh.get_mapping(mapping_id)
    assert got.status == "REVOKED"
    assert got.target_user_id is None


def test_live_bind_and_replace_persist_a_real_audit_row_atomically(sql_ledger, live_database_url):
    """completion-rereview R2/R4: on REAL PostgreSQL, bind and replace must
    each leave exactly one durable audit row - not a manufactured
    audit_id with nothing behind it."""
    from cvf_runtime.identity import Principal
    from workspace_api.application.p4e_placement import P4ePlacementCommandService

    user_id = f"pg-live-bind-{uuid4().hex[:8]}"
    sup_id = f"pg-live-bind-sup-{uuid4().hex[:8]}"
    _user(sql_ledger, user_id)
    _user(sql_ledger, sup_id, "shift_supervisor")

    observation_id = f"obs-bind-{uuid4().hex[:8]}"
    key_digest = uuid4().hex + uuid4().hex[:32]
    sql_ledger.add_observation(_observation(observation_id, key_digest))
    now = datetime.now(timezone.utc)
    mapping_id = f"m-bind-{uuid4().hex[:8]}"
    sql_ledger.propose_mapping(IdentityMappingV1(
        mapping_id=mapping_id, external_key_digest=key_digest, target_user_id=user_id,
        proposal_evidence_digest=_DIGEST64, proposer_id=sup_id, status="PROPOSED",
        version=1, created_at=now, updated_at=now,
    ))
    sql_ledger.confirm_mapping(mapping_id, expected_version=1, confirmer_id=sup_id)

    service = P4ePlacementCommandService(sql_ledger, _DIGEST64)
    bind_receipt = service.bind(
        Principal(user_id=sup_id, role="shift_supervisor"), mapping_id=mapping_id,
        expected_mapping_version=2, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key=f"idem-bind-{uuid4().hex[:8]}",
    )
    assert bind_receipt.outcome == "APPLIED"
    entries = sql_ledger.audit_entries_for(bind_receipt.aggregate_id)
    assert len(entries) == 1
    assert entries[0]["action"] == "BIND"

    replace_receipt = service.replace_binding(
        Principal(user_id=sup_id, role="shift_supervisor"), old_binding_id=bind_receipt.aggregate_id,
        expected_binding_version=1, target_kind="WORKSPACE", target_id=_DIGEST64,
        idempotency_key=f"idem-replace-{uuid4().hex[:8]}",
    )
    assert replace_receipt.outcome == "APPLIED"
    replace_entries = sql_ledger.audit_entries_for(replace_receipt.aggregate_id)
    assert len(replace_entries) == 1
    assert replace_entries[0]["action"] == "REPLACE_BINDING"
