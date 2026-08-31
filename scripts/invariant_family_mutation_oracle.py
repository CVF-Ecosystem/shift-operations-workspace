"""Independent exact mutation-id oracle derived only from matrix semantics."""
from __future__ import annotations

from typing import Any, Callable


def _shape(matrix: dict[str, Any], shape_id: str) -> dict[str, Any]:
    return next(s for o in matrix["outcomes"] for s in o["shapes"] if s["shapeId"] == shape_id)


def _conditional(rule: dict[str, Any], valid: dict[str, Any], add: Callable) -> None:
    if valid.get(rule["controllingField"]) != rule["controllingValue"]:
        return
    field = rule["field"]
    if rule["presence"] == "REQUIRED_WHEN_MATCH" and field in valid:
        add("CONDITIONAL_FLIP", f"{field}_absent")
        add("CONDITIONAL_FLIP", f"{field}_null")
    elif rule["presence"] == "FORBIDDEN_WHEN_MATCH" and field not in valid:
        add("CONDITIONAL_FLIP", f"{field}_present")


def _relation(rel: dict[str, Any], valid: dict[str, Any], add: Callable) -> None:
    kind = rel["kind"]
    if kind == "COUNTER_EQUALITY":
        field = rel["field"]
        if field not in valid or type(valid[field]) is not int:
            return
        add("COUNTER_MUTATION", f"{field}_minus_one")
        add("COUNTER_MUTATION", f"{field}_plus_one")
        if (1 if valid[field] == 0 else 0) != valid[field]:
            add("COUNTER_MUTATION", f"{field}_zero_or_nonzero")
        add("COUNTER_MUTATION", f"{field}_wrong_type")
    elif kind in ("DIGEST_EQUALITY", "FIELD_EQUALITY"):
        if kind == "DIGEST_EQUALITY" or rel.get("targetField") in valid or rel.get("sourceField") in valid:
            add("ONE_SIDE_RELATION_CHANGE", rel["relationId"])
    else:
        raise ValueError(f"unsupported relation: {kind!r}")


def required_mutation_ids(matrix: dict[str, Any], shape_id: str, valid: dict[str, Any]) -> set[str]:
    excluded = {(e["operator"], e["shapeId"]) for e in matrix.get("mutationPolicy", {}).get("excludedOperators", [])}
    shape = _shape(matrix, shape_id)
    result: set[str] = set()

    def add(operator: str, suffix: str) -> None:
        if (operator, shape_id) in excluded:
            return
        mutation_id = f"{shape_id}::{operator}::{suffix}"
        if mutation_id in result:
            raise ValueError(f"duplicate oracle id: {mutation_id}")
        result.add(mutation_id)

    for field in shape["requiredFields"]:
        add("DELETE_REQUIRED_FIELD", field)
    for field in shape["forbiddenFields"]:
        add("ADD_FORBIDDEN_FIELD", field)
    add("ADD_UNKNOWN_FIELD", "closed_boundary")
    owner = next(o["outcomeId"] for o in matrix["outcomes"] if any(s["shapeId"] == shape_id for s in o["shapes"]))
    for outcome in matrix["outcomes"]:
        if outcome["outcomeId"] != owner:
            add("REPLACE_DISCRIMINATOR", outcome["outcomeId"])
    add("REPLACE_DISCRIMINATOR", "unknown_value")
    for field, domain in shape["fieldDomains"].items():
        if field not in valid:
            continue
        add("WRONG_TYPE", field)
        if "const" in domain:
            add("CONST_MISMATCH", field)
        elif "enum" in domain:
            add("ENUM_MISMATCH", field)
        elif domain.get("minLength", 0) > 0:
            add("MIN_LENGTH_VIOLATION", field)
        elif "pattern" in domain:
            add("PATTERN_MISMATCH", field)
    for rule in shape["conditionalRules"]:
        _conditional(rule, valid, add)
    for relation in shape["relations"]:
        _relation(relation, valid, add)
    for field, domain in shape["fieldDomains"].items():
        if domain.get("type") == "NESTED_OBJECT" and isinstance(valid.get(field), dict):
            for nested_id in required_mutation_ids(matrix, domain["nestedShapeId"], valid[field]):
                add("RECURSE_NESTED_OBJECTS", f"{field}::{nested_id}")
    return result


__all__ = ["required_mutation_ids"]
