"""Reusable invariant-family contract module (SPEC R3-R16). Read-only, no provider/network/dynamic-import. See docs/cvf/INVARIANT_FAMILY_STANDARD.md."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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

# Mutation basis (SPEC R10) — deterministic, one semantic fact per mutation.

@dataclass(frozen=True)
class Mutation:
    mutationId: str
    operator: str
    shapeId: str
    payload: dict[str, Any]

def _sibling_outcomes(matrix: dict[str, Any], shape_id: str) -> list[str]:
    owner = None
    for outcome in matrix["outcomes"]:
        for shape in outcome["shapes"]:
            if shape["shapeId"] == shape_id:
                owner = outcome["outcomeId"]
    return [o["outcomeId"] for o in matrix["outcomes"] if o["outcomeId"] != owner]

def find_shape(matrix: dict[str, Any], shape_id: str) -> dict[str, Any]:
    return next(
        s for o in matrix["outcomes"] for s in o["shapes"] if s["shapeId"] == shape_id
    )

def rule_is_active(rule: dict[str, Any], instance: dict[str, Any]) -> bool:
    return instance.get(rule["controllingField"]) == rule["controllingValue"]

def generate_mutations(matrix: dict[str, Any], shape_id: str, valid: dict[str, Any]) -> list[Mutation]:
    # SPEC R10 minimum one-fact mutation basis, honoring declared exclusions.
    excluded = {
        (e["operator"], e["shapeId"])
        for e in matrix.get("mutationPolicy", {}).get("excludedOperators", [])
    }
    shape = find_shape(matrix, shape_id)
    out: list[Mutation] = []

    def add(operator: str, suffix: str, payload: dict[str, Any]) -> None:
        if (operator, shape_id) in excluded:
            return
        out.append(Mutation(f"{shape_id}::{operator}::{suffix}", operator, shape_id, payload))

    for f in shape["requiredFields"]:
        p = copy.deepcopy(valid)
        p.pop(f, None)
        add("DELETE_REQUIRED_FIELD", f, p)
    for f in shape["forbiddenFields"]:
        p = copy.deepcopy(valid)
        p[f] = "MUTATION_INJECTED_VALUE"
        add("ADD_FORBIDDEN_FIELD", f, p)
    p = copy.deepcopy(valid)
    p["__unknown_mutation_field__"] = True
    add("ADD_UNKNOWN_FIELD", "closed_boundary", p)
    for sibling in _sibling_outcomes(matrix, shape_id):
        p = copy.deepcopy(valid)
        p["outcome"] = sibling
        add("REPLACE_DISCRIMINATOR", sibling, p)
    p = copy.deepcopy(valid)
    p["outcome"] = "UNKNOWN_MUTATION_OUTCOME"
    add("REPLACE_DISCRIMINATOR", "unknown_value", p)
    for f, domain in shape["fieldDomains"].items():
        if f in valid:
            p = copy.deepcopy(valid)
            p[f] = _illegal_value_for_domain(domain)
            add("ILLEGAL_VALUE", f, p)
    for rule in shape["conditionalRules"]:
        _add_conditional_mutations(rule, valid, add)
    for rel in shape["relations"]:
        _add_relation_mutations(rel, valid, add)
    for f, domain in shape["fieldDomains"].items():
        if domain.get("type") == "NESTED_OBJECT" and f in valid and isinstance(valid[f], dict):
            for nested in generate_mutations(matrix, domain["nestedShapeId"], valid[f]):
                p = copy.deepcopy(valid)
                p[f] = nested.payload
                add("RECURSE_NESTED_OBJECTS", f"{f}::{nested.mutationId}", p)
    return out

def _add_conditional_mutations(rule: dict[str, Any], valid: dict[str, Any], add) -> None:
    # F2-R3: only an ACTIVE rule makes the governed field's presence a real
    # validity fact; when inactive the field is optional, so toggling it
    # cannot flip validity and would be a no-op "negative" the matcher accepts.
    f = rule["field"]
    if not rule_is_active(rule, valid):
        return
    if rule["presence"] == "REQUIRED_WHEN_MATCH":
        if f not in valid:
            return
        p = copy.deepcopy(valid)
        del p[f]
        add("CONDITIONAL_FLIP", f"{f}_absent", p)
        p = copy.deepcopy(valid)
        p[f] = None
        add("CONDITIONAL_FLIP", f"{f}_null", p)
    elif f not in valid:
        p = copy.deepcopy(valid)
        p[f] = "MUTATION_INJECTED_VALUE"
        add("CONDITIONAL_FLIP", f"{f}_present", p)

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

def _illegal_value_for_domain(domain: dict[str, Any]) -> Any:
    # Unconstrained STRING: same-type would be a silent no-op, so wrong-type instead.
    t = domain.get("type")
    if t == "STRING":
        if "enum" in domain:
            return "MUTATION_NOT_IN_ENUM"
        if domain.get("minLength", 0) > 0:
            return ""
        return -999
    if t == "BOOLEAN":
        return "MUTATION_NOT_A_BOOLEAN"
    if t in ("INTEGER", "NUMBER"):
        return "MUTATION_WRONG_TYPE"
    return "MUTATION_ILLEGAL_VALUE"

def _add_relation_mutations(rel: dict[str, Any], valid: dict[str, Any], add) -> None:
    kind = rel["kind"]
    if kind == "COUNTER_EQUALITY":
        f = rel["field"]
        if f not in valid or not isinstance(valid[f], int):
            return
        zero_flip = 1 if valid[f] == 0 else 0
        variants = [("minus_one", valid[f] - 1), ("plus_one", valid[f] + 1)]
        if zero_flip != valid[f]:
            variants.append(("zero_or_nonzero", zero_flip))
        for tag, new_value in variants:
            if new_value == valid[f]:
                continue
            p = copy.deepcopy(valid)
            p[f] = new_value
            add("COUNTER_MUTATION", f"{f}_{tag}", p)
        p = copy.deepcopy(valid)
        p[f] = "MUTATION_WRONG_TYPE"
        add("COUNTER_MUTATION", f"{f}_wrong_type", p)
    elif kind == "DIGEST_EQUALITY":
        p = copy.deepcopy(valid)
        p[rel["targetField"]] = "0" * 64
        add("ONE_SIDE_RELATION_CHANGE", rel["relationId"], p)
    elif kind == "FIELD_EQUALITY":
        field = rel["targetField"] if rel["targetField"] in valid else rel["sourceField"]
        if field in valid:
            p = copy.deepcopy(valid)
            p[field] = f"{p[field]}_MUTATED"
            add("ONE_SIDE_RELATION_CHANGE", rel["relationId"], p)

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
    "find_shape", "matches_shape_exactly",
    "evaluate_relations", "evaluate_conditional_rules", "rule_is_active",
    "run_parity",
]
