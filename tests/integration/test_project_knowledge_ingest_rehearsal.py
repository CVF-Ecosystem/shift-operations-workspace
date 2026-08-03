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


def _pinned_helper() -> Path:
    manifest = json.loads((ROOT / ".cvf/manifest.json").read_text(encoding="utf-8"))
    core = (ROOT / manifest["cvfCoreRelativePath"]).resolve(strict=True)
    expected = manifest["cvfCoreCommit"]
    head = subprocess.run(
        ["git", "-C", str(core), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    remote = subprocess.run(
        ["git", "-C", str(core), "rev-parse", "origin/main"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert head == remote == expected
    assert not subprocess.run(
        ["git", "-C", str(core), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    helper = core / "scripts/ingest_cvf_downstream_knowledge.ps1"
    assert _hash(helper) == HELPER_SHA256
    source = helper.read_text(encoding="utf-8")
    for token in NETWORK_TOKENS:
        assert not re.search(rf"(?i)(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", source)
    return helper


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
