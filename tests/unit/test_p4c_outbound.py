from integration_edge.outbound import OutboundService
from integration_edge.storage import InMemoryEdgeStore

class Fake:
    evidence_eligible=False
    def __init__(self,status):self.status=status;self.calls=0
    def deliver(self,**kwargs):self.calls+=1;return {"status":self.status,"delivery_id":"d"}
def verifier(*args,**kwargs):return True

def test_outbound_accepted_exactly_once():
    store=InMemoryEdgeStore(); fake=Fake("SENT_ACCEPTED"); receipt=OutboundService(store,fake,verifier).deliver({"command_id":"c","channel":"ch"},"assert")
    assert receipt.outcome=="SENT_ACCEPTED" and receipt.delivery_attempts==1 and fake.calls==1

def test_ambiguous_is_terminal_and_blocks_blind_retry():
    store=InMemoryEdgeStore(); fake=Fake("UNKNOWN"); service=OutboundService(store,fake,verifier); receipt=service.deliver({"command_id":"c","channel":"ch"},"assert")
    assert receipt.outcome=="OUTCOME_UNKNOWN" and receipt.delivery_attempts==1
    again=service.deliver({"command_id":"c","channel":"ch"},"assert")
    assert again.outcome=="OUTCOME_UNKNOWN" and fake.calls==1
