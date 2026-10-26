"""Exact OpenAPI delta contract for the bounded P5-A2 source route."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

_SOURCE_PATH = "/proactive/source"
_READY = "P5A2ReadyReceipt"
_REFUSED = "P5A2RefusedReceipt"
_FIXTURE_SHA = "64b5123445e1e9a6f6ac123c809d57414a511412fe0b1ea575c2bf5fecf27dbf"
_READY_FIELDS = {
    "actor_id", "candidate_version_count", "canonical_manifest",
    "cohort_policy_version", "coverage_mode", "eligible_count",
    "max_snapshot_incident_refs", "numeric_policy_version", "outcome",
    "query_end", "query_start", "receipt_version", "run_as_of", "scope_id",
    "selected_count", "source_digest",
}
_REFUSED_FIELDS = {
    "cohort_policy_version", "numeric_policy_version", "outcome", "reason",
    "receipt_version",
}
_QUERY_PARAMETERS = [
    {
        "name": name,
        "in": "query",
        "required": True,
        "schema": {"type": "string", "format": "date-time", "maxLength": 128},
    }
    for name in ("query_start", "query_end", "run_as_of")
]


def _frozen_delta() -> dict:
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "p5a2_source_openapi_delta.json"
    raw = fixture_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _FIXTURE_SHA
    delta = json.loads(raw)
    assert set(delta) == {"paths", "schemas"}
    assert set(delta["paths"]) == {_SOURCE_PATH}
    assert set(delta["paths"][_SOURCE_PATH]) == {"get"}
    assert set(delta["schemas"]) == {_READY, _REFUSED}

    operation = delta["paths"][_SOURCE_PATH]["get"]
    assert operation["tags"] == ["proactive"]
    assert operation["summary"] == "Read Source"
    assert operation["operationId"] == "read_source_proactive_source_get"
    assert operation["security"] == [{"HTTPBearer": []}]
    assert operation["parameters"] == _QUERY_PARAMETERS
    assert set(operation["responses"]) == {"200", "401", "403", "422"}
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["anyOf"] == [
        {"$ref": f"#/components/schemas/{_READY}"},
        {"$ref": f"#/components/schemas/{_REFUSED}"},
    ]
    assert operation["responses"]["401"]["description"] == "Authentication required"
    assert operation["responses"]["403"]["description"] == "Access denied"
    assert operation["responses"]["422"]["description"] == "Invalid request"

    for name, fields in ((_READY, _READY_FIELDS), (_REFUSED, _REFUSED_FIELDS)):
        schema = delta["schemas"][name]
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == fields
        assert set(schema["properties"]) == fields
    return delta


def _strip_p5a_source_delta(doc: dict) -> None:
    """Validate the full frozen source leaf, then remove exactly its three objects."""
    delta = _frozen_delta()
    paths = doc["paths"]
    assert _SOURCE_PATH in paths, "P5-A2 source path missing"
    assert set(paths[_SOURCE_PATH]) == {"get"}, "P5-A2 source method set changed"
    assert paths[_SOURCE_PATH]["get"] == delta["paths"][_SOURCE_PATH]["get"], "P5-A2 source operation changed"

    schemas = doc["components"]["schemas"]
    for name in (_READY, _REFUSED):
        assert name in schemas, f"P5-A2 source schema {name} missing"
        assert schemas[name] == delta["schemas"][name], f"P5-A2 source schema {name} changed"

    del paths[_SOURCE_PATH]
    del schemas[_READY]
    del schemas[_REFUSED]


def _openapi() -> dict:
    from workspace_api.main import app

    return copy.deepcopy(app.openapi())


def _assert_rejected_without_more_mutation(change) -> None:
    doc = _openapi()
    change(doc)
    changed = copy.deepcopy(doc)
    with pytest.raises(AssertionError):
        _strip_p5a_source_delta(doc)
    assert doc == changed


def test_source_leaf_removes_only_the_frozen_operation_and_schemas():
    doc = _openapi()
    expected = copy.deepcopy(doc)
    del expected["paths"][_SOURCE_PATH]
    del expected["components"]["schemas"][_READY]
    del expected["components"]["schemas"][_REFUSED]
    _strip_p5a_source_delta(doc)
    assert doc == expected


@pytest.mark.parametrize(
    "change",
    [
        lambda doc: doc["paths"].pop(_SOURCE_PATH),
        lambda doc: doc["paths"][_SOURCE_PATH].update(post={"responses": {"200": {}}}),
        lambda doc: doc["paths"][_SOURCE_PATH]["get"].update(security=[]),
        lambda doc: doc["paths"][_SOURCE_PATH]["get"]["parameters"][0]["schema"].update(maxLength=127),
        lambda doc: doc["paths"][_SOURCE_PATH]["get"]["responses"]["401"].update(description="Changed"),
        lambda doc: doc["components"]["schemas"][_READY]["properties"]["outcome"].update(title="Changed"),
        lambda doc: doc["components"]["schemas"][_REFUSED]["properties"]["reason"].update(title="Changed"),
        lambda doc: doc["components"]["schemas"].pop(_READY),
        lambda doc: doc["components"]["schemas"].pop(_REFUSED),
    ],
    ids=[
        "missing-path", "extra-method", "changed-security", "changed-query",
        "changed-response", "ready-schema", "refused-schema",
        "missing-ready-schema", "missing-refused-schema",
    ],
)
def test_changed_source_delta_is_rejected_before_any_deletion(change):
    _assert_rejected_without_more_mutation(change)


def test_unknown_path_and_schema_remain_after_source_leaf_removal():
    doc = _openapi()
    unknown_path = "/unrelated-probe"
    unknown_schema = "UnrelatedProbe"
    doc["paths"][unknown_path] = {"get": {"responses": {"200": {}}}}
    doc["components"]["schemas"][unknown_schema] = {"type": "object"}
    _strip_p5a_source_delta(doc)
    assert unknown_path in doc["paths"]
    assert doc["components"]["schemas"][unknown_schema] == {"type": "object"}
