"""P4-E closed model contract tests (SPEC R3, R4, R6): extra-field
rejection, mapping lifecycle transitions, and digest determinism/mutation
sensitivity for `ExternalIdentityKeyV1` (SPEC R4/AC-02)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from identity_mapping.models import (
    ExternalIdentityKeyV1,
    IdentityMappingV1,
    SenderEvidenceV1,
    SenderObservationV1,
    mapping_transition_allowed,
)

_DIGEST = "a" * 64
_NOW = datetime.now(timezone.utc)


def _key(**overrides) -> ExternalIdentityKeyV1:
    fields = dict(
        workspace_digest=_DIGEST, endpoint_id="ep1", channel_id="ch1",
        provider_account_digest=_DIGEST, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        sender_token=_DIGEST, token_key_id="k1", token_key_version="1",
    )
    fields.update(overrides)
    return ExternalIdentityKeyV1(**fields)


def test_sender_evidence_rejects_extra_fields():
    with pytest.raises(ValidationError):
        SenderEvidenceV1(
            workspace_digest=_DIGEST, endpoint_id="ep1", channel_id="ch1",
            provider_account_digest=_DIGEST, subject_kind="phone",
            extraction_policy_id="pol1", extraction_policy_version="1",
            verification_scheme="hmac", verification_version="1",
            sender_token=_DIGEST, token_key_id="k1", token_key_version="1",
            source_path_digest=_DIGEST, raw_envelope_id="env1",
            external_message_id="msg1", body_sha256=_DIGEST, received_at=_NOW,
            raw_sender="+84901234567",  # forbidden: no raw sender field
        )


def test_sender_evidence_has_no_raw_sender_or_principal_field():
    """SPEC R3: contains no raw sender, principal, assignment, permission,
    approval, confirmation, or conversation field."""
    fields = set(SenderEvidenceV1.model_fields)
    forbidden = {"raw_sender", "principal", "assignment_id", "permission", "approval_id",
                 "confirmed", "conversation_id"}
    assert fields.isdisjoint(forbidden)


def test_sender_evidence_requires_aware_timestamp():
    with pytest.raises(ValidationError):
        SenderEvidenceV1(
            workspace_digest=_DIGEST, endpoint_id="ep1", channel_id="ch1",
            provider_account_digest=_DIGEST, subject_kind="phone",
            extraction_policy_id="pol1", extraction_policy_version="1",
            verification_scheme="hmac", verification_version="1",
            sender_token=_DIGEST, token_key_id="k1", token_key_version="1",
            source_path_digest=_DIGEST, raw_envelope_id="env1",
            external_message_id="msg1", body_sha256=_DIGEST,
            received_at=datetime(2026, 1, 1),  # naive
        )


def test_observation_omits_sender_token_and_candidate_content():
    """SPEC R5: management reads may expose only observation id, non-secret
    selector metadata, and received time - never sender token, raw sender,
    or candidate body."""
    fields = set(SenderObservationV1.model_fields)
    forbidden = {"sender_token", "raw_sender", "candidate", "candidate_body"}
    assert fields.isdisjoint(forbidden)


def test_external_identity_key_digest_is_deterministic():
    key = _key()
    assert key.digest() == key.digest()
    assert len(key.digest()) == 64


@pytest.mark.parametrize("field,value", [
    ("workspace_digest", "b" * 64),
    ("endpoint_id", "ep2"),
    ("channel_id", "ch2"),
    ("provider_account_digest", "b" * 64),
    ("subject_kind", "email"),
    ("extraction_policy_id", "pol2"),
    ("extraction_policy_version", "2"),
    ("verification_scheme", "oauth"),
    ("verification_version", "2"),
    ("sender_token", "b" * 64),
    ("token_key_id", "k2"),
    ("token_key_version", "2"),
])
def test_any_key_dimension_change_changes_the_digest(field, value):
    """SPEC R4/AC-02: a change to any dimension produces a new key."""
    baseline = _key()
    mutated = _key(**{field: value})
    assert baseline.digest() != mutated.digest()


def test_mapping_transition_graph_matches_spec_r6():
    assert mapping_transition_allowed("PROPOSED", "CONFIRMED")
    assert mapping_transition_allowed("PROPOSED", "REJECTED")
    assert mapping_transition_allowed("CONFIRMED", "REVOKED")
    assert not mapping_transition_allowed("PROPOSED", "REVOKED")
    assert not mapping_transition_allowed("REJECTED", "CONFIRMED")
    assert not mapping_transition_allowed("REVOKED", "CONFIRMED")
    assert not mapping_transition_allowed("CONFIRMED", "PROPOSED")


def test_identity_mapping_stores_only_a_user_reference():
    """SPEC section 5: a confirmed mapping stores a user reference only -
    never a copy of role, active status, JWT claims, permission, or
    assignment authority."""
    fields = set(IdentityMappingV1.model_fields)
    forbidden = {"role", "is_active", "jwt", "permission", "assignment_id", "password_hash"}
    assert fields.isdisjoint(forbidden)


def test_identity_mapping_rejects_extra_fields():
    with pytest.raises(ValidationError):
        IdentityMappingV1(
            mapping_id="m1", external_key_digest=_DIGEST, target_user_id="u1",
            proposal_evidence_digest=_DIGEST, proposer_id="u2", status="PROPOSED",
            version=1, created_at=_NOW, updated_at=_NOW, unexpected_field="x",
        )
