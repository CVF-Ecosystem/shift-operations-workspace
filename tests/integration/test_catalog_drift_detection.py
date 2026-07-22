"""P-FIX-5: generate_catalog.py --check must actually detect drift.

A 2026-07-22 independent review (Medium Finding #6) proved --check never
called enrich_metrics or render_markdown - it only validated registry
structure (module ids/paths/status/dependencies). A probe that changed
code_loc to 999999 and one that hand-edited MODULE_CATALOG.md both still
passed --check.

These tests exercise the real repository (its module paths genuinely exist,
so `verify()` passes) and call `main(["--check"])` in-process against the
REAL docs/catalog/ files, which are always regenerated back to a known-good
state in a fixture teardown. This proves the check function itself catches
drift, without needing to fake an entire second repository tree.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_catalog.py"
REGISTRY_PATH = REPO_ROOT / "docs" / "catalog" / "MODULE_REGISTRY.json"
CATALOG_MD_PATH = REPO_ROOT / "docs" / "catalog" / "MODULE_CATALOG.md"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


@pytest.fixture
def restore_catalog_files():
    """Snapshot the real registry + Markdown, restore them after the test -
    every negative probe here mutates the actual repo files temporarily."""
    registry_backup = REGISTRY_PATH.read_text(encoding="utf-8")
    markdown_backup = CATALOG_MD_PATH.read_text(encoding="utf-8")
    try:
        yield
    finally:
        REGISTRY_PATH.write_text(registry_backup, encoding="utf-8")
        CATALOG_MD_PATH.write_text(markdown_backup, encoding="utf-8")


def test_check_passes_on_unmodified_repository():
    result = _run("--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "up to date" in result.stdout


def test_check_fails_when_code_loc_is_tampered(restore_catalog_files):
    """Reproduces the exact Codex probe: hand-set code_loc to a wrong value."""
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["metrics"]["totals"]["code_loc"] = 999999
    REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    result = _run("--check")
    assert result.returncode == 1
    assert "stale" in result.stdout


def test_check_fails_when_module_metrics_are_tampered(restore_catalog_files):
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["modules"][0]["metrics"]["loc"] = 123456
    REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    result = _run("--check")
    assert result.returncode == 1
    assert "stale" in result.stdout


def test_check_fails_when_markdown_is_hand_edited(restore_catalog_files):
    with CATALOG_MD_PATH.open("a", encoding="utf-8") as f:
        f.write("\nTAMPERED - hand-edited, not regenerated\n")

    result = _run("--check")
    assert result.returncode == 1
    assert "does not match" in result.stdout


def test_write_then_check_round_trips_clean(restore_catalog_files):
    """--write followed by --check must always pass - this is the normal
    developer workflow the gate should never block."""
    write_result = _run("--write")
    assert write_result.returncode == 0, write_result.stdout + write_result.stderr

    check_result = _run("--check")
    assert check_result.returncode == 0, check_result.stdout + check_result.stderr
