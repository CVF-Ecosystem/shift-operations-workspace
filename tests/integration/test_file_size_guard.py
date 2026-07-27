"""Negative-probe suite for the hardened file-size guard (CVF-FSG-SPEC-001
AC-01-AC-12, the SPEC R12 closed-allowlist round, and R24/AC-31-AC-32
portable debt digests, HOV-REV-F13).

Every probe uses a throwaway tmp_path git-repo fixture; production is never
mutated. scripts/ is added to sys.path here (not in pyproject.toml's
pythonpath) - same pattern as test_migration_idempotency_guard.py. Debt-
baseline probes reuse the four real SPEC R12 paths, never arbitrary names.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_file_size import (  # noqa: E402
    APPROVED_LEGACY_DEBT_PATHS,
    GuardConfigError,
    check,
    count_lines,
    load_debt_baseline,
    load_exceptions,
)
from check_file_size import _sha256 as _guard_sha256  # noqa: E402

# Four real SPEC R12 allowlisted paths, reused where a distinct approved path is needed.
_A0, _A1, _A2, _A3 = sorted(APPROVED_LEGACY_DEBT_PATHS)
_LIMITS = '{".py": 300, ".ts": 200, ".tsx": 200, ".js": 200, ".jsx": 200}'

def _write(root: Path, rel: str, content: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="")
    return p

def _baseline_json(entries: str = "") -> str:
    return f'{{"schemaVersion": "1.0", "targetLimits": {_LIMITS}, "debt": [{entries}]}}'

def _base_fixture(tmp_path: Path) -> Path:
    """Minimal tracked repo with an empty registry/baseline pair."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _write(tmp_path, "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", '{"description": "empty", "exceptions": []}')
    _write(tmp_path, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json())
    subprocess.run(
        ["git", "add", "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", "docs/reference/FILE_SPLIT_DEBT_BASELINE.json"],
        cwd=tmp_path, check=True,
    )
    return tmp_path

def _oversized_py(n_lines: int) -> str:
    return "\n".join(f"x{i} = {i}" for i in range(n_lines)) + "\n"

def _debt_entry(root: Path, rel: str, *, n_lines: int = 310, track: bool = True) -> str:
    """Write an oversized .py at ``rel`` and return its exact debt-entry JSON."""
    target = _write(root, rel, _oversized_py(n_lines))
    if track:
        subprocess.run(["git", "add", rel], cwd=root, check=True)
    lines = count_lines(target)
    return f'{{"path": "{rel}", "sha256": "{_guard_sha256(target)}", "lineCount": {lines}, "hardLimit": 300, "reason": "r", "requiredSplit": "s"}}'

# --- AC-01/AC-02/AC-03: hard limits and deterministic counting --------------

def test_ac01_py_at_300_passes_301_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _write(root, "pkg/at_limit.py", _oversized_py(300))
    assert check(root=root)[0] == []
    _write(root, "pkg/over_limit.py", _oversized_py(301))
    assert any("over_limit.py" in v for v in check(root=root)[0])

def test_ac02_ts_at_200_passes_201_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _write(root, "web/at_limit.ts", "\n".join(f"const x{i}={i};" for i in range(200)) + "\n")
    assert check(root=root)[0] == []
    _write(root, "web/over_limit.tsx", "\n".join(f"const x{i}={i};" for i in range(201)) + "\n")
    assert any("over_limit.tsx" in v for v in check(root=root)[0])

def test_ac03_line_counting_is_deterministic(tmp_path):
    (tmp_path / "lf.py").write_bytes(b"a\nb\nc\n")
    (tmp_path / "crlf.py").write_bytes(b"a\r\nb\r\nc\r\n")
    (tmp_path / "nofinal.py").write_bytes(b"a\nb\nc")
    (tmp_path / "empty.py").write_bytes(b"")
    assert count_lines(tmp_path / "lf.py") == 3
    assert count_lines(tmp_path / "crlf.py") == 3
    assert count_lines(tmp_path / "nofinal.py") == 3
    assert count_lines(tmp_path / "empty.py") == 0

# --- AC-04/AC-05/AC-06/AC-07: debt baseline fail-closed semantics -----------

def test_ac04_unchanged_digest_bound_legacy_debt_passes(tmp_path):
    root = _base_fixture(tmp_path)
    entry = _debt_entry(root, _A0)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json(entry))
    assert check(root=root)[0] == []
    target = root / _A0
    target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
    assert check(root=root)[0] == []  # AC-31: same content, CRLF-represented, still valid

def test_ac05_same_line_count_content_edit_to_legacy_debt_fails(tmp_path):
    root = _base_fixture(tmp_path)
    entry = _debt_entry(root, _A0)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json(entry))
    target = root / _A0
    lines_before = count_lines(target)
    edited = target.read_text(encoding="utf-8").replace("x0 = 0", "x0 = 999999")
    _write(root, _A0, edited)
    assert count_lines(target) == lines_before  # line count unchanged, content changed
    with pytest.raises(GuardConfigError, match="stale"):
        check(root=root)
    target.write_bytes(edited.replace("\n", "\r\n").encode("utf-8"))
    with pytest.raises(GuardConfigError, match="stale"):  # AC-32: same mutation, CRLF-represented
        check(root=root)

def test_ac06_reduced_but_still_oversized_legacy_debt_fails(tmp_path):
    root = _base_fixture(tmp_path)
    entry = _debt_entry(root, _A0)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json(entry))
    _write(root, _A0, _oversized_py(305))  # still > 300, digest/lineCount now stale
    with pytest.raises(GuardConfigError, match="stale"):
        check(root=root)

def test_ac07_debt_reduced_to_compliant_size_fails_until_entry_removed(tmp_path):
    root = _base_fixture(tmp_path)
    entry = _debt_entry(root, _A0)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json(entry))
    _write(root, _A0, _oversized_py(100))  # now compliant, entry is stale
    with pytest.raises(GuardConfigError):
        check(root=root)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json())  # entry removed
    assert check(root=root)[0] == []

# --- AC-08: oversized new/unregistered executable fails ---------------------

def test_ac08_oversized_new_unregistered_executable_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _write(root, "pkg/surprise.py", _oversized_py(400))
    assert any("surprise.py" in v for v in check(root=root)[0])

# --- AC-09 + R12: malformed/duplicate/missing/untracked/fifth-path/shape ---

@pytest.mark.parametrize(
    "baseline_json",
    [
        "not json at all",
        _baseline_json('{"path": "a.py"}'),
        _baseline_json('{"path": "../a.py", "sha256": "x", "lineCount": 1, "hardLimit": 300, "reason": "r", "requiredSplit": "s"}'),
        _baseline_json('{"path": "/etc/passwd.py", "sha256": "x", "lineCount": 1, "hardLimit": 300, "reason": "r", "requiredSplit": "s"}'),
        "[]",
        f'{{"schemaVersion": "1.0", "targetLimits": {_LIMITS}}}',
        f'{{"schemaVersion": "1.0", "targetLimits": {_LIMITS}, "debt": "nope"}}',
        f'{{"schemaVersion": "2.0", "targetLimits": {_LIMITS}, "debt": []}}',
    ],
    ids=[
        "malformed_json", "missing_fields", "traversal", "absolute",
        "top_level_list", "missing_debt_field", "wrong_type_debt_field", "wrong_schema_version",
    ],
)
def test_ac09_malformed_debt_entries_fail(tmp_path, baseline_json):
    root = _base_fixture(tmp_path)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", baseline_json)
    with pytest.raises(GuardConfigError):
        load_debt_baseline(root / "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", root=root)

def _setup_debt_case(root: Path, kind: str) -> str:
    if kind == "duplicate":
        entry = _debt_entry(root, _A0)
        return _baseline_json(f"{entry}, {entry}")
    if kind == "missing_target":
        entry = f'{{"path": "{_A1}", "sha256": "x", "lineCount": 999, "hardLimit": 300, "reason": "r", "requiredSplit": "s"}}'
        return _baseline_json(entry)
    if kind == "untracked":
        return _baseline_json(_debt_entry(root, _A2, track=False))
    return _baseline_json(_debt_entry(root, "outside/allowlist.py"))  # kind == "fifth_path"

@pytest.mark.parametrize(
    "kind, match",
    [
        ("duplicate", "duplicate"),
        ("missing_target", "does not exist"),
        ("untracked", "not a tracked file"),
        ("fifth_path", "closed legacy-debt allowlist"),
    ],
)
def test_ac09_debt_entry_semantic_failures(tmp_path, kind, match):
    root = _base_fixture(tmp_path)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _setup_debt_case(root, kind))
    with pytest.raises(GuardConfigError, match=match):
        check(root=root)

def test_debt_entry_removable_after_split_even_for_an_r12_approved_path(tmp_path):
    """Allowlist bounds what MAY appear, not what MUST: split-then-drop passes."""
    root = _base_fixture(tmp_path)
    entry = _debt_entry(root, _A3)
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json(entry))
    assert check(root=root)[0] == []
    _write(root, _A3, _oversized_py(100))  # split to compliant size
    _write(root, "docs/reference/FILE_SPLIT_DEBT_BASELINE.json", _baseline_json())  # entry dropped
    assert check(root=root)[0] == []

@pytest.mark.parametrize(
    "rel, match",
    [
        ("docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", "exception registry missing"),
        ("docs/reference/FILE_SPLIT_DEBT_BASELINE.json", "debt baseline missing"),
    ],
)
def test_missing_policy_file_fails(tmp_path, rel, match):
    root = _base_fixture(tmp_path)
    (root / rel).unlink()
    with pytest.raises(GuardConfigError, match=match):
        check(root=root)

# --- AC-10: malformed/duplicate/missing/absolute exception entries + shape -

@pytest.mark.parametrize(
    "registry_json",
    [
        "not json at all",
        '{"description": "d", "exceptions": [{"path": "a.md"}]}',
        '{"description": "d", "exceptions": [{"path": "../a.md", "approvedMaxLines": 10, "reason": "r", "requiredFollowup": "f"}]}',
        '{"description": "d", "exceptions": [{"path": "/etc/a.md", "approvedMaxLines": 10, "reason": "r", "requiredFollowup": "f"}]}',
        "[]",
        '{"description": "d"}',
        '{"description": "d", "exceptions": "nope"}',
    ],
    ids=[
        "malformed_json", "missing_fields", "traversal", "absolute",
        "top_level_list", "missing_exceptions_field", "wrong_type_exceptions_field",
    ],
)
def test_ac10_malformed_exception_entries_fail(tmp_path, registry_json):
    root = _base_fixture(tmp_path)
    _write(root, "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", registry_json)
    with pytest.raises(GuardConfigError):
        load_exceptions(root / "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", root=root)

@pytest.mark.parametrize(
    "registry_json, match",
    [
        (
            '{{"description": "d", "exceptions": [{e}, {e}]}}'.format(
                e='{"path": "docs/notes.md", "approvedMaxLines": 10, "reason": "r", "requiredFollowup": "f"}'
            ),
            "duplicate",
        ),
        (
            '{"description": "d", "exceptions": [{"path": "docs/notes.md", "approvedMaxLines": 0, "reason": "r", "requiredFollowup": "f"}]}',
            "positive integer",
        ),
        (
            '{"description": "d", "exceptions": [{"path": "docs/does_not_exist.md", "approvedMaxLines": 10, "reason": "r", "requiredFollowup": "f"}]}',
            "does not exist",
        ),
    ],
    ids=["duplicate", "nonpositive_approved_max_lines", "missing_target"],
)
def test_ac10_exception_entry_semantic_failures(tmp_path, registry_json, match):
    root = _base_fixture(tmp_path)
    _write(root, "docs/notes.md", "x\n")
    _write(root, "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", registry_json)
    with pytest.raises(GuardConfigError, match=match):
        load_exceptions(root / "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", root=root)

# --- AC-11: executable exception attempt fails ------------------------------

def test_ac11_executable_exception_attempt_fails(tmp_path):
    root = _base_fixture(tmp_path)
    _write(root, "pkg/mod.py", "x = 1\n")
    _write(
        root, "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json",
        '{"description": "d", "exceptions": [{"path": "pkg/mod.py", "approvedMaxLines": 500, "reason": "r", "requiredFollowup": "f"}]}',
    )
    with pytest.raises(GuardConfigError, match="executable suffix cannot be excepted"):
        load_exceptions(root / "docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json", root=root)

# --- AC-12: unknown CLI argument fails; --warn cannot turn FAIL into PASS ---

def test_ac12_unknown_cli_argument_fails(tmp_path):
    root = _base_fixture(tmp_path)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_file_size.py"), "--not-a-real-flag"],
        cwd=root, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "unknown argument" in (result.stdout + result.stderr)

def test_ac12_warn_does_not_weaken_a_real_failure(tmp_path):
    root = _base_fixture(tmp_path)
    _write(root, "pkg/surprise.py", _oversized_py(400))
    no_warn_violations = check(root=root, show_warn=False)[0]
    warn_violations, _warnings = check(root=root, show_warn=True)
    assert no_warn_violations == warn_violations
    assert any("surprise.py" in v for v in warn_violations)
