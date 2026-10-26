"""Inert recovery refusal and exact command tests; no physical effects."""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import p5a2_source_demo_recovery_docker as docker  # noqa: E402
import p5a2_source_demo_recovery_inventory as inventory  # noqa: E402
import p5a2_source_demo_recover as recover  # noqa: E402
import p5a2_source_demo_common as common  # noqa: E402
import p5a2_source_demo_recovery_custody as custody  # noqa: E402


def test_expected_migration_set_and_partial_rows_refuse():
    names = inventory.expected_tables()
    assert len(names) == 31
    assert set(inventory.TARGET) < names
    empty = {name: 0 for name in names}
    assert inventory.classify_counts(empty) == "EMPTY_COMPATIBLE"
    exact = {name: inventory.TARGET.get(name, 0) for name in names}
    assert inventory.classify_counts(exact) == "EXACT_SEEDED"
    partial = {**exact, "reports": 36}
    with pytest.raises(RuntimeError, match="PARTIAL_OR_FOREIGN_DATA"):
        inventory.classify_counts(partial)
    with pytest.raises(RuntimeError, match="PARTIAL_OR_FOREIGN_DATA"):
        inventory.classify_counts({**exact, "audit_records": 1})


def test_inspect_absence_is_distinct_from_daemon_error(monkeypatch):
    calls = []
    def fake_run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=1, stdout="", stderr="No such volume: absent")
    monkeypatch.setattr(docker.subprocess, "run", fake_run)
    assert docker.inspect("volume", "absent") is None
    assert calls[0][:3] == [docker.DOCKER, "--host", docker.HOST]
    monkeypatch.setattr(docker.subprocess, "run", lambda *a, **k:
                        SimpleNamespace(returncode=1, stdout="", stderr="daemon unavailable"))
    with pytest.raises(RuntimeError, match="DOCKER_INSPECT_FAILED"):
        docker.inspect("volume", "absent")


def test_container_create_uses_existing_cluster_guard(monkeypatch):
    args = []
    monkeypatch.setattr(docker, "docker", lambda *a, **k: (args.extend(a), "a" * 64)[1])
    assert docker.create_container("b" * 64) == "a" * 64
    assert args[:3] == ["run", "--detach", "--name"]
    assert args[args.index("--pull") + 1] == "never"
    assert args[args.index("--entrypoint") + 1] == "/bin/sh"
    assert "PG_VERSION" in args[-1] and "gosu postgres postgres" in args[-1]
    assert "initdb" not in args[-1]
    assert "127.0.0.1:5433:5432" in args
    assert not any(x in args for x in ("POSTGRES_PASSWORD", "-e", "--env"))


def test_container_mount_label_port_and_image_are_exact(monkeypatch):
    nonce, cid = "b" * 64, "a" * 64
    item = {"Id": cid, "Image": docker.IMAGE,
            "Config": {"Labels": {"cvf.project": docker.PROJECT,
                                  "cvf.profile": docker.PROFILE,
                                  "cvf.owner-nonce": nonce}},
            "Mounts": [{"Type": "volume", "Name": docker.VOLUME,
                        "Destination": docker.PGDATA, "RW": True}],
            "HostConfig": {"PortBindings": {"5432/tcp": [
                {"HostIp": "127.0.0.1", "HostPort": "5433"}]}},
            "State": {"Running": True}}
    monkeypatch.setattr(docker, "inspect", lambda *a: item)
    assert docker.verified_container(nonce, cid) == item
    for mutation in (
        lambda x: x["Mounts"][0].update(Name="foreign"),
        lambda x: x["Config"]["Labels"].update({"cvf.owner-nonce": "c" * 64}),
        lambda x: x["HostConfig"]["PortBindings"]["5432/tcp"][0].update(HostIp="0.0.0.0"),
        lambda x: x.update(Image="sha256:" + "c" * 64),
    ):
        changed = copy.deepcopy(item)
        mutation(changed)
        monkeypatch.setattr(docker, "inspect", lambda *a: changed)
        with pytest.raises(RuntimeError):
            docker.verified_container(nonce, cid)


def test_reservation_rejects_missing_marker(monkeypatch, tmp_path):
    monkeypatch.setattr(recover, "ATTEMPT", tmp_path / "absent-attempt.json")
    with pytest.raises(RuntimeError, match="RECOVERY_RESERVATION_ABSENT"):
        recover.reservation("0" * 64, "1" * 64)


def test_old_partial_owner_to_running_uses_existing_registered_adapter(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "RUNTIME", tmp_path)
    monkeypatch.setattr(common, "OWNER", tmp_path / "owner.json")
    nonce = recover.EXPECTED_NONCE
    old = common.resource_record("PARTIAL_OWNED_FAILURE", nonce,
        volume_id=common.VOLUME, image_id=docker.IMAGE.removeprefix("sha256:"),
        reason="SEED_FAILED")
    state = {**old, "secret_ref": "private-reference-only",
             "creation_trail": [{"kind": "volume", "id": common.VOLUME}],
             "cleanup_trail": [{"kind": "container", "id": "a" * 64}]}
    new = common.resource_record("OWNED_RUNNING", nonce,
        container_id="b" * 64, volume_id=common.VOLUME, api_pid=101,
        web_pid=102, image_id=docker.IMAGE.removeprefix("sha256:"),
        db_fingerprint="c" * 64)
    recover.replace_lifecycle(state, new)
    common.write_owner(state)
    loaded = common.read_owner()
    assert loaded["outcome"] == "OWNED_RUNNING"
    assert "reason" not in loaded
    assert loaded["secret_ref"] == "private-reference-only"
    assert loaded["cleanup_trail"] == [{"kind": "container", "id": "a" * 64}]


def test_failure_after_exact_cleanup_keeps_old_volume_and_history(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "RUNTIME", tmp_path)
    monkeypatch.setattr(common, "OWNER", tmp_path / "owner.json")
    monkeypatch.setattr(recover, "inspect", lambda *_: None)
    monkeypatch.setattr(recover, "verified_volume", lambda *_: {"Name": common.VOLUME})
    nonce = recover.EXPECTED_NONCE
    old = common.resource_record("PARTIAL_OWNED_FAILURE", nonce,
        volume_id=common.VOLUME, image_id=docker.IMAGE.removeprefix("sha256:"),
        reason="SEED_FAILED")
    state = {**old, "secret_ref": "private-reference-only",
             "creation_trail": [{"kind": "volume", "id": common.VOLUME}],
             "cleanup_trail": [{"kind": "container", "id": "a" * 64}]}
    resource = {"volume_id": common.VOLUME, "container_id": None,
                "api_pid": None, "web_pid": None}
    recover._record_failure(old, state, resource, "READ_ONLY_INVENTORY", True)
    loaded = common.read_owner()
    assert loaded["outcome"] == "PARTIAL_OWNED_FAILURE"
    assert loaded["total_owned_count"] == 1
    assert loaded["recovery_failure_stage"] == "READ_ONLY_INVENTORY"
    assert loaded["cleanup_trail"] == [{"kind": "container", "id": "a" * 64}]


def test_prewrite_inventory_uses_one_explicit_read_only_snapshot(monkeypatch):
    names = inventory.expected_tables()
    statements = []
    class Cursor:
        current = ""
        def __enter__(self): return self
        def __exit__(self, *_): return None
        def execute(self, sql):
            self.current = sql
            statements.append(sql)
        def fetchone(self):
            if self.current == "SHOW transaction_isolation": return ("repeatable read",)
            if self.current == "SHOW transaction_read_only": return ("on",)
            if self.current.startswith("SELECT current_database"): return (inventory.DATABASE, "PostgreSQL 16.15")
            if self.current.startswith("SELECT system_identifier"): return (12345,)
            if self.current.startswith('SELECT count(*) FROM "'): return (0,)
            raise AssertionError(self.current)
        def fetchall(self):
            if self.current.startswith("SELECT nspname"): return [("public",)]
            if self.current.startswith("SELECT tablename"): return [(name,) for name in names]
            if self.current.startswith("SELECT table_name, column_name"):
                return [("users", "user_id")]
            raise AssertionError(self.current)
    class Connection:
        def __enter__(self): return self
        def __exit__(self, *_): return None
        def cursor(self): return Cursor()
    monkeypatch.setattr(inventory, "required_columns", lambda: {"users": {"user_id"}})
    monkeypatch.setitem(sys.modules, "psycopg", SimpleNamespace(connect=lambda *a, **kw: Connection()))
    result = inventory.inventory("inert")
    assert result["classification"] == "EMPTY_COMPATIBLE"
    assert result["schema_table_count"] == 31
    assert result["postgresql_version"] == "PostgreSQL 16.15"
    assert result["transaction_isolation"] == "repeatable read"
    assert result["transaction_read_only"] == "on"
    assert set(result["counts"]) == names
    assert statements[0] == "BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY"
    assert statements[-1] == "ROLLBACK"
    assert len([item for item in statements if item.startswith("SELECT count(*)")]) == 31
    assert not any(item.startswith(("INSERT", "UPDATE", "ALTER", "CREATE")) for item in statements)


def test_owner_preflight_uses_registered_partial_record_and_same_volume(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "RUNTIME", tmp_path)
    monkeypatch.setattr(common, "OWNER", tmp_path / "owner.json")
    monkeypatch.setattr(custody, "RUNTIME", tmp_path)
    monkeypatch.setattr(custody, "OWNER", tmp_path / "owner.json")
    monkeypatch.setattr(custody, "EXPECTED_RUNTIME", tmp_path)
    secret = tmp_path / "secrets.json"
    secret.write_text("inert-custody-only")
    monkeypatch.setattr(custody, "SECRET", secret)
    nonce = custody.EXPECTED_NONCE
    old_id = "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"
    record = common.resource_record("PARTIAL_OWNED_FAILURE", nonce,
        volume_id=common.VOLUME, image_id=docker.IMAGE.removeprefix("sha256:"),
        reason="SEED_FAILED")
    owner = {**record, "secret_ref": str(secret),
             "creation_trail": [{"kind": "volume", "id": common.VOLUME},
                                {"kind": "container", "id": old_id}],
             "cleanup_trail": [{"kind": "container", "id": old_id}]}
    common.write_owner(owner)
    actual = common.read_owner()
    monkeypatch.setattr(custody, "verified_image", lambda: None)
    monkeypatch.setattr(custody, "verified_volume", lambda _: {
        "Name": common.VOLUME, "CreatedAt": "inert", "Mountpoint": "/inert",
        "Driver": "local", "Labels": {"cvf.owner-nonce": nonce}})
    monkeypatch.setattr(custody, "inspect", lambda *_: None)
    monkeypatch.setattr(custody, "port_free", lambda *_: True)
    monkeypatch.setattr(custody, "secret_custody", lambda: None)
    result = custody.preflight(common.digest(actual))
    assert result["volume_id"] == common.VOLUME
    assert result["owner_digest"] == common.digest(actual)
    with pytest.raises(RuntimeError, match="OWNER_DIGEST_CHANGED"):
        custody.preflight("0" * 64)
