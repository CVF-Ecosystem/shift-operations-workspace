"""Nonphysical in-process demo: real login/JWT/native source/full frozen HTTP."""

import importlib
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient

from workspace_api.config import settings
from workspace_api.demo.bundle import load_bundle
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models
from workspace_api.infrastructure.repository import InMemoryLedger
from operations_domain.assignment_models import AssignmentStatus

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "tests/fixtures/p5a2_source_demo_oracle.json"
ORACLE_SHA = "b43b5aa27cd593ba560cc48e534d7c7c12f2299d084d8c45dcbfb40a5c1a6aca"
PASSWORD = "nonphysical-test-viewer-password"


def _ledger():
    from workspace_api.auth.passwords import hash_password

    bundle = load_bundle()
    ledger = InMemoryLedger()
    ledger.add_user(models.User(**bundle["user"], password_hash=hash_password(PASSWORD)))
    for row in bundle["shifts"]:
        ledger.create_shift(models.Shift(**row))
    for row in bundle["assignments"]:
        ledger.add_assignment(models.ShiftAssignment(**row))
    for row in bundle["reports"]:
        ledger.add_report(models.Report(**row))
    return ledger


@pytest.fixture
def demo_client(monkeypatch):
    monkeypatch.setenv("P5A2_SOURCE_DEMO_PROFILE", "P5A2-SOURCE-DEMO-LOCAL-1")
    monkeypatch.setattr(settings, "ai_mode", "NO_AI")
    monkeypatch.setattr(settings, "app_env", "source_demo")
    monkeypatch.setattr(settings, "database_url",
                        "postgresql+psycopg://demo:local@127.0.0.1:5433/shiftops_p5a2_source_demo")
    monkeypatch.setattr(settings, "proactive_source_instance_id", "P5A2-SOURCE-DEMO-LOCAL-1")
    monkeypatch.setattr(settings, "cors_allowed_origins", "http://127.0.0.1:5174")
    module = importlib.import_module("workspace_api.demo.app")
    app = module.create_app(nonphysical_test_ledger=_ledger())
    with TestClient(app) as client:
        yield client, app


def _token(client):
    response = client.post("/auth/login", json={"username": "source-demo-viewer",
                                                "password": PASSWORD})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def test_complete_frozen_new_scope_receipts(demo_client):
    client, app = demo_client
    assert app.state.demo_evidence_class == "NONPHYSICAL_IN_PROCESS"
    raw = ORACLE.read_bytes()
    assert sha256(raw).hexdigest() == ORACLE_SHA
    cases = json.loads(raw)["cases"]
    headers = _token(client)
    for case in cases:
        seed = case["coverage_seed"]
        params = {key: seed[key] for key in ("query_start", "query_end", "run_as_of")}
        response = client.get("/proactive/source", params=params, headers=headers)
        assert response.status_code == 200
        assert response.json() == case["expected_receipt"]
        assert response.content == json.dumps(case["expected_receipt"],
                                              ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        assert response.headers["cache-control"] == "no-store"


def test_demo_route_surface_and_auth_refusals(demo_client):
    client, app = demo_client
    expected = {("/auth/login", "POST"), ("/auth/me", "GET"),
                ("/proactive/source", "GET"),
                ("/health", "GET"), ("/shifts", "GET"),
                ("/staffing/shifts", "GET"), ("/staffing/users", "GET"),
                ("/events", "GET"), ("/shifts/{shift_id}/open-work", "GET"),
                ("/incidents", "GET"), ("/handovers", "GET"),
                ("/messages", "GET"), ("/tasks", "GET"),
                ("/customer-requests", "GET"),
                ("/shifts/{shift_id}/capabilities", "GET"),
                ("/reports", "GET")}
    actual = {(route.path, method) for route in app.routes
              for method in (route.methods or set()) if route.path not in
              {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}}
    assert actual == expected
    assert client.get("/health").json() == {
        "status": "ok", "mode": "NO_AI", "service": "workspace-api"}
    assert client.get("/shifts").status_code == 401
    headers = _token(client)
    assert len(client.get("/shifts", headers=headers).json()) == 36
    assert client.get("/staffing/shifts", headers=headers).status_code == 403
    assert client.post("/shifts", headers=headers, json={}).status_code in {404, 405}


@pytest.mark.parametrize("bad_exp", [None, True, float("inf"), 10**30, "invalid"])
def test_read_guards_reject_missing_boolean_nonfinite_and_out_of_range_exp(
    demo_client, bad_exp,
):
    client, _ = demo_client
    payload = {"sub": "PUBLIC_ACTOR", "role": "viewer"}
    if bad_exp is not None:
        payload["exp"] = bad_exp
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    headers = {"Authorization": "Bearer " + token}
    for path, params in (("/shifts", None), ("/proactive/source", {
        "query_start": "2026-01-01T00:00:00Z",
        "query_end": "2026-01-02T12:00:00Z",
        "run_as_of": "2026-01-02T12:00:00Z",
    })):
        response = client.get(path, params=params, headers=headers)
        assert response.status_code == 401
        assert response.headers["cache-control"] == "no-store"


def test_bad_signature_stored_identity_and_assignment_refuse(demo_client):
    client, app = demo_client
    wrong = jwt.encode({"sub": "PUBLIC_ACTOR", "role": "viewer",
                        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600},
                       "different-test-signature-key" * 2, algorithm="HS256")
    response = client.get("/shifts", headers={"Authorization": "Bearer " + wrong})
    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
    headers = _token(client)
    ledger = app.dependency_overrides[get_ledger]()
    shift_id = str(next(iter(ledger.shifts)))
    report_path = "/reports"
    report_rows = client.get(report_path, params={"shift_id": shift_id,
                                                  "include_history": "true"}, headers=headers)
    assert report_rows.status_code == 200
    assert {row["report_id"] for row in report_rows.json()} == {
        str(item.report_id) for item in ledger.reports.values()
        if str(item.shift_id) == shift_id}
    ledger.users["PUBLIC_ACTOR"].is_active = False
    response = client.get("/shifts", headers=headers)
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    ledger.users["PUBLIC_ACTOR"].is_active = True
    assignment = next(row for row in ledger.assignments.values()
                      if str(row.shift_id) == shift_id)
    assignment.status = AssignmentStatus.REVOKED
    response = client.get(report_path, params={"shift_id": shift_id,
                                               "include_history": "true"}, headers=headers)
    assert response.status_code == 403
    case = json.loads(ORACLE.read_bytes())["cases"][0]["coverage_seed"]
    params = {key: case[key] for key in ("query_start", "query_end", "run_as_of")}
    response = client.get("/proactive/source", params=params, headers=headers)
    assert response.status_code == 200
    assert response.json()["outcome"] == "SOURCE_REFUSED"


def test_normal_absent_coverage_and_wrong_actor_refuse(demo_client):
    client, app = demo_client
    from workspace_api.dependencies import get_proactive_source_coverage

    case = json.loads(ORACLE.read_bytes())["cases"][0]
    seed = case["coverage_seed"]
    params = {key: seed[key] for key in ("query_start", "query_end", "run_as_of")}
    headers = _token(client)
    app.dependency_overrides[get_proactive_source_coverage] = lambda: None
    response = client.get("/proactive/source", params=params, headers=headers)
    assert response.status_code == 200
    assert response.json()["reason"] == "COVERAGE_UNKNOWN"
    wrong = jwt.encode({"sub": "OTHER_ACTOR", "role": "viewer",
                        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600},
                       settings.jwt_secret_key, algorithm="HS256")
    response = client.get("/proactive/source", params=params,
                          headers={"Authorization": "Bearer " + wrong})
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
