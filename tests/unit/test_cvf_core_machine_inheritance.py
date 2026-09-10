from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "check_cvf_core_machine_inheritance.py"
SPEC = importlib.util.spec_from_file_location("check_cvf_core_machine_inheritance", MODULE_PATH)
guard = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = guard
SPEC.loader.exec_module(guard)


def _write_fixture(tmp_path: Path, *, pack_commit: str) -> Path:
    project = tmp_path / "workspace" / "project"
    provenance = tmp_path / "provenance"
    pack_root = tmp_path / "workspace" / "CVF_RULE_PACKS" / "operator-local"
    (project / ".cvf").mkdir(parents=True)
    provenance.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=provenance, check=True)
    subprocess.run(["git", "config", "user.email", "cvf-test@example.invalid"], cwd=provenance, check=True)
    subprocess.run(["git", "config", "user.name", "CVF Test"], cwd=provenance, check=True)
    (provenance / "README.md").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=provenance, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=provenance, check=True)
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=provenance, text=True).strip()

    project_manifest = {
        "operatorLocalProvenance": {
            "sourceCommit": actual,
            "relativePath": "../../provenance",
            "rulePackManifestRelativePath": "../CVF_RULE_PACKS/operator-local/RULE_PACK_MANIFEST.json",
        }
    }
    (project / ".cvf" / "manifest.json").write_text(json.dumps(project_manifest), encoding="utf-8")
    artifacts = []
    for artifact_id, relative_path in guard.REQUIRED_ARTIFACTS.items():
        target = pack_root / "source" / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n", encoding="utf-8")
        artifacts.append({"artifactId": artifact_id})
    resolved_pack = actual[:9] if pack_commit == "ACTUAL" else pack_commit
    (pack_root / "RULE_PACK_MANIFEST.json").write_text(
        json.dumps({"sourceCommit": resolved_pack, "artifacts": artifacts}), encoding="utf-8"
    )
    return project


def test_valid_operator_local_binding_passes(tmp_path: Path) -> None:
    project = _write_fixture(tmp_path, pack_commit="ACTUAL")
    _, issues = guard.verify_binding(project)
    assert issues == []


def test_stale_pack_pin_fails_closed(tmp_path: Path) -> None:
    project = _write_fixture(tmp_path, pack_commit="deadbeef0")
    _, issues = guard.verify_binding(project)
    assert any("does not match project pin" in issue for issue in issues)
