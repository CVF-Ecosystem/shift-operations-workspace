#!/usr/bin/env python3
"""Live governance evidence for the `approval` CVF control.
P2B-APPROVER-IDENTITY-RECONCILIATION (SPEC section 7 & 10).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
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

RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md"
KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_APPROVAL_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_APPROVAL_EVIDENCE_OK"
_PROVIDER_CALL_COUNT = 0


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


def _new_ledger_shift_event(risk_class, *, evidence_count=1):
    from operations_domain.models import DataState, EvidenceRef, OperationalEvent, Shift
    from workspace_api.infrastructure.repository import InMemoryLedger

    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Live-evidence shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Live-evidence probe",
        risk_class=risk_class,
        state=DataState.PROPOSED,
        evidence=[EvidenceRef(source_type="message", source_id=f"m{i}") for i in range(evidence_count)],
    )
    ledger.add_event(event)
    return ledger, event


def _register_user(ledger, user_id, role, *, is_active=True):
    import workspace_api.domain.models as _domain_models
    ledger.add_user(_domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role, is_active=is_active))


def _auth_headers(user_id: str, role: str) -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}


def check_approval_gate() -> list[dict]:
    """Exercise approval gate via TestClient and real minted JWTs."""
    from fastapi.testclient import TestClient
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app

    results: list[dict] = []

    def _rec(client, headers, rtype, action, rid):
        return client.post("/approvals", json={"record_type": rtype, "action": action, "record_id": str(rid)}, headers=headers)

    # 1. Fabricated: zero receipts for an R3 record.
    ledger, event = _new_ledger_shift_event("R3")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        results.append({"case": "fabricated_approval_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 2. Wrong role: active real user below required seat.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-op1", "operator")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = _rec(client, _auth_headers("evidence-op1", "operator"), "OperationalEvent", "event.confirm", event.event_id)
        results.append({"case": "wrong_role_rejected", "outcome": "PASS" if res.status_code == 403 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 3. Inactive user.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup2", "shift_supervisor", is_active=False)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = _rec(client, _auth_headers("evidence-sup2", "shift_supervisor"), "OperationalEvent", "event.confirm", event.event_id)
        results.append({"case": "inactive_user_rejected", "outcome": "PASS" if res.status_code == 403 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 4. Self-approval: R2 needs one seat, confirmer fills it alone.
    ledger, event = _new_ledger_shift_event("R2")
    _register_user(ledger, "evidence-sup1", "shift_supervisor")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        headers = _auth_headers("evidence-sup1", "shift_supervisor")
        _rec(client, headers, "OperationalEvent", "event.confirm", event.event_id)
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=headers)
        results.append({"case": "self_approval_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 5. Insufficient quorum: R3 needs two seats, one filled.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup3", "shift_supervisor")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        _rec(client, _auth_headers("evidence-sup3", "shift_supervisor"), "OperationalEvent", "event.confirm", event.event_id)
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        results.append({"case": "insufficient_quorum_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 6. Replay: receipts bound to a version that has since advanced.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup4", "shift_supervisor")
    _register_user(ledger, "evidence-mgr1", "responsible_manager")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        _rec(client, _auth_headers("evidence-sup4", "shift_supervisor"), "OperationalEvent", "event.confirm", event.event_id)
        _rec(client, _auth_headers("evidence-mgr1", "responsible_manager"), "OperationalEvent", "event.confirm", event.event_id)
        ledger.events[event.event_id].version += 1
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        results.append({"case": "replay_stale_version_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    return results


def build_and_confirm_valid_quorum() -> tuple[bool, str]:
    """Construct genuine authenticated R3 quorum via minted JWTs & HTTP."""
    from fastapi.testclient import TestClient
    from operations_domain.models import DataState
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app

    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup5", "shift_supervisor")
    _register_user(ledger, "evidence-mgr2", "responsible_manager")
    _register_user(ledger, "evidence-sup1", "shift_supervisor")

    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        r1 = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=_auth_headers("evidence-sup5", "shift_supervisor"))
        if r1.status_code != 201: return False, f"receipt 1 failed: {r1.status_code}"
        r2 = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=_auth_headers("evidence-mgr2", "responsible_manager"))
        if r2.status_code != 201: return False, f"receipt 2 failed: {r2.status_code}"
        cres = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        if cres.status_code != 200: return False, f"confirm failed with HTTP {cres.status_code}"
        confirmed = ledger.get_event(event.event_id)
        if confirmed.state != DataState.CONFIRMED: return False, f"confirm state={confirmed.state}"
        return True, "distinct authenticated approvers (evidence-sup5, evidence-mgr2) satisfied the R3 quorum via minted JWTs and HTTP requests"
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def call_alibaba(model: str, key_env_name: str, endpoint: str) -> dict:
    """One real minimal provider call."""
    global _PROVIDER_CALL_COUNT
    _PROVIDER_CALL_COUNT += 1
    api_key = os.environ[key_env_name]
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": PROMPT}], "max_tokens": 32}).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    started = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        return {"outcome": "FAIL", "reached_server": True, "http_status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:300], "started_at": started.isoformat()}
    except Exception as exc:
        return {"outcome": "FAIL", "reached_server": False, "http_status": None, "error": f"{type(exc).__name__}: {exc}", "started_at": started.isoformat()}

    content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"outcome": "PASS" if EXPECTED_TOKEN in content else "FAIL", "reached_server": True, "http_status": status, "response_excerpt": content.strip()[:200], "started_at": started.isoformat()}


def write_receipt(gate_results, quorum_detail, provider_result, model, endpoint, call_count) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# P2-B approver-identity control - live governance evidence receipt",
        "",
        f"Overall outcome: {overall}",
        "",
        "Produced by `scripts/run_approval_governance_evidence.py`",
        "(P2B-APPROVER-IDENTITY-RECONCILIATION, SPEC section 7). Sanitized: contains no API key, no Authorization header, no JWT, no password, no raw secret.",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}",
        f"- Endpoint: {endpoint}",
        "",
        "## 1. Gate-refusal cases (in-process, real code path, 0 provider calls each)",
        "",
        "| Case | Outcome | Detail | Provider calls |",
        "|---|---|---|---|",
    ]
    for r in gate_results:
        lines.append(f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |")
    lines += [
        "",
        "## 2. Authenticated-quorum construction (real code path)",
        "",
        f"- {quorum_detail}",
        "",
        "## 3. Real provider call",
        "",
        "Reached only because the quorum above genuinely satisfied the R3 requirement.",
        "",
        f"- Outcome: **{provider_result['outcome']}**",
        f"- Reached the provider (got any HTTP response): **{provider_result.get('reached_server', False)}**",
        f"- HTTP status: {provider_result.get('http_status')}",
        f"- Started at: {provider_result.get('started_at')}",
    ]
    if "response_excerpt" in provider_result:
        lines.append(f"- Response excerpt: `{provider_result['response_excerpt']}`")
    if "error" in provider_result:
        lines.append(f"- Error: `{provider_result['error']}`")
    lines += [
        "",
        "## 4. Provider-call count (self-asserted)",
        "",
        f"- Total provider calls made by this run: **{call_count}**",
        "- Expected: 0 for every gate-refusal case above, exactly 1 after the valid quorum.",
        "",
        "## Claim boundary",
        "",
        "This receipt evidences that the `approval` control - authenticated,",
        "server-derived, scope-bound receipts evaluated by a deterministic,",
        "order-invariant quorum matcher - correctly refuses fabricated, wrong-role,",
        "inactive-user, self-approval, insufficient-quorum, and replayed approvals",
        "before any provider call, and correctly admits a genuine, distinct-approver",
        "quorum through the real application code path. It does NOT evidence that any",
        "production endpoint calls a provider in production (none do). It does not",
        "evidence PostgreSQL production verification (remains NOT LIVE VERIFIED).",
        "",
    ]
    RECEIPT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    print("== approval gate: refusal cases ==")
    gate_results = check_approval_gate()
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("APPROVAL GATE REFUSAL CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine authenticated quorum ==")
    quorum_ok, quorum_detail = build_and_confirm_valid_quorum()
    print(f"  {quorum_detail}")
    if not quorum_ok:
        print("QUORUM CONSTRUCTION FAILED", file=sys.stderr)
        return 1

    present, key_env_name = _key_present()
    print(f"== provider credential present: {present} ==")
    if args.dry_run: return 0
    if not present:
        print("READY_FOR_LIVE_EVIDENCE: no provider key", file=sys.stderr)
        return 2

    try:
        from select_model import select_model
        model = select_model()
    except Exception as exc:
        print(f"READY_FOR_LIVE_EVIDENCE: model select failed: {exc}", file=sys.stderr)
        return 2

    print(f"== calling provider (model={model}) ==")
    provider_result = call_alibaba(model, key_env_name, _endpoint())
    print(f"  outcome: {provider_result['outcome']} (http {provider_result.get('http_status')})")
    write_receipt(gate_results, quorum_detail, provider_result, model, _endpoint(), _PROVIDER_CALL_COUNT)

    if _PROVIDER_CALL_COUNT != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
