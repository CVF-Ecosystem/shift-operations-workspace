#!/usr/bin/env python3
"""File size guard — keeps files from silently growing into technical debt.

CVF-style (GC-023) size control for this workspace. Executable suffixes
(.py/.ts/.tsx/.js/.jsx) have strict hard limits enforced by fail-closed
scanning; a pre-existing oversized executable may remain only through an
exact digest-bound entry in the debt baseline (see
docs/reference/FILE_SPLIT_DEBT_BASELINE.json). Markdown keeps its own,
looser thresholds and may use the exception registry
(docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json); no executable suffix may
ever be excepted (CVF-FSG-SPEC-001 R6/R11).

Usage:
    python scripts/check_file_size.py            # verify, non-zero on violation
    python scripts/check_file_size.py --warn      # also print warn-level files
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXCEPTION_REGISTRY = REPO_ROOT / "docs" / "reference" / "FILE_SIZE_EXCEPTION_REGISTRY.json"
DEBT_BASELINE = REPO_ROOT / "docs" / "reference" / "FILE_SPLIT_DEBT_BASELINE.json"

# (warn, hard) line thresholds per suffix. See docs/reference/FILE_SIZE_GUARD.md.
EXECUTABLE_THRESHOLDS: dict[str, tuple[int, int]] = {
    ".py": (250, 300),
    ".ts": (160, 200),
    ".tsx": (160, 200),
    ".js": (160, 200),
    ".jsx": (160, 200),
}
DOC_THRESHOLDS: dict[str, tuple[int, int]] = {
    ".md": (400, 600),
}
THRESHOLDS: dict[str, tuple[int, int]] = {**EXECUTABLE_THRESHOLDS, **DOC_THRESHOLDS}

SKIP_DIRS = {".venv", "node_modules", ".pytest_cache", "__pycache__", ".git", "dist", "build"}
SKIP_NAMES = {"__init__.py"}

# SPEC R12: the closed legacy-debt allowlist. Exactly these four paths may
# ever appear in docs/reference/FILE_SPLIT_DEBT_BASELINE.json; a fifth or
# substituted path fails closed regardless of digest/lineCount validity. A
# path may be safely removed from the baseline once its file is split down to
# compliant size - this allowlist only bounds what MAY be present, it does
# not require every member to be present.
APPROVED_LEGACY_DEBT_PATHS = frozenset(
    {
        "scripts/generate_catalog.py",
        "scripts/run_identity_live_governance_evidence.py",
        "tests/cvf/test_customer_request_vertical.py",
        "tests/cvf/test_shift_close_governance.py",
    }
)


class GuardConfigError(Exception):
    """Fail-closed policy error: a malformed/stale/invalid registry, baseline
    or debt entry (SPEC R5/R6). Caught by main() and reported as FAIL."""


def count_lines(path: Path) -> int:
    """Deterministic line count (SPEC R2): universal-newline text read makes
    CRLF count identically to LF; a trailing final newline does not add a
    phantom extra line; an empty file counts as zero lines."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if text == "":
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(raw: str) -> str:
    """Reject absolute paths and traversal; return a normalized POSIX
    repository-relative path (SPEC R3/R6/R9)."""
    if not isinstance(raw, str) or not raw:
        raise GuardConfigError(f"path must be a non-empty string: {raw!r}")
    if raw.startswith("/") or raw.startswith("\\") or (len(raw) > 1 and raw[1] == ":"):
        raise GuardConfigError(f"path must be repository-relative, not absolute: {raw!r}")
    posix = raw.replace("\\", "/")
    parts = posix.split("/")
    if any(p in ("..", "") for p in parts):
        raise GuardConfigError(f"path fails normalization/traversal check: {raw!r}")
    return posix


def _tracked_files(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise GuardConfigError("unable to list git-tracked files for debt-baseline validation")
    return set(result.stdout.splitlines())


def load_exceptions(registry_path: Path = EXCEPTION_REGISTRY, *, root: Path = REPO_ROOT) -> dict[str, int]:
    if not registry_path.is_file():
        raise GuardConfigError(f"exception registry missing: {registry_path}")
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GuardConfigError(f"exception registry is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise GuardConfigError("exception registry top-level JSON must be an object")
    if "exceptions" not in data:
        raise GuardConfigError("exception registry missing required field 'exceptions'")
    exceptions_raw = data["exceptions"]
    if not isinstance(exceptions_raw, list):
        raise GuardConfigError("exception registry 'exceptions' must be a list")

    exceptions: dict[str, int] = {}
    for entry in exceptions_raw:
        if not isinstance(entry, dict):
            raise GuardConfigError(f"exception entry must be an object: {entry!r}")
        for field in ("path", "approvedMaxLines", "reason", "requiredFollowup"):
            if field not in entry:
                raise GuardConfigError(f"exception entry missing required field {field!r}: {entry!r}")
        path = _normalize(entry["path"])
        if path in exceptions:
            raise GuardConfigError(f"duplicate exception entry: {path}")
        suffix = Path(path).suffix
        if suffix in EXECUTABLE_THRESHOLDS:
            raise GuardConfigError(f"executable suffix cannot be excepted: {path}")
        limit = entry["approvedMaxLines"]
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise GuardConfigError(f"approvedMaxLines must be a positive integer: {path}")
        if not (root / path).is_file():
            raise GuardConfigError(f"exception target does not exist: {path}")
        exceptions[path] = limit
    return exceptions


def load_debt_baseline(baseline_path: Path = DEBT_BASELINE, *, root: Path = REPO_ROOT) -> dict[str, dict]:
    if not baseline_path.is_file():
        raise GuardConfigError(f"debt baseline missing: {baseline_path}")
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GuardConfigError(f"debt baseline is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise GuardConfigError("debt baseline top-level JSON must be an object")
    if data.get("schemaVersion") != "1.0":
        raise GuardConfigError("debt baseline schemaVersion must be exactly '1.0'")
    target_limits = data.get("targetLimits")
    if not isinstance(target_limits, dict):
        raise GuardConfigError("debt baseline missing required field 'targetLimits'")
    for suffix, (_, hard) in EXECUTABLE_THRESHOLDS.items():
        if target_limits.get(suffix) != hard:
            raise GuardConfigError(
                f"debt baseline targetLimits[{suffix!r}] does not match current policy"
            )
    if "debt" not in data:
        raise GuardConfigError("debt baseline missing required field 'debt'")
    debt_raw = data["debt"]
    if not isinstance(debt_raw, list):
        raise GuardConfigError("debt baseline 'debt' must be a list")

    tracked = _tracked_files(root)
    entries: dict[str, dict] = {}
    for entry in debt_raw:
        if not isinstance(entry, dict):
            raise GuardConfigError(f"debt entry must be an object: {entry!r}")
        for field in ("path", "sha256", "lineCount", "hardLimit", "reason", "requiredSplit"):
            if field not in entry:
                raise GuardConfigError(f"debt entry missing required field {field!r}: {entry!r}")
        path = _normalize(entry["path"])
        if path in entries:
            raise GuardConfigError(f"duplicate debt entry: {path}")
        if path not in APPROVED_LEGACY_DEBT_PATHS:
            raise GuardConfigError(
                f"debt entry path is not in the SPEC R12 closed legacy-debt allowlist: {path}"
            )
        suffix = Path(path).suffix
        if suffix not in EXECUTABLE_THRESHOLDS:
            raise GuardConfigError(f"debt entry suffix is not governed-executable: {path}")
        target = root / path
        if not target.is_file() or target.is_symlink():
            raise GuardConfigError(f"debt entry target does not exist as a regular file: {path}")
        if path not in tracked:
            raise GuardConfigError(f"debt entry target is not a tracked file: {path}")

        warn, hard = EXECUTABLE_THRESHOLDS[suffix]
        if entry["hardLimit"] != hard:
            raise GuardConfigError(f"debt entry hardLimit does not match current policy: {path}")
        actual_lines = count_lines(target)
        if actual_lines != entry["lineCount"]:
            raise GuardConfigError(f"debt entry lineCount is stale: {path}")
        actual_sha = _sha256(target)
        if actual_sha != entry["sha256"]:
            raise GuardConfigError(f"debt entry sha256 is stale: {path}")
        if actual_lines <= hard:
            raise GuardConfigError(f"debt entry is now compliant and must be removed: {path}")
        entries[path] = entry
    return entries


def check(
    show_warn: bool = False,
    *,
    root: Path = REPO_ROOT,
    registry_path: Path | None = None,
    baseline_path: Path | None = None,
) -> tuple[list[str], list[str]]:
    exceptions = load_exceptions(registry_path or (root / "docs" / "reference" / "FILE_SIZE_EXCEPTION_REGISTRY.json"), root=root)
    debt = load_debt_baseline(baseline_path or (root / "docs" / "reference" / "FILE_SPLIT_DEBT_BASELINE.json"), root=root)
    violations: list[str] = []
    warnings: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.name in SKIP_NAMES:
            continue
        thresholds = THRESHOLDS.get(path.suffix)
        if thresholds is None:
            continue

        warn, hard = thresholds
        lines = count_lines(path)
        rel_str = rel.as_posix()
        is_executable = path.suffix in EXECUTABLE_THRESHOLDS

        if is_executable and rel_str in debt:
            # Already proven exact-digest/lineCount/hardLimit match above.
            continue

        allowed = None if is_executable else exceptions.get(rel_str)
        if allowed is not None:
            if lines > allowed:
                violations.append(
                    f"{rel_str}: {lines} lines exceeds approved max {allowed}"
                )
            continue

        if lines > hard:
            violations.append(f"{rel_str}: {lines} lines exceeds hard limit {hard}")
        elif lines > warn and show_warn:
            warnings.append(f"{rel_str}: {lines} lines (warn at {warn}, hard {hard})")

    return violations, warnings


def main(argv: list[str]) -> int:
    known_flags = {"--warn"}
    unknown = [a for a in argv if a not in known_flags]
    if unknown:
        print(f"FILE SIZE GUARD: FAIL - unknown argument(s): {', '.join(unknown)}", file=sys.stderr)
        return 1

    show_warn = "--warn" in argv

    try:
        violations, warnings = check(show_warn=show_warn)
    except GuardConfigError as exc:
        print("FILE SIZE GUARD: FAIL")
        print(f"  - policy configuration error: {exc}")
        return 1

    if show_warn and warnings:
        print("FILE SIZE WARN:")
        for w in warnings:
            print(f"  - {w}")

    if violations:
        print("FILE SIZE GUARD: FAIL")
        for v in violations:
            print(f"  - {v}")
        print("See docs/reference/FILE_SIZE_GUARD.md to split or register an exception.")
        return 1

    print("FILE SIZE GUARD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
