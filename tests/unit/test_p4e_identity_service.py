"""P4-E IdentityMappingService unit tests (SPEC R7/R8, AC-04): propose/
confirm separation, target-self-confirm refusal, transient re-entry
mismatch, and lifecycle refusals - against fake ports, no SQL backend."""

from __future__ import annotations

from datetime import datetime, timezone

from identity_mapping.crypto import derive_sender_token, normalize_sender_bytes
from identity_mapping.models import ExternalIdentityKeyV1, IdentityMappingV1, SenderObservationV1
from identity_mapping.service import IdentityMappingService

_NOW = datetime.now(timezone.utc)
_DIGEST64 = "a" * 64
_KEY_ID, _KEY_VERSION, _SECRET = "k1", "1", b"0" * 32


class _FakeKeyPort:
    def active_key(self):
        return _KEY_ID, _KEY_VERSION, _SECRET

    def resolve_key(self, key_id, key_version):
        if (key_id, key_version) == (_KEY_ID, _KEY_VERSION):
            return _SECRET
        return None


class _FakeRepository:
    def __init__(self):
        self.observations: dict[str, SenderObservationV1] = {}
        self.mappings: dict[str, IdentityMappingV1] = {}

    def get_observation(self, observation_id, *, unit=None):
        return self.observations[observation_id]

    def get_mapping(self, mapping_id, *, unit=None):
        return self.mappings[mapping_id]

    def get_current_mapping(self, external_key_digest, *, unit=None):
        current = [m for m in self.mappings.values() if m.external_key_digest == external_key_digest and m.status == "CONFIRMED"]
        if len(current) > 1:
            raise ValueError("multiple current")
        return current[0] if current else None

    def propose_mapping(self, mapping, *, unit=None):
        self.mappings[mapping.mapping_id] = mapping
        return mapping

    def confirm_mapping(self, mapping_id, *, expected_version, confirmer_id, predecessor_mapping_id=None, unit=None):
        mapping = self.mappings[mapping_id]
        if mapping.version != expected_version:
            raise ValueError("stale version")
        updated = mapping.model_copy(update={"status": "CONFIRMED", "confirmer_id": confirmer_id, "version": mapping.version + 1})
        self.mappings[mapping_id] = updated
        return updated

    def reject_mapping(self, mapping_id, *, expected_version, rejector_id, unit=None):
        mapping = self.mappings[mapping_id]
        updated = mapping.model_copy(update={"status": "REJECTED", "rejector_id": rejector_id, "version": mapping.version + 1})
        self.mappings[mapping_id] = updated
        return updated

    def revoke_mapping(self, mapping_id, *, expected_version, revoker_id, unit=None):
        mapping = self.mappings[mapping_id]
        updated = mapping.model_copy(update={"status": "REVOKED", "revoker_id": revoker_id, "version": mapping.version + 1})
        self.mappings[mapping_id] = updated
        return updated


def _observation_and_key(raw_sender="+84901234567"):
    normalized = normalize_sender_bytes(raw_sender)
    token = derive_sender_token(
        key_id=_KEY_ID, key_secret=_SECRET, workspace_digest=_DIGEST64, endpoint_id="ep1",
        channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="observation", verification_version="1", normalized_sender_bytes=normalized,
    )
    key = ExternalIdentityKeyV1(
        workspace_digest=_DIGEST64, endpoint_id="ep1", channel_id="ch1",
        provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="observation", verification_version="1",
        sender_token=token, token_key_id=_KEY_ID, token_key_version=_KEY_VERSION,
    )
    observation = SenderObservationV1(
        observation_id="obs1", external_key_digest=key.digest(), workspace_digest=_DIGEST64,
        endpoint_id="ep1", channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        raw_envelope_id="env1", external_message_id="msg1", received_at=_NOW,
    )
    return observation, key, raw_sender


def _service():
    repo = _FakeRepository()
    return IdentityMappingService(repo, _FakeKeyPort()), repo


def test_propose_applies_and_persists():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation

    receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    assert receipt.outcome == "APPLIED"
    assert receipt.action == "PROPOSE"
    assert len(repo.mappings) == 1


def test_propose_rejects_a_stale_or_wrong_expected_version():
    """completion-rereview2 F3/SPEC R8: expected_version is a real,
    enforced CAS input on propose - a fresh propose always creates
    version 1, so any other value is a closed conflict, never silently
    accepted or ignored."""
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation

    receipt = service.propose(
        observation_id="obs1", expected_version=2, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    assert receipt.outcome == "CONFLICT"
    assert receipt.reason == "VERSION_CONFLICT"
    assert len(repo.mappings) == 0


def test_propose_refuses_on_missing_observation():
    service, _repo = _service()
    receipt = service.propose(
        observation_id="missing", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender="x",
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    assert receipt.outcome == "REFUSED"
    assert receipt.reason == "IDENTITY_REQUIRED"


def test_propose_refuses_on_unknown_key():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id="unknown-key", key_version="9", idempotency_key="idem1",
    )
    assert receipt.outcome == "REFUSED"
    assert receipt.reason == "SENDER_MISMATCH"


def test_confirm_refuses_self_confirm_by_proposer():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    propose_receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    receipt = service.confirm(
        mapping_id=propose_receipt.aggregate_id, expected_version=1, confirmer_id="u2",
        target_user_active=True, observation_id="obs1", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION,
    )
    assert receipt.outcome == "REFUSED"
    assert receipt.reason == "SEPARATION_OF_DUTY"


def test_confirm_refuses_self_confirm_by_target_user():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    propose_receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    receipt = service.confirm(
        mapping_id=propose_receipt.aggregate_id, expected_version=1, confirmer_id="u1",
        target_user_active=True, observation_id="obs1", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION,
    )
    assert receipt.outcome == "REFUSED"
    assert receipt.reason == "SEPARATION_OF_DUTY"


def test_confirm_refuses_on_transient_reentry_mismatch():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    propose_receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    receipt = service.confirm(
        mapping_id=propose_receipt.aggregate_id, expected_version=1, confirmer_id="u3",
        target_user_active=True, observation_id="obs1", raw_sender="a-different-sender-value",
        key_id=_KEY_ID, key_version=_KEY_VERSION,
    )
    assert receipt.outcome == "REFUSED"
    assert receipt.reason == "SENDER_MISMATCH"


def test_confirm_refuses_inactive_target_user():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    propose_receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    receipt = service.confirm(
        mapping_id=propose_receipt.aggregate_id, expected_version=1, confirmer_id="u3",
        target_user_active=False, observation_id="obs1", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION,
    )
    assert receipt.outcome == "REFUSED"
    assert receipt.reason == "ACTOR_INACTIVE"


def test_confirm_succeeds_with_valid_different_human():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    propose_receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    receipt = service.confirm(
        mapping_id=propose_receipt.aggregate_id, expected_version=1, confirmer_id="u3",
        target_user_active=True, observation_id="obs1", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION,
    )
    assert receipt.outcome == "APPLIED"
    assert receipt.action == "CONFIRM"


def test_resolve_fallback_on_no_mapping():
    service, _repo = _service()
    result = service.resolve(_DIGEST64)
    assert result.outcome == "FALLBACK"
    assert result.reason == "NO_MAPPING"


def test_resolve_resolved_on_confirmed_current_mapping():
    service, repo = _service()
    observation, _key, raw_sender = _observation_and_key()
    repo.observations["obs1"] = observation
    propose_receipt = service.propose(
        observation_id="obs1", expected_version=1, target_user_id="u1", proposer_id="u2", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION, idempotency_key="idem1",
    )
    service.confirm(
        mapping_id=propose_receipt.aggregate_id, expected_version=1, confirmer_id="u3",
        target_user_active=True, observation_id="obs1", raw_sender=raw_sender,
        key_id=_KEY_ID, key_version=_KEY_VERSION,
    )
    result = service.resolve(observation.external_key_digest)
    assert result.outcome == "RESOLVED"
    assert result.target_user_id == "u1"
    assert result.resolution_count == 1
