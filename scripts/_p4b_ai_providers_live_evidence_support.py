"""Support state and helpers for a future P4-B live evidence run (SPEC R12).

REHEARSAL-focused: every helper here uses spies/fakes and performs no I/O at
import time and no network call ever. This module proves the *mechanics*
the mandated zero-call refusal cases use, and re-exports the P4-A/P4-B
building blocks the paired runner needs to assemble its own real (never-
invoked-here) admitted-path mechanics - P4B-REV-F6-R1's
``_CountingAdmittedProvider``/``run_admitted_case`` live in
``run_p4b_ai_providers_live_evidence.py`` itself (room under the file-size
guard), not here. This module does not itself constitute governance
evidence, and the runner must not be executed with a real provider during
this tranche/repair.

Reuses the P4-A secret-sanitizing helpers rather than duplicating them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_SIBLING_PATHS = (
    "apps/workspace-api/src", "packages/cvf-runtime/src", "packages/ai-gateway/src",
    "packages/ai-providers/src",
)
for _p in (str(REPO_ROOT / s) for s in _SIBLING_PATHS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p4a_gateway_live_evidence_support import (  # noqa: E402
    CANARY_SCHEMA,
    LiveEvidenceError,
    safe_origin,
    sanitize,
    scan_for_secrets,
    sha256_hex,
)
from ai_gateway.models import (  # noqa: E402
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    GatewayRequest,
    Placement,
    TerminationFacts,
    digest_of,
)
from ai_gateway.registry import ProviderRegistry  # noqa: E402
from ai_gateway.service import AIGateway  # noqa: E402
from ai_gateway.usage import UsageLedger  # noqa: E402
from ai_providers.models import MockAuthorizationV1, ProviderModeRequestV1  # noqa: E402
from ai_providers.rules_only import RuleSetV1  # noqa: E402
from ai_providers.service import ProviderModeService  # noqa: E402

__all__ = [
    "LiveEvidenceError", "safe_origin", "sanitize", "scan_for_secrets", "sha256_hex",
    "PROVIDER_ID", "SCHEMA", "REFUSAL_CASES", "build_no_ai_request", "build_rules_only_request",
    "build_mismatched_external_request", "build_matching_gateway_request",
    "build_admitted_external_request", "run_refusals", "mock_output_is_evidence_ineligible",
    "ProviderRegistry", "AIGateway", "UsageLedger", "RuleSetV1", "ProviderModeService", "Placement",
    "render_receipt", "write_receipt",
]

PROVIDER_ID = "p4b_evidence_only_test_provider"
# P4B-LIVE-F1: the runner imports P4-A's CANARY_PROMPT, so its schema must
# come from the same canonical contract rather than a divergent local copy.
SCHEMA = CANARY_SCHEMA
REFUSAL_CASES = ("NO_AI", "RULES_NO_MATCH", "EXTERNAL_TASK_TYPE_MISMATCH", "EXTERNAL_NO_GATEWAY")


def build_no_ai_request() -> ProviderModeRequestV1:
    return ProviderModeRequestV1(
        task_type="p4b_canary", ai_mode="NO_AI", facts={}, output_schema=SCHEMA,
        policy_version="p4b-evidence-v1", request_id="p4b-refusal-no-ai",
    )


def build_rules_only_request() -> ProviderModeRequestV1:
    """Facts deliberately do not match any rule in the empty rule set used
    by the refusal harness, so this always yields RULES_NO_MATCH."""
    return ProviderModeRequestV1(
        task_type="p4b_canary", ai_mode="RULES_ONLY", facts={"unmatched": True}, output_schema=SCHEMA,
        policy_version="p4b-evidence-v1", request_id="p4b-refusal-rules-no-match",
    )


def _context_facts() -> ContextFacts:
    return ContextFacts(
        classification=Classification.PUBLIC, redaction_applied=True, minimization_proven=True,
        evidence_count=1, estimated_input_tokens=5, context_digest=digest_of({}),
    )


def _budget_facts() -> BudgetFacts:
    return BudgetFacts(
        per_request_token_limit=1000, daily_budget_usd_millis=0, monthly_budget_usd_millis=0,
        spent_today_usd_millis=0, spent_month_usd_millis=0, estimated_cost_usd_millis=0,
    )


def build_matching_gateway_request(model_id: str, *, placement: Placement = Placement.EXTERNAL) -> GatewayRequest:
    return GatewayRequest(
        task_type="p4b_canary", ai_mode=AIMode.EXTERNAL_AI, provider_id=PROVIDER_ID, model_id=model_id,
        placement=placement, context={}, output_schema=SCHEMA,
        context_facts=_context_facts(), budget_facts=_budget_facts(), termination_facts=TerminationFacts(),
    )


def build_admitted_external_request(model_id: str) -> ProviderModeRequestV1:
    """P4B-REV-F6 - the fully matching outer/nested request shape a FUTURE,
    separately authorized admitted-path run would submit to
    ProviderModeService for its single admitted EXTERNAL_AI call. Building
    this request performs no I/O; it is exercised only by unit/integration
    tests here (spies/fakes), never dispatched by this BUILD/repair."""
    gw_req = build_matching_gateway_request(model_id)
    return ProviderModeRequestV1(
        task_type="p4b_canary", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="p4b-evidence-v1", request_id="p4b-admitted-external-ai",
        nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )


def build_mismatched_external_request(model_id: str) -> ProviderModeRequestV1:
    """A nested GatewayRequest whose task_type disagrees with the outer
    request - SPEC R6 requires this to be a zero-call refusal. The outer
    envelope still declares its own provider/model/placement/context_digest
    (P4B-REV-F3) so this exercises the task_type check specifically, not an
    incidental missing-binding-fact refusal."""
    gw_req = build_matching_gateway_request(model_id).model_copy(update={"task_type": "different_task"})
    return ProviderModeRequestV1(
        task_type="p4b_canary", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="p4b-evidence-v1", request_id="p4b-refusal-identity-mismatch",
        nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )


def build_no_gateway_external_request(model_id: str) -> ProviderModeRequestV1:
    """A fully matching outer/nested request (P4B-REV-F3 binding facts
    included) submitted to a service with NO injected gateway - proves that
    path is zero-call independent of the identity-binding checks."""
    gw_req = build_matching_gateway_request(model_id)
    return ProviderModeRequestV1(
        task_type="p4b_canary", ai_mode="EXTERNAL_AI", facts={}, output_schema=SCHEMA,
        policy_version="p4b-evidence-v1", request_id="p4b-refusal-no-gateway",
        nested_gateway_request=gw_req.model_dump(mode="python"),
        provider_id=gw_req.provider_id, model_id=gw_req.model_id,
        placement=gw_req.placement, context_digest=gw_req.context_facts.context_digest,
    )


class _GuardProvider:
    """Raises if ever dispatched; every refusal case must never reach it."""

    provider_id = PROVIDER_ID

    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured_output(self, request):
        self.calls += 1
        raise LiveEvidenceError("a refusal case reached the provider")

    async def health_check(self) -> dict:
        raise LiveEvidenceError("health_check is not authorized in this tranche")

    async def cancel_request(self, request_id: str) -> None:
        return None


def run_refusals(model_id: str) -> list[dict]:
    """Every mandated P4-B refusal must produce zero rules/gateway/provider
    attempts (except RULES_NO_MATCH, which evaluates the rule set locally
    but must still make zero gateway/provider calls). Spies/fakes only -
    performs no network I/O."""
    import asyncio

    from ai_providers.models import ProviderKind, ProviderMetadataV1
    from ai_providers.registry import ProviderAdapterRegistry

    results: list[dict] = []
    for case in REFUSAL_CASES:
        provider = _GuardProvider()
        registry = ProviderRegistry()
        registry.register(provider, (model_id,), placement=Placement.EXTERNAL)
        gateway = AIGateway(registry, UsageLedger(), endpoint_origin=safe_origin("https://example.invalid"))
        # P4B-REV-F1/F1-R1: the load-bearing P4-B registry, independent of
        # the P4-A ProviderRegistry the gateway itself holds - registered
        # here with kind=EXTERNAL_GATEWAY AND evidence_eligible=True (the
        # one combination the registry gate actually admits) so
        # EXTERNAL_NO_GATEWAY exercises specifically the "no gateway
        # injected" refusal rather than an incidental registry-eligibility
        # refusal masking it.
        p4b_registry = ProviderAdapterRegistry()
        p4b_registry.register(
            ProviderMetadataV1(
                provider_id=PROVIDER_ID, kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.EXTERNAL,
                model_ids=(model_id,), evidence_eligible=True,
            )
        )
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=p4b_registry, gateway=gateway)

        builders = {
            "NO_AI": build_no_ai_request,
            "RULES_NO_MATCH": build_rules_only_request,
            "EXTERNAL_TASK_TYPE_MISMATCH": lambda: build_mismatched_external_request(model_id),
            "EXTERNAL_NO_GATEWAY": lambda: build_no_gateway_external_request(model_id),
        }
        request = builders[case]()
        # EXTERNAL_NO_GATEWAY deliberately uses a service with NO injected
        # gateway, to prove that path is also zero-call.
        active_service = (
            ProviderModeService(rule_set=RuleSetV1(()), registry=p4b_registry, gateway=None)
            if case == "EXTERNAL_NO_GATEWAY"
            else service
        )
        result = asyncio.run(active_service.execute(request=request, started_at="t0", finished_at="t1"))
        receipt = result.receipt
        results.append({
            "case": case, "outcome": receipt.outcome.value, "reason_code": receipt.reason_code,
            "gateway_calls": receipt.gateway_calls, "provider_attempts": receipt.provider_attempts,
            "adapter_calls": provider.calls, "gateway_physical_attempts": gateway.physical_attempts,
        })
    return results


def mock_output_is_evidence_ineligible() -> bool:
    """Proves a MockProviderAdapter's authorization is structurally
    evidence-ineligible - used by the runner to assert it must never treat
    mock output as governance proof (SPEC R7/R12)."""
    from ai_providers.mock_provider import MockProviderAdapter

    auth = MockAuthorizationV1(purpose="TEST_ONLY_COMPONENT_TEST", evidence_eligible=False)
    adapter = MockProviderAdapter(provider_id="mock-evidence-check", authorization=auth, fixed_output={"status": "ok"})
    return adapter.evidence_eligible is False


def render_receipt(payload: dict, *, tranche: str) -> tuple[str, list[str]]:
    """P4B-REV-F6-R2: build the receipt document and scan it for secrets
    WITHOUT writing anything to disk - so the caller (the runner's
    ``main()``) can compute every evidence invariant, including this secret
    scan, before deciding whether a write - and with which disposition -
    should happen at all. Never called by this repair with a real
    admitted-case payload; only by tests with fakes/spies."""
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    hits = scan_for_secrets(body)
    document = f"""# P4-B AI Providers - Live Evidence Receipt

- Tranche: `{tranche}`
- Generated: `{payload["generated_at"]}`
- Disposition: `{payload["disposition"]}`

Sanitized machine-readable record. Contains digests, safe identifiers,
counts, and outcome/reason codes only - no facts, context, rule output,
prompt, provider output, credential, or raw exception.

```json
{body}
```

## Claim boundary

Proves the mandated zero-call refusal cases reached the provider zero
times, MockProviderAdapter output is structurally evidence-ineligible, and
(when past refusals-only) exactly one admitted EXTERNAL_AI dispatch was
attempted. Not proof of a production adapter, automatic routing, durable
usage/audit, a public API/UI, deployment, or production readiness.
"""
    return document, hits


def write_receipt(document: str, *, receipt_path: Path) -> str:
    """Write an already-rendered document (see :func:`render_receipt`) and
    return its hash. Takes the final text, never a payload, so a caller must
    have already decided the disposition before anything reaches disk."""
    receipt_path.write_text(document, encoding="utf-8")
    return sha256_hex(document)
