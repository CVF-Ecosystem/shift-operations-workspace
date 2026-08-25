from datetime import datetime,timedelta,timezone
import hashlib
import pytest
from channel_sdk import ServiceAssertionV1
from integration_edge import InMemoryNonceStore,ServiceAssertionKey,ServiceKeyRegistry,sign_service_assertion,verify_service_assertion

def _fixture():
    now=datetime.now(timezone.utc); secret=b"a"*32; body=b"{}"
    claim=ServiceAssertionV1(key_id="k",issuer="edge",subject="edge",audience="workspace-api",operation="external_ingress.propose",method="POST",path="/external-ingress/proposals",issued_at=now,expires_at=now+timedelta(seconds=30),nonce="n"*16,body_sha256=hashlib.sha256(body).hexdigest(),idempotency_key="i",correlation_id="c")
    keys=ServiceKeyRegistry({"k":ServiceAssertionKey(secret,now-timedelta(seconds=1),now+timedelta(minutes=2),"edge","edge")})
    return sign_service_assertion(claim,secret),keys,body,now

def test_assertion_verifies_once_and_replay_refuses():
    claim,keys,body,now=_fixture(); nonces=InMemoryNonceStore(); args=dict(key_registry=keys,nonce_store=nonces,expected_audience="workspace-api",expected_operation="external_ingress.propose",expected_method="POST",expected_path="/external-ingress/proposals",body=body,now=now)
    assert verify_service_assertion(claim,**args)==claim
    with pytest.raises(Exception):verify_service_assertion(claim,**args)

def test_assertion_binds_body_audience_and_operation():
    claim,keys,body,now=_fixture()
    with pytest.raises(Exception):verify_service_assertion(claim,key_registry=keys,nonce_store=InMemoryNonceStore(),expected_audience="wrong",expected_operation="external_ingress.propose",expected_method="POST",expected_path="/external-ingress/proposals",body=body,now=now)
