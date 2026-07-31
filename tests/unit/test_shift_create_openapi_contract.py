"""SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29 — OpenAPI contract tests (SPEC
R9, AC-11).

Chained mechanical proof that the OpenAPI delta from this tranche is exactly
the new bearer-security requirement on the pre-existing POST /shifts — no
new path, no new schema, no change to its query parameters, response schema
or status-contract shape. Mirrors the P2C read/incident/handover delta proof
pattern from test_p2b_openapi_contract.py / test_p2c_read_openapi_contract.py.
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


# The post-P2C-read, pre-shift-create value - imported (not retyped) from
# test_p2b_openapi_contract.py so both files can never silently drift,
# mirroring how that file itself imports PRE_P2C_READ_OPENAPI_SHA from
# test_p2c_read_openapi_contract.py.
from test_p2b_openapi_contract import PRE_SHIFT_CREATE_OPENAPI_SHA  # noqa: E402


def _strip_shifts_post_security(doc: dict) -> None:
    """Remove exactly the `security` key this tranche added to POST /shifts,
    in place. Raises if the key is missing or the path/method has moved - a
    silent no-op here would let this test pass while masking a security-
    policy regression on the shift-create mutation route."""
    post_op = doc["paths"]["/shifts"]["post"]
    assert "security" in post_op, "POST /shifts lost its expected security requirement"
    del post_op["security"]


def _strip_messages_post_delta(doc: dict) -> None:
    """MAR-BUILD-REV-F1 repair (SPEC R21): reverse the COMPLETE later
    MESSAGE-ADMISSION-TRUST-REPAIR `POST /messages` delta, in place - not
    just `security`, but also MessageInput's required order and the
    sender_id/source property shapes (both previously required plain
    strings, not optional `anyOf` fields). Asserts the current authorized
    shape before reversal; never refreshes this file's own historical
    PRE_SHIFT_CREATE_OPENAPI_SHA baseline."""
    post_op = doc["paths"]["/messages"]["post"]
    assert "security" in post_op, "POST /messages lost its expected security requirement"
    del post_op["security"]

    schema_ref = post_op["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema = doc["components"]["schemas"][schema_ref.split("/")[-1]]
    assert set(schema["required"]) == {"shift_id", "text"}, schema["required"]
    schema["required"] = ["shift_id", "sender_id", "text"]
    assert schema["properties"]["sender_id"].get("anyOf"), schema["properties"]["sender_id"]
    schema["properties"]["sender_id"] = {"title": "Sender Id", "type": "string"}
    assert schema["properties"]["source"].get("anyOf"), schema["properties"]["source"]
    schema["properties"]["source"] = {"default": "INTERNAL", "title": "Source", "type": "string"}


_REPORT_PATHS = {
    "/reports",
    "/reports/{report_id}",
    "/reports/{report_id}/versions",
    "/reports/{report_id}/submit-review",
    "/reports/{report_id}/approve",
}
_REPORT_SCHEMAS = {
    "ReportCreateInput", "ReportResponse", "ReportSection", "ReportSourceRef",
    "ReportStatus", "ReportType", "ReportVersionInput",
}


def _strip_report_delta(doc: dict) -> None:
    """P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE (SPEC R28): reverse the
    COMPLETE later report delta, in place - the five new paths/schemas plus
    the FreezeInput deprecation markers."""
    for path in _REPORT_PATHS:
        assert path in doc["paths"], f"report path missing: {path}"
        del doc["paths"][path]
    for schema in _REPORT_SCHEMAS:
        assert schema in doc["components"]["schemas"], f"report schema missing: {schema}"
        del doc["components"]["schemas"][schema]
    freeze_schema = doc["components"]["schemas"]["FreezeInput"]
    assert freeze_schema.get("additionalProperties") is False
    del freeze_schema["additionalProperties"]
    for field in ("override_unimplemented_prerequisites", "override_reason"):
        prop = freeze_schema["properties"][field]
        assert prop.get("deprecated") is True
        del prop["deprecated"]
        del prop["description"]


def test_post_shifts_has_security_requirement():
    """AC-01/AC-04/R1: POST /shifts requires JWT via get_principal."""
    from workspace_api.main import app

    post_op = app.openapi()["paths"]["/shifts"]["post"]
    assert "security" in post_op
    assert len(post_op["security"]) > 0


def test_post_shifts_query_parameters_and_response_shape_unchanged():
    """AC-04: the three required query parameters, canonical Shift response
    and 200/422 status contract remain unchanged."""
    from workspace_api.main import app

    post_op = app.openapi()["paths"]["/shifts"]["post"]
    param_names = {p["name"] for p in post_op.get("parameters", [])}
    assert param_names == {"name", "starts_at", "ends_at"}
    assert set(post_op["responses"].keys()) == {"200", "422"}
    assert post_op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/Shift"


def test_openapi_delta_is_exactly_the_shift_create_security_requirement():
    """R9/AC-11/SPEC R21: mechanical proof, not an assertion of trust. Strips
    the new `security` key from POST /shifts, PLUS the complete later
    message-admission delta (security + MessageInput requiredness/schema),
    and re-hashes the remainder against the exact pre-tranche golden
    document - no other path, schema, parameter or response may have moved."""
    from workspace_api.main import app

    doc = app.openapi()
    assert "security" in doc["paths"]["/shifts"]["post"]

    reduced = json.loads(json.dumps(doc))
    _strip_report_delta(reduced)
    _strip_messages_post_delta(reduced)
    _strip_shifts_post_security(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_SHIFT_CREATE_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_unrelated_path_addition_fails_the_golden_chain():
    """Negative protection: an undisclosed new path must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_shifts_post_security(reduced)
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_SHIFT_CREATE_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect an undisclosed path "
        "addition - the proof is not actually structural"
    )


def test_unrelated_mutation_route_removal_fails_the_golden_chain():
    """Negative protection: silently dropping a pre-existing operation (e.g.
    POST /shifts itself, or an unrelated route) must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_shifts_post_security(reduced)

    assert "post" in reduced["paths"]["/handovers"], (
        "test fixture assumption broken: /handovers no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/handovers"]["post"]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_SHIFT_CREATE_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion - the proof is not actually structural"
    )
