"""P2C-MUTATION-FULL-UI-C3A1 — OpenAPI contract tests (SPEC R5/R9, AC-01/AC-07).

Exact schema/security assertions for the six new C3a1 operations: the five
R5 staffing routes plus /auth/me and capabilities. This module ALSO owns the
canonical assignment-delta path/schema constants and the
`_strip_assignment_delta` helper (Amendment 1: these moved here from
test_p2b_openapi_contract.py, which had grown past the 300-line hard limit).
Every earlier-chain OpenAPI test file imports `_strip_assignment_delta` from
here rather than duplicating it - `test_p2b_openapi_contract.py` included,
since this module imports nothing from it (no circular import).

C3B1: the chain's current golden-hash link moved one further to
`test_c3b_read_openapi_contract.py` (this module's assignment delta had grown
to be the last one before C3b1's own read/readiness delta) - this module's
own `test_openapi_delta_is_exactly_the_assignment_operations` now nets back
to `PRE_ASSIGNMENT_OPENAPI_SHA` by stripping BOTH the assignment delta AND
the later C3b1 delta, mirroring the chain-proof pattern every earlier link
already uses. `PRE_C3B_READ_OPENAPI_SHA` (imported, not retyped) is this
module's post-assignment value, now consumed by
`test_c3b_read_openapi_contract.py` as its own pre-tranche baseline.

Chain: `PRE_INCIDENT_OPENAPI_SHA` -> ... -> `PRE_ASSIGNMENT_OPENAPI_SHA` ->
`PRE_C3B_READ_OPENAPI_SHA` -> current `GOLDEN_OPENAPI_SHA` (both owned by
test_c3b_read_openapi_contract.py).
"""

from __future__ import annotations

import hashlib
import json
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

from test_c3b_read_openapi_contract import (  # noqa: E402
    PRE_C3B_READ_OPENAPI_SHA,
    _strip_c3b_read_delta,
)


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Post-report, pre-assignment (the prior GOLDEN_OPENAPI_SHA).
PRE_ASSIGNMENT_OPENAPI_SHA = "d00d106260306caa216c5f68001c7fdc7b94e778348cd0f6cc763291246b7516"

# P2C-MUTATION-FULL-UI-C3A1: five staffing routes plus /auth/me and
# capabilities, and every schema they reach.
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


def test_openapi_delta_is_exactly_the_assignment_operations():
    """P2C-MUTATION-FULL-UI-C3A1: mechanical proof, not an assertion of
    trust. Strips the assignment delta PLUS the later C3b1 read/readiness
    delta, re-hashing against PRE_ASSIGNMENT_OPENAPI_SHA (mirrors the
    chain-proof pattern every earlier link already uses)."""
    from workspace_api.main import app

    doc = app.openapi()
    assert _ASSIGNMENT_PATHS <= doc["paths"].keys()
    assert _ASSIGNMENT_SCHEMAS <= doc["components"]["schemas"].keys()

    reduced = json.loads(json.dumps(doc))
    _strip_c3b_read_delta(reduced)
    _strip_assignment_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_ASSIGNMENT_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_openapi_document_is_the_pre_c3b_read_value():
    """The full document with only the assignment delta present (i.e. before
    C3b1) matches PRE_C3B_READ_OPENAPI_SHA - proves this module's exported
    constant is the true current pre-C3b1 baseline."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b_read_delta(reduced)

    actual = canonical(reduced)
    assert _sha(actual) == PRE_C3B_READ_OPENAPI_SHA, actual.decode("utf-8")[:4000]


def test_unrelated_path_addition_fails_the_golden_chain():
    """Negative protection: an undisclosed new path must fail this proof."""
    from workspace_api.main import app

    doc = app.openapi()
    reduced = json.loads(json.dumps(doc))
    _strip_c3b_read_delta(reduced)
    _strip_assignment_delta(reduced)
    reduced["paths"]["/unrelated-undisclosed-probe-path"] = {
        "get": {"responses": {"200": {"description": "OK"}}}
    }

    actual = canonical(reduced)
    assert _sha(actual) != PRE_ASSIGNMENT_OPENAPI_SHA, (
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
    _strip_assignment_delta(reduced)

    assert "post" in reduced["paths"]["/shifts"], (
        "test fixture assumption broken: /shifts no longer has a "
        "pre-existing POST operation to protect"
    )
    del reduced["paths"]["/shifts"]["post"]

    actual = canonical(reduced)
    assert _sha(actual) != PRE_ASSIGNMENT_OPENAPI_SHA, (
        "golden-chain hash comparison did not detect a mutation-route "
        "deletion - the proof is not actually structural"
    )


def test_staffing_routes_require_authentication():
    from workspace_api.main import app

    doc = app.openapi()
    for path, method in (
        ("/staffing/shifts", "get"),
        ("/staffing/users", "get"),
        ("/shifts/{shift_id}/assignments", "get"),
        ("/shifts/{shift_id}/assignments", "post"),
        ("/shifts/{shift_id}/assignments/{assignment_id}/revoke", "post"),
        ("/shifts/{shift_id}/capabilities", "get"),
        ("/auth/me", "get"),
    ):
        op = doc["paths"][path][method]
        assert "security" in op, f"{method.upper()} {path} has no security requirement"
        assert len(op["security"]) > 0


def test_assign_input_schema_is_user_id_only():
    from workspace_api.main import app

    schemas = app.openapi()["components"]["schemas"]
    assert schemas["AssignInput"]["additionalProperties"] is False
    assert set(schemas["AssignInput"]["properties"].keys()) == {"user_id"}
    assert schemas["AssignInput"]["required"] == ["user_id"]


def test_revoke_input_schema_is_expected_version_only():
    from workspace_api.main import app

    schemas = app.openapi()["components"]["schemas"]
    assert schemas["RevokeInput"]["additionalProperties"] is False
    assert set(schemas["RevokeInput"]["properties"].keys()) == {"expected_version"}
    assert schemas["RevokeInput"]["required"] == ["expected_version"]


def test_shift_assignment_response_schema_has_no_tenant_or_data_scope_field():
    """R1: no tenant field or provider data_scope field may be added."""
    from workspace_api.main import app

    props = app.openapi()["components"]["schemas"]["ShiftAssignment"]["properties"].keys()
    assert set(props) == {
        "assignment_id", "shift_id", "user_id", "status", "assigned_by",
        "assigned_at", "revoked_by", "revoked_at", "version",
    }
    assert "tenant_id" not in props
    assert "data_scope" not in props


def test_staffing_shift_and_user_responses_are_minimal():
    """R5: staffing reads return only id/name/status and id/username/role -
    never operational events/work/messages/handovers/Reports."""
    from workspace_api.main import app

    schemas = app.openapi()["components"]["schemas"]
    assert set(schemas["StaffingShift"]["properties"].keys()) == {"shift_id", "name", "status"}
    assert set(schemas["StaffingUser"]["properties"].keys()) == {"user_id", "username", "role"}


def test_me_response_schema_is_verified_claims_only():
    """R9: /auth/me returns only verified user id, role and expiry - no
    password hash, no raw token, no other user's data."""
    from workspace_api.main import app

    props = app.openapi()["components"]["schemas"]["MeResponse"]["properties"]
    assert set(props.keys()) == {"user_id", "role", "expires_at"}


def test_capabilities_response_schema_excludes_secrets():
    """R9: advisory action names plus bounded reason categories only - no
    digest, credential or policy internal."""
    from workspace_api.main import app

    props = app.openapi()["components"]["schemas"]["CapabilitiesResponse"]["properties"]
    assert set(props.keys()) == {"shift_id", "actions", "reasons"}
    assert "payload_digest" not in props
    assert "credential" not in props
