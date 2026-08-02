"""Sanitized support for Phase 2 full-shift governance evidence."""
from __future__ import annotations

import json
import hashlib
import os
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

try:
    from scripts._p2c_c3d_live_evidence_support import ProviderCallCounter, call_provider, safe_endpoint_description
except ModuleNotFoundError:
    from _p2c_c3d_live_evidence_support import ProviderCallCounter, call_provider, safe_endpoint_description  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
PRODUCER_ID = "phase2-full-shift-exit-playwright-v1"
SPEC_PATH = ROOT / "apps/workspace-web/e2e/phase2-full-shift-exit.spec.ts"
TOP_LEVEL_KEYS = {"schema_version", "producer_id", "run_id", "checkpoint", "playwright_pass", "queue_checkpoint", "queue_checkpoint_pass", "sanitized", "spec_sha256", "harness_payload", "harness_sha256", "assertions"}
HARNESS_KEYS = {"checkpoint", "api_port", "vite_port", "static_smoke", "static_assets_checked", "playwright_pass", "queue_checkpoint", "queue_checkpoint_pass"}
ASSERTION_KEYS = {"schema_version", "producer_id", "run_id", "browser_contract", "task_reconciliation"}
CONTRACT_KEYS = {"positive_actions", "transport_requests", "automatic_retries", "queue_insertions", "authoritative_reconciliation"}
TASK_KEYS = {"fresh_get_after_replay", "exact_task_id", "exact_committed_version", "status_in_progress", "dom_after_get"}


def canonical_digest(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def auth_headers(user_id: str, role: str) -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}


def new_ledger():
    import workspace_api.domain.models as domain_models
    from workspace_api.infrastructure.repository import InMemoryLedger
    ledger = InMemoryLedger()
    for user_id, role in (("p2-op", "operator"), ("p2-sup1", "shift_supervisor"), ("p2-sup2", "shift_supervisor"), ("p2-out", "operator")):
        ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    return ledger


@contextmanager
def client_for(ledger):
    from fastapi.testclient import TestClient
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def ok(response) -> dict:
    if response.status_code not in (200, 201):
        raise AssertionError(f"unexpected route status {response.status_code}")
    return response.json()


def _serialized(value) -> object:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _serialized(item) for key, item in value.items()}
    return value


def ledger_fingerprint(ledger) -> dict:
    """Canonical whole-ledger mutation fingerprint for isolated refusals."""
    surfaces = {
        "shifts": list(ledger.shifts.values()),
        "assignments": list(ledger.assignments.values()),
        "events": list(ledger.events.values()),
        "tasks": list(ledger.tasks.values()),
        "handovers": list(ledger.handovers.values()),
        "reports": list(ledger.reports.values()),
        "approval_receipts": list(ledger.approval_receipts.values()),
        "audits": ledger._audit.all(),
    }
    canonical_surfaces = {
        name: sorted((_serialized(item) for item in values), key=lambda item: json.dumps(item, sort_keys=True, default=str))
        for name, values in surfaces.items()
    }
    canonical = json.dumps(canonical_surfaces, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "counts": {name: len(values) for name, values in surfaces.items()},
        "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "canonical": canonical,
    }


def audit_tuple(entry) -> tuple[str, str, str]:
    if hasattr(entry, "action"):
        return str(entry.record_id), str(entry.action), str(entry.actor_id)
    return str(entry["record_id"]), str(entry["action"]), str(entry["actor_id"])


def integrated_scenario() -> tuple[bool, str]:
    """One genuine route-level lifecycle with persisted audits."""
    ledger = new_ledger()
    op, sup1, sup2 = auth_headers("p2-op", "operator"), auth_headers("p2-sup1", "shift_supervisor"), auth_headers("p2-sup2", "shift_supervisor")
    start = datetime(2026, 8, 10, 8, tzinfo=timezone.utc)
    with client_for(ledger) as client:
        source = ok(client.post("/shifts", params={"name": "P2 governed source", "starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=12)).isoformat()}, headers=op))
        dest = ok(client.post("/shifts", params={"name": "P2 governed destination", "starts_at": (start + timedelta(hours=12)).isoformat(), "ends_at": (start + timedelta(hours=24)).isoformat()}, headers=op))
        assignments = []
        for shift_id in (source["shift_id"], dest["shift_id"]):
            assignments.append(ok(client.post(f"/shifts/{shift_id}/assignments", json={"user_id": "p2-sup1"}, headers=sup1)))
            assignments.append(ok(client.post(f"/shifts/{shift_id}/assignments", json={"user_id": "p2-sup2"}, headers=sup1)))
        event = ok(client.post("/events", json={"shift_id": source["shift_id"], "event_type": "shift_update", "title": "P2 governed update", "risk_class": "R0"}, headers=op))
        event = ok(client.post(f"/events/{event['event_id']}/confirm", json={"expected_version": event["version"]}, headers=sup1))
        task = ok(client.post("/tasks", json={"shift_id": source["shift_id"], "title": "P2 governed work", "risk_class": "R0"}, headers=op))
        task = ok(client.post(f"/tasks/{task['task_id']}/transition", json={"target_status": "IN_PROGRESS", "expected_version": task["version"]}, headers=op))
        handover = ok(client.post("/handovers", json={"from_shift_id": source["shift_id"], "to_shift_id": dest["shift_id"]}, headers=op))
        original_items = handover["items"]
        handover = ok(client.post(f"/handovers/{handover['handover_id']}/review", json={"expected_version": handover["version"]}, headers=sup1))
        handover = ok(client.post(f"/handovers/{handover['handover_id']}/acknowledge", json={"expected_version": handover["version"]}, headers=sup2))
        current = ledger.get_shift(UUID(source["shift_id"]))
        closed = ok(client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": current.version}, headers=op))
        report = ok(client.post("/reports", json={"shift_id": source["shift_id"]}, headers=op))
        report = ok(client.post(f"/reports/{report['report_id']}/submit-review", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=op))
        ok(client.post("/approvals", json={"record_type": "Report", "record_id": report["report_id"], "action": "report.approve"}, headers=sup2))
        report = ok(client.post(f"/reports/{report['report_id']}/approve", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=sup1))
        frozen = ok(client.post(f"/shifts/{source['shift_id']}/freeze", json={"expected_version": closed["version"]}, headers=sup1))
    handover_obj = ledger.get_handover(UUID(handover["handover_id"]))
    report_obj = ledger.get_report(UUID(report["report_id"]))
    receipt = ledger.get_approval_receipt(
        record_type="Report", record_id=UUID(report["report_id"]), action="report.approve",
        target_version=report["version"], approver_id="p2-sup2",
    )
    record_ids = [source["shift_id"], dest["shift_id"], event["event_id"], task["task_id"], handover["handover_id"], report["report_id"]]
    record_ids.extend(item["assignment_id"] for item in assignments)
    observed_audits = Counter(
        audit_tuple(entry) for record_id in record_ids for entry in ledger.audit_entries_for(record_id)
    )
    expected_audits = Counter([
        (source["shift_id"], "shift.create", "p2-op"),
        (dest["shift_id"], "shift.create", "p2-op"),
        *((item["assignment_id"], "shift.assignment.manage", "p2-sup1") for item in assignments),
        (event["event_id"], "event.confirm", "p2-sup1"),
        (task["task_id"], "task.create", "p2-op"),
        (task["task_id"], "task.transition", "p2-op"),
        (handover["handover_id"], "handover.create", "p2-op"),
        (handover["handover_id"], "handover.review", "p2-sup1"),
        (handover["handover_id"], "handover.acknowledge", "p2-sup2"),
        (source["shift_id"], "shift.close", "p2-op"),
        (report["report_id"], "report.generate", "p2-op"),
        (report["report_id"], "report.submit_review", "p2-op"),
        (report["report_id"], "approval.create", "p2-sup2"),
        (report["report_id"], "report.approve", "p2-sup1"),
        (report["report_id"], "report.freeze", "p2-sup1"),
        (source["shift_id"], "shift.freeze", "p2-sup1"),
    ])
    passed = (
        frozen["status"] == "FROZEN" and event["state"] == "CONFIRMED" and task["status"] == "IN_PROGRESS"
        and handover_obj.status.value == "ACKNOWLEDGED"
        and [_serialized(item) for item in handover_obj.items] == original_items
        and report_obj.status.value == "FROZEN"
        and receipt is not None and receipt.record_type == "Report" and str(receipt.record_id) == report["report_id"]
        and receipt.action == "report.approve" and receipt.target_version == report["version"]
        and receipt.risk_class == "R2" and receipt.payload_digest == report_obj.content.snapshot_digest
        and receipt.approver_id == "p2-sup2" and receipt.approver_role == "shift_supervisor"
        and observed_audits == expected_audits
    )
    return passed, "one 12-hour route-level lineage persisted FROZEN with current Report, acknowledged non-empty handover, IN_PROGRESS task and actor-bound audits"


def validate_browser_evidence(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != TOP_LEVEL_KEYS:
        raise ValueError("BLOCKED_BROWSER_EVIDENCE_INVALID")
    harness = payload.get("harness_payload")
    assertions = payload.get("assertions")
    if not isinstance(harness, dict) or set(harness) != HARNESS_KEYS:
        raise ValueError("BLOCKED_BROWSER_EVIDENCE_INVALID")
    if not isinstance(assertions, dict) or set(assertions) != ASSERTION_KEYS:
        raise ValueError("BLOCKED_BROWSER_EVIDENCE_INVALID")
    contract = assertions.get("browser_contract")
    task = assertions.get("task_reconciliation")
    try:
        UUID(str(payload.get("run_id")))
        valid_run_id = True
    except (TypeError, ValueError):
        valid_run_id = False
    assets = harness.get("static_assets_checked")
    valid_assets = isinstance(assets, list) and all(
        isinstance(item, str) and item.startswith("/") and len(item) <= 200
        and "?" not in item and "#" not in item and "\\" not in item
        for item in assets
    )
    required = (
        payload.get("schema_version") == 1,
        payload.get("producer_id") == PRODUCER_ID,
        valid_run_id,
        payload.get("checkpoint") == "P2_FULL_SHIFT_EXIT",
        payload.get("playwright_pass") is True,
        payload.get("queue_checkpoint") == "bounded_exercised_and_cleaned",
        payload.get("queue_checkpoint_pass") is True,
        payload.get("sanitized") is True,
        payload.get("spec_sha256") == hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
        payload.get("harness_sha256") == canonical_digest(harness),
        assertions.get("schema_version") == 1,
        assertions.get("producer_id") == PRODUCER_ID,
        assertions.get("run_id") == payload.get("run_id"),
        harness.get("checkpoint") == payload.get("checkpoint"),
        harness.get("playwright_pass") is True,
        harness.get("queue_checkpoint") == payload.get("queue_checkpoint"),
        harness.get("queue_checkpoint_pass") is True,
        harness.get("static_smoke") is True,
        isinstance(harness.get("api_port"), int),
        isinstance(harness.get("vite_port"), int),
        valid_assets,
        isinstance(contract, dict) and set(contract) == CONTRACT_KEYS,
        contract == {"positive_actions": "rendered_ui", "transport_requests": 1, "automatic_retries": 0, "queue_insertions": 0, "authoritative_reconciliation": True},
        isinstance(task, dict) and set(task) == TASK_KEYS,
        isinstance(task, dict) and all(value is True for value in task.values()),
    )
    if not all(required):
        raise ValueError("BLOCKED_BROWSER_EVIDENCE_INVALID")
    return {"checkpoint": payload["checkpoint"], "playwright_pass": True, "queue_checkpoint_pass": True, "transport_ambiguity_pass": True}


RESERVATION_HEADING = "## Replacement provider attempt reservation"
RESULT_HEADING = "## Replacement provider attempt result"


@contextmanager
def _locked_receipt(path: Path):
    """Serialize the read/check/append transaction across competing processes."""
    with path.open("r+", encoding="utf-8") as stream:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield stream
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def reserve_replacement_attempt(path: Path, attempt_id: str) -> None:
    UUID(attempt_id)
    with _locked_receipt(path) as stream:
        historical = stream.read()
        if "INVALIDATED_BY_REVIEW_FAIL" not in historical or RESERVATION_HEADING in historical or RESULT_HEADING in historical:
            raise ValueError("BLOCKED_PROVIDER_RECEIPT_HISTORY")
        stream.seek(0, os.SEEK_END)
        stream.write(f"\n\n{RESERVATION_HEADING}\n\n- State: **RESERVED_BEFORE_NETWORK**\n- Attempt id: `{attempt_id}`\n- Budget effect: sole replacement slot consumed; every rerun is fail-closed.\n")
        stream.flush()
        os.fsync(stream.fileno())


def render_receipt(path: Path, gates: list[dict], durable_detail: str, browser: dict, provider: dict, model: str, endpoint: str, calls: int, attempt_id: str) -> None:
    accepted = calls == 1 and provider.get("outcome") == "PASS" and provider.get("reached_server") is True and provider.get("expected_token_match") is True
    disposition = "ACCEPTED" if accepted else "NOT_ACCEPTED_PROVIDER_FAILURE"
    lines = [
        "", RESULT_HEADING, "",
        f"- Attempt id: `{attempt_id}`", f"- Disposition: **{disposition}**",
        f"- Replacement outcome: {provider.get('outcome')}", "",
        "Sanitized replacement receipt: no API key, bearer/JWT, DSN, raw provider body, URL credentials/query/fragment or raw exception.", "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)", f"- Model: {model}",
        f"- Endpoint class: {endpoint}", f"- Browser checkpoint: {browser['checkpoint']}", "",
        "### Replacement-run zero-call refusal gates", "", "| Case | Outcome | HTTP status | Replacement-run calls |", "|---|---|---:|---:|",
    ]
    lines.extend(f"| {gate['case']} | {gate['outcome']} | {gate['status']} | {gate['calls']} |" for gate in gates)
    lines += [
        "", "### Replacement admitted evidence", "", f"- Durable scenario: {durable_detail}",
        "- Browser: Playwright PASS; bounded queue PASS; transport ambiguity PASS (one request, zero retry/queue, authoritative reconciliation).", "",
        "### Replacement provider result", "", f"- Outcome: **{provider.get('outcome')}**", f"- Reached provider: **{provider.get('reached_server', False)}**",
        f"- HTTP status: {provider.get('http_status')}", f"- Expected token matched: **{provider.get('expected_token_match', False)}**",
        f"- Replacement-run calls: **{calls}** (zero before admission; exactly one after)",
        f"- Tranche physical calls: **{1 + calls}** (first invalidated plus this attempt)",
        f"- Accepted final calls: **{1 if accepted else 0}**", "",
        "### Final claim boundary", "",
        "This is bounded Phase 2 functional exit evidence on real browser/FastAPI, local durable stores and one provider receipt. It is not a wall-clock soak, push/exactly-once, fully-offline, production-readiness, Phase 3 or external-channel claim.", "",
    ]
    reservation = f"- Attempt id: `{attempt_id}`"
    with _locked_receipt(path) as stream:
        historical = stream.read()
        if RESERVATION_HEADING not in historical or reservation not in historical or RESULT_HEADING in historical:
            raise ValueError("BLOCKED_PROVIDER_RECEIPT_HISTORY")
        stream.seek(0, os.SEEK_END)
        stream.write("\n".join(lines))
        stream.flush()
        os.fsync(stream.fileno())
