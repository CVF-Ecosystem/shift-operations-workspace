"""P4-E sender-token key authority tests (SPEC R19; Work Order carry-forward
F4): dual-read window, cryptographic erasure, and the sanitized
`TOKEN_KEY_RETIREMENT_BLOCKED` readiness record's exclusive ownership."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from integration_edge.verification.sender_keys import (
    DUAL_READ_WINDOW,
    SenderTokenKeyAuthority,
    TokenKeyRetirementReadinessV1,
)


class _MutableClock:
    def __init__(self, start: datetime) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now


class _FakeSecretStore:
    def __init__(self, *, delete_ok=True, purge_ok=True) -> None:
        self.delete_ok, self.purge_ok = delete_ok, purge_ok
        self.deleted, self.purged = [], []

    def delete_wrapping_key(self, key_id, key_version):
        self.deleted.append((key_id, key_version))
        return self.delete_ok

    def purge_cache(self, key_id, key_version):
        self.purged.append((key_id, key_version))
        return self.purge_ok


def test_active_key_and_resolve_current_version():
    store = _FakeSecretStore()
    authority = SenderTokenKeyAuthority(store)
    authority.activate("k1", "1", b"0" * 32)
    key_id, key_version, secret = authority.active_key()
    assert (key_id, key_version) == ("k1", "1")
    assert authority.resolve_key("k1", "1") == secret


def test_resolve_unknown_key_returns_none():
    authority = SenderTokenKeyAuthority(_FakeSecretStore())
    authority.activate("k1", "1", b"0" * 32)
    assert authority.resolve_key("k9", "9") is None


def test_previous_version_resolves_within_dual_read_window():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = _MutableClock(start)
    authority = SenderTokenKeyAuthority(_FakeSecretStore(), clock=clock)
    authority.activate("k1", "1", b"0" * 32)
    authority.activate("k2", "2", b"1" * 32)
    clock.now = start + timedelta(hours=23)
    assert authority.resolve_key("k1", "1") is not None


def test_previous_version_expires_after_dual_read_window():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = _MutableClock(start)
    authority = SenderTokenKeyAuthority(_FakeSecretStore(), clock=clock)
    authority.activate("k1", "1", b"0" * 32)
    authority.activate("k2", "2", b"1" * 32)
    clock.now = start + DUAL_READ_WINDOW + timedelta(seconds=1)
    assert authority.resolve_key("k1", "1") is None


def test_retire_previous_blocked_while_dual_read_window_active():
    authority = SenderTokenKeyAuthority(_FakeSecretStore())
    authority.activate("k1", "1", b"0" * 32)
    authority.activate("k2", "2", b"1" * 32)
    readiness = authority.retire_previous()
    assert readiness.outcome == "TOKEN_KEY_RETIREMENT_BLOCKED"
    assert readiness.reason == "DUAL_READ_WINDOW_ACTIVE"


def test_retire_previous_succeeds_after_window_and_erases_secret():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = _MutableClock(start)
    store = _FakeSecretStore()
    authority = SenderTokenKeyAuthority(store, clock=clock)
    authority.activate("k1", "1", b"0" * 32)
    authority.activate("k2", "2", b"1" * 32)
    clock.now = start + DUAL_READ_WINDOW + timedelta(seconds=1)
    readiness = authority.retire_previous()
    assert readiness.outcome == "RETIRED"
    assert store.deleted == [("k1", "1")]
    assert store.purged == [("k1", "1")]
    assert authority.resolve_key("k1", "1") is None


def test_retire_previous_blocked_on_erasure_failure():
    """SPEC R19: failure to erase or purge fails the rotation closed and
    blocks retirement. The dual-read window (a lookup-validity control) and
    erasure (a storage control) are independent: once the window has
    expired, lookups refuse regardless of erasure outcome - a blocked
    retirement must not silently re-extend the window."""
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = _MutableClock(start)
    store = _FakeSecretStore(delete_ok=False)
    authority = SenderTokenKeyAuthority(store, clock=clock)
    authority.activate("k1", "1", b"0" * 32)
    authority.activate("k2", "2", b"1" * 32)
    clock.now = start + DUAL_READ_WINDOW + timedelta(seconds=1)
    readiness = authority.retire_previous()
    assert readiness.outcome == "TOKEN_KEY_RETIREMENT_BLOCKED"
    assert readiness.reason == "SECRET_ERASURE_FAILED"
    # The blocked retirement did not erase the internal key entry (the
    # secret bytes are still tracked pending a successful retry), even
    # though window-expired lookups correctly still refuse it.
    assert ("k1", "1") in authority._keys


def test_retire_previous_blocked_on_purge_failure():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = _MutableClock(start)
    store = _FakeSecretStore(purge_ok=False)
    authority = SenderTokenKeyAuthority(store, clock=clock)
    authority.activate("k1", "1", b"0" * 32)
    authority.activate("k2", "2", b"1" * 32)
    clock.now = start + DUAL_READ_WINDOW + timedelta(seconds=1)
    readiness = authority.retire_previous()
    assert readiness.outcome == "TOKEN_KEY_RETIREMENT_BLOCKED"
    assert readiness.reason == "SECRET_ERASURE_FAILED"


def test_retire_previous_blocked_when_no_previous_key():
    authority = SenderTokenKeyAuthority(_FakeSecretStore())
    authority.activate("k1", "1", b"0" * 32)
    readiness = authority.retire_previous()
    assert readiness.outcome == "TOKEN_KEY_RETIREMENT_BLOCKED"
    assert readiness.reason == "NO_PREVIOUS_KEY"


def test_readiness_record_is_sanitized_no_secret_bytes():
    """Only non-secret key id/version, attempted-at, closed reason, and an
    opaque correlation id - never a secret or raw sender value."""
    fields = set(TokenKeyRetirementReadinessV1.model_fields)
    forbidden = {"secret", "key_secret", "raw_sender", "wrapping_key", "action", "aggregate_id"}
    assert fields.isdisjoint(forbidden)


def test_activation_rejects_short_secret():
    authority = SenderTokenKeyAuthority(_FakeSecretStore())
    try:
        authority.activate("k1", "1", b"short")
        assert False, "should have raised"
    except ValueError:
        pass


def test_token_key_retirement_blocked_not_emitted_by_any_p4e_matrix():
    """Carry-forward F4: TOKEN_KEY_RETIREMENT_BLOCKED is neither a mapping
    action nor a Workspace management API receipt."""
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "docs" / "cvf" / "invariants"
    for name in ("p4e-mapping-action-outcomes.json", "p4e-identity-resolution-outcomes.json",
                 "p4e-placement-outcomes.json"):
        matrix_text = (root / name).read_text(encoding="utf-8")
        assert "TOKEN_KEY_RETIREMENT_BLOCKED" not in matrix_text, name
