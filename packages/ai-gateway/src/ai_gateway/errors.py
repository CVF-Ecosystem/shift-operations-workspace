"""Typed gateway errors and their receipt representation (SPEC R2/R4/R10).

Every error carries a stable ``reason_code`` so receipts and tests can assert an
outcome without parsing prose. No error message may embed prompt text, context
text, provider output, a credential, or raw provider error text; callers build
messages from safe identifiers only.

The rest of this module turns those reason codes into what ``service.py``
needs to build the sanitized ``GatewayReceipt`` SPEC R10 requires:
``GateRecorder`` accumulates gate outcomes in order and ``ReceiptBuilder``
turns them into a receipt. It lives here, not in ``service.py``, because a
receipt is fundamentally the typed record of *which errors did or did not
occur*, in order - the natural counterpart to the error vocabulary defined
above. The ``cvf_runtime`` policy adapters (``cost_policy_of`` and friends)
live in ``context.py`` alongside the other caller-facts-to-gate-input
adapters.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .fallback import build_rules_fallback
from .models import (
    FinalOutcome,
    GateOutcome,
    GateRecord,
    GatewayReceipt,
    GatewayRequest,
    GatewayResult,
    digest_of,
)


class GatewayError(RuntimeError):
    """Base class. ``reason_code`` is the stable, assertable outcome name."""

    reason_code = "GATEWAY_ERROR"

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail or self.reason_code)
        self.detail = detail


class InvalidRequestError(GatewayError):
    """Request/schema failed strict validation before any gate ran."""

    reason_code = "INVALID_REQUEST"


class AIModeDisabledError(GatewayError):
    """AI mode is NO_AI/RULES_ONLY, so no provider dispatch is permitted."""

    reason_code = "AI_MODE_DISABLED"


class NoEvidenceError(GatewayError):
    """No admitted evidence/context, so there is nothing to ground a call."""

    reason_code = "NO_EVIDENCE"


class ContextInadmissibleError(GatewayError):
    """Context failed classification/minimization admission (SPEC R5)."""

    reason_code = "CONTEXT_INADMISSIBLE"


class ContextDigestMismatchError(GatewayError):
    """Declared context_digest does not match the actual dispatched context
    (P4A-REV-F3: SPEC R10 requires the receipt to bind the real facts)."""

    reason_code = "CONTEXT_DIGEST_MISMATCH"


class ProviderIdentityMismatchError(GatewayError):
    """Returned provider/model id differs from the registered request
    (P4A-REV-F3: SPEC R10/R11 - a receipt must not claim false provenance)."""

    reason_code = "PROVIDER_IDENTITY_MISMATCH"


class EndpointOriginError(GatewayError):
    """``endpoint_origin`` is not a bare scheme+host string (P4A-REV-F3): a
    receipt must never persist userinfo, path, query, or a secret-shaped
    value that a caller passed as the gateway's origin."""

    reason_code = "ENDPOINT_ORIGIN_INVALID"


class PlacementDeniedError(GatewayError):
    """``assert_placement_allowed`` refused this classification/placement."""

    reason_code = "PLACEMENT_DENIED"


class ProviderPlacementMismatchError(GatewayError):
    """Request ``placement`` disagrees with the registered provider's own
    immutable ``Placement`` (P4A2-REV-F3/Amendment 1). Registry-owned:
    refused BEFORE context admission/data-scope, zero attempts, no
    reservation - a caller cannot relabel a provider's true placement. An
    unregistered provider/model keeps its distinct, later, unchanged
    refusal; this fires only when registered and placements disagree."""

    reason_code = "PROVIDER_PLACEMENT_MISMATCH"


class BudgetUnavailableError(GatewayError):
    """Reservation refused, or ``assert_within_budget`` refused the request."""

    reason_code = "BUDGET_UNAVAILABLE"


class TerminatedError(GatewayError):
    """``assert_not_terminated`` refused: kill switch or stop condition met."""

    reason_code = "TERMINATED"


class ProviderNotRegisteredError(GatewayError):
    """Provider id or model id is not explicitly registered (SPEC R11)."""

    reason_code = "PROVIDER_NOT_REGISTERED"


class ProviderDispatchError(GatewayError):
    """Provider call failed after one physical attempt. Never retried here."""

    reason_code = "PROVIDER_DISPATCH_FAILED"


class ProviderTimeoutError(ProviderDispatchError):
    """Provider call exceeded the configured timeout (SPEC R7)."""

    reason_code = "PROVIDER_TIMEOUT"


class OutputSchemaError(GatewayError):
    """Returned output is not an object satisfying the exact schema (R9)."""

    reason_code = "OUTPUT_SCHEMA_INVALID"


class UsageLedgerError(GatewayError):
    """Illegal ledger transition, e.g. double commit or double release (R6)."""

    reason_code = "USAGE_LEDGER_INVALID_TRANSITION"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GateRecorder:
    """Accumulates gate outcomes in execution order for the receipt (R3/R10)."""

    def __init__(self) -> None:
        self._records: list[GateRecord] = []

    def passed(self, gate: str) -> None:
        self._records.append(GateRecord(gate=gate, outcome=GateOutcome.PASS))

    def failed(self, gate: str, reason_code: str) -> None:
        self._records.append(
            GateRecord(gate=gate, outcome=GateOutcome.FAIL, reason_code=reason_code)
        )

    def as_tuple(self) -> tuple[GateRecord, ...]:
        return tuple(self._records)


class ReceiptBuilder:
    """Carries the fields common to every receipt for one execution (R10).

    Collapses what would otherwise be four near-duplicate methods, each
    repeating the same dozen keyword arguments, into one small object plus a
    handful of terminal-outcome calls.
    """

    def __init__(
        self,
        request: GatewayRequest,
        gates: GateRecorder,
        *,
        endpoint_origin: str,
        request_digest: str,
        schema_digest: str,
        started_at: str,
    ) -> None:
        self._request = request
        self._gates = gates
        self._endpoint_origin = endpoint_origin
        self._request_digest = request_digest
        self._schema_digest = schema_digest
        self._started_at = started_at

    def _receipt(self, **fields: Any) -> GatewayReceipt:
        request = self._request
        return GatewayReceipt(
            task_type=request.task_type,
            provider_id=request.provider_id,
            model_id=request.model_id,
            endpoint_origin=self._endpoint_origin,
            ai_mode=request.ai_mode,
            classification=request.context_facts.classification,
            placement=request.placement,
            request_digest=self._request_digest,
            context_digest=request.context_facts.context_digest,
            output_schema_digest=self._schema_digest,
            gates=self._gates.as_tuple(),
            started_at=self._started_at,
            finished_at=_now(),
            **fields,
        )

    def refused(self, reason_code: str) -> GatewayResult:
        """Zero-attempt pre-dispatch refusal (SPEC R4)."""
        receipt = self._receipt(
            output_digest="",
            final_outcome=FinalOutcome.REFUSED_PRE_DISPATCH,
            reason_code=reason_code,
            reserved_tokens=0,
            reserved_cost_usd_millis=0,
            reservation_released=False,
            timed_out=False,
            cancel_attempted=False,
            provider_attempts=0,
        )
        return GatewayResult(accepted=False, output=None, receipt=receipt)

    def fallback(self, reason_code: str, *, reservation_released: bool) -> GatewayResult:
        """Deterministic rules fallback in place of a provider call (R4)."""
        fallback_body = build_rules_fallback(self._request.task_type, reason_code)
        receipt = self._receipt(
            output_digest=digest_of(fallback_body),
            final_outcome=FinalOutcome.FALLBACK_RULES,
            reason_code=reason_code,
            reserved_tokens=0,
            reserved_cost_usd_millis=0,
            reservation_released=reservation_released,
            timed_out=False,
            cancel_attempted=False,
            provider_attempts=0,
        )
        return GatewayResult(accepted=False, output=None, receipt=receipt)

    def post_dispatch_failure(
        self,
        reason_code: str,
        *,
        reserved_tokens: int,
        reserved_cost: int,
        timed_out: bool,
        cancel_attempted: bool,
    ) -> GatewayResult:
        """One attempt made, but the result cannot be accepted (R7/R9)."""
        receipt = self._receipt(
            output_digest="",
            final_outcome=FinalOutcome.FAILED_POST_DISPATCH,
            reason_code=reason_code,
            reserved_tokens=reserved_tokens,
            reserved_cost_usd_millis=reserved_cost,
            reservation_released=True,
            timed_out=timed_out,
            cancel_attempted=cancel_attempted,
            provider_attempts=1,
        )
        return GatewayResult(accepted=False, output=None, receipt=receipt)

    def accepted(
        self,
        output: dict[str, Any],
        *,
        reserved_tokens: int,
        reserved_cost: int,
        actual_tokens: int,
        actual_cost: int,
        cancel_attempted: bool,
    ) -> GatewayResult:
        """The one-attempt, usage-committed accepted result (R9/R10)."""
        receipt = self._receipt(
            output_digest=digest_of(output),
            final_outcome=FinalOutcome.ACCEPTED,
            reason_code="",
            reserved_tokens=reserved_tokens,
            reserved_cost_usd_millis=reserved_cost,
            actual_tokens=actual_tokens,
            actual_cost_usd_millis=actual_cost,
            usage_committed=True,
            reservation_released=False,
            timed_out=False,
            cancel_attempted=cancel_attempted,
            provider_attempts=1,
        )
        return GatewayResult(accepted=True, output=output, receipt=receipt)
