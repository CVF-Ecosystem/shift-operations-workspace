"""P4-E real sender-aware webhook ingress, positive/wiring path
(completion-rereview R1, corrected by completion-rereview2 F1/F4): proves
the actual FastAPI webhook route - not only the internal helper - accepts
the closed sender-aware transport binding, selects verification behavior
by ``signature_version`` as ONE integrated decision, and carries the
verified evidence through the REAL webhook -> InboundService ->
RoutingService -> ExternalIngressService -> LedgerExternalIngressRepository
-> durable Operations Ledger chain - never a recording fake router plus
a manual insert into a separately constructed ledger the route never
touched. Negative/mutation cases live in
``test_p4e_webhook_sender_aware_negative.py`` (file-size guard)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from integration_edge.verification.hmac import sign_hmac

from tests.integration._p4e_webhook_helpers import (
    RecordingRouter, app_with, real_ledger, real_router, sender_aware_payload, sender_key_port, webhook_headers,
)


def test_valid_p4e_sender_v1_webhook_creates_durable_ledger_observation_end_to_end():
    """The REAL, complete chain: webhook -> InboundService -> RoutingService
    -> ExternalIngressService -> LedgerExternalIngressRepository -> the
    SAME durable Operations Ledger the route itself wrote to. No
    RecordingRouter, no manually-constructed second ledger."""
    body = b'{"text": "hello"}'
    payload = sender_aware_payload(body=body)
    ledger = real_ledger()
    router = real_router(ledger)
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="p4e-sender-v1", signature="ignored-for-p4e-sender-v1",
            sender_aware_json=json.dumps(payload),
        ),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "ROUTED"

    from identity_mapping.models import ExternalIdentityKeyV1
    from operations_ledger.tables import p4e_proposals, external_identity_observations
    from sqlalchemy import select

    with ledger.engine.connect() as conn:
        proposal_rows = conn.execute(select(p4e_proposals)).mappings().all()
        observation_rows = conn.execute(select(external_identity_observations)).mappings().all()

    assert len(proposal_rows) == 1
    stored_proposal = proposal_rows[0]
    assert stored_proposal["sender_evidence"] is not None
    evidence_dict = stored_proposal["sender_evidence"]
    assert evidence_dict["body_sha256"] == hashlib.sha256(body).hexdigest()

    assert len(observation_rows) == 1
    stored_observation = observation_rows[0]
    expected_key = ExternalIdentityKeyV1(
        workspace_digest=evidence_dict["workspace_digest"], endpoint_id=evidence_dict["endpoint_id"],
        channel_id=evidence_dict["channel_id"], provider_account_digest=evidence_dict["provider_account_digest"],
        subject_kind=evidence_dict["subject_kind"], extraction_policy_id=evidence_dict["extraction_policy_id"],
        extraction_policy_version=evidence_dict["extraction_policy_version"],
        verification_scheme=evidence_dict["verification_scheme"], verification_version=evidence_dict["verification_version"],
        sender_token=evidence_dict["sender_token"], token_key_id=evidence_dict["token_key_id"],
        token_key_version=evidence_dict["token_key_version"],
    )
    assert stored_observation["external_key_digest"] == expected_key.digest()
    assert stored_observation["raw_envelope_id"] == evidence_dict["raw_envelope_id"]


def test_legacy_v1_webhook_creates_no_sender_evidence():
    body = b'{"text": "legacy"}'
    now = datetime.now(timezone.utc).isoformat()
    signature = sign_hmac(
        body, b"e" * 32, signature_version="v1", endpoint_id="ep1",
        channel_id="ch1", external_message_id="msg1", timestamp=now,
    )
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(signature_version="v1", signature=signature, timestamp=now),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "ROUTED"
    assert router.calls[0]["sender_evidence"] is None


def test_legacy_input_cannot_smuggle_a_second_optional_identity_object():
    """R1: even if a caller attaches an X-Sender-Aware header on a legacy
    signature version, it must never be parsed or trusted - only
    p4e-sender-v1 constructs the closed request at all."""
    body = b'{"text": "legacy-with-smuggled-header"}'
    now = datetime.now(timezone.utc).isoformat()
    signature = sign_hmac(
        body, b"e" * 32, signature_version="v1", endpoint_id="ep1",
        channel_id="ch1", external_message_id="msg1", timestamp=now,
    )
    smuggled = sender_aware_payload(body=body)
    router = RecordingRouter()
    app, _store = app_with(router=router, port=sender_key_port())
    client = TestClient(app)

    response = client.post(
        "/webhooks/ep1", content=body,
        headers=webhook_headers(
            signature_version="v1", signature=signature, timestamp=now,
            sender_aware_json=json.dumps(smuggled),
        ),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "ROUTED"
    assert router.calls[0]["sender_evidence"] is None
