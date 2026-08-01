"""JSON Schema contract files: parse validity plus the open-work contract's
negative/positive proofs (P2C-OPERATIONS-CONSOLE-READ-SLICE Amendment 1 R7).

open-work.schema.json reuses (via $ref) the canonical task/customer-request/
incident schemas rather than forking a generic object shape - these tests
prove that reuse is real: a representative route response must validate, and
a missing required field, an invalid enum/status value, or an unexpected
extra property must be REJECTED, not silently accepted.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

from jsonschema.validators import validator_for
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tests" / "cvf"))

CONTRACTS_ROOT = REPO_ROOT / "packages" / "workspace-contracts"


def test_json_contracts_are_parseable():
    files = list(CONTRACTS_ROOT.rglob("*.json"))
    assert files
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))


def _registry() -> Registry:
    """A referencing.Registry seeded with every contract schema at the URI
    open-work.schema.json's relative $refs would resolve to (its own $id's
    directory, mirroring the on-disk layout), so ../tasks/task.schema.json
    etc. resolve exactly the way this schema's declared $id says they must."""
    resources = []
    for path in CONTRACTS_ROOT.rglob("*.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or "$schema" not in doc:
            continue
        rel = path.relative_to(CONTRACTS_ROOT).as_posix()
        uri = f"https://shift-operations-workspace/packages/workspace-contracts/{rel}"
        resources.append((uri, Resource.from_contents(doc)))
    return Registry().with_resources(resources)


def _open_work_schema() -> dict:
    path = CONTRACTS_ROOT / "open-work" / "open-work.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _validator():
    schema = _open_work_schema()
    cls = validator_for(schema)
    cls.check_schema(schema)
    return cls(schema, registry=_registry())


def _valid_open_work_body() -> dict:
    shift_id = "11111111-1111-1111-1111-111111111111"
    return {
        "shift_id": shift_id,
        "tasks": [
            {
                "task_id": "22222222-2222-2222-2222-222222222222",
                "shift_id": shift_id,
                "title": "Inspect crane",
                "status": "IN_PROGRESS",
                "owner_id": "op-1",
            }
        ],
        "customer_requests": [
            {
                "request_id": "33333333-3333-3333-3333-333333333333",
                "customer_id": "c1",
                "summary": "Need update",
                "status": "NEW",
                "received_at": "2026-07-28T09:00:00+00:00",
            }
        ],
        "incidents": [
            {
                "incident_id": "44444444-4444-4444-4444-444444444444",
                "shift_id": shift_id,
                "risk_class": "R2",
                "summary": "Pump failure",
                "status": "REPORTED",
            }
        ],
    }


def test_open_work_schema_accepts_a_valid_representative_body():
    """A representative open-work response - one item per array, built from
    the exact required fields each canonical schema declares - validates."""
    _validator().validate(_valid_open_work_body())


def test_open_work_schema_rejects_task_missing_required_field():
    body = _valid_open_work_body()
    del body["tasks"][0]["status"]
    assert list(_validator().iter_errors(body)), "missing required Task field must be rejected"


def test_open_work_schema_rejects_customer_request_missing_required_field():
    body = _valid_open_work_body()
    del body["customer_requests"][0]["summary"]
    assert list(_validator().iter_errors(body)), "missing required CustomerRequest field must be rejected"


def test_open_work_schema_rejects_incident_missing_required_field():
    body = _valid_open_work_body()
    del body["incidents"][0]["risk_class"]
    assert list(_validator().iter_errors(body)), "missing required Incident field must be rejected"


def test_open_work_schema_rejects_invalid_incident_status_enum():
    body = _valid_open_work_body()
    body["incidents"][0]["status"] = "NOT_A_REAL_STATUS"
    assert list(_validator().iter_errors(body)), "invalid Incident status enum value must be rejected"


def test_open_work_schema_rejects_invalid_incident_risk_class_enum():
    body = _valid_open_work_body()
    body["incidents"][0]["risk_class"] = "R99"
    assert list(_validator().iter_errors(body)), "invalid Incident risk_class enum value must be rejected"


def test_open_work_schema_rejects_invalid_task_status_enum():
    """SPEC R26: task.schema.json locks status to the canonical TaskStatus
    enum, not a generic string - an out-of-lifecycle value must be rejected."""
    body = _valid_open_work_body()
    body["tasks"][0]["status"] = "NOT_A_REAL_TASK_STATUS"
    assert list(_validator().iter_errors(body)), "invalid Task status enum value must be rejected"


def test_open_work_schema_accepts_task_with_null_owner_id():
    """SPEC R26/P2C-C3A-REV-F15: an unassigned task (owner_id=None) is a
    valid domain response and must validate, not be rejected."""
    body = _valid_open_work_body()
    body["tasks"][0]["owner_id"] = None
    _validator().validate(body)


def test_open_work_schema_rejects_task_missing_owner_id_key():
    """P2C-C3A-REV-F23: owner_id is a required KEY (the actual Task response
    always includes it, per Pydantic's default serialization) even though
    its VALUE may be null - required-key-nullable-value is the correct
    contract, not weakening owner_id out of required entirely."""
    body = _valid_open_work_body()
    del body["tasks"][0]["owner_id"]
    assert list(_validator().iter_errors(body)), "missing owner_id key must be rejected"


def test_open_work_schema_rejects_invalid_customer_request_status_enum():
    """SPEC R26: customer-request.schema.json locks status to the canonical
    CustomerRequestStatus enum, not a generic string."""
    body = _valid_open_work_body()
    body["customer_requests"][0]["status"] = "NOT_A_REAL_CUSTOMER_REQUEST_STATUS"
    assert list(_validator().iter_errors(body)), (
        "invalid CustomerRequest status enum value must be rejected"
    )


def test_open_work_schema_rejects_additional_property_on_response():
    body = _valid_open_work_body()
    body["unexpected_extra_field"] = "should not be allowed"
    assert list(_validator().iter_errors(body)), "unexpected top-level property must be rejected"


def test_open_work_schema_item_arrays_reference_canonical_contracts():
    """R7: the array item shapes must be $ref'd to the canonical contracts,
    not a fork - this is the mechanical proof the schema reuses them."""
    schema = _open_work_schema()
    assert schema["properties"]["tasks"]["items"]["$ref"] == "../tasks/task.schema.json"
    assert schema["properties"]["customer_requests"]["items"]["$ref"] == "../customers/customer-request.schema.json"
    assert schema["properties"]["incidents"]["items"]["$ref"] == "../incidents/incident.schema.json"


def test_representative_open_work_route_response_validates_against_schema():
    """R7: the ACTUAL FastAPI route response (not a hand-built fixture) for
    GET /shifts/{shift_id}/open-work validates against open-work.schema.json,
    proving the typed OpenWorkResponse and the contract agree."""
    from fastapi.testclient import TestClient

    from operations_domain.models import CustomerRequest, Incident, RiskClass, Shift, Task, TaskStatus
    from workspace_api.dependencies import get_ledger
    from workspace_api.infrastructure.repository import InMemoryLedger
    from workspace_api.domain.models import ShiftAssignment, User
    from workspace_api.main import app

    now = datetime.now(timezone.utc)
    shift = Shift(name="Contract shift", starts_at=now, ends_at=now + timedelta(hours=8))
    # P2C-C3A-REV-F15: owner_id is deliberately left None here - an
    # unassigned task is a real, valid domain response (Task.owner_id is
    # nullable) and task.schema.json (SPEC R26) now accepts it.
    task = Task(shift_id=shift.shift_id, title="T1", risk_class=RiskClass.R1, owner_id=None)
    task.status = TaskStatus.IN_PROGRESS
    request = CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="R1")
    incident = Incident(shift_id=shift.shift_id, summary="I1", risk_class=RiskClass.R2)

    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    ledger.add_user(User(user_id="viewer-1", username="viewer-1", password_hash="x", role="viewer"))
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="viewer-1", assigned_by="viewer-1"))
    ledger.add_task(task)
    ledger.add_customer_request(request)
    ledger.add_incident(incident)

    from _auth_test_helpers import auth_headers

    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = client.get(
            f"/shifts/{shift.shift_id}/open-work",
            headers=auth_headers("viewer-1", "viewer"),
        )
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    assert res.status_code == 200
    _validator().validate(res.json())
