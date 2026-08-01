"""P2C-MUTATION-FULL-UI-C3B2 — OpenAPI contract tests (SPEC R13/R15, AC-13,
AC-16).

Chained mechanical proof of the exact C3b2 delta. Unlike every earlier link
in this chain, C3b2 adds no new path and one merged schema (incident's and
handover's ``AcknowledgeInput`` became structurally identical and FastAPI
deduplicated them): it tightens nine existing request-body schemas
(``ConfirmInput``, ``CorrectEventInput``, the three ``TransitionInput``
variants, ``AcknowledgeInput``, ``ReviewInput``, ``FreezeInput``,
``ReportVersionInput``) with a required ``expected_version``
(``ReportVersionInput`` also gains ``expected_status``), adds two brand-new
schemas (``CloseInput``, ``ReportPreconditionInput``) for the two routes that
previously took no/an optional body, and adds ``version`` to the
``CustomerRequest`` response schema. ``_strip_c3b2_mutation_delta`` reverses
every one of those changes in place, mirroring the exact-set discipline
``_strip_c3b_read_delta`` established.

Chain: ... -> `PRE_C3B_READ_OPENAPI_SHA` -> (C3b1's own prior
`GOLDEN_OPENAPI_SHA`, now `PRE_C3B2_MUTATION_OPENAPI_SHA`) -> current
`GOLDEN_OPENAPI_SHA`.
"""

from __future__ import annotations

import hashlib
import json
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

from test_c3b_read_openapi_contract import (  # noqa: E402
    GOLDEN_OPENAPI_SHA as PRE_C3B2_MUTATION_OPENAPI_SHA,
    _strip_c3b_read_delta,
)


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Post-C3b1 (imported above), pre-C3b2. Post-C3b2: PRE_C3B2_MUTATION_OPENAPI_SHA
# plus the exact mutation-precondition delta below. Computed mechanically,
# pinned once the delta proof passes.
GOLDEN_OPENAPI_SHA = "a85bd8909ca88aba97d57825f3457ce9e5ef52979234db71b08a5ad05a20d211"

_C3B2_NEW_SCHEMAS = {"CloseInput", "ReportPreconditionInput"}

# Existing schemas whose *properties* the C3b2 precondition tightening
# changed in place - no schema name added or removed for these.
_C3B2_TIGHTENED_SCHEMAS = {
    "ConfirmInput", "CorrectEventInput", "AcknowledgeInput", "ReviewInput",
    "FreezeInput", "ReportVersionInput",
    "workspace_api__api__customer_requests__router__TransitionInput",
    "workspace_api__api__incidents__router__TransitionInput",
    "workspace_api__api__tasks__router__TransitionInput",
}

_NEW_BODY_OPERATIONS = {
    ("/shifts/{shift_id}/close", "post"): "CloseInput",
    ("/reports/{report_id}/submit-review", "post"): "ReportPreconditionInput",
    ("/reports/{report_id}/approve", "post"): "ReportPreconditionInput",
}


def _strip_c3b2_mutation_delta(doc: dict) -> None:
    """Remove exactly the C3b2 delta, in place. Raises on any missing/moved
    key so a silent no-op can never mask a regression."""
    schemas = doc["components"]["schemas"]

    for path, method in _NEW_BODY_OPERATIONS:
        op = doc["paths"][path][method]
        assert "requestBody" in op, f"C3b2 requestBody missing: {method.upper()} {path}"
        del op["requestBody"]

    freeze_body = doc["paths"]["/shifts/{shift_id}/freeze"]["post"]["requestBody"]
    assert freeze_body["required"] is True
    freeze_body["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/FreezeInput",
        "default": {"override_unimplemented_prerequisites": False},
    }
    del freeze_body["required"]

    for schema_name in _C3B2_NEW_SCHEMAS:
        assert schema_name in schemas, f"C3b2 schema missing: {schema_name}"
        del schemas[schema_name]

    for schema_name in _C3B2_TIGHTENED_SCHEMAS:
        assert schema_name in schemas, f"C3b2-tightened schema missing: {schema_name}"
        schema = schemas[schema_name]
        assert "expected_version" in schema["properties"], schema_name
        del schema["properties"]["expected_version"]
        schema["required"] = [f for f in schema.get("required", []) if f != "expected_version"]
        if schema_name == "ReportVersionInput":
            assert "expected_status" in schema["properties"], schema_name
            del schema["properties"]["expected_status"]
            schema["required"] = [f for f in schema["required"] if f != "expected_status"]
        if not schema["required"]:
            del schema["required"]

    # Two PRE forms lacked additionalProperties=false (customer_requests'/
    # tasks' TransitionInput never declared it; ReportVersionInput already
    # had it pre-C3b2, unlike ConfirmInput/AcknowledgeInput/ReviewInput).
    for schema_name in (
        "workspace_api__api__customer_requests__router__TransitionInput",
        "workspace_api__api__tasks__router__TransitionInput",
    ):
        del schemas[schema_name]["additionalProperties"]

    version_prop = schemas["CustomerRequest"]["properties"]
    assert "version" in version_prop, "CustomerRequest.version schema missing"
    del version_prop["version"]


def test_openapi_delta_is_exactly_the_c3b2_mutation_precondition_changes():
    """AC-13/AC-16: mechanical proof, not an assertion of trust. Strips ONLY
    the C3b2 delta, re-hashing against PRE_C3B2_MUTATION_OPENAPI_SHA."""
    from workspace_api.main import app

    doc = app.openapi()
    for schema_name in _C3B2_NEW_SCHEMAS | _C3B2_TIGHTENED_SCHEMAS:
        assert schema_name in doc["components"]["schemas"], schema_name

    reduced = json.loads(json.dumps(doc))
    _strip_c3b2_mutation_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_C3B2_MUTATION_OPENAPI_SHA, actual.decode("utf-8")[:6000]


def test_openapi_document_is_the_new_golden_value():
    """The full current document, including the C3b2 delta, matches the
    pinned current GOLDEN_OPENAPI_SHA."""
    from workspace_api.main import app

    actual = canonical(app.openapi())
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:6000]


def test_unrelated_path_addition_fails_the_golden_chain():
    """Negative protection: an undisclosed new path must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b2_mutation_delta(reduced)
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_C3B2_MUTATION_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect an undisclosed path "
        "addition - the proof is not actually structural"
    )


def test_unrelated_mutation_route_removal_fails_the_golden_chain():
    """Negative protection: silently dropping a pre-existing operation must
    fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b2_mutation_delta(reduced)

    assert "post" in reduced["paths"]["/shifts"], (
        "test fixture assumption broken: /shifts no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/shifts"]["post"]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_C3B2_MUTATION_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion - the proof is not actually structural"
    )


def test_protected_create_and_approval_operations_have_zero_delta():
    """Work Order section 3.4: create/append/task-intent/approval-receipt
    operations show no OpenAPI delta from this tranche."""
    from workspace_api.main import app

    doc = app.openapi()
    protected_schemas = (
        "EventInput", "TaskInput", "TaskCreationIntentInput",
        "CustomerRequestInput", "IncidentInput", "HandoverCreateInput",
        "ApprovalCreateInput", "ReportCreateInput",
    )
    for schema_name in protected_schemas:
        schema = doc["components"]["schemas"][schema_name]
        assert "expected_version" not in schema.get("properties", {}), schema_name
        assert "expected_status" not in schema.get("properties", {}), schema_name


def test_close_and_report_precondition_schemas_are_exact():
    from workspace_api.main import app

    schemas = app.openapi()["components"]["schemas"]
    assert schemas["CloseInput"]["additionalProperties"] is False
    assert set(schemas["CloseInput"]["properties"].keys()) == {"expected_version"}
    assert schemas["CloseInput"]["required"] == ["expected_version"]

    assert schemas["ReportPreconditionInput"]["additionalProperties"] is False
    assert set(schemas["ReportPreconditionInput"]["properties"].keys()) == {
        "expected_version", "expected_status",
    }
    assert set(schemas["ReportPreconditionInput"]["required"]) == {
        "expected_version", "expected_status",
    }


def test_customer_request_response_includes_version():
    from workspace_api.main import app

    props = app.openapi()["components"]["schemas"]["CustomerRequest"]["properties"]
    assert "version" in props
    assert props["version"]["minimum"] == 1.0
