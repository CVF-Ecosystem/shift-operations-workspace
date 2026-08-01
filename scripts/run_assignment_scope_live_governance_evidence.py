#!/usr/bin/env python3
"""Live governance evidence for route-wide operational assignment enforcement
(P2C-MUTATION-FULL-UI-C3A2, WO section 3.6). In-process refusal probes over
the real FastAPI/JWT route chain for a representative set of assignment-
scope-refused operational routes (zero provider calls each), then one genuine
ACTIVE-assignment-admitted mutation with an exact-field-matched audit, then
exactly one real, non-mocked provider call. Self-contained (no support
module): the C3a2 ceiling authorizes exactly this one new script path."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIRS = ("apps/workspace-api/src", "packages/cvf-runtime/src", "packages/operations-ledger/src",
             "packages/operations-domain/src", "packages/ai-providers/alibaba", "scripts")
for _rel in _SRC_DIRS:
    sys.path.insert(0, str(REPO_ROOT / _rel))

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_ASSIGNMENT_SCOPE_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_ASSIGNMENT_SCOPE_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2C_C3A2_ASSIGNMENT_SCOPE_LIVE_EVIDENCE_RECEIPT.md"
_BEARER_RE = re.compile(r"Bearer\s+\S+", re.IGNORECASE)
_JWT_RE = re.compile(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")

class ProviderCallCounter:
    def __init__(self) -> None:
        self.count = 0

    def record(self) -> None:
        self.count += 1

def sanitize_secret_text(text: str | None, *, api_key: str | None = None) -> str:
    if not text:
        return text or ""
    if api_key:
        text = text.replace(api_key, "<redacted-key>")
    return _JWT_RE.sub("<redacted-jwt>", _BEARER_RE.sub("Bearer <redacted>", text))

def safe_endpoint_description(endpoint: str) -> str:
    parts = urlsplit(endpoint)
    return f"{parts.scheme}://{parts.hostname or '<unknown-host>'}"

def _clean_endpoint(endpoint: str) -> tuple[str, list[str]]:
    parts = urlsplit(endpoint)
    secrets = [v for v in (parts.username, parts.password, parts.query, parts.fragment) if v]
    netloc = parts.hostname or ""
    if parts.port:
        netloc = f"{netloc}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, "", "")), secrets

def call_provider(*, model, api_key, endpoint, prompt, expected_token, counter) -> dict:
    counter.record()
    clean_endpoint, endpoint_secrets = _clean_endpoint(endpoint)

    def _sanitize(text: str) -> str:
        text = sanitize_secret_text(text, api_key=api_key)
        for secret in endpoint_secrets:
            text = text.replace(secret, "<redacted-endpoint-credential>")
        return text

    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 32}).encode()
    started = datetime.now(timezone.utc)
    try:
        req = urllib.request.Request(
            clean_endpoint, data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:300]
        return {"outcome": "FAIL", "reached_server": True, "http_status": exc.code,
                "error": _sanitize(error_body), "started_at": started.isoformat()}
    except Exception as exc:  # noqa: BLE001 - construction/transport failure, sanitized alike
        return {"outcome": "FAIL", "reached_server": False, "http_status": None,
                "error": _sanitize(f"{type(exc).__name__}: {exc}"), "started_at": started.isoformat()}

    content = _sanitize(payload.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return {"outcome": "PASS" if expected_token in content else "FAIL", "reached_server": True,
            "http_status": status, "response_excerpt": content.strip()[:200], "started_at": started.isoformat()}

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

def _seed(ledger, user_id, role):
    import workspace_api.domain.models as domain_models
    ledger.add_user(domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role))

def _new_shift(prefix: str):
    from operations_domain.models import Shift
    now = datetime.now(timezone.utc)
    return Shift(name=f"{prefix} shift", starts_at=now, ends_at=now + timedelta(hours=8))

def _evidence_ledger_and_shift(prefix: str):
    from workspace_api.infrastructure.repository import InMemoryLedger
    ledger = InMemoryLedger()
    shift = _new_shift(prefix)
    ledger.create_shift(shift)
    _seed(ledger, "scope-ev-op", "operator")
    _seed(ledger, "scope-ev-sup", "shift_supervisor")
    return ledger, shift

_REFUSAL_CASES = (
    (
        "open_work_denied_without_active_assignment",
        lambda c, sid: c.get(f"/shifts/{sid}/open-work", headers=_auth_headers("scope-ev-op", "operator")),
        404,
    ),
    (
        "message_create_denied_without_active_assignment",
        lambda c, sid: c.post("/messages", json={"shift_id": str(sid), "text": "hi"},
                               headers=_auth_headers("scope-ev-op", "operator")),
        404,
    ),
    (
        "incident_acknowledge_denied_insufficient_role_before_assignment",
        lambda c, sid: c.post(f"/incidents/{sid}/acknowledge", json={},
                               headers=_auth_headers("scope-ev-op", "operator")),
        403,
    ),
)

def check_assignment_scope_refusal_gate(counter: ProviderCallCounter) -> list[dict]:
    """Refusal cases: each records the OBSERVED provider-call delta, never a
    hard-coded literal - none of these code paths can reach call_provider."""
    results: list[dict] = []
    for name, run, expected_status in _REFUSAL_CASES:
        ledger, shift = _evidence_ledger_and_shift(name)
        before = counter.count
        res = _with_ledger(ledger, lambda c, run=run, sid=shift.shift_id: run(c, sid))
        outcome = "PASS" if res.status_code == expected_status else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}",
                         "calls": counter.count - before})
    return results

def build_admitted_message_create_genuine() -> tuple[bool, str]:
    """POST /messages admits through the canonical assignment_scope guard and
    leaves exactly one exact-field-matched message.create audit."""
    ledger, shift = _evidence_ledger_and_shift("genuine")
    from workspace_api.domain.models import ShiftAssignment

    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="scope-ev-op", assigned_by="scope-ev-op"))
    headers = _auth_headers("scope-ev-op", "operator")

    def _run(client):
        res = client.post(
            "/messages", json={"shift_id": str(shift.shift_id), "text": "scope evidence"}, headers=headers
        )
        if res.status_code != 200:
            return False, f"message create admission failed: {res.status_code}"
        message_id = res.json()["message_id"]
        audits = ledger.audit_entries_for(message_id)
        if len(audits) != 1:
            return False, f"expected exactly one audit for the created message, found {len(audits)}"
        a = audits[0]
        expected = {"actor_id": "scope-ev-op", "actor_role": "operator", "action": "message.create",
                    "record_type": "Message", "record_id": message_id,
                    "control_chain": ["identity", "permission", "create", "audit"],
                    "before_state": None, "after_state": "RAW"}
        actual = {"actor_id": a.actor_id, "actor_role": a.actor_role, "action": a.action,
                  "record_type": a.record_type, "record_id": a.record_id, "control_chain": list(a.control_chain),
                  "before_state": a.before_state, "after_state": a.after_state}
        if actual != expected:
            return False, f"audit fields did not match exactly: expected {expected}, got {actual}"
        return True, (
            "valid operator JWT (scope-ev-op) with a durable ACTIVE assignment admitted POST /messages via a "
            "real HTTP request through the canonical assignment_scope guard, persisting exactly one "
            "exactly-field-matched message.create audit")
    return _with_ledger(ledger, _run)

def _key_present() -> tuple[bool, str | None]:
    for name in KEY_ENV_NAMES:
        if os.environ.get(name, "").strip():
            return True, name
    return False, None

def _endpoint() -> str:
    base_url = next((os.environ[n].strip() for n in BASE_URL_ENV_NAMES if os.environ.get(n, "").strip()),
                     DEFAULT_BASE_URL).rstrip("/")
    return base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"

def render_receipt(path, *, gate_results, admitted_detail, provider_result, model, safe_endpoint, call_count) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# P2C-C3A2 assignment-scope route enforcement - live governance evidence receipt", "",
        f"Overall outcome: {overall}", "",
        "Produced by `scripts/run_assignment_scope_live_governance_evidence.py` (P2C-MUTATION-FULL-UI-C3A2, WO "
        "section 3.6). Sanitized: no API key, Authorization header, JWT, raw secret, or URL userinfo/query/"
        "fragment.", "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}", f"- Endpoint (host only): {safe_endpoint}", "",
        "## 1. Refusal cases", "", "| Case | Outcome | Detail | Provider calls |", "|---|---|---|---|",
    ]
    lines += [f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |" for r in gate_results]
    lines += [
        "", "## 2. Genuine ACTIVE-assignment-admitted operation", "", f"- {admitted_detail}", "",
        "## 3. Real provider call", "",
        f"- Outcome: **{provider_result['outcome']}**",
        f"- Reached the provider: **{provider_result.get('reached_server', False)}**",
        f"- HTTP status: {provider_result.get('http_status')}", f"- Started at: {provider_result.get('started_at')}",
    ]
    if "response_excerpt" in provider_result:
        lines.append(f"- Response excerpt: `{provider_result['response_excerpt']}`")
    if "error" in provider_result:
        lines.append(f"- Error: `{provider_result['error']}`")
    lines += [
        "", "## 4. Provider-call count", "", f"- Total provider calls made by this run: **{call_count}**",
        "- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted operation.", "",
        "## Claim boundary", "",
        "Evidences that C3a2's route-wide assignment_scope guard correctly refuses unassigned/insufficient-role "
        "attempts on a representative sample of R6 routes before any provider call, and admits a genuine "
        "valid-operator-JWT ACTIVE-assignment-scoped POST /messages mutation with an exact-field-matched audit "
        "through the real HTTP route chain. Does NOT evidence exhaustive R6/R7 coverage (see "
        "tests/cvf/test_assignment_scope_*.py), production PostgreSQL, or frontend mutation.", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Assignment-scope route enforcement live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()
    counter = ProviderCallCounter()

    print("== assignment-scope refusal gate: refusal cases ==")
    gate_results = check_assignment_scope_refusal_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("ASSIGNMENT SCOPE REFUSAL GATE CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine ACTIVE-assignment-admitted operation ==")
    ok, detail = build_admitted_message_create_genuine()
    print(f"  {detail}")
    if not ok:
        print("GENUINE ADMITTED OPERATION CONSTRUCTION FAILED", file=sys.stderr)
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
        prompt=PROMPT, expected_token=EXPECTED_TOKEN, counter=counter)
    print(f"  outcome: {provider_result['outcome']} (http {provider_result.get('http_status')})")
    render_receipt(
        RECEIPT_PATH, gate_results=gate_results, admitted_detail=detail, provider_result=provider_result,
        model=model, safe_endpoint=safe_endpoint, call_count=counter.count)
    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
