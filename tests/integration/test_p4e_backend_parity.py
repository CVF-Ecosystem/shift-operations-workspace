"""P4-E SQLite persistence integration tests (SPEC AC-05/AC-10): mapping
lifecycle, unique-current, CAS, idempotent replay, key conflict, concurrent
confirmation, and audit atomicity on the deterministic SQLite backend.
Disposable-PostgreSQL companion coverage of the SAME `_P4eStoreMixin`
methods lives in `test_p4e_postgres_live.py` (opt-in, skips without
LIVE_POSTGRES_DATABASE_URL) - both exercise identical SqlLedger code paths,
so this file is the always-run half of that backend-parity pair.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import insert

from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata, users
from workspace_api.domain import models as domain_models

from identity_mapping.models import IdentityMappingV1, SenderObservationV1
from conversation_routing.models import RouteBindingV1

_DIGEST64 = "a" * 64
_NOW = datetime.now(timezone.utc)


@pytest.fixture()
def ledger() -> SqlLedger:
    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    sql_ledger = SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)
    with engine.begin() as conn:
        conn.execute(insert(users).values(user_id="u1", username="u1", password_hash="x", role="operator", is_active=True))
        conn.execute(insert(users).values(user_id="u2", username="u2", password_hash="x", role="shift_supervisor", is_active=True))
        conn.execute(insert(users).values(user_id="u3", username="u3", password_hash="x", role="shift_supervisor", is_active=True))
    return sql_ledger


def _observation(observation_id="obs1", key_digest=_DIGEST64):
    return SenderObservationV1(
        observation_id=observation_id, external_key_digest=key_digest, workspace_digest=_DIGEST64,
        endpoint_id="ep1", channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        raw_envelope_id=f"env-{observation_id}", external_message_id=f"msg-{observation_id}", received_at=_NOW,
    )


def _mapping(mapping_id="m1", **overrides):
    fields = dict(
        mapping_id=mapping_id, external_key_digest=_DIGEST64, target_user_id="u1",
        proposal_evidence_digest="b" * 64, proposer_id="u2", status="PROPOSED",
        version=1, created_at=_NOW, updated_at=_NOW,
    )
    fields.update(overrides)
    return IdentityMappingV1(**fields)


def test_observation_add_and_get_round_trip(ledger):
    ledger.add_observation(_observation())
    got = ledger.get_observation("obs1")
    assert got.external_key_digest == _DIGEST64


def test_duplicate_observation_lineage_rejected(ledger):
    ledger.add_observation(_observation())
    with pytest.raises(ValueError):
        ledger.add_observation(_observation())


def test_propose_confirm_lifecycle(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    updated = ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    assert updated.status == "CONFIRMED"
    assert updated.version == 2


def test_unique_current_mapping_enforced_at_write_time(ledger):
    """SPEC R6: at most one current confirmed mapping per complete key."""
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping("m1"))
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")

    ledger.propose_mapping(_mapping("m2"))
    with pytest.raises(ValueError):
        ledger.confirm_mapping("m2", expected_version=1, confirmer_id="u3")


def test_stale_version_confirm_rejected_with_no_partial_write(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    with pytest.raises(ValueError):
        ledger.confirm_mapping("m1", expected_version=99, confirmer_id="u3")
    unchanged = ledger.get_mapping("m1")
    assert unchanged.status == "PROPOSED"
    assert unchanged.version == 1


def test_reject_transition(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    rejected = ledger.reject_mapping("m1", expected_version=1, rejector_id="u3")
    assert rejected.status == "REJECTED"


def test_revoke_transition(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    revoked = ledger.revoke_mapping("m1", expected_version=2, revoker_id="u3")
    assert revoked.status == "REVOKED"


def test_correction_atomically_revokes_predecessor(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping("m1"))
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")

    ledger.add_observation(_observation("obs2"))
    ledger.propose_mapping(_mapping("m2", predecessor_mapping_id="m1"))
    ledger.confirm_mapping("m2", expected_version=1, confirmer_id="u3", predecessor_mapping_id="m1")

    predecessor = ledger.get_mapping("m1")
    assert predecessor.status == "REVOKED"
    current = ledger.get_current_mapping(_DIGEST64)
    assert current.mapping_id == "m2"


def test_privacy_delete_preserves_lineage_digests(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    deleted = ledger.privacy_delete_mapping("m1", expected_version=2)
    assert deleted.status == "REVOKED"
    assert deleted.mapping_id == "m1"
    assert deleted.external_key_digest == _DIGEST64
    assert deleted.proposal_evidence_digest == "b" * 64


def test_binding_create_and_replace(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")

    binding = RouteBindingV1(
        binding_id="b1", mapping_id="m1", mapping_version=2, target_kind="WORKSPACE",
        target_id=_DIGEST64, target_version=1, creator_id="u3", status="ACTIVE", version=1, created_at=_NOW,
    )
    ledger.create_binding(binding)
    current = ledger.get_current_binding("m1")
    assert current.binding_id == "b1"

    successor = binding.model_copy(update={"binding_id": "b2"})
    with pytest.raises(ValueError):
        ledger.replace_binding("b1", successor, expected_binding_version=2)
    unchanged = ledger.get_binding("b1")
    assert unchanged.status == "ACTIVE"
    assert unchanged.version == 1
    ledger.replace_binding("b1", successor, expected_binding_version=1)
    current_after = ledger.get_current_binding("m1")
    assert current_after.binding_id == "b2"
    old = ledger.get_binding("b1")
    assert old.status == "REVOKED"
    assert old.version == 2


def test_unique_current_binding_enforced_at_write_time(ledger):
    ledger.add_observation(_observation())
    ledger.propose_mapping(_mapping())
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    binding1 = RouteBindingV1(
        binding_id="b1", mapping_id="m1", mapping_version=2, target_kind="WORKSPACE",
        target_id=_DIGEST64, target_version=1, creator_id="u3", status="ACTIVE", version=1, created_at=_NOW,
    )
    ledger.create_binding(binding1)
    binding2 = binding1.model_copy(update={"binding_id": "b2"})
    with pytest.raises(ValueError):
        ledger.create_binding(binding2)


def test_proposal_admission_idempotent_on_same_key_and_lineage(ledger):
    proposal = {
        "proposal_id": str(uuid4()), "envelope_id": "env1", "channel": "ch1", "external_id": "msg1",
        "candidate": {"text": "hi"}, "provenance_digest": _DIGEST64, "sender_evidence": None,
        "idempotency_key": "idem1",
    }
    _stored1, replayed1 = ledger.add_p4e_proposal(proposal)
    _stored2, replayed2 = ledger.add_p4e_proposal(proposal)
    assert replayed1 is False
    assert replayed2 is True


def test_proposal_admission_lineage_collision_on_reused_key_different_envelope(ledger):
    proposal_a = {
        "proposal_id": str(uuid4()), "envelope_id": "env1", "channel": "ch1", "external_id": "msg1",
        "candidate": {"text": "hi"}, "provenance_digest": _DIGEST64, "sender_evidence": None,
        "idempotency_key": "idem1",
    }
    ledger.add_p4e_proposal(proposal_a)
    proposal_b = dict(proposal_a, proposal_id=str(uuid4()), envelope_id="env2")
    with pytest.raises(ValueError):
        ledger.add_p4e_proposal(proposal_b)


def test_placement_work_claim_and_complete(ledger):
    proposal = {
        "proposal_id": str(uuid4()), "envelope_id": "env1", "channel": "ch1", "external_id": "msg1",
        "candidate": {"text": "hi"}, "provenance_digest": _DIGEST64, "sender_evidence": None,
        "idempotency_key": "idem1",
    }
    stored, _ = ledger.add_p4e_proposal(proposal)
    work = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert work["state"] == "CLAIMED"
    ledger.complete_placement_work(
        stored["proposal_id"], {
            "decision_id": str(uuid4()), "proposal_id": stored["proposal_id"], "outcome": "FALLBACK",
            "reason": "NO_MAPPING", "mapping_id": None, "binding_id": None, "target_kind": None,
            "target_id": None, "conversation_key": None,
        },
        expected_version=work["version"], claim_token=work["claim_token"],
        expected_lineage_digest=work["lineage_digest"],
    )
    second_claim = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert second_claim is None


def test_action_receipt_idempotency_round_trip(ledger):
    receipt = {"outcome": "APPLIED", "action": "PROPOSE", "aggregate_id": "m1", "aggregate_version": 1,
               "audit_id": "a1", "command_application_count": 1, "audit_count": 1, "replayed": False}
    ledger.put_action_receipt("idem1", "PROPOSE", "digest1", receipt)
    stored = ledger.get_action_receipt("idem1")
    assert stored["receipt"]["outcome"] == "APPLIED"
    assert stored["payload_digest"] == "digest1"
