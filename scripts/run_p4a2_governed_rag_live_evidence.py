#!/usr/bin/env python3
"""P4-A2 governed-RAG live governance evidence (SPEC R19/R20).

Protocol, in order: (1) preflight - report only whether a credential exists
and which env var name, never the value; (2) at least six representative
pre-gateway refusal cases, each proven to reach the provider zero times:
P4-A1 no-evidence short-circuit, a forged/mismatched positive result,
stale-index rejection, all-evidence injection omission, minimization-failure
rejection, and context-budget-exceeded rejection; (3) only if every refusal
case passed and a credential is present, reserve exactly one call and run
the FULL admitted application composition (``execute_governed_rag``, with
``placement=Placement.EXTERNAL`` bound per P4A2-REV-F3) against an isolated
synthetic ``PROJECT_KNOWLEDGE_LOCAL_V1`` fixture, through the real
``AIGateway.execute`` to the real Alibaba DashScope endpoint; (4) write one sanitized receipt.

Any failure is ``LIVE_EVIDENCE_BLOCKED``. There is no retry and no
replacement call: a second attempt would require an amended Work Order.
The provider adapter here is EVIDENCE-ONLY - not a production adapter and
does not close P4-A3/P4-B.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_SIBLING_PATHS = (
    "apps/workspace-api/src", "packages/cvf-runtime/src", "packages/operations-ledger/src",
    "packages/operations-domain/src", "packages/refinery-bridge/src", "packages/retrieval-contracts/src",
    "packages/governed-retrieval/src", "packages/ai-gateway/src", "packages/governed-rag/src",
    "packages/ai-providers",
)
for _p in (str(REPO_ROOT / s) for s in _SIBLING_PATHS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p4a2_governed_rag_live_evidence_support import (  # noqa: E402
    REFUSAL_CASES, CallBudget, LiveEvidenceError, build_synthetic_knowledge_root, endpoint,
    execution_metadata, extract_json_object, key_presence, p4a1_request_body, rag_request,
    run_refusals, safe_origin, sanitize, scan_for_secrets, seeded_workspace, sha256_hex,
)
from ai_gateway.models import Placement, ProviderRequest, ProviderResult  # noqa: E402
from ai_gateway.registry import ProviderRegistry  # noqa: E402
from ai_gateway.service import AIGateway  # noqa: E402
from ai_gateway.usage import UsageLedger  # noqa: E402
from workspace_api.application.governed_rag import execute_governed_rag  # noqa: E402

RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P4A2_GOVERNED_RAG_LIVE_EVIDENCE_RECEIPT.md"
ADMITTED_QUERY = "handover procedure"
TRANCHE = "P4A2-GOVERNED-RAG-2026-08-21"


class _CountingProvider:
    """Base adapter that refuses to be called; refusal cases must never
    reach it."""

    provider_id = "alibaba_dashscope_evidence_only"

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

    def _prompt(self, request: ProviderRequest) -> str:
        instructions = request.context.get("instruction_contract", {}).get("instructions", "")
        records = request.context.get("evidence_records", [])
        evidence_text = "\n".join(f"- citation_id={r['citation_id']}: {r['minimized_text']}" for r in records)
        return (
            f"{instructions}\n\nEvidence records:\n{evidence_text}\n\n"
            f"Respond with ONLY a compact JSON object matching this exact schema: "
            f'{{"status": "ANSWER"|"ABSTAIN", "claims": [{{"text": str, "citation_ids": [str]}}], '
            f'"abstention_reason": str}}. No prose, no code fence.'
        )

    def _post(self, request: ProviderRequest) -> ProviderResult:
        body = json.dumps({
            "model": request.model_id, "messages": [{"role": "user", "content": self._prompt(request)}],
            "max_tokens": request.max_output_tokens, "temperature": 0,
        }).encode("utf-8")
        api_key = os.environ[self._key_env_name]
        http_request = urllib.request.Request(
            endpoint(), data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST",
        )

        self._budget.record_physical()
        self.calls += 1
        try:
            with urllib.request.urlopen(http_request, timeout=request.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                self.http_status = response.status
                self.reached_server = True
        except urllib.error.HTTPError as exc:
            self.http_status, self.reached_server = exc.code, True
            self.error_note = sanitize(f"HTTPError {exc.code}")
            raise LiveEvidenceError(self.error_note) from None
        except Exception as exc:
            self.error_note = sanitize(f"{type(exc).__name__}")
            raise LiveEvidenceError(self.error_note) from None

        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = payload.get("usage") or {}
        return ProviderResult(
            output=extract_json_object(content), provider_id=self.provider_id, model_id=request.model_id,
            usage={"total_tokens": int(usage.get("total_tokens", 0)), "cost_usd_millis": 0},
        )


def write_receipt(payload: dict) -> tuple[str, list[str]]:
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    hits = scan_for_secrets(body)
    document = f"""# P4-A2 Governed RAG - Live Evidence Receipt

- Tranche: `{TRANCHE}`
- Generated: `{payload["generated_at"]}`
- Disposition: `{payload["disposition"]}`
- Physical provider calls this run: `{payload["physical_calls"]}`

Sanitized machine-readable record. Contains digests, safe identifiers, counts,
and outcome/reason codes only - no query text, evidence body, output body,
endpoint path, authorization header, or credential.

```json
{body}
```

## Claim boundary

This receipt proves that on the recorded run at least six representative
pre-gateway refusal cases (P4-A1 no-evidence, forged/mismatched positive
binding, stale index, all-evidence injection omission, minimization failure,
context-budget-exceeded) reached the provider zero times, and that the full
admitted application composition (`execute_governed_rag`, `placement=
Placement.EXTERNAL` bound per P4A2-REV-F3) made exactly one HTTPS POST
through the real `AIGateway.execute` against an isolated
synthetic `PROJECT_KNOWLEDGE_LOCAL_V1` fixture containing no operational or
customer data. It does not prove a public endpoint, general semantic
embeddings, operational-corpus RAG, durability, production provider
integration, deployment, or production readiness.
"""
    RECEIPT_PATH.write_text(document, encoding="utf-8")
    return sha256_hex(document), hits


def _base_payload(*, generated_at, provider, model_id, origin, key_env_name, refusals, gateway, budget) -> dict:
    """Fields common to both the blocked and the accepted receipt payload."""
    return {
        "generated_at": generated_at, "tranche": TRANCHE, "provider_id": provider.provider_id,
        "model_id": model_id, "endpoint_origin": origin, "credential_env_var": key_env_name,
        "refusal_cases": refusals, "physical_calls": budget.physical, "adapter_calls": provider.calls,
        "gateway_attempts": gateway.physical_attempts, "http_status": provider.http_status,
        "reached_server": provider.reached_server, "error_note": provider.error_note,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="P4-A2 governed-RAG live governance evidence")
    parser.add_argument("--refusals-only", action="store_true", help="stop before any provider call")
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

    with tempfile.TemporaryDirectory(prefix="p4a2_live_evidence_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)

        print(f"== refusal cases (must be zero-call; {len(REFUSAL_CASES)} mandated) ==")
        refusals = run_refusals(model_id, budget, _RefusalGuardProvider, tmp_dir)
        for row in refusals:
            print(f"  {row['case']}: reason={row['reason_code'] or 'NONE'} attempts={row['provider_attempts']} adapter_calls={row['adapter_calls']}")
        zero_call = lambda r: not r["accepted"] and r["provider_attempts"] == r["adapter_calls"] == r["gateway_attempts"] == 0  # noqa: E731
        if not all(zero_call(row) for row in refusals):
            print("LIVE_EVIDENCE_BLOCKED: a refusal case was not zero-call", file=sys.stderr)
            return 1
        print(f"  all {len(refusals)} refusal cases passed with zero provider attempts")

        if args.refusals_only:
            print("refusals-only mode: stopping before any provider call")
            return 0

        if not present or key_env_name is None:
            print("LIVE_EVIDENCE_BLOCKED: no credential in environment", file=sys.stderr)
            return 1

        print("== single admitted call through the full application composition ==")
        budget.reserve()
        knowledge_root = build_synthetic_knowledge_root(tmp_dir / "kb")
        ledger, shift, scope, token = seeded_workspace()
        body = p4a1_request_body(query=ADMITTED_QUERY, shift_ids=(str(shift.shift_id),))

        provider = _LiveDashScopeProvider(budget, key_env_name)
        registry = ProviderRegistry()
        registry.register(provider, (model_id,), placement=Placement.EXTERNAL)  # A1-F3: truthful EXTERNAL
        origin = safe_origin(endpoint())
        gateway = AIGateway(registry, UsageLedger(), endpoint_origin=origin)

        try:
            outcome = asyncio.run(
                execute_governed_rag(
                    raw_body=body,
                    rag_request=rag_request(query=ADMITTED_QUERY, model_id=model_id),
                    bearer_token=token,
                    assignment_scope=scope,
                    ledger=ledger,
                    metadata=execution_metadata(repository_root=knowledge_root),
                    gateway=gateway,
                    placement=Placement.EXTERNAL,  # P4A2-REV-F3: real dispatch, never LOCAL default.
                )
            )
        except LiveEvidenceError as exc:
            print(f"LIVE_EVIDENCE_BLOCKED: {exc}", file=sys.stderr)
            payload = _base_payload(
                generated_at=generated_at, provider=provider, model_id=model_id, origin=origin,
                key_env_name=key_env_name, refusals=refusals, gateway=gateway, budget=budget,
            )
            payload["disposition"] = "LIVE_EVIDENCE_BLOCKED"
            _, hits = write_receipt(payload)
            if hits:
                print("SECOND-ORDER WARNING: secret scan hit in blocked-run receipt", file=sys.stderr)
            return 1

        accepted = outcome.receipt.final_outcome.value in ("ANSWERED", "ABSTAINED")
        payload = _base_payload(
            generated_at=generated_at, provider=provider, model_id=model_id, origin=origin,
            key_env_name=key_env_name, refusals=refusals, gateway=gateway, budget=budget,
        )
        payload.update(
            accepted=accepted, receipt=json.loads(outcome.receipt.model_dump_json()),
            disposition="LIVE_EVIDENCE_PASS" if accepted else "LIVE_EVIDENCE_BLOCKED",
        )

        receipt_hash, hits = write_receipt(payload)
        print(
            f"  http_status: {provider.http_status}\n  physical calls: {budget.physical}\n"
            f"  final_outcome: {outcome.receipt.final_outcome.value}  reason: {outcome.receipt.reason_code or 'NONE'}\n"
            f"  receipt sha256: {receipt_hash}\n  secret scan hits: {hits or 'NONE'}"
        )
        if hits or budget.physical != 1 or not accepted:
            reason = "secret-like content in receipt" if hits else (
                f"expected exactly one physical call, got {budget.physical}" if budget.physical != 1
                else "admitted call was not accepted"
            )
            print(f"LIVE_EVIDENCE_BLOCKED: {reason}", file=sys.stderr)
            return 1

        print("LIVE_EVIDENCE_PASS")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
