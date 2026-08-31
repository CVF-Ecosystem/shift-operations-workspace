"""Agent/workflow routing tests for the invariant-family standard (SPEC R2,
R17, AC-01). Proves AGENTS.md, the operate-shift-workspace skill, and the
shared Work Order/reviewer template point to the canonical standard/matrix
rather than copying per-outcome field rules or the R10 mutation-operator list.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_MD = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
SKILL_MD = (REPO_ROOT / "skills" / "operate-shift-workspace" / "SKILL.md").read_text(encoding="utf-8")
TEMPLATE_MD = (REPO_ROOT / "docs" / "templates" / "INVARIANT_FAMILY_PROOF.md").read_text(encoding="utf-8")
STANDARD_MD = (REPO_ROOT / "docs" / "cvf" / "INVARIANT_FAMILY_STANDARD.md").read_text(encoding="utf-8")

# R10 mutation-operator identifiers and R14 per-outcome field facts that must
# never be literally copied into AGENTS.md, the skill, or the template.
COPIED_RULE_MARKERS = [
    "DELETE_REQUIRED_FIELD", "ADD_FORBIDDEN_FIELD", "REPLACE_DISCRIMINATOR",
    "WRONG_TYPE", "CONST_MISMATCH", "ENUM_MISMATCH",
    "MIN_LENGTH_VIOLATION", "PATTERN_MISMATCH", "COUNTER_MUTATION",
    "ONE_SIDE_RELATION_CHANGE",
    "POLICY_BLOCKED", "INPUT_INVALID", "provider_attempts=1", "provider_attempts=0",
]


def test_agents_md_points_to_standard_not_copies_rules() -> None:
    assert "docs/cvf/INVARIANT_FAMILY_STANDARD.md" in AGENTS_MD
    assert "invariant" in AGENTS_MD.lower()
    for marker in COPIED_RULE_MARKERS:
        assert marker not in AGENTS_MD, f"AGENTS.md copied a matrix-owned rule: {marker}"


def test_skill_points_to_standard_not_copies_rules() -> None:
    assert "docs/cvf/INVARIANT_FAMILY_STANDARD.md" in SKILL_MD or "invariant-family" in SKILL_MD.lower()
    for marker in COPIED_RULE_MARKERS:
        assert marker not in SKILL_MD, f"SKILL.md copied a matrix-owned rule: {marker}"


def test_shared_template_has_no_family_specific_rules() -> None:
    for marker in COPIED_RULE_MARKERS:
        assert marker not in TEMPLATE_MD, f"template copied a matrix-owned rule: {marker}"
    for field in ("matrix id", "digest", "applicability", "adapter", "evidence owner"):
        assert field.lower() in TEMPLATE_MD.lower(), f"template missing required field: {field}"


def test_standard_guide_is_the_declared_pointer_target() -> None:
    assert "docs/cvf/invariants/registry.json" in STANDARD_MD
    assert "docs/cvf/invariants/invariant-family.schema.json" in STANDARD_MD


def test_registry_and_schema_paths_referenced_from_index() -> None:
    index_md = (REPO_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    assert "INVARIANT_FAMILY_STANDARD.md" in index_md
    assert "registry.json" in index_md
