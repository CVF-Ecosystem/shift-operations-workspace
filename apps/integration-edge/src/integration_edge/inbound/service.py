from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from integration_edge.crypto import encrypt_envelope
from integration_edge.invariants import emit_ingress_terminal_receipt
from integration_edge.storage.protocol import StoredEnvelope
from integration_edge.verification.hmac import verify_hmac


class InboundService:
    def __init__(self, *, store, key_registry, limiter, endpoints: set[str], trusted_peers: set[str], secret_resolver, router=None, max_body_bytes: int = 1_048_576, clock_skew_seconds: int = 300):
        self.store,self.key_registry,self.limiter=store,key_registry,limiter
        self.endpoints,self.trusted_peers=endpoints,trusted_peers
        self.secret_resolver,self.router=secret_resolver,router
        self.max_body_bytes,self.clock_skew_seconds=max_body_bytes,clock_skew_seconds

    def preauthorize(self, *, peer: str | None, endpoint_id: str, content_length: int) -> object | None:
        peer_key=peer or "missing"
        if not self.limiter.consume_preauth(peer_key):
            return emit_ingress_terminal_receipt("PREAUTH_REFUSED",reason="RATE_LIMITED",preauth_count=1,postauth_count=0,route_attempts=0)
        if not peer or peer not in self.trusted_peers or endpoint_id not in self.endpoints:
            return emit_ingress_terminal_receipt("PREAUTH_REFUSED",reason="UNTRUSTED_PEER",preauth_count=1,postauth_count=0,route_attempts=0)
        if content_length<0 or content_length>self.max_body_bytes:
            return emit_ingress_terminal_receipt("PREAUTH_REFUSED",reason="OVERSIZED",preauth_count=1,postauth_count=0,route_attempts=0)
        return None

    def process(self, *, endpoint_id: str, channel_id: str, external_message_id: str, timestamp: str, signature_version: str, signature: str, body: bytes):
        try: secret=self.secret_resolver(endpoint_id)
        except Exception: secret=b""
        if not signature:
            return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="MISSING_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
        if not _fresh(timestamp,self.clock_skew_seconds):
            return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="STALE_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
        if not verify_hmac(body,signature,secret,signature_version=signature_version,endpoint_id=endpoint_id,channel_id=channel_id,external_message_id=external_message_id,timestamp=timestamp):
            return emit_ingress_terminal_receipt("AUTH_REFUSED",reason="INVALID_SIGNATURE",preauth_count=1,postauth_count=0,route_attempts=0)
        aad=f"{endpoint_id}\0{channel_id}\0{external_message_id}".encode()
        encrypted=encrypt_envelope(body,aad=aad,key_registry=self.key_registry)
        envelope_id=str(uuid4())
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
        try: accepted=self.router.route(envelope_id=envelope_id,channel=channel_id,external_id=external_message_id,candidate=candidate)
        except (PermissionError,ValueError):
            return emit_ingress_terminal_receipt("ROUTE_REFUSED",reason="DOWNSTREAM_REFUSED",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)
        except Exception:
            return emit_ingress_terminal_receipt("ROUTE_OUTCOME_UNKNOWN",reason="AMBIGUOUS_TRANSPORT",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)
        if accepted is False:
            return emit_ingress_terminal_receipt("ROUTE_REFUSED",reason="DOWNSTREAM_REFUSED",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)
        return emit_ingress_terminal_receipt("ROUTED",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=1)

    def _quarantine(self,envelope_id:str,reason:str):
        try:q=self.store.quarantine(envelope_id,reason)
        except RuntimeError:
            return emit_ingress_terminal_receipt("QUARANTINE_PERSISTENCE_FAILED",reason="QUARANTINE_SINK_UNAVAILABLE",raw_envelope_id=envelope_id,preauth_count=1,postauth_count=1,route_attempts=0)
        return emit_ingress_terminal_receipt("QUARANTINED",reason=reason,raw_envelope_id=envelope_id,quarantine_id=q.quarantine_id,preauth_count=1,postauth_count=1,route_attempts=0)


def _fresh(value:str,skew:int)->bool:
    try: stamp=datetime.fromisoformat(value.replace("Z","+00:00")); return abs((datetime.now(timezone.utc)-stamp).total_seconds())<=skew
    except (ValueError,TypeError): return False
