from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from test_cvf_core_machine_inheritance import binding


PUBLIC = "https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git"


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _fixture(tmp_path: Path) -> tuple[Path, Path, dict, dict]:
    workspace = tmp_path / "workspace"
    core = workspace / ".Controlled-Vibe-Framework-CVF"
    project = workspace / "project"
    core.mkdir(parents=True)
    (project / ".cvf").mkdir(parents=True)
    _git(core, "init", "-q")
    _git(core, "config", "user.email", "fixture@example.invalid")
    _git(core, "config", "user.name", "Fixture")
    _git(core, "remote", "add", "origin", PUBLIC)
    artifacts = []
    for relative in binding.REQUIRED_ARTIFACTS:
        target = core / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(f"fixture {relative}\n".encode())
        artifacts.append({"path": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    _git(core, "add", ".")
    _git(core, "commit", "-q", "-m", "fixture")
    manifest = {
        "schemaVersion": "2.2-core-only", "workspaceLayout": "SIBLING_HIDDEN_CORE",
        "cvfCoreRelativePath": "../.Controlled-Vibe-Framework-CVF",
        "cvfCoreRepository": PUBLIC, "cvfCoreCommit": _git(core, "rev-parse", "HEAD"),
        "liveGovernanceEvidenceRequired": True, "mockAllowedOnlyForUi": True,
        "cvfControls": {
            "bindingMode": "PINNED_WORKSPACE_CORE", "updateMode": "EXPLICIT_REVIEWED_UPDATE",
            "integrityNormalization": "LF", "artifacts": artifacts,
        },
    }
    policy = {flag: True for flag in binding.TRUE_CONTROLS}
    policy.update({"policyVersion": "1.2-core-only", "cvfCoreRef": "../.Controlled-Vibe-Framework-CVF", "riskCeiling": "R2"})
    _save(project, manifest, policy)
    return project, core, manifest, policy


def _save(project: Path, manifest: dict, policy: dict) -> None:
    (project / ".cvf" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (project / ".cvf" / "policy.json").write_text(json.dumps(policy), encoding="utf-8")


def test_valid_pin_ignores_private_and_remote_main(tmp_path: Path) -> None:
    project, core, manifest, _ = _fixture(tmp_path)
    (core / "newer.txt").write_text("newer\n", encoding="utf-8")
    _git(core, "add", "newer.txt")
    _git(core, "commit", "-q", "-m", "newer remote")
    _git(core, "update-ref", "refs/remotes/origin/main", "HEAD")
    _git(core, "checkout", "-q", "--detach", manifest["cvfCoreCommit"])
    assert binding.verify_binding(project).is_file()


@pytest.mark.parametrize("change", ["wrong_pin", "malformed_pin", "wrong_origin", "missing_checker", "missing_standard", "dirty_checker", "dirty_standard", "weak_policy", "weak_manifest", "malformed_artifacts", "wrong_digest", "private_binding"])
def test_binding_negative_cases(tmp_path: Path, change: str) -> None:
    project, core, manifest, policy = _fixture(tmp_path)
    if change == "wrong_pin":
        manifest["cvfCoreCommit"] = "0" * 40
    elif change == "malformed_pin":
        manifest["cvfCoreCommit"] = "bad"
    elif change == "wrong_origin":
        _git(core, "remote", "set-url", "origin", "https://example.invalid/core.git")
    elif change.startswith("missing_"):
        relative = binding.REQUIRED_ARTIFACTS[0 if change == "missing_checker" else 1]
        (core / relative).unlink()
    elif change.startswith("dirty_"):
        relative = binding.REQUIRED_ARTIFACTS[0 if change == "dirty_checker" else 1]
        (core / relative).write_text("tampered\n", encoding="utf-8")
    elif change == "weak_policy":
        policy["liveGovernanceEvidenceRequired"] = False
    elif change == "weak_manifest":
        manifest["mockAllowedOnlyForUi"] = False
    elif change == "malformed_artifacts":
        manifest["cvfControls"]["artifacts"][0]["sha256"] = "bad"
    elif change == "wrong_digest":
        manifest["cvfControls"]["artifacts"][0]["sha256"] = "0" * 64
    elif change == "private_binding":
        manifest["operatorLocalProvenance"] = {"sourceCommit": "0" * 40}
    _save(project, manifest, policy)
    with pytest.raises((ValueError, FileNotFoundError)):
        binding.verify_binding(project)


def test_missing_core_fails_closed_without_deleting_a_repository(tmp_path: Path) -> None:
    project = tmp_path / "workspace" / "project"
    (project / ".cvf").mkdir(parents=True)
    manifest = {
        "schemaVersion": "2.2-core-only", "workspaceLayout": "SIBLING_HIDDEN_CORE",
        "cvfCoreRelativePath": "../.Controlled-Vibe-Framework-CVF",
        "cvfCoreCommit": "0" * 40, "cvfCoreRepository": PUBLIC,
    }
    _save(project, manifest, {"policyVersion": "1.2-core-only"})
    with pytest.raises(FileNotFoundError):
        binding.verify_binding(project)


def test_existing_core_mismatch_initializer_is_read_only(tmp_path: Path) -> None:
    project, core, manifest, _ = _fixture(tmp_path)
    manifest["workspaceRulesRelativePath"] = "../WORKSPACE_RULES.md"
    (project / ".cvf" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (core / "newer.txt").write_text("newer\n", encoding="utf-8")
    _git(core, "add", "newer.txt")
    _git(core, "commit", "-q", "-m", "newer installed Core")
    head_before = _git(core, "rev-parse", "HEAD")
    config_before = (core / ".git" / "config").read_bytes()
    status_before = _git(core, "status", "--porcelain")
    script = Path(__file__).resolve().parents[2] / "scripts" / "initialize_cvf_clone.ps1"
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-ProjectPath", str(project)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "request separately reviewed adoption" in (result.stdout + result.stderr)
    assert _git(core, "rev-parse", "HEAD") == head_before
    assert (core / ".git" / "config").read_bytes() == config_before
    assert _git(core, "status", "--porcelain") == status_before
