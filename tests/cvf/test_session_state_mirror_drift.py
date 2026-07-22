"""CVF_SESSION/ACTIVE_SESSION_STATE.json mirror-drift detection.

Independent review, 2026-07-22, Finding 5 (bootstrap-continuity batch): the
compatibility mirror (CVF_SESSION/ACTIVE_SESSION_STATE.json) duplicated a
bounded set of fields from SESSION/ACTIVE_SESSION_STATE.json's
cvf_bootstrap_continuity_contract block, but nothing deterministically
verified the two stayed in agreement - only prose telling future agents to
update both. scripts/check_session_state.py now has verify_mirror_drift()
for this. These tests prove it detects mirror drift, canonical internal drift,
and a missing required mirror without mutating governed repository files.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_session_state.py"
CANONICAL_PATH = REPO_ROOT / "SESSION" / "ACTIVE_SESSION_STATE.json"
MIRROR_PATH = REPO_ROOT / "CVF_SESSION" / "ACTIVE_SESSION_STATE.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_session_state", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_session_state"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def isolated_checker(tmp_path, monkeypatch):
    """Load the checker with its mirror path redirected to a disposable copy."""
    module = _load_module()
    mirror_copy = tmp_path / "ACTIVE_SESSION_STATE.json"
    mirror_copy.write_text(MIRROR_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(module, "MIRROR_PATH", mirror_copy)
    canonical = json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))
    return module, canonical, mirror_copy


def test_mirror_drift_check_passes_on_unmodified_repository(isolated_checker):
    module, canonical, _ = isolated_checker
    problems = module.verify_mirror_drift(canonical)
    assert problems == [], problems


def test_mirror_drift_check_fails_when_current_mode_diverges(isolated_checker):
    """A stale mirror currentMode must not survive validation."""
    module, canonical, mirror_path = isolated_checker
    mirror = json.loads(mirror_path.read_text(encoding="utf-8"))
    mirror["currentMode"] = "some_other_mode_the_mirror_was_not_updated_for"
    mirror_path.write_text(json.dumps(mirror, indent=2, ensure_ascii=False), encoding="utf-8")

    problems = module.verify_mirror_drift(canonical)
    assert problems, "drift was injected but verify_mirror_drift() reported no problems"
    assert any("currentMode" in p for p in problems)


def test_mirror_drift_check_fails_when_active_handoff_diverges(isolated_checker):
    """The most dangerous drift shape: the mirror still points at a
    superseded handoff after the canonical active_handoff moved on - this is
    exactly the 'two competing active handoffs' failure mode the bootstrap
    continuity contract prohibits."""
    module, canonical, mirror_path = isolated_checker
    mirror = json.loads(mirror_path.read_text(encoding="utf-8"))
    mirror["activeHandoff"] = "SESSION/handoffs/AGENT_HANDOFF_2026-07-22_PFIX6.md"
    mirror_path.write_text(json.dumps(mirror, indent=2, ensure_ascii=False), encoding="utf-8")

    problems = module.verify_mirror_drift(canonical)
    assert problems, "drift was injected but verify_mirror_drift() reported no problems"
    assert any("activeHandoff" in p for p in problems)


def test_mirror_drift_check_fails_when_phase_model_diverges(isolated_checker):
    """phaseModel (mirror) maps to controlChainModel (canonical block) -
    proves the explicit field-name mapping is actually exercised, not just
    a same-name comparison that would silently no-op if the mapping were
    wrong."""
    module, canonical, mirror_path = isolated_checker
    mirror = json.loads(mirror_path.read_text(encoding="utf-8"))
    mirror["phaseModel"] = ["INTAKE", "BUILD", "FREEZE"]
    mirror_path.write_text(json.dumps(mirror, indent=2, ensure_ascii=False), encoding="utf-8")

    problems = module.verify_mirror_drift(canonical)
    assert problems, "drift was injected but verify_mirror_drift() reported no problems"
    assert any("phaseModel" in p for p in problems)


def test_mirror_drift_check_fails_on_wrong_canonical_source(isolated_checker):
    """canonicalSource must literally equal 'SESSION/ACTIVE_SESSION_STATE.json'
    - if it ever pointed anywhere else, an agent could be misdirected to a
    third file entirely."""
    module, canonical, mirror_path = isolated_checker
    fake_mirror = {
        "canonicalSource": "CVF_SESSION/SOME_OTHER_FILE.json",
        "currentMode": canonical["cvf_bootstrap_continuity_contract"]["currentMode"],
        "activePhase": canonical["cvf_bootstrap_continuity_contract"]["activePhase"],
        "phaseModel": canonical["cvf_bootstrap_continuity_contract"]["controlChainModel"],
        "activeHandoff": canonical["cvf_bootstrap_continuity_contract"]["activeHandoff"],
        "nextAllowedMove": "placeholder text",
        "parkedOperatorCheckpoint": canonical["cvf_bootstrap_continuity_contract"]["parkedOperatorCheckpoint"],
        "activeRole": canonical["cvf_bootstrap_continuity_contract"]["activeRole"],
        "roleRoute": canonical["cvf_bootstrap_continuity_contract"]["roleRoute"],
        "updatedAt": canonical["cvf_bootstrap_continuity_contract"]["updatedAt"],
    }
    mirror_path.write_text(json.dumps(fake_mirror, indent=2, ensure_ascii=False), encoding="utf-8")
    problems = module.verify_mirror_drift(canonical)
    assert problems, "wrong canonicalSource was injected but verify_mirror_drift() reported no problems"
    assert any("canonicalSource" in p for p in problems)


def test_mirror_drift_check_fails_when_required_mirror_is_absent(
    tmp_path, monkeypatch, isolated_checker
):
    module, canonical, _ = isolated_checker
    monkeypatch.setattr(module, "MIRROR_PATH", tmp_path / "does_not_exist.json")
    problems = module.verify_mirror_drift(canonical)
    assert any("missing required compatibility mirror" in p for p in problems)


def test_canonical_top_level_handoff_drift_is_detected(isolated_checker):
    """The top-level canonical pointer must agree with its nested contract block."""
    module, canonical, _ = isolated_checker
    canonical["active_handoff"] = "SESSION/handoffs/AGENT_HANDOFF_2026-07-22_P2A_CUSTOMER_REQUEST.md"
    problems = module.verify_mirror_drift(canonical)
    assert any("activeHandoff" in p and "canonical continuity drift" in p for p in problems)
