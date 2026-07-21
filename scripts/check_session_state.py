#!/usr/bin/env python3
"""Verify the project session state is consistent (provider-neutral governance).

Catches the drift modes a handoff/session system actually hits:
* active_handoff points at a file that does not exist,
* a required_reads entry is missing from disk,
* next_allowed_move or blocked_work is empty (a session with no stated next
  move or no guardrails is not a usable handoff).

Usage:
    python scripts/check_session_state.py         # verify, non-zero on drift
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "SESSION" / "ACTIVE_SESSION_STATE.json"


def verify() -> list[str]:
    problems: list[str] = []

    if not STATE_PATH.is_file():
        return [f"missing: {STATE_PATH.relative_to(REPO_ROOT)}"]

    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"ACTIVE_SESSION_STATE.json is not valid JSON: {exc}"]

    active = state.get("active_handoff")
    if not active:
        problems.append("active_handoff is empty")
    elif not (REPO_ROOT / active).is_file():
        problems.append(f"active_handoff points at missing file: {active}")

    required = state.get("required_reads", [])
    if not required:
        problems.append("required_reads is empty")
    for rel in required:
        if not (REPO_ROOT / rel).exists():
            problems.append(f"required_reads missing on disk: {rel}")

    if not str(state.get("next_allowed_move", "")).strip():
        problems.append("next_allowed_move is empty (no stated next move)")

    if not state.get("blocked_work"):
        problems.append("blocked_work is empty (no guardrails recorded)")

    # SESSION_MEMORY companion should exist alongside the machine state.
    if not (REPO_ROOT / "SESSION" / "SESSION_MEMORY.md").is_file():
        problems.append("missing: SESSION/SESSION_MEMORY.md")

    return problems


def main() -> int:
    problems = verify()
    if problems:
        print("SESSION STATE: FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("SESSION STATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
