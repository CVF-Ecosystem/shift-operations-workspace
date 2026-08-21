"""``GovernedRAG.execute`` - the P4-A2 pure-package pipeline owner (SPEC
R3/R4/R5/R7/R8/R9/R10/R11/R12/R13/R14/R15).

Receives ONLY a positive P4-A1 ``EvidenceAvailableV1`` result (never a raw
query, corpus or credential) plus a strict :class:`~governed_rag.models.
GovernedRagRequestV1` and an injected, already-configured concrete
``ai_gateway.service.AIGateway`` instance. Implements DESIGN steps 4-13:
recompute/verify P4-A1 bindings, build/validate the ephemeral index, fuse
lexical+semantic scores, screen for injection, minimize, assemble context,
dispatch the gateway at most once, validate the answer, and emit a sanitized
receipt. Never imports a provider SDK, HTTP client, environment, database, or
the application layer (see ``pyproject.toml``'s exact dependency list)."""

from __future__ import annotations

from ai_gateway.models import (
    AIMode,
    BudgetFacts,
    Classification,
    ContextFacts,
    GatewayRequest,
    Placement,
    TerminationFacts,
    digest_of,
)
from ai_gateway.service import AIGateway
from governed_retrieval.result_models import EvidenceAvailableV1

from . import index as index_mod
from . import injection as injection_mod
from . import minimization as minimization_mod
from .context import assemble_context
from .errors import (
    BindingMismatchError,
    ContextBudgetExceededError,
    GatewayNotAcceptedError,
    InjectionBlockedError,
    MinimizationFailedError,
    OutputValidationFailedError,
    PlacementRefusedError,
    RetrievalNotPositiveError,
    ScopeMismatchError,
    ScopeWideningError,
    StaleIndexError,
)
from .index import verify_bindings
from .hashing import (
    answer_digest as compute_answer_digest,
    normalized_query_digest,
    output_schema_digest as compute_output_schema_digest,
    score_policy_digest,
)
from .models import LEXICAL_WEIGHT, SCORE_POLICY_ID, SEMANTIC_WEIGHT, GovernedRagRequestV1, rank_projections
from .receipts import GovernedRagReceiptV1, RagFinalOutcome, RagStage
from .semantic import ENCODER_VERSION, LEXICON_DIGEST_SHA256
from .validation import (
    ANSWER_JSON_SCHEMA,
    AnswerStatus,
    GovernedRagAnswerV1,
    ReceiptContext,
    parse_answer,
    validate_citation_membership,
)

_OUTPUT_SCHEMA_DIGEST_FN = lambda: compute_output_schema_digest(ANSWER_JSON_SCHEMA)  # noqa: E731

_SCORE_POLICY_DIGEST = score_policy_digest(
    lexical_weight=LEXICAL_WEIGHT, semantic_weight=SEMANTIC_WEIGHT, policy_id=SCORE_POLICY_ID
)


class GovernedRagOutcome:
    """Wraps either a final :class:`~governed_rag.validation.
    GovernedRagAnswerV1` (when ANSWERED) or ``None`` (every other outcome)
    alongside the sanitized receipt, so a caller never needs to inspect an
    exception to learn the outcome of a completed (non-raising) execution."""

    __slots__ = ("answer", "receipt")

    def __init__(self, *, answer: GovernedRagAnswerV1 | None, receipt: GovernedRagReceiptV1) -> None:
        self.answer = answer
        self.receipt = receipt


class GovernedRAG:
    """SPEC R12 - holds an injected, already-configured concrete
    ``AIGateway`` instance and calls its ``execute`` method zero or one time
    per :meth:`execute` call. Owns no provider dispatch of its own.

    ``placement`` (P4A2-REV-F3/Amendment 1) is a strict, provider-neutral
    fact bound at construction from the caller's real adapter/dispatch
    wiring - REQUIRED, no default, never a per-request ``execute()`` field,
    so a caller cannot default-or-relabel an external dispatch as LOCAL.
    ``ai_gateway.service.AIGateway.execute`` independently re-verifies this
    same fact against the provider's own registered placement pre-dispatch."""

    def __init__(self, gateway: AIGateway, *, placement: Placement) -> None:
        self._gateway = gateway
        self._placement = placement

    @property
    def gateway(self) -> AIGateway:
        """Exposed for object-identity tests (SPEC R12) - never used by this
        class itself to construct a second gateway."""
        return self._gateway

    @property
    def placement(self) -> Placement:
        """Exposed for identity/mismatch tests (P4A2-REV-F3) - the fixed
        placement this engine's gateway physically dispatches to."""
        return self._placement

    async def execute(
        self, *, request: GovernedRagRequestV1, retrieval_result, authorization_scope_digest_sha256: str
    ) -> GovernedRagOutcome:
        """DESIGN steps 4-13. ``retrieval_result`` is the exact P4-A1
        ``GovernedRetrievalResultV1`` union member the application layer
        obtained; only ``EvidenceAvailableV1`` proceeds past step 3/4 - every
        other member short-circuits here with zero gateway attempts (SPEC
        R4). ``authorization_scope_digest_sha256`` is the exact P4-A1
        authorization-scope digest the caller already computed/verified for
        this principal/shift/workspace, passed through unchanged (this
        package never recomputes authorization from raw principal input -
        that is P4-A1's own boundary).
        """
        nq_digest = normalized_query_digest(request.query)
        base = ReceiptContext(nq_digest=nq_digest, retrieval_result=retrieval_result)

        if not isinstance(retrieval_result, EvidenceAvailableV1):  # DESIGN step 3
            return self._negative(base, RagStage.RETRIEVAL_BOUND, RagFinalOutcome.RETRIEVAL_NOT_POSITIVE, RetrievalNotPositiveError.reason_code)

        try:  # P4A2-REV-F4 - independent corpus/authorization-scope equality,
            # before any index/minimization/context/gateway work.
            index_mod.verify_request_scope(
                result=retrieval_result, request_corpus_id=request.corpus_id,
                authorization_scope_digest_sha256=authorization_scope_digest_sha256,
            )
        except ScopeMismatchError as exc:
            return self._negative(base, RagStage.RETRIEVAL_BOUND, RagFinalOutcome.SCOPE_MISMATCH, exc.reason_code)

        try:  # DESIGN step 4 - never trust caller relabeling.
            verify_bindings(retrieval_result)
        except ScopeWideningError as exc:
            return self._negative(base, RagStage.RETRIEVAL_BOUND, RagFinalOutcome.SCOPE_WIDENING_REJECTED, exc.reason_code)
        except BindingMismatchError as exc:
            return self._negative(base, RagStage.RETRIEVAL_BOUND, RagFinalOutcome.BINDING_MISMATCH, exc.reason_code)

        return await self._execute_positive(request, retrieval_result, base, authorization_scope_digest_sha256)

    def _negative(self, base: ReceiptContext, terminal_stage: RagStage, final_outcome: RagFinalOutcome, reason_code: str, **kwargs) -> GovernedRagOutcome:
        """Shared negative-outcome wrapper: fills in the three fixed
        encoder/lexicon/policy digests every receipt needs, so pipeline call
        sites only ever pass what varies per stage."""
        receipt = base.build(
            terminal_stage=terminal_stage, final_outcome=final_outcome, reason_code=reason_code,
            encoder_version=ENCODER_VERSION, lexicon_digest_sha256=LEXICON_DIGEST_SHA256,
            score_policy_digest_sha256=_SCORE_POLICY_DIGEST,
            output_schema_digest_sha256_fn=_OUTPUT_SCHEMA_DIGEST_FN, **kwargs,
        )
        return GovernedRagOutcome(answer=None, receipt=receipt)

    async def _execute_positive(
        self, request: GovernedRagRequestV1, retrieval_result: EvidenceAvailableV1,
        base: ReceiptContext, authorization_scope_digest_sha256: str,
    ) -> GovernedRagOutcome:
        projections = retrieval_result.projections

        # DESIGN steps 5-6 - build the fresh ephemeral index and immediately
        # self-validate it against the exact same granted projections (this
        # composition function always builds fresh, so validation against
        # itself is a determinism proof; callers/tests may separately inject
        # a prebuilt index through governed_rag.index.validate_index).
        built_index = index_mod.build_index(
            authorization_scope_digest_sha256=authorization_scope_digest_sha256,
            corpus_id=request.corpus_id, projections=projections,
        )
        try:
            index_mod.validate_index(
                built_index, authorization_scope_digest_sha256=authorization_scope_digest_sha256,
                corpus_id=request.corpus_id, projections=projections,
            )
        except StaleIndexError as exc:
            return self._negative(base, RagStage.INDEX_VALIDATED, RagFinalOutcome.STALE_INDEX, exc.reason_code, index=built_index)

        ranked = rank_projections(request.query, projections, built_index)  # DESIGN step 7

        # DESIGN step 8 - injection screening.
        citation_texts = tuple((r.citation_id, r.content_snippet) for r in ranked)
        clean_ids, omissions = injection_mod.screen(citation_texts)
        pre_ids = tuple(r.citation_id for r in ranked)
        if not clean_ids:
            return self._negative(
                base, RagStage.INJECTION_SCREENED, RagFinalOutcome.INJECTION_BLOCKED, InjectionBlockedError.reason_code,
                index=built_index, injection_omissions=omissions, pre_injection_ids=pre_ids,
            )
        clean_records = [r for r in ranked if r.citation_id in set(clean_ids)]

        # DESIGN step 9 - extractive minimization.
        minimization_input = tuple((r.citation_id, r.content_snippet) for r in clean_records)
        min_proof, minimized_records = minimization_mod.minimize_all(records=minimization_input, query=request.query)
        if not minimized_records:
            return self._negative(
                base, RagStage.MINIMIZED, RagFinalOutcome.MINIMIZATION_FAILED, MinimizationFailedError.reason_code,
                index=built_index, injection_omissions=omissions, pre_injection_ids=pre_ids,
                post_injection_ids=tuple(clean_ids), minimization_proof=min_proof,
            )

        # DESIGN step 10 - context assembly.
        limits = retrieval_result.future_context_handoff.applied_limits
        try:
            assembled = assemble_context(
                evidence_records=minimized_records, budget_policy=request.context_budget_policy,
                handoff_max_projection_records=limits.max_projection_records,
                handoff_max_serialized_utf8_bytes=limits.max_serialized_utf8_bytes,
                handoff_max_estimated_input_tokens=limits.max_estimated_input_tokens,
            )
        except ContextBudgetExceededError as exc:
            return self._negative(
                base, RagStage.CONTEXT_ASSEMBLED, RagFinalOutcome.CONTEXT_BUDGET_EXCEEDED, exc.reason_code,
                index=built_index, injection_omissions=omissions, pre_injection_ids=pre_ids,
                post_injection_ids=tuple(clean_ids), minimization_proof=min_proof,
            )

        granted_post_omission = tuple(r.citation_id for r in minimized_records)

        # P4A2-REV-F3 - EXTERNAL placement requires this execution's own
        # positive minimization proof; refuse BEFORE dispatch, zero calls.
        if self._placement is Placement.EXTERNAL and min_proof.retained_count < 1:
            return self._negative(
                base, RagStage.CONTEXT_ASSEMBLED, RagFinalOutcome.PLACEMENT_REFUSED, PlacementRefusedError.reason_code,
                index=built_index, injection_omissions=omissions, pre_injection_ids=pre_ids,
                post_injection_ids=tuple(clean_ids), minimization_proof=min_proof, assembled=assembled,
            )

        # DESIGN step 11 - at most one gateway dispatch.
        gateway_request = self._build_gateway_request(request, assembled)
        result = await self._gateway.execute(gateway_request)

        common = dict(
            index=built_index, injection_omissions=omissions, pre_injection_ids=pre_ids,
            post_injection_ids=tuple(clean_ids), minimization_proof=min_proof,
            assembled=assembled, gateway_request=gateway_request,
            physical_attempt_count=result.receipt.provider_attempts,
        )
        if not result.accepted:
            return self._negative(
                base, RagStage.GATEWAY_DISPATCHED, RagFinalOutcome.GATEWAY_NOT_ACCEPTED,
                result.receipt.reason_code or GatewayNotAcceptedError.reason_code, **common,
            )

        # DESIGN step 12 - answer/citation validation.
        try:
            answer = parse_answer(result.output or {})
            validate_citation_membership(answer, granted_post_omission)
        except OutputValidationFailedError as exc:
            return self._negative(base, RagStage.ANSWER_VALIDATED, RagFinalOutcome.OUTPUT_VALIDATION_FAILED, exc.reason_code, **common)

        # DESIGN step 13 - positive, sanitized receipt.
        final_outcome = RagFinalOutcome.ANSWERED if answer.status is AnswerStatus.ANSWER else RagFinalOutcome.ABSTAINED
        receipt = base.build(
            index=built_index, pre_injection_ids=pre_ids, post_injection_ids=tuple(clean_ids),
            injection_omissions=omissions, minimization_proof=min_proof, assembled=assembled,
            gateway_request=gateway_request, terminal_stage=None, final_outcome=final_outcome, reason_code="",
            physical_attempt_count=result.receipt.provider_attempts,
            gateway_receipt_output_digest_sha256=result.receipt.output_digest or None,
            provider_response_digest_sha256=result.receipt.output_digest or None,
            validated_answer_digest_sha256=compute_answer_digest(answer.model_dump(mode="python")),
            encoder_version=ENCODER_VERSION, lexicon_digest_sha256=LEXICON_DIGEST_SHA256,
            score_policy_digest_sha256=_SCORE_POLICY_DIGEST, output_schema_digest_sha256_fn=_OUTPUT_SCHEMA_DIGEST_FN,
        )
        return GovernedRagOutcome(answer=answer, receipt=receipt)

    def _build_gateway_request(self, request: GovernedRagRequestV1, assembled) -> GatewayRequest:
        context_dict = {
            "instruction_contract": assembled.instruction_contract.model_dump(mode="python"),
            "evidence_records": [r.model_dump(mode="python") for r in assembled.evidence_records],
        }
        context_facts = ContextFacts(
            classification=Classification.INTERNAL, redaction_applied=True, minimization_proven=True,
            evidence_count=len(assembled.evidence_records),
            estimated_input_tokens=assembled.facts.context_estimated_tokens,
            context_digest=digest_of(context_dict),
        )
        budget_facts = BudgetFacts(
            per_request_token_limit=max(assembled.facts.context_estimated_tokens, 1) + request.max_output_tokens,
            daily_budget_usd_millis=0, monthly_budget_usd_millis=0, spent_today_usd_millis=0,
            spent_month_usd_millis=0, estimated_cost_usd_millis=0, on_budget_exceeded="hard_stop",
            kill_switch_enabled=False,
        )
        return GatewayRequest(
            # P4A2-REV-F3: real bound placement, never hardcoded/per-call.
            task_type="governed_rag_answer", ai_mode=AIMode.EXTERNAL_AI, provider_id=request.provider_id,
            model_id=request.model_id, placement=self._placement, context=context_dict,
            output_schema=ANSWER_JSON_SCHEMA, context_facts=context_facts, budget_facts=budget_facts,
            termination_facts=TerminationFacts(), timeout_seconds=request.timeout_seconds,
            max_output_tokens=request.max_output_tokens,
        )


__all__ = ["GovernedRAG", "GovernedRagOutcome"]
