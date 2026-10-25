from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import pytest

from scripts._cvf_core_binding import verify_binding
from scripts.check_project_knowledge import DOCS, ROOT, secret_codes, validate_pack

HELPER_SHA256 = "856b99d9273b0384c40c05bc2132eae66e9dce20b9a9c8b75c3d91ae7016d2c6"
COLLECTION_ID = "shift-operations-project-knowledge"
COLLECTION_NAME = "Shift Operations Project Knowledge"
NETWORK_TOKENS = (
    "Invoke-WebRequest", "Invoke-RestMethod", "Start-BitsTransfer", "curl",
    "wget", "System.Net", "HttpClient", "WebClient", "TcpClient",
    "UdpClient", "Start-Process",
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pinned_helper(project_root: Path = ROOT) -> Path:
    manifest = json.loads((project_root / ".cvf/manifest.json").read_text(encoding="utf-8"))
    verify_binding(project_root)
    core = (project_root / manifest["cvfCoreRelativePath"]).resolve(strict=True)
    expected = manifest["cvfCoreCommit"]
    head = subprocess.run(
        ["git", "-C", str(core), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    origin = subprocess.run(
        ["git", "-C", str(core), "remote", "get-url", "origin"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert head == expected
    assert origin == manifest["cvfCoreRepository"]
    helper = core / "scripts/ingest_cvf_downstream_knowledge.ps1"
    blob = subprocess.run(
        ["git", "-C", str(core), "show", f"{expected}:scripts/ingest_cvf_downstream_knowledge.ps1"],
        capture_output=True, check=True,
    ).stdout
    assert helper.read_bytes().replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n")
    assert _hash(helper) == HELPER_SHA256
    source = helper.read_text(encoding="utf-8")
    for token in NETWORK_TOKENS:
        assert not re.search(rf"(?i)(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", source)
    return helper


def _disposable_core_project(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "workspace"
    project = workspace / "project"
    core = workspace / ".Controlled-Vibe-Framework-CVF"
    (project / ".cvf").mkdir(parents=True)
    core.mkdir(parents=True)
    live_core = (ROOT / "../.Controlled-Vibe-Framework-CVF").resolve(strict=True)
    manifest = json.loads((ROOT / ".cvf/manifest.json").read_text(encoding="utf-8"))
    for relative in [
        *(item["path"] for item in manifest["cvfControls"]["artifacts"]),
        "scripts/ingest_cvf_downstream_knowledge.ps1",
    ]:
        target = core / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(live_core / relative, target)
    (core / "unrelated-model-gateway.txt").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(core)], check=True)
    subprocess.run(["git", "-C", str(core), "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(core), "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", str(core), "remote", "add", "origin", manifest["cvfCoreRepository"]], check=True)
    subprocess.run(["git", "-C", str(core), "add", "."], check=True)
    subprocess.run(["git", "-C", str(core), "commit", "-q", "-m", "local fixture"], check=True)
    manifest["cvfCoreCommit"] = subprocess.check_output(
        ["git", "-C", str(core), "rev-parse", "HEAD"], text=True,
    ).strip()
    (project / ".cvf/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    shutil.copyfile(ROOT / ".cvf/policy.json", project / ".cvf/policy.json")
    return project, core


def test_disposable_pinned_core_tolerates_unrelated_tracked_dirt(tmp_path: Path) -> None:
    project, core = _disposable_core_project(tmp_path)
    (core / "unrelated-model-gateway.txt").write_text("changed\n", encoding="utf-8")
    assert _pinned_helper(project) == core / "scripts/ingest_cvf_downstream_knowledge.ps1"


@pytest.mark.parametrize(
    "change",
    ["changed_helper", "missing_helper", "changed_control", "missing_control", "wrong_origin", "wrong_pin"],
)
def test_disposable_pinned_core_rejects_bound_drift(tmp_path: Path, change: str) -> None:
    project, core = _disposable_core_project(tmp_path)
    helper = core / "scripts/ingest_cvf_downstream_knowledge.ps1"
    control = core / "governance/compat/check_gate_to_role_closeability.py"
    if change == "changed_helper":
        helper.write_bytes(helper.read_bytes() + b"\n# tampered\n")
    elif change == "missing_helper":
        helper.unlink()
    elif change == "changed_control":
        control.write_bytes(control.read_bytes() + b"\n# tampered\n")
    elif change == "missing_control":
        control.unlink()
    elif change == "wrong_origin":
        subprocess.run(["git", "-C", str(core), "remote", "set-url", "origin", "https://example.invalid/core.git"], check=True)
    elif change == "wrong_pin":
        manifest_path = project / ".cvf/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["cvfCoreCommit"] = "0" * 40
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises((ValueError, FileNotFoundError, AssertionError)):
        _pinned_helper(project)


def _assert_index(payload: dict, root: Path, expected: set[str] = DOCS) -> None:
    assert payload["collectionId"] == COLLECTION_ID
    assert payload["collectionName"] == COLLECTION_NAME
    assert isinstance(payload["generatedAt"], str) and payload["generatedAt"]
    source_folder = Path(payload["sourceFolder"]).resolve(strict=True)
    source_folder.relative_to(root.resolve(strict=True))
    chunks = payload["chunks"]
    assert type(payload["chunkCount"]) is int
    assert payload["chunkCount"] == len(chunks) > 0
    ids: set[str] = set()
    sources: set[str] = set()
    for chunk in chunks:
        assert set(chunk) == {"id", "sourceFile", "content", "keywords"}
        assert isinstance(chunk["id"], str) and chunk["id"] and chunk["id"] not in ids
        ids.add(chunk["id"])
        source = chunk["sourceFile"]
        assert isinstance(source, str) and Path(source).name == source
        assert source != "README.md" and source in expected
        sources.add(source)
        assert isinstance(chunk["content"], str) and len(chunk["content"].strip()) >= 20
        assert not secret_codes(chunk["content"])
        assert isinstance(chunk["keywords"], list) and chunk["keywords"]
    assert sources == expected


def _run_rehearsal(
    mutate: Callable[[dict], None] | None = None,
) -> tuple[dict, Path]:
    result = validate_pack(ROOT)
    assert result.ok and set(result.eligible) == DOCS
    helper = _pinned_helper()
    temporary: Path | None = None
    payload: dict = {}
    try:
        temporary = Path(tempfile.mkdtemp(prefix="cvf-kpk-rehearsal-"))
        for name in result.eligible:
            shutil.copy2(ROOT / "knowledge" / name, temporary / name)
        assert {path.name for path in temporary.iterdir()} == DOCS
        output = temporary / "_index.json"
        completed = subprocess.run(
            [
                "powershell", "-ExecutionPolicy", "Bypass", "-File", str(helper),
                "-KnowledgePath", str(temporary), "-OutputIndex", str(output),
                "-CollectionId", COLLECTION_ID, "-CollectionName", COLLECTION_NAME,
            ],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert completed.returncode == 0
        assert output.is_file() and output.parent == temporary
        payload = json.loads(output.read_text(encoding="utf-8-sig"))
        if mutate:
            mutate(payload)
        _assert_index(payload, temporary)
        return payload, temporary
    finally:
        if temporary is not None:
            shutil.rmtree(temporary, ignore_errors=False)


@pytest.fixture(scope="module")
def valid_payload() -> dict:
    payload, temporary = _run_rehearsal()
    assert not temporary.exists()
    assert not list(ROOT.rglob("_index.json"))
    return payload


def test_real_pinned_helper_rehearsal_and_cleanup(valid_payload: dict) -> None:
    assert valid_payload["chunkCount"] == len(valid_payload["chunks"])
    assert {chunk["sourceFile"] for chunk in valid_payload["chunks"]} == DOCS


def test_cleanup_after_induced_assertion_failure() -> None:
    holder: dict[str, Path] = {}

    def fail(payload: dict) -> None:
        holder["path"] = Path(payload["sourceFolder"])
        payload["collectionId"] = "invalid"

    with pytest.raises(AssertionError):
        _run_rehearsal(fail)
    assert not holder["path"].exists()
    assert not list(ROOT.rglob("_index.json"))


@pytest.mark.parametrize(
    "source",
    ["UNEXPECTED.md", "STALE.md", "C:/absolute.md", "nested/missing.md"],
)
def test_unexpected_stale_absolute_or_missing_sourcefile_fails(
    valid_payload: dict, tmp_path: Path, source: str
) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["sourceFolder"] = str(tmp_path)
    payload["chunks"][0]["sourceFile"] = source
    with pytest.raises(AssertionError):
        _assert_index(payload, tmp_path)


def test_missing_eligible_sourcefile_fails(valid_payload: dict, tmp_path: Path) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["sourceFolder"] = str(tmp_path)
    payload["chunks"] = [
        chunk for chunk in payload["chunks"] if chunk["sourceFile"] != "PROJECT_CONTEXT.md"
    ]
    payload["chunkCount"] = len(payload["chunks"])
    with pytest.raises(AssertionError):
        _assert_index(payload, tmp_path)


def test_secret_like_chunk_content_fails(valid_payload: dict, tmp_path: Path) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["sourceFolder"] = str(tmp_path)
    payload["chunks"][0]["content"] = "TOKEN=synthetic-non-placeholder-value"
    with pytest.raises(AssertionError):
        _assert_index(payload, tmp_path)


def test_readme_manifest_and_repository_output_are_excluded(valid_payload: dict) -> None:
    sources = {chunk["sourceFile"] for chunk in valid_payload["chunks"]}
    assert "README.md" not in sources
    assert "manifest.json" not in sources
    assert not list(ROOT.rglob("_index.json"))
