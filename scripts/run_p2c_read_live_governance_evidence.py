#!/usr/bin/env python3
"""Live governance evidence for the P2C read slice (SPEC R16, Amendment 1).
Self-contained (no separate support module authorized for C3a): refusal
probes over the real FastAPI/JWT route chain for anonymous/malformed-token
reads (observed zero provider calls each), then a genuine valid-JWT read of
shift/events/open-work, followed by exactly one real provider call. Nothing
here ever returns/prints/writes the exact key, a bearer/JWT value, or a
URL's userinfo/query/fragment - sanitized before leaving ``call_provider``.
"""

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
for _rel in ("apps/workspace-api/src", "packages/cvf-runtime/src", "packages/operations-ledger/src",
             "packages/operations-domain/src", "packages/ai-providers/alibaba", "scripts"):
    sys.path.insert(0, str(REPO_ROOT / _rel))

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_P2C_READ_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_P2C_READ_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2C_READ_LIVE_EVIDENCE_RECEIPT.md"

_BEARER_RE = re.compile(r"Bearer\s+\S+", re.IGNORECASE)
_JWT_RE = re.compile(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")


class ProviderCallCounter:
    """Fresh per invocation (SPEC R15-B parity) - never a module global."""

    def __init__(self) -> None:
        self.count = 0

    def record(self) -> None:
        self.count += 1

def sanitize_secret_text(text: str | None, *, api_key: str | None = None) -> str:
    if not text:
        return text or ""
    if api_key:
        text = text.replace(api_key, "<redacted-key>")
    text = _BEARER_RE.sub("Bearer <redacted>", text)
    return _JWT_RE.sub("<redacted-jwt>", text)

def safe_endpoint_description(endpoint: str) -> str:
    parts = urlsplit(endpoint)
    return f"{parts.scheme}://{parts.hostname or '<unknown-host>'}"

def _clean_endpoint(endpoint: str) -> tuple[str, list[str]]:
    parts = urlsplit(endpoint)
    secrets = [v for v in (parts.username, parts.password, parts.query, parts.fragment) if v]
    netloc = f"{parts.hostname or ''}:{parts.port}" if parts.port else (parts.hostname or "")
    return urlunsplit((parts.scheme, netloc, parts.path, "", "")), secrets


def call_provider(*, model: str, api_key: str, endpoint: str, prompt: str,
                   expected_token: str, counter: ProviderCallCounter) -> dict:
    counter.record()
    clean_endpoint, endpoint_secrets = _clean_endpoint(endpoint)

    def _sanitize(text: str) -> str:
        text = sanitize_secret_text(text, api_key=api_key)
        for secret in endpoint_secrets:
            text = text.replace(secret, "<redacted-endpoint-credential>")
        return text

    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 32}).encode("utf-8")
    started = datetime.now(timezone.utc)
    try:
        req = urllib.request.Request(
            clean_endpoint, data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:300]
        return {"outcome": "FAIL", "reached_server": True, "http_status": exc.code,
                "error": _sanitize(error_body), "started_at": started.isoformat()}
    except Exception as exc:  # noqa: BLE001 - construction or transport failure, sanitized alike
        return {"outcome": "FAIL", "reached_server": False, "http_status": None,
                "error": _sanitize(f"{type(exc).__name__}: {exc}"), "started_at": started.isoformat()}

    content = _sanitize(payload.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return {"outcome": "PASS" if expected_token in content else "FAIL",
            "reached_server": True, "http_status": status,
            "response_excerpt": content.strip()[:200], "started_at": started.isoformat()}


def _new_ledger_and_shift(prefix: str):
    from operations_domain.models import CustomerRequest, Incident, OperationalEvent, RiskClass, Shift, Task
    from workspace_api.infrastructure.repository import InMemoryLedger
    now = datetime.now(timezone.utc)
    shift = Shift(name=f"{prefix} shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger = InMemoryLedger()
    ledger.create_shift(shift)
    ledger.add_event(OperationalEvent(shift_id=shift.shift_id, event_type="equipment_downtime", title="E1", risk_class=RiskClass.R1))
    ledger.add_task(Task(shift_id=shift.shift_id, title="T1", risk_class=RiskClass.R1))
    ledger.add_customer_request(CustomerRequest(customer_id="c1", shift_id=shift.shift_id, summary="R1"))
    ledger.add_incident(Incident(shift_id=shift.shift_id, summary="I1", risk_class=RiskClass.R2))
    return ledger, shift


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


def check_p2c_read_refusal_gate(counter: ProviderCallCounter) -> list[dict]:
    """Refusal cases: each records the OBSERVED provider-call delta on the
    shared counter - none of these code paths can reach call_provider."""
    results: list[dict] = []
    ledger, shift = _new_ledger_and_shift("refusal")

    def _case(name, run, expected_status):
        before = counter.count
        res = _with_ledger(ledger, run)
        outcome = "PASS" if res.status_code == expected_status else "FAIL"
        results.append({"case": name, "outcome": outcome,
                         "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    _case("anonymous_shifts_read_rejected", lambda c: c.get("/shifts"), 401)
    _case("malformed_token_shifts_read_rejected",
          lambda c: c.get("/shifts", headers={"Authorization": "Bearer not-a-jwt"}), 401)
    _case("anonymous_events_read_rejected", lambda c: c.get("/events", params={"shift_id": str(shift.shift_id)}), 401)
    _case("anonymous_open_work_read_rejected", lambda c: c.get(f"/shifts/{shift.shift_id}/open-work"), 401)
    return results


def build_admitted_reads_genuine() -> tuple[bool, str]:
    """Construct a genuine valid-JWT read of shift, events and open-work via
    a minted JWT and real HTTP requests (SPEC R16)."""
    ledger, shift = _new_ledger_and_shift("admitted")
    headers = _auth_headers("p2c-ev-viewer", "viewer")

    def _run(client):
        shifts_res = client.get("/shifts", headers=headers)
        if shifts_res.status_code != 200:
            return False, f"shifts read failed: {shifts_res.status_code}"
        events_res = client.get("/events", params={"shift_id": str(shift.shift_id)}, headers=headers)
        if events_res.status_code != 200 or len(events_res.json()) != 1:
            return False, f"events read failed: {events_res.status_code}"
        open_work_res = client.get(f"/shifts/{shift.shift_id}/open-work", headers=headers)
        if open_work_res.status_code != 200:
            return False, f"open-work read failed: {open_work_res.status_code}"
        body = open_work_res.json()
        if not (len(body["tasks"]) == 1 and len(body["customer_requests"]) == 1 and len(body["incidents"]) == 1):
            return False, "open-work body did not contain the expected one-of-each open items"
        return True, (
            "valid JWT (p2c-ev-viewer) admitted GET /shifts, GET /events and "
            "GET /shifts/{shift_id}/open-work via minted token and real HTTP requests"
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


_CLAIM_BOUNDARY = (
    "This receipt evidences that the P2C read surfaces' identity-only JWT gate "
    "correctly refuses anonymous and malformed-token reads before any provider "
    "call, and correctly admits a genuine valid-JWT read of shift, events and "
    "open-work through the real HTTP route chain. It does NOT evidence that "
    "any production read endpoint calls a provider in production (none do), "
    "does not evidence per-shift assignment or data_scope enforcement, and "
    "does not evidence PostgreSQL production readiness."
)


def render_receipt(path: Path, *, gate_results: list[dict], admitted_detail: str,
                    provider_result: dict, model: str, safe_endpoint: str, call_count: int) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# P2-C read slice - live governance evidence receipt", "",
        f"Overall outcome: {overall}", "",
        "Produced by `scripts/run_p2c_read_live_governance_evidence.py` "
        "(P2C-OPERATIONS-CONSOLE-READ-SLICE Amendment 1, SPEC R16). Sanitized: "
        "no API key, Authorization header, JWT, raw secret, or URL userinfo/query/fragment.",
        "", f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}", f"- Endpoint (host only): {safe_endpoint}", "",
        "## 1. Refusal cases (real HTTP route chain, observed provider-call delta)", "",
        "| Case | Outcome | Detail | Provider calls |", "|---|---|---|---|",
        *(f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |" for r in gate_results),
        "", "## 2. Genuine admitted reads (real HTTP route chain)", "", f"- {admitted_detail}",
        "", "## 3. Real provider call", "",
        "Reached only because the reads above genuinely admitted a valid JWT.", "",
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
        "", "## 4. Provider-call count (observed, reset per invocation)", "",
        f"- Total provider calls made by this run: **{call_count}**",
        "- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted reads.",
        "", "## Claim boundary", "", _CLAIM_BOUNDARY, "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="P2C read slice live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()
    counter = ProviderCallCounter()

    print("== P2C read refusal gate: anonymous/malformed-token cases ==")
    gate_results = check_p2c_read_refusal_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("P2C READ REFUSAL GATE CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing genuine admitted reads (valid JWT) ==")
    ok, detail = build_admitted_reads_genuine()
    print(f"  {detail}")
    if not ok:
        print("GENUINE P2C READ CONSTRUCTION FAILED", file=sys.stderr)
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
    provider_result = call_provider(model=model, api_key=os.environ[key_env_name], endpoint=endpoint,
                                     prompt=PROMPT, expected_token=EXPECTED_TOKEN, counter=counter)
    print(f"  outcome: {provider_result['outcome']} (http {provider_result.get('http_status')})")
    render_receipt(RECEIPT_PATH, gate_results=gate_results, admitted_detail=detail,
                    provider_result=provider_result, model=model, safe_endpoint=safe_endpoint,
                    call_count=counter.count)

    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
