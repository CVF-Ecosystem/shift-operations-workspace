"""OpenAPI contract parity for the P2B-APPROVER-IDENTITY-RECONCILIATION
endpoints (SPEC AC-09 OpenAPI half, F14/F17), plus the reviewed incident
vertical delta (INC-REV-F1/R10-A).

`canonical()`/`_sha()` mirror the trivial byte-canonicalization helpers in
test_operations_domain_serialization.py, duplicated rather than cross-imported.

INC-REV-F1/R10-A: a golden digest cannot simply be refreshed on faith. Each
`test_openapi_delta_is_exactly_the_*` test proves its tranche's delta
mechanically - it strips exactly the known paths/schemas/security keys added
by that tranche (and every later tranche's delta too), then re-hashes the
remainder against that tranche's own pre-change SHA.

Chain: `PRE_INCIDENT_OPENAPI_SHA` -> `PRE_HANDOVER_OPENAPI_SHA` ->
`PRE_P2C_READ_OPENAPI_SHA` -> `PRE_SHIFT_CREATE_OPENAPI_SHA` ->
`PRE_MESSAGE_ADMISSION_OPENAPI_SHA` -> `PRE_REPORT_OPENAPI_SHA` ->
`PRE_ASSIGNMENT_OPENAPI_SHA` -> current `GOLDEN_OPENAPI_SHA`. Each earlier
delta test strips every later delta too, netting back to its own true
historical baseline.
"""

from __future__ import annotations

import hashlib
import json
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")


def canonical(value) -> bytes:
    """SPEC section 4.4: the one definition of 'byte-identical'."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Pre-P2A-INCIDENT-VERTICAL value (commit 46da20a), recomputed mechanically.
PRE_INCIDENT_OPENAPI_SHA = "d72a31fd86b4cac2bdb2332c5aef5377f8690ebcdb69081ab59a6339073d0af9"
# Post-incident, pre-handover value (commit eac28f9).
PRE_HANDOVER_OPENAPI_SHA = "24390ee413e43cca086ad68cc34925280745db9fde55d7d6e0400f9b9752106d"
# Post-handover, pre-P2C-read value. Imported (not retyped) so both files agree.
from test_p2c_read_openapi_contract import PRE_P2C_READ_OPENAPI_SHA  # noqa: E402

# Post-P2C-read, pre-shift-create: PRE_P2C_READ_OPENAPI_SHA plus the P2C read
# operations/schema and the GET /shifts security delta.
PRE_SHIFT_CREATE_OPENAPI_SHA = "a982980a1aa8af5585a1bf95006d66c73108dc2c33829c804650fe1b9828c67c"

# Post-shift-create, pre-message-admission (kept under this name because
# test_message_openapi_contract.py imports it directly).
PRE_MESSAGE_ADMISSION_OPENAPI_SHA = "94f56893835b046736efe6697e4d2786ff1716702bfda2a4e9e712a131fee0b3"

# Post-message-admission, pre-report (kept under this name because
# test_report_openapi_contract.py imports it directly).
PRE_REPORT_OPENAPI_SHA = "547d630d1d7fc62dfeb0691b5fcc4bb30fdc2dfe721783c377c4ff25b75a2881"

# Post-report, pre-assignment, and the current golden value: both now owned
# by test_assignment_openapi_contract.py (Amendment 1 line-count repair) -
# imported so this module's GOLDEN check still uses the true current value.
from test_assignment_openapi_contract import (  # noqa: E402
    GOLDEN_OPENAPI_SHA,
    _strip_assignment_delta,
)

_INCIDENT_PATHS = {
    "/incidents",
    "/incidents/{incident_id}",
    "/incidents/{incident_id}/acknowledge",
    "/incidents/{incident_id}/transition",
}
_INCIDENT_SCHEMAS = {
    "AcknowledgeInput", "Incident", "IncidentInput", "IncidentStatus",
    "workspace_api__api__incidents__router__TransitionInput",
}
_HANDOVER_PATHS = {
    "/handovers",
    "/handovers/{handover_id}",
    "/handovers/{handover_id}/acknowledge",
    "/handovers/{handover_id}/review",
}
_HANDOVER_SCHEMAS = {"Handover", "HandoverCreateInput", "HandoverItem", "HandoverStatus", "ReviewInput"}
# The two new read GET operations plus the one new schema; /events already
# had a POST, so only its `get` is removed, never the whole path.
_P2C_READ_OPERATIONS = {
    ("/events", "get"),
    ("/shifts/{shift_id}/open-work", "get"),
}
_P2C_READ_NEW_PATHS = {"/shifts/{shift_id}/open-work"}
_P2C_READ_SCHEMAS = {
    "OpenWorkResponse",
}
# F8 repair: duplicated, not imported - importing these back from
# test_report_openapi_contract.py was a genuine two-way circular import.
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
    for path in _REPORT_PATHS:
        del doc["paths"][path]
    for schema in _REPORT_SCHEMAS:
        del doc["components"]["schemas"][schema]

    freeze_schema = doc["components"]["schemas"]["FreezeInput"]
    del freeze_schema["additionalProperties"]
    for field in ("override_unimplemented_prerequisites", "override_reason"):
        prop = freeze_schema["properties"][field]
        del prop["deprecated"]
        del prop["description"]


def _strip_security(doc: dict, path: str, method: str) -> None:
    """Remove exactly the `security` key a tranche added to one operation."""
    op = doc["paths"][path][method]
    assert "security" in op, f"{method.upper()} {path} lost its expected security requirement"
    del op["security"]


def _strip_shifts_get_security(doc: dict) -> None:
    _strip_security(doc, "/shifts", "get")  # P2C


def _strip_shifts_post_security(doc: dict) -> None:
    _strip_security(doc, "/shifts", "post")  # SHIFT-CREATE-ADMISSION-REPAIR


def _strip_messages_post_delta(doc: dict) -> None:
    """Reverse the COMPLETE message-admission `POST /messages` delta: security
    plus MessageInput's required order and sender_id/source shapes."""
    _strip_security(doc, "/messages", "post")
    schema_ref = doc["paths"]["/messages"]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema = doc["components"]["schemas"][schema_ref.split("/")[-1]]
    assert set(schema["required"]) == {"shift_id", "text"}, schema["required"]
    schema["required"] = ["shift_id", "sender_id", "text"]
    assert schema["properties"]["sender_id"].get("anyOf"), schema["properties"]["sender_id"]
    schema["properties"]["sender_id"] = {"title": "Sender Id", "type": "string"}
    assert schema["properties"]["source"].get("anyOf"), schema["properties"]["source"]
    schema["properties"]["source"] = {"default": "INTERNAL", "title": "Source", "type": "string"}


def _strip_p2c_read_operations(doc: dict) -> None:
    """Remove exactly the P2C read GET operations - deleting only the new
    `get` on a path (like /events) that already had another operation."""
    for path, method in _P2C_READ_OPERATIONS:
        assert path in doc["paths"], f"P2C read path missing: {path}"
        assert method in doc["paths"][path], f"P2C read method missing: {method} {path}"
        if path in _P2C_READ_NEW_PATHS:
            del doc["paths"][path]
        else:
            del doc["paths"][path][method]
            assert doc["paths"][path], (
                f"{path} became empty after removing only {method} - a "
                f"pre-existing operation on this path went missing too"
            )


def test_openapi_document_is_unchanged_from_the_pre_build_capture():
    """AC-09: the contract did not move beyond the reviewed Report delta."""
    from workspace_api.main import app

    actual = canonical(app.openapi())
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_five_incident_operations():
    """Also strips later deltas, netting back to the true pre-incident baseline."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _INCIDENT_PATHS <= doc["paths"].keys()
    assert _INCIDENT_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_assignment_delta(reduced)
    _strip_report_delta(reduced)
    _strip_messages_post_delta(reduced)
    _strip_shifts_post_security(reduced)
    _strip_shifts_get_security(reduced)
    _strip_p2c_read_operations(reduced)
    for path in _INCIDENT_PATHS | _HANDOVER_PATHS:
        del reduced["paths"][path]
    for schema in _INCIDENT_SCHEMAS | _HANDOVER_SCHEMAS | _P2C_READ_SCHEMAS:
        del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_INCIDENT_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_five_handover_operations():
    """Mirrors the incident proof one link up; nets back to pre-handover."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _HANDOVER_PATHS <= doc["paths"].keys()
    assert _HANDOVER_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_assignment_delta(reduced)
    _strip_report_delta(reduced)
    _strip_messages_post_delta(reduced)
    _strip_shifts_post_security(reduced)
    _strip_shifts_get_security(reduced)
    _strip_p2c_read_operations(reduced)
    for path in _HANDOVER_PATHS:
        del reduced["paths"][path]
    for schema in _HANDOVER_SCHEMAS | _P2C_READ_SCHEMAS:
        del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_HANDOVER_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_p2c_read_operations_from_this_module():
    """Strips ONLY the P2C read delta plus later deltas, re-hashing against
    PRE_P2C_READ_OPENAPI_SHA."""
    from workspace_api.main import app

    doc = app.openapi()
    for path, method in _P2C_READ_OPERATIONS:
        assert path in doc["paths"] and method in doc["paths"][path]
    assert _P2C_READ_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_assignment_delta(reduced)
    _strip_report_delta(reduced)
    _strip_messages_post_delta(reduced)
    _strip_shifts_post_security(reduced)
    _strip_shifts_get_security(reduced)
    _strip_p2c_read_operations(reduced)
    for schema in _P2C_READ_SCHEMAS:
        del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_P2C_READ_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_new_endpoints_and_schemas_exact_contract():
    """F14 / F17: exact schema and status code assertions for P2B endpoints."""
    from workspace_api.main import app

    openapi = app.openapi()
    paths = openapi["paths"]
    schemas = openapi["components"]["schemas"]

    # POST /approvals
    assert "/approvals" in paths
    assert "post" in paths["/approvals"]
    approvals_post = paths["/approvals"]["post"]
    assert "200" in approvals_post["responses"]
    assert (
        approvals_post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/ApprovalCreateInput"
    )

    # POST /tasks/creation-intents
    assert "/tasks/creation-intents" in paths
    assert "post" in paths["/tasks/creation-intents"]
    intent_post = paths["/tasks/creation-intents"]["post"]
    assert "201" in intent_post["responses"]
    assert (
        intent_post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/TaskCreationIntentInput"
    )

    # GET /tasks/creation-intents/{intent_id}
    assert "/tasks/creation-intents/{intent_id}" in paths
    assert "get" in paths["/tasks/creation-intents/{intent_id}"]
    intent_get = paths["/tasks/creation-intents/{intent_id}"]["get"]
    assert "200" in intent_get["responses"]

    # Schema field key sets matching SPEC §5.4
    assert set(schemas["ApprovalCreateInput"]["properties"].keys()) == {"record_type", "action", "record_id"}
    assert set(schemas["ApprovalReceiptResponse"]["properties"].keys()) == {
        "receipt_id", "record_type", "record_id", "action", "target_version",
        "risk_class", "approver_id", "approver_role", "created_at",
    }
    assert set(schemas["TaskCreationIntentInput"]["properties"].keys()) == {
        "shift_id", "title", "description", "owner_id", "risk_class", "evidence",
    }
    assert set(schemas["TaskCreationIntentCreateResponse"]["properties"].keys()) == {
        "intent_id", "payload_digest", "risk_class", "created_at",
    }
    assert set(schemas["TaskCreationIntentGetResponse"]["properties"].keys()) == {
        "intent_id", "payload_snapshot", "payload_digest", "risk_class", "created_by", "created_at",
    }
