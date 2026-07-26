"""OpenAPI contract parity for the P2B-APPROVER-IDENTITY-RECONCILIATION
endpoints (SPEC AC-09 OpenAPI half, F14/F17).

Split out of test_operations_domain_serialization.py
(CVF-FILE-SPLIT-GUARD-HARDENING) to keep that module under the hard line
limit; not a behavior change. `canonical()`/`_sha()` are the same trivial
byte-canonicalization helpers defined there - duplicated here rather than
cross-imported between test modules, per the same `SPEC section 4.4`
"byte-identical" definition. `GOLDEN_OPENAPI_SHA` is the exact same digest
value captured at the pre-BUILD commit, only relocated.
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


GOLDEN_OPENAPI_SHA = "c2af8708e4579a8d1204dd12c1b75c304e5e16b831ef3ba54e0859a0beb9851b"


def test_openapi_document_is_unchanged_from_the_pre_build_capture():
    """AC-09: the generated contract did not move."""
    from workspace_api.main import app

    actual = canonical(app.openapi())
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:4000]


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
