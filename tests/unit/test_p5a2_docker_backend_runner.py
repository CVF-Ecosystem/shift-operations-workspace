"""Inert failure probes for the bounded P5-A2 Docker wrapper."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts" / "run_p5a2_docker_backend.py"
spec = importlib.util.spec_from_file_location("run_p5a2_docker_backend", WRAPPER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

URL = "postgresql+psycopg://user:secret@127.0.0.1:5432/test"


def test_missing_image_fails_without_pull(monkeypatch):
    calls = []

    def fake_run(cmd):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 1, "", "missing")

    monkeypatch.setattr(runner.base, "_run", fake_run)
    with pytest.raises(runner.base.LiveRoundTripError, match="BLOCKED_WITH_REASON"):
        runner.local_image_id()
    assert calls == [["docker", "image", "inspect", runner.base.IMAGE, "--format", "{{.Id}}"]]


def test_collision_or_failed_create_never_deletes_unowned_container(monkeypatch):
    deleted = []
    monkeypatch.setattr(runner.base, "start_container", lambda *_: (_ for _ in ()).throw(
        runner.base.LiveRoundTripError("container name collision")))
    monkeypatch.setattr(runner.base, "remove_container", lambda *args: deleted.append(args))
    summary = runner.run_once(URL, "existing", 5432, "secret", "sha256:image")
    assert summary["failure"] and "collision" in summary["failure"]
    assert summary["container_absent_after_cleanup"] is True
    assert summary["cleanup_skipped_reason"]
    assert deleted == []
    assert "secret" not in summary["failure"] and URL not in summary["failure"]


def test_owned_container_cleanup_and_secret_redaction(monkeypatch):
    calls = []
    monkeypatch.setattr(runner.base, "start_container", lambda *args: calls.append("start"))
    monkeypatch.setattr(runner, "container_image_id", lambda name: "sha256:image")
    monkeypatch.setattr(runner.base, "container_volumes", lambda name: ["owned-anonymous"])
    monkeypatch.setattr(runner.base, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner.base, "wait_ready_via_database", lambda url: None)
    monkeypatch.setattr(runner, "server_version", lambda name: "16.0")
    monkeypatch.setattr(runner.base, "apply_migrations_twice", lambda url: [{"applied": 1}, {"skipped": 1}])
    monkeypatch.setattr(runner, "run_target", lambda url: subprocess.CompletedProcess(
        [], 1, "postgresql://user:secret@127.0.0.1:5432/test", "secret"))
    monkeypatch.setattr(runner.base, "remove_container", lambda name, volumes: (calls.append(
        (name, volumes)) or True, []))
    monkeypatch.setattr(runner.base, "container_exists", lambda name: False)
    summary = runner.run_once(URL, "owned", 5432, "secret", "sha256:image")
    assert calls == ["start", ("owned", ["owned-anonymous"])]
    assert summary["container_absent_after_cleanup"] is True
    assert summary["failure"] == "P5-A2 SQL target failed or skipped"
    assert "secret" not in summary["target_tail"]
    assert "postgresql://" not in summary["target_tail"]


def test_cleanup_failure_is_never_success(monkeypatch):
    monkeypatch.setattr(runner.base, "start_container", lambda *args: None)
    monkeypatch.setattr(runner, "container_image_id", lambda name: "sha256:image")
    monkeypatch.setattr(runner.base, "container_volumes", lambda name: ["owned-anonymous"])
    monkeypatch.setattr(runner.base, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner.base, "wait_ready_via_database", lambda url: None)
    monkeypatch.setattr(runner, "server_version", lambda name: "16.0")
    monkeypatch.setattr(runner.base, "apply_migrations_twice", lambda url: [])
    monkeypatch.setattr(runner, "run_target", lambda url: subprocess.CompletedProcess([], 0, "1 passed", ""))
    monkeypatch.setattr(runner.base, "remove_container", lambda name, volumes: (False, volumes))
    monkeypatch.setattr(runner.base, "container_exists", lambda name: True)
    summary = runner.run_once(URL, "owned", 5432, "secret", "sha256:image")
    assert summary["container_absent_after_cleanup"] is False
    assert summary["anonymous_volumes_still_present"] == ["owned-anonymous"]
    assert summary["failure"] == "owned resource cleanup incomplete"


def test_sql_target_skip_is_not_positive_proof(monkeypatch):
    monkeypatch.setattr(runner.base, "start_container", lambda *args: None)
    monkeypatch.setattr(runner, "container_image_id", lambda name: "sha256:image")
    monkeypatch.setattr(runner.base, "container_volumes", lambda name: ["owned-anonymous"])
    monkeypatch.setattr(runner.base, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner.base, "wait_ready_via_database", lambda url: None)
    monkeypatch.setattr(runner, "server_version", lambda name: "16.0")
    monkeypatch.setattr(runner.base, "apply_migrations_twice", lambda url: [])
    monkeypatch.setattr(runner, "run_target", lambda url: subprocess.CompletedProcess([], 0, "1 skipped", ""))
    monkeypatch.setattr(runner.base, "remove_container", lambda name, volumes: (True, []))
    monkeypatch.setattr(runner.base, "container_exists", lambda name: False)
    summary = runner.run_once(URL, "owned", 5432, "secret", "sha256:image")
    assert summary["container_absent_after_cleanup"] is True
    assert summary["failure"] == "P5-A2 SQL target failed or skipped"


def test_readiness_failure_still_cleans_owned_resource(monkeypatch):
    deleted = []
    monkeypatch.setattr(runner.base, "start_container", lambda *args: None)
    monkeypatch.setattr(runner, "container_image_id", lambda name: "sha256:image")
    monkeypatch.setattr(runner.base, "container_volumes", lambda name: ["owned-anonymous"])
    monkeypatch.setattr(runner.base, "wait_ready", lambda name: (_ for _ in ()).throw(
        runner.base.LiveRoundTripError("readiness failed")))
    monkeypatch.setattr(runner.base, "remove_container", lambda name, volumes: (deleted.append(
        (name, volumes)) or True, []))
    monkeypatch.setattr(runner.base, "container_exists", lambda name: False)
    summary = runner.run_once(URL, "owned", 5432, "secret", "sha256:image")
    assert deleted == [("owned", ["owned-anonymous"])]
    assert summary["container_absent_after_cleanup"] is True
    assert "readiness failed" in summary["failure"]


def test_migration_failure_still_cleans_owned_resource(monkeypatch):
    deleted = []
    monkeypatch.setattr(runner.base, "start_container", lambda *args: None)
    monkeypatch.setattr(runner, "container_image_id", lambda name: "sha256:image")
    monkeypatch.setattr(runner.base, "container_volumes", lambda name: ["owned-anonymous"])
    monkeypatch.setattr(runner.base, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner.base, "wait_ready_via_database", lambda url: None)
    monkeypatch.setattr(runner, "server_version", lambda name: "16.0")
    monkeypatch.setattr(runner.base, "apply_migrations_twice", lambda url: (_ for _ in ()).throw(
        runner.base.LiveRoundTripError("migration failed")))
    monkeypatch.setattr(runner.base, "remove_container", lambda name, volumes: (deleted.append(
        (name, volumes)) or True, []))
    monkeypatch.setattr(runner.base, "container_exists", lambda name: False)
    summary = runner.run_once(URL, "owned", 5432, "secret", "sha256:image")
    assert deleted == [("owned", ["owned-anonymous"])]
    assert summary["container_absent_after_cleanup"] is True
    assert "migration failed" in summary["failure"]


def test_child_environment_drops_provider_credentials(monkeypatch):
    captured = {}
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-sensitive-value")

    def fake_subprocess(cmd, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(cmd, 0, "ok", "")

    monkeypatch.setattr(runner.subprocess, "run", fake_subprocess)
    runner.run_target(URL)
    assert captured["env"][runner.base.LIVE_URL_ENV] == URL
    assert "OPENAI_API_KEY" not in captured["env"]
    assert captured["cwd"] == runner.base.REPO_ROOT
    assert captured["env"]["PYTHONNOUSERSITE"] == "1"


def test_frozen_public_fixture_has_distinct_asof_lineages():
    from proactive_helpers import START, history, report
    from reporting_engine.proactive_analysis import analyze
    from reporting_engine.proactive_history import select_history
    from reporting_engine.proactive_models import HistoryInput

    path = ROOT / "tests" / "fixtures" / "p5a2_docker_backend_oracle.json"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "12ad36cbd335a8def5e7ac9a6ade6f0bf542cb45af4cec1760a7291a8f6973c0")
    golden = json.loads(raw)
    source = history([4] * 36)
    future = report(0, 9, version=2, created_offset=timedelta(hours=37))
    assert golden["persisted_report_count"] == len(source.candidates) + 1 == 37
    digests = []
    for case in golden["cases"]:
        as_of = START + timedelta(hours=36 if case["case"] == "initial_asof36" else 38)
        current = HistoryInput(source.scope_id, source.actor_id, source.query_start,
                               source.query_end, as_of, source.eligible_shift_ids,
                               source.candidates + (future,), True, True)
        selected = select_history(current, as_of, require_complete=True)
        assert [item.lineage_item() for item in selected] == case["selected_reports"]
        shift_zero = next(item for item in selected if item.shift_id == future.shift_id)
        assert shift_zero.version == (1 if case["case"] == "initial_asof36" else 2)
        result = analyze(current)
        assert {k: v for k, v in result.items() if k != "history_context"} == case["analysis"]
        digests.append((result["lineage_digest"], result["evaluation_digest"]))
    assert digests[0][0] != digests[1][0]
    assert digests[0][1] != digests[1][1]


def test_reloaded_report_validator_refuses_naive_time_and_tamper():
    path = ROOT / "tests" / "integration" / "test_p5a2_docker_backend.py"
    module_spec = importlib.util.spec_from_file_location("p5a2_sql_target_probe", path)
    assert module_spec and module_spec.loader
    target = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(target)
    from proactive_helpers import report

    original = report(0, 4)
    assert target._candidate_metadata(original)["version"] == 1
    naive = original.model_copy(deep=True)
    naive.created_at = naive.created_at.replace(tzinfo=None)
    with pytest.raises(AssertionError):
        target._candidate_metadata(naive)
    tampered = original.model_copy(deep=True)
    tampered.content.snapshot_digest = "0" * 64
    with pytest.raises(AssertionError):
        target._candidate_metadata(tampered)
