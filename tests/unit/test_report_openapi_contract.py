"""P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE — OpenAPI contract tests (SPEC
R28, AC-23/24).

Chained mechanical proof that the OpenAPI delta from this tranche is exactly
the five new Report operations/schemas plus the FreezeInput deprecation
markers (SPEC R19) - no unrelated path, schema, parameter or response may
have moved. Mirrors the shift-create/message-admission delta proof pattern.
"""

from __future__ import annotations

import hashlib
import json
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# The post-message-admission, pre-report value - this WAS
# PRE_MESSAGE_ADMISSION_OPENAPI_SHA's successor GOLDEN_OPENAPI_SHA before
# this tranche. Imported (not retyped) from test_p2b_openapi_contract.py so
# both files can never silently drift.
from test_p2b_openapi_contract import (  # noqa: E402
    PRE_REPORT_OPENAPI_SHA,
    _strip_assignment_delta,
)
from test_c3b_read_openapi_contract import _strip_c3b_read_delta  # noqa: E402

_REPORT_PATHS = {
    "/reports",
    "/reports/{report_id}",
    "/reports/{report_id}/versions",
    "/reports/{report_id}/submit-review",
    "/reports/{report_id}/approve",
}
# F7 repair: submit-review/approve take NO request body at all (not even an
# empty-shape one) - so unlike the pre-repair draft, there is no ReviewInput/
# ApproveInput schema for this tranche to introduce or strip.
_REPORT_SCHEMAS = {
    "ReportCreateInput",
    "ReportResponse",
    "ReportSection",
    "ReportSourceRef",
    "ReportStatus",
    "ReportType",
    "ReportVersionInput",
}


def _strip_freeze_input_deprecation_delta(doc: dict) -> None:
    """Reverse the COMPLETE FreezeInput delta (SPEC R19), in place: removes
    `additionalProperties: false` and the `deprecated` marker/description
    this tranche added to both legacy fields, restoring the pre-tranche
    permissive shape. Raises on any missing/moved key so a silent no-op can
    never mask a regression."""
    schema = doc["components"]["schemas"]["FreezeInput"]
    assert schema.get("additionalProperties") is False, "FreezeInput lost its expected additionalProperties:false"
    del schema["additionalProperties"]

    override_bool = schema["properties"]["override_unimplemented_prerequisites"]
    assert override_bool.get("deprecated") is True, "override_unimplemented_prerequisites lost its deprecated marker"
    del override_bool["deprecated"]
    del override_bool["description"]

    override_reason = schema["properties"]["override_reason"]
    assert override_reason.get("deprecated") is True, "override_reason lost its deprecated marker"
    del override_reason["deprecated"]
    del override_reason["description"]


def _strip_report_delta(doc: dict) -> None:
    for path in _REPORT_PATHS:
        assert path in doc["paths"], f"report path missing: {path}"
        del doc["paths"][path]
    for schema in _REPORT_SCHEMAS:
        assert schema in doc["components"]["schemas"], f"report schema missing: {schema}"
        del doc["components"]["schemas"][schema]
    _strip_freeze_input_deprecation_delta(doc)


def test_report_paths_and_schemas_present():
    from workspace_api.main import app

    doc = app.openapi()
    assert _REPORT_PATHS <= doc["paths"].keys()
    assert _REPORT_SCHEMAS <= doc["components"]["schemas"].keys()


def test_report_endpoints_require_authentication():
    from workspace_api.main import app

    doc = app.openapi()
    for path in _REPORT_PATHS:
        for method, op in doc["paths"][path].items():
            assert "security" in op, f"{method.upper()} {path} has no security requirement"


def test_report_request_models_forbid_extra_fields():
    from workspace_api.main import app

    doc = app.openapi()
    for schema_name in ("ReportCreateInput", "ReportVersionInput"):
        assert doc["components"]["schemas"][schema_name].get("additionalProperties") is False


def test_report_submit_review_and_approve_have_no_request_body():
    """F7: these two operations take no request body at all - not even an
    empty-shape one - so OpenAPI must omit `requestBody` entirely."""
    from workspace_api.main import app

    doc = app.openapi()
    for path in ("/reports/{report_id}/submit-review", "/reports/{report_id}/approve"):
        assert "requestBody" not in doc["paths"][path]["post"]


def test_report_response_has_no_nested_content_property():
    from workspace_api.main import app

    doc = app.openapi()
    props = doc["components"]["schemas"]["ReportResponse"]["properties"]
    assert "content" not in props
    assert set(props.keys()) == {
        "report_id", "shift_id", "report_type", "version", "status", "is_current",
        "sections", "source_manifest", "snapshot_digest", "generated_from_cutoff", "created_at",
    }


def test_openapi_delta_is_exactly_the_report_operations_and_freeze_deprecation():
    """SPEC R28/AC-23: mechanical proof. Strips exactly the five Report
    operations/schemas plus the FreezeInput deprecation delta, and re-hashes
    the remainder against the exact pre-tranche golden document."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b_read_delta(reduced)
    _strip_assignment_delta(reduced)
    _strip_report_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_REPORT_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_unrelated_path_addition_fails_the_golden_chain():
    """Negative protection: an undisclosed new path must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_report_delta(reduced)
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_REPORT_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect an undisclosed path "
        "addition - the proof is not actually structural"
    )


def test_unrelated_mutation_route_removal_fails_the_golden_chain():
    """Negative protection: silently dropping a pre-existing operation must
    fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_report_delta(reduced)

    assert "post" in reduced["paths"]["/shifts"], (
        "test fixture assumption broken: /shifts no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/shifts"]["post"]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_REPORT_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion - the proof is not actually structural"
    )
