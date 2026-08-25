import pytest
from integration_edge import InMemoryKeyRegistry,decrypt_envelope,encrypt_envelope

def test_aes256_gcm_roundtrip_and_tamper():
    keys=InMemoryKeyRegistry({"k":b"k"*32},active_key_id="k"); env=encrypt_envelope(b"secret",aad=b"aad",key_registry=keys,nonce=b"n"*12)
    assert decrypt_envelope(env,aad=b"aad",key_registry=keys)==b"secret"
    with pytest.raises(Exception):decrypt_envelope(env,aad=b"bad",key_registry=keys)

def test_nonce_reuse_and_generator_failure_refuse():
    keys=InMemoryKeyRegistry({"k":b"k"*32},active_key_id="k"); encrypt_envelope(b"a",aad=b"x",key_registry=keys,nonce=b"1"*12)
    with pytest.raises(Exception):encrypt_envelope(b"b",aad=b"x",key_registry=keys,nonce=b"1"*12)
    with pytest.raises(Exception):encrypt_envelope(b"b",aad=b"x",key_registry=keys,nonce_factory=lambda _:(_ for _ in ()).throw(RuntimeError()))
