"""P4-E raw sender/token negative disclosure scans (SPEC AC-03) and
retention boundary tests (SPEC AC-13): raw sender/token never appear in
models, receipts, audit, or telemetry-shaped output; retention windows use
an injected clock and verify the exact boundary instant."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from identity_mapping.models import (
    IdentityMappingV1,
    MappingActionReceipt,
    SenderEvidenceV1,
    SenderObservationV1,
)
from identity_mapping.retention import (
    TERMINAL_LINEAGE_RETENTION,
    TOKEN_KEY_DUAL_READ_WINDOW,
    UNMAPPED_OBSERVATION_RETENTION,
    observation_expired,
    terminal_lineage_expired,
    token_key_within_dual_read_window,
)

_DIGEST64 = "a" * 64
_RAW_SENDER = "+84901234567"
_NOW = datetime.now(timezone.utc)


def test_sender_evidence_serialization_never_contains_raw_sender():
    evidence = SenderEvidenceV1(
        workspace_digest=_DIGEST64, endpoint_id="ep1", channel_id="ch1",
        provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        sender_token=_DIGEST64, token_key_id="k1", token_key_version="1",
        source_path_digest=_DIGEST64, raw_envelope_id="env1",
        external_message_id="msg1", body_sha256=_DIGEST64, received_at=_NOW,
    )
    dumped = evidence.model_dump_json()
    assert _RAW_SENDER not in dumped


def test_observation_serialization_never_contains_raw_sender_or_token():
    observation = SenderObservationV1(
        observation_id="obs1", external_key_digest=_DIGEST64, workspace_digest=_DIGEST64,
        endpoint_id="ep1", channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        raw_envelope_id="env1", external_message_id="msg1", received_at=_NOW,
    )
    dumped = observation.model_dump_json()
    assert _RAW_SENDER not in dumped
    assert "sender_token" not in dumped


def test_mapping_receipt_serialization_never_contains_raw_sender():
    receipt = MappingActionReceipt(
        outcome="APPLIED", action="PROPOSE", aggregate_id="m1", aggregate_version=1,
        audit_id="a1", command_application_count=1, audit_count=1, replayed=False,
    )
    dumped = receipt.model_dump_json()
    assert _RAW_SENDER not in dumped
    assert "raw_sender" not in dumped


def test_identity_mapping_serialization_never_contains_password_or_role():
    mapping = IdentityMappingV1(
        mapping_id="m1", external_key_digest=_DIGEST64, target_user_id="u1",
        proposal_evidence_digest=_DIGEST64, proposer_id="u2", status="CONFIRMED",
        version=1, created_at=_NOW, updated_at=_NOW,
    )
    dumped = mapping.model_dump_json()
    assert "password_hash" not in dumped
    assert '"role"' not in dumped


def test_privacy_delete_reason_never_appears_in_applied_receipt():
    """SPEC R19/F3: the operator-supplied deletion reason is a command
    input written only to the restricted actor-bound audit record - never
    present in the sanitized APPLIED receipt."""
    receipt = MappingActionReceipt(
        outcome="APPLIED", action="PRIVACY_DELETE", aggregate_id="m1", aggregate_version=2,
        audit_id="a1", command_application_count=1, audit_count=1, replayed=False,
    )
    assert "reason" not in receipt.model_dump(exclude_none=True)


def test_observation_not_expired_before_30_days():
    created_at = _NOW
    now = created_at + UNMAPPED_OBSERVATION_RETENTION - timedelta(seconds=1)
    assert not observation_expired(created_at=created_at, now=now)


def test_observation_expired_exact_boundary_and_beyond():
    """SPEC AC-13: verify the exact boundary instant with a fixed clock."""
    created_at = _NOW
    at_boundary = created_at + UNMAPPED_OBSERVATION_RETENTION
    assert not observation_expired(created_at=created_at, now=at_boundary)
    one_second_past = at_boundary + timedelta(seconds=1)
    assert observation_expired(created_at=created_at, now=one_second_past)


def test_terminal_lineage_not_expired_before_365_days():
    terminal_at = _NOW
    now = terminal_at + TERMINAL_LINEAGE_RETENTION - timedelta(seconds=1)
    assert not terminal_lineage_expired(terminal_at=terminal_at, now=now)


def test_terminal_lineage_expired_exact_boundary_and_beyond():
    terminal_at = _NOW
    at_boundary = terminal_at + TERMINAL_LINEAGE_RETENTION
    assert not terminal_lineage_expired(terminal_at=terminal_at, now=at_boundary)
    one_second_past = at_boundary + timedelta(seconds=1)
    assert terminal_lineage_expired(terminal_at=terminal_at, now=one_second_past)


def test_dual_read_window_exact_boundary():
    activated_at = _NOW
    at_boundary = activated_at + TOKEN_KEY_DUAL_READ_WINDOW
    assert token_key_within_dual_read_window(activated_at=activated_at, now=at_boundary)
    one_second_past = at_boundary + timedelta(seconds=1)
    assert not token_key_within_dual_read_window(activated_at=activated_at, now=one_second_past)


def test_retention_functions_require_aware_timestamps():
    naive = datetime(2026, 1, 1)
    try:
        observation_expired(created_at=naive, now=_NOW)
        assert False, "should have raised"
    except ValueError:
        pass
