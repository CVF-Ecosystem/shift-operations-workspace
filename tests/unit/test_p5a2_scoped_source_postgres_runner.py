"""Inert Stage B runner and fixture fences; never starts Docker."""
from __future__ import annotations

import importlib.util
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/run_p5a2_scoped_source_postgres.py"
spec = importlib.util.spec_from_file_location("p5a2_source_pg_runner", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
sys.path.insert(0, str(ROOT / "tests/integration"))
from p5a2_scoped_source_pg_fixture import (  # noqa: E402
    baseline_expectations, validate_all_auxiliary_fixtures,
)

URL = "postgresql+psycopg://cvf_live:secret@127.0.0.1:5432/cvf_live_roundtrip"


def test_planning_admission_cannot_start_daemon_or_reserve(monkeypatch, capsys):
    monkeypatch.setattr(runner.base, "check_docker_daemon", lambda: pytest.fail("daemon read before seal"))
    monkeypatch.setattr(runner, "_reserve", lambda *_: pytest.fail("spent marker before seal"))
    assert runner.main(["--json"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["failure"].startswith("BLOCKED_WITH_REASON")


def test_exact_image_command_prevents_implicit_pull():
    cmd = runner.docker_run_cmd("cvf-pg-live-owned", 54321, "ephemeral")
    assert "--pull=never" in cmd and cmd[-1] == runner.IMAGE_ID
    assert "postgres:16-alpine" not in cmd and "127.0.0.1:54321:5432" in cmd
    assert "--mount" not in cmd and "-v" not in cmd
    with pytest.raises(runner.base.LiveRoundTripError):
        runner.docker_run_cmd("cvf-pg-live-owned", 54321, "x", "postgres:16-alpine")


def test_collision_does_not_delete_unowned_resource(monkeypatch):
    commands = []
    def fake_run(cmd):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, runner.IMAGE_ID, "")
    monkeypatch.setattr(runner.base, "_run", fake_run)
    monkeypatch.setattr(runner.base, "container_exists", lambda _name: True)
    result = runner.run_once({"observationPath": ".venv/unused"},
                             "cvf-pg-live-existing", 54321, "secret", "nonce")
    assert "collision" in result["failure"]
    assert result["container_absent_after_cleanup"] is False
    assert all(cmd[:2] != ["docker", "rm"] and cmd[:2] != ["docker", "run"] for cmd in commands)
    assert "secret" not in json.dumps(result)


def test_missing_cached_image_fails_without_pull_or_container(monkeypatch):
    calls = []
    def fake_run(cmd):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 1, "", "missing")
    monkeypatch.setattr(runner.base, "_run", fake_run)
    result = runner.run_once({"observationPath": ".venv/unused"},
                             "cvf-pg-live-owned", 54321, "secret", "nonce")
    assert "cached exact image unavailable" in result["failure"]
    assert calls == [["docker", "image", "inspect", runner.IMAGE_ID, "--format", "{{.Id}}"]]
    assert result["container_absent_after_cleanup"] is False


def test_owned_identity_cleanup_and_sanitized_failure(monkeypatch, tmp_path):
    calls = []
    owned = "a" * 64
    observation = tmp_path / "obs.json"
    monkeypatch.setattr(runner, "_inside", lambda _relative: observation)
    def fake_run(cmd):
        calls.append(cmd[:3])
        if cmd[:3] == ["docker", "image", "inspect"]:
            return subprocess.CompletedProcess(cmd, 0, runner.IMAGE_ID, "")
        if cmd[:2] == ["docker", "run"]:
            return subprocess.CompletedProcess(cmd, 0, owned, "")
        if cmd[:2] == ["docker", "rm"]:
            assert cmd[-1] == owned
            return subprocess.CompletedProcess(cmd, 0, owned, "")
        return subprocess.CompletedProcess(cmd, 0, "16.15", "")
    monkeypatch.setattr(runner.base, "_run", fake_run)
    monkeypatch.setattr(runner.base, "container_exists", lambda _name: False)
    monkeypatch.setattr(runner, "_inspect", lambda _name, field: (
        owned if field == "{{.Id}}" else runner.IMAGE_ID if field == "{{.Image}}" else
        json.dumps({"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "54321"}]})))
    monkeypatch.setattr(runner.base, "container_volumes", lambda _name: ["owned-volume"])
    monkeypatch.setattr(runner.base, "volume_exists", lambda _name: False)
    monkeypatch.setattr(runner.base, "wait_ready", lambda _name: None)
    monkeypatch.setattr(runner.base, "wait_ready_via_database", lambda _url: None)
    monkeypatch.setattr(runner.base, "apply_migrations_twice", lambda _url: [{"applied": 1}])
    monkeypatch.setattr(runner, "run_target", lambda _url, _ctx: subprocess.CompletedProcess(
        [], 1, URL, "secret"))
    result = runner.run_once({"observationPath": ".venv/unused"},
                             "cvf-pg-live-owned", 54321, "secret", "nonce")
    assert result["failure"] == "LiveRoundTripError: physical source target failed or skipped"
    assert result["container_absent_after_cleanup"] is True
    assert result["anonymous_volumes_still_present"] == []
    assert any(cmd[:2] == ["docker", "rm"] for cmd in calls)
    assert "secret" not in json.dumps(result) and URL not in json.dumps(result)


def test_cleanup_uncertainty_blocks_success(monkeypatch):
    owned = "a" * 64
    monkeypatch.setattr(runner.base, "_run", lambda cmd: subprocess.CompletedProcess(
        cmd, 0, runner.IMAGE_ID if cmd[:2] == ["docker", "image"] else owned, ""))
    monkeypatch.setattr(runner.base, "container_exists", lambda _name: False)
    monkeypatch.setattr(runner, "_inspect", lambda _name, field: (
        owned if field == "{{.Id}}" else runner.IMAGE_ID if field == "{{.Image}}" else
        json.dumps({"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "54321"}]})))
    monkeypatch.setattr(runner.base, "container_volumes", lambda _name: [])
    result = runner.run_once({"observationPath": ".venv/unused"},
                             "cvf-pg-live-owned", 54321, "secret", "nonce")
    assert result["failure"] and result["container_absent_after_cleanup"] is False


def test_atomic_spent_marker_cannot_be_reused(monkeypatch, tmp_path):
    marker = tmp_path / "attempt.json"
    monkeypatch.setattr(runner, "_inside", lambda _relative: marker)
    monkeypatch.setattr(runner, "_sha", lambda _path: "d" * 64)
    admission = {"attemptPath": "fixed"}
    assert runner._reserve(admission, "cvf-pg-live-owned", 54321, "nonce") == marker
    original = marker.read_bytes()
    with pytest.raises(FileExistsError):
        runner._reserve(admission, "cvf-pg-live-owned", 54321, "new")
    assert marker.read_bytes() == original


def test_minimal_child_environment_and_no_ambient_live_activation(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-sensitive-value")
    captured = {}
    def child(cmd, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(cmd, 0, "1 passed", "")
    monkeypatch.setattr(runner.subprocess, "run", child)
    runner.run_target(URL, {"nonce": "owned"})
    assert captured["env"][runner.base.LIVE_URL_ENV] == URL
    assert "OPENAI_API_KEY" not in captured["env"] and captured["env"][runner.CONTEXT_ENV]
    assert captured["cwd"] == ROOT and captured["timeout"] == 300
    monkeypatch.delenv(runner.CONTEXT_ENV, raising=False)
    monkeypatch.setenv(runner.base.LIVE_URL_ENV, URL)
    from test_p5a2_scoped_source_postgres_live import _owned_context
    with pytest.raises(pytest.skip.Exception):
        _owned_context()


def test_forged_owned_context_nonce_refuses_before_docker_or_database(monkeypatch, tmp_path):
    import test_p5a2_scoped_source_postgres_live as live
    admission = tmp_path / "admission.json"
    marker = tmp_path / "attempt.json"
    admission.write_text(json.dumps({"status": "SOURCE_REVIEWED", "harnessPins": {"x": "y"}}),
                         encoding="utf-8")
    marker.write_text(json.dumps({"nonce": "real", "container_name": "cvf-pg-live-owned",
                                  "image_id": runner.IMAGE_ID, "host_port": 54321,
                                  "admission_sha256": sha256(admission.read_bytes()).hexdigest()}),
                      encoding="utf-8")
    monkeypatch.setattr(live, "ADMISSION", admission)
    monkeypatch.setattr(live, "ATTEMPT", marker)
    monkeypatch.setenv(live.OWNED_ENV, json.dumps({"nonce": "forged",
        "container_name": "cvf-pg-live-owned", "image_id": runner.IMAGE_ID,
        "host_port": 54321, "admission_sha256": sha256(admission.read_bytes()).hexdigest()}))
    monkeypatch.setattr(live.subprocess, "run", lambda *_a, **_kw: pytest.fail("Docker reached"))
    with pytest.raises(AssertionError):
        live._owned_context()


def test_all_frozen_auxiliary_fixtures_construct_without_database():
    validate_all_auxiliary_fixtures()
    assert set(baseline_expectations()) == {"initial_asof36", "later_asof38"}


def test_admission_rejects_draft_phrase_and_changed_policy_before_runtime(monkeypatch, tmp_path):
    admission = json.loads(runner.ADMISSION.read_text(encoding="utf-8"))
    admission["status"] = "SOURCE_REVIEWED"
    admission["harnessPins"] = {key: "a" * 64 for key in (
        "scripts/run_p5a2_scoped_source_postgres.py",
        "tests/integration/p5a2_scoped_source_pg_fixture.py",
        "tests/integration/p5a2_scoped_source_pg_probes.py",
        runner.TARGET, "tests/unit/test_p5a2_scoped_source_postgres_runner.py")}
    source = tmp_path / "admission.json"
    effect = tmp_path / "effect.md"
    source.write_text(json.dumps(admission), encoding="utf-8")
    monkeypatch.setattr(runner, "ADMISSION", source)
    monkeypatch.setattr(runner, "EFFECT_WO", effect)
    effect.write_text("Status: DRAFT\nApproval: Status: APPROVED_FOR_EXECUTION\n", encoding="utf-8")
    with pytest.raises(runner.base.LiveRoundTripError, match="admission"):
        runner.sealed_admission()
    effect.write_text("Status: APPROVED_FOR_EXECUTION\n", encoding="utf-8")
    for key, value in (("baselineCommit", "f" * 40), ("loopbackOnly", False),
                       ("attemptPath", "attacker-path"), ("maxContainers", 2)):
        changed = dict(admission, **{key: value})
        source.write_text(json.dumps(changed), encoding="utf-8")
        with pytest.raises(runner.base.LiveRoundTripError, match="admission"):
            runner.sealed_admission()


def test_reservation_precedes_prerequisite_failure_and_persists_partial(monkeypatch, tmp_path, capsys):
    paths = {runner.ATTEMPT_REL: tmp_path / "attempt.json",
             runner.EVIDENCE_REL: tmp_path / "evidence.json"}
    monkeypatch.setattr(runner, "_inside", lambda relative: paths[relative])
    monkeypatch.setattr(runner, "sealed_admission", lambda: {
        "attemptPath": runner.ATTEMPT_REL, "psycopgVersion": "3.3.4"})
    monkeypatch.setattr(runner, "_sha", lambda _path: "d" * 64)
    monkeypatch.setattr(runner.base, "check_psycopg", lambda: (_ for _ in ()).throw(OSError("absent")))
    monkeypatch.setattr(runner.base, "check_docker_daemon", lambda: pytest.fail("daemon entered"))
    assert runner.main(["--json"]) == 1
    assert paths[runner.ATTEMPT_REL].exists()
    partial = json.loads(paths[runner.EVIDENCE_REL].read_text(encoding="utf-8"))
    assert partial["failure"] == "BLOCKED_WITH_REASON: OSError"
    assert partial["container_absent_after_cleanup"] is False
    assert "OSError: absent" not in json.dumps(partial)
    capsys.readouterr()
    with pytest.raises(FileExistsError):
        runner._reserve({"attemptPath": runner.ATTEMPT_REL}, "cvf-pg-live-owned", 54321, "new")


def test_parent_port_binding_rejects_wrong_mapping(monkeypatch):
    monkeypatch.setattr(runner, "_inspect", lambda *_: json.dumps({
        "5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "54321"}]}))
    with pytest.raises(runner.base.LiveRoundTripError, match="loopback"):
        runner._port_binding("cvf-pg-live-owned", 54321)


def test_child_target_claim_is_single_use(monkeypatch, tmp_path):
    import test_p5a2_scoped_source_postgres_live as live
    monkeypatch.setattr(live, "ROOT", tmp_path)
    admission = {"observationPath": "observation.json"}
    owned = {"nonce": "sealed"}
    path = live._claim_target(admission, owned)
    assert json.loads(path.read_text(encoding="utf-8"))["target_claim"] == "SPENT_ONCE"
    with pytest.raises(FileExistsError):
        live._claim_target(admission, owned)


def test_child_refuses_wrong_port_mapping_before_database(monkeypatch):
    import test_p5a2_scoped_source_postgres_live as live
    monkeypatch.setattr(live.subprocess, "run", lambda cmd, **_kwargs: subprocess.CompletedProcess(
        cmd, 0, json.dumps({"5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "54321"}]}), ""))
    with pytest.raises(AssertionError):
        live._verified_port_binding("cvf-pg-live-owned", 54321)


def test_transaction_trace_requires_real_transaction_object():
    from p5a2_scoped_source_pg_probes import _identity
    transaction = object()
    class FakeResult:
        def first(self):
            return (42, "same-snapshot")
    class FakeConnection:
        def __init__(self, tx):
            self.tx = tx
        def get_transaction(self):
            return self.tx
        def exec_driver_sql(self, _sql):
            return FakeResult()
    source = _identity(FakeConnection(transaction))
    fresh = _identity(FakeConnection(object()))
    assert source["snapshot"] == fresh["snapshot"]
    assert source["transaction_object_id"] != fresh["transaction_object_id"]
    with pytest.raises(AssertionError, match="transaction boundary"):
        _identity(FakeConnection(None))
