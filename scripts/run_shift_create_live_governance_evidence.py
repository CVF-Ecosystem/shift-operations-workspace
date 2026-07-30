#!/usr/bin/env python3
"""Live governance evidence for shift-create admission
(SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29, SPEC section 6/R12-R14). Mirrors
run_incident_live_governance_evidence.py's shape: in-process refusal probes
over the real FastAPI/JWT route chain (observed zero provider calls each),
then a genuine operator-JWT create through ShiftService.create, followed by
exactly one real, non-mocked provider call.

Provider HTTP, sanitization, safe endpoint description, provider-call
accounting and receipt rendering live in
`_shift_create_live_evidence_support.py`; this module is the orchestration
facade and CLI entrypoint only. Production POST /shifts never imports or
invokes anything from either of these two files.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

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

from _shift_create_live_evidence_support import (  # noqa: E402
    ProviderCallCounter,
    call_provider,
    render_receipt,
    safe_endpoint_description,
)

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_SHIFT_CREATE_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_SHIFT_CREATE_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "SHIFT_CREATE_ADMISSION_REPAIR_LIVE_EVIDENCE_RECEIPT.md"


def _window():
    now = datetime.now(timezone.utc)
    return now, now + timedelta(hours=8)


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


def _create(client, headers, *, starts_at=None, ends_at=None):
    s, e = _window()
    return client.post(
        "/shifts",
        params={"name": "Live evidence shift", "starts_at": (starts_at or s).isoformat(), "ends_at": (ends_at or e).isoformat()},
        headers=headers,
    )


def check_shift_create_refusal_gate(counter: ProviderCallCounter) -> list[dict]:
    """Refusal cases: each records the OBSERVED provider-call delta on the
    shared counter (SPEC R12), never a hard-coded literal - none of these
    code paths can reach call_provider, and this proves it empirically."""
    from workspace_api.infrastructure.repository import InMemoryLedger

    results: list[dict] = []

    def _case(name, run, expected_status):
        ledger = InMemoryLedger()
        before = counter.count
        res = _with_ledger(ledger, run)
        outcome = "PASS" if res.status_code == expected_status and ledger.list_shifts() == [] else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    _case("anonymous_create_rejected", lambda c: _create(c, {}), 401)
    _case("malformed_token_create_rejected", lambda c: _create(c, {"Authorization": "Bearer not-a-jwt"}), 401)
    _case("viewer_role_create_rejected", lambda c: _create(c, _auth_headers("shift-ev-viewer", "viewer")), 403)

    s, _ = _window()
    _case(
        "invalid_window_create_rejected",
        lambda c: _create(c, _auth_headers("shift-ev-op", "operator"), starts_at=s, ends_at=s - timedelta(hours=1)),
        422,
    )
    return results


def build_admitted_create_genuine() -> tuple[bool, str]:
    """Construct a genuine operator-JWT create via a minted token and a real
    HTTP request (SPEC R13/R5-R6). SCR-BUILD-REV-F2 repair: asserts exactly
    one shift exists in the ledger (not just one audit keyed to the created
    id) and every required audit field is exactly right - actor_id,
    actor_role, action, record_type, record_id, control_chain, before_state
    and after_state - so a tampered actor or an unexpected second shift
    cannot silently pass as "one actor-bound audit"."""
    from workspace_api.infrastructure.repository import InMemoryLedger

    ledger = InMemoryLedger()
    headers = _auth_headers("shift-ev-op", "operator")

    def _run(client):
        res = _create(client, headers)
        if res.status_code != 200:
            return False, f"create failed: {res.status_code}"
        body = res.json()

        shifts = ledger.list_shifts()
        if len(shifts) != 1:
            return False, f"expected exactly one persisted shift, found {len(shifts)}"
        if str(shifts[0].shift_id) != body["shift_id"]:
            return False, "the one persisted shift does not match the created id"

        audits = ledger.audit_entries_for(body["shift_id"])
        if len(audits) != 1:
            return False, f"expected exactly one audit for the created shift, found {len(audits)}"
        a = audits[0]
        expected = {
            "actor_id": "shift-ev-op",
            "actor_role": "operator",
            "action": "shift.create",
            "record_type": "Shift",
            "record_id": body["shift_id"],
            "control_chain": ["identity", "permission", "create", "audit"],
            "before_state": None,
            "after_state": "OPEN",
        }
        actual = {
            "actor_id": a.actor_id, "actor_role": a.actor_role, "action": a.action,
            "record_type": a.record_type, "record_id": a.record_id,
            "control_chain": list(a.control_chain), "before_state": a.before_state,
            "after_state": a.after_state,
        }
        if actual != expected:
            return False, f"audit fields did not match exactly: expected {expected}, got {actual}"

        return True, (
            "valid operator JWT (shift-ev-op) admitted POST /shifts via a "
            "minted token and a real HTTP request, persisting exactly one "
            "shift and one exactly-field-matched actor-bound shift.create audit"
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
    parser = argparse.ArgumentParser(description="Shift create admission live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    counter = ProviderCallCounter()  # fresh per invocation (SPEC R12 parity)

    print("== shift-create admission refusal gate: refusal cases ==")
    gate_results = check_shift_create_refusal_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("SHIFT CREATE REFUSAL GATE CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine admitted create ==")
    ok, detail = build_admitted_create_genuine()
    print(f"  {detail}")
    if not ok:
        print("GENUINE SHIFT CREATE CONSTRUCTION FAILED", file=sys.stderr)
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
        RECEIPT_PATH, gate_results=gate_results, admitted_detail=detail,
        provider_result=provider_result, model=model, safe_endpoint=safe_endpoint,
        call_count=counter.count,
    )

    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
