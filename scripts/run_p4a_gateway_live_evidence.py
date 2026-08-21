#!/usr/bin/env python3
"""P4-A live governance evidence (SPEC R13).

Protocol, in order:

1. preflight - report only whether a credential exists and which env var name;
2. zero-call refusal cases - NO_AI, no evidence, P4-A1 INTERNAL without
   minimization, RESTRICTED external, budget exceeded, kill switch. Each must
   reach the provider zero times;
3. only if every refusal passed, reserve exactly one call and send one PUBLIC
   canary through the real gateway to the real endpoint;
4. write a sanitized receipt.

Any failure is ``LIVE_EVIDENCE_BLOCKED``. There is no retry and no replacement
call: a second attempt would require an amended Work Order.

The provider adapter here is EVIDENCE-ONLY. It is not a production adapter and
does not close P4-B.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "ai-gateway" / "src"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "cvf-runtime" / "src"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "ai-providers"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p4a_gateway_live_evidence_support import (  # noqa: E402
    CANARY_CONTEXT,
    CANARY_PROMPT,
    PROVIDER_ID,
    CallBudget,
    LiveEvidenceError,
    build_canary_request,
    endpoint,
    extract_json_object,
    key_presence,
    run_refusals,
    safe_origin,
    sanitize,
    scan_for_secrets,
    sha256_hex,
)
from ai_gateway.models import ProviderRequest, ProviderResult  # noqa: E402
from ai_gateway.registry import ProviderRegistry  # noqa: E402
from ai_gateway.service import AIGateway  # noqa: E402
from ai_gateway.usage import UsageLedger  # noqa: E402

RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md"


class _CountingProvider:
    """Base adapter that refuses to be called; refusal cases must never reach it."""

    provider_id = PROVIDER_ID

    def __init__(self, budget: CallBudget) -> None:
        self._budget = budget
        self.calls = 0

    async def health_check(self) -> dict:
        raise LiveEvidenceError("health_check is not authorized in this tranche")

    async def cancel_request(self, request_id: str) -> None:
        return None


class _RefusalGuardProvider(_CountingProvider):
    """Used for refusal cases: any dispatch here is a governance failure."""

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        self.calls += 1
        raise LiveEvidenceError("a refusal case reached the provider")


class _LiveDashScopeProvider(_CountingProvider):
    """Evidence-only adapter. Makes exactly one HTTPS POST. Not production."""

    def __init__(self, budget: CallBudget, key_env_name: str) -> None:
        super().__init__(budget)
        self._key_env_name = key_env_name
        self.http_status: int | None = None
        self.reached_server = False
        self.error_note = ""

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        return await asyncio.to_thread(self._post, request)

    def _post(self, request: ProviderRequest) -> ProviderResult:
        url = endpoint()
        body = json.dumps(
            {
                "model": request.model_id,
                "messages": [{"role": "user", "content": CANARY_PROMPT}],
                "max_tokens": request.max_output_tokens,
                "temperature": 0,
            }
        ).encode("utf-8")
        # Read the key at the last moment; never store or echo it.
        api_key = os.environ[self._key_env_name]
        http_request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        self._budget.record_physical()
        self.calls += 1
        try:
            with urllib.request.urlopen(http_request, timeout=request.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                self.http_status = response.status
                self.reached_server = True
        except urllib.error.HTTPError as exc:
            self.http_status = exc.code
            self.reached_server = True
            self.error_note = sanitize(f"HTTPError {exc.code}")
            raise LiveEvidenceError(self.error_note) from None
        except Exception as exc:
            self.error_note = sanitize(f"{type(exc).__name__}")
            raise LiveEvidenceError(self.error_note) from None

        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = payload.get("usage") or {}
        return ProviderResult(
            output=extract_json_object(content),
            provider_id=self.provider_id,
            model_id=request.model_id,
            usage={
                "total_tokens": int(usage.get("total_tokens", 0)),
                "cost_usd_millis": 0,
            },
        )


def write_receipt(payload: dict) -> tuple[str, list[str]]:
    """Write the sanitized receipt and return (sha256, secret-scan hits)."""
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    hits = scan_for_secrets(body)
    document = f"""# P4-A AI Gateway - Live Evidence Receipt

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Generated: `{payload["generated_at"]}`
- Disposition: `{payload["disposition"]}`
- Physical provider calls this run: `{payload["physical_calls"]}`

Sanitized machine-readable record. Contains digests, safe identifiers, and gate
outcomes only - no prompt text, context body, output body, endpoint path,
authorization header, or credential.

```json
{body}
```

## Claim boundary

This receipt proves that on the recorded run the three CVF gates preceded a
single provider dispatch through `AIGateway.execute`, and that each mandated
refusal case reached the provider zero times. It does not prove an application
API uses the gateway, durable usage accounting, a production provider adapter,
RAG, deployment, or production readiness.
"""
    RECEIPT_PATH.write_text(document, encoding="utf-8")
    return sha256_hex(document), hits


def main() -> int:
    parser = argparse.ArgumentParser(description="P4-A live governance evidence")
    parser.add_argument(
        "--refusals-only",
        action="store_true",
        help="run the zero-call refusal proofs and stop before any provider call",
    )
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).isoformat()
    budget = CallBudget(limit=1)

    present, key_env_name = key_presence()
    print(f"== preflight ==\n  credential present: {present}\n  env var: {key_env_name or 'NONE'}")

    try:
        from alibaba.select_model import select_model  # noqa: PLC0415

        model_id = select_model()
    except Exception as exc:
        print(f"LIVE_EVIDENCE_BLOCKED: no eligible model ({type(exc).__name__})", file=sys.stderr)
        return 1
    print(f"  selected model: {model_id}")

    print("== refusal cases (must be zero-call) ==")
    refusals = run_refusals(model_id, budget, _RefusalGuardProvider)
    for row in refusals:
        print(
            f"  {row['case']}: reason={row['reason_code'] or 'NONE'} "
            f"attempts={row['provider_attempts']} adapter_calls={row['adapter_calls']}"
        )
    refusals_ok = all(
        not row["accepted"]
        and row["provider_attempts"] == 0
        and row["adapter_calls"] == 0
        and row["gateway_attempts"] == 0
        for row in refusals
    )
    if not refusals_ok:
        print("LIVE_EVIDENCE_BLOCKED: a refusal case was not zero-call", file=sys.stderr)
        return 1
    print(f"  all {len(refusals)} refusal cases passed with zero provider attempts")

    if args.refusals_only:
        print("refusals-only mode: stopping before any provider call")
        return 0

    if not present or key_env_name is None:
        print("LIVE_EVIDENCE_BLOCKED: no credential in environment", file=sys.stderr)
        return 1

    print("== single PUBLIC canary through the gateway ==")
    budget.reserve()
    provider = _LiveDashScopeProvider(budget, key_env_name)
    registry = ProviderRegistry()
    registry.register(provider, (model_id,))
    origin = safe_origin(endpoint())
    gateway = AIGateway(registry, UsageLedger(), endpoint_origin=origin)

    result = asyncio.run(gateway.execute(build_canary_request(model_id)))

    payload = {
        "generated_at": generated_at,
        "tranche": "P4A-AI-GATEWAY-2026-08-20",
        "provider_id": PROVIDER_ID,
        "model_id": model_id,
        "endpoint_origin": origin,
        "credential_env_var": key_env_name,
        "refusal_cases": refusals,
        "physical_calls": budget.physical,
        "adapter_calls": provider.calls,
        "gateway_attempts": gateway.physical_attempts,
        "http_status": provider.http_status,
        "reached_server": provider.reached_server,
        "accepted": result.accepted,
        "receipt": json.loads(result.receipt.model_dump_json()),
        "error_note": provider.error_note,
        "disposition": "LIVE_EVIDENCE_PASS" if result.accepted else "LIVE_EVIDENCE_BLOCKED",
    }

    receipt_hash, hits = write_receipt(payload)
    print(f"  http_status: {provider.http_status}")
    print(f"  physical calls: {budget.physical}")
    print(f"  accepted: {result.accepted}  reason: {result.receipt.reason_code or 'NONE'}")
    print(f"  receipt sha256: {receipt_hash}")
    print(f"  secret scan hits: {hits or 'NONE'}")

    if hits:
        print("LIVE_EVIDENCE_BLOCKED: secret-like content in receipt", file=sys.stderr)
        return 1
    if budget.physical != 1:
        print(
            f"LIVE_EVIDENCE_BLOCKED: expected exactly one physical call, got {budget.physical}",
            file=sys.stderr,
        )
        return 1
    if not result.accepted:
        print("LIVE_EVIDENCE_BLOCKED: canary was not accepted", file=sys.stderr)
        return 1

    print("LIVE_EVIDENCE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
