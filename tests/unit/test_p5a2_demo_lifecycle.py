"""Inert real-adapter parity and contextual ownership refusal checks."""
from __future__ import annotations

import copy
import contextlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from invariant_family_contract import generate_mutations  # noqa: E402
from p5a2_source_demo_common import (accepts_lifecycle_record, check_pid,
                                     process_identity, resource_record, stop_refusal)  # noqa: E402
import p5a2_source_demo_preflight as preflight  # noqa: E402
import p5a2_source_demo_start as launcher  # noqa: E402
import p5a2_source_demo_stop as stopper  # noqa: E402

MATRIX = json.loads((ROOT / "docs/cvf/invariants/p5a2-demo-resource-lifecycle.json").read_text())
ORACLE = json.loads((ROOT / "tests/fixtures/p5a2_source_demo_lifecycle_oracle.json").read_text())


def test_eight_frozen_samples_and_full_mutation_corpus_use_real_adapter():
    mutations = []
    for sample in ORACLE["samples"]:
        record = sample["record"]
        assert accepts_lifecycle_record(record), sample["shapeId"]
        for mutation in generate_mutations(MATRIX, sample["shapeId"], record):
            assert not accepts_lifecycle_record(mutation.payload), mutation.mutationId
            mutations.append(mutation.mutationId)
    assert len(mutations) == 608
    assert len(set(mutations)) == 608


@pytest.mark.parametrize("bad", [0, -1, False, True, 1.2, "1234", None])
def test_context_rejects_nonpositive_boolean_fractional_pid(bad):
    assert not check_pid(bad)
    assert not process_identity(bad, "1" * 64, "uvicorn", probe=lambda _: "uvicorn")


def test_context_rejects_stale_nonce_and_swapped_command():
    assert not process_identity(42, "1" * 64, "uvicorn",
                                probe=lambda _: "2" * 64 + " uvicorn")
    assert not process_identity(42, "1" * 64, "uvicorn",
                                probe=lambda _: "1" * 64 + " vite.js")
    assert process_identity(42, "1" * 64, "uvicorn",
                            probe=lambda _: "1" * 64 + " uvicorn")


def test_owned_resource_prefix_and_count_after_cleanup():
    base = ORACLE["samples"][1]["record"]
    with pytest.raises(RuntimeError, match="PARTIAL_PREFIX_INVALID"):
        resource_record("PARTIAL_OWNED_FAILURE", base["owner_nonce"],
                        volume_id=base["volume_id"], web_pid=base["web_pid"],
                        image_id=base["image_id"], reason="SEED_FAILED")
    after = resource_record("PARTIAL_OWNED_FAILURE", base["owner_nonce"],
                            volume_id=base["volume_id"], image_id=base["image_id"],
                            reason="SEED_FAILED")
    assert after["total_owned_count"] == 1
    assert "container_id" not in after
    assert accepts_lifecycle_record(after)


def test_stop_refusal_preserves_owner_and_digest():
    owner = copy.deepcopy(ORACLE["samples"][1]["record"])
    before = copy.deepcopy(owner)
    refused = stop_refusal(owner, owner["owner_nonce"], "FOREIGN_RESOURCE")
    assert owner == before
    assert refused["effect_count"] == 0
    assert refused["owner_record_digest_before"] == refused["owner_record_digest_after"]
    assert accepts_lifecycle_record(refused)


def test_preflight_uses_exact_cached_node_and_refuses_port_collision(monkeypatch, tmp_path):
    node = tmp_path / "nvm/v22.14.0/node.exe"
    node.parent.mkdir(parents=True)
    node.write_text("fake cached node")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("NVM_HOME", str(tmp_path / "nvm"))
    calls = []
    def fake_run(argv, **kwargs):
        calls.append(argv)
        return "v22.14.0" if argv[-1] == "--version" else "sha256:" + "f" * 64
    monkeypatch.setattr(preflight, "run", fake_run)
    monkeypatch.setattr(preflight, "read_owner", lambda: None)
    monkeypatch.setattr(preflight, "OWNER", tmp_path / "owner.json")
    monkeypatch.setattr(preflight, "inspect", lambda *_: None)
    monkeypatch.setattr(preflight, "port_free", lambda port: port != 5433)
    with pytest.raises(RuntimeError, match="PORT_BUSY"):
        preflight.prerequisites()
    assert calls[0][0] == str(node.resolve())
    assert calls[1][:3] == ["docker", "image", "inspect"]


def test_preflight_refuses_absent_image_before_port_probe(monkeypatch, tmp_path):
    node = tmp_path / "nvm/v22.14.0/node.exe"
    node.parent.mkdir(parents=True)
    node.write_text("fake cached node")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("NVM_HOME", str(tmp_path / "nvm"))
    def fake_run(argv, **kwargs):
        if argv[-1] == "--version":
            return "v22.14.0"
        raise RuntimeError("COMMAND_FAILED")
    monkeypatch.setattr(preflight, "run", fake_run)
    monkeypatch.setattr(preflight, "port_free", lambda _: pytest.fail("port probe after absent image"))
    with pytest.raises(RuntimeError, match="IMAGE_ABSENT"):
        preflight.prerequisites()


@pytest.mark.parametrize("web_spawn,expected", [(True, [1, 1, 1, 1]),
                                           (False, [1, 1, 1, 0])])
def test_start_child_failure_halts_reverse_cleanup_at_first_failure(monkeypatch, tmp_path,
                                                                      web_spawn, expected):
    class FakeHandle:
        pid = 1002
        def poll(self):
            return None
        def terminate(self):
            raise OSError("fake handle refusal")
    calls, saved = [], []
    created = {"value": False}
    cid = "a" * 64
    monkeypatch.setattr(launcher, "RUNTIME", tmp_path)
    monkeypatch.setattr(launcher, "owner_lock", contextlib.nullcontext)
    monkeypatch.setattr(launcher, "prerequisites", lambda: {"image_id": "f" * 64,
        "node_path": "C:/cached/v22.14.0/node.exe"})
    monkeypatch.setattr(launcher, "private_file", lambda *_: None)
    monkeypatch.setattr(launcher, "labels_match", lambda *_: True)
    monkeypatch.setattr(launcher, "inspect", lambda kind, _: ({"Id": cid,
        "Image": "sha256:" + "f" * 64} if kind == "container" else {"Name": "owned"})
        if created["value"] else None)
    monkeypatch.setattr(launcher, "wait_db", lambda _: "e" * 64)
    monkeypatch.setattr(launcher, "wait_http", lambda _: None)
    monkeypatch.setattr(launcher, "write_owner", lambda record: saved.append(record))
    def fake_run(argv, **kwargs):
        calls.append(argv)
        if argv[:2] == ["docker", "compose"]:
            created["value"] = True
        return ""
    monkeypatch.setattr(launcher, "run", fake_run)
    def fake_child(argv, env, kind, resource, state, handles, cwd=None):
        if kind == "api":
            class ApiHandle:
                pid = 1001
                def poll(self):
                    return None
                def terminate(self):
                    raise OSError("fake API handle refusal")
            handles["api"] = ApiHandle()
            resource["api_pid"] = 1001
            return 1001, "start-api"
        if web_spawn:
            handles["web"] = FakeHandle()
            resource["web_pid"] = 1002
        raise RuntimeError("CHILD_IDENTITY_UNAVAILABLE")
    monkeypatch.setattr(launcher, "start_child", fake_child)
    with pytest.raises(RuntimeError, match="START_FAILED_OWNERSHIP_RECORDED"):
        launcher.start()
    assert saved[-1]["outcome"] == "PARTIAL_OWNED_FAILURE"
    assert [saved[-1][k] for k in ("volume_count", "container_count", "api_count", "web_count")] == expected
    assert not any(argv[:2] == ["docker", "stop"] for argv in calls)


def test_stop_rejects_stale_nonce_or_foreign_container_without_effect(monkeypatch):
    owner = copy.deepcopy(ORACLE["samples"][1]["record"])
    owner.update({"api_start": "a", "web_start": "b",
                  "api_executable": "api.exe", "web_executable": "node.exe"})
    writes, calls = [], []
    monkeypatch.setattr(stopper, "owner_lock", contextlib.nullcontext)
    monkeypatch.setattr(stopper, "read_owner", lambda: owner)
    monkeypatch.setattr(stopper, "write_owner", lambda x: writes.append(x))
    monkeypatch.setattr(stopper, "run", lambda argv, **kw: calls.append(argv))
    assert stopper.stop("2" * 64)["outcome"] == "STOP_REFUSED"
    monkeypatch.setattr(stopper, "inspect", lambda kind, _: {"Id": "b" * 64,
        "Image": "sha256:" + "f" * 64, "State": {"Running": True}})
    monkeypatch.setattr(stopper, "labels_match", lambda *_: True)
    assert stopper.stop(owner["owner_nonce"])["reason"] == "FOREIGN_RESOURCE"
    assert not writes and not calls


def test_stop_rejects_swapped_pid_before_effect(monkeypatch):
    owner = copy.deepcopy(ORACLE["samples"][1]["record"])
    owner.update({"api_start": "a", "web_start": "b",
                  "api_executable": "api.exe", "web_executable": "node.exe"})
    monkeypatch.setattr(stopper, "owner_lock", contextlib.nullcontext)
    monkeypatch.setattr(stopper, "read_owner", lambda: owner)
    monkeypatch.setattr(stopper, "labels_match", lambda *_: True)
    monkeypatch.setattr(stopper, "inspect", lambda kind, _: {"Id": owner["container_id"],
        "Image": "sha256:" + owner["image_id"], "State": {"Running": True}})
    @contextlib.contextmanager
    def fake_held(*args):
        raise RuntimeError("PID_REUSED")
        yield
    monkeypatch.setattr(stopper, "_held_process", fake_held)
    monkeypatch.setattr(stopper, "run", lambda *args, **kw: pytest.fail("stop effect on swapped PID"))
    monkeypatch.setattr(stopper, "write_owner", lambda _: pytest.fail("refusal overwrote owner"))
    assert stopper.stop(owner["owner_nonce"])["reason"] == "PID_REUSED"


def test_stop_removes_exact_container_after_children_and_retains_volume(monkeypatch):
    owner = copy.deepcopy(ORACLE["samples"][1]["record"])
    owner.update({"api_start": "a", "web_start": "b",
                  "api_executable": "api.exe", "web_executable": "node.exe",
                  "cleanup_trail": []})
    effects, writes = [], []
    state = {"container": True, "running": True}
    def fake_inspect(kind, _):
        if kind == "volume":
            return {"Name": "owned"}
        return ({"Id": owner["container_id"], "Image": "sha256:" + owner["image_id"],
                 "State": {"Running": state["running"]}} if state["container"] else None)
    def fake_run(argv, **kwargs):
        effects.append(argv[:2])
        if argv[:2] == ["docker", "stop"]:
            state["running"] = False
        if argv[:2] == ["docker", "rm"]:
            state["container"] = False
    @contextlib.contextmanager
    def fake_held(*args):
        yield None, args[0]
    monkeypatch.setattr(stopper, "owner_lock", contextlib.nullcontext)
    monkeypatch.setattr(stopper, "read_owner", lambda: owner)
    monkeypatch.setattr(stopper, "inspect", fake_inspect)
    monkeypatch.setattr(stopper, "labels_match", lambda *_: True)
    monkeypatch.setattr(stopper, "_held_process", fake_held)
    monkeypatch.setattr(stopper, "_terminate", lambda _, pid: effects.append(["terminate", pid]))
    monkeypatch.setattr(stopper, "run", fake_run)
    monkeypatch.setattr(stopper, "write_owner", lambda x: writes.append(x))
    result = stopper.stop(owner["owner_nonce"])
    assert result["outcome"] == "STOPPED_RETAINED"
    assert result["container_count"] == 0 and result["volume_count"] == 1
    assert effects == [["terminate", owner["web_pid"]],
                       ["terminate", owner["api_pid"]], ["docker", "stop"],
                       ["docker", "rm"]]
    assert writes[-1]["outcome"] == "STOPPED_RETAINED"
