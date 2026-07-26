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


# The value at the pre-P2A-INCIDENT-VERTICAL commit - never itself edited by
# this repair, only compared against (see the delta-proof test below).
PRE_INCIDENT_OPENAPI_SHA = "c2af8708e4579a8d1204dd12c1b75c304e5e16b831ef3ba54e0859a0beb9851b"
# The reviewed post-incident value: PRE_INCIDENT_OPENAPI_SHA plus exactly the
# five incident operations and their reachable schemas (proven below).
GOLDEN_OPENAPI_SHA = "497e827e11cb194daedd26dd456a985ca63893212e60534e42662e1850adaf96"

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


def test_openapi_document_is_unchanged_from_the_pre_build_capture():
    """AC-09: the generated contract did not move beyond the reviewed
    incident delta proven by the next test."""
    from workspace_api.main import app

    actual = canonical(app.openapi())
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_delta_is_exactly_the_five_incident_operations():
    """INC-REV-F1/R10-A: mechanical proof, not an assertion of trust."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _INCIDENT_PATHS <= doc["paths"].keys()
    assert _INCIDENT_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    for path in _INCIDENT_PATHS:
        del reduced["paths"][path]
    for schema in _INCIDENT_SCHEMAS:
        del reduced["components"]["schemas"][schema]

    actual = canonical(reduced)
    assert _sha(actual) == PRE_INCIDENT_OPENAPI_SHA, actual.decode("utf-8")[:4000]


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
