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
MIRROR_PATH = REPO_ROOT / "CVF_SESSION" / "ACTIVE_SESSION_STATE.json"

# CVF_SESSION/ACTIVE_SESSION_STATE.json is a non-canonical compatibility
# mirror (see docs/CVF_BOOTSTRAP_LOG_2026-07-22.md and that file's own
# canonicalSource/note fields) required only because
# scripts/check_cvf_workspace_agent_enforcement.ps1 hard-checks that exact
# literal path. It duplicates a bounded set of control fields from
# SESSION/ACTIVE_SESSION_STATE.json's "cvf_bootstrap_continuity_contract"
# block. This maps each mirror field to where its source-of-truth value lives
# in the canonical file - field names differ between the two (snake_case
# top-level canonical fields, camelCase nested-block fields, one renamed key)
# so an explicit mapping is used instead of requiring identical JSON shape.
#
# "nextAllowedMove" is intentionally EXCLUDED from value comparison: the
# mirror deliberately holds a short "see canonical file" pointer instead of
# duplicating the full next_allowed_move text (to avoid drifting out of sync
# with a long free-text field) - only its non-empty presence is checked.
_MIRROR_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "canonicalSource": (),  # constant expected value, checked separately
    "currentMode": ("cvf_bootstrap_continuity_contract", "currentMode"),
    "activePhase": ("cvf_bootstrap_continuity_contract", "activePhase"),
    "phaseModel": ("cvf_bootstrap_continuity_contract", "controlChainModel"),
    "activeHandoff": ("cvf_bootstrap_continuity_contract", "activeHandoff"),
    "parkedOperatorCheckpoint": ("cvf_bootstrap_continuity_contract", "parkedOperatorCheckpoint"),
    "activeRole": ("cvf_bootstrap_continuity_contract", "activeRole"),
    "roleRoute": ("cvf_bootstrap_continuity_contract", "roleRoute"),
    "updatedAt": ("cvf_bootstrap_continuity_contract", "updatedAt"),
}
_EXPECTED_CANONICAL_SOURCE = "SESSION/ACTIVE_SESSION_STATE.json"
_EXPECTED_CONTRACT_NEXT_MOVE = "Mirrors next_allowed_move above - see that field for the full text."
_EXPECTED_MIRROR_NEXT_MOVE = (
    "See SESSION/ACTIVE_SESSION_STATE.json's next_allowed_move field for the full, "
    "current text - this mirror does not duplicate that long-form text to avoid "
    "drifting out of sync with the canonical source."
)
_CANONICAL_TOP_LEVEL_MAP: dict[str, tuple[str, ...]] = {
    "currentMode": ("mode",),
    "activeHandoff": ("active_handoff",),
    "updatedAt": ("last_updated",),
}


def _get_path(obj: dict, path: tuple[str, ...]):
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return _MISSING
        cur = cur[key]
    return cur


_MISSING = object()


def verify_mirror_drift(canonical: dict) -> list[str]:
    """Compare CVF_SESSION/ACTIVE_SESSION_STATE.json against the canonical
    cvf_bootstrap_continuity_contract block. Returns an empty list if the
    mirror is missing or any duplicated/pointer field drifts."""
    problems: list[str] = []

    if not MIRROR_PATH.is_file():
        return ["missing required compatibility mirror: CVF_SESSION/ACTIVE_SESSION_STATE.json"]

    try:
        mirror = json.loads(MIRROR_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"CVF_SESSION/ACTIVE_SESSION_STATE.json is not valid JSON: {exc}"]

    contract_block = canonical.get("cvf_bootstrap_continuity_contract")
    if not isinstance(contract_block, dict):
        return [
            "CVF_SESSION/ACTIVE_SESSION_STATE.json (compatibility mirror) exists "
            "but SESSION/ACTIVE_SESSION_STATE.json has no "
            "'cvf_bootstrap_continuity_contract' block to compare it against"
        ]

    for contract_field, top_level_path in _CANONICAL_TOP_LEVEL_MAP.items():
        contract_value = contract_block.get(contract_field, _MISSING)
        top_level_value = _get_path(canonical, top_level_path)
        if contract_value is _MISSING or top_level_value is _MISSING:
            problems.append(
                f"canonical continuity drift: {contract_field!r} missing from contract "
                f"block or top-level path {'.'.join(top_level_path)!r}"
            )
        elif contract_value != top_level_value:
            problems.append(
                f"canonical continuity drift: {contract_field!r} mismatch - contract="
                f"{contract_value!r}, top-level ({'.'.join(top_level_path)})="
                f"{top_level_value!r}"
            )

    contract_next_move = contract_block.get("nextAllowedMove")
    if contract_next_move != _EXPECTED_CONTRACT_NEXT_MOVE:
        problems.append(
            "canonical continuity drift: contract nextAllowedMove must be the exact "
            "pointer to top-level next_allowed_move"
        )

    actual_source = mirror.get("canonicalSource")
    if actual_source != _EXPECTED_CANONICAL_SOURCE:
        problems.append(
            "mirror drift: canonicalSource="
            f"{actual_source!r}, expected {_EXPECTED_CANONICAL_SOURCE!r}"
        )

    for mirror_field, canonical_path in _MIRROR_FIELD_MAP.items():
        if mirror_field == "canonicalSource":
            continue  # already checked above
        mirror_value = mirror.get(mirror_field, _MISSING)
        canonical_value = _get_path(canonical, canonical_path)
        if mirror_value is _MISSING or canonical_value is _MISSING:
            problems.append(
                f"mirror drift: field {mirror_field!r} missing from mirror "
                f"or from canonical path {'.'.join(canonical_path)!r}"
            )
        elif mirror_value != canonical_value:
            problems.append(
                f"mirror drift: {mirror_field!r} mismatch - mirror={mirror_value!r}, "
                f"canonical ({'.'.join(canonical_path)})={canonical_value!r}"
            )

    if mirror.get("nextAllowedMove") != _EXPECTED_MIRROR_NEXT_MOVE:
        problems.append(
            "mirror drift: nextAllowedMove must be the exact canonical-state pointer"
        )

    return problems


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

    problems.extend(verify_mirror_drift(state))

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
