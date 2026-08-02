#!/usr/bin/env python3
"""Phase 2 refusal/durability/browser gates, then exactly one provider call."""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")
ROOT = Path(__file__).resolve().parents[1]
for rel in ("apps/workspace-api/src", "packages/cvf-runtime/src", "packages/operations-ledger/src", "packages/operations-domain/src", "packages/ai-providers/alibaba", "scripts"):
    sys.path.insert(0, str(ROOT / rel))

from _phase2_full_shift_live_evidence_support import (  # noqa: E402
    ProviderCallCounter, auth_headers, call_provider, client_for, integrated_scenario,
    ledger_fingerprint, new_ledger, ok, render_receipt, reserve_replacement_attempt, safe_endpoint_description,
    validate_browser_evidence,
)

KEYS = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
EXPECTED = "CVF_PHASE2_FULL_SHIFT_EXIT_OK"
PROMPT = f"Reply with exactly this token and nothing else: {EXPECTED}"
RECEIPT = ROOT / "docs/decisions/PHASE2_FULL_SHIFT_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md"


def _base_scenario():
    ledger = new_ledger()
    op, sup1 = auth_headers("p2-op", "operator"), auth_headers("p2-sup1", "shift_supervisor")
    start = datetime(2026, 8, 12, 8, tzinfo=timezone.utc)
    with client_for(ledger) as client:
        source = ok(client.post("/shifts", params={"name": "refusal source", "starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=12)).isoformat()}, headers=op))
        dest = ok(client.post("/shifts", params={"name": "refusal dest", "starts_at": (start + timedelta(hours=12)).isoformat(), "ends_at": (start + timedelta(hours=24)).isoformat()}, headers=op))
        ok(client.post(f"/shifts/{source['shift_id']}/assignments", json={"user_id": "p2-sup1"}, headers=sup1))
    return ledger, source, dest


def refusal_matrix(counter: ProviderCallCounter) -> list[dict]:
    results: list[dict] = []

    def record(name: str, ledger, before: dict, response, expected: int):
        after = ledger_fingerprint(ledger)
        passed = response.status_code == expected and before == after and counter.count == 0
        results.append({
            "case": name, "outcome": "PASS" if passed else "FAIL",
            "status": response.status_code, "calls": counter.count,
        })

    op = auth_headers("p2-op", "operator")
    sup1 = auth_headers("p2-sup1", "shift_supervisor")
    sup2 = auth_headers("p2-sup2", "shift_supervisor")
    outsider = auth_headers("p2-out", "operator")

    def isolated(name: str, arrange_and_request, expected: int):
        ledger, source, dest = _base_scenario()
        with client_for(ledger) as client:
            response, before = arrange_and_request(client, ledger, source, dest)
            record(name, ledger, before, response, expected)

    def snap_request(ledger, request):
        before = ledger_fingerprint(ledger)
        return request(), before

    isolated("anonymous_shift_create", lambda client, ledger, source, dest: snap_request(
        ledger, lambda: client.post("/shifts", params={"name": "x", "starts_at": "2026-08-01T00:00:00Z", "ends_at": "2026-08-01T12:00:00Z"})
    ), 401)
    isolated("anonymous_shift_close", lambda client, ledger, source, dest: snap_request(
        ledger, lambda: client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": source["version"]})
    ), 401)
    isolated("unassigned_read", lambda client, ledger, source, dest: snap_request(
        ledger, lambda: client.get("/tasks", params={"shift_id": source["shift_id"]}, headers=outsider)
    ), 404)

    def task_refusal(client, ledger, source, _dest, *, stale: bool):
        task = ok(client.post("/tasks", json={"shift_id": source["shift_id"], "title": "refusal task", "risk_class": "R0"}, headers=op))
        return snap_request(ledger, lambda: client.post(
            f"/tasks/{task['task_id']}/transition",
            json={"target_status": "IN_PROGRESS", "expected_version": 999 if stale else task["version"]},
            headers=op if stale else outsider,
        ))

    isolated("unassigned_mutation", lambda *args: task_refusal(*args, stale=False), 404)
    isolated("stale_task_cas", lambda *args: task_refusal(*args, stale=True), 409)
    isolated("stale_close_cas", lambda client, ledger, source, dest: snap_request(
        ledger, lambda: client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": 999}, headers=op)
    ), 409)

    def reviewed_handover(client, source, dest):
        task = ok(client.post("/tasks", json={"shift_id": source["shift_id"], "title": "handover item", "risk_class": "R0"}, headers=op))
        handover = ok(client.post("/handovers", json={"from_shift_id": source["shift_id"], "to_shift_id": dest["shift_id"]}, headers=op))
        assert handover["items"] and handover["items"][0]["source_record_id"] == task["task_id"]
        return ok(client.post(f"/handovers/{handover['handover_id']}/review", json={"expected_version": handover["version"]}, headers=sup1))

    def ack_without_assignment(client, ledger, source, dest):
        handover = reviewed_handover(client, source, dest)
        return snap_request(ledger, lambda: client.post(
            f"/handovers/{handover['handover_id']}/acknowledge",
            json={"expected_version": handover["version"]}, headers=sup2,
        ))

    isolated("handover_ack_without_destination_assignment", ack_without_assignment, 404)

    def acknowledge(client, source, dest):
        ok(client.post(f"/shifts/{dest['shift_id']}/assignments", json={"user_id": "p2-sup2"}, headers=sup1))
        handover = reviewed_handover(client, source, dest)
        return ok(client.post(f"/handovers/{handover['handover_id']}/acknowledge", json={"expected_version": handover["version"]}, headers=sup2))

    def report_in_review(client, source):
        report = ok(client.post("/reports", json={"shift_id": source["shift_id"]}, headers=op))
        return ok(client.post(f"/reports/{report['report_id']}/submit-review", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=op))

    def approve_report(client, source):
        report = report_in_review(client, source)
        ok(client.post("/approvals", json={"record_type": "Report", "record_id": report["report_id"], "action": "report.approve"}, headers=sup2))
        return ok(client.post(f"/reports/{report['report_id']}/approve", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=sup1))

    def approval_without_receipt(client, ledger, source, dest):
        ok(client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": source["version"]}, headers=op))
        report = report_in_review(client, source)
        return snap_request(ledger, lambda: client.post(f"/reports/{report['report_id']}/approve", json={"expected_version": report["version"], "expected_status": report["status"]}, headers=sup1))

    isolated("report_approval_without_receipt", approval_without_receipt, 409)

    def freeze_before_close(client, ledger, source, dest):
        acknowledge(client, source, dest)
        return snap_request(ledger, lambda: client.post(f"/shifts/{source['shift_id']}/freeze", json={"expected_version": source["version"]}, headers=sup1))

    isolated("freeze_before_close", freeze_before_close, 409)

    def freeze_without_handover(client, ledger, source, dest):
        ok(client.post(f"/shifts/{source['shift_id']}/assignments", json={"user_id": "p2-sup2"}, headers=sup1))
        closed = ok(client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": source["version"]}, headers=op))
        approve_report(client, source)
        return snap_request(ledger, lambda: client.post(f"/shifts/{source['shift_id']}/freeze", json={"expected_version": closed["version"]}, headers=sup1))

    isolated("freeze_without_acknowledged_current_handover", freeze_without_handover, 409)

    def freeze_ready(client, source, dest):
        acknowledge(client, source, dest)
        ok(client.post(f"/shifts/{source['shift_id']}/assignments", json={"user_id": "p2-sup2"}, headers=sup1))
        closed = ok(client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": source["version"]}, headers=op))
        approve_report(client, source)
        return closed

    def stale_freeze(client, ledger, source, dest):
        freeze_ready(client, source, dest)
        return snap_request(ledger, lambda: client.post(f"/shifts/{source['shift_id']}/freeze", json={"expected_version": 999}, headers=sup1))

    isolated("stale_freeze_cas", stale_freeze, 409)

    def freeze_without_approved_report(client, ledger, source, dest):
        acknowledge(client, source, dest)
        closed = ok(client.post(f"/shifts/{source['shift_id']}/close", json={"expected_version": source["version"]}, headers=op))
        report_in_review(client, source)
        return snap_request(ledger, lambda: client.post(f"/shifts/{source['shift_id']}/freeze", json={"expected_version": closed["version"]}, headers=sup1))

    isolated("freeze_without_current_approved_report", freeze_without_approved_report, 409)
    return results


def endpoint() -> str:
    base = next((os.environ[name].strip() for name in BASES if os.environ.get(name, "").strip()), DEFAULT_BASE).rstrip("/")
    return base if base.endswith("/chat/completions") else f"{base}/chat/completions"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-evidence-json", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    counter = ProviderCallCounter()
    try:
        browser = validate_browser_evidence(args.browser_evidence_json)
    except (OSError, ValueError):
        return 3
    gates = refusal_matrix(counter)
    if any(gate["outcome"] != "PASS" or gate["calls"] != 0 for gate in gates):
        return 1
    durable_ok, durable_detail = integrated_scenario()
    if not durable_ok or counter.count != 0:
        return 1
    if args.dry_run:
        return 0
    if os.environ.get("PHASE2_EXACT_PARENT_REHEARSAL") != "PASS":
        return 4
    try:
        receipt_history = RECEIPT.read_text(encoding="utf-8")
    except OSError:
        return 5
    if (
        "INVALIDATED_BY_REVIEW_FAIL" not in receipt_history
        or "## Replacement provider attempt reservation" in receipt_history
        or "## Replacement provider attempt result" in receipt_history
    ):
        return 5
    key_name = next((name for name in KEYS if os.environ.get(name, "").strip()), None)
    if key_name is None:
        return 2
    try:
        from select_model import select_model
        model = select_model()
    except Exception:
        return 2
    target = endpoint()
    attempt_id = str(uuid4())
    try:
        reserve_replacement_attempt(RECEIPT, attempt_id)
    except (OSError, ValueError):
        return 5
    result = call_provider(model=model, api_key=os.environ[key_name], endpoint=target, prompt=PROMPT, expected_token=EXPECTED, counter=counter)
    try:
        render_receipt(RECEIPT, gates, durable_detail, browser, result, model, safe_endpoint_description(target), counter.count, attempt_id)
    except (OSError, ValueError):
        return 5
    return 0 if counter.count == 1 and result.get("outcome") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
