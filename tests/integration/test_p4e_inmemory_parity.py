"""P4-E InMemory persistence integration tests (completion-review F8/AC-05:
InMemory/SQLite/PostgreSQL parity). Exercises the identical scenarios as
``test_p4e_backend_parity.py`` against ``InMemoryLedger``'s
``_InMemoryP4eRepositoryMixin`` instead of ``SqlLedger``, proving both
backends agree on CAS, uniqueness, lineage, exhaustion boundary, and
rollback semantics - not just that each independently passes its own
suite.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from workspace_api.infrastructure.repository import InMemoryLedger
from identity_mapping.models import IdentityMappingV1, SenderObservationV1
from conversation_routing.models import RouteBindingV1

_DIGEST64 = "a" * 64
_NOW = datetime.now(timezone.utc)


@pytest.fixture()
def ledger() -> InMemoryLedger:
    return InMemoryLedger()


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
    ledger.propose_mapping(_mapping())
    updated = ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    assert updated.status == "CONFIRMED"
    assert updated.version == 2


def test_unique_current_mapping_enforced_at_write_time(ledger):
    ledger.propose_mapping(_mapping("m1"))
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    ledger.propose_mapping(_mapping("m2"))
    with pytest.raises(ValueError):
        ledger.confirm_mapping("m2", expected_version=1, confirmer_id="u3")


def test_stale_version_confirm_rejected_with_no_partial_write(ledger):
    ledger.propose_mapping(_mapping())
    with pytest.raises(ValueError):
        ledger.confirm_mapping("m1", expected_version=99, confirmer_id="u3")
    unchanged = ledger.get_mapping("m1")
    assert unchanged.status == "PROPOSED"
    assert unchanged.version == 1


def test_privacy_delete_writes_null_not_sentinel_string(ledger):
    ledger.propose_mapping(_mapping())
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    deleted = ledger.privacy_delete_mapping("m1", expected_version=2)
    assert deleted.status == "REVOKED"
    assert deleted.target_user_id is None
    assert deleted.proposal_evidence_digest == "b" * 64


def test_binding_create_and_replace(ledger):
    ledger.propose_mapping(_mapping())
    ledger.confirm_mapping("m1", expected_version=1, confirmer_id="u3")
    binding = RouteBindingV1(
        binding_id="b1", mapping_id="m1", mapping_version=2, target_kind="WORKSPACE",
        target_id=_DIGEST64, target_version=1, creator_id="u3", status="ACTIVE", version=1, created_at=_NOW,
    )
    ledger.create_binding(binding)
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


def _proposal(**overrides):
    fields = dict(
        proposal_id=str(uuid4()), envelope_id="env1", channel="ch1", external_id="msg1",
        candidate={"text": "hi"}, provenance_digest=_DIGEST64, sender_evidence=None,
        idempotency_key="idem1",
    )
    fields.update(overrides)
    return fields


def test_proposal_admission_idempotent_on_same_key_and_lineage(ledger):
    proposal = _proposal()
    _stored1, replayed1 = ledger.add_p4e_proposal(proposal)
    _stored2, replayed2 = ledger.add_p4e_proposal(proposal)
    assert replayed1 is False
    assert replayed2 is True


def test_proposal_admission_lineage_collision_on_reused_key_different_envelope(ledger):
    proposal_a = _proposal()
    ledger.add_p4e_proposal(proposal_a)
    proposal_b = dict(proposal_a, proposal_id=str(uuid4()), envelope_id="env2")
    with pytest.raises(ValueError):
        ledger.add_p4e_proposal(proposal_b)


def test_placement_work_claim_and_complete(ledger):
    stored, _ = ledger.add_p4e_proposal(_proposal())
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


def test_claim_exhaustion_at_exact_three_attempt_boundary(ledger):
    """completion-review F6/F8: both backends must exhaust at exactly
    attempt_count == 3, never 4 (off-by-one) and never silently reclaim."""
    stored, _ = ledger.add_p4e_proposal(_proposal(idempotency_key="idem-exhaust", envelope_id="env-exhaust"))
    for _ in range(3):
        claimed = ledger.claim_placement_work(
            stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
        )
        assert claimed["state"] == "CLAIMED"
        ledger.rollback_placement_work(
            stored["proposal_id"], expected_version=claimed["version"], claim_token=claimed["claim_token"],
            expected_lineage_digest=claimed["lineage_digest"],
        )
    exhausted = ledger.claim_placement_work(
        stored["proposal_id"], expected_lineage_digest=stored["lineage_digest"],
    )
    assert exhausted["_terminal_reason"] == "EXHAUSTED"


def test_action_receipt_idempotency_round_trip(ledger):
    receipt = {"outcome": "APPLIED", "action": "PROPOSE", "aggregate_id": "m1", "aggregate_version": 1,
               "audit_id": "a1", "command_application_count": 1, "audit_count": 1, "replayed": False}
    ledger.put_action_receipt("idem1", "PROPOSE", "digest1", receipt)
    stored = ledger.get_action_receipt("idem1")
    assert stored["receipt"]["outcome"] == "APPLIED"
    assert stored["payload_digest"] == "digest1"


def test_transaction_rollback_removes_mapping_mutation(ledger):
    class _Boom(Exception):
        pass

    with pytest.raises(_Boom):
        with ledger.transaction() as unit:
            ledger.propose_mapping(_mapping("m-rollback", external_key_digest="c" * 64), unit=unit)
            raise _Boom("simulated failure")

    with pytest.raises(KeyError):
        ledger.get_mapping("m-rollback")
