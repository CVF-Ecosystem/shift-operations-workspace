"""P4-A1 governed retrieval - application orchestration (SPEC R1-R11).

Owns authenticated principal input, permission, assignment admission, server
registry access, Ledger/source reads, P3-A/P3-C construction, revalidation,
and pure-engine invocation. Executes R3's exact five-stage ordering:
(1) structural validation, (2) authentication through a verified bearer
token, (3) permission, (4) per-shift assignment inside the single
``Ledger.transaction()`` unit opened only after (2)+(3) pass, (5) corpus
resolution/filter narrowing. The same unit token threads through every
subsequent assignment/read/reload/final-check call. Calls neither
``AuditLog.record`` nor ``Ledger.append_audit``; receipts are response data
only. Registers no HTTP route.

Every execution input that would otherwise need a production default (clock,
ids, P3-A control bundle, dedupe context, quarantine route, timeout) is an
explicit, caller-supplied
:class:`_governed_retrieval_admission.GovernedRetrievalExecutionMetadataV1` -
absence is a caller programming error (fails closed via a raised exception),
never a silently substituted default.
"""

from __future__ import annotations

from typing import Any

from cvf_runtime.identity import Principal
from governed_retrieval.enums import FinalOutcome, RetrievalStage, StageOutcome, StageReasonCode
from governed_retrieval.hashing import authorization_scope_digest, citation_id, evidence_set_hash
from governed_retrieval.lexical import (
    normalize_and_tokenize_query,
    normalize_query_for_matching,
    normalize_with_offsets,
    rank_key,
    score_candidate,
)
from governed_retrieval.projection import (
    MAX_ESTIMATED_INPUT_TOKENS,
    MAX_PROJECTION_RECORDS,
    MAX_SERIALIZED_UTF8_BYTES,
    MAX_SNIPPET_CODEPOINTS,
    MAX_SNIPPET_UTF8_BYTES,
    estimate_tokens,
    serialized_projection_bytes,
)
from governed_retrieval.receipt_models import FutureContextHandoffV1
from governed_retrieval.request_models import GovernedRetrievalRequestV1
from governed_retrieval.result_models import EvidenceAvailableV1, GovernedRetrievalResultV1
from retrieval_contracts.contract_models import RetrievalReadyV1

from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.application import _governed_retrieval_admission as admission
from workspace_api.application import _governed_retrieval_knowledge as knowledge
from workspace_api.application import _governed_retrieval_revalidation as revalidation
from workspace_api.application import _governed_retrieval_sources as sources

# Re-exported for callers/tests that construct execution metadata.
GovernedRetrievalExecutionMetadataV1 = admission.GovernedRetrievalExecutionMetadataV1

def _applied_limits(request: GovernedRetrievalRequestV1):
    from governed_retrieval.evidence_models import RetrievalLimitsV1

    return RetrievalLimitsV1(
        result_limit=request.result_limit,
        max_projection_records=min(request.context_budget.max_projection_records, MAX_PROJECTION_RECORDS),
        max_snippet_codepoints=min(request.context_budget.max_snippet_codepoints, MAX_SNIPPET_CODEPOINTS),
        max_snippet_utf8_bytes=min(request.context_budget.max_snippet_utf8_bytes, MAX_SNIPPET_UTF8_BYTES),
        max_serialized_utf8_bytes=min(request.context_budget.max_serialized_utf8_bytes, MAX_SERIALIZED_UTF8_BYTES),
        max_estimated_input_tokens=min(request.context_budget.max_estimated_input_tokens, MAX_ESTIMATED_INPUT_TOKENS),
    )

def execute_governed_retrieval(
    *,
    raw_body: dict[str, Any],
    bearer_token: str,
    assignment_scope: AssignmentScope,
    ledger: Any,
    metadata: admission.GovernedRetrievalExecutionMetadataV1,
) -> GovernedRetrievalResultV1:
    """R3 - execute the exact five-stage governed retrieval pipeline once
    and return exactly one of the ten R11 result variants.

    ``bearer_token`` is the raw, not-yet-verified wire credential; R3 stage 2
    verifies it through ``workspace_api.dependencies.get_principal``.

    RR2-F3 - the service-owned execution context (two distinct uuid4_factory
    calls plus the start-time utc_now call) is allocated unconditionally
    FIRST, before R2 structural validation, for every safe result including
    INVALID_REQUEST - never after.
    """
    tracker = admission.StageTracker()
    counts = admission.empty_counts()
    ctx = admission.ExecutionContext(metadata=metadata, tracker=tracker, counts=counts, requested=None)

    try:
        request = admission.validate_structure(raw_body)
    except admission.RequestInvalid as exc:
        return ctx.negative(
            RetrievalStage.REQUEST_VALIDATED, StageOutcome.FAIL,
            StageReasonCode(exc.code.value), FinalOutcome.INVALID_REQUEST,
        )

    tracker.record(RetrievalStage.REQUEST_VALIDATED, StageOutcome.PASS, None, counts)
    ctx.requested = admission.requested_limits(request)

    # R3 stage 2 - authentication happens before any Ledger unit is opened.
    try:
        principal = admission.authenticate(bearer_token)
    except admission.AuthenticationFailed:
        # RR2-F4/Amendment 3 5.4 - authentication failure is exactly
        # AUTHENTICATED=DENY (an access-denial stage), never FAIL.
        return ctx.negative(
            RetrievalStage.AUTHENTICATED, StageOutcome.DENY,
            StageReasonCode.AUTHENTICATION_FAILED, FinalOutcome.ACCESS_DENIED,
        )
    ctx.tracker.record(RetrievalStage.AUTHENTICATED, StageOutcome.PASS, None, ctx.counts)

    # R3 stage 3 - permission, still before any Ledger unit is opened.
    try:
        sources.authorize_permission(principal)
    except sources.AccessDenied:
        return ctx.negative(
            RetrievalStage.PERMISSION_AUTHORIZED, StageOutcome.DENY,
            StageReasonCode.ACCESS_DENIED, FinalOutcome.ACCESS_DENIED,
        )
    ctx.tracker.record(RetrievalStage.PERMISSION_AUTHORIZED, StageOutcome.PASS, None, ctx.counts)

    # Exactly one Ledger unit, opened only after authentication + permission
    # pass, reused through assignment/reads/final checks (R3, R7).
    with ledger.transaction() as unit:
        return _execute_authorized(request, principal, assignment_scope, unit, ctx)

def _execute_authorized(
    request: GovernedRetrievalRequestV1, principal: Principal, assignment_scope: AssignmentScope,
    unit: Any, ctx: admission.ExecutionContext,
) -> GovernedRetrievalResultV1:
    # R3 stage 4 - per-shift assignment, inside the single shared unit.
    try:
        admitted_shifts = sources.authorize_assignment(
            shift_ids=request.filters.shift_ids, principal=principal, assignment_scope=assignment_scope, unit=unit
        )
    except sources.AccessDenied:
        return ctx.negative(
            RetrievalStage.ASSIGNMENT_AUTHORIZED, StageOutcome.DENY,
            StageReasonCode.ACCESS_DENIED, FinalOutcome.ACCESS_DENIED,
        )
    ctx.tracker.record(RetrievalStage.ASSIGNMENT_AUTHORIZED, StageOutcome.PASS, None, ctx.counts)

    admitted_shift_ids = tuple(sorted(str(s.shift_id) for s in admitted_shifts))
    ctx.auth_digest = authorization_scope_digest(ctx.metadata.workspace_id, principal.user_id, admitted_shift_ids)

    # R3 stage 5 - corpus resolution and filter narrowing, only reachable now.
    try:
        corpus_id, descriptor = sources.resolve_and_authorize_corpus(request)
    except sources.CorpusResolutionFailed as exc:
        return ctx.negative(
            RetrievalStage.CORPUS_RESOLVED, StageOutcome.FAIL,
            StageReasonCode(exc.code.value), FinalOutcome.INVALID_REQUEST,
        )

    if sources.is_operational_corpus(corpus_id):
        try:
            sources.ensure_available(descriptor)
        except sources.CorpusUnavailable:
            ctx.corpus_id = corpus_id
            return ctx.negative(
                RetrievalStage.CORPUS_RESOLVED, StageOutcome.FAIL,
                StageReasonCode.CORPUS_UNAVAILABLE, FinalOutcome.CORPUS_UNAVAILABLE,
            )
        raise AssertionError("operational corpus must remain dependency-blocked")

    ctx.corpus_id = corpus_id
    ctx.tracker.record(RetrievalStage.CORPUS_RESOLVED, StageOutcome.PASS, None, ctx.counts)
    # RR1-F7 - applied limits are set immediately after CORPUS_RESOLVED=PASS,
    # not deferred until projection.
    ctx.applied_limits = _applied_limits(request)

    # F11 - real local timeout/cancellation checkpoint before the (possibly
    # larger) source read and ranking work begins.
    stopped = sources.check_stopped(ctx, RetrievalStage.SOURCES_READ)
    if stopped is not None:
        return stopped
    return _execute_project_knowledge(request, principal, assignment_scope, unit, ctx, admitted_shifts)

def _execute_project_knowledge(
    request: GovernedRetrievalRequestV1, principal: Principal, assignment_scope: AssignmentScope,
    unit: Any, ctx: admission.ExecutionContext, admitted_shifts: tuple,
) -> GovernedRetrievalResultV1:
    admitted, failure = sources.admit_knowledge_candidates(ctx)
    if failure is not None:
        return failure
    # RR1-F7 - source_cutoff_utc is captured independently, right after this
    # real source snapshot, for positive/no-match/stale outcomes alike.
    ctx.mark_source_cutoff()

    normalized_query = normalize_query_for_matching(request.query)
    query_tokens = normalize_and_tokenize_query(request.query)

    ranked: list[tuple[tuple, RetrievalReadyV1, dict, str]] = []
    for ready, entry, sensitivity in admitted:
        normalized = normalize_with_offsets(ready.redacted_normalized_text)
        score = score_candidate(normalized_query, query_tokens, normalized.text)
        if score is None:
            continue
        ranked.append((rank_key(score, sources.tie_break_for(ready)), ready, entry, sensitivity))

    ctx.counts = ctx.counts.model_copy(update={"matches_ranked": len(ranked)})
    if not ranked:
        # RR1-F7 - the first terminal non-access operational stage is FAIL,
        # never PASS, for the NO_EVIDENCE outcome.
        return ctx.negative(RetrievalStage.MATCHED_AND_RANKED, StageOutcome.FAIL, StageReasonCode.NO_EVIDENCE, FinalOutcome.NO_EVIDENCE)
    ctx.tracker.record(RetrievalStage.MATCHED_AND_RANKED, StageOutcome.PASS, None, ctx.counts)

    ranked.sort(key=lambda item: item[0])
    selected = ranked[: request.result_limit]
    ctx.counts = ctx.counts.model_copy(update={"selected_for_revalidation": len(selected)})

    survivors, stale_count = revalidation.revalidate_knowledge_candidates(
        [(entry, ready, sensitivity) for _, ready, entry, sensitivity in selected],
        ctx.metadata.repository_root, ctx.metadata, ctx.started_at_utc,
    )
    ctx.counts = ctx.counts.model_copy(update={"stale_omitted": stale_count})
    if not survivors:
        # RR1-F7 - same FAIL-not-PASS rule for the STALE_EVIDENCE outcome.
        return ctx.negative(RetrievalStage.REVALIDATED, StageOutcome.FAIL, StageReasonCode.STALE_EVIDENCE, FinalOutcome.STALE_EVIDENCE)
    ctx.tracker.record(RetrievalStage.REVALIDATED, StageOutcome.PASS, None, ctx.counts)

    shift_ids = tuple(s.shift_id for s in admitted_shifts)
    if not revalidation.reverify_final_assignments(
        shift_ids=shift_ids, principal=principal, assignment_scope=assignment_scope, unit=unit
    ):
        return ctx.negative(
            RetrievalStage.REVALIDATED, StageOutcome.DENY, StageReasonCode.ACCESS_DENIED, FinalOutcome.ACCESS_DENIED
        )

    stopped = sources.check_stopped(ctx, RetrievalStage.PROJECTED)
    if stopped is not None:
        return stopped
    return _project_and_emit(request, ctx, survivors, normalized_query, query_tokens)

def _project_and_emit(
    request: GovernedRetrievalRequestV1, ctx: admission.ExecutionContext, survivors: list,
    normalized_query: str, query_tokens: tuple[str, ...],
) -> GovernedRetrievalResultV1:
    applied = ctx.applied_limits
    assembly = revalidation.assemble_projections(
        survivors, normalized_query=normalized_query, query_tokens=query_tokens,
        max_projection_records=applied.max_projection_records,
        max_snippet_codepoints=applied.max_snippet_codepoints,
        max_snippet_utf8_bytes=applied.max_snippet_utf8_bytes,
        max_serialized_utf8_bytes=applied.max_serialized_utf8_bytes,
        max_estimated_input_tokens=applied.max_estimated_input_tokens,
    )
    ctx.counts = ctx.counts.model_copy(update={"projections_budget_omitted": assembly.budget_omitted})
    if not assembly.projections:
        return ctx.negative(
            RetrievalStage.PROJECTED, StageOutcome.FAIL,
            StageReasonCode.CONTEXT_BUDGET_EXCEEDED, FinalOutcome.CONTEXT_BUDGET_EXCEEDED,
        )

    ctx.counts = ctx.counts.model_copy(update={"projections_emitted": len(assembly.projections)})
    ctx.tracker.record(RetrievalStage.PROJECTED, StageOutcome.PASS, None, ctx.counts)

    citation_ids = tuple(citation_id(dump["citation"]) for dump in assembly.citation_dumps)
    evidence_hash = evidence_set_hash([d["citation"] for d in assembly.citation_dumps], assembly.projection_dumps)

    # RR1-F8/RR2-F4 - FINAL stop checkpoint, immediately before constructing/
    # emitting the positive receipt/handoff. Recorded against PROJECTED
    # (never RECEIPT_EMITTED, which stays PASS always) - may overwrite the
    # PASS above since no positive projection returns on this path.
    stopped = sources.check_stopped(ctx, RetrievalStage.PROJECTED)
    if stopped is not None:
        return stopped

    ctx.tracker.record(RetrievalStage.RECEIPT_EMITTED, StageOutcome.PASS, None, ctx.counts)
    receipt = ctx.build_receipt(FinalOutcome.EVIDENCE_AVAILABLE, citation_ids, evidence_hash)
    serialized_bytes = serialized_projection_bytes(assembly.projection_dumps)
    snippet_codepoints = sum(p.snippet_end_codepoint - p.snippet_start_codepoint for p in assembly.projections)
    handoff = FutureContextHandoffV1(
        retrieval_receipt_hash_sha256=receipt.receipt_hash_sha256,
        evidence_set_hash_sha256=evidence_hash,
        citation_ids=citation_ids,
        classifications=("INTERNAL",),
        sensitivities=tuple(sorted({p.sensitivity for p in assembly.projections})),
        serialized_context_bytes=serialized_bytes,
        snippet_codepoints=snippet_codepoints,
        projection_count=len(assembly.projections),
        estimated_input_tokens=estimate_tokens(serialized_bytes),
        applied_limits=applied,
        elapsed_ms=receipt.elapsed_ms,
        configured_timeout_ms=ctx.metadata.configured_timeout_ms,
        timed_out=False,
        cancelled=False,
    )
    return EvidenceAvailableV1(
        receipt=receipt, projections=tuple(assembly.projections), future_context_handoff=handoff
    )
