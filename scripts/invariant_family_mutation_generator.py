"""Deterministic invariant-family mutation witnesses.

This module owns generation only.  The independent obligation oracle lives in
``invariant_family_mutation_oracle`` and is intentionally not imported here.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Mutation:
    mutationId: str
    operator: str
    shapeId: str
    payload: dict[str, Any]


def _find_shape(matrix: dict[str, Any], shape_id: str) -> dict[str, Any]:
    return next(s for o in matrix["outcomes"] for s in o["shapes"] if s["shapeId"] == shape_id)


def _rule_active(rule: dict[str, Any], instance: dict[str, Any]) -> bool:
    return instance.get(rule["controllingField"]) == rule["controllingValue"]


def _different_scalar(value: Any) -> Any:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is float:
        return value + 1.0
    if isinstance(value, str):
        return value + "_MUTATED"
    raise ValueError("unsupported scalar constant")


def _wrong_type(domain: dict[str, Any]) -> Any:
    kind = domain.get("type")
    if kind == "STRING":
        return -999
    if kind == "BOOLEAN":
        return "MUTATION_NOT_A_BOOLEAN"
    if kind in ("INTEGER", "NUMBER"):
        return "MUTATION_WRONG_TYPE"
    if kind == "NESTED_OBJECT":
        return "MUTATION_NOT_AN_OBJECT"
    raise ValueError(f"unsupported domain type: {kind!r}")


def _pattern_mismatch(pattern: str) -> str:
    if pattern == "^[0-9a-f]{64}$":
        return "x"
    raise ValueError(f"unsupported pattern: {pattern!r}")


def _constraint_witness(domain: dict[str, Any]) -> tuple[str, Any] | None:
    if "const" in domain:
        return "CONST_MISMATCH", _different_scalar(domain["const"])
    if "enum" in domain:
        values = domain["enum"]
        if not values:
            raise ValueError("empty enum")
        candidate = _different_scalar(values[0])
        while candidate in values:
            candidate = _different_scalar(candidate)
        return "ENUM_MISMATCH", candidate
    if domain.get("minLength", 0) > 0:
        return "MIN_LENGTH_VIOLATION", "x" * (domain["minLength"] - 1)
    if "pattern" in domain:
        return "PATTERN_MISMATCH", _pattern_mismatch(domain["pattern"])
    return None


def _conditional(rule: dict[str, Any], valid: dict[str, Any], add: Callable) -> None:
    field = rule["field"]
    if not _rule_active(rule, valid):
        return
    if rule["presence"] == "REQUIRED_WHEN_MATCH" and field in valid:
        payload = copy.deepcopy(valid)
        del payload[field]
        add("CONDITIONAL_FLIP", f"{field}_absent", payload)
        payload = copy.deepcopy(valid)
        payload[field] = None
        add("CONDITIONAL_FLIP", f"{field}_null", payload)
    elif rule["presence"] == "FORBIDDEN_WHEN_MATCH" and field not in valid:
        payload = copy.deepcopy(valid)
        payload[field] = "MUTATION_INJECTED_VALUE"
        add("CONDITIONAL_FLIP", f"{field}_present", payload)


def _relations(rel: dict[str, Any], valid: dict[str, Any], add: Callable) -> None:
    kind = rel["kind"]
    if kind == "COUNTER_EQUALITY":
        field = rel["field"]
        if field not in valid or type(valid[field]) is not int:
            return
        variants = [("minus_one", valid[field] - 1), ("plus_one", valid[field] + 1)]
        flip = 1 if valid[field] == 0 else 0
        if flip != valid[field]:
            variants.append(("zero_or_nonzero", flip))
        variants.append(("wrong_type", "MUTATION_WRONG_TYPE"))
        for tag, value in variants:
            payload = copy.deepcopy(valid)
            payload[field] = value
            add("COUNTER_MUTATION", f"{field}_{tag}", payload)
    elif kind == "DIGEST_EQUALITY":
        payload = copy.deepcopy(valid)
        payload[rel["targetField"]] = "0" * 64
        add("ONE_SIDE_RELATION_CHANGE", rel["relationId"], payload)
    elif kind == "FIELD_EQUALITY":
        field = rel["targetField"] if rel["targetField"] in valid else rel["sourceField"]
        if field in valid:
            payload = copy.deepcopy(valid)
            payload[field] = _different_scalar(payload[field])
            add("ONE_SIDE_RELATION_CHANGE", rel["relationId"], payload)
    else:
        raise ValueError(f"unsupported relation: {kind!r}")


def generate_mutations(matrix: dict[str, Any], shape_id: str, valid: dict[str, Any]) -> list[Mutation]:
    excluded = {(e["operator"], e["shapeId"]) for e in matrix.get("mutationPolicy", {}).get("excludedOperators", [])}
    shape = _find_shape(matrix, shape_id)
    result: list[Mutation] = []
    seen: set[str] = set()

    def add(operator: str, suffix: str, payload: dict[str, Any]) -> None:
        if (operator, shape_id) in excluded:
            return
        mutation_id = f"{shape_id}::{operator}::{suffix}"
        if mutation_id in seen:
            raise ValueError(f"duplicate mutation id: {mutation_id}")
        seen.add(mutation_id)
        result.append(Mutation(mutation_id, operator, shape_id, payload))

    for field in shape["requiredFields"]:
        payload = copy.deepcopy(valid)
        payload.pop(field, None)
        add("DELETE_REQUIRED_FIELD", field, payload)
    for field in shape["forbiddenFields"]:
        payload = copy.deepcopy(valid)
        payload[field] = "MUTATION_INJECTED_VALUE"
        add("ADD_FORBIDDEN_FIELD", field, payload)
    payload = copy.deepcopy(valid)
    payload["__unknown_mutation_field__"] = True
    add("ADD_UNKNOWN_FIELD", "closed_boundary", payload)
    owner = next(o["outcomeId"] for o in matrix["outcomes"] if any(s["shapeId"] == shape_id for s in o["shapes"]))
    for sibling in (o["outcomeId"] for o in matrix["outcomes"] if o["outcomeId"] != owner):
        payload = copy.deepcopy(valid)
        payload["outcome"] = sibling
        add("REPLACE_DISCRIMINATOR", sibling, payload)
    payload = copy.deepcopy(valid)
    payload["outcome"] = "UNKNOWN_MUTATION_OUTCOME"
    add("REPLACE_DISCRIMINATOR", "unknown_value", payload)
    for field, domain in shape["fieldDomains"].items():
        if field not in valid:
            continue
        payload = copy.deepcopy(valid)
        payload[field] = _wrong_type(domain)
        add("WRONG_TYPE", field, payload)
        constraint = _constraint_witness(domain)
        if constraint:
            operator, value = constraint
            payload = copy.deepcopy(valid)
            payload[field] = value
            add(operator, field, payload)
    for rule in shape["conditionalRules"]:
        _conditional(rule, valid, add)
    for relation in shape["relations"]:
        _relations(relation, valid, add)
    for field, domain in shape["fieldDomains"].items():
        if domain.get("type") == "NESTED_OBJECT" and isinstance(valid.get(field), dict):
            for nested in generate_mutations(matrix, domain["nestedShapeId"], valid[field]):
                payload = copy.deepcopy(valid)
                payload[field] = nested.payload
                add("RECURSE_NESTED_OBJECTS", f"{field}::{nested.mutationId}", payload)
    return result


_illegal_value_for_domain = _wrong_type

__all__ = ["Mutation", "generate_mutations", "_illegal_value_for_domain"]
