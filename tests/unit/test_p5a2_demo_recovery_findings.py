"""Focused inert probes for the independent SRC-1 through SRC-4 findings."""
from __future__ import annotations

import copy
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
import p5a2_source_demo_verify_runtime as am3  # noqa: E402


def test_am3_marker_is_distinct_and_exact(monkeypatch, tmp_path):
    path = tmp_path / "am3-attempt.json"
    monkeypatch.setattr(am3, "ATTEMPT", path)
    owner_digest, volume_id = custody.AM3_OWNER_DIGEST, custody.AM3_VOLUME_IDENTITY
    marker = {"id": am3.MARKER_ID, "status": "RESERVED_SPENT_NO_RETRY",
              "maximumVerifyRuntimeCalls": 1, "profileId": common.PROFILE,
              "ownerNonce": custody.EXPECTED_NONCE, "ownerDigest": owner_digest,
              "imageId": docker.IMAGE, "volumeIdentity": volume_id,
              "expectedDatabaseFingerprint": am3.FINGERPRINT,
              "expectedSchemaDigest": am3.SCHEMA_DIGEST,
              "expectedStateDigest": am3.STATE_DIGEST}
    def receipt(value):
        raw = json.dumps(value).encode()
        path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()
    am3.reservation(receipt(marker), owner_digest, volume_id)
    for changed in ({**marker, "id": "P5A2-SYNTHETIC-BACKEND-RECOVERY-AM2-ATTEMPT-20261027"},
                    {**marker, "maximumVerifyRuntimeCalls": True},
                    {**marker, "ownerDigest": "0" * 64},
                    {**marker, "unreviewed": 1}):
        with pytest.raises(RuntimeError, match="AM3_RESERVATION_INVALID"):
            am3.reservation(receipt(changed), owner_digest, volume_id)


def test_am3_owner_trails_and_volume_identity_are_exact(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "RUNTIME", tmp_path)
    monkeypatch.setattr(common, "OWNER", tmp_path / "owner.json")
    monkeypatch.setattr(custody, "RUNTIME", tmp_path)
    monkeypatch.setattr(custody, "OWNER", tmp_path / "owner.json")
    monkeypatch.setattr(custody, "EXPECTED_RUNTIME", tmp_path)
    monkeypatch.setattr(custody, "SECRET", tmp_path / "secrets.json")
    record = common.resource_record("PARTIAL_OWNED_FAILURE", custody.EXPECTED_NONCE,
        volume_id=common.VOLUME, image_id=docker.IMAGE.removeprefix("sha256:"),
        reason="HEALTH_FAILED")
    fc = "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"
    dee = "dee30bee86b3cd5395ca06188f586b869dbf329529701c296efa7c3b4bb49747"
    owner = {**record, "secret_ref": str(custody.SECRET),
             "creation_trail": [{"kind": "volume", "id": common.VOLUME},
                                {"kind": "container", "id": fc},
                                {"kind": "container", "id": dee, "recovery": True},
                                {"kind": "container", "id": custody.AM2_CONTAINER, "recovery": True},
                                {"kind": "api", "id": 12612}, {"kind": "web", "id": 38184}],
             "cleanup_trail": [{"kind": "container", "id": fc},
                               {"kind": "container", "id": dee, "recovery": True},
                               {"kind": "web", "id": 38184, "result": "ALREADY_ABSENT_VERIFIED", "am2": True},
                               {"kind": "api", "id": 12612, "result": "ALREADY_ABSENT_VERIFIED", "am2": True},
                               {"kind": "container", "id": custody.AM2_CONTAINER,
                                "result": "REMOVED_STOPPED_EXACT_OWNED", "am2": True}]}
    common.write_owner(owner)
    monkeypatch.setattr(custody, "digest", lambda _: custody.AM3_OWNER_DIGEST)
    monkeypatch.setattr(custody, "verified_image", lambda: None)
    monkeypatch.setattr(custody, "verified_volume", lambda _: {"Name": common.VOLUME})
    monkeypatch.setattr(custody, "volume_identity", lambda _: custody.AM3_VOLUME_IDENTITY)
    monkeypatch.setattr(custody, "inspect", lambda *_: None)
    monkeypatch.setattr(custody, "port_free", lambda *_: True)
    monkeypatch.setattr(custody, "secret_custody", lambda: None)
    assert custody.am3_preflight(custody.AM3_OWNER_DIGEST)["preflight"] == "PASS"
    altered = copy.deepcopy(common.read_owner())
    altered["cleanup_trail"][-1].pop("result")
    monkeypatch.setattr(custody, "read_owner", lambda: altered)
    with pytest.raises(RuntimeError, match="AM3_OWNER_STATE_INVALID"):
        custody.am3_owner_state(custody.AM3_OWNER_DIGEST)
    monkeypatch.setattr(custody, "read_owner", common.read_owner)
    monkeypatch.setattr(custody, "volume_identity", lambda _: "0" * 64)
    with pytest.raises(RuntimeError, match="AM3_VOLUME_CHANGED"):
        custody.am3_preflight(custody.AM3_OWNER_DIGEST)


def test_marker_exact_integer_and_isolated_attempt_path(monkeypatch, tmp_path):
    marker_path = tmp_path / "attempt.json"
    monkeypatch.setattr(recover, "ATTEMPT", marker_path)
    owner_digest = "a" * 64
    payload = {"id": "P5A2-SYNTHETIC-BACKEND-RECOVERY-AM2-ATTEMPT-20261027",
               "status": "RESERVED_SPENT_NO_RETRY", "maximumRecoveryCalls": 1,
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
    payload["maximumRecoveryCalls"] = 1
    payload["id"] = "P5A2-SYNTHETIC-BACKEND-RECOVERY-ATTEMPT-20261027"
    raw = json.dumps(payload).encode()
    marker_path.write_bytes(raw)
    with pytest.raises(RuntimeError, match="RECOVERY_RESERVATION_INVALID"):
        recover.reservation(hashlib.sha256(raw).hexdigest(), owner_digest)
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
    foreign = False
    extra_column = False
    names = inventory.expected_tables()
    native = inventory.required_columns()
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
        def fetchall(self):
            if self.current.startswith("SELECT tablename FROM pg_tables"):
                return [(name,) for name in names] + ([('foreign_table',)] if foreign else [])
            if self.current.startswith("SELECT table_name, column_name"):
                return [(table, column) for table, columns in native.items()
                        for column in columns] + ([('users', 'injected')]
                                               if extra_column else [])
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
    foreign = True
    statements.clear()
    with pytest.raises(RuntimeError, match="POST_SEED_TABLE_SET_INVALID"):
        inventory.post_seed_summary("inert", fingerprint)
    assert not any(sql.startswith('SELECT count(*)') for sql in statements)
    foreign = False
    extra_column = True
    with pytest.raises(RuntimeError, match="POST_SEED_TARGET_COLUMNS_INVALID"):
        inventory.post_seed_summary("inert", fingerprint)


def test_post_seed_digest_must_equal_committed_native_receipt():
    after = {"state_digest": "a" * 64, "record_classification": "EXACT_SEEDED"}
    receipt = {"state_digest": "a" * 64}
    inventory.verify_post_seed_digest(after, receipt)
    with pytest.raises(RuntimeError, match="POST_SEED_DIGEST_CHANGED"):
        inventory.verify_post_seed_digest(after, {"state_digest": "b" * 64})


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
