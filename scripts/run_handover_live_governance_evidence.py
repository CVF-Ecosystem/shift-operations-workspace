#!/usr/bin/env python3
"""Live governance evidence for the handover vertical (P2A-HANDOVER-VERTICAL,
SPEC section 6/R16): in-process refusal probes over the real FastAPI/JWT
route chain (observed zero provider calls each), then a genuine sender
review + distinct receiver acknowledgement + a real approved END_SHIFT
report + freeze, followed by exactly one real, non-mocked provider call.
Provider HTTP/sanitization/receipt rendering live in
`_handover_live_evidence_support.py`; this module is the orchestration
facade and CLI entrypoint only."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

REPO_ROOT = Path(__file__).resolve().parents[1]
for _rel in (
    "apps/workspace-api/src",
    "packages/cvf-runtime/src",
    "packages/operations-ledger/src",
    "packages/operations-domain/src",
    "packages/ai-providers/alibaba",
):
    sys.path.insert(0, str(REPO_ROOT / _rel))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _handover_live_evidence_support import (  # noqa: E402
    ProviderCallCounter,
    call_provider,
    render_receipt,
    safe_endpoint_description,
)

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_HANDOVER_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_HANDOVER_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2A_HANDOVER_LIVE_EVIDENCE_RECEIPT.md"


def _new_ledger_and_shift(prefix: str):
    from workspace_api.infrastructure.repository import InMemoryLedger
    ledger = InMemoryLedger()
    shift = _new_shift(prefix)
    ledger.create_shift(shift)
    return ledger, shift

def _new_shift(prefix: str):
    from operations_domain.models import Shift
    now = datetime.now(timezone.utc)
    return Shift(name=f"{prefix} shift", starts_at=now, ends_at=now + timedelta(hours=8))

def _auth_headers(user_id: str, role: str) -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}

def _with_ledger(ledger, fn):
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        from fastapi.testclient import TestClient
        return fn(TestClient(app))
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _create(client, from_shift_id, to_shift_id, headers):
    return client.post(
        "/handovers",
        json={"from_shift_id": str(from_shift_id), "to_shift_id": str(to_shift_id)},
        headers=headers,
    )


def _review(client, handover_id, headers):
    return client.post(f"/handovers/{handover_id}/review", json={}, headers=headers)

def _acknowledge(client, handover_id, headers):
    return client.post(f"/handovers/{handover_id}/acknowledge", json={}, headers=headers)

def _close(client, shift_id, headers):
    return client.post(f"/shifts/{shift_id}/close", headers=headers)

def _freeze(client, shift_id, headers):
    return client.post(f"/shifts/{shift_id}/freeze", json={}, headers=headers)


def _make_ready_report(ledger, client, shift_id, operator_headers, approver_headers):
    """A real current, APPROVED END_SHIFT report (P2R-OPERATIONAL-REPORT-
    FREEZE-PREREQUISITE) - the retired override no longer exists."""
    from cvf_runtime.identity import Principal
    from workspace_api.application import approval_service
    import workspace_api.domain.models as _domain_models
    generate_res = client.post("/reports", json={"shift_id": str(shift_id)}, headers=operator_headers)
    report_id = generate_res.json()["report_id"]
    client.post(f"/reports/{report_id}/submit-review", json={}, headers=operator_headers)
    ledger.add_user(_domain_models.User(user_id="hov-ev-rep-approver", username="hov-ev-rep-approver", password_hash="x", role="shift_supervisor"))
    approval_service.create_approval_receipt(
        ledger, Principal(user_id="hov-ev-rep-approver", role="shift_supervisor"),
        record_type="Report", action="report.approve", record_id=UUID(report_id),
    )
    return client.post(f"/reports/{report_id}/approve", json={}, headers=approver_headers)


def check_handover_freeze_gate(counter: ProviderCallCounter) -> list[dict]:
    """Refusal cases: each records the OBSERVED provider-call delta on the
    shared counter (SPEC R15-B parity), never a hard-coded literal - none of
    these code paths can reach call_provider, and this proves it empirically."""
    results: list[dict] = []
    op = _auth_headers("hov-ev-op", "operator")
    sup1 = _auth_headers("hov-ev-sup1", "shift_supervisor")
    sup2 = _auth_headers("hov-ev-sup2", "shift_supervisor")

    def _case(name, ledger, run):
        before = counter.count
        res = _with_ledger(ledger, run)
        outcome = "PASS" if res.status_code == 409 else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    ledger, shift = _new_ledger_and_shift("missing-handover")
    def _missing_handover(client):
        _close(client, shift.shift_id, op)
        return _freeze(client, shift.shift_id, sup1)
    _case("missing_handover_freeze_rejected", ledger, _missing_handover)

    ledger, shift = _new_ledger_and_shift("draft-only")
    dest = _new_shift("dest")
    ledger.create_shift(dest)
    def _reviewed_only(client):
        create_res = _create(client, shift.shift_id, dest.shift_id, op)
        handover_id = create_res.json()["handover_id"]
        _review(client, handover_id, sup1)
        _close(client, shift.shift_id, op)
        return _freeze(client, shift.shift_id, sup1)
    _case("reviewed_only_handover_freeze_rejected", ledger, _reviewed_only)

    ledger, shift = _new_ledger_and_shift("self-ack")
    dest = _new_shift("dest")
    ledger.create_shift(dest)
    def _self_ack(client):
        create_res = _create(client, shift.shift_id, dest.shift_id, op)
        handover_id = create_res.json()["handover_id"]
        _review(client, handover_id, sup1)
        return _acknowledge(client, handover_id, sup1)
    _case("self_acknowledgement_rejected", ledger, _self_ack)

    ledger, shift = _new_ledger_and_shift("stale")
    dest = _new_shift("dest")
    ledger.create_shift(dest)
    def _stale(client):
        from operations_domain.models import Task, TaskStatus
        task = Task(shift_id=shift.shift_id, title="Inspect crane")
        ledger.add_task(task)
        create_res = _create(client, shift.shift_id, dest.shift_id, op)
        handover_id = create_res.json()["handover_id"]
        _review(client, handover_id, sup1)
        _acknowledge(client, handover_id, sup2)
        mutated = ledger.get_task(task.task_id)
        mutated.status = TaskStatus.IN_PROGRESS
        ledger.put_task(mutated)
        _close(client, shift.shift_id, op)
        return _freeze(client, shift.shift_id, sup1)

    _case("stale_snapshot_freeze_rejected", ledger, _stale)

    return results


def build_review_acknowledge_and_freeze_genuine() -> tuple[bool, str]:
    """Construct a genuine sender review, distinct receiver acknowledgement
    and freeze via minted JWTs and real HTTP requests (SPEC R16)."""
    ledger, shift = _new_ledger_and_shift("genuine")
    dest = _new_shift("genuine-dest")
    ledger.create_shift(dest)
    op = _auth_headers("hov-ev-op", "operator")
    sup1 = _auth_headers("hov-ev-sup1", "shift_supervisor")
    sup2 = _auth_headers("hov-ev-sup2", "shift_supervisor")

    def _run(client):
        create_res = _create(client, shift.shift_id, dest.shift_id, op)
        if create_res.status_code != 200:
            return False, f"create failed: {create_res.status_code}"
        handover_id = create_res.json()["handover_id"]

        review_res = _review(client, handover_id, sup1)
        if review_res.status_code != 200:
            return False, f"review failed: {review_res.status_code}"

        ack_res = _acknowledge(client, handover_id, sup2)
        if ack_res.status_code != 200 or ack_res.json()["status"] != "ACKNOWLEDGED":
            return False, f"acknowledge failed: {ack_res.status_code}"

        close_res = _close(client, shift.shift_id, op)
        if close_res.status_code != 200:
            return False, f"close failed: {close_res.status_code}"

        report_res = _make_ready_report(ledger, client, shift.shift_id, op, sup1)
        if report_res.status_code != 200 or report_res.json()["status"] != "APPROVED":
            return False, f"report approval failed: {report_res.status_code}"

        freeze_res = _freeze(client, shift.shift_id, sup1)
        if freeze_res.status_code != 200 or freeze_res.json()["status"] != "FROZEN":
            return False, f"freeze failed: {freeze_res.status_code}"

        return True, (
            "distinct authenticated reviewer (hov-ev-sup1) and receiver "
            "(hov-ev-sup2) satisfied handover review/acknowledgement; a real "
            "END_SHIFT report was generated/reviewed/approved; freeze "
            "succeeded via open_handover_items_linked and report_approved - "
            "no override exists anymore"
        )

    return _with_ledger(ledger, _run)


def _key_present() -> tuple[bool, str | None]:
    for name in KEY_ENV_NAMES:
        if os.environ.get(name, "").strip():
            return True, name
    return False, None


def _endpoint() -> str:
    base_url = next(
        (os.environ[n].strip() for n in BASE_URL_ENV_NAMES if os.environ.get(n, "").strip()),
        DEFAULT_BASE_URL,
    ).rstrip("/")
    return base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"


def main() -> int:
    parser = argparse.ArgumentParser(description="Handover live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    counter = ProviderCallCounter()  # fresh per invocation (SPEC R15-B parity)

    print("== handover freeze-readiness gate: refusal cases ==")
    gate_results = check_handover_freeze_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("HANDOVER FREEZE GATE REFUSAL CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine review, acknowledgement and freeze ==")
    ok, detail = build_review_acknowledge_and_freeze_genuine()
    print(f"  {detail}")
    if not ok:
        print("GENUINE HANDOVER/FREEZE CONSTRUCTION FAILED", file=sys.stderr)
        return 1

    present, key_env_name = _key_present()
    print(f"== provider credential present: {present} ==")
    if args.dry_run:
        return 0
    if not present:
        print("READY_FOR_LIVE_EVIDENCE: no provider key", file=sys.stderr)
        return 2

    try:
        from select_model import select_model
        model = select_model()
    except Exception as exc:
        print(f"READY_FOR_LIVE_EVIDENCE: model select failed: {exc}", file=sys.stderr)
        return 2

    endpoint = _endpoint()
    safe_endpoint = safe_endpoint_description(endpoint)
    print(f"== calling provider (model={model}, endpoint={safe_endpoint}) ==")
    provider_result = call_provider(
        model=model, api_key=os.environ[key_env_name], endpoint=endpoint,
        prompt=PROMPT, expected_token=EXPECTED_TOKEN, counter=counter,
    )
    print(f"  outcome: {provider_result['outcome']} (http {provider_result.get('http_status')})")
    render_receipt(
        RECEIPT_PATH, gate_results=gate_results, quorum_detail=detail,
        provider_result=provider_result, model=model, safe_endpoint=safe_endpoint,
        call_count=counter.count,
    )

    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
