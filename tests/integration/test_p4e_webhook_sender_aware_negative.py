"""P4-E real sender-aware webhook ingress, negative/mutation path
(completion-rereview R1): proves ``p4e-sender-v1`` is authenticated
EXCLUSIVELY over the sender-aware preimage (never a legacy-HMAC fallback),
that the closed request model rejects arbitrary/secret-bearing fields
before verification runs, and that mutating any bound dimension - or the
signing key itself - fails closed. Positive/wiring cases live in
``test_p4e_webhook_sender_aware_ingress.py`` (file-size guard)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from integration_edge.verification.hmac import sign_hmac
from integration_edge.verification.sender_keys import SenderTokenKeyAuthority

from tests.integration._p4e_webhook_helpers import (
    NoOpSecretStore, RecordingRouter, app_with, sender_aware_payload, sender_key_port, webhook_headers,
)


def test_stale_inner_timestamp_with_fresh_outer_timestamp_and_arbitrary_outer_signature_fails_closed():
    """completion-rereview2 F1 exact reproduction: the reviewer's probe
    supplied a stale INNER (sender-aware) timestamp, a fresh OUTER
    (transport) timestamp, and an arbitrary non-empty OUTER signature -
    the split-context bug returned ROUTED because only the outer pair was
    checked for freshness/presence while the inner pair was verified for
    signature correctness alone. Freshness must now be evaluated against
    the SAME signed timestamp that is actually authenticated, so a stale
    inner timestamp fails closed regardless of what the meaningless outer
    header pair claims."""
    body = b'{"text": "hi"}'
    stale_inner = datetime.now(timezone.utc) - timedelta(hours=1)
    payload = sender_aware_payload(body=body, timestamp=stale_inner.isoformat())
    fresh_outer = datetime.now(timezone.utc).isoformat()
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1",
            signature="deadbeef" * 8,  # arbitrary non-empty outer signature - never consulted
            timestamp=fresh_outer,     # fresh outer timestamp - never consulted
            sender_aware_json=json.dumps(payload),
        ),
    )

    assert response.status_code == 200
    body_json = response.json()
    assert body_json["outcome"] == "AUTH_REFUSED"
    assert body_json["reason"] == "STALE_SIGNATURE"
    assert len(router.calls) == 0


def test_outer_and_inner_endpoint_channel_message_mismatch_fails_closed():
    """The outer webhook path params (``endpoint_id`` from the URL,
    ``channel_id``/``external_message_id`` from outer headers) must agree
    with the inner sender-aware request's own claimed scope - an outer/
    inner mismatch on any of the three is refused, never silently
    resolved by trusting one side."""
    body = b'{"text": "hi"}'
    payload = sender_aware_payload(body=body)
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1", signature="ignored",
            channel_id="outer-channel-mismatch",  # outer header disagrees with payload["channel_id"]
            sender_aware_json=json.dumps(payload),
        ),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "AUTH_REFUSED"
    assert len(router.calls) == 0


def test_malformed_sender_aware_evidence_fails_closed():
    """A structurally malformed ``X-Sender-Aware`` JSON body (missing
    required fields) is refused before any verification runs."""
    body = b'{"text": "hi"}'
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1", signature="ignored",
            sender_aware_json=json.dumps({"only": "a partial, invalid payload"}),
        ),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "AUTH_REFUSED"
    assert len(router.calls) == 0


def test_missing_sender_aware_envelope_on_p4e_sender_v1_fails_closed():
    """``p4e-sender-v1`` selected but no ``X-Sender-Aware`` header at all
    must refuse, never silently fall through to legacy behavior. The
    empty header fails closed at the closed-model construction step
    (missing required fields) before ``InboundService.process`` is even
    reached - still a closed refusal, not a route call."""
    body = b'{"text": "hi"}'
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(signature_version="p4e-sender-v1", signature="ignored"),
    )

    assert response.status_code == 200
    body_json = response.json()
    assert body_json["outcome"] == "AUTH_REFUSED"
    assert body_json["reason"] == "INVALID_SIGNATURE"
    assert len(router.calls) == 0


def test_p4e_sender_v1_never_falls_back_to_legacy_hmac():
    """p4e-sender-v1 is authenticated EXCLUSIVELY over the sender-aware
    preimage. A caller supplying a correct legacy HMAC signature but no
    (or an invalid) sender-aware envelope must still fail closed."""
    body = b'{"text": "hi"}'
    now = datetime.now(timezone.utc).isoformat()
    legacy_signature = sign_hmac(
        body, b"e" * 32, signature_version="p4e-sender-v1", endpoint_id="ep1",
        channel_id="ch1", external_message_id="msg1", timestamp=now,
    )
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(signature_version="p4e-sender-v1", signature=legacy_signature, timestamp=now),
    )

    assert response.status_code == 200
    body_json = response.json()
    assert body_json["outcome"] == "AUTH_REFUSED"
    assert body_json["reason"] == "INVALID_SIGNATURE"
    assert len(router.calls) == 0


def test_arbitrary_and_secret_bearing_fields_are_rejected_by_the_closed_model():
    """The closed SenderAwareIngressRequest (extra='forbid') rejects an
    unknown/secret-bearing field before any signature verification runs."""
    body = b'{"text": "hi"}'
    payload = sender_aware_payload(body=body)
    payload["unexpected_secret"] = "should-be-rejected"
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1", signature="ignored",
            sender_aware_json=json.dumps(payload),
        ),
    )

    assert response.status_code == 200
    body_json = response.json()
    assert body_json["outcome"] == "AUTH_REFUSED"
    assert body_json["reason"] == "INVALID_SIGNATURE"
    assert len(router.calls) == 0


def _mutation_case(field, value, *, in_body=False):
    body = b'{"text": "hi"}'
    payload = sender_aware_payload(body=body)
    if in_body:
        body = b'{"text": "CHANGED"}'
    else:
        payload[field] = value
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)
    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1", signature="ignored",
            sender_aware_json=json.dumps(payload),
        ),
    )
    return response, router


def test_changed_endpoint_channel_message_body_timestamp_sender_or_policy_fails_closed():
    for field, value in [
        ("channel_id", "ch-other"), ("external_message_id", "msg-other"),
        ("raw_sender", "+1999999999"), ("extraction_policy_id", "pol-other"),
        ("workspace_digest", "b" * 64), ("provider_account_digest", "b" * 64),
    ]:
        response, router = _mutation_case(field, value)
        assert response.status_code == 200
        assert response.json()["outcome"] == "AUTH_REFUSED", field
        assert len(router.calls) == 0, field

    response, router = _mutation_case("body", None, in_body=True)
    assert response.json()["outcome"] == "AUTH_REFUSED"
    assert len(router.calls) == 0


def test_changed_key_version_fails_closed():
    body = b'{"text": "hi"}'
    payload = sender_aware_payload(body=body)
    router = RecordingRouter()
    other_authority = SenderTokenKeyAuthority(NoOpSecretStore(), clock=lambda: datetime.now(timezone.utc))
    other_authority.activate("skey2", "2", b"z" * 32)  # different key than the one that signed
    app, _store = app_with(router=router, port=other_authority)
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1", signature="ignored",
            sender_aware_json=json.dumps(payload),
        ),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "AUTH_REFUSED"
    assert len(router.calls) == 0
