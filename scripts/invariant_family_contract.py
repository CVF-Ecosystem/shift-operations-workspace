"""Reusable invariant-family contract module (SPEC R3-R16). Read-only, no provider/network/dynamic-import. See docs/cvf/INVARIANT_FAMILY_STANDARD.md."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from invariant_family_mutation_generator import (
    Mutation, _illegal_value_for_domain, generate_mutations,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
_PATH_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./-]*$")
_PATH_BAD_RE = re.compile(r"^[A-Za-z]:|\\|(^|/)\.\.(/|$)|(^|/)\.(/|$)|(^|/)(/|$)")

class DuplicateKey(ValueError): pass

@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    familyId: str
    message: str

def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result

def load_json_no_dup(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)

def canonical_digest(path: Path) -> str:
    raw = path.read_bytes()
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def raw_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _has_symlink_component(joined: Path) -> bool:
    # resolve() erases symlink identity; check each unresolved component first.
    node = REPO_ROOT
    for part in joined.relative_to(REPO_ROOT).parts:
        node = node / part
        if node.is_symlink():
            return True
    return False

def safe_repo_path(candidate: str) -> Path | None:
    # Normalize a declared repository-relative path; None if unsafe.
    if not isinstance(candidate, str) or not _PATH_RE.fullmatch(candidate):
        return None
    if _PATH_BAD_RE.search(candidate):
        return None
    joined = REPO_ROOT / candidate
    if _has_symlink_component(joined):
        return None
    resolved = joined.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return None
    return resolved

def is_safe_regular_file(resolved: Path) -> bool:
    return resolved.is_file() and not resolved.is_symlink()

def find_shape(matrix: dict[str, Any], shape_id: str) -> dict[str, Any]:
    return next(
        s for o in matrix["outcomes"] for s in o["shapes"] if s["shapeId"] == shape_id
    )

def rule_is_active(rule: dict[str, Any], instance: dict[str, Any]) -> bool:
    return instance.get(rule["controllingField"]) == rule["controllingValue"]

def _required_conditional_ids(rule: dict[str, Any], valid: dict[str, Any], add) -> None:
    f = rule["field"]
    if not rule_is_active(rule, valid):
        return
    if rule["presence"] == "REQUIRED_WHEN_MATCH":
        if f in valid:
            add("CONDITIONAL_FLIP", f"{f}_absent")
            add("CONDITIONAL_FLIP", f"{f}_null")
    elif f not in valid:
        add("CONDITIONAL_FLIP", f"{f}_present")

# Shape matching / relation evaluation (used by guard, conformance, tests).

def evaluate_relations(shape: dict[str, Any], instance: dict[str, Any]) -> bool:
    for rel in shape["relations"]:
        kind = rel["kind"]
        if kind == "DIGEST_EQUALITY":
            src, tgt = instance.get(rel["sourceField"]), instance.get(rel["targetField"])
            if not isinstance(src, str) or hashlib.sha256(src.encode("utf-8")).hexdigest() != tgt:
                return False
        elif kind == "COUNTER_EQUALITY":
            val = instance.get(rel["field"])
            if type(val) is not int or val != rel["value"]:
                return False
        elif kind == "FIELD_EQUALITY" and instance.get(rel["sourceField"]) != instance.get(rel["targetField"]):
            return False
    return True

def _value_matches_domain(val: Any, domain: dict[str, Any], matrix: dict[str, Any] | None) -> bool:
    t = domain["type"]
    if t == "STRING" and (not isinstance(val, str) or isinstance(val, bool)):
        return False
    if t == "INTEGER" and type(val) is not int:
        return False
    if t == "BOOLEAN" and type(val) is not bool:
        return False
    if t == "NUMBER" and (type(val) not in (int, float) or isinstance(val, bool)):
        return False
    if t == "NESTED_OBJECT" and (not isinstance(val, dict) or matrix is None or not matches_shape_exactly(find_shape(matrix, domain["nestedShapeId"]), val, matrix)):
        return False
    if "const" in domain and val != domain["const"]:
        return False
    if "enum" in domain and val not in domain["enum"]:
        return False
    if t == "STRING" and "minLength" in domain and len(val) < domain["minLength"]:
        return False
    return not (t == "STRING" and "pattern" in domain and not re.fullmatch(domain["pattern"], val))

def evaluate_conditional_rules(shape: dict[str, Any], instance: dict[str, Any]) -> bool:
    for rule in shape["conditionalRules"]:
        active = rule_is_active(rule, instance)
        present = rule["field"] in instance
        if active and rule["presence"] == "REQUIRED_WHEN_MATCH" and not present:
            return False
        if active and rule["presence"] == "FORBIDDEN_WHEN_MATCH" and present:
            return False
    return True

def matches_shape_exactly(shape: dict[str, Any], instance: dict[str, Any], matrix: dict[str, Any] | None = None) -> bool:
    if not isinstance(instance, dict):
        return False
    keys = set(instance.keys())
    required = set(shape["requiredFields"])
    forbidden = set(shape["forbiddenFields"])
    conditional = {rule["field"] for rule in shape["conditionalRules"]}
    if not required.issubset(keys) or (keys & forbidden):
        return False
    if keys - required - conditional:
        return False
    for f, domain in shape["fieldDomains"].items():
        if f in instance and not _value_matches_domain(instance[f], domain, matrix):
            return False
    if not evaluate_conditional_rules(shape, instance):
        return False
    return evaluate_relations(shape, instance)

def run_parity(surfaces: list[Any], shape: dict[str, Any], instance: dict[str, Any]) -> bool:
    # True if all declared validator surfaces agree on accept/reject.
    results = {surface(shape, instance) for surface in surfaces}
    return len(results) <= 1

__all__ = [
    "REPO_ROOT", "DuplicateKey", "Diagnostic", "Mutation",
    "load_json_no_dup", "canonical_digest", "raw_digest", "safe_repo_path",
    "is_safe_regular_file", "generate_mutations",
    "_illegal_value_for_domain",
    "find_shape", "matches_shape_exactly",
    "evaluate_relations", "evaluate_conditional_rules", "rule_is_active",
    "run_parity",
]
