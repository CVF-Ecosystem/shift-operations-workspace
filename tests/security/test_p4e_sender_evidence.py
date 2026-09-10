"""P4-E sender-aware signature/evidence security tests (SPEC AC-02):
every R1/R2 dimension is covered by mutation vectors; mutating any
dimension changes or invalidates the key; legacy ingress reaches fallback
without a mapping lookup."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from integration_edge.models import SenderAwareIngressRequest
from integration_edge.verification.hmac import verify_sender_aware_signature
from channel_sdk import derive_sender_token, normalize_sender_bytes, sender_aware_signature_preimage

_DIGEST64 = "a" * 64
_NOW = datetime.now(timezone.utc)
_SECRET = b"0" * 32


def _request(**overrides) -> SenderAwareIngressRequest:
    fields = dict(
        workspace_digest=_DIGEST64, endpoint_id="ep1", channel_id="ch1",
        provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        external_message_id="msg1", timestamp=_NOW, raw_sender="+84901234567",
        body_sha256=_DIGEST64, signature="0" * 64,
    )
    fields.update(overrides)
    return SenderAwareIngressRequest(**fields)


def _sign(request: SenderAwareIngressRequest, normalized: bytes) -> str:
    import hashlib
    import hmac as hmaclib

    preimage = sender_aware_signature_preimage(
        signature_version=request.signature_version, workspace_digest=request.workspace_digest,
        endpoint_id=request.endpoint_id, channel_id=request.channel_id,
        provider_account_digest=request.provider_account_digest, subject_kind=request.subject_kind,
        extraction_policy_id=request.extraction_policy_id, extraction_policy_version=request.extraction_policy_version,
        verification_scheme=request.verification_scheme, verification_version=request.verification_version,
        external_message_id=request.external_message_id, timestamp=request.timestamp,
        normalized_sender_bytes=normalized, body_sha256=request.body_sha256,
    )
    return hmaclib.new(_SECRET, preimage, hashlib.sha256).hexdigest()


def test_valid_signature_verifies():
    request = _request()
    normalized = normalize_sender_bytes(request.raw_sender)
    signature = _sign(request, normalized)
    assert verify_sender_aware_signature(signature, _SECRET, request=request, normalized_sender_bytes=normalized)


@pytest.mark.parametrize("field,new_value", [
    ("workspace_digest", "b" * 64),
    ("endpoint_id", "ep2"),
    ("channel_id", "ch2"),
    ("provider_account_digest", "b" * 64),
    ("subject_kind", "email"),
    ("extraction_policy_id", "pol2"),
    ("extraction_policy_version", "2"),
    ("verification_scheme", "oauth"),
    ("verification_version", "2"),
    ("external_message_id", "msg2"),
    ("body_sha256", "b" * 64),
])
def test_mutating_any_r1_dimension_invalidates_the_signature(field, new_value):
    """SPEC AC-02: every R1/R2 dimension is covered; mutating any dimension
    invalidates the previously computed signature."""
    request = _request()
    normalized = normalize_sender_bytes(request.raw_sender)
    signature = _sign(request, normalized)
    mutated = request.model_copy(update={field: new_value})
    assert not verify_sender_aware_signature(signature, _SECRET, request=mutated, normalized_sender_bytes=normalized)


def test_mutating_raw_sender_invalidates_the_signature():
    request = _request()
    normalized = normalize_sender_bytes(request.raw_sender)
    signature = _sign(request, normalized)
    other_normalized = normalize_sender_bytes("+1999999999")
    assert not verify_sender_aware_signature(signature, _SECRET, request=request, normalized_sender_bytes=other_normalized)


def test_wrong_secret_fails_verification():
    request = _request()
    normalized = normalize_sender_bytes(request.raw_sender)
    signature = _sign(request, normalized)
    assert not verify_sender_aware_signature(signature, b"1" * 32, request=request, normalized_sender_bytes=normalized)


def test_derived_token_changes_when_any_identity_semantic_field_changes():
    """SPEC R2/AC-02: every identity-semantic field (excluding message id,
    timestamp, body digest) is bound into the token."""
    base_kwargs = dict(
        key_id="k1", key_secret=_SECRET, workspace_digest=_DIGEST64, endpoint_id="ep1",
        channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        normalized_sender_bytes=normalize_sender_bytes("+84901234567"),
    )
    base_token = derive_sender_token(**base_kwargs)
    for field, value in [
        ("workspace_digest", "b" * 64), ("endpoint_id", "ep2"), ("channel_id", "ch2"),
        ("provider_account_digest", "b" * 64), ("subject_kind", "email"),
        ("extraction_policy_id", "pol2"), ("extraction_policy_version", "2"),
        ("verification_scheme", "oauth"), ("verification_version", "2"),
    ]:
        mutated_kwargs = dict(base_kwargs)
        mutated_kwargs[field] = value
        assert derive_sender_token(**mutated_kwargs) != base_token, field


def test_derived_token_changes_when_key_id_or_secret_changes():
    base = derive_sender_token(
        key_id="k1", key_secret=_SECRET, workspace_digest=_DIGEST64, endpoint_id="ep1",
        channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        normalized_sender_bytes=normalize_sender_bytes("+84901234567"),
    )
    different_key_id = derive_sender_token(
        key_id="k2", key_secret=_SECRET, workspace_digest=_DIGEST64, endpoint_id="ep1",
        channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        normalized_sender_bytes=normalize_sender_bytes("+84901234567"),
    )
    different_secret = derive_sender_token(
        key_id="k1", key_secret=b"9" * 32, workspace_digest=_DIGEST64, endpoint_id="ep1",
        channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        normalized_sender_bytes=normalize_sender_bytes("+84901234567"),
    )
    assert base != different_key_id
    assert base != different_secret


def test_normalize_rejects_empty_and_control_characters():
    with pytest.raises(ValueError):
        normalize_sender_bytes("")
    with pytest.raises(ValueError):
        normalize_sender_bytes("bad\x00value")
    with pytest.raises(ValueError):
        normalize_sender_bytes("bad\x01value")


def test_normalize_preserves_case_and_permits_horizontal_space():
    result = normalize_sender_bytes("John Doe")
    assert result == b"John Doe"


def test_normalize_rejects_over_512_bytes():
    with pytest.raises(ValueError):
        normalize_sender_bytes("x" * 513)


def test_derive_sender_token_rejects_short_key():
    with pytest.raises(ValueError):
        derive_sender_token(
            key_id="k1", key_secret=b"short", workspace_digest=_DIGEST64, endpoint_id="ep1",
            channel_id="ch1", provider_account_digest=_DIGEST64, subject_kind="phone",
            extraction_policy_id="pol1", extraction_policy_version="1",
            verification_scheme="hmac", verification_version="1",
            normalized_sender_bytes=normalize_sender_bytes("+84901234567"),
        )


def test_legacy_ingress_produces_no_sender_evidence():
    """SPEC AC-02: legacy ingress reaches fallback without a mapping
    lookup - InboundService derives no evidence when the caller supplies
    no sender-aware request or key port."""
    from integration_edge.inbound.service import InboundService

    service = InboundService(
        store=None, key_registry=None, limiter=None, endpoints=set(), trusted_peers=set(),
        secret_resolver=lambda _endpoint: b"0" * 32,
    )
    assert service._derive_sender_evidence(
        None, envelope_id="env1", endpoint_id="ep1", channel_id="ch1",
        external_message_id="msg1", body=b"{}",
    ) is None
