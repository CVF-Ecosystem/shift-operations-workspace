"""AM4 owner, marker and verify-only entry contract; inert only."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import p5a2_source_demo_common as common  # noqa: E402
import p5a2_source_demo_recover as legacy  # noqa: E402
import p5a2_source_demo_recovery_custody as custody  # noqa: E402
import p5a2_source_demo_recovery_docker as docker  # noqa: E402
import p5a2_source_demo_recovery_inventory as inventory  # noqa: E402
import p5a2_source_demo_verify_am4 as am4  # noqa: E402
import p5a2_source_demo_verify_am4_custody as am4_custody  # noqa: E402
import p5a2_source_demo_verify_guard as guard  # noqa: E402
from workspace_api.demo import seed_recovery  # noqa: E402

ADMISSION = json.loads((ROOT / "docs/decisions/P5A2_UI_COMPLETION_AM4_ADMISSION_2026-10-27.json").read_text())
RETAINED = ADMISSION["retainedOwner"]
NAMES = inventory.expected_tables()
COUNTS = {name: guard.TARGET.get(name, 0) for name in NAMES}


def _owner():
    record = common.resource_record(
        "PARTIAL_OWNED_FAILURE", custody.EXPECTED_NONCE,
        volume_id=common.VOLUME, image_id=docker.IMAGE.removeprefix("sha256:"),
        reason="HEALTH_FAILED")
    return {**record, "secret_ref": str(custody.SECRET),
            "creation_trail": copy.deepcopy(RETAINED["creationTrail"]),
            "cleanup_trail": copy.deepcopy(RETAINED["cleanupTrail"])}


def _before(**changes):
    return {"database": guard.DATABASE, "postgresql_major": 16,
            "postgresql_version": guard.POSTGRESQL_VERSION,
            "transaction_isolation": "repeatable read",
            "transaction_read_only": "on", "db_fingerprint": guard.FINGERPRINT,
            "schema_table_count": 31, "schema_digest": guard.SCHEMA_DIGEST,
            "table_names": sorted(NAMES), "counts": copy.deepcopy(COUNTS),
            "classification": "EXACT_SEEDED", "state_digest": guard.STATE_DIGEST,
            "observed_created_at": guard.FROZEN_CREATED_AT, **changes}


def _after(**changes):
    return {"database": guard.DATABASE, "postgresql_major": 16,
            "postgresql_version": guard.POSTGRESQL_VERSION,
            "transaction_isolation": "repeatable read",
            "transaction_read_only": "on", "db_fingerprint": guard.FINGERPRINT,
            "schema_digest": guard.SCHEMA_DIGEST, "counts": copy.deepcopy(COUNTS),
            "state_digest": guard.STATE_DIGEST,
            "record_classification": "EXACT_SEEDED", **changes}


def _forbidden(*_args, **_kwargs):
    raise AssertionError("AM4 verify-only path invoked a seed writer")


def _owner_fixture(monkeypatch, tmp_path, owner=None):
    owner = _owner() if owner is None else owner
    path = tmp_path / "owner.json"
    path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(am4_custody, "RUNTIME", tmp_path)
    monkeypatch.setattr(am4_custody, "EXPECTED_RUNTIME", tmp_path)
    monkeypatch.setattr(am4_custody, "OWNER", path)
    monkeypatch.setattr(am4_custody, "read_owner", lambda: owner)
    digest_calls = []

    def digest(value):
        digest_calls.append(value)
        return RETAINED["ownerDigest"] if value == owner else "0" * 64

    monkeypatch.setattr(am4_custody, "digest", digest)
    return owner, digest_calls


def test_am4_owner_binds_exact_admitted_metadata_and_trails(monkeypatch, tmp_path):
    owner, digest_calls = _owner_fixture(monkeypatch, tmp_path)
    assert len(owner["creation_trail"]) == 9
    assert len(owner["cleanup_trail"]) == 8
    assert am4_custody.AM4_OWNER_DIGEST == RETAINED["ownerDigest"]
    assert am4_custody.am4_owner_state(am4_custody.AM4_OWNER_DIGEST) == owner
    assert digest_calls == [owner]
    with pytest.raises(RuntimeError, match="AM4_OWNER_DIGEST_INVALID"):
        am4_custody.am4_owner_state(custody.AM3_OWNER_DIGEST)

    changed = copy.deepcopy(owner)
    changed["cleanup_trail"][-1]["result"] = "OTHER"
    monkeypatch.setattr(am4_custody, "read_owner", lambda: changed)
    with pytest.raises(RuntimeError, match="AM4_OWNER_STATE_INVALID"):
        am4_custody.am4_owner_state(am4_custody.AM4_OWNER_DIGEST)


def test_am4_preflight_checks_volume_without_reading_secret_contents(monkeypatch, tmp_path):
    _owner_fixture(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(am4_custody, "verified_image", lambda: calls.append("image"))
    monkeypatch.setattr(am4_custody, "verified_volume", lambda _nonce: {})
    monkeypatch.setattr(am4_custody, "volume_identity",
                        lambda _volume: am4_custody.AM4_VOLUME_IDENTITY)
    monkeypatch.setattr(am4_custody, "inspect", lambda *_args: None)
    monkeypatch.setattr(am4_custody, "port_free", lambda _port: True)
    monkeypatch.setattr(am4_custody, "secret_custody", lambda: calls.append("secret_custody"))
    result = am4_custody.am4_preflight(am4_custody.AM4_OWNER_DIGEST)
    assert result["preflight"] == "PASS"
    assert result["volume_identity"] == am4_custody.AM4_VOLUME_IDENTITY
    assert calls == ["image", "secret_custody"]

    monkeypatch.setattr(am4_custody, "volume_identity", lambda _volume: "0" * 64)
    calls.clear()
    with pytest.raises(RuntimeError, match="AM4_VOLUME_CHANGED"):
        am4_custody.am4_preflight(am4_custody.AM4_OWNER_DIGEST)
    assert calls == ["image"]


def _marker():
    return {"id": am4.MARKER_ID, "status": "RESERVED_SPENT_NO_RETRY",
            "maximumVerifyRuntimeCalls": 1, "profileId": common.PROFILE,
            "ownerNonce": custody.EXPECTED_NONCE,
            "ownerDigest": am4_custody.AM4_OWNER_DIGEST, "imageId": docker.IMAGE,
            "volumeIdentity": am4_custody.AM4_VOLUME_IDENTITY,
            "expectedDatabaseFingerprint": guard.FINGERPRINT,
            "expectedSchemaDigest": guard.SCHEMA_DIGEST,
            "expectedStateDigest": guard.STATE_DIGEST}


def _write_marker(path, marker):
    raw = json.dumps(marker, sort_keys=True).encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def test_am4_marker_is_unique_exact_and_never_accepts_predecessor(monkeypatch, tmp_path):
    path = tmp_path / "attempt.json"
    monkeypatch.setattr(am4, "ATTEMPT", path)
    marker = _marker()
    assert set(marker) == am4.MARKER_KEYS
    am4.reservation(_write_marker(path, marker), marker["ownerDigest"],
                    marker["volumeIdentity"])
    changes = [
        {"id": "P5A2-VERIFY-ONLY-AM3-ATTEMPT-20261027"},
        {"maximumVerifyRuntimeCalls": True},
        {"maximumVerifyRuntimeCalls": 2},
        {"ownerDigest": "0" * 64}, {"volumeIdentity": "0" * 64},
        {"expectedDatabaseFingerprint": "0" * 64},
        {"expectedSchemaDigest": "0" * 64}, {"expectedStateDigest": "0" * 64},
        {"unreviewed": True},
    ]
    for change in changes:
        altered = {**marker, **change}
        with pytest.raises(RuntimeError, match="AM4_RESERVATION_INVALID"):
            am4.reservation(_write_marker(path, altered), marker["ownerDigest"],
                            marker["volumeIdentity"])
    sha = _write_marker(path, marker)
    with pytest.raises(RuntimeError, match="AM4_RESERVATION_CHANGED"):
        am4.reservation("0" * 64, marker["ownerDigest"], marker["volumeIdentity"])
    path.unlink()
    with pytest.raises(RuntimeError, match="AM4_RESERVATION_ABSENT"):
        am4.reservation(sha, marker["ownerDigest"], marker["volumeIdentity"])


def _patch_runtime(monkeypatch, events, post=None, pre=None):
    import p5a2_source_demo_start as start

    monkeypatch.setattr(am4, "owner_lock", lambda: nullcontext())
    monkeypatch.setattr(am4, "am4_preflight", lambda _owner: {
        "volume_identity": am4_custody.AM4_VOLUME_IDENTITY})
    monkeypatch.setattr(am4, "reservation", lambda *_args: events.append("marker"))
    monkeypatch.setattr(am4, "_node_ready", lambda: events.append("node"))
    monkeypatch.setattr(am4, "am4_owner_state", lambda _owner: {
        "creation_trail": [], "cleanup_trail": []})
    monkeypatch.setattr(am4, "secret_file", lambda: {"viewer_password": "inert"})
    monkeypatch.setattr(am4, "child_settings", lambda *_args: (
        "postgresql+psycopg://inert", {}))
    monkeypatch.setattr(am4, "create_container", lambda *_args: (
        events.append("container") or "b" * 64))
    monkeypatch.setattr(am4, "verified_container", lambda *_args: None)
    monkeypatch.setattr(am4, "verified_volume", lambda *_args: {})
    monkeypatch.setattr(am4, "volume_identity",
                        lambda _volume: am4_custody.AM4_VOLUME_IDENTITY)
    monkeypatch.setattr(start, "wait_db", lambda _dsn: events.append("db_ready"))
    monkeypatch.setattr(am4, "inventory", lambda *_args: (
        events.append("inventory") or (_before() if pre is None else pre)))
    monkeypatch.setattr(am4, "post_seed_summary", lambda *_args: (
        events.append("post_summary") or (_after() if post is None else post)))
    monkeypatch.setattr(am4, "start_services", lambda *_args: events.append("services"))
    monkeypatch.setattr(am4, "resource_record", lambda _outcome, _nonce, **resources: {
        "profile_id": common.PROFILE, **resources})
    monkeypatch.setattr(am4, "replace_lifecycle", lambda *_args: None)
    monkeypatch.setattr(am4, "write_owner", lambda _state: events.append("owner_write"))
    monkeypatch.setattr(am4, "_adopt_lost_create", lambda *_args: True)
    monkeypatch.setattr(am4, "_cleanup", lambda *_args: True)
    monkeypatch.setattr(am4, "_record_failure", lambda *_args, **_kw: events.append("cleanup"))
    monkeypatch.setattr(legacy, "_native_seed", _forbidden)
    monkeypatch.setattr(seed_recovery, "seed_transaction", _forbidden)


def test_am4_runtime_double_read_and_seed_canaries_precede_services(monkeypatch):
    events = []
    _patch_runtime(monkeypatch, events)
    result = am4.verify_runtime(am4_custody.AM4_OWNER_DIGEST, "a" * 64)
    assert events.count("inventory") == events.count("post_summary") == 1
    assert events.index("inventory") < events.index("post_summary") < events.index("services")
    assert result["verification_family_record"]["outcome"] == "EXACT_VERIFIED"
    assert result["verification_family_record"]["durable_application_writes"] == 0
    assert result["application_data_writes"] == 0


@pytest.mark.parametrize("drift", ["pre", "post"])
def test_am4_snapshot_drift_refuses_services_with_fixed_failure_stage(monkeypatch, drift):
    events = []
    pre, post = _before(), _after()
    if drift == "pre":
        pre["state_digest"] = "0" * 64
    else:
        post["schema_digest"] = "0" * 64
    _patch_runtime(monkeypatch, events, post=post, pre=pre)
    with pytest.raises(RuntimeError, match="AM4_VERIFY_RUNTIME_FAILED_VERIFY_ONLY_GUARD"):
        am4.verify_runtime(am4_custody.AM4_OWNER_DIGEST, "a" * 64)
    assert "services" not in events
    assert events[-1] == "cleanup"


def test_am4_entry_clean_child_import_has_no_config_or_database(tmp_path):
    from p5a2_source_demo_bootstrap import isolated_child_env

    env = isolated_child_env()
    env["PYTHONPATH"] = str(ROOT / "scripts") + os.pathsep + env["PYTHONPATH"]
    code = ("import sys; import p5a2_source_demo_verify_am4; "
            "assert 'workspace_api.config' not in sys.modules; "
            "assert 'psycopg' not in sys.modules")
    proc = subprocess.run([sys.executable, "-P", "-c", code], cwd=tmp_path,
                          env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
