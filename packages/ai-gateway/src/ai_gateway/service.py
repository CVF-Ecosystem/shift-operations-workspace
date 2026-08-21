"""AIGateway.execute - the sole authorized provider-dispatch point (SPEC R3).

DESIGN order, implemented literally: (1) request/schema validation, (2)
AI-mode/evidence/context checks, (2b) registry-owned placement binding check
(P4A2-REV-F3/Amendment 1: a REGISTERED provider's own immutable placement
must equal the request's, before any context/data-scope work), (3)
context-digest binding + classification/minimization admission, (4)
``assert_placement_allowed``, (5) reserve then ``assert_within_budget``, (6)
``assert_not_terminated``, (7) resolve a registered provider/model, (8) count
the attempt immediately before dispatch, (9) timeout + best-effort cancel,
(10) provider-identity check + exact-schema validation, (11) commit or
release and emit a sanitized receipt or fallback. The three CVF gates are
imported from ``cvf_runtime`` and called directly, so a dependency test can
assert this module is a real call site rather than a re-implementation.
Every pre-dispatch refusal returns ``provider_attempts=0``; post-dispatch
failures preserve exactly one attempt and never retry.
"""

from __future__ import annotations

import asyncio
from typing import Any

from cvf_runtime.budget import BudgetState, assert_within_budget
from cvf_runtime.data_scope import assert_placement_allowed
from cvf_runtime.errors import CvfDenied
from cvf_runtime.termination import assert_not_terminated

from .context import (
    CvfProfileView,
    assert_context_admissible,
    assert_context_digest_matches,
    assert_provider_identity_matches,
    canonicalize_endpoint_origin,
    cost_policy_of,
    millis_to_usd,
    task_state_of,
    termination_policy_of,
)
from .errors import (
    AIModeDisabledError,
    BudgetUnavailableError,
    GatewayError,
    GateRecorder,
    OutputSchemaError,
    PlacementDeniedError,
    ProviderDispatchError,
    ProviderIdentityMismatchError,
    ProviderPlacementMismatchError,
    ProviderTimeoutError,
    ReceiptBuilder,
    TerminatedError,
    _now,
)
from .models import AIMode, GatewayRequest, GatewayResult, ProviderRequest, ProviderResult, digest_of
from .registry import ProviderRegistry
from .usage import UsageLedger
from .validation import validate_output

GATE_REQUEST = "request_validation"
GATE_AI_MODE = "ai_mode"
GATE_PLACEMENT_BINDING = "registry.provider_placement_binding"
GATE_CONTEXT = "context_admission"
GATE_PLACEMENT = "data_scope.assert_placement_allowed"
GATE_BUDGET = "cost.assert_within_budget"
GATE_TERMINATION = "termination.assert_not_terminated"
GATE_REGISTRY = "provider_registry"
GATE_DISPATCH = "provider_dispatch"
GATE_OUTPUT = "output_schema"
FALLBACK_ACTION = "fallback_to_rules"


class AIGateway:
    """Provider-neutral governed gateway. No application globals, no web
    endpoint; callers inject the registry and ledger. ``endpoint_origin`` is
    canonicalized to scheme+host (P4A-REV-F3) - never credentials or query."""

    def __init__(
        self, registry: ProviderRegistry, ledger: UsageLedger, *, endpoint_origin: str = ""
    ) -> None:
        self._registry = registry
        self._ledger = ledger
        # P4A-REV-F3: canonicalize here, not trusting the caller's string.
        self._endpoint_origin = canonicalize_endpoint_origin(endpoint_origin)
        self._physical_attempts = 0

    @property
    def physical_attempts(self) -> int:
        """Total physical provider attempts made by this instance."""
        return self._physical_attempts

    async def execute(self, request: GatewayRequest) -> GatewayResult:
        """Run the mandatory gate order and at most one provider dispatch."""
        gates = GateRecorder()
        gates.passed(GATE_REQUEST)  # strict models validated at construction

        request_digest = digest_of({
            "task_type": request.task_type, "provider_id": request.provider_id,
            "model_id": request.model_id, "placement": request.placement.value,
            "ai_mode": request.ai_mode.value, "max_output_tokens": request.max_output_tokens,
            "timeout_seconds": request.timeout_seconds,
        })
        receipts = ReceiptBuilder(
            request, gates, endpoint_origin=self._endpoint_origin, request_digest=request_digest,
            schema_digest=digest_of(request.output_schema), started_at=_now(),
        )

        def _refuse(gate: str, reason_code: str, *, reservation_id: str = "") -> GatewayResult:
            if reservation_id:
                self._ledger.release(reservation_id)
            gates.failed(gate, reason_code)
            return receipts.refused(reason_code)

        # 2 - AI mode, evidence and context handoff.
        if request.ai_mode is not AIMode.EXTERNAL_AI:
            return _refuse(GATE_AI_MODE, AIModeDisabledError.reason_code)
        gates.passed(GATE_AI_MODE)

        # 2b - P4A2-REV-F3/Amendment 1: registry-owned placement binding,
        # before context admission/data-scope. Only fires when registered
        # AND its bound placement disagrees; unregistered keeps its existing
        # later GATE_REGISTRY refusal. Zero calls/reservations either way.
        registered_placement = self._registry.registered_placement(request.provider_id)
        if registered_placement is not None and registered_placement is not request.placement:
            return _refuse(GATE_PLACEMENT_BINDING, ProviderPlacementMismatchError.reason_code)
        gates.passed(GATE_PLACEMENT_BINDING)

        # 3 - bind context_digest to the actual context (P4A-REV-F3), then
        # classification/minimization admission.
        try:
            assert_context_digest_matches(request.context, request.context_facts)
            assert_context_admissible(request.context_facts, request.placement)
        except GatewayError as exc:
            return _refuse(GATE_CONTEXT, exc.reason_code)
        gates.passed(GATE_CONTEXT)

        # 4 - the data-scope gate itself.
        try:
            assert_placement_allowed(
                profile=CvfProfileView(), classification=request.context_facts.classification.value,
                placement=request.placement.value,
            )
        except CvfDenied:
            return _refuse(GATE_PLACEMENT, PlacementDeniedError.reason_code)
        gates.passed(GATE_PLACEMENT)

        # 5 - reserve, then the cost gate. A non-PASS cost outcome always
        # releases the reservation so a refusal can never leak one.
        try:
            reservation = self._ledger.reserve(
                request.budget_facts, estimated_tokens=request.context_facts.estimated_input_tokens,
            )
        except GatewayError as exc:
            return _refuse(GATE_BUDGET, exc.reason_code)
        rid = reservation.reservation_id

        # P4A-REV-F2: state.spent_* is USD (not millis) and includes this
        # ledger's own committed+reserved cost, not just caller-supplied spend.
        ledger_total_millis = self._ledger.committed_cost_usd_millis + self._ledger.reserved_cost_usd_millis
        try:
            budget_action = assert_within_budget(
                cost_policy=cost_policy_of(request),
                state=BudgetState(
                    spent_today_usd=millis_to_usd(
                        request.budget_facts.spent_today_usd_millis + ledger_total_millis
                    ),
                    spent_month_usd=millis_to_usd(
                        request.budget_facts.spent_month_usd_millis + ledger_total_millis
                    ),
                ),
                requested_tokens=request.context_facts.estimated_input_tokens,
            )
        except CvfDenied:
            return _refuse(GATE_BUDGET, BudgetUnavailableError.reason_code, reservation_id=rid)
        if budget_action == FALLBACK_ACTION:
            self._ledger.release(rid)
            gates.failed(GATE_BUDGET, BudgetUnavailableError.reason_code)
            return receipts.fallback(BudgetUnavailableError.reason_code, reservation_released=True)
        gates.passed(GATE_BUDGET)

        # 6 - termination/kill-switch preflight.
        try:
            assert_not_terminated(termination_policy_of(request), task_state_of(request))
        except CvfDenied:
            return _refuse(GATE_TERMINATION, TerminatedError.reason_code, reservation_id=rid)
        gates.passed(GATE_TERMINATION)

        # 7 - explicit provider/model resolution.
        try:
            provider = self._registry.resolve(request.provider_id, request.model_id)
        except GatewayError as exc:
            return _refuse(GATE_REGISTRY, exc.reason_code, reservation_id=rid)
        gates.passed(GATE_REGISTRY)

        # 8-11 - one dispatch, then settle.
        return await self._dispatch(
            request,
            gates,
            receipts,
            provider=provider,
            reservation_id=reservation.reservation_id,
            reserved_tokens=reservation.estimated_tokens,
            reserved_cost=reservation.estimated_cost_usd_millis,
        )

    async def _dispatch(
        self,
        request: GatewayRequest,
        gates: GateRecorder,
        receipts: ReceiptBuilder,
        *,
        provider: Any,
        reservation_id: str,
        reserved_tokens: int,
        reserved_cost: int,
    ) -> GatewayResult:
        provider_request = ProviderRequest(
            task_type=request.task_type,
            model_id=request.model_id,
            context=request.context,
            output_schema=request.output_schema,
            timeout_seconds=request.timeout_seconds,
            max_output_tokens=request.max_output_tokens,
        )

        # 8 - count now, so a crash mid-call cannot under-report an attempt.
        self._physical_attempts += 1
        result, timed_out, cancel_attempted, failure_reason = await self._call_provider(
            provider, provider_request, reservation_id, timeout=request.timeout_seconds
        )

        def _failure(reason_code: str, *, timed_out: bool = False) -> GatewayResult:
            self._ledger.release(reservation_id)
            return receipts.post_dispatch_failure(
                reason_code,
                reserved_tokens=reserved_tokens,
                reserved_cost=reserved_cost,
                timed_out=timed_out,
                cancel_attempted=cancel_attempted,
            )

        if result is None:
            gates.failed(GATE_DISPATCH, failure_reason)
            return _failure(failure_reason, timed_out=timed_out)

        # P4A-REV-F3: reject a result claiming a different provider/model.
        try:
            assert_provider_identity_matches(result.provider_id, result.model_id, request)
        except ProviderIdentityMismatchError:
            gates.failed(GATE_DISPATCH, ProviderIdentityMismatchError.reason_code)
            return _failure(ProviderIdentityMismatchError.reason_code)
        gates.passed(GATE_DISPATCH)

        # 10 - exact schema validation of returned JSON.
        try:
            validate_output(result.output, request.output_schema)
        except OutputSchemaError:
            gates.failed(GATE_OUTPUT, OutputSchemaError.reason_code)
            return _failure(OutputSchemaError.reason_code)
        gates.passed(GATE_OUTPUT)

        # 11 - commit actual usage exactly once.
        actual_tokens = int(result.usage.get("total_tokens", 0))
        actual_cost = int(result.usage.get("cost_usd_millis", 0))
        self._ledger.commit(
            reservation_id, actual_tokens=actual_tokens, actual_cost_usd_millis=actual_cost
        )
        return receipts.accepted(
            result.output,
            reserved_tokens=reserved_tokens,
            reserved_cost=reserved_cost,
            actual_tokens=actual_tokens,
            actual_cost=actual_cost,
            cancel_attempted=cancel_attempted,
        )

    @staticmethod
    async def _call_provider(
        provider: Any,
        provider_request: ProviderRequest,
        reservation_id: str,
        *,
        timeout: int,
    ) -> tuple[ProviderResult | None, bool, bool, str]:
        """One attempt, never retried: (result, timed_out, cancelled, reason)."""
        try:
            result = await asyncio.wait_for(
                provider.generate_structured_output(provider_request), timeout=timeout
            )
            return result, False, False, ""
        except asyncio.TimeoutError:
            try:  # best-effort cancel; failure here does not change the outcome
                await provider.cancel_request(reservation_id)
            except Exception:
                pass
            return None, True, True, ProviderTimeoutError.reason_code
        except Exception:
            # Raw exception text may echo credentials; keep only the reason code.
            return None, False, False, ProviderDispatchError.reason_code
