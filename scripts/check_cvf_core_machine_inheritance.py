#!/usr/bin/env python3
"""Fail closed when the operator-local CVF machine-control binding drifts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ARTIFACTS = {
    "gate-to-role-closeability-standard": "docs/reference/CVF_GATE_TO_ROLE_CLOSEABILITY_MACHINE_STANDARD.md",
    "gate-to-role-closeability-checker": "governance/compat/check_gate_to_role_closeability.py",
    "adif-0057-entry": "docs/reference/agent_defect_intelligence/entries/CVF_ADIF-0057.md",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"cannot resolve Git HEAD at {root}")
    return result.stdout.strip()


def verify_binding(project_root: Path = PROJECT_ROOT) -> tuple[Path, list[str]]:
    issues: list[str] = []
    project_manifest = _load_json(project_root / ".cvf" / "manifest.json")
    binding = project_manifest.get("operatorLocalProvenance", {})
    pinned_commit = str(binding.get("sourceCommit", ""))
    provenance_root = (project_root / str(binding.get("relativePath", ""))).resolve()
    pack_manifest = (project_root / str(binding.get("rulePackManifestRelativePath", ""))).resolve()

    if not pinned_commit:
        issues.append("operatorLocalProvenance.sourceCommit is missing")
    if not pack_manifest.is_file():
        issues.append(f"rule-pack manifest is missing: {pack_manifest}")
        return pack_manifest.parent / "source" / REQUIRED_ARTIFACTS["gate-to-role-closeability-checker"], issues

    pack = _load_json(pack_manifest)
    pack_commit = str(pack.get("sourceCommit", ""))
    if not pack_commit or not pinned_commit.startswith(pack_commit):
        issues.append(f"rule-pack sourceCommit {pack_commit or '<missing>'} does not match project pin {pinned_commit or '<missing>'}")

    if not provenance_root.is_dir():
        issues.append(f"private provenance root is missing: {provenance_root}")
    else:
        try:
            actual_head = _git_head(provenance_root)
            if actual_head != pinned_commit:
                issues.append(f"private provenance HEAD {actual_head} does not match project pin {pinned_commit}")
        except RuntimeError as exc:
            issues.append(str(exc))

    artifacts = {str(item.get("artifactId")): item for item in pack.get("artifacts", [])}
    source_root = pack_manifest.parent / "source"
    for artifact_id, relative_path in REQUIRED_ARTIFACTS.items():
        if artifact_id not in artifacts:
            issues.append(f"rule-pack artifact is missing: {artifact_id}")
        projected = source_root / Path(relative_path)
        if not projected.is_file():
            issues.append(f"projected artifact is missing: {projected}")

    checker = source_root / Path(REQUIRED_ARTIFACTS["gate-to-role-closeability-checker"])
    return checker, issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    checker, issues = verify_binding()
    print("=== CVF Core Machine Inheritance Guard ===")
    print(f"Binding violations: {len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    if issues:
        print("VIOLATION - refresh and repin the operator-local CVF rule pack.")
        return 2 if args.enforce else 0

    command = [
        sys.executable,
        str(checker),
        "--repo-root",
        str(PROJECT_ROOT),
        "--base",
        args.base,
        "--head",
        args.head,
    ]
    if args.enforce:
        command.append("--enforce")
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode:
        return result.returncode
    print("COMPLIANT - pinned Core control is present and applied to this project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
