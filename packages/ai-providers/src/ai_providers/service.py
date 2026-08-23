"""``ProviderModeService.execute`` - the sole P4-B mode-selection entry point
(SPEC R2/R3/R6).

Exact order: (1) request validation - the strict ``ProviderModeRequestV1``
model already validated at construction, plus mode-string recognition here,
wrapped so an unexpected exception still reaches typed ``REQUEST_INVALID``
(P4B-REV-F4.2); (2) mode selection - dispatch on ``AIMode``, an unknown
string refuses first; (3) local policy (``RULES_ONLY``) or external identity
binding (``EXTERNAL_AI``) - which also consults the load-bearing
:class:`~ai_providers.registry.ProviderAdapterRegistry` (P4B-REV-F1/F3)
before any delegation; (4) execution/delegation - local rule evaluation, or
exactly one call to the injected gateway; (5) output validation - the real
``ai_gateway.validation`` schema check, folded into rule evaluation for
RULES_ONLY and implicit in the gateway's own acceptance for EXTERNAL_AI; (6)
a strict result envelope pairing the releasable output with a sanitized
receipt (P4B-REV-F2). Each call reaches exactly one terminal
:class:`~ai_providers.models.ProviderModeOutcome`.

Never imports a provider SDK, HTTP client, low-level network module,
environment, filesystem, database, or the workspace application layer
(SPEC R10).
"""

from __future__ import annotations

from ai_gateway.models import AIMode, GatewayRequest, digest_of

from .errors import ProviderNotRegisteredError
from .models import (
    ProviderKind,
    ProviderModeOutcome,
    ProviderModeRequestV1,
    ProviderModeResultV1,
    build_receipt,
    build_result,
)
from .no_ai import evaluate_no_ai
from .protocols import InjectedGateway
from .registry import ProviderAdapterRegistry
from .rules_only import RuleSetV1, evaluate_rules

_VALID_MODES = {mode.value for mode in AIMode}


def _refuse_external(base: dict, reason_code: str, *, provider_id: str = "", model_id: str = "") -> ProviderModeResultV1:
    """A zero-call EXTERNAL_IDENTITY_MISMATCH result (every pre-dispatch
    EXTERNAL_AI refusal shares this exact shape)."""
    receipt = build_receipt(
        **base, outcome=ProviderModeOutcome.EXTERNAL_IDENTITY_MISMATCH,
        reason_code=reason_code, provider_id=provider_id, model_id=model_id,
    )
    return build_result(output=None, receipt=receipt)


class ProviderModeService:
    """Owns mode selection for one execution. Holds the load-bearing
    :class:`~ai_providers.registry.ProviderAdapterRegistry` (P4B-REV-F1) and
    an optionally injected gateway (SPEC R6) it calls at most once per
    :meth:`execute`; never constructs a second gateway and never calls an
    ``AIProvider`` directly.
    """

    def __init__(
        self,
        *,
        rule_set: RuleSetV1,
        registry: ProviderAdapterRegistry | None = None,
        gateway: InjectedGateway | None = None,
    ) -> None:
        self._rule_set = rule_set
        # P4B-REV-F1: default to an EMPTY registry, never to "no check at
        # all" - an empty registry still refuses every EXTERNAL_AI target as
        # unregistered, so omitting this constructor argument can never
        # accidentally widen into the old, non-load-bearing behavior.
        self._registry = registry if registry is not None else ProviderAdapterRegistry()
        self._gateway = gateway

    @property
    def gateway(self) -> InjectedGateway | None:
        """Exposed for object-identity tests - never used internally to
        construct a second gateway."""
        return self._gateway

    @property
    def registry(self) -> ProviderAdapterRegistry:
        """Exposed for object-identity tests - never used internally to
        construct a second registry."""
        return self._registry

    async def execute(
        self, *, request: ProviderModeRequestV1, started_at: str, finished_at: str
    ) -> ProviderModeResultV1:
        # P4B-REV-F4-R1: a request that reached this call already passed
        # ProviderModeRequestV1's own validators at construction, but a
        # model_construct-bypassed instance (or any other way invalid
        # content reaches here) must never surface a raw, untyped exception,
        # and must never silently proceed on content that is not genuinely
        # valid. Round 1 only guarded the digest computation itself; that
        # left a model_construct-bypassed request whose facts contain a
        # JSON-invalid value (e.g. a tuple) "digestible" (json.dumps happily
        # serializes some non-JSON Python values, like tuples, as if they
        # were lists) but not actually valid, so it fell through past this
        # guard into normal mode dispatch. The fix is to fully reconstruct
        # and revalidate the ENTIRE request from its own primitive dump
        # before doing anything else - the same discipline already applied
        # to MockAuthorizationV1 in mock_provider.py - so a request that is
        # merely digest-safe but not genuinely valid is still caught here.
        try:
            revalidated = ProviderModeRequestV1.model_validate(request.model_dump(mode="python"))
            request_digest = digest_of(revalidated.model_dump(mode="python"))
            schema_digest = digest_of(revalidated.output_schema)
            request = revalidated
        except Exception:
            fallback_base = dict(
                request_id=getattr(request, "request_id", "") or "unknown",
                policy_version=getattr(request, "policy_version", "") or "unknown",
                request_digest="0" * 64,
                output_schema_digest="0" * 64,
                ai_mode="UNKNOWN",
                started_at=started_at,
                finished_at=finished_at,
            )
            receipt = build_receipt(
                **fallback_base,
                outcome=ProviderModeOutcome.REQUEST_INVALID,
                reason_code="REQUEST_NOT_REVALIDATABLE",
            )
            return build_result(output=None, receipt=receipt)

        raw_ai_mode = request.ai_mode
        base = dict(
            request_id=request.request_id,
            policy_version=request.policy_version,
            request_digest=request_digest,
            output_schema_digest=schema_digest,
            started_at=started_at,
            finished_at=finished_at,
        )

        if raw_ai_mode not in _VALID_MODES:
            receipt = build_receipt(
                **base,
                ai_mode="UNKNOWN",
                outcome=ProviderModeOutcome.REQUEST_INVALID,
                reason_code="UNKNOWN_AI_MODE",
            )
            return build_result(output=None, receipt=receipt)

        base["ai_mode"] = raw_ai_mode
        mode = AIMode(raw_ai_mode)
        if mode is AIMode.NO_AI:
            return self._finish_no_ai(base)
        if mode is AIMode.RULES_ONLY:
            return self._finish_rules_only(base, request)
        return await self._finish_external_ai(base, request)

    def _finish_no_ai(self, base: dict) -> ProviderModeResultV1:
        outcome, reason = evaluate_no_ai()
        receipt = build_receipt(**base, outcome=outcome, reason_code=reason)
        return build_result(output=None, receipt=receipt)

    def _finish_rules_only(self, base: dict, request: ProviderModeRequestV1) -> ProviderModeResultV1:
        outcome, rule_id, _rule, output = evaluate_rules(
            self._rule_set,
            task_type=request.task_type,
            facts=request.facts,
            output_schema=request.output_schema,
        )
        output_digest = digest_of(output) if output is not None else ""
        ruleset_digest = digest_of(self._rule_set.digest_source())
        reason = "" if outcome is ProviderModeOutcome.RULES_MATCHED else outcome.value
        receipt = build_receipt(
            **base,
            outcome=outcome,
            reason_code=reason,
            rule_id=rule_id,
            output_digest=output_digest,
            ruleset_digest=ruleset_digest,
            rules_evaluated=len(self._rule_set.rules),
        )
        # P4B-REV-F2: the released output is the SAME isolated dict
        # evaluate_rules already deep-copied out of the winning rule's own
        # state (rules_only.evaluate_rules deep-copies before returning);
        # build_result deep-copies it again here so the envelope can never
        # alias back to internal rule-set state even indirectly.
        return build_result(output=output, receipt=receipt)

    async def _finish_external_ai(
        self, base: dict, request: ProviderModeRequestV1
    ) -> ProviderModeResultV1:
        nested = request.nested_gateway_request
        if nested is None:
            return _refuse_external(base, "MISSING_NESTED_GATEWAY_REQUEST")
        try:
            # R1: reconstruct from the primitive dump, never trust a
            # caller-attached instance as already validated.
            gateway_request = GatewayRequest.model_validate(nested)
        except Exception:
            return _refuse_external(base, "NESTED_GATEWAY_REQUEST_INVALID")

        mismatch = _identity_mismatch(request, gateway_request)
        if mismatch:
            return _refuse_external(
                base, mismatch, provider_id=gateway_request.provider_id, model_id=gateway_request.model_id
            )

        # P4B-REV-F1/F3: the load-bearing registry check - independent of
        # which P4-A ProviderRegistry the injected gateway itself holds, and
        # independent of any caller-supplied label. An unregistered
        # (provider_id, model_id) pair, or one registered with kind MOCK,
        # is refused here with zero gateway/provider calls. A caller cannot
        # get a MOCK-kind target dispatched through EXTERNAL_AI merely by
        # registering it directly in P4-A's own ProviderRegistry and never
        # telling P4-B's registry about it - "not registered in the P4-B
        # registry at all" is refused exactly like "registered as MOCK".
        ids = dict(provider_id=gateway_request.provider_id, model_id=gateway_request.model_id)
        try:
            metadata = self._registry.resolve(gateway_request.provider_id, gateway_request.model_id)
        except ProviderNotRegisteredError:
            return _refuse_external(base, "PROVIDER_NOT_REGISTERED", **ids)
        # P4B-REV-F1-R1: external delegation is permitted ONLY when the
        # registry-owned metadata is EXACTLY kind=EXTERNAL_GATEWAY AND
        # evidence_eligible=True - both conditions, both exact. Round 1 only
        # rejected kind=MOCK, which left every other wrong combination
        # (kind=EXTERNAL_GATEWAY/evidence_eligible=False,
        # kind=RULES_ONLY/evidence_eligible=True,
        # kind=NO_AI/evidence_eligible=True, and MOCK with
        # evidence_eligible=True - impossible to construct but excluded here
        # too for defence in depth) reaching the gateway. This single check
        # replaces the old MOCK-only check and is strictly narrower.
        if metadata.kind is not ProviderKind.EXTERNAL_GATEWAY or metadata.evidence_eligible is not True:
            return _refuse_external(base, "PROVIDER_NOT_EXTERNAL_GATEWAY_EVIDENCE_ELIGIBLE", **ids)
        if metadata.placement is not gateway_request.placement:
            return _refuse_external(base, "REGISTRY_PLACEMENT_MISMATCH", **ids)

        if self._gateway is None:
            return _refuse_external(base, "NO_GATEWAY_INJECTED", **ids)

        result = await self._gateway.execute(gateway_request)
        common = dict(
            provider_id=gateway_request.provider_id,
            model_id=gateway_request.model_id,
            gateway_calls=1,
            provider_attempts=result.receipt.provider_attempts,
        )
        if not result.accepted:
            receipt = build_receipt(
                **base,
                **common,
                outcome=ProviderModeOutcome.EXTERNAL_NOT_ACCEPTED,
                reason_code=result.receipt.reason_code or "GATEWAY_NOT_ACCEPTED",
            )
            return build_result(output=None, receipt=receipt)
        receipt = build_receipt(
            **base,
            **common,
            outcome=ProviderModeOutcome.EXTERNAL_ACCEPTED,
            reason_code="",
            output_digest=digest_of(result.output),
        )
        # P4B-REV-F2: preserve the gateway's own accepted output faithfully
        # (never re-derive or re-synthesize it) - build_result deep-copies
        # it so the envelope never aliases the GatewayResult's own dict.
        return build_result(output=result.output, receipt=receipt)


def _identity_mismatch(request: ProviderModeRequestV1, gateway_request: GatewayRequest) -> str:
    """SPEC R6 - the nested request's task/mode/provider/model/placement/
    schema/context-digest must equal the outer request's own explicitly
    declared binding facts (P4B-REV-F3); any mismatch OR any missing outer
    fact is a zero-call refusal reason code. A caller cannot satisfy SPEC R6
    by supplying a nested ``GatewayRequest`` alone without also declaring
    the same provider_id/model_id/placement/context_digest on the outer
    envelope - an unset outer fact is exactly as much a mismatch as a
    disagreeing one, since "the outer request never committed to a
    provider/model/placement/digest at all" is not a fact the nested
    request's own claims can satisfy on the outer request's behalf.
    """
    if gateway_request.task_type != request.task_type:
        return "TASK_TYPE_MISMATCH"
    if gateway_request.ai_mode is not AIMode.EXTERNAL_AI:
        return "NESTED_MODE_NOT_EXTERNAL_AI"
    if gateway_request.output_schema != request.output_schema:
        return "OUTPUT_SCHEMA_MISMATCH"
    if not request.provider_id or gateway_request.provider_id != request.provider_id:
        return "PROVIDER_ID_MISMATCH"
    if not request.model_id or gateway_request.model_id != request.model_id:
        return "MODEL_ID_MISMATCH"
    if request.placement is None or gateway_request.placement is not request.placement:
        return "PLACEMENT_MISMATCH"
    if (
        request.context_digest is None
        or gateway_request.context_facts.context_digest != request.context_digest
    ):
        return "CONTEXT_DIGEST_MISMATCH"
    return ""


__all__ = ["ProviderModeService"]
