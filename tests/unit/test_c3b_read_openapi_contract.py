"""P2C-MUTATION-FULL-UI-C3B1 — OpenAPI contract tests (SPEC R11/R15/R35/R37,
AC-11/AC-16).

Chained mechanical proof that the OpenAPI delta from C3b1 is exactly the four
new read/readiness GET operations and their one new schema — not a blind
digest refresh. This module owns the canonical C3b1-delta path/schema
constants, the `_strip_c3b_read_delta` helper and the fresh
`GOLDEN_OPENAPI_SHA`, mirroring how `test_assignment_openapi_contract.py`
owns the assignment-delta chain link. Every earlier-chain OpenAPI test file
imports `_strip_c3b_read_delta` from here instead of duplicating it or
refreshing its own historical PRE_* baseline (Work Order section 3.4).

Chain: ... -> `PRE_ASSIGNMENT_OPENAPI_SHA` -> (assignment's own prior
`GOLDEN_OPENAPI_SHA`, now `PRE_C3B_READ_OPENAPI_SHA`) -> this module's
`GOLDEN_OPENAPI_SHA` -> (C3B2: consumed as `PRE_C3B2_MUTATION_OPENAPI_SHA` by
test_c3b2_mutation_openapi_contract.py, which now owns the current golden-hash
link).
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


# Post-assignment, pre-C3b1 (the prior GOLDEN_OPENAPI_SHA in
# test_assignment_openapi_contract.py before this tranche).
PRE_C3B_READ_OPENAPI_SHA = "3b708784f9a1c6e02b9b051fb8463dbe41b6f7d4a3eeead14b348e4c44aefe71"

# Post-C3b1: PRE_C3B_READ_OPENAPI_SHA plus the four new read/readiness
# operations and their one new schema. Computed mechanically below and
# pinned once the delta proof passes.
GOLDEN_OPENAPI_SHA = "a198d78eb2761fd0e18b148b046f5a1b043d686b18df345ee8cb013113a5696f"

# P2C-MUTATION-FULL-UI-C3B1 (SPEC R11/R35): three new GET list operations on
# existing paths (each already had at least one other method), plus one
# brand-new GET path for readiness.
_C3B_READ_OPERATIONS = {
    ("/messages", "get"),
    ("/tasks", "get"),
    ("/customer-requests", "get"),
}
_C3B_READ_NEW_PATHS = {"/approvals/readiness"}
_C3B_READ_SCHEMAS = {
    "ReadinessResponse",
}


def _strip_c3b_read_delta(doc: dict) -> None:
    """Remove exactly the C3b1 delta, in place: the three new `get`
    operations added to pre-existing paths, the one brand-new path, and the
    one new schema. Raises on any missing/moved key so a silent no-op can
    never mask a regression, mirroring `_strip_assignment_delta`."""
    for path, method in _C3B_READ_OPERATIONS:
        assert path in doc["paths"], f"C3b1 read path missing: {path}"
        assert method in doc["paths"][path], f"C3b1 read method missing: {method} {path}"
        del doc["paths"][path][method]
        assert doc["paths"][path], (
            f"{path} became empty after removing only {method} - a "
            f"pre-existing operation on this path went missing too"
        )
    for path in _C3B_READ_NEW_PATHS:
        assert path in doc["paths"], f"C3b1 read path missing: {path}"
        del doc["paths"][path]
    for schema in _C3B_READ_SCHEMAS:
        assert schema in doc["components"]["schemas"], f"C3b1 read schema missing: {schema}"
        del doc["components"]["schemas"][schema]


def test_openapi_delta_is_exactly_the_c3b_read_operations():
    """AC-11/AC-16: mechanical proof, not an assertion of trust. Strips the
    C3b1 delta PLUS the later C3b2 mutation-precondition delta, re-hashing
    against PRE_C3B_READ_OPENAPI_SHA (mirrors the chain-proof pattern every
    earlier link already uses)."""
    from workspace_api.main import app
    from test_c3b2_mutation_openapi_contract import _strip_c3b2_mutation_delta

    doc = app.openapi()
    assert _C3B_READ_OPERATIONS <= {
        (p, m) for p, methods in doc["paths"].items() for m in methods
    }
    assert _C3B_READ_NEW_PATHS <= doc["paths"].keys()
    assert _C3B_READ_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_c3b2_mutation_delta(reduced)
    _strip_c3b_read_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_C3B_READ_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_document_is_the_pre_c3b2_mutation_value():
    """The full document with only the C3b1 delta present (i.e. before C3b2)
    matches the C3b1-era GOLDEN_OPENAPI_SHA this module still owns - proves
    this module's exported constant is the true pre-C3b2 baseline that
    test_c3b2_mutation_openapi_contract.py imports as its own PRE_ value."""
    from workspace_api.main import app
    from test_c3b2_mutation_openapi_contract import _strip_c3b2_mutation_delta

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b2_mutation_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == GOLDEN_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_unrelated_path_addition_fails_the_golden_chain():
    """Negative protection: an undisclosed new path must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b_read_delta(reduced)
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_C3B_READ_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect an undisclosed path "
        "addition - the proof is not actually structural"
    )


def test_unrelated_mutation_route_removal_fails_the_golden_chain():
    """Negative protection: silently dropping a pre-existing operation must
    fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b_read_delta(reduced)

    assert "post" in reduced["paths"]["/shifts"], (
        "test fixture assumption broken: /shifts no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/shifts"]["post"]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_C3B_READ_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion - the proof is not actually structural"
    )


def test_c3b_read_routes_require_authentication():
    from workspace_api.main import app

    doc = app.openapi()
    for path, method in _C3B_READ_OPERATIONS | {("/approvals/readiness", "get")}:
        op = doc["paths"][path][method]
        assert "security" in op, f"{method.upper()} {path} has no security requirement"
        assert len(op["security"]) > 0


def test_readiness_response_schema_excludes_secrets():
    """SPEC R35: no payload digest, receipt id, approver identity or
    credential in the readiness response schema."""
    from workspace_api.main import app

    props = app.openapi()["components"]["schemas"]["ReadinessResponse"]["properties"]
    assert set(props.keys()) == {
        "record_type", "record_id", "action", "target_version",
        "risk_class", "ready", "required_roles", "satisfied_roles",
    }
    for forbidden in ("payload_digest", "receipt_id", "approver_id", "approver_role", "credential"):
        assert forbidden not in props


def test_readiness_query_parameters_are_exact():
    from workspace_api.main import app

    op = app.openapi()["paths"]["/approvals/readiness"]["get"]
    names = {p["name"] for p in op["parameters"]}
    assert names == {"record_type", "record_id", "action"}
    for param in op["parameters"]:
        assert param["required"] is True
