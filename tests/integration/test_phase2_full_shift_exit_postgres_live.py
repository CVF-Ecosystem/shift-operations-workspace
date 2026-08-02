"""Opt-in PostgreSQL proof for one complete Phase 2 shift lineage."""
from __future__ import annotations

import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from cvf_runtime.identity import Principal
from operations_ledger.sql_ledger import SqlLedger, make_engine
from workspace_api.auth.tokens import create_access_token
from workspace_api.dependencies import get_ledger
from workspace_api.domain import models as domain_models
from workspace_api.main import app

LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


def headers(user_id: str, role: str) -> dict[str, str]:
    token = create_access_token(Principal(user_id=user_id, role=role))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def live_chain():
    url = os.environ.get(LIVE_URL_ENV)
    if not url:
        pytest.skip(f"{LIVE_URL_ENV} not set; opt-in live PostgreSQL suite")
    ledger = SqlLedger(url, models=domain_models, engine=make_engine(url))
    for user_id, role in (("p2-op", "operator"), ("p2-sup1", "shift_supervisor"), ("p2-sup2", "shift_supervisor")):
        ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield url, ledger, TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)
        ledger.engine.dispose()


def expect_ok(response):
    assert response.status_code in (200, 201), response.text
    return response.json()


def test_full_shift_routes_and_audits_survive_engine_reconnect(live_chain):
    url, ledger, client = live_chain
    op = headers("p2-op", "operator")
    sup1 = headers("p2-sup1", "shift_supervisor")
    sup2 = headers("p2-sup2", "shift_supervisor")
    starts = datetime(2026, 8, 10, 8, tzinfo=timezone.utc)

    source = expect_ok(client.post("/shifts", params={"name": "P2 live source", "starts_at": starts.isoformat(), "ends_at": (starts + timedelta(hours=12)).isoformat()}, headers=op))
    destination = expect_ok(client.post("/shifts", params={"name": "P2 live destination", "starts_at": (starts + timedelta(hours=12)).isoformat(), "ends_at": (starts + timedelta(hours=24)).isoformat()}, headers=op))
    source_id, destination_id = source["shift_id"], destination["shift_id"]
    assignments = []
    for shift_id in (source_id, destination_id):
        assignments.append(expect_ok(client.post(f"/shifts/{shift_id}/assignments", json={"user_id": "p2-sup1"}, headers=sup1)))
        assignments.append(expect_ok(client.post(f"/shifts/{shift_id}/assignments", json={"user_id": "p2-sup2"}, headers=sup1)))

    event = expect_ok(client.post("/events", json={"shift_id": source_id, "event_type": "shift_update", "title": "P2 live event", "risk_class": "R0"}, headers=op))
    confirmed = expect_ok(client.post(f"/events/{event['event_id']}/confirm", json={"expected_version": event["version"]}, headers=sup1))
    assert confirmed["state"] == "CONFIRMED"
    task = expect_ok(client.post("/tasks", json={"shift_id": source_id, "title": "P2 live open work", "risk_class": "R0"}, headers=op))
    task = expect_ok(client.post(f"/tasks/{task['task_id']}/transition", json={"target_status": "IN_PROGRESS", "expected_version": task["version"]}, headers=op))

    handover = expect_ok(client.post("/handovers", json={"from_shift_id": source_id, "to_shift_id": destination_id}, headers=op))
    assert handover["items"] and handover["items"][0]["source_record_id"] == task["task_id"]
    original_items = handover["items"]
    handover = expect_ok(client.post(f"/handovers/{handover['handover_id']}/review", json={"expected_version": handover["version"]}, headers=sup1))
    handover = expect_ok(client.post(f"/handovers/{handover['handover_id']}/acknowledge", json={"expected_version": handover["version"]}, headers=sup2))
    assert handover["items"] == original_items

    current_shift = ledger.get_shift(UUID(source_id))
    closed = expect_ok(client.post(f"/shifts/{source_id}/close", json={"expected_version": current_shift.version}, headers=op))
    report = expect_ok(client.post("/reports", json={"shift_id": source_id}, headers=op))
    report = expect_ok(client.post(f"/reports/{report['report_id']}/submit-review", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=op))
    receipt_binding = {
        "record_type": "Report", "record_id": report["report_id"],
        "action": "report.approve", "target_version": report["version"],
        "risk_class": "R2", "payload_digest": ledger.get_report(UUID(report["report_id"])).content.snapshot_digest,
        "approver_id": "p2-sup2", "approver_role": "shift_supervisor",
    }
    expect_ok(client.post("/approvals", json={"record_type": "Report", "record_id": report["report_id"], "action": "report.approve"}, headers=sup2))
    report = expect_ok(client.post(f"/reports/{report['report_id']}/approve", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=sup1))
    frozen = expect_ok(client.post(f"/shifts/{source_id}/freeze", json={"expected_version": closed["version"]}, headers=sup1))
    assert frozen["status"] == "FROZEN"

    ledger.engine.dispose()
    fresh = SqlLedger(url, models=domain_models, engine=make_engine(url))
    try:
        durable_source = fresh.get_shift(UUID(source_id))
        durable_destination = fresh.get_shift(UUID(destination_id))
        durable_event = fresh.get_event(UUID(event["event_id"]))
        durable_task = fresh.get_task(UUID(task["task_id"]))
        durable_handover = fresh.get_handover(UUID(handover["handover_id"]))
        durable_report = fresh.get_report(UUID(report["report_id"]))
        receipt = fresh.get_approval_receipt(record_type="Report", record_id=UUID(report["report_id"]), action="report.approve", target_version=report["version"], approver_id="p2-sup2")
        assert durable_source.ends_at - durable_source.starts_at == timedelta(hours=12)
        assert durable_source.status.value == "FROZEN" and durable_destination.status.value == "OPEN"
        for shift_id in (source_id, destination_id):
            assert {
                (assignment.user_id, assignment.status.value)
                for assignment in fresh.list_assignments_for_shift(UUID(shift_id))
            } == {("p2-op", "ACTIVE"), ("p2-sup1", "ACTIVE"), ("p2-sup2", "ACTIVE")}
        assert durable_event.state.value == "CONFIRMED" and durable_task.status.value == "IN_PROGRESS"
        assert durable_handover.status.value == "ACKNOWLEDGED" and durable_handover.items
        assert [item.model_dump(mode="json") for item in durable_handover.items] == original_items
        assert durable_report.status.value == "FROZEN" and durable_report.is_current is True
        assert receipt is not None
        assert {
            "record_type": receipt.record_type, "record_id": str(receipt.record_id),
            "action": receipt.action, "target_version": receipt.target_version,
            "risk_class": receipt.risk_class, "payload_digest": receipt.payload_digest,
            "approver_id": receipt.approver_id, "approver_role": receipt.approver_role,
        } == receipt_binding
        record_ids = [source_id, destination_id, event["event_id"], task["task_id"], handover["handover_id"], report["report_id"]]
        record_ids.extend(item["assignment_id"] for item in assignments)
        audits = [entry for record_id in record_ids for entry in fresh.audit_entries_for(record_id)]
        observed = Counter((entry["target_id"], entry["action"], entry["actor_id"]) for entry in audits)
        expected = Counter([
            (source_id, "shift.create", "p2-op"),
            (destination_id, "shift.create", "p2-op"),
            *((item["assignment_id"], "shift.assignment.manage", "p2-sup1") for item in assignments),
            (event["event_id"], "event.confirm", "p2-sup1"),
            (task["task_id"], "task.create", "p2-op"),
            (task["task_id"], "task.transition", "p2-op"),
            (handover["handover_id"], "handover.create", "p2-op"),
            (handover["handover_id"], "handover.review", "p2-sup1"),
            (handover["handover_id"], "handover.acknowledge", "p2-sup2"),
            (source_id, "shift.close", "p2-op"),
            (report["report_id"], "report.generate", "p2-op"),
            (report["report_id"], "report.submit_review", "p2-op"),
            (report["report_id"], "approval.create", "p2-sup2"),
            (report["report_id"], "report.approve", "p2-sup1"),
            (report["report_id"], "report.freeze", "p2-sup1"),
            (source_id, "shift.freeze", "p2-sup1"),
        ])
        # Automatic creator assignments are durable under shift.create; event
        # creation is durable without an invented event.create audit.
        assert observed == expected
    finally:
        fresh.engine.dispose()
