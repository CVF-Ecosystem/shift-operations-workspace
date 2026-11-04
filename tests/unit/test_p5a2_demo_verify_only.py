"""AM3 exact-state verify guard tests; no runtime or data writes."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import p5a2_source_demo_verify_guard as guard  # noqa: E402
import p5a2_source_demo_recover as recover  # noqa: E402
import p5a2_source_demo_verify_runtime as runtime  # noqa: E402
from p5a2_source_demo_recovery_inventory import expected_tables  # noqa: E402
from workspace_api.demo import seed_recovery  # noqa: E402

NAMES = expected_tables()
COUNTS = {name: guard.TARGET.get(name, 0) for name in NAMES}


def before(**changes):
    return {
        "database": guard.DATABASE,
        "postgresql_major": 16,
        "postgresql_version": guard.POSTGRESQL_VERSION,
        "transaction_isolation": "repeatable read",
        "transaction_read_only": "on",
        "db_fingerprint": guard.FINGERPRINT,
        "schema_table_count": 31,
        "schema_digest": guard.SCHEMA_DIGEST,
        "table_names": sorted(NAMES),
        "counts": copy.deepcopy(COUNTS),
        "classification": "EXACT_SEEDED",
        "state_digest": guard.STATE_DIGEST,
        "observed_created_at": guard.FROZEN_CREATED_AT,
        **changes,
    }


def after(**changes):
    return {
        "database": guard.DATABASE,
        "postgresql_major": 16,
        "postgresql_version": guard.POSTGRESQL_VERSION,
        "transaction_isolation": "repeatable read",
        "transaction_read_only": "on",
        "db_fingerprint": guard.FINGERPRINT,
        "schema_digest": guard.SCHEMA_DIGEST,
        "counts": copy.deepcopy(COUNTS),
        "state_digest": guard.STATE_DIGEST,
        "record_classification": "EXACT_SEEDED",
        **changes,
    }


def _forbidden(*_args, **_kwargs):
    raise AssertionError("verify-only path invoked a seed writer")


def _inert_runtime(monkeypatch, events, post=None):
    from contextlib import nullcontext
    import p5a2_source_demo_start as start

    monkeypatch.setattr(runtime, "owner_lock", lambda: nullcontext())
    monkeypatch.setattr(runtime, "am3_preflight", lambda _owner: {
        "volume_identity": "inert-volume-identity"})
    monkeypatch.setattr(runtime, "reservation", lambda *_args: events.append("marker"))
    monkeypatch.setattr(runtime, "_node_ready", lambda: events.append("node"))
    monkeypatch.setattr(runtime, "am3_owner_state", lambda _owner: {
        "creation_trail": [], "cleanup_trail": []})
    monkeypatch.setattr(runtime, "secret_file", lambda: {"viewer_password": "inert"})
    monkeypatch.setattr(runtime, "child_settings", lambda *_args: (
        "postgresql+psycopg://inert", {}))
    monkeypatch.setattr(runtime, "create_container", lambda *_args: (
        events.append("container") or "b" * 64))
    monkeypatch.setattr(runtime, "verified_container", lambda *_args: None)
    monkeypatch.setattr(runtime, "verified_volume", lambda *_args: {})
    monkeypatch.setattr(runtime, "volume_identity", lambda _volume: "inert-volume-identity")
    monkeypatch.setattr(start, "wait_db", lambda _dsn: events.append("db_ready"))
    monkeypatch.setattr(runtime, "inventory", lambda *_args: (
        events.append("inventory") or before()))
    monkeypatch.setattr(runtime, "post_seed_summary", lambda *_args: (
        events.append("post_summary") or (after() if post is None else post)))
    monkeypatch.setattr(runtime, "start_services", lambda *_args: events.append("services"))
    monkeypatch.setattr(runtime, "resource_record", lambda _outcome, _nonce, **resource: {
        "profile_id": "P5A2-SOURCE-DEMO-LOCAL-1", **resource})
    monkeypatch.setattr(runtime, "replace_lifecycle", lambda *_args: None)
    monkeypatch.setattr(runtime, "write_owner", lambda _state: events.append("owner_write"))
    monkeypatch.setattr(runtime, "_adopt_lost_create", lambda *_args: True)
    monkeypatch.setattr(runtime, "_cleanup", lambda *_args: True)
    monkeypatch.setattr(runtime, "_record_failure", lambda *_args, **_kw: None)
    monkeypatch.setattr(recover, "_native_seed", _forbidden)
    monkeypatch.setattr(seed_recovery, "seed_transaction", _forbidden)


def test_exact_snapshots_emit_registered_zero_write_receipt_without_seed(monkeypatch):
    monkeypatch.setattr(recover, "_native_seed", _forbidden)
    monkeypatch.setattr(seed_recovery, "seed_transaction", _forbidden)
    calls = []

    def post_summary():
        calls.append("post_summary")
        return after()

    receipt, observed_after = guard.verify_only(before(), post_summary)
    assert calls == ["post_summary"]
    assert observed_after == after()
    assert receipt["result"] == "VERIFY"
    assert receipt["state_digest"] == guard.STATE_DIGEST
    assert receipt["db_fingerprint"] == guard.FINGERPRINT
    assert receipt["family_record"] == seed_recovery.family_record(
        "VERIFY", guard.FINGERPRINT)
    assert receipt["family_record"]["outcome"] == "EXACT_VERIFIED"
    assert receipt["family_record"]["durable_application_writes"] == 0


def test_runtime_reads_both_exact_snapshots_before_services(monkeypatch):
    events = []
    _inert_runtime(monkeypatch, events)
    result = runtime.verify_runtime(runtime.AM3_OWNER_DIGEST, "a" * 64)
    assert events.count("inventory") == 1
    assert events.count("post_summary") == 1
    assert events.count("services") == 1
    assert events.index("inventory") < events.index("post_summary")
    assert events.index("post_summary") < events.index("services")
    assert events[-1] == "owner_write"
    assert result["verification_family_record"]["outcome"] == "EXACT_VERIFIED"
    assert result["verification_family_record"]["durable_application_writes"] == 0
    assert result["application_data_writes"] == 0


def test_runtime_post_snapshot_mismatch_never_starts_services(monkeypatch):
    events = []
    changed = after(state_digest="0" * 64)
    _inert_runtime(monkeypatch, events, changed)
    with pytest.raises(RuntimeError, match="AM3_VERIFY_RUNTIME_FAILED_VERIFY_ONLY_GUARD"):
        runtime.verify_runtime(runtime.AM3_OWNER_DIGEST, "a" * 64)
    assert events.count("inventory") == 1
    assert events.count("post_summary") == 1
    assert "services" not in events


@pytest.mark.parametrize("damage", [
    "empty", "sole_timestamp", "partial", "foreign", "fingerprint",
    "schema", "state_digest", "counts", "table_names", "table_count",
    "created_at_drift", "created_at_missing", "version", "read_write",
])
def test_nonexact_prestate_refuses_before_second_read(damage):
    snapshot = before()
    if damage == "empty":
        snapshot["classification"] = "EMPTY_COMPATIBLE"
        snapshot["counts"] = {name: 0 for name in NAMES}
    elif damage == "sole_timestamp":
        snapshot["classification"] = "SOLE_CREATED_AT_MISMATCH"
        snapshot["observed_created_at"] = "2024-01-02T00:00:00+00:00"
    elif damage == "partial":
        snapshot["counts"]["reports"] -= 1
    elif damage == "foreign":
        snapshot["counts"]["audit_records"] = 1
    elif damage == "fingerprint":
        snapshot["db_fingerprint"] = "0" * 64
    elif damage == "schema":
        snapshot["schema_digest"] = "0" * 64
    elif damage == "state_digest":
        snapshot["state_digest"] = "0" * 64
    elif damage == "counts":
        snapshot["counts"]["shifts"] += 1
    elif damage == "table_names":
        snapshot["table_names"].pop()
    elif damage == "table_count":
        snapshot["schema_table_count"] -= 1
    elif damage == "created_at_drift":
        snapshot["observed_created_at"] = "2024-01-02T00:00:00+00:00"
    elif damage == "created_at_missing":
        snapshot["observed_created_at"] = None
    elif damage == "version":
        snapshot["postgresql_version"] = "PostgreSQL 16.15 (different build)"
    else:
        snapshot["transaction_read_only"] = "off"
    calls = []
    with pytest.raises(RuntimeError, match="VERIFY_PRESTATE_INVALID"):
        guard.verify_only(snapshot, lambda: calls.append("post_summary") or after())
    assert calls == []


@pytest.mark.parametrize("damage", [
    "empty", "sole_timestamp", "partial", "foreign", "fingerprint",
    "schema", "state_digest", "counts", "classification", "extra_field",
    "version",
])
def test_changed_poststate_refuses_after_exactly_one_second_read(damage):
    snapshot = after()
    if damage == "empty":
        snapshot["record_classification"] = "EMPTY_COMPATIBLE"
        snapshot["counts"] = {name: 0 for name in NAMES}
    elif damage == "sole_timestamp":
        snapshot["record_classification"] = "SOLE_CREATED_AT_MISMATCH"
    elif damage == "partial":
        snapshot["counts"]["reports"] -= 1
    elif damage == "foreign":
        snapshot["counts"]["audit_records"] = 1
    elif damage == "fingerprint":
        snapshot["db_fingerprint"] = "0" * 64
    elif damage == "schema":
        snapshot["schema_digest"] = "0" * 64
    elif damage == "state_digest":
        snapshot["state_digest"] = "0" * 64
    elif damage == "counts":
        snapshot["counts"]["shifts"] += 1
    elif damage == "classification":
        snapshot["record_classification"] = "UNKNOWN"
    elif damage == "version":
        snapshot["postgresql_version"] = "PostgreSQL 16.15 (different build)"
    else:
        snapshot["unexpected"] = True
    calls = []

    def post_summary():
        calls.append("post_summary")
        return snapshot

    with pytest.raises(RuntimeError, match="VERIFY_POSTSTATE_INVALID"):
        guard.verify_only(before(), post_summary)
    assert calls == ["post_summary"]
