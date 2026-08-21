"""Structured-output validation (SPEC R9).

A deliberately small, dependency-free JSON Schema subset: the gateway must not
take a runtime dependency on a schema library to stay a pure package (R1). The
supported keywords are exactly those the gateway's own contract schema uses.

Validation is fail-closed: an unsupported keyword at any level of the schema -
top level, `properties` subschema, `items` subschema, or `oneOf` branch -
rejects the output rather than silently widening acceptance. This is checked
before value validation begins, so a caller cannot smuggle a wider match past
an unrecognized constraint.

Supported schema keys: ``type`` (object/array/string/integer/number/boolean/
null), ``properties``, ``required``, ``additionalProperties`` (bool),
``items``, ``enum``, ``oneOf``, ``pattern``, ``minimum``, ``maximum``,
``minLength``, ``maxLength``, ``minItems``, ``maxItems``.
"""

from __future__ import annotations

import math
import re
from typing import Any

from .errors import OutputSchemaError

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    # bool is a subclass of int in Python; exclude it explicitly.
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "null": lambda v: v is None,
}

_SUPPORTED_KEYS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "oneOf",
    "pattern",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
}


def validate_output(value: Any, schema: dict[str, Any]) -> None:
    """Raise :class:`OutputSchemaError` unless ``value`` satisfies ``schema``.

    Fail-closed: every schema and subschema reachable from ``schema`` is
    checked for unsupported keys before any value is matched.
    """
    if schema.get("type") != "object":
        raise OutputSchemaError("output schema must declare type 'object'")
    _assert_supported(schema, path="$")
    if not isinstance(value, dict):
        raise OutputSchemaError("provider output must be a JSON object")
    _validate(value, schema, path="$")


def _is_integer(value: Any) -> bool:
    """``bool`` subclasses ``int``; bounds must be genuine integers, not booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _has_duplicates(values: list[Any]) -> bool:
    """True if any two members are equal; uses ``==`` so unhashable members work."""
    for index, value in enumerate(values):
        if any(value == other for other in values[index + 1:]):
            return True
    return False


def _assert_supported(schema: dict[str, Any], *, path: str) -> None:
    """Reject any unsupported keyword or malformed value shape before matching.

    Fail-closed in two dimensions: a schema node may use only the supported
    keyword *names* and, for every supported keyword it declares, only the
    exact value shape this validator implements. An invalid constraint is
    rejected here, before any value is matched, so a caller cannot smuggle a
    wider match past a misread keyword.
    """
    if not isinstance(schema, dict):
        raise OutputSchemaError(f"{path}: schema node must be an object")
    unsupported = sorted(set(schema) - _SUPPORTED_KEYS)
    if unsupported:
        raise OutputSchemaError(f"{path}: unsupported schema keyword(s) {unsupported}")

    if "type" in schema:
        declared = schema["type"]
        if not isinstance(declared, str):
            raise OutputSchemaError(f"{path}.type: must be a string")
        if declared not in _TYPE_CHECKS:
            raise OutputSchemaError(f"{path}.type: unsupported schema type {declared!r}")

    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            raise OutputSchemaError(f"{path}.properties: must be an object")
        for key, subschema in properties.items():
            if not isinstance(key, str):
                raise OutputSchemaError(f"{path}.properties: property names must be strings")
            _assert_supported(subschema, path=f"{path}.properties.{key}")

    required = schema.get("required")
    if required is not None:
        if not isinstance(required, list):
            raise OutputSchemaError(f"{path}.required: must be an array")
        if any(not isinstance(entry, str) for entry in required):
            raise OutputSchemaError(f"{path}.required: entries must be strings")
        if _has_duplicates(required):
            raise OutputSchemaError(f"{path}.required: entries must be unique")

    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise OutputSchemaError(f"{path}.additionalProperties: must be a boolean")

    items = schema.get("items")
    if items is not None:
        _assert_supported(items, path=f"{path}.items")

    if "enum" in schema:
        allowed = schema["enum"]
        if not isinstance(allowed, list) or not allowed:
            raise OutputSchemaError(f"{path}.enum: must be a non-empty array")
        if _has_duplicates(allowed):
            raise OutputSchemaError(f"{path}.enum: members must be unique")

    one_of = schema.get("oneOf")
    if one_of is not None:
        if not isinstance(one_of, list) or not one_of:
            raise OutputSchemaError(f"{path}.oneOf: must be a non-empty array")
        for index, branch in enumerate(one_of):
            _assert_supported(branch, path=f"{path}.oneOf[{index}]")

    pattern = schema.get("pattern")
    if pattern is not None:
        if not isinstance(pattern, str):
            raise OutputSchemaError(f"{path}.pattern: must be a string")
        try:
            re.compile(pattern)
        except re.error as exc:
            raise OutputSchemaError(f"{path}.pattern: invalid regex ({exc})") from exc

    for keyword in ("minimum", "maximum"):
        if keyword in schema:
            bound = schema[keyword]
            if not _is_number(bound):
                raise OutputSchemaError(f"{path}.{keyword}: must be a number")
            if not math.isfinite(bound):
                raise OutputSchemaError(f"{path}.{keyword}: must be finite")

    for keyword in ("minLength", "maxLength", "minItems", "maxItems"):
        if keyword in schema:
            bound = schema[keyword]
            if not _is_integer(bound):
                raise OutputSchemaError(f"{path}.{keyword}: must be an integer")
            if bound < 0:
                raise OutputSchemaError(f"{path}.{keyword}: must be non-negative")


def _validate(value: Any, schema: dict[str, Any], *, path: str) -> None:
    declared = schema.get("type")
    if isinstance(declared, str):
        check = _TYPE_CHECKS.get(declared)
        if check is None:
            raise OutputSchemaError(f"{path}: unsupported schema type {declared!r}")
        if not check(value):
            raise OutputSchemaError(f"{path}: expected {declared}")

    if "enum" in schema:
        allowed = schema["enum"]
        if not isinstance(allowed, list) or value not in allowed:
            raise OutputSchemaError(f"{path}: value is not an allowed enum member")

    if "oneOf" in schema:
        _validate_one_of(value, schema["oneOf"], path=path)

    if isinstance(value, str):
        _validate_string(value, schema, path=path)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        _validate_number(value, schema, path=path)
    if isinstance(value, dict):
        _validate_object(value, schema, path=path)
    if isinstance(value, list):
        _validate_array(value, schema, path=path)


def _validate_one_of(value: Any, branches: list[Any], *, path: str) -> None:
    """Exactly one branch of ``oneOf`` must accept ``value`` (JSON Schema semantics)."""
    matches = 0
    for branch in branches:
        try:
            _validate(value, branch, path=path)
        except OutputSchemaError:
            continue
        matches += 1
    if matches != 1:
        raise OutputSchemaError(f"{path}: matched {matches} of oneOf branches, expected exactly 1")


def _validate_string(value: str, schema: dict[str, Any], *, path: str) -> None:
    minimum = schema.get("minLength")
    maximum = schema.get("maxLength")
    if isinstance(minimum, int) and len(value) < minimum:
        raise OutputSchemaError(f"{path}: shorter than minLength")
    if isinstance(maximum, int) and len(value) > maximum:
        raise OutputSchemaError(f"{path}: longer than maxLength")
    pattern = schema.get("pattern")
    if isinstance(pattern, str) and re.search(pattern, value) is None:
        raise OutputSchemaError(f"{path}: does not match pattern")


def _validate_number(value: float, schema: dict[str, Any], *, path: str) -> None:
    minimum = schema.get("minimum")
    maximum = schema.get("maximum")
    if isinstance(minimum, (int, float)) and not isinstance(minimum, bool) and value < minimum:
        raise OutputSchemaError(f"{path}: below minimum")
    if isinstance(maximum, (int, float)) and not isinstance(maximum, bool) and value > maximum:
        raise OutputSchemaError(f"{path}: above maximum")


def _validate_object(value: dict[str, Any], schema: dict[str, Any], *, path: str) -> None:
    properties = schema.get("properties")
    properties = properties if isinstance(properties, dict) else {}
    required = schema.get("required")
    for key in required if isinstance(required, list) else []:
        if key not in value:
            raise OutputSchemaError(f"{path}: missing required property {key!r}")
    if schema.get("additionalProperties") is False:
        unexpected = sorted(set(value) - set(properties))
        if unexpected:
            raise OutputSchemaError(f"{path}: unexpected properties {unexpected}")
    for key, subschema in properties.items():
        if key in value and isinstance(subschema, dict):
            _validate(value[key], subschema, path=f"{path}.{key}")


def _validate_array(value: list[Any], schema: dict[str, Any], *, path: str) -> None:
    minimum = schema.get("minItems")
    maximum = schema.get("maxItems")
    if isinstance(minimum, int) and len(value) < minimum:
        raise OutputSchemaError(f"{path}: fewer than minItems")
    if isinstance(maximum, int) and len(value) > maximum:
        raise OutputSchemaError(f"{path}: more than maxItems")
    items = schema.get("items")
    if isinstance(items, dict):
        for index, item in enumerate(value):
            _validate(item, items, path=f"{path}[{index}]")
