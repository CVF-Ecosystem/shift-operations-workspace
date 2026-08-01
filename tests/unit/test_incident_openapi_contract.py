"""OpenAPI contract for the incident endpoints (fifth vertical, P2-A), AC-12.

Split as its own module (mirrors test_p2b_openapi_contract.py's split from
test_operations_domain_serialization.py) - not a whole-document golden-hash
comparison, since this tranche's endpoints necessarily change app.openapi().
"""

from __future__ import annotations

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")


def test_incident_endpoints_and_schemas_exact_contract():
    from workspace_api.main import app

    openapi = app.openapi()
    paths = openapi["paths"]
    schemas = openapi["components"]["schemas"]

    assert "/incidents" in paths
    assert "post" in paths["/incidents"] and "get" in paths["/incidents"]
    assert "/incidents/{incident_id}" in paths
    assert "get" in paths["/incidents/{incident_id}"]
    assert "/incidents/{incident_id}/acknowledge" in paths
    assert "/incidents/{incident_id}/transition" in paths

    report_post = paths["/incidents"]["post"]
    assert (
        report_post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/IncidentInput"
    )

    # No approvals/approver/target_version/status field on the request boundary.
    assert set(schemas["IncidentInput"]["properties"].keys()) == {
        "shift_id", "risk_class", "summary", "description", "owner_id", "evidence",
    }
    assert schemas["IncidentInput"]["additionalProperties"] is False
    # P2C-MUTATION-FULL-UI-C3B2 (SPEC R13): AcknowledgeInput now requires
    # expected_version - and is structurally identical to handover's
    # AcknowledgeInput, so FastAPI deduplicates them into one shared schema.
    assert schemas["AcknowledgeInput"]["additionalProperties"] is False
    assert set(schemas["AcknowledgeInput"]["properties"].keys()) == {"expected_version"}
    assert schemas["AcknowledgeInput"]["required"] == ["expected_version"]
    # FastAPI disambiguates same-named request models across routers by full
    # module path (tasks/customer_requests/incidents each define TransitionInput).
    incident_transition = schemas["workspace_api__api__incidents__router__TransitionInput"]
    assert set(incident_transition["properties"].keys()) == {"target_status", "expected_version"}
    assert incident_transition["additionalProperties"] is False

    assert set(schemas["Incident"]["properties"].keys()) == {
        "incident_id", "shift_id", "risk_class", "summary", "description",
        "status", "owner_id", "evidence", "version", "created_at",
    }


def test_incident_contract_schema_requires_and_constrains_canonical_fields():
    """SPEC R3: incident.schema.json must require the public fields and
    constrain risk/status to canonical enum values."""
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    schema = json.loads(
        (repo_root / "packages" / "workspace-contracts" / "incidents" / "incident.schema.json").read_text()
    )

    assert set(schema["required"]) == {"incident_id", "shift_id", "risk_class", "summary", "status"}
    assert schema["properties"]["risk_class"]["enum"] == ["R0", "R1", "R2", "R3", "R4"]
    assert schema["properties"]["status"]["enum"] == [
        "REPORTED", "ACKNOWLEDGED", "MITIGATING", "RESOLVED", "CLOSED",
    ]
