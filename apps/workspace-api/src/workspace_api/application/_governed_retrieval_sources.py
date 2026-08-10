"""P4-A1 governed retrieval - operational-corpus boundary and R3 stage-5
corpus resolution (SPEC R2/R4/R5/R7.3).

``SHIFT_CONFIRMED_OPERATIONS_V1`` and ``SHIFT_ADVISORY_MESSAGES_V1`` remain
``DEPENDENCY_BLOCKED`` in this tranche. This module's ONLY behavior for those
two corpora is to prove that fact and refuse to read or count any
canonical/Message record. It performs zero Ledger reads for either corpus -
the six ``operations_domain.retrieval_digests.*`` owners do not exist, and
this module MUST NOT import, alias, or invent one.

It also owns ``resolve_and_authorize_corpus``: the R3 stage-5 corpus half,
reachable only after every prior authorization stage passes. A client
``corpus_id`` string is matched against the closed :class:`CorpusId` registry
only here - never earlier, during R2 structural validation.
"""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action
from governed_retrieval.corpus import CorpusDescriptor, filters_within_descriptor, is_available, resolve_corpus
from governed_retrieval.enums import CorpusId, FinalOutcome, RequestFailureCode, RetrievalStage, StageOutcome, StageReasonCode
from governed_retrieval.evidence_models import RetrievalCountsV1, RetrievalStageReceiptV1
from governed_retrieval.lexical import TieBreakKey, version_sort_key
from governed_retrieval.request_models import GovernedRetrievalRequestV1
from governed_retrieval.result_models import RetrievalStoppedV1
from operations_domain.models import Shift
from retrieval_contracts.contract_models import RetrievalReadyV1

from workspace_api.application import _governed_retrieval_knowledge as knowledge
from workspace_api.application.assignment_scope import AssignmentScope, OperationalResourceNotFound


class AccessDenied(Exception):
    """Enumeration-safe denial at authentication, permission, or assignment."""


def authorize_permission(principal: Principal) -> None:
    """R3 stage 3 - permission authorization only. Raises
    :class:`AccessDenied` on denial; performs no assignment or corpus access."""
    try:
        require_action(principal, "retrieval.query")
    except CvfDenied as exc:
        raise AccessDenied("permission denied") from exc


def authorize_assignment(
    *, shift_ids: tuple[str, ...], principal: Principal, assignment_scope: AssignmentScope, unit: Any,
) -> tuple[Shift, ...]:
    """R3 stage 4 - per-shift assignment admission, inside the single shared
    ``unit``. Raises :class:`AccessDenied` on any failure, with no
    distinguishing detail between missing shift and missing assignment
    (SPEC R3 enumeration-safety requirement)."""
    admitted: list[Shift] = []
    for shift_id in shift_ids:
        try:
            shift_uuid = UUID(shift_id)
        except ValueError as exc:
            raise AccessDenied("shift not accessible") from exc
        try:
            shift = assignment_scope.require_shift(shift_uuid, principal, unit=unit)
        except OperationalResourceNotFound as exc:
            raise AccessDenied("shift not accessible") from exc
        admitted.append(shift)
    return tuple(admitted)


def tie_break_for(ready: RetrievalReadyV1) -> TieBreakKey:
    """R6 - the exact seven-part tie-break key for one admitted candidate."""
    record_or_source_id = ready.source_reference.record_id or ready.source_reference.source_id
    version_value = version_sort_key(
        ready.source_reference.version.kind.value,
        ready.source_reference.version.integer_version,
        ready.source_reference.version.source_version_string,
    )
    return TieBreakKey(
        truth_class=ready.truth_class.value,
        record_type=ready.source_reference.record_type.value,
        record_or_source_id=record_or_source_id,
        source_version_kind=ready.source_reference.version.kind.value,
        source_version_value=version_value,
        field_selector=ready.field_selector,
        chunk_id=ready.chunk_id,
    )

_MAX_ADMITTED_CANDIDATES = 2000


def check_stopped(ctx, stage: RetrievalStage):
    """F11 - real stop-check at a pipeline checkpoint. Evaluates local
    monotonic elapsed time against ``configured_timeout_ms`` (never a remote
    call) and calls the caller-supplied ``metadata.cancellation_check()``.
    Returns the ``RetrievalStoppedV1`` variant (never a partial projection)
    if either fires, else ``None`` to continue."""
    elapsed_ms = (time.monotonic() - ctx._monotonic_start) * 1000
    if elapsed_ms >= ctx.metadata.configured_timeout_ms:
        ctx.timed_out = True
        ctx.tracker.record(stage, StageOutcome.FAIL, StageReasonCode.RETRIEVAL_TIMEOUT, ctx.counts)
        ctx.tracker.fill_not_run(ctx.counts)
        ctx.tracker.record(RetrievalStage.RECEIPT_EMITTED, StageOutcome.PASS, None, ctx.counts)
        receipt = ctx.build_receipt(FinalOutcome.RETRIEVAL_TIMEOUT, (), None)
        return RetrievalStoppedV1(outcome=FinalOutcome.RETRIEVAL_TIMEOUT, receipt=receipt)
    if ctx.metadata.cancellation_check():
        ctx.cancelled = True
        ctx.tracker.record(stage, StageOutcome.FAIL, StageReasonCode.RETRIEVAL_CANCELLED, ctx.counts)
        ctx.tracker.fill_not_run(ctx.counts)
        ctx.tracker.record(RetrievalStage.RECEIPT_EMITTED, StageOutcome.PASS, None, ctx.counts)
        receipt = ctx.build_receipt(FinalOutcome.RETRIEVAL_CANCELLED, (), None)
        return RetrievalStoppedV1(outcome=FinalOutcome.RETRIEVAL_CANCELLED, receipt=receipt)
    return None


class StageTracker:
    """Accumulates the exact eleven ordered stage receipts (receipt appendix).
    Shared bookkeeping used by every R3 pipeline stage; lives here (rather
    than in ``_governed_retrieval_admission``) only because that module is at
    its file-size ceiling - this class has no corpus-specific behavior."""

    _ORDER = list(RetrievalStage)

    def __init__(self) -> None:
        self._by_stage: dict[RetrievalStage, RetrievalStageReceiptV1] = {}

    def record(self, stage, outcome, reason_code, counts) -> None:
        # Idempotent-safe: a caller that already recorded a PASS for the
        # current stage (e.g. MATCHED_AND_RANKED) and then immediately calls
        # a negative-outcome helper for that SAME stage must not produce two
        # entries - the later call always wins.
        self._by_stage[stage] = RetrievalStageReceiptV1(
            stage=stage, outcome=outcome, reason_code=reason_code, safe_counts=counts
        )

    def fill_not_run(self, counts: RetrievalCountsV1) -> None:
        for stage in self._ORDER:
            if stage not in self._by_stage:
                self.record(stage, StageOutcome.NOT_RUN, None, counts)

    def finalize(self) -> tuple[RetrievalStageReceiptV1, ...]:
        return tuple(self._by_stage[stage] for stage in self._ORDER)


class CorpusUnavailable(Exception):
    """Raised for any corpus whose descriptor state is not available."""


def ensure_available(descriptor: CorpusDescriptor) -> None:
    """R4 - a blocked corpus returns ``CORPUS_UNAVAILABLE`` after
    authorization, without reading or counting any source.

    This is the ONLY function this module exposes for the two operational
    corpora: it never reaches a Ledger call, a digest function, or a source
    read for ``SHIFT_CONFIRMED_OPERATIONS_V1``/``SHIFT_ADVISORY_MESSAGES_V1``,
    both of which are always ``DEPENDENCY_BLOCKED`` in this tranche.
    """
    if not is_available(descriptor):
        raise CorpusUnavailable(descriptor.corpus_id)


def is_operational_corpus(corpus_id: CorpusId) -> bool:
    """True for either of the two dependency-blocked operational corpora."""
    return corpus_id in (CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1, CorpusId.SHIFT_ADVISORY_MESSAGES_V1)


class CorpusResolutionFailed(Exception):
    """R3 stage 5 - carries the exact closed R2 code for a post-authorization
    corpus/filter failure (``CORPUS_ID_INVALID`` or ``FILTER_WIDENS_SCOPE``)."""

    def __init__(self, code: RequestFailureCode) -> None:
        self.code = code
        super().__init__(str(code))


def resolve_and_authorize_corpus(request: GovernedRetrievalRequestV1) -> tuple[CorpusId, CorpusDescriptor]:
    """R3 stage 5 (corpus half) - only reachable after every prior stage
    passes. Resolves the wire ``corpus_id`` string against the closed
    registry and enforces filter narrowing (R4) and the exact per-corpus
    shift-id cardinality. A client value never becomes a path, URL, or
    adapter import - it is matched against :class:`CorpusId`'s closed set
    only.

    Raises :class:`CorpusResolutionFailed` with ``CORPUS_ID_INVALID`` for an
    unknown id, or ``FILTER_WIDENS_SCOPE`` for a well-formed filter outside
    the authorized corpus descriptor.
    """
    try:
        corpus_id = CorpusId(request.corpus_id)
    except ValueError as exc:
        raise CorpusResolutionFailed(RequestFailureCode.CORPUS_ID_INVALID) from exc
    descriptor = resolve_corpus(corpus_id)

    expected_shift_count = 1 if corpus_id == CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1 else None
    if expected_shift_count is not None and len(request.filters.shift_ids) != expected_shift_count:
        raise CorpusResolutionFailed(RequestFailureCode.FILTER_WIDENS_SCOPE)

    if not filters_within_descriptor(
        descriptor, request.filters.record_types, request.filters.truth_classes,
        request.filters.lifecycle_statuses,
    ):
        raise CorpusResolutionFailed(RequestFailureCode.FILTER_WIDENS_SCOPE)
    return corpus_id, descriptor


def admit_knowledge_candidates(ctx):
    """R5/R6/R10 - SOURCES_READ then P3C_ADMITTED for the Project Knowledge
    corpus: read every admissible manifest entry, build its P3-C
    ``RetrievalReadyV1`` plus its P3-A candidate sensitivity, dedupe by
    ``chunk_id`` (byte-identical duplicates collapse; unequal-byte duplicates
    are ``INVARIANT_FAILURE``), and enforce the 2000-candidate ceiling with a
    typed ``RETRIEVAL_LIMIT_EXCEEDED`` - never a silent truncation.

    Returns ``(admitted, None)`` on success, where ``admitted`` is a list of
    ``(RetrievalReadyV1, manifest_entry, sensitivity)`` tuples, or
    ``(None, negative_result)`` on a P3C_ADMITTED-stage failure.
    """
    try:
        entries = knowledge.list_admissible_knowledge_entries(ctx.metadata.repository_root)
    except knowledge.ManifestEntryLimitExceeded:
        return None, ctx.negative(
            RetrievalStage.SOURCES_READ, StageOutcome.FAIL,
            StageReasonCode.RETRIEVAL_LIMIT_EXCEEDED, FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED,
        )
    except Exception:  # noqa: BLE001 - RR3-F2: every ordinary initial-
        # admission failure (unreadable/malformed manifest, or any other
        # ordinary exception from manifest validation) is a safe typed
        # CORPUS_UNAVAILABLE, never a raw exception escaping the application
        # boundary. Only BaseException (process termination, KeyboardInterrupt)
        # is ever allowed to propagate; exception text never enters the result.
        return None, ctx.negative(
            RetrievalStage.SOURCES_READ, StageOutcome.FAIL,
            StageReasonCode.CORPUS_UNAVAILABLE, FinalOutcome.CORPUS_UNAVAILABLE,
        )
    ctx.counts = ctx.counts.model_copy(update={"source_records_read": len(entries)})
    ctx.tracker.record(RetrievalStage.SOURCES_READ, StageOutcome.PASS, None, ctx.counts)

    context = knowledge.ProjectKnowledgeExecutionContext(
        repository_root=ctx.metadata.repository_root, control_bundle=ctx.metadata.control_bundle,
        now=ctx.started_at_utc, dedupe_context=ctx.metadata.dedupe_context,
        quarantine_route=ctx.metadata.quarantine_route, anchor_shift=None, anchor_principal_user_id="",
    )
    ready_by_chunk: dict[str, tuple[RetrievalReadyV1, dict, str]] = {}
    for entry in entries:
        try:
            built = knowledge.build_ready_contract(entry, context)
        except knowledge.DocumentLimitExceeded:
            return None, ctx.negative(
                RetrievalStage.P3C_ADMITTED, StageOutcome.FAIL,
                StageReasonCode.RETRIEVAL_LIMIT_EXCEEDED, FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED,
            )
        except Exception:  # noqa: BLE001 - RR3-F2: an ordinary exception from
            # P3-A refine()/P3-C construct_retrieval_contract() during initial
            # candidate construction is a safe typed CORPUS_UNAVAILABLE, never
            # a raw exception escaping the boundary; text never surfaces.
            return None, ctx.negative(
                RetrievalStage.P3C_ADMITTED, StageOutcome.FAIL,
                StageReasonCode.CORPUS_UNAVAILABLE, FinalOutcome.CORPUS_UNAVAILABLE,
            )
        if built is None:
            continue
        ready, sensitivity = built
        existing = ready_by_chunk.get(ready.chunk_id)
        if existing is not None:
            if existing[0].model_dump_json() != ready.model_dump_json():
                return None, ctx.negative(
                    RetrievalStage.P3C_ADMITTED, StageOutcome.FAIL,
                    StageReasonCode.INVARIANT_FAILURE, FinalOutcome.INVARIANT_FAILURE,
                )
            continue
        ready_by_chunk[ready.chunk_id] = (ready, entry, sensitivity)

    admitted = list(ready_by_chunk.values())
    ctx.counts = ctx.counts.model_copy(update={"candidates_admitted": len(admitted)})
    ctx.tracker.record(RetrievalStage.P3C_ADMITTED, StageOutcome.PASS, None, ctx.counts)

    if len(admitted) > _MAX_ADMITTED_CANDIDATES:
        return None, ctx.negative(
            RetrievalStage.P3C_ADMITTED, StageOutcome.FAIL,
            StageReasonCode.RETRIEVAL_LIMIT_EXCEEDED, FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED,
        )
    return admitted, None
