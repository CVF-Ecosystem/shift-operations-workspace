#!/usr/bin/env python3
"""P4-B provider-mode live governance evidence (SPEC R12).

NOT EXECUTED WITH A REAL PROVIDER DURING THIS BUILD/REPAIR. ``--refusals-only``
IS safe during REPAIR (P4B-REV-F6: credential-independent, never imports
``alibaba.select_model``, never constructs a dispatching provider). The
admitted (consuming) branch is real, tested mechanics (P4B-REV-F6-R1: hard
one-attempt ``CallBudget``, last-moment credential read, one physical HTTPS
POST, no retry; P4B-REV-F6-R2: every evidence invariant is computed before
any disposition/write decision - see ``main()``) - not a stub - but this
repair round still never executes it. Tested via fakes/spies only in
``tests/integration/test_p4b_provider_live_evidence_support.py``.

Protocol, in order: (1) preflight - report only credential presence/env var
name, never the value; (2) mandated zero-call refusal cases, credential/
model-selection-independent; (3) confirm MockProviderAdapter output is
structurally evidence-ineligible; (4) only past this point, with refusals
passed and a credential present, select a model and dispatch the admitted
EXTERNAL_AI case; (5) compute outcome/counter/secret-scan invariants, THEN
write one sanitized receipt with the correct disposition. Any failure is
LIVE_EVIDENCE_BLOCKED; there is no retry.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
# P4B-REV-F6: "packages/ai-providers" (not just its src/) must be on
# sys.path so `from alibaba.select_model import select_model` resolves.
_SIBLING_PATHS = (
    "apps/workspace-api/src", "packages/cvf-runtime/src", "packages/ai-gateway/src",
    "packages/ai-providers/src", "packages/ai-providers",
)
for _p in (str(REPO_ROOT / s) for s in _SIBLING_PATHS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p4a_gateway_live_evidence_support import (  # noqa: E402
    CANARY_PROMPT,
    CallBudget,
    LiveEvidenceError,
    endpoint,
    extract_json_object,
    key_presence,
    safe_origin,
    sanitize,
)
from _p4b_ai_providers_live_evidence_support import (  # noqa: E402
    PROVIDER_ID,
    REFUSAL_CASES,
    AIGateway,
    Placement,
    ProviderModeService,
    ProviderRegistry,
    RuleSetV1,
    UsageLedger,
    build_admitted_external_request,
    mock_output_is_evidence_ineligible,
    render_receipt,
    run_refusals,
    write_receipt,
)

RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P4B_AI_PROVIDERS_LIVE_EVIDENCE_RECEIPT.md"
TRANCHE = "P4B-AI-PROVIDERS-2026-08-21"


class _CountingAdmittedProvider:
    """P4B-REV-F6-R1 - admitted-path adapter, mirroring P4-A's
    ``_LiveDashScopeProvider``: one-attempt ``CallBudget``, last-moment
    credential read, one physical POST, no retry. Testable/injectable via a
    fake/spy. Never invoked by ``main()`` during this repair."""

    provider_id = PROVIDER_ID

    def __init__(self, *, budget: CallBudget | None = None, key_env_name: str | None = None) -> None:
        self._budget = budget if budget is not None else CallBudget(limit=1)
        self._key_env_name = key_env_name
        self.calls = 0
        self.http_status: int | None = None
        self.reached_server, self.error_note = False, ""

    async def generate_structured_output(self, request):
        return await asyncio.to_thread(self._post, request)

    def _post(self, request):
        """One bounded HTTPS attempt; credential read only here. The budget
        reservation happens FIRST, before touching the request, building the
        body, or reading any credential - an exhausted budget fails closed
        immediately with no other side effect."""
        import urllib.error
        import urllib.request

        from ai_gateway.models import ProviderResult

        self._budget.reserve()
        if self._key_env_name is None:
            raise LiveEvidenceError("no credential env var configured")
        url = endpoint()
        body = json.dumps({
            "model": request.model_id, "messages": [{"role": "user", "content": CANARY_PROMPT}],
            "max_tokens": getattr(request, "max_output_tokens", 200), "temperature": 0,
        }).encode("utf-8")
        api_key = os.environ[self._key_env_name]  # read at the last moment; never stored/echoed
        http_request = urllib.request.Request(
            url, data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        self._budget.record_physical()
        self.calls += 1
        try:
            with urllib.request.urlopen(http_request, timeout=getattr(request, "timeout_seconds", 60)) as response:
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
            output=extract_json_object(content), provider_id=self.provider_id, model_id=request.model_id,
            usage={"total_tokens": int(usage.get("total_tokens", 0)), "cost_usd_millis": 0},
        )

    async def health_check(self) -> dict:
        raise LiveEvidenceError("health_check is not authorized in this tranche")

    async def cancel_request(self, request_id: str) -> None:
        return None


def run_admitted_case(model_id: str, key_env_name: str):
    """P4B-REV-F6-R1 - assemble (never invoke) the one-call admitted-path
    mechanics: matching outer/nested request, load-bearing P4-B registry
    entry, real gateway, :class:`_CountingAdmittedProvider`. Returns
    ``(service, request, provider, gateway)``; performs no I/O itself."""
    from ai_providers.models import ProviderKind, ProviderMetadataV1
    from ai_providers.registry import ProviderAdapterRegistry

    provider = _CountingAdmittedProvider(key_env_name=key_env_name)
    registry = ProviderRegistry()
    registry.register(provider, (model_id,), placement=Placement.EXTERNAL)
    gateway = AIGateway(registry, UsageLedger(), endpoint_origin=safe_origin(endpoint()))
    p4b_registry = ProviderAdapterRegistry()
    p4b_registry.register(ProviderMetadataV1(
        provider_id=PROVIDER_ID, kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.EXTERNAL,
        model_ids=(model_id,), evidence_eligible=True,
    ))
    service = ProviderModeService(rule_set=RuleSetV1(()), registry=p4b_registry, gateway=gateway)
    request = build_admitted_external_request(model_id)
    return service, request, provider, gateway


REHEARSAL_MODEL_ID = "p4b-refusal-rehearsal-model"
"""P4B-REV-F6: a stable label for the zero-call refusal path, which never
needs a real, credential/quota-gated model selection - keeps
``--refusals-only`` credential/model-selection-independent."""


def decide_admitted_disposition(*, receipt, provider, gateway, generated_at, model_id, key_env_name, refusals) -> dict:
    """P4B-REV-F6-R2 - compute EVERY evidence invariant and the final
    disposition BEFORE anything is written to disk. Pure with respect to
    I/O: takes an already-executed receipt/provider/gateway (real or fake)
    and returns a dict describing the decision, including the fully
    rendered receipt document - callers decide whether/how to persist it.

    ``counters_agree`` is the exact match across all four independent
    counters (adapter's own call count, gateway's own physical-attempt
    count, receipt's own gateway_calls/provider_attempts) - an anomalous
    accepted result where any of these four disagree must never be labeled
    PASS. The secret scan runs on the actual rendered body BEFORE the
    disposition line is decided, so a provisional BLOCKED body is scanned
    first and only re-rendered as PASS if every invariant holds."""
    accepted = receipt.outcome.value == "EXTERNAL_ACCEPTED"
    counters = (provider.calls, gateway.physical_attempts, receipt.gateway_calls, receipt.provider_attempts)
    counters_agree = counters == (1, 1, 1, 1)
    payload = {
        "generated_at": generated_at, "tranche": TRANCHE, "provider_id": PROVIDER_ID,
        "model_id": model_id, "refusal_cases": refusals,
        "mock_evidence_ineligible_confirmed": True,
        "endpoint_origin": safe_origin(endpoint()),
        "credential_env_var": key_env_name,
        "adapter_calls": provider.calls,
        "gateway_physical_attempts": gateway.physical_attempts,
        "http_status": provider.http_status,
        "reached_server": provider.reached_server,
        "outcome": receipt.outcome.value,
        "reason_code": receipt.reason_code,
        "gateway_calls": receipt.gateway_calls,
        "provider_attempts": receipt.provider_attempts,
        "disposition": "LIVE_EVIDENCE_BLOCKED",  # provisional; never PASS until every invariant below holds
    }
    document, hits = render_receipt(payload, tranche=TRANCHE)  # secret-scan first, no disk write yet
    evidence_pass = accepted and counters_agree and not hits
    if evidence_pass:
        payload["disposition"] = "LIVE_EVIDENCE_PASS"
        document, hits = render_receipt(payload, tranche=TRANCHE)
    return dict(document=document, hits=hits, accepted=accepted, counters_agree=counters_agree, counters=counters, evidence_pass=evidence_pass)


def main() -> int:
    parser = argparse.ArgumentParser(description="P4-B provider-mode live governance evidence")
    parser.add_argument("--refusals-only", action="store_true", help="stop before any provider call")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).isoformat()
    present, key_env_name = key_presence()
    print(f"== preflight ==\n  credential present: {present}\n  env var: {key_env_name or 'NONE'}")

    # alibaba.select_model belongs only to the admitted branch below - the
    # refusals-only rehearsal never needs a live model selection.
    rehearsal_model_id = REHEARSAL_MODEL_ID

    print(f"== refusal cases (must be zero gateway/provider attempts; {len(REFUSAL_CASES)} mandated) ==")
    refusals = run_refusals(rehearsal_model_id)
    for row in refusals:
        print(
            f"  {row['case']}: outcome={row['outcome']} reason={row['reason_code'] or 'NONE'} "
            f"gateway_calls={row['gateway_calls']} adapter_calls={row['adapter_calls']}"
        )
    zero_call = lambda r: r["gateway_calls"] == r["adapter_calls"] == r["gateway_physical_attempts"] == 0  # noqa: E731
    if not all(zero_call(row) for row in refusals):
        print("LIVE_EVIDENCE_BLOCKED: a refusal case was not zero-call", file=sys.stderr)
        return 1
    print(f"  all {len(refusals)} refusal cases passed with zero gateway/provider attempts")

    if not mock_output_is_evidence_ineligible():
        print("LIVE_EVIDENCE_BLOCKED: mock output was not evidence-ineligible", file=sys.stderr)
        return 1
    print("  mock output confirmed structurally evidence-ineligible")

    if args.refusals_only:
        print("refusals-only mode: stopping before any provider call")
        return 0

    if not present or key_env_name is None:
        print("LIVE_EVIDENCE_BLOCKED: no credential in environment", file=sys.stderr)
        return 1

    try:
        from alibaba.select_model import select_model  # noqa: PLC0415

        model_id = select_model()
    except Exception as exc:
        print(f"LIVE_EVIDENCE_BLOCKED: no eligible model ({type(exc).__name__})", file=sys.stderr)
        return 1
    print(f"  selected model: {model_id}")

    print("== single admitted EXTERNAL_AI case through the P4-B service ==")
    service, request, provider, gateway = run_admitted_case(model_id, key_env_name)
    result = asyncio.run(service.execute(request=request, started_at=generated_at, finished_at=datetime.now(timezone.utc).isoformat()))

    decision = decide_admitted_disposition(
        receipt=result.receipt, provider=provider, gateway=gateway,
        generated_at=generated_at, model_id=model_id, key_env_name=key_env_name, refusals=refusals,
    )
    receipt_hash = write_receipt(decision["document"], receipt_path=RECEIPT_PATH)  # only now, disposition is final
    print(f"  http_status: {provider.http_status}")
    print(f"  adapter calls: {provider.calls}  gateway physical attempts: {gateway.physical_attempts}")
    print(f"  outcome: {result.receipt.outcome.value}  reason: {result.receipt.reason_code or 'NONE'}")
    print(f"  receipt sha256: {receipt_hash}")
    print(f"  secret scan hits: {decision['hits'] or 'NONE'}")

    if decision["hits"]:
        print("LIVE_EVIDENCE_BLOCKED: secret-like content in receipt", file=sys.stderr)
        return 1
    if not decision["counters_agree"]:
        print(f"LIVE_EVIDENCE_BLOCKED: counters disagree, expected all-1: got {decision['counters']}", file=sys.stderr)
        return 1
    if not decision["accepted"]:
        print("LIVE_EVIDENCE_BLOCKED: admitted case was not accepted", file=sys.stderr)
        return 1

    print("LIVE_EVIDENCE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
