#!/usr/bin/env python3
"""File size guard — keeps files from silently growing into technical debt.

CVF-style (GC-023) size control for this workspace. Thresholds by file type,
with an exception registry for justified/generated files. Fail-closed: a file
over its hard threshold (and not covered by an approved exception) fails.

Usage:
    python scripts/check_file_size.py            # verify, non-zero on violation
    python scripts/check_file_size.py --warn      # also print warn-level files
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "docs" / "reference" / "FILE_SIZE_EXCEPTION_REGISTRY.json"

# (warn, hard) line thresholds per suffix. See docs/reference/FILE_SIZE_GUARD.md.
THRESHOLDS: dict[str, tuple[int, int]] = {
    ".py": (300, 400),
    ".ts": (200, 300),
    ".tsx": (200, 300),
    ".md": (400, 600),
}

SKIP_DIRS = {".venv", "node_modules", ".pytest_cache", "__pycache__", ".git", "dist", "build"}
SKIP_NAMES = {"__init__.py"}


def load_exceptions() -> dict[str, int]:
    if not REGISTRY.is_file():
        return {}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {e["path"]: int(e["approvedMaxLines"]) for e in data.get("exceptions", [])}


def count_lines(path: Path) -> int:
    try:
        return path.read_text(encoding="utf-8", errors="replace").count("\n") + 1
    except OSError:
        return 0


def check(show_warn: bool = False) -> tuple[list[str], list[str]]:
    exceptions = load_exceptions()
    violations: list[str] = []
    warnings: list[str] = []

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT)
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
        allowed = exceptions.get(rel_str)

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
    show_warn = "--warn" in argv
    violations, warnings = check(show_warn=show_warn)

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
