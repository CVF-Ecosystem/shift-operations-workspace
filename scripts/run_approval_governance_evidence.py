#!/usr/bin/env python3
"""Live governance evidence for the `approval` CVF control.
P2B-APPROVER-IDENTITY-RECONCILIATION (SPEC section 7 & 10).

CVF-FILE-SPLIT-GUARD-HARDENING split the gate-refusal probes, quorum
construction and receipt rendering into
`_approval_governance_evidence_support.py` to keep this entrypoint under the
hard line limit; the real provider call and CLI flow stay here unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
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

from _approval_governance_evidence_support import (  # noqa: E402
    build_and_confirm_valid_quorum,
    check_approval_gate,
    write_receipt,
)

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
