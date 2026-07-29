"""OpenAPI contract parity for the P2B-APPROVER-IDENTITY-RECONCILIATION
endpoints (SPEC AC-09 OpenAPI half, F14/F17), plus the reviewed incident
vertical delta (INC-REV-F1/R10-A).

Split out of test_operations_domain_serialization.py
(CVF-FILE-SPLIT-GUARD-HARDENING) to keep that module under the hard line
limit; not a behavior change. `canonical()`/`_sha()` are the same trivial
byte-canonicalization helpers defined there - duplicated here rather than
cross-imported between test modules, per the same `SPEC section 4.4`
"byte-identical" definition.

INC-REV-F1: wiring the five authorized incident endpoints (P2A-INCIDENT-
VERTICAL) necessarily changes this repository-wide document, but a golden
digest cannot simply be refreshed on faith - Amendment 1 (ADR section 6,
SPEC R10-A) requires PROVING the delta is exactly the five incident
operations and their reachable canonical schemas before the digest moves.
`test_openapi_delta_is_exactly_the_five_incident_operations` does that proof
mechanically: it removes exactly the known incident paths/schemas from the
current document and re-hashes the remainder against `PRE_INCIDENT_OPENAPI_SHA`
(the original golden value, captured before this tranche existed) - a blind
digest refresh, or any additional undisclosed change, could not pass it.

P2A-HANDOVER-VERTICAL (SPEC R12): the same chained proof extends one more
link. `PRE_HANDOVER_OPENAPI_SHA` is the exact prior `GOLDEN_OPENAPI_SHA`
(post-incident, pre-handover); `test_openapi_delta_is_exactly_the_five_handover_operations`
strips only the five handover operations and their reachable schemas and
re-hashes against it. The incident delta test is extended to strip the
handover delta too, so it still nets back to the true pre-incident baseline.

P2C-OPERATIONS-CONSOLE-READ-SLICE (Amendment 1 R21): the chain extends one
more link. `PRE_P2C_READ_OPENAPI_SHA` is the exact prior `GOLDEN_OPENAPI_SHA`
(post-handover, pre-P2C-read) - imported, not retyped, from
`test_p2c_read_openapi_contract.py` so both files can never silently drift.
The incident/handover delta tests are extended to also strip the P2C read
delta (two new GET operations, the `OpenWorkResponse` schema, and the
`security` key added to pre-existing `GET /shifts`), so each still nets back
to its own true historical baseline. Repairing this chain also found that
`PRE_INCIDENT_OPENAPI_SHA` and `PRE_HANDOVER_OPENAPI_SHA` were themselves
stale (verified against their named commits in an isolated worktree) - both
were recomputed mechanically from source, not carried forward on faith.
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

# Post-P2C-read value: PRE_P2C_READ_OPENAPI_SHA plus exactly the P2C read
# operations/schema and the GET /shifts security delta (proven below).
GOLDEN_OPENAPI_SHA = "a982980a1aa8af5585a1bf95006d66c73108dc2c33829c804650fe1b9828c67c"

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
# P2C-OPERATIONS-CONSOLE-READ-SLICE (Amendment 1 R21): the two new read GET
# operations and the one new schema. /events already had a pre-existing POST,
# so only its `get` is removed (_strip_p2c_read_operations) - never the whole
# path. GET /shifts keeps its path/schema but gains a `security` requirement,
# stripped separately (_strip_shifts_get_security) so an unrelated change
# elsewhere still fails this test.
_P2C_READ_OPERATIONS = {
    ("/events", "get"),
    ("/shifts/{shift_id}/open-work", "get"),
}
_P2C_READ_NEW_PATHS = {"/shifts/{shift_id}/open-work"}
_P2C_READ_SCHEMAS = {
    "OpenWorkResponse",
}


def _strip_shifts_get_security(doc: dict) -> None:
    """Remove exactly the `security` key P2C added to GET /shifts, in place.

    Raises (via direct KeyError/AssertionError) if the key is missing or the
    path/method has moved - a silent no-op here would let this test pass
    while masking a security-policy regression on a mutation route."""
    get_op = doc["paths"]["/shifts"]["get"]
    assert "security" in get_op, "GET /shifts lost its expected security requirement"
    del get_op["security"]


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
    """INC-REV-F1/R10-A: mechanical proof, not an assertion of trust.

    Also strips the later handover and P2C read deltas so this still nets
    back to the true pre-incident baseline, not just a more recent one."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _INCIDENT_PATHS <= doc["paths"].keys()
    assert _INCIDENT_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_shifts_get_security(reduced)
    _strip_p2c_read_operations(reduced)
    for path in _INCIDENT_PATHS | _HANDOVER_PATHS:
        del reduced["paths"][path]
    for schema in _INCIDENT_SCHEMAS | _HANDOVER_SCHEMAS | _P2C_READ_SCHEMAS:
        del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_INCIDENT_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_five_handover_operations():
    """P2A-HANDOVER-VERTICAL (SPEC R12): mechanical proof, not an assertion
    of trust - mirrors the incident delta proof one link further up the chain.

    Also strips the later P2C read delta so this still nets back to the true
    pre-handover baseline, not just the pre-P2C-read one."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _HANDOVER_PATHS <= doc["paths"].keys()
    assert _HANDOVER_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_shifts_get_security(reduced)
    _strip_p2c_read_operations(reduced)
    for path in _HANDOVER_PATHS:
        del reduced["paths"][path]
    for schema in _HANDOVER_SCHEMAS | _P2C_READ_SCHEMAS:
        del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_HANDOVER_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_p2c_read_operations_from_this_module():
    """Amendment 1 R21: the same chained mechanical proof one more link up -
    strips ONLY the P2C read GET operations/schema and the GET /shifts
    security delta, re-hashing against PRE_P2C_READ_OPENAPI_SHA (the exact
    prior GOLDEN_OPENAPI_SHA). Complements (does not replace)
    test_p2c_read_openapi_contract.py's own delta test, which uses the same
    operation/schema set independently."""
    from workspace_api.main import app

    doc = app.openapi()
    for path, method in _P2C_READ_OPERATIONS:
        assert path in doc["paths"] and method in doc["paths"][path]
    assert _P2C_READ_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
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
    assert set(schemas["ApprovalCreateInput"]["properties"].keys()) == {
        "record_type",
        "action",
        "record_id",
    }
    assert set(schemas["ApprovalReceiptResponse"]["properties"].keys()) == {
        "receipt_id",
        "record_type",
        "record_id",
        "action",
        "target_version",
        "risk_class",
        "approver_id",
        "approver_role",
        "created_at",
    }
    assert set(schemas["TaskCreationIntentInput"]["properties"].keys()) == {
        "shift_id",
        "title",
        "description",
        "owner_id",
        "risk_class",
        "evidence",
    }
    assert set(schemas["TaskCreationIntentCreateResponse"]["properties"].keys()) == {
        "intent_id",
        "payload_digest",
        "risk_class",
        "created_at",
    }
    assert set(schemas["TaskCreationIntentGetResponse"]["properties"].keys()) == {
        "intent_id",
        "payload_snapshot",
        "payload_digest",
        "risk_class",
        "created_by",
        "created_at",
    }
