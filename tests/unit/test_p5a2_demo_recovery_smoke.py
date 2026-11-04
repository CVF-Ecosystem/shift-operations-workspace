"""Inert proof that the native smoke uses and releases the exact transport."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import p5a2_source_demo_recovery_smoke as wrapper  # noqa: E402


def test_native_smoke_delegates_to_exact_transport_and_restores(monkeypatch):
    native = wrapper.native_smoke
    original = native.inspect
    calls = []
    def local(kind, name):
        calls.append((kind, name))
        return {"Name": name}
    monkeypatch.setattr(wrapper, "local_inspect", local)
    def native_stub(nonce):
        assert nonce == wrapper.EXPECTED_NONCE
        assert native.inspect("volume", "owned") == {"Name": "owned"}
        return {"result": "INERT_DELEGATION_ONLY"}
    monkeypatch.setattr(native, "smoke", native_stub)
    assert wrapper.smoke(wrapper.EXPECTED_NONCE) == {"result": "INERT_DELEGATION_ONLY"}
    assert calls == [("volume", "owned")]
    assert native.inspect is original


def test_native_smoke_restores_transport_on_error(monkeypatch):
    native = wrapper.native_smoke
    original = native.inspect
    monkeypatch.setattr(wrapper, "local_inspect", lambda *_: None)
    def native_error(_):
        assert native.inspect is wrapper.local_inspect
        raise RuntimeError("inert native failure")
    monkeypatch.setattr(native, "smoke", native_error)
    with pytest.raises(RuntimeError, match="inert native failure"):
        wrapper.smoke(wrapper.EXPECTED_NONCE)
    assert native.inspect is original
    with pytest.raises(RuntimeError, match="OWNER_NONCE_INVALID"):
        wrapper.smoke("0" * 64)
