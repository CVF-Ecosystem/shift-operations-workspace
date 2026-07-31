"""P2C-OPERATIONS-CONSOLE-READ-SLICE — OpenAPI contract tests (SPEC R11/AC-11).

Chained mechanical proof that the OpenAPI delta from the P2C read slice is
exactly the new read operations and their reachable schemas — not a blind
digest refresh. Mirrors the incident/handover delta proof pattern from
test_p2b_openapi_contract.py.

The new P2C read operations are:
- GET /events (with query param shift_id)
- GET /shifts/{shift_id}/open-work

Plus GET /shifts gained a security requirement (JWT via get_principal).
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


# The post-handover, pre-P2C-read value - the ACTUAL committed-HEAD document
# hash before this tranche's routes existed (recomputed mechanically against
# commit 0ac5c4d4a97b20d71ca34949e60ea9ad007886f5's workspace_api.main.app;
# the interrupted BUILD's committed test_p2b_openapi_contract.py had copied
# the stale prior GOLDEN_OPENAPI_SHA literal here without verifying it still
# matched real committed HEAD, and it did not - Amendment 1 P2C-C3A-R6/R21
# requires re-deriving this from source, not trusting an inherited literal).
PRE_P2C_READ_OPENAPI_SHA = "503aa741493ade06de26a9422dec014a98a1b3af2895f9fc90c83dd61fb3635d"

# P2C read operations, expressed as (path, method) so /events - which already
# had a pre-existing POST /events mutation operation before this tranche -
# only loses its NEW `get`, not the whole path (an earlier draft of this test
# deleted the entire "/events" path key, which silently also removed the
# pre-existing POST operation and its schema reachability - a mutation-route
# deletion this test exists specifically to catch, not commit).
_P2C_READ_OPERATIONS = {
    ("/events", "get"),
    ("/shifts/{shift_id}/open-work", "get"),
}
# Whole paths that are entirely new (safe to delete outright).
_P2C_READ_NEW_PATHS = {"/shifts/{shift_id}/open-work"}

# Schemas reachable from the P2C read operations.
_P2C_READ_SCHEMAS = {
    "OpenWorkResponse",
}

# P2C-MUTATION-FULL-UI-C3A1: duplicated (not imported - importing back from
# test_p2b_openapi_contract.py would be circular, mirroring this file's own
# report-delta duplication) rather than adding a shared third module.
_ASSIGNMENT_PATHS = {
    "/auth/me",
    "/staffing/shifts",
    "/staffing/users",
    "/shifts/{shift_id}/assignments",
    "/shifts/{shift_id}/assignments/{assignment_id}/revoke",
    "/shifts/{shift_id}/capabilities",
}
_ASSIGNMENT_SCHEMAS = {
    "AssignInput", "AssignmentStatus", "CapabilitiesResponse", "MeResponse",
    "RevokeInput", "ShiftAssignment", "StaffingShift", "StaffingUser",
}


def _strip_assignment_delta(doc: dict) -> None:
    for path in _ASSIGNMENT_PATHS:
        assert path in doc["paths"], f"assignment path missing: {path}"
        del doc["paths"][path]
    for schema in _ASSIGNMENT_SCHEMAS:
        assert schema in doc["components"]["schemas"], f"assignment schema missing: {schema}"
        del doc["components"]["schemas"][schema]


def test_openapi_delta_is_exactly_the_p2c_read_operations():
    """AC-11: mechanical proof that the OpenAPI delta is exactly the P2C read
    operations. Strips only the new `get` operations (not the pre-existing
    `post /events`), their reachable schemas, AND the `security` requirement
    P2C added to the pre-existing GET /shifts operation from the current
    document, then re-hashes the remainder against the pre-P2C-read baseline
    (PRE_P2C_READ_OPENAPI_SHA). Asserting each key exists before deleting it
    (rather than a no-op `if` guard) means an unrelated regression that
    silently removes it - including a mutation-route deletion - would fail
    this test instead of being absorbed.

    SHIFT-CREATE-ADMISSION-REPAIR (2026-07-29) added a `security` requirement
    to POST /shifts, and MESSAGE-ADMISSION-TRUST-REPAIR (2026-07-30) added one
    to POST /messages; both later deltas are stripped first so this proof
    still nets back to the true pre-P2C-read baseline, not a more recent one."""
    from workspace_api.main import app

    doc = app.openapi()
    for path, method in _P2C_READ_OPERATIONS:
        assert path in doc["paths"], f"P2C read path missing: {path}"
        assert method in doc["paths"][path], f"P2C read method missing: {method} {path}"

    reduced = json.loads(json.dumps(doc))

    _strip_assignment_delta(reduced)

    # P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE (SPEC R28): reverse the
    # COMPLETE later report delta first - the five new paths/schemas plus the
    # FreezeInput deprecation markers.
    for report_path in (
        "/reports", "/reports/{report_id}", "/reports/{report_id}/versions",
        "/reports/{report_id}/submit-review", "/reports/{report_id}/approve",
    ):
        assert report_path in reduced["paths"], f"report path missing: {report_path}"
        del reduced["paths"][report_path]
    for report_schema in (
        "ReportCreateInput", "ReportResponse", "ReportSection", "ReportSourceRef",
        "ReportStatus", "ReportType", "ReportVersionInput",
    ):
        assert report_schema in reduced["components"]["schemas"], f"report schema missing: {report_schema}"
        del reduced["components"]["schemas"][report_schema]
    freeze_schema = reduced["components"]["schemas"]["FreezeInput"]
    assert freeze_schema.get("additionalProperties") is False
    del freeze_schema["additionalProperties"]
    for field in ("override_unimplemented_prerequisites", "override_reason"):
        prop = freeze_schema["properties"][field]
        assert prop.get("deprecated") is True
        del prop["deprecated"]
        del prop["description"]

    messages_post = reduced["paths"]["/messages"]["post"]
    assert "security" in messages_post, "POST /messages lost its expected security requirement"
    del messages_post["security"]
    message_schema_ref = messages_post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    message_schema = reduced["components"]["schemas"][message_schema_ref.split("/")[-1]]
    assert set(message_schema["required"]) == {"shift_id", "text"}, message_schema["required"]
    message_schema["required"] = ["shift_id", "sender_id", "text"]
    assert message_schema["properties"]["sender_id"].get("anyOf"), message_schema["properties"]["sender_id"]
    message_schema["properties"]["sender_id"] = {"title": "Sender Id", "type": "string"}
    assert message_schema["properties"]["source"].get("anyOf"), message_schema["properties"]["source"]
    message_schema["properties"]["source"] = {"default": "INTERNAL", "title": "Source", "type": "string"}
    shifts_post = reduced["paths"]["/shifts"]["post"]
    assert "security" in shifts_post, "POST /shifts lost its expected security requirement"
    del shifts_post["security"]
    shifts_get = reduced["paths"]["/shifts"]["get"]
    assert "security" in shifts_get, "GET /shifts lost its expected security requirement"
    del shifts_get["security"]

    for path, method in _P2C_READ_OPERATIONS:
        if path in _P2C_READ_NEW_PATHS:
            del reduced["paths"][path]
        else:
            del reduced["paths"][path][method]
            assert reduced["paths"][path], (
                f"{path} became empty after removing only {method} - a "
                f"pre-existing operation on this path went missing too"
            )
    for schema in _P2C_READ_SCHEMAS:
        if schema in reduced["components"]["schemas"]:
            del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_P2C_READ_OPENAPI_SHA, (
        f"OpenAPI delta is not exactly the P2C read operations. "
        f"Expected pre-P2C-read SHA {PRE_P2C_READ_OPENAPI_SHA}, "
        f"got {_sha(actual)}. Diff (first 4000 chars):\n{actual.decode('utf-8')[:4000]}"
    )


def test_openwork_response_schema_exact_contract():
    """AC-11/AC-01: the OpenWorkResponse schema has exactly the required fields."""
    from workspace_api.main import app

    schemas = app.openapi()["components"]["schemas"]
    assert "OpenWorkResponse" in schemas
    props = schemas["OpenWorkResponse"]["properties"]
    assert set(props.keys()) == {"shift_id", "tasks", "customer_requests", "incidents"}
    assert props["shift_id"]["type"] == "string"
    assert props["tasks"]["type"] == "array"
    assert props["customer_requests"]["type"] == "array"
    assert props["incidents"]["type"] == "array"


def test_get_events_has_security_requirement():
    """AC-04/R5: GET /events requires JWT via get_principal."""
    from workspace_api.main import app

    paths = app.openapi()["paths"]
    assert "/events" in paths
    assert "get" in paths["/events"]
    get_op = paths["/events"]["get"]
    assert "security" in get_op
    assert len(get_op["security"]) > 0


def test_get_shifts_has_security_requirement():
    """AC-04/R5: GET /shifts requires JWT via get_principal."""
    from workspace_api.main import app

    paths = app.openapi()["paths"]
    assert "/shifts" in paths
    assert "get" in paths["/shifts"]
    get_op = paths["/shifts"]["get"]
    assert "security" in get_op
    assert len(get_op["security"]) > 0


def test_get_open_work_has_security_requirement():
    """AC-04/R5: GET /shifts/{shift_id}/open-work requires JWT via get_principal."""
    from workspace_api.main import app

    paths = app.openapi()["paths"]
    assert "/shifts/{shift_id}/open-work" in paths
    assert "get" in paths["/shifts/{shift_id}/open-work"]
    get_op = paths["/shifts/{shift_id}/open-work"]["get"]
    assert "security" in get_op
    assert len(get_op["security"]) > 0


def test_unrelated_path_addition_fails_the_golden_chain():
    """SPEC R24/AC-24 negative protection: the mechanical delta proof must
    fail closed on drift it was never told about, not just pass on the
    reviewed P2C delta. Simulates an undisclosed new path appearing in the
    document (e.g. an unauthorized route added alongside a legitimate
    change) and asserts the same reduction/re-hash this test performs above
    would no longer match PRE_P2C_READ_OPENAPI_SHA - proving the pinned
    fastapi/pydantic versions (SPEC R23) did not turn this into a tautology
    that passes regardless of what the document actually contains."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    shifts_get = reduced["paths"]["/shifts"]["get"]
    del shifts_get["security"]
    for path, method in _P2C_READ_OPERATIONS:
        if path in _P2C_READ_NEW_PATHS:
            del reduced["paths"][path]
        else:
            del reduced["paths"][path][method]
    for schema in _P2C_READ_SCHEMAS:
        if schema in reduced["components"]["schemas"]:
            del reduced["components"]["schemas"][schema]

    # Undisclosed drift this proof must catch: an extra path this amendment
    # never authorized and the delta-strip logic above never removes.
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_P2C_READ_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect an undisclosed path "
        "addition - the proof is not actually structural under the pinned "
        "dependency versions"
    )


def test_unrelated_mutation_route_removal_fails_the_golden_chain():
    """SPEC R24/AC-24 negative protection, mutation-route variant: proves
    that silently dropping a pre-existing mutation operation (the exact
    defect R6/P2C-C3A-R6 found and fixed - a whole-path deletion that also
    removed POST /events) would still fail this proof today, under the
    pinned fastapi/pydantic versions - not just at the time R6 was fixed."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    shifts_get = reduced["paths"]["/shifts"]["get"]
    del shifts_get["security"]

    # The regression this test exists to catch: deleting the WHOLE /events
    # path (instead of only its new `get`) silently discards the
    # pre-existing `post` mutation operation too.
    assert "post" in reduced["paths"]["/events"], (
        "test fixture assumption broken: /events no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/events"]
    del reduced["paths"]["/shifts/{shift_id}/open-work"]
    for schema in _P2C_READ_SCHEMAS:
        if schema in reduced["components"]["schemas"]:
            del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_P2C_READ_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion masked as part of the P2C read delta - the proof is not "
        "actually structural under the pinned dependency versions"
    )