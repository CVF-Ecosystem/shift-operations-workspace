"""Verify the installed, pinned public CVF Core before invoking its controls."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

REQUIRED_ARTIFACTS = (
    "governance/compat/check_gate_to_role_closeability.py",
    "docs/reference/CVF_GATE_TO_ROLE_CLOSEABILITY_MACHINE_STANDARD.md",
)
TRUE_CONTROLS = (
    "liveGovernanceEvidenceRequired", "mockAllowedOnlyForUi",
    "workspaceIsolationRequired", "workspaceRulesRequired",
    "phaseTransitionRequired", "explicitRoleTransitionRequired",
    "providerNeutralRolesRequired", "coreBindingRequired",
    "coreUpdatesRequireExplicitRequest", "referenceRepositoriesReadOnly",
)
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def _json_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise ValueError(f"Git control check failed: {' '.join(args[:2])}")
    return result.stdout.strip() if args[0] in {"rev-parse", "remote", "ls-files"} else result.stdout


def _lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def verify_binding(project_root: Path) -> Path:
    root = project_root.resolve(strict=True)
    manifest = _json_object(root / ".cvf" / "manifest.json")
    policy = _json_object(root / ".cvf" / "policy.json")
    if manifest.get("schemaVersion") != "2.2-core-only" or policy.get("policyVersion") != "1.2-core-only":
        raise ValueError("Core-only manifest/policy schema mismatch")
    if "operatorLocalProvenance" in manifest or "operatorLocalProvenance" in policy:
        raise ValueError("active private provenance binding is forbidden")
    if manifest.get("workspaceLayout") != "SIBLING_HIDDEN_CORE":
        raise ValueError("workspace layout mismatch")
    if manifest.get("cvfCoreRelativePath") != "../.Controlled-Vibe-Framework-CVF":
        raise ValueError("CVF Core path mismatch")
    core = (root / manifest["cvfCoreRelativePath"]).resolve(strict=True)
    if not core.is_dir():
        raise ValueError("CVF Core directory missing")
    pin = manifest.get("cvfCoreCommit")
    if not isinstance(pin, str) or not HEX40.fullmatch(pin):
        raise ValueError("malformed CVF Core commit pin")
    repository = manifest.get("cvfCoreRepository")
    if repository != "https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git":
        raise ValueError("unapproved public CVF Core repository")
    if _git(core, "rev-parse", "HEAD").decode("ascii") != pin:
        raise ValueError("installed CVF Core HEAD differs from pin")
    if _git(core, "remote", "get-url", "origin").decode("utf-8") != repository:
        raise ValueError("installed CVF Core origin differs from public repository")
    if manifest.get("liveGovernanceEvidenceRequired") is not True or manifest.get("mockAllowedOnlyForUi") is not True:
        raise ValueError("manifest live evidence flags weakened")
    if any(policy.get(flag) is not True for flag in TRUE_CONTROLS):
        raise ValueError("policy control flag weakened")
    if policy.get("cvfCoreRef") != manifest["cvfCoreRelativePath"] or policy.get("riskCeiling") != "R2":
        raise ValueError("policy Core reference or risk ceiling mismatch")
    controls = manifest.get("cvfControls")
    if not isinstance(controls, dict) or (
        controls.get("bindingMode") != "PINNED_WORKSPACE_CORE"
        or controls.get("updateMode") != "EXPLICIT_REVIEWED_UPDATE"
        or controls.get("integrityNormalization") != "LF"
    ):
        raise ValueError("invalid cvfControls contract")
    artifacts = controls.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("invalid selected Core artifact set")
    by_path = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
            raise ValueError("malformed Core artifact pin")
        path, digest = artifact["path"], artifact["sha256"]
        if not isinstance(path, str) or not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError("malformed Core artifact path or digest")
        if path in by_path:
            raise ValueError("duplicate Core artifact pin")
        by_path[path] = digest
    if set(by_path) != set(REQUIRED_ARTIFACTS):
        raise ValueError("selected Core artifact set mismatch")
    for relative in REQUIRED_ARTIFACTS:
        source = core / relative
        if not source.is_file():
            raise ValueError(f"missing selected Core artifact: {relative}")
        _git(core, "ls-files", "--error-unmatch", "--", relative)
        blob = _git(core, "show", f"{pin}:{relative}")
        working = source.read_bytes()
        if _lf(working) != _lf(blob):
            raise ValueError(f"selected Core artifact differs from pinned Git blob: {relative}")
        if hashlib.sha256(_lf(working)).hexdigest() != by_path[relative]:
            raise ValueError(f"selected Core artifact SHA256 mismatch: {relative}")
    return core / REQUIRED_ARTIFACTS[0]
