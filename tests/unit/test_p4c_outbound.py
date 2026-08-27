from channel_adapters.conformance import emit_adapter_result
from integration_edge.outbound import AdapterScopeBindingV1, OutboundService
from integration_edge.storage import InMemoryEdgeStore

class Fake:
    adapter_mode="DEPLOYABLE"
    def __init__(self,status):self.status=status;self.calls=0
    def deliver(self,**kwargs):self.calls+=1;return emit_adapter_result(self.status)
def verifier(*args,**kwargs):return True

def command():
    return {"version":"1","command_id":"c","workspace_digest":"1"*64,"record_digest":"2"*64,
            "action_digest":"3"*64,"record_version":1,"content_digest":"4"*64,
            "recipient_digest":"5"*64,"channel_digest":"6"*64,"idempotency_key":"i",
            "policy_version":"p","prerequisite_receipt_refs":("ref",),"correlation_id":"r"}

def binding():
    return AdapterScopeBindingV1(workspace_digest="1"*64,channel_digest="6"*64,
                                 policy_version="p",required_prerequisite_receipt_ref="ref",
                                 adapter_id="generic-webhook")

def test_outbound_accepted_exactly_once():
    store=InMemoryEdgeStore(); fake=Fake("SENT_ACCEPTED"); receipt=OutboundService(store,fake,verifier,scope_bindings=(binding(),)).deliver(command(),"assert")
    assert receipt.outcome=="SENT_ACCEPTED" and receipt.delivery_attempts==1 and fake.calls==1

def test_ambiguous_is_terminal_and_blocks_blind_retry():
    store=InMemoryEdgeStore(); fake=Fake("OUTCOME_UNKNOWN"); service=OutboundService(store,fake,verifier,scope_bindings=(binding(),)); receipt=service.deliver(command(),"assert")
    assert receipt.outcome=="OUTCOME_UNKNOWN" and receipt.delivery_attempts==1
    again=service.deliver(command(),"assert")
    assert again.outcome=="OUTCOME_UNKNOWN" and fake.calls==1
