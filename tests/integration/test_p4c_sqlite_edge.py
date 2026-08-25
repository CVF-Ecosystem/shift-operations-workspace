from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from integration_edge.storage import SqlEdgeStore
from integration_edge.storage.protocol import StoredEnvelope

def test_sqlite_ciphertext_nonce_and_tombstone_transaction():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    store=SqlEdgeStore(engine,create_schema=True); env=StoredEnvelope("e","ch","ep","m","a"*64,"k",b"n"*12,b"cipher",b"t"*16,b"aad")
    assert store.reserve(env).kind=="NEW" and store.get_envelope("e").ciphertext==b"cipher"
    store.tombstone("e"); saved=store.get_envelope("e"); assert saved.tombstoned and saved.ciphertext is None and saved.tag is None

def test_sqlite_key_nonce_uniqueness_fails_closed():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool); store=SqlEdgeStore(engine,create_schema=True)
    store.reserve(StoredEnvelope("1","ch","ep","m1","a"*64,"k",b"n"*12,b"c",b"t"*16,b"a"))
    try:store.reserve(StoredEnvelope("2","ch","ep","m2","b"*64,"k",b"n"*12,b"c",b"t"*16,b"a"));assert False
    except ValueError:pass
