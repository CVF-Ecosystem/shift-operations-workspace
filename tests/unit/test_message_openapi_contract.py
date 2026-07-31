"""MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30 — OpenAPI contract tests (SPEC
R13, AC-14).

Chained mechanical proof that the OpenAPI delta from this tranche is exactly
the new bearer-security requirement and requiredness change on the
pre-existing POST /messages - no new path, no unrelated schema, no change to
the canonical Message response. Mirrors the shift-create delta proof pattern
from test_shift_create_openapi_contract.py / test_p2b_openapi_contract.py.
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


# The post-shift-create, pre-message-admission value - imported (not
# retyped) from test_p2b_openapi_contract.py so both files can never
# silently drift.
from test_p2b_openapi_contract import PRE_MESSAGE_ADMISSION_OPENAPI_SHA  # noqa: E402


def _strip_messages_post_delta(doc: dict) -> None:
    """Reverse the COMPLETE authorized `POST /messages` delta (SPEC R13), in
    place, not just the `security` key: (1) the `security` requirement is
    removed; (2) `MessageInput.required` is restored to its exact pre-tranche
    order `["shift_id", "sender_id", "text"]` (sender_id/source were
    previously required plain strings, not optional `anyOf` fields); (3)
    `sender_id` is restored to a required plain string property; (4) `source`
    is restored to a required string property defaulting to `"INTERNAL"`.
    Raises on any missing/moved key so a silent no-op can never mask a
    regression."""
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


def test_post_messages_has_security_requirement():
    """AC-01/R1: POST /messages requires JWT via get_principal."""
    from workspace_api.main import app

    post_op = app.openapi()["paths"]["/messages"]["post"]
    assert "security" in post_op
    assert len(post_op["security"]) > 0


def test_post_messages_request_schema_matches_r2():
    """R2: shift_id/text required; sender_id/source optional/nullable."""
    from workspace_api.main import app

    doc = app.openapi()
    schema_ref = doc["paths"]["/messages"]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema = doc["components"]["schemas"][schema_ref.split("/")[-1]]
    assert set(schema["required"]) == {"shift_id", "text"}
    assert set(schema["properties"].keys()) == {"shift_id", "text", "sender_id", "source"}
    for optional in ("sender_id", "source"):
        types = {t.get("type") for t in schema["properties"][optional]["anyOf"]}
        assert types == {"string", "null"}


def test_post_messages_response_is_canonical_message_and_status_contract_unchanged():
    """R13: canonical Message response and 200/422 status contract unchanged."""
    from workspace_api.main import app

    post_op = app.openapi()["paths"]["/messages"]["post"]
    assert set(post_op["responses"].keys()) == {"200", "422"}
    assert post_op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/Message"


def test_openapi_delta_is_exactly_the_message_admission_security_requirement():
    """R13/AC-14: mechanical proof, not an assertion of trust. Strips only the
    new `security` key from POST /messages and re-hashes the remainder
    against the exact pre-tranche golden document."""
    from workspace_api.main import app

    doc = app.openapi()
    assert "security" in doc["paths"]["/messages"]["post"]

    reduced = json.loads(json.dumps(doc))
    _strip_report_delta(reduced)
    _strip_messages_post_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_MESSAGE_ADMISSION_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_unrelated_path_addition_fails_the_golden_chain():
    """Negative protection: an undisclosed new path must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_messages_post_delta(reduced)
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_MESSAGE_ADMISSION_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect an undisclosed path "
        "addition - the proof is not actually structural"
    )


def test_unrelated_mutation_route_removal_fails_the_golden_chain():
    """Negative protection: silently dropping a pre-existing operation (e.g.
    POST /messages itself, or an unrelated route) must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_messages_post_delta(reduced)

    assert "post" in reduced["paths"]["/shifts"], (
        "test fixture assumption broken: /shifts no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/shifts"]["post"]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_MESSAGE_ADMISSION_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion - the proof is not actually structural"
    )
