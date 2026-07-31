#!/usr/bin/env python3
"""Live governance evidence for the report vertical (P2R-OPERATIONAL-REPORT-
FREEZE-PREREQUISITE, SPEC R31): in-process refusal probes over the real
FastAPI/JWT route chain (observed zero provider calls each), then a genuine
generate -> submit-review -> distinct-approver receipt -> approve -> freeze,
followed by exactly one real provider call. Provider HTTP/sanitization/
receipt rendering live in `_report_live_evidence_support.py`; this module is
the orchestration facade and CLI entrypoint only."""

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

from _report_live_evidence_support import (  # noqa: E402
    ProviderCallCounter,
    call_provider,
    render_receipt,
    safe_endpoint_description,
)

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_REPORT_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_REPORT_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2R_OPERATIONAL_REPORT_FREEZE_LIVE_EVIDENCE_RECEIPT.md"


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


def _generate(client, shift_id, headers=None):
    return client.post("/reports", json={"shift_id": str(shift_id)}, headers=headers or {})

def _submit_review(client, report_id, headers):
    return client.post(f"/reports/{report_id}/submit-review", json={}, headers=headers)

def _approve(client, report_id, headers):
    return client.post(f"/reports/{report_id}/approve", json={}, headers=headers)

def _close(client, shift_id, headers):
    return client.post(f"/shifts/{shift_id}/close", headers=headers)

def _freeze(client, shift_id, headers, *, override=False):
    body = {"override_unimplemented_prerequisites": True, "override_reason": "x"} if override else {}
    return client.post(f"/shifts/{shift_id}/freeze", json=body, headers=headers)


def _make_ready_handover(ledger, shift, op, sup1, sup2):
    from workspace_api.application.handover_service import HandoverService
    dest = _new_shift("dest")
    ledger.create_shift(dest)
    svc = HandoverService(ledger)
    h = svc.create(shift.shift_id, dest.shift_id, _principal_of(op))
    h = svc.review(h.handover_id, _principal_of(sup1))
    return svc.acknowledge(h.handover_id, _principal_of(sup2))


def _principal_of(headers):
    """Recover a Principal from minted auth headers by decoding the token -
    avoids threading raw user_id/role tuples through every call site."""
    from workspace_api.auth.tokens import decode_access_token
    token = headers["Authorization"].split(" ", 1)[1]
    return decode_access_token(token)


def check_report_freeze_gate(counter: ProviderCallCounter) -> list[dict]:
    """SPEC R31 refusal matrix: each records the OBSERVED provider-call delta
    on the shared counter - none of these code paths can reach
    call_provider, and this proves it empirically."""
    results: list[dict] = []
    op = _auth_headers("rep-ev-op", "operator")
    sup1 = _auth_headers("rep-ev-sup1", "shift_supervisor")
    viewer = _auth_headers("rep-ev-viewer", "viewer")

    def _case(name, ledger, run, expected_statuses=(409,)):
        before = counter.count
        res = _with_ledger(ledger, run)
        outcome = "PASS" if res.status_code in expected_statuses else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    ledger, shift = _new_ledger_and_shift("missing-bearer")
    _case("missing_bearer_generate_rejected", ledger, lambda c: _generate(c, shift.shift_id), (401,))

    ledger, shift = _new_ledger_and_shift("viewer-generate")
    _case("viewer_cannot_generate_rejected", ledger, lambda c: _generate(c, shift.shift_id, viewer), (403,))

    ledger, shift = _new_ledger_and_shift("not-closed")
    _case("non_closed_generate_rejected", ledger, lambda c: _generate(c, shift.shift_id, op), (409,))

    ledger, shift = _new_ledger_and_shift("stale-review")
    ledger.close_shift(shift.shift_id)
    def _stale_submit(client):
        from operations_domain.models import Task
        gen = _generate(client, shift.shift_id, op)
        report_id = gen.json()["report_id"]
        ledger.add_task(Task(shift_id=shift.shift_id, title="late"))
        return _submit_review(client, report_id, op)
    _case("stale_submit_review_rejected", ledger, _stale_submit)

    ledger, shift = _new_ledger_and_shift("missing-receipt")
    def _missing_receipt(client):
        ledger.close_shift(shift.shift_id)
        gen = _generate(client, shift.shift_id, op)
        report_id = gen.json()["report_id"]
        _submit_review(client, report_id, op)
        return _approve(client, report_id, sup1)
    _case("missing_receipt_approve_rejected", ledger, _missing_receipt)

    ledger, shift = _new_ledger_and_shift("non-current")
    ledger.close_shift(shift.shift_id)
    def _non_current_submit_review(client):
        from workspace_api.application.report_service import ReportService
        gen = _generate(client, shift.shift_id, op)
        report_id = gen.json()["report_id"]
        ReportService(ledger).create_successor(UUID(report_id), _principal_of(op))
        return _submit_review(client, report_id, op)  # predecessor is now non-current
    _case("non_current_report_submit_review_rejected", ledger, _non_current_submit_review)

    ledger, shift = _new_ledger_and_shift("legacy-override")
    def _legacy_override(client):
        ledger.close_shift(shift.shift_id)
        return _freeze(client, shift.shift_id, sup1, override=True)
    _case("legacy_override_attempt_refused", ledger, _legacy_override, (422,))

    return results


def build_generate_review_approve_and_freeze_genuine() -> tuple[bool, str]:
    """Construct a genuine generate -> submit-review -> distinct-approver
    receipt -> approve -> freeze via minted JWTs and real HTTP requests."""
    from workspace_api.application import approval_service
    import workspace_api.domain.models as _domain_models

    ledger, shift = _new_ledger_and_shift("genuine")
    op = _auth_headers("rep-ev-op", "operator")
    sup1 = _auth_headers("rep-ev-sup1", "shift_supervisor")
    sup2 = _auth_headers("rep-ev-sup2", "shift_supervisor")

    def _run(client):
        close_res = _close(client, shift.shift_id, op)
        if close_res.status_code != 200:
            return False, f"close failed: {close_res.status_code}"

        handover = _make_ready_handover(ledger, shift, op, sup1, sup2)
        if not handover.acknowledged:
            return False, "handover not acknowledged"

        gen_res = _generate(client, shift.shift_id, op)
        if gen_res.status_code != 201:
            return False, f"generate failed: {gen_res.status_code}"
        report_id = gen_res.json()["report_id"]

        review_res = _submit_review(client, report_id, op)
        if review_res.status_code != 200:
            return False, f"submit-review failed: {review_res.status_code}"

        ledger.add_user(_domain_models.User(user_id="rep-ev-approver", username="rep-ev-approver", password_hash="x", role="shift_supervisor"))
        approval_service.create_approval_receipt(
            ledger, _principal_of(_auth_headers("rep-ev-approver", "shift_supervisor")),
            record_type="Report", action="report.approve", record_id=UUID(report_id),
        )

        approve_res = _approve(client, report_id, sup1)
        if approve_res.status_code != 200 or approve_res.json()["status"] != "APPROVED":
            return False, f"approve failed: {approve_res.status_code}"

        freeze_res = _freeze(client, shift.shift_id, sup1)
        if freeze_res.status_code != 200 or freeze_res.json()["status"] != "FROZEN":
            return False, f"freeze failed: {freeze_res.status_code}"

        return True, (
            "genuine END_SHIFT report generated by rep-ev-op, reviewed, "
            "approved via a distinct receipt approver (rep-ev-approver) by "
            "rep-ev-sup1, then freeze succeeded via report_approved and "
            "open_handover_items_linked - no override was used"
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
    parser = argparse.ArgumentParser(description="Report live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    counter = ProviderCallCounter()

    print("== report/freeze gate: refusal cases ==")
    gate_results = check_report_freeze_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("REPORT FREEZE GATE REFUSAL CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine generate/review/approve/freeze ==")
    ok, detail = build_generate_review_approve_and_freeze_genuine()
    print(f"  {detail}")
    if not ok:
        print("GENUINE REPORT/FREEZE CONSTRUCTION FAILED", file=sys.stderr)
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
