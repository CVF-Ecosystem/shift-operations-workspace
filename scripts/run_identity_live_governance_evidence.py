#!/usr/bin/env python3
"""Live governance evidence for the `identity` CVF control.

P2B-AUTHENTICATION-REPAIR, SPEC SS1.5/SS7. AGENTS.md's Mandatory Governance
Proof rule: any claim that CVF governs a control - here `identity` - must be
backed by a REAL provider API call, never a mock or a TestClient-only probe.

Why this script exists in this shape
------------------------------------
JWT authentication has no intrinsic technical dependency on an LLM provider,
so a bare provider canary (does the Alibaba key work at all?) would prove
nothing about this project's identity gate. Conversely, an in-process test of
the identity gate alone is not live evidence. This script therefore binds the
two: the real identity gate DECIDES whether the real provider call happens.

  1. Exercise the real identity path in-process:
       - a validly-signed token for a permitted role must resolve to a
         Principal and be authorized for a governed action;
       - a forged/invalid token must be refused.
  2. ONLY if step 1's valid case succeeds does the script make exactly one
     real, minimal Alibaba API call.
  3. Record a sanitized receipt.

So a recorded successful receipt is only producible when the identity gate
actually admitted a legitimate principal and actually refused a forged one.

Secret handling (SPEC SI-3)
---------------------------
The Alibaba key is read from the environment ONLY. It is never printed,
logged, written to the receipt, or passed on a command line. Only its
presence (a boolean) is ever reported. The JWT secret is likewise never
emitted.

Usage:
    python scripts/run_identity_live_governance_evidence.py
    python scripts/run_identity_live_governance_evidence.py --dry-run

Exit codes: 0 = evidence PASS, 1 = failure (recorded, not reframed as pass),
2 = prerequisites absent (READY_FOR_LIVE_EVIDENCE, not a failure).
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

REPO_ROOT = Path(__file__).resolve().parents[1]
for _rel in (
    "apps/workspace-api/src",
    "packages/cvf-runtime/src",
    "packages/operations-ledger/src",
    "packages/operations-domain/src",
    "packages/ai-providers/alibaba",
):
    sys.path.insert(0, str(REPO_ROOT / _rel))

RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md"
KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_IDENTITY_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_IDENTITY_EVIDENCE_OK"


def _key_present() -> tuple[bool, str | None]:
    """Return (present, env-var-name). Never returns the value itself."""
    for name in KEY_ENV_NAMES:
        if os.environ.get(name, "").strip():
            return True, name
    return False, None


def _endpoint() -> str:
    """Resolve the regional OpenAI-compatible endpoint from non-secret config."""
    base_url = next(
        (
            os.environ[name].strip()
            for name in BASE_URL_ENV_NAMES
            if os.environ.get(name, "").strip()
        ),
        DEFAULT_BASE_URL,
    )
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def check_identity_gate() -> list[dict]:
    """Exercise the real identity gate. Returns per-case results.

    Uses the same functions the running API uses - create_access_token,
    decode_access_token, and the permission check governed actions run -
    not reimplementations.
    """
    from cvf_runtime.identity import Principal
    from cvf_runtime.permission import require_action

    from workspace_api.auth.tokens import TokenError, create_access_token, decode_access_token

    results: list[dict] = []

    # Case 1: a validly-signed token for a permitted role must be admitted.
    principal = Principal(user_id="evidence-operator", role="operator")
    token = create_access_token(principal)
    decoded = decode_access_token(token)
    require_action(decoded, "shift.close")
    results.append(
        {
            "case": "valid_token_admitted",
            "outcome": "PASS",
            "detail": (
                f"token decoded to user_id={decoded.user_id} role={decoded.role}; "
                f"require_action('shift.close') allowed"
            ),
        }
    )
    if decoded.user_id != principal.user_id or decoded.role != principal.role:
        raise AssertionError("decoded principal does not match the signed principal")

    # Case 2: a forged token must be refused.
    forged = token[:-4] + ("abcd" if not token.endswith("abcd") else "efgh")
    try:
        decode_access_token(forged)
    except TokenError as exc:
        results.append(
            {
                "case": "forged_token_refused",
                "outcome": "PASS",
                "detail": f"tampered signature rejected: {exc}",
            }
        )
    else:
        results.append(
            {
                "case": "forged_token_refused",
                "outcome": "FAIL",
                "detail": "a tampered token was accepted",
            }
        )

    return results


def call_alibaba(model: str, key_env_name: str, endpoint: str) -> dict:
    """One real, minimal provider call. Returns a sanitized result dict."""
    api_key = os.environ[key_env_name]
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 32,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        # An HTTPError means the request DID reach the provider and got a
        # real (if unwelcome) HTTP response - reached_server=True. Body may
        # carry a provider error message; it must not carry the key.
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return {
            "outcome": "FAIL",
            "reached_server": True,
            "http_status": exc.code,
            "error": detail,
            "started_at": started.isoformat(),
        }
    except Exception as exc:  # noqa: BLE001 - DNS/connection/timeout
        # No HTTP response of any kind was received - the call never
        # reached the provider at all. Independent review (2026-07-22):
        # the receipt previously claimed "a real provider call was made"
        # even in this case, which is false - nothing was exchanged with
        # Alibaba. reached_server=False lets write_receipt say so honestly.
        return {
            "outcome": "FAIL",
            "reached_server": False,
            "http_status": None,
            "error": f"{type(exc).__name__}: {exc}",
            "started_at": started.isoformat(),
        }

    content = ""
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = ""

    return {
        "outcome": "PASS" if EXPECTED_TOKEN in content else "FAIL",
        "reached_server": True,
        "http_status": status,
        "response_excerpt": content.strip()[:200],
        "started_at": started.isoformat(),
    }


def write_receipt(
    identity_results: list[dict], provider_result: dict, model: str, endpoint: str
) -> None:
    lines = [
        "# P2-B identity control - live governance evidence receipt",
        "",
        "Produced by `scripts/run_identity_live_governance_evidence.py`",
        "(P2B-AUTHENTICATION-REPAIR, SPEC SS7). Sanitized: contains no API key,",
        "no Authorization header, and no JWT secret.",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}",
        f"- Endpoint: {endpoint}",
        "",
        "## 1. Identity gate (in-process, real code path)",
        "",
        "| Case | Outcome | Detail |",
        "|---|---|---|",
    ]
    for result in identity_results:
        lines.append(f"| {result['case']} | {result['outcome']} | {result['detail']} |")

    reached_server = provider_result.get("reached_server", False)
    lines += [
        "",
        "## 2. Real provider call",
        "",
        "Reached only because case `valid_token_admitted` passed - the identity",
        "gate is what authorized this call.",
        "",
        f"- Outcome: **{provider_result['outcome']}**",
        f"- Reached the provider (got any HTTP response): **{reached_server}**",
        f"- HTTP status: {provider_result.get('http_status')}",
        f"- Started at: {provider_result.get('started_at')}",
    ]
    if "response_excerpt" in provider_result:
        lines.append(f"- Response excerpt: `{provider_result['response_excerpt']}`")
    if "error" in provider_result:
        lines.append(f"- Error: `{provider_result['error']}`")

    # Independent review (2026-07-22): this section previously stated flatly
    # that "a real provider call was made", even when the call never reached
    # the provider at all (e.g. a connection reset) - a failure reframed as
    # evidence, exactly what WORK_ORDER Section 5.4 forbids. The wording now
    # depends on what actually happened.
    if provider_result["outcome"] == "PASS":
        call_claim = (
            "a real (non-mock) provider call was made and returned the "
            "expected response under that gate"
        )
    elif reached_server:
        call_claim = (
            "a real (non-mock) network round trip reached the provider "
            "under that gate, but the provider returned an error "
            "(see HTTP status/error above) - this is NOT a passing result"
        )
    else:
        call_claim = (
            "an attempt was made to call the provider under that gate, but "
            "it did NOT reach the provider at all (see error above) - no "
            "call actually landed, and this is NOT evidence of a working "
            "provider integration"
        )

    lines += [
        "",
        "## Claim boundary",
        "",
        "This receipt evidences that the `identity` control admits a validly",
        f"signed principal and refuses a forged token, and that {call_claim}.",
        "It does NOT evidence approval quorum (High Finding #4), PostgreSQL",
        "production verification, or any AI-gateway capability - all",
        "explicitly out of scope for this tranche.",
        "",
    ]
    RECEIPT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run the identity checks and report readiness without calling the provider",
    )
    args = parser.parse_args()

    print("== identity gate ==")
    identity_results = check_identity_gate()
    for result in identity_results:
        print(f"  {result['case']}: {result['outcome']} - {result['detail']}")
    if any(r["outcome"] != "PASS" for r in identity_results):
        print("IDENTITY GATE FAILED - not proceeding to the provider call", file=sys.stderr)
        return 1

    present, key_env_name = _key_present()
    print(f"== provider credential present: {present} ==")

    if args.dry_run:
        print("DRY RUN - identity gate verified, provider not called")
        return 0

    if not present:
        print(
            "READY_FOR_LIVE_EVIDENCE: identity gate passes, but no "
            f"{' / '.join(KEY_ENV_NAMES)} is set in the environment. "
            "Live evidence is NOT complete; do not record REVIEW_PASS/FREEZE/DONE.",
            file=sys.stderr,
        )
        return 2

    try:
        from select_model import CatalogError, select_model
    except ImportError as exc:
        print(
            "READY_FOR_LIVE_EVIDENCE: the Alibaba provider configuration "
            f"(packages/ai-providers/alibaba) is not importable: {exc}",
            file=sys.stderr,
        )
        return 2

    try:
        model = select_model()
    except CatalogError as exc:
        print(f"READY_FOR_LIVE_EVIDENCE: no eligible Alibaba model - {exc}", file=sys.stderr)
        return 2

    print(f"== calling provider (model={model}) ==")
    endpoint = _endpoint()
    provider_result = call_alibaba(model, key_env_name, endpoint)
    print(f"  outcome: {provider_result['outcome']} (http {provider_result.get('http_status')})")

    write_receipt(identity_results, provider_result, model, endpoint)
    print(f"receipt written: {RECEIPT_PATH.relative_to(REPO_ROOT)}")

    if provider_result["outcome"] != "PASS":
        print("LIVE EVIDENCE FAILED - recorded as failure, not as proof", file=sys.stderr)
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
