"""OpenAPI contract parity for the P2B-APPROVER-IDENTITY-RECONCILIATION
endpoints (SPEC AC-09 OpenAPI half, F14/F17), plus the reviewed incident
vertical delta (INC-REV-F1/R10-A).

`canonical()`/`_sha()` mirror the trivial byte-canonicalization helpers in
test_operations_domain_serialization.py (SPEC section 4.4 "byte-identical"),
duplicated rather than cross-imported.

INC-REV-F1/R10-A: a golden digest cannot simply be refreshed on faith. Each
`test_openapi_delta_is_exactly_the_*` test proves its tranche's delta
mechanically - it strips exactly the known paths/schemas/security keys added
by that tranche (and every later tranche's delta too), then re-hashes the
remainder against that tranche's own pre-change SHA. A blind digest refresh
fails.

Chain: `PRE_INCIDENT_OPENAPI_SHA` -> `PRE_HANDOVER_OPENAPI_SHA` (R12) ->
`PRE_P2C_READ_OPENAPI_SHA` (Amendment 1 R21, from
`test_p2c_read_openapi_contract.py`) -> `PRE_SHIFT_CREATE_OPENAPI_SHA` (SPEC
R9) -> `PRE_MESSAGE_ADMISSION_OPENAPI_SHA` (SPEC R13, from
`test_message_openapi_contract.py`) -> current `GOLDEN_OPENAPI_SHA`. Each
earlier delta test strips every later delta too, netting back to its own
true historical baseline.
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


# Pre-P2A-INCIDENT-VERTICAL value (commit 46da20a) - recomputed mechanically
# against that exact commit's workspace_api.main.app; see module docstring.
PRE_INCIDENT_OPENAPI_SHA = "d72a31fd86b4cac2bdb2332c5aef5377f8690ebcdb69081ab59a6339073d0af9"
# Post-incident, pre-handover value (commit eac28f9) - recomputed the same way.
PRE_HANDOVER_OPENAPI_SHA = "24390ee413e43cca086ad68cc34925280745db9fde55d7d6e0400f9b9752106d"
# Post-handover, pre-P2C-read value - this WAS GOLDEN_OPENAPI_SHA before this
# repair. Imported, not retyped, from test_p2c_read_openapi_contract.py so
# both files always agree on the exact same literal.
from test_p2c_read_openapi_contract import PRE_P2C_READ_OPENAPI_SHA  # noqa: E402

# Post-P2C-read, pre-shift-create value: PRE_P2C_READ_OPENAPI_SHA plus exactly
# the P2C read operations/schema and the GET /shifts security delta.
PRE_SHIFT_CREATE_OPENAPI_SHA = "a982980a1aa8af5585a1bf95006d66c73108dc2c33829c804650fe1b9828c67c"

# Post-shift-create, pre-message-admission value: this WAS GOLDEN_OPENAPI_SHA
# before this tranche; kept under this name because
# test_message_openapi_contract.py imports it directly.
PRE_MESSAGE_ADMISSION_OPENAPI_SHA = "94f56893835b046736efe6697e4d2786ff1716702bfda2a4e9e712a131fee0b3"

# Post-message-admission value: PRE_MESSAGE_ADMISSION_OPENAPI_SHA plus exactly
# the new POST /messages security/requiredness delta. Recomputed mechanically
# post-BUILD against the real generated document (see the delta test below).
GOLDEN_OPENAPI_SHA = "547d630d1d7fc62dfeb0691b5fcc4bb30fdc2dfe721783c377c4ff25b75a2881"

_INCIDENT_PATHS = {
    "/incidents",
    "/incidents/{incident_id}",
    "/incidents/{incident_id}/acknowledge",
    "/incidents/{incident_id}/transition",
}
_INCIDENT_SCHEMAS = {
    "AcknowledgeInput",
    "Incident",
    "IncidentInput",
    "IncidentStatus",
    "workspace_api__api__incidents__router__TransitionInput",
}
_HANDOVER_PATHS = {
    "/handovers",
    "/handovers/{handover_id}",
    "/handovers/{handover_id}/acknowledge",
    "/handovers/{handover_id}/review",
}
_HANDOVER_SCHEMAS = {
    "Handover",
    "HandoverCreateInput",
    "HandoverItem",
    "HandoverStatus",
    "ReviewInput",
}
# Amendment 1 R21: the two new read GET operations and the one new schema.
# /events already had a pre-existing POST, so only its `get` is removed
# (_strip_p2c_read_operations) - never the whole path.
_P2C_READ_OPERATIONS = {
    ("/events", "get"),
    ("/shifts/{shift_id}/open-work", "get"),
}
_P2C_READ_NEW_PATHS = {"/shifts/{shift_id}/open-work"}
_P2C_READ_SCHEMAS = {
    "OpenWorkResponse",
}


def _strip_security(doc: dict, path: str, method: str) -> None:
    """Remove exactly the `security` key a tranche added to one operation, in
    place. Raises if the key is missing or the path/method has moved,
    instead of a silent no-op that would mask a security-policy regression."""
    op = doc["paths"][path][method]
    assert "security" in op, f"{method.upper()} {path} lost its expected security requirement"
    del op["security"]


def _strip_shifts_get_security(doc: dict) -> None:
    _strip_security(doc, "/shifts", "get")  # P2C


def _strip_shifts_post_security(doc: dict) -> None:
    _strip_security(doc, "/shifts", "post")  # SHIFT-CREATE-ADMISSION-REPAIR


def _strip_messages_post_delta(doc: dict) -> None:
    """Reverse the COMPLETE message-admission `POST /messages` delta (SPEC
    R13): `security` plus MessageInput's required order and sender_id/source
    shapes - not just the security key."""
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
    """Remove exactly the P2C read GET operations, in place - deleting only
    the new `get` method on paths (like /events) that already carried a
    pre-existing operation, never the whole path (see module docstring)."""
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
    """AC-09: the generated contract did not move beyond the reviewed P2C
    read delta proven by the next tests."""
    from workspace_api.main import app

    actual = canonical(app.openapi())
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_five_incident_operations():
    """INC-REV-F1/R10-A: also strips later deltas, netting back to the true
    pre-incident baseline."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _INCIDENT_PATHS <= doc["paths"].keys()
    assert _INCIDENT_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
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
    """SPEC R12: mirrors the incident proof one link up; also strips later
    deltas, netting back to the true pre-handover baseline."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _HANDOVER_PATHS <= doc["paths"].keys()
    assert _HANDOVER_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
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
    """Amendment 1 R21, extended twice since: strips ONLY the P2C read
    delta plus later security/schema deltas, re-hashing against
    PRE_P2C_READ_OPENAPI_SHA."""
    from workspace_api.main import app

    doc = app.openapi()
    for path, method in _P2C_READ_OPERATIONS:
        assert path in doc["paths"] and method in doc["paths"][path]
    assert _P2C_READ_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
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
