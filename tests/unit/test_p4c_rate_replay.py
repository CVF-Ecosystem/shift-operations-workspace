from integration_edge.storage import InMemoryEdgeStore
from integration_edge.storage.protocol import StoredEnvelope

def _env(i,digest,nonce):return StoredEnvelope(i,"ch","ep","external",digest,"k",nonce,b"cipher",b"t"*16,b"aad")

def test_duplicate_links_first_without_second_raw_copy():
    store=InMemoryEdgeStore(); first=store.reserve(_env("1","a"*64,b"1"*12)); duplicate=store.reserve(_env("2","a"*64,b"2"*12))
    assert first.kind=="NEW" and duplicate.kind=="DUPLICATE" and duplicate.original_envelope_id=="1" and len(store.envelopes)==1

def test_collision_preserves_original_and_quarantines_distinct_raw():
    store=InMemoryEdgeStore(); store.reserve(_env("1","a"*64,b"1"*12)); result=store.reserve(_env("2","b"*64,b"2"*12))
    assert result.kind=="COLLISION" and result.original_envelope_id=="1" and result.quarantine.envelope_id=="2" and len(store.envelopes)==2
