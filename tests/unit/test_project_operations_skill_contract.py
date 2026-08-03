from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "skills" / "operate-shift-workspace"
SKILL = SKILL_DIR / "SKILL.md"
OPENAI = SKILL_DIR / "agents" / "openai.yaml"

DESCRIPTION = (
    "Operate the shift-operations-workspace through its governed continuity, "
    "phase, role, evidence, review, repair, and closure workflow. Use when "
    "resuming this project, opening or advancing a tranche, preparing a bounded "
    "worker handoff, reviewing or repairing work, or closing and synchronizing "
    "project state."
)


def _frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n")
    raw, _body = text[4:].split("\n---\n", 1)
    return yaml.safe_load(raw)


def _skill_creator_root() -> Path:
    configured = os.environ.get("SKILL_CREATOR_ROOT", "").strip()
    return Path(configured) if configured else Path.home() / ".codex" / "skills" / ".system" / "skill-creator"


def test_exact_tree_and_metadata_contract() -> None:
    files = sorted(p.relative_to(SKILL_DIR).as_posix() for p in SKILL_DIR.rglob("*") if p.is_file())
    assert files == ["SKILL.md", "agents/openai.yaml"]
    text = SKILL.read_text(encoding="utf-8")
    assert _frontmatter(text) == {"name": "operate-shift-workspace", "description": DESCRIPTION}
    assert len(text.splitlines()) <= 220

    metadata = yaml.safe_load(OPENAI.read_text(encoding="utf-8"))
    assert metadata == {
        "interface": {
            "display_name": "Operate Shift Workspace",
            "short_description": "Run governed shift-workspace delivery safely",
            "default_prompt": (
                "Use $operate-shift-workspace to resume this project from canonical continuity "
                "and identify the next authorized move."
            ),
        }
    }


def test_workflow_contracts_are_present_and_ordered() -> None:
    text = SKILL.read_text(encoding="utf-8")
    ordered = [
        "## Establish the authority boundary",
        "## Rehydrate current continuity",
        "## Route phase, risk, and role",
        "### INTAKE",
        "### DESIGN",
        "### SPEC",
        "### WORK_ORDER",
        "### BUILD",
        "### REVIEW and repair",
        "### FREEZE",
        "## Stop and refuse",
        "## Validate this navigation",
    ]
    positions = [text.index(marker) for marker in ordered]
    assert positions == sorted(positions)
    required = [
        "BLOCKED_CONTINUITY_DRIFT",
        "INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE",
        "independent reviewer",
        "real provider API call",
        "mock evidence is UI-only",
        "exact changed set",
        "read-only CVF core",
        "Control-chain FREEZE does not imply roadmap-phase",
    ]
    assert all(token in text for token in required)


def test_no_stale_machine_or_self_authorizing_content() -> None:
    text = SKILL.read_text(encoding="utf-8")
    forbidden_patterns = [
        r"[A-Za-z]:[\\/]",
        r"/(?:home|Users)/",
        r"\b[0-9a-f]{40}\b",
        r"\b20\d{2}-\d{2}-\d{2}\b",
        r"AGENT_HANDOFF_20",
        r"(?:Claude|Codex)\s+(?:worker|reviewer)",
        r"https?://",
        r"(?:API_KEY|SECRET|TOKEN)\s*=",
        r"this skill (?:grants|authorizes|approves|enforces|guarantees)",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, text, flags=re.IGNORECASE) is None, pattern
    assert "## When to use" not in text


def test_named_repository_truth_and_commands_exist() -> None:
    assert (ROOT / "AGENTS.md").is_file()
    assert (ROOT / ".cvf" / "manifest.json").is_file()
    assert (ROOT / ".cvf" / "policy.json").is_file()
    assert (ROOT / "scripts" / "initialize_cvf_clone.ps1").is_file()
    assert (ROOT.parent / "WORKSPACE_RULES.md").is_file()


def test_current_skill_creator_quick_validate_passes() -> None:
    validator = _skill_creator_root() / "scripts" / "quick_validate.py"
    assert validator.is_file(), "current skill-creator quick_validate.py is required"
    result = subprocess.run(
        [sys.executable, str(validator), str(SKILL_DIR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
