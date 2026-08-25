from datetime import datetime,timezone
from integration_edge import InMemoryKeyRegistry
from integration_edge.inbound import InboundService
from integration_edge.rate_limit import DualBudgetLimiter
from integration_edge.storage import InMemoryEdgeStore
from integration_edge.verification.hmac import sign_hmac

class Router:
    def __init__(self):self.calls=0
    def route(self,**kwargs):self.calls+=1;return True

def _service():
    store=InMemoryEdgeStore(); router=Router(); limiter=DualBudgetLimiter(store,preauth_limit=20,postauth_limit=20)
    service=InboundService(store=store,key_registry=InMemoryKeyRegistry({"k":b"k"*32},active_key_id="k"),limiter=limiter,endpoints={"ep"},trusted_peers={"peer"},secret_resolver=lambda _:b"s"*32,router=router)
    return service,store,router

def _send(service,body=b'{"type":"note"}',external="m"):
    stamp=datetime.now(timezone.utc).isoformat(); meta=dict(endpoint_id="ep",channel_id="ch",external_message_id=external,timestamp=stamp,signature_version="v1")
    sig=sign_hmac(body,b"s"*32,**meta); assert service.preauthorize(peer="peer",endpoint_id="ep",content_length=len(body)) is None
    return service.process(**meta,signature=sig,body=body)

def test_new_duplicate_collision_and_no_second_raw_copy():
    service,store,router=_service(); assert _send(service).outcome=="ROUTED"; assert _send(service).outcome=="DUPLICATE"
    assert _send(service,b'{"type":"other"}').outcome=="COLLISION_QUARANTINED" and len(store.envelopes)==2 and router.calls==1

def test_malformed_is_encrypted_then_quarantined_without_echo():
    service,store,_=_service(); receipt=_send(service,b"not-json","bad")
    assert receipt.outcome=="QUARANTINED" and receipt.reason=="MALFORMED_SCHEMA"
    assert all(env.ciphertext!=b"not-json" for env in store.envelopes.values())
