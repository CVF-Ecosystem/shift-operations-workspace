#!/usr/bin/env python3
"""Run the selected native control from the installed pinned public CVF Core."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _cvf_core_binding import verify_binding

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    try:
        checker = verify_binding(PROJECT_ROOT)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"VIOLATION - pinned public CVF Core binding: {exc}", file=sys.stderr)
        return 2
    command = [
        sys.executable, "-I", str(checker), "--repo-root", str(PROJECT_ROOT),
        "--base", args.base, "--head", args.head,
    ]
    if args.enforce:
        command.append("--enforce")
    return subprocess.run(command, cwd=PROJECT_ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
