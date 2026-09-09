"""Shared fixtures for the P4-E real sender-aware webhook ingress tests
(completion-rereview R1). Split out of the test files for the file-size
guard, same reason ``_schema_parity_parsing.py`` is split out of the
schema-parity test files."""

from __future__ import annotations

import hashlib
import hmac as hmaclib
import json
from datetime import datetime, timezone

from fastapi import FastAPI

from channel_sdk import normalize_sender_bytes, sender_aware_signature_preimage
from integration_edge import InMemoryKeyRegistry
from integration_edge.inbound import InboundService
from integration_edge.rate_limit import DualBudgetLimiter
from integration_edge.routing.service import RoutingService
from integration_edge.storage import InMemoryEdgeStore
from integration_edge.verification.sender_keys import SenderTokenKeyAuthority
from integration_edge.webhook.router import router as webhook_router

DIGEST64 = "a" * 64
ENDPOINT_SECRET = b"e" * 32
SENDER_KEY_SECRET = b"k" * 32


class RecordingRouter:
    def __init__(self):
        self.calls: list[dict] = []

    def route(self, *, envelope_id, channel, external_id, candidate, sender_evidence=None):
        self.calls.append({
            "envelope_id": envelope_id, "channel": channel, "external_id": external_id,
            "candidate": candidate, "sender_evidence": sender_evidence,
        })
        return True


class NoOpSecretStore:
    def delete_wrapping_key(self, key_id, key_version): return True
    def purge_cache(self, key_id, key_version): return True


def sender_key_port(*, key_id="skey1", key_version="1", secret=SENDER_KEY_SECRET):
    authority = SenderTokenKeyAuthority(NoOpSecretStore(), clock=lambda: datetime.now(timezone.utc))
    authority.activate(key_id, key_version, secret)
    return authority


def app_with(*, router, port):
    store = InMemoryEdgeStore()
    limiter = DualBudgetLimiter(store, preauth_limit=100, postauth_limit=100)
    service = InboundService(
        store=store, key_registry=InMemoryKeyRegistry({"k": b"k" * 32}, active_key_id="k"),
        limiter=limiter, endpoints={"ep1"}, trusted_peers={"testclient"},
        secret_resolver=lambda _endpoint: ENDPOINT_SECRET, router=router,
        sender_key_port=port,
    )
    app = FastAPI()
    app.include_router(webhook_router)
    app.state.inbound_service = service
    return app, store


def sender_aware_payload(*, body: bytes, endpoint_id="ep1", channel_id="ch1",
                          external_message_id="msg1", raw_sender="+84901234567",
                          secret=SENDER_KEY_SECRET, **overrides):
    now = datetime.now(timezone.utc)
    fields = dict(
        signature_version="p4e-sender-v1", workspace_digest=DIGEST64, endpoint_id=endpoint_id,
        channel_id=channel_id, provider_account_digest=DIGEST64, subject_kind="phone",
        extraction_policy_id="pol1", extraction_policy_version="1",
        verification_scheme="hmac", verification_version="1",
        external_message_id=external_message_id, timestamp=now.isoformat(),
        raw_sender=raw_sender, body_sha256=hashlib.sha256(body).hexdigest(),
    )
    fields.update(overrides)
    normalized = normalize_sender_bytes(fields["raw_sender"])
    preimage = sender_aware_signature_preimage(
        signature_version=fields["signature_version"], workspace_digest=fields["workspace_digest"],
        endpoint_id=fields["endpoint_id"], channel_id=fields["channel_id"],
        provider_account_digest=fields["provider_account_digest"], subject_kind=fields["subject_kind"],
        extraction_policy_id=fields["extraction_policy_id"], extraction_policy_version=fields["extraction_policy_version"],
        verification_scheme=fields["verification_scheme"], verification_version=fields["verification_version"],
        external_message_id=fields["external_message_id"], timestamp=now,
        normalized_sender_bytes=normalized, body_sha256=fields["body_sha256"],
    )
    fields["signature"] = hmaclib.new(secret, preimage, hashlib.sha256).hexdigest()
    return fields


def webhook_headers(*, channel_id="ch1", external_message_id="msg1", signature_version, signature,
                     timestamp=None, sender_aware_json=None):
    headers = {
        "X-Channel-Id": channel_id, "X-External-Message-Id": external_message_id,
        "X-Signature-Version": signature_version, "X-Signature": signature,
        "X-Timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }
    if sender_aware_json is not None:
        headers["X-Sender-Aware"] = sender_aware_json
    return headers


_SERVICE_ASSERTION_SECRET = b"0" * 32
_SERVICE_ASSERTION_KEY_ID = "p4e-test-service-key-1"


def real_ledger():
    """completion-rereview2 F1/F4: a REAL durable Operations Ledger,
    exactly the same class production composition uses, for tests that
    must prove webhook -> route -> durable persistence rather than
    manually inserting evidence into a separately constructed ledger the
    route never touched. ``StaticPool`` keeps every connection on the SAME
    in-memory SQLite database - required here (unlike other P4-E tests
    that never route through a real ``TestClient``) because FastAPI's
    ``TestClient`` may dispatch the request off a different thread than
    the one that created the schema, and a bare ``sqlite:///:memory:``
    engine hands each new connection an empty, separate database."""
    from sqlalchemy.pool import StaticPool

    from operations_ledger.sql_ledger import SqlLedger, make_engine
    from operations_ledger.tables import metadata
    from workspace_api.domain import models as domain_models

    engine = make_engine("sqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
    metadata.create_all(engine)
    return SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)


def real_router(ledger):
    """completion-rereview2 F1/F4: a REAL ``integration_edge.routing.
    service.RoutingService`` wired to the REAL cross-service seam - a
    real signed ``ServiceAssertionV1``, the REAL ``verify_service_
    assertion`` path, and the REAL ``ExternalIngressService.propose`` ->
    ``LedgerExternalIngressRepository.add`` -> ``ledger.add_p4e_proposal``
    chain - never ``RecordingRouter`` plus a manual insert into a separate
    ledger the route never touched. Only the literal HTTP socket hop
    between the two FastAPI apps is elided; the assertion sign/verify
    pair, persistence, idempotency, and lineage logic are all real,
    unmocked production code."""
    from datetime import timedelta
    from uuid import uuid4

    from channel_sdk import ServiceAssertionV1
    from integration_edge.verification.service_assertion import (
        InMemoryNonceStore, ServiceAssertionKey, ServiceKeyRegistry,
        sign_service_assertion, verify_service_assertion,
    )
    from workspace_api.external_ingress.models import ExternalIngressProposalInput
    from workspace_api.external_ingress.repository import LedgerExternalIngressRepository
    from workspace_api.external_ingress.service import ExternalIngressService

    repository = LedgerExternalIngressRepository(ledger)
    key_registry = ServiceKeyRegistry({
        _SERVICE_ASSERTION_KEY_ID: ServiceAssertionKey(
            secret=_SERVICE_ASSERTION_SECRET,
            not_before=datetime(2020, 1, 1, tzinfo=timezone.utc),
            not_after=datetime(2999, 1, 1, tzinfo=timezone.utc),
            issuer="integration-edge", subject="workspace-api",
        )
    })
    nonce_store = InMemoryNonceStore()

    def _verifier(assertion: str, *, audience: str, operation: str, body: bytes):
        parsed = ServiceAssertionV1.model_validate_json(assertion)
        return verify_service_assertion(
            parsed, key_registry=key_registry, nonce_store=nonce_store,
            expected_audience=audience, expected_operation=operation,
            expected_method="POST", expected_path="/external-ingress/proposals",
            body=body,
        )

    service = ExternalIngressService(repository, _verifier)

    class _CorePort:
        def propose_external_ingress(self, *, assertion, proposal, idempotency_key):
            payload = ExternalIngressProposalInput(**{
                k: v for k, v in proposal.items()
                if k in ("envelope_id", "channel", "external_id", "candidate", "provenance_digest", "sender_evidence")
            })
            return service.propose(payload, assertion)

    def _assertion_signer(*, audience, operation, body, idempotency_key):
        payload = ExternalIngressProposalInput(**{
            k: v for k, v in json.loads(body).items()
            if k in ("envelope_id", "channel", "external_id", "candidate", "provenance_digest", "sender_evidence")
        })
        now = datetime.now(timezone.utc)
        unsigned = ServiceAssertionV1(
            key_id=_SERVICE_ASSERTION_KEY_ID, issuer="integration-edge", subject="workspace-api",
            audience=audience, operation=operation, method="POST",
            path="/external-ingress/proposals", issued_at=now, expires_at=now + timedelta(seconds=30),
            nonce=uuid4().hex,
            body_sha256=hashlib.sha256(payload.model_dump_json(exclude_none=True).encode()).hexdigest(),
            idempotency_key=idempotency_key, correlation_id=uuid4().hex,
        )
        return sign_service_assertion(unsigned, _SERVICE_ASSERTION_SECRET).model_dump_json()

    return RoutingService(_CorePort(), _assertion_signer, InMemoryEdgeStore())
