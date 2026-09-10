from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from uuid import uuid4

from integration_edge.crypto import encrypt_envelope
from integration_edge.invariants import emit_ingress_terminal_receipt
from integration_edge.storage.protocol import StoredEnvelope
from integration_edge.verification.hmac import verify_hmac, verify_sender_aware_signature


class InboundService:
    def __init__(self, *, store, key_registry, limiter, endpoints: set[str], trusted_peers: set[str], secret_resolver, router=None, max_body_bytes: int = 1_048_576, clock_skew_seconds: int = 300, sender_key_port=None):
        self.store,self.key_registry,self.limiter=store,key_registry,limiter
        self.endpoints,self.trusted_peers=endpoints,trusted_peers
        self.secret_resolver,self.router=secret_resolver,router
        self.max_body_bytes,self.clock_skew_seconds=max_body_bytes,clock_skew_seconds
        # P4-E SPEC R1/R2: optional sender-token key authority. Absent means
        # no sender evidence can ever be derived - legacy behavior only.
        self.sender_key_port=sender_key_port

    def preauthorize(self, *, peer: str | None, endpoint_id: str, content_length: int) -> object | None:
        peer_key=peer or "missing"
        if not self.limiter.consume_preauth(peer_key):
            return emit_ingress_terminal_receipt("PREAUTH_REFUSED",reason="RATE_LIMITED",preauth_count=1,postauth_count=0,route_attempts=0)
        if not peer or peer not in self.trusted_peers or endpoint_id not in self.endpoints:
            return emit_ingress_terminal_receipt("PREAUTH_REFUSED",reason="UNTRUSTED_PEER",preauth_count=1,postauth_count=0,route_attempts=0)
        if content_length<0 or content_length>self.max_body_bytes:
            return emit_ingress_terminal_receipt("PREAUTH_REFUSED",reason="OVERSIZED",preauth_count=1,postauth_count=0,route_attempts=0)
        return None

    def process(self, *, endpoint_id: str, channel_id: str, external_message_id: str, timestamp: str, signature_version: str, signature: str, body: bytes, sender_aware_request=None):
        """completion-rereview2 F1: exactly ONE authoritative signature and
        timestamp location per signature version - never two parallel
        authentication contexts where only one is actually enforced.
        ``p4e-sender-v1`` reads its signature and timestamp EXCLUSIVELY
        from ``sender_aware_request`` (never the outer ``signature``/
        ``timestamp`` transport parameters, which are meaningless noise on
        this path and are not consulted for auth at all); every other
        version reads them EXCLUSIVELY from the outer parameters and never
        constructs or trusts a sender-aware request, so legacy input can
        never carry sender evidence, matching SPEC R1's 'legacy signature
        versions remain valid P4-C inputs but carry no P4-E evidence.'"""
        try: secret=self.secret_resolver(endpoint_id)
        except Exception: secret=b""
        sender_evidence = None
        if signature_version == "p4e-sender-v1":
            if sender_aware_request is None:
                # pinned p4c-ingress-terminal-outcomes matrix: AUTH_REFUSED's
                # reason is closed to MISSING_SIGNATURE/INVALID_SIGNATURE/
                # STALE_SIGNATURE - a missing sender-aware envelope is an
                # authentication failure, not a new reason literal.
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="MISSING_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
            if not sender_aware_request.signature:
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="MISSING_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
            if not _fresh_datetime(sender_aware_request.timestamp, self.clock_skew_seconds):
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="STALE_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
            envelope_id = str(uuid4())
            sender_evidence = self._derive_sender_evidence(
                sender_aware_request, envelope_id=envelope_id, endpoint_id=endpoint_id,
                channel_id=channel_id, external_message_id=external_message_id, body=body,
            )
            if sender_evidence is None:
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="INVALID_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
        else:
            if not signature:
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="MISSING_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
            if not _fresh(timestamp,self.clock_skew_seconds):
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="STALE_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
            if not verify_hmac(body,signature,secret,signature_version=signature_version,endpoint_id=endpoint_id,channel_id=channel_id,external_message_id=external_message_id,timestamp=timestamp):
                return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="INVALID_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
            envelope_id = str(uuid4())
        aad=f"{endpoint_id}\0{channel_id}\0{external_message_id}".encode()
        encrypted=encrypt_envelope(body,aad=aad,key_registry=self.key_registry)
        stored=StoredEnvelope(envelope_id,channel_id,endpoint_id,external_message_id,encrypted.plaintext_sha256,encrypted.key_id,encrypted.nonce,encrypted.ciphertext,encrypted.tag,aad)
        result=self.store.reserve(stored)
        if not self.limiter.consume_postauth(f"{channel_id}:{external_message_id}"):
            return emit_ingress_terminal_receipt("POSTAUTH_RATE_REFUSED",reason="RATE_LIMITED",raw_envelope_id=result.envelope.envelope_id,preauth_count=1,postauth_count=1,route_attempts=0)
        if result.kind=="DUPLICATE":
            return emit_ingress_terminal_receipt("DUPLICATE",raw_envelope_id=result.original_envelope_id,preauth_count=1,postauth_count=1,route_attempts=0)
        if result.kind=="COLLISION":
            return emit_ingress_terminal_receipt("COLLISION_QUARANTINED",reason="KEY_COLLISION",raw_envelope_id=envelope_id,quarantine_id=result.quarantine.quarantine_id,preauth_count=1,postauth_count=1,route_attempts=0)
        try:
            candidate=json.loads(body)
            if not isinstance(candidate,dict):raise ValueError
        except (UnicodeDecodeError,json.JSONDecodeError,ValueError):
            return self._quarantine(envelope_id,"MALFORMED_SCHEMA")
        if self.router is None:
            return self._quarantine(envelope_id,"ROUTE_POLICY_REFUSED")
        try: accepted=self.router.route(envelope_id=envelope_id,channel=channel_id,external_id=external_message_id,candidate=candidate,sender_evidence=sender_evidence)
        except (PermissionError,ValueError):
            return emit_ingress_terminal_receipt("ROUTE_REFUSED",reason="DOWNSTREAM_REFUSED",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)
        except Exception:
            return emit_ingress_terminal_receipt("ROUTE_OUTCOME_UNKNOWN",reason="AMBIGUOUS_TRANSPORT",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)
        if accepted is False:
            return emit_ingress_terminal_receipt("ROUTE_REFUSED",reason="DOWNSTREAM_REFUSED",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)
        return emit_ingress_terminal_receipt("ROUTED",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)

    def _derive_sender_evidence(self, sender_aware_request, *, envelope_id, endpoint_id,
                                 channel_id, external_message_id, body):
        """SPEC R1/R2/completion-review F2: verifies the sender-aware
        signature over the exact normalized bytes, binds the result to the
        ACTUAL persisted envelope and the ACTUAL ingress arguments (never a
        second, disconnected identity), recomputes the body digest from the
        real received bytes rather than trusting the caller's claimed
        digest, and returns a closed SenderEvidenceV1 - or None (no
        observation, no mapping attempt) on any mismatch or missing/
        invalid/unavailable-key condition. Raw sender bytes and token key
        bytes are never returned, logged, or persisted here."""
        if sender_aware_request is None or self.sender_key_port is None:
            return None
        from channel_sdk import SenderEvidenceV1, derive_sender_token, normalize_sender_bytes

        # Bind to the real ingress arguments before doing anything else -
        # a sender-aware request whose own claimed scope disagrees with
        # what was actually authenticated/received is never usable.
        if (sender_aware_request.endpoint_id != endpoint_id
                or sender_aware_request.channel_id != channel_id
                or sender_aware_request.external_message_id != external_message_id):
            return None
        recomputed_body_sha256 = hashlib.sha256(body).hexdigest()
        if not hmac.compare_digest(recomputed_body_sha256, sender_aware_request.body_sha256):
            return None

        try:
            normalized = normalize_sender_bytes(sender_aware_request.raw_sender)
        except ValueError:
            return None
        try:
            key_id, key_version, secret = self.sender_key_port.active_key()
        except ValueError:
            return None
        if not verify_sender_aware_signature(
            sender_aware_request.signature, secret,
            request=sender_aware_request, normalized_sender_bytes=normalized,
        ):
            return None
        token = derive_sender_token(
            key_id=key_id, key_secret=secret,
            workspace_digest=sender_aware_request.workspace_digest,
            endpoint_id=sender_aware_request.endpoint_id,
            channel_id=sender_aware_request.channel_id,
            provider_account_digest=sender_aware_request.provider_account_digest,
            subject_kind=sender_aware_request.subject_kind,
            extraction_policy_id=sender_aware_request.extraction_policy_id,
            extraction_policy_version=sender_aware_request.extraction_policy_version,
            verification_scheme="observation", verification_version="1",
            normalized_sender_bytes=normalized,
        )

        return SenderEvidenceV1(
            workspace_digest=sender_aware_request.workspace_digest,
            endpoint_id=sender_aware_request.endpoint_id,
            channel_id=sender_aware_request.channel_id,
            provider_account_digest=sender_aware_request.provider_account_digest,
            subject_kind=sender_aware_request.subject_kind,
            extraction_policy_id=sender_aware_request.extraction_policy_id,
            extraction_policy_version=sender_aware_request.extraction_policy_version,
            verification_scheme="observation", verification_version="1",
            sender_token=token, token_key_id=key_id, token_key_version=key_version,
            source_path_digest=hashlib.sha256(b"webhook-inbound").hexdigest(),
            raw_envelope_id=envelope_id,
            external_message_id=sender_aware_request.external_message_id,
            body_sha256=recomputed_body_sha256,
            received_at=sender_aware_request.timestamp,
        )

    def _quarantine(self,envelope_id:str,reason:str):
        try:q=self.store.quarantine(envelope_id,reason)
        except RuntimeError:
            return emit_ingress_terminal_receipt("QUARANTINE_PERSISTENCE_FAILED",reason="QUARANTINE_SINK_UNAVAILABLE",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=0)
        return emit_ingress_terminal_receipt("QUARANTINED",reason=reason,raw_envelope_id=envelope_id,quarantine_id=q.quarantine_id,preauth_count=1,postauth_count=1,route_attempts=0)


def _fresh(value:str,skew:int)->bool:
    try: stamp=datetime.fromisoformat(value.replace("Z","+00:00")); return abs((datetime.now(timezone.utc)-stamp).total_seconds())<=skew
    except (ValueError,TypeError): return False


def _fresh_datetime(stamp: datetime, skew: int) -> bool:
    """completion-rereview2 F1: freshness for the sender-aware path checks
    the SAME already-parsed, timezone-aware ``sender_aware_request.
    timestamp`` the signature itself is verified over - never a second,
    independently-supplied outer timestamp string."""
    try:
        return abs((datetime.now(timezone.utc) - stamp).total_seconds()) <= skew
    except (TypeError, OverflowError):
        return False
