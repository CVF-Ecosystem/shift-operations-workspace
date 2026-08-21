"""P4-A SPEC R9 - structured-output schema validation.

NOT GOVERNANCE PROOF: mechanical schema tests. R13's live run proves invalid
real provider output is actually rejected end to end.
"""

from __future__ import annotations

import pytest

from ai_gateway.errors import OutputSchemaError
from ai_gateway.validation import validate_output

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "count"],
    "properties": {
        "status": {"type": "string", "enum": ["ok", "error"]},
        "count": {"type": "integer", "minimum": 0, "maximum": 10},
        "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
    },
}


class TestTopLevel:
    def test_valid_object_accepted(self):
        validate_output({"status": "ok", "count": 1}, SCHEMA)

    def test_non_object_output_rejected(self):
        for value in ("string", 5, [1], None, True):
            with pytest.raises(OutputSchemaError):
                validate_output(value, SCHEMA)

    def test_non_object_schema_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({}, {"type": "string"})


class TestRequiredAndAdditional:
    def test_missing_required_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok"}, SCHEMA)

    def test_unexpected_property_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": 1, "extra": 1}, SCHEMA)


class TestTypesAndBounds:
    def test_wrong_property_type_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": "1"}, SCHEMA)

    def test_bool_is_not_an_integer(self):
        """bool subclasses int in Python; the validator must not accept it."""
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": True}, SCHEMA)

    def test_below_minimum_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": -1}, SCHEMA)

    def test_above_maximum_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": 11}, SCHEMA)

    def test_enum_violation_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "maybe", "count": 1}, SCHEMA)


class TestArrays:
    def test_valid_array_accepted(self):
        validate_output({"status": "ok", "count": 1, "tags": ["a", "b"]}, SCHEMA)

    def test_wrong_item_type_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": 1, "tags": ["a", 2]}, SCHEMA)

    def test_max_items_enforced(self):
        with pytest.raises(OutputSchemaError):
            validate_output({"status": "ok", "count": 1, "tags": ["a", "b", "c", "d"]}, SCHEMA)

    def test_min_items_enforced(self):
        schema = {
            "type": "object",
            "required": ["tags"],
            "properties": {"tags": {"type": "array", "items": {"type": "string"}, "minItems": 2}},
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"tags": ["a"]}, schema)


class TestStrings:
    def test_min_and_max_length_enforced(self):
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "minLength": 2, "maxLength": 4}},
        }
        validate_output({"name": "abc"}, schema)
        with pytest.raises(OutputSchemaError):
            validate_output({"name": "a"}, schema)
        with pytest.raises(OutputSchemaError):
            validate_output({"name": "abcde"}, schema)


class TestNested:
    def test_nested_object_validated(self):
        schema = {
            "type": "object",
            "required": ["inner"],
            "properties": {
                "inner": {
                    "type": "object",
                    "required": ["flag"],
                    "properties": {"flag": {"type": "boolean"}},
                }
            },
        }
        validate_output({"inner": {"flag": True}}, schema)
        with pytest.raises(OutputSchemaError):
            validate_output({"inner": {"flag": "yes"}}, schema)

    def test_unsupported_type_keyword_fails_closed(self):
        schema = {"type": "object", "properties": {"x": {"type": "weird"}}}
        with pytest.raises(OutputSchemaError):
            validate_output({"x": 1}, schema)


class TestPattern:
    def test_matching_pattern_accepted(self):
        schema = {
            "type": "object",
            "required": ["code"],
            "properties": {"code": {"type": "string", "pattern": r"^[A-Z]{3}-\d{4}$"}},
        }
        validate_output({"code": "ABC-1234"}, schema)

    def test_non_matching_pattern_rejected(self):
        """P4A-REV-F1: pattern must actually be enforced, not silently ignored."""
        schema = {
            "type": "object",
            "required": ["code"],
            "properties": {"code": {"type": "string", "pattern": r"^[A-Z]{3}-\d{4}$"}},
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"code": "not-a-match"}, schema)

    def test_invalid_pattern_regex_fails_closed(self):
        schema = {
            "type": "object",
            "properties": {"code": {"type": "string", "pattern": "("}},
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"code": "x"}, schema)

    def test_non_string_pattern_fails_closed(self):
        schema = {"type": "object", "properties": {"code": {"type": "string", "pattern": 123}}}
        with pytest.raises(OutputSchemaError):
            validate_output({"code": "x"}, schema)


class TestOneOf:
    ONE_OF_SCHEMA = {
        "type": "object",
        "required": ["value"],
        "properties": {
            "value": {
                "oneOf": [
                    {"type": "string", "enum": ["a"]},
                    {"type": "integer", "minimum": 10},
                ]
            }
        },
    }

    def test_exactly_one_branch_matches_accepted(self):
        validate_output({"value": "a"}, self.ONE_OF_SCHEMA)
        validate_output({"value": 11}, self.ONE_OF_SCHEMA)

    def test_zero_branches_match_rejected(self):
        """P4A-REV-F1: oneOf must actually be enforced, not silently ignored."""
        with pytest.raises(OutputSchemaError):
            validate_output({"value": "b"}, self.ONE_OF_SCHEMA)
        with pytest.raises(OutputSchemaError):
            validate_output({"value": 5}, self.ONE_OF_SCHEMA)

    def test_multiple_branches_match_rejected(self):
        """JSON Schema oneOf semantics: exactly one match, not any-of."""
        schema = {
            "type": "object",
            "required": ["value"],
            "properties": {
                "value": {"oneOf": [{"type": "integer", "minimum": 0}, {"type": "integer", "maximum": 100}]}
            },
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"value": 50}, schema)

    def test_empty_one_of_fails_closed(self):
        schema = {"type": "object", "properties": {"value": {"oneOf": []}}}
        with pytest.raises(OutputSchemaError):
            validate_output({"value": 1}, schema)


class TestMalformedSchema:
    def test_non_object_top_level_schema_rejected(self):
        with pytest.raises(OutputSchemaError):
            validate_output({}, {"type": "object", "properties": "not-an-object"})

    def test_non_object_items_schema_rejected(self):
        schema = {"type": "object", "properties": {"tags": {"type": "array", "items": "nope"}}}
        with pytest.raises(OutputSchemaError):
            validate_output({"tags": [1]}, schema)

    def test_non_list_one_of_rejected(self):
        schema = {"type": "object", "properties": {"x": {"oneOf": "not-a-list"}}}
        with pytest.raises(OutputSchemaError):
            validate_output({"x": 1}, schema)


class TestNestedUnsupportedKeywords:
    def test_unsupported_keyword_in_nested_property_fails_closed(self):
        """P4A-REV-F1: unsupported keywords must fail closed at every nesting level."""
        schema = {
            "type": "object",
            "properties": {"inner": {"type": "object", "properties": {"x": {"type": "string", "format": "email"}}}},
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"inner": {"x": "a@b.com"}}, schema)

    def test_unsupported_keyword_in_items_fails_closed(self):
        schema = {
            "type": "object",
            "properties": {"tags": {"type": "array", "items": {"type": "string", "contains": "x"}}},
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"tags": ["a"]}, schema)

    def test_unsupported_keyword_in_one_of_branch_fails_closed(self):
        schema = {
            "type": "object",
            "properties": {"x": {"oneOf": [{"type": "string"}, {"type": "integer", "multipleOf": 2}]}},
        }
        with pytest.raises(OutputSchemaError):
            validate_output({"x": "a"}, schema)

    def test_unsupported_top_level_keyword_fails_closed(self):
        schema = {"type": "object", "unevaluatedProperties": False}
        with pytest.raises(OutputSchemaError):
            validate_output({}, schema)


class TestMalformedKeywordValueShapes:
    """P4A-REV-F1: malformed supported-keyword value shapes must fail closed."""

    @pytest.mark.parametrize(
        "schema, value",
        [
            ({"type": "object", "properties": {"x": {"type": ["string", "integer"]}}}, {"x": "a"}),
            ({"type": "object", "additionalProperties": "false"}, {}),
            ({"type": "object", "properties": {"count": {"type": "integer", "minimum": "0"}}}, {"count": 1}),
            ({"type": "object", "properties": {"count": {"type": "integer", "maximum": "10"}}}, {"count": 1}),
            ({"type": "object", "properties": {"name": {"type": "string", "minLength": "2"}}}, {"name": "abc"}),
            ({"type": "object", "properties": {"name": {"type": "string", "maxLength": "4"}}}, {"name": "abc"}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "minItems": "1"}}}, {"tags": ["a"]}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "maxItems": "3"}}}, {"tags": ["a"]}),
            ({"type": "object", "required": "status"}, {"status": "ok"}),
            ({"type": "object", "properties": {"count": {"type": "integer", "minimum": True}}}, {"count": 1}),
            ({"type": "object", "properties": {"count": {"type": "integer", "maximum": False}}}, {"count": 1}),
            ({"type": "object", "properties": {"name": {"type": "string", "minLength": True}}}, {"name": "abc"}),
            ({"type": "object", "properties": {"name": {"type": "string", "maxLength": False}}}, {"name": "abc"}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "minItems": True}}}, {"tags": ["a"]}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "maxItems": False}}}, {"tags": ["a"]}),
            # equivalent malformed shapes nested inside properties/items/oneOf
            ({"type": "object", "properties": {"inner": {"type": "object", "properties": {"x": {"type": ["string"]}}}}}, {"inner": {"x": "a"}}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": ["string"]}}}}, {"tags": ["a"]}),
            ({"type": "object", "properties": {"x": {"oneOf": [{"type": ["string"]}, {"type": "integer"}]}}}, {"x": "a"}),
            ({"type": "object", "properties": {"inner": {"type": "object", "required": "flag"}}}, {"inner": {"flag": True}}),
            ({"type": "object", "properties": {"inner": {"type": "object", "additionalProperties": "false"}}}, {"inner": {}}),
            ({"type": "object", "properties": {"nums": {"type": "array", "items": {"type": "integer", "minimum": "0"}}}}, {"nums": [1]}),
            ({"type": "object", "properties": {"inner": {"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "maxItems": True}}}}}, {"inner": {"tags": ["a"]}}),
            ({"type": "object", "properties": {"name": {"type": "string", "minLength": -1}}}, {"name": "abc"}),
            ({"type": "object", "properties": {"name": {"type": "string", "maxLength": -1}}}, {"name": "abc"}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "minItems": -1}}}, {"tags": ["a"]}),
            ({"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}, "maxItems": -1}}}, {"tags": ["a"]}),
            ({"type": "object", "required": ["status", "status"]}, {"status": "ok"}),
            ({"type": "object", "properties": {"status": {"type": "string", "enum": ["ok", "ok"]}}}, {"status": "ok"}),
            ({"type": "object", "properties": {1: {"type": "string"}}}, {}),
            ({"type": "object", "properties": {"count": {"type": "integer", "minimum": float("inf")}}}, {"count": 1}),
            ({"type": "object", "properties": {"count": {"type": "integer", "maximum": float("nan")}}}, {"count": 1}),
        ],
    )
    def test_malformed_keyword_value_shape_fails_closed(self, schema, value):
        with pytest.raises(OutputSchemaError):
            validate_output(value, schema)
