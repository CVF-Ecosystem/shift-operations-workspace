"""P4-A SPEC R4/R7/R8/R9/R10 - execution outcomes and sanitized receipts.

NOT GOVERNANCE PROOF: fake-provider mechanics only; do NOT prove governance
against a real provider. R13's live run is the governance proof.
"""

from __future__ import annotations

import asyncio

import pytest

from ai_gateway.models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    FinalOutcome,
    GateOutcome,
    GatewayRequest,
    Placement,
    ProviderRequest,
    ProviderResult,
    TerminationFacts,
    digest_of,
)
from ai_gateway.registry import ProviderRegistry
from ai_gateway.service import AIGateway
from ai_gateway.usage import UsageLedger

DIGEST = "b" * 64
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["ok"],
    "properties": {"ok": {"type": "boolean"}},
}
SECRET_LIKE = "sk-canary-must-never-appear-in-receipt"


class _FakeProvider:
    """Non-governance fake. Configurable outcome; records dispatch count."""

    def __init__(self, *, output=None, raises=None, delay=0.0, provider_id="fake") -> None:
        self.provider_id = provider_id
        self._output = {"ok": True} if output is None else output
        self._raises = raises
        self._delay = delay
        self.calls = 0
        self.cancelled: list[str] = []

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        self.calls += 1
        if self._delay:
            await asyncio.sleep(self._delay)
        if self._raises is not None:
            raise self._raises
        return ProviderResult(
            output=self._output,
            provider_id=self.provider_id,
            model_id=request.model_id,
            usage={"total_tokens": 12, "cost_usd_millis": 3},
        )

    async def health_check(self) -> dict:
        return {}

    async def cancel_request(self, request_id: str) -> None:
        self.cancelled.append(request_id)


def _request(**overrides) -> GatewayRequest:
    """Build a GatewayRequest whose context_facts.context_digest matches the
    actual ``context`` by default (P4A-REV-F3 binds the two). A test that
    wants to exercise a digest MISMATCH should pass an explicit
    ``context_facts={"context_digest": "<wrong 64-hex>"}`` override."""
    context_overrides = overrides.pop("context_facts", {})
    budget_overrides = overrides.pop("budget_facts", {})
    termination_overrides = overrides.pop("termination_facts", {})
    context = overrides.get("context", {"note": "public canary"})

    context_base = dict(
        classification=Classification.PUBLIC,
        redaction_applied=True,
        minimization_proven=False,
        evidence_count=1,
        estimated_input_tokens=10,
        context_digest=digest_of(context),
    )
    context_base.update(context_overrides)

    budget_base = dict(
        per_request_token_limit=1000,
        daily_budget_usd_millis=1000,
        monthly_budget_usd_millis=10000,
        spent_today_usd_millis=0,
        spent_month_usd_millis=0,
        estimated_cost_usd_millis=1,
    )
    budget_base.update(budget_overrides)

    base = dict(
        task_type="canary",
        ai_mode=AIMode.EXTERNAL_AI,
        provider_id="fake",
        model_id="model-a",
        placement=Placement.EXTERNAL,
        context=context,
        output_schema=SCHEMA,
        context_facts=ContextFacts(**context_base),
        budget_facts=BudgetFacts(**budget_base),
        termination_facts=TerminationFacts(**termination_overrides),
    )
    base.update(overrides)
    return GatewayRequest(**base)


def _gateway(provider: _FakeProvider) -> tuple[AIGateway, UsageLedger]:
    registry = ProviderRegistry()
    registry.register(provider, ("model-a",), placement=Placement.EXTERNAL)
    ledger = UsageLedger()
    return AIGateway(registry, ledger, endpoint_origin="https://example.invalid"), ledger


def _run(coro):
    return asyncio.run(coro)


class TestAcceptedPath:
    def test_accepted_result_commits_usage_and_counts_one_attempt(self):
        provider = _FakeProvider()
        gateway, ledger = _gateway(provider)
        result = _run(gateway.execute(_request()))

        assert result.accepted is True
        assert result.output == {"ok": True}
        assert provider.calls == 1
        assert gateway.physical_attempts == 1
        assert result.receipt.final_outcome is FinalOutcome.ACCEPTED
        assert result.receipt.provider_attempts == 1
        assert result.receipt.usage_committed is True
        assert ledger.committed_tokens == 12
        assert ledger.outstanding_reservations == 0

    def test_gate_order_is_recorded_in_execution_order(self):
        """R3: the three CVF gates appear in the mandated relative order."""
        provider = _FakeProvider()
        gateway, _ = _gateway(provider)
        result = _run(gateway.execute(_request()))
        gates = [record.gate for record in result.receipt.gates]

        placement = gates.index("data_scope.assert_placement_allowed")
        budget = gates.index("cost.assert_within_budget")
        termination = gates.index("termination.assert_not_terminated")
        dispatch = gates.index("provider_dispatch")
        assert placement < budget < termination < dispatch

    def test_receipt_contains_no_context_or_output_body(self):
        """R10: receipts carry digests and safe identifiers only."""
        provider = _FakeProvider(output={"ok": True})
        gateway, _ = _gateway(provider)
        request = _request(context={"secret_note": SECRET_LIKE})
        result = _run(gateway.execute(request))

        serialized = result.receipt.model_dump_json()
        assert SECRET_LIKE not in serialized
        assert "secret_note" not in serialized
        assert "public canary" not in serialized
        assert result.receipt.output_digest and len(result.receipt.output_digest) == 64


class TestZeroAttemptRefusals:
    """R4: every pre-dispatch refusal must reach the provider zero times."""

    _INTERNAL = {"context_facts": {"classification": Classification.INTERNAL}}
    _RESTRICTED = {"context_facts": {"classification": Classification.RESTRICTED}}
    _CONFIDENTIAL = {"context_facts": {"classification": Classification.CONFIDENTIAL}}
    _KILL_SWITCH = {
        "termination_facts": {"terminate_when": ("kill_switch_active",), "kill_switch_active": True}
    }

    @pytest.mark.parametrize(
        "overrides,expected_reason",
        [
            ({"ai_mode": AIMode.NO_AI}, "AI_MODE_DISABLED"),
            ({"ai_mode": AIMode.RULES_ONLY}, "AI_MODE_DISABLED"),
            ({"context_facts": {"evidence_count": 0}}, "NO_EVIDENCE"),
            (_INTERNAL, "CONTEXT_INADMISSIBLE"),
            (_RESTRICTED, "CONTEXT_INADMISSIBLE"),
            (_CONFIDENTIAL, "CONTEXT_INADMISSIBLE"),
            ({"context_facts": {"redaction_applied": False}}, "CONTEXT_INADMISSIBLE"),
            ({"model_id": "unregistered-model"}, "PROVIDER_NOT_REGISTERED"),
            ({"budget_facts": {"per_request_token_limit": 1}}, "BUDGET_UNAVAILABLE"),
            (_KILL_SWITCH, "TERMINATED"),
        ],
    )
    def test_refusal_makes_zero_calls(self, overrides, expected_reason):
        provider = _FakeProvider()
        gateway, ledger = _gateway(provider)
        result = _run(gateway.execute(_request(**overrides)))

        assert result.accepted is False
        assert result.output is None
        assert provider.calls == 0, "provider must not be reached"
        assert gateway.physical_attempts == 0
        assert result.receipt.provider_attempts == 0
        assert result.receipt.reason_code == expected_reason
        assert result.receipt.final_outcome in (
            FinalOutcome.REFUSED_PRE_DISPATCH,
            FinalOutcome.FALLBACK_RULES,
        )
        assert ledger.outstanding_reservations == 0, "reservation must not leak"

    def test_unknown_provider_makes_zero_calls(self):
        provider = _FakeProvider()
        gateway, _ = _gateway(provider)
        result = _run(gateway.execute(_request(provider_id="not-registered")))
        assert provider.calls == 0
        assert result.receipt.reason_code == "PROVIDER_NOT_REGISTERED"

    def test_failed_gate_is_recorded_as_fail(self):
        provider = _FakeProvider()
        gateway, _ = _gateway(provider)
        result = _run(gateway.execute(_request(ai_mode=AIMode.NO_AI)))
        failed = [g for g in result.receipt.gates if g.outcome is GateOutcome.FAIL]
        assert failed and failed[-1].reason_code == "AI_MODE_DISABLED"


class TestPostDispatchFailures:
    def test_invalid_output_keeps_one_attempt_and_releases(self):
        """R9: schema-invalid output never becomes an accepted result."""
        provider = _FakeProvider(output={"ok": "not-a-boolean"})
        gateway, ledger = _gateway(provider)
        result = _run(gateway.execute(_request()))

        assert result.accepted is False
        assert provider.calls == 1
        assert result.receipt.provider_attempts == 1
        assert result.receipt.reason_code == "OUTPUT_SCHEMA_INVALID"
        assert result.receipt.final_outcome is FinalOutcome.FAILED_POST_DISPATCH
        assert result.receipt.usage_committed is False
        assert result.receipt.reservation_released is True
        assert ledger.committed_tokens == 0
        assert ledger.outstanding_reservations == 0

    def test_provider_exception_does_not_retry(self):
        """R8: one attempt only; the gateway never retries in this tranche."""
        provider = _FakeProvider(raises=RuntimeError(SECRET_LIKE))
        gateway, _ = _gateway(provider)
        result = _run(gateway.execute(_request()))

        assert provider.calls == 1
        assert result.receipt.provider_attempts == 1
        assert result.receipt.reason_code == "PROVIDER_DISPATCH_FAILED"
        # Raw exception text may echo a secret; it must not reach the receipt.
        assert SECRET_LIKE not in result.receipt.model_dump_json()

    def test_timeout_records_attempt_and_attempts_cancel(self):
        """R7: timeout keeps one attempt, cancels best-effort, never retries.

        The provider sleeps well past the gateway's configured bound, so this
        exercises the real ``asyncio.wait_for`` timeout path rather than
        completing early and asserting for the wrong reason.
        """
        provider = _FakeProvider(delay=30.0)
        gateway, ledger = _gateway(provider)
        result = _run(gateway.execute(_request(timeout_seconds=1)))

        assert provider.calls == 1, "the attempt was physically made"
        assert result.receipt.provider_attempts == 1
        assert result.receipt.timed_out is True
        assert result.receipt.cancel_attempted is True
        assert result.receipt.reason_code == "PROVIDER_TIMEOUT"
        assert result.receipt.final_outcome is FinalOutcome.FAILED_POST_DISPATCH
        assert result.receipt.usage_committed is False
        assert result.receipt.reservation_released is True
        assert ledger.outstanding_reservations == 0
        assert provider.cancelled, "best-effort cancel_request was invoked"


class TestFallback:
    def test_budget_exceeded_falls_back_with_zero_calls(self):
        provider = _FakeProvider()
        gateway, ledger = _gateway(provider)
        result = _run(
            gateway.execute(
                _request(
                    budget_facts={
                        "daily_budget_usd_millis": 10,
                        "spent_today_usd_millis": 10,
                        "estimated_cost_usd_millis": 0,
                        "on_budget_exceeded": "fallback_to_rules",
                    }
                )
            )
        )
        assert provider.calls == 0
        assert result.accepted is False
        assert result.receipt.provider_attempts == 0
        assert ledger.outstanding_reservations == 0
