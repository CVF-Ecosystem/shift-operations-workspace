"""Focused inert probes for the independent SRC-1 through SRC-4 findings."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import p5a2_source_demo_common as common  # noqa: E402
import p5a2_source_demo_recover as recover  # noqa: E402
import p5a2_source_demo_recovery_custody as custody  # noqa: E402
import p5a2_source_demo_recovery_docker as docker  # noqa: E402
import p5a2_source_demo_recovery_inventory as inventory  # noqa: E402


def test_marker_exact_integer_and_isolated_attempt_path(monkeypatch, tmp_path):
    marker_path = tmp_path / "attempt.json"
    monkeypatch.setattr(recover, "ATTEMPT", marker_path)
    owner_digest = "a" * 64
    payload = {"status": "RESERVED_SPENT_NO_RETRY", "maximumRecoveryCalls": 1,
               "profileId": common.PROFILE, "ownerNonce": custody.EXPECTED_NONCE,
               "ownerDigest": owner_digest, "imageId": docker.IMAGE}
    for value, accepted in ((1, True), (True, False), (1.0, False), (2, False)):
        payload["maximumRecoveryCalls"] = value
        raw = json.dumps(payload).encode()
        marker_path.write_bytes(raw)
        sha = hashlib.sha256(raw).hexdigest()
        if accepted:
            recover.reservation(sha, owner_digest)
        else:
            with pytest.raises(RuntimeError, match="RECOVERY_RESERVATION_INVALID"):
                recover.reservation(sha, owner_digest)
    marker_path.unlink()
    with pytest.raises(RuntimeError, match="RECOVERY_RESERVATION_ABSENT"):
        recover.reservation("0" * 64, owner_digest)


def test_lost_create_receipt_adopts_only_exact_container(monkeypatch):
    cid = "a" * 64
    monkeypatch.setattr(docker, "docker", lambda *a, **k: "invalid-cid")
    with pytest.raises(RuntimeError, match="CONTAINER_CREATE_ID_INVALID"):
        docker.create_container(custody.EXPECTED_NONCE)
    monkeypatch.setattr(recover, "inspect", lambda *_: {"Id": cid})
    monkeypatch.setattr(recover, "verified_container", lambda *a, **k: {"Id": cid})
    monkeypatch.setattr(recover, "verified_volume", lambda *_: {"Name": common.VOLUME})
    monkeypatch.setattr(recover, "volume_identity", lambda *_: "same-volume")
    resource = {"volume_id": common.VOLUME, "container_id": None,
                "api_pid": None, "web_pid": None}
    state = {"creation_trail": [], "cleanup_trail": []}
    assert recover._adopt_lost_create(resource, state, "same-volume")
    assert resource["container_id"] == cid
    assert state["creation_trail"] == [{"kind": "container", "id": cid,
                                        "recovery": True, "receipt": "LOST"}]
    removed = []
    monkeypatch.setattr(recover, "remove_container", lambda *a: removed.append(a))
    assert recover._cleanup(resource, state, {})
    assert removed == [(custody.EXPECTED_NONCE, cid)]
    assert resource["container_id"] is None


def test_lost_create_foreign_container_is_not_removed(monkeypatch, tmp_path):
    monkeypatch.setattr(recover, "inspect", lambda *_: {"Id": "a" * 64})
    monkeypatch.setattr(recover, "verified_container", lambda *a, **k:
                        (_ for _ in ()).throw(RuntimeError("foreign")))
    monkeypatch.setattr(recover, "verified_volume", lambda *_: {"Name": common.VOLUME})
    resource = {"volume_id": common.VOLUME, "container_id": None,
                "api_pid": None, "web_pid": None}
    state = {"creation_trail": [], "cleanup_trail": []}
    assert not recover._adopt_lost_create(resource, state, "same-volume")
    assert resource["container_id"] is None
    assert state["recovery_unknown_custody"] == "CONTAINER_IDENTITY_UNVERIFIED"
    monkeypatch.setattr(recover, "remove_container", lambda *a: pytest.fail("foreign remove"))
    assert recover._cleanup(resource, state, {})
    monkeypatch.setattr(common, "RUNTIME", tmp_path)
    monkeypatch.setattr(common, "OWNER", tmp_path / "owner.json")
    old = common.resource_record("PARTIAL_OWNED_FAILURE", custody.EXPECTED_NONCE,
        volume_id=common.VOLUME, image_id=docker.IMAGE.removeprefix("sha256:"),
        reason="SEED_FAILED")
    state.update(old)
    recover._record_failure(old, state, resource, "CONTAINER_CREATE", False)
    loaded = common.read_owner()
    assert loaded["total_owned_count"] == 1
    assert loaded["recovery_unknown_custody"] == "CONTAINER_IDENTITY_UNVERIFIED"
    assert loaded["recovery_cleanup_verified"] is False


def test_post_seed_summary_returns_actual_safe_mode_version_and_counts(monkeypatch):
    statements = []
    fingerprint = common.digest({"database": inventory.DATABASE,
                                 "system_identifier": "12345"})
    class Cursor:
        current = ""
        def __enter__(self): return self
        def __exit__(self, *_): return None
        def execute(self, sql): self.current = sql; statements.append(sql)
        def fetchone(self):
            if self.current == "SHOW transaction_isolation": return ("repeatable read",)
            if self.current == "SHOW transaction_read_only": return ("on",)
            if self.current.startswith("SELECT current_database"): return (inventory.DATABASE, "PostgreSQL 16.15")
            if self.current.startswith("SELECT system_identifier"): return (12345,)
            if self.current.startswith('SELECT count(*) FROM "'):
                name = self.current.split('"')[1]
                return (inventory.TARGET.get(name, 0),)
            raise AssertionError(self.current)
    class Connection:
        def __enter__(self): return self
        def __exit__(self, *_): return None
        def cursor(self): return Cursor()
    monkeypatch.setitem(sys.modules, "psycopg", SimpleNamespace(connect=lambda *a, **k: Connection()))
    result = inventory.post_seed_summary("inert", fingerprint)
    assert result["database"] == inventory.DATABASE
    assert result["postgresql_version"] == "PostgreSQL 16.15"
    assert result["transaction_isolation"] == "repeatable read"
    assert result["transaction_read_only"] == "on"
    assert result["db_fingerprint"] == fingerprint
    assert result["counts"]["reports"] == 37
    assert statements[0] == "BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY"
    assert statements[-1] == "ROLLBACK"


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL test")
def test_explicit_everyone_read_grant_refuses_private_acl(tmp_path):
    folder = tmp_path / "private"
    folder.mkdir()
    file = folder / "inert.txt"
    file.write_text("inert")
    user = os.environ["USERNAME"]
    for path, grant in ((folder, f"{user}:(OI)(CI)F"), (file, f"{user}:F")):
        result = subprocess.run(["icacls", str(path), "/inheritance:r", "/grant:r", grant],
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
    assert custody.windows_private_acl(folder, file)
    result = subprocess.run(["icacls", str(file), "/grant", "*S-1-3-4:(F)"],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    assert custody.windows_private_acl(folder, file)
    result = subprocess.run(["icacls", str(file), "/grant", "*S-1-1-0:(R)"],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    assert not custody.windows_private_acl(folder, file)
