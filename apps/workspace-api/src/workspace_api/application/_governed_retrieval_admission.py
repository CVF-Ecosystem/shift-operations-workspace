"""P4-A1 governed retrieval - R2/R3 admission: structural validation, then
authentication/permission/assignment authorization in exact order. Also owns
the eleven-stage receipt bookkeeping (:class:`StageTracker`) and the
per-execution negative-result/receipt helper (:class:`ExecutionContext`)
shared by every pipeline stage.

CVF control chain: this module performs stages 1-4 of SPEC R3. Corpus
resolution and any protected read happen only after every stage here passes
(stage 5, in ``_governed_retrieval_sources``/``_governed_retrieval_knowledge``).
No provider, network, product API, external database, or audit access.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from cvf_runtime.identity import Principal
from governed_retrieval.enums import CorpusId, FinalOutcome, RequestFailureCode, RetrievalStage, StageOutcome, StageReasonCode
from governed_retrieval.evidence_models import RetrievalCountsV1, RetrievalLimitsV1, TerminationFactsV1
from governed_retrieval.hashing import receipt_hash
from governed_retrieval.receipt_models import RetrievalReceiptV1
from governed_retrieval.request_models import GovernedRetrievalRequestV1, RequestValidationError
from governed_retrieval.result_models import (
    AccessDeniedV1,
    ContextBudgetExceededV1,
    CorpusUnavailableV1,
    GovernedRetrievalResultV1,
    InvalidRequestV1,
    InvariantFailureV1,
    NoEvidenceV1,
    RetrievalLimitExceededV1,
    RetrievalStoppedV1,
    StaleEvidenceV1,
)
from pydantic import ValidationError
from refinery_bridge.controls import ControlBundleV1
from refinery_bridge.input_models import DedupeContextV1, QuarantineRouteV1

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from workspace_api.application._governed_retrieval_sources import StageTracker
from workspace_api.dependencies import get_principal

NEGATIVE_VARIANTS = {
    FinalOutcome.INVALID_REQUEST: InvalidRequestV1,
    FinalOutcome.ACCESS_DENIED: AccessDeniedV1,
    FinalOutcome.CORPUS_UNAVAILABLE: CorpusUnavailableV1,
    FinalOutcome.NO_EVIDENCE: NoEvidenceV1,
    FinalOutcome.STALE_EVIDENCE: StaleEvidenceV1,
    FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED: RetrievalLimitExceededV1,
    FinalOutcome.CONTEXT_BUDGET_EXCEEDED: ContextBudgetExceededV1,
    FinalOutcome.INVARIANT_FAILURE: InvariantFailureV1,
}


@dataclass(frozen=True)
class GovernedRetrievalExecutionMetadataV1:
    """Explicit execution metadata for one governed retrieval call. There is
    no production default for any field - the caller (a future route, or a
    test) must supply all of them; a missing required field fails closed at
    construction time (a plain Python ``TypeError``, not a silent default).

    RR1-F9/Amendment-2 5.6: ``receipt_id``/``retrieval_correlation_id`` and a
    single reused ``now`` are NOT accepted here as already-allocated caller
    values. Instead ``uuid4_factory`` is called by the service exactly twice
    (never by a test/caller directly) to allocate two distinct UUIDv4
    identities before R2, and ``utc_now`` is called independently at three
    points (start before R2, source cutoff after a source snapshot, finish at
    receipt emission) - never one timestamp reused. Both are injectable so
    golden tests can supply deterministic sequences.
    """

    uuid4_factory: Any
    utc_now: Any
    repository_root: Path
    control_bundle: ControlBundleV1
    dedupe_context: DedupeContextV1
    quarantine_route: QuarantineRouteV1
    configured_timeout_ms: int
    # F11 - explicit, caller-supplied cancellation predicate (no production
    # default: a caller that does not want cancellation support must pass
    # ``lambda: False`` explicitly, never receive a silent one). Checked
    # locally at pipeline checkpoints; never a remote/network call.
    cancellation_check: Any
    workspace_id: str = "shift-operations-workspace"


def empty_counts() -> RetrievalCountsV1:
    return RetrievalCountsV1(
        source_records_read=0, candidates_admitted=0, matches_ranked=0,
        selected_for_revalidation=0, stale_omitted=0, projections_emitted=0,
        projections_budget_omitted=0,
    )


def requested_limits(request: GovernedRetrievalRequestV1) -> RetrievalLimitsV1:
    return RetrievalLimitsV1(
        result_limit=request.result_limit,
        max_projection_records=request.context_budget.max_projection_records,
        max_snippet_codepoints=request.context_budget.max_snippet_codepoints,
        max_snippet_utf8_bytes=request.context_budget.max_snippet_utf8_bytes,
        max_serialized_utf8_bytes=request.context_budget.max_serialized_utf8_bytes,
        max_estimated_input_tokens=request.context_budget.max_estimated_input_tokens,
    )


@dataclass
class ExecutionContext:
    """Mutable per-execution state. RR1-F9: ``receipt_id``/
    ``retrieval_correlation_id``/``started_at_utc`` are allocated ONCE here
    by calling injected ``uuid4_factory`` (twice) and ``utc_now`` (once) -
    never a caller-pre-allocated value. ``source_cutoff``/``finished_at`` are
    each captured by their own later, independent ``utc_now`` call."""

    metadata: GovernedRetrievalExecutionMetadataV1
    tracker: StageTracker
    counts: RetrievalCountsV1
    requested: RetrievalLimitsV1 | None
    corpus_id: CorpusId | None = None
    auth_digest: str | None = None
    applied_limits: RetrievalLimitsV1 | None = None
    # R7/R9 - local monotonic clock only (no remote call); used to measure
    # real, non-zero ``elapsed_ms`` instead of a caller-supplied constant.
    _monotonic_start: float = field(default_factory=time.monotonic)
    timed_out: bool = False
    cancelled: bool = False
    receipt_id: Any = field(init=False)
    retrieval_correlation_id: Any = field(init=False)
    started_at_utc: datetime = field(init=False)
    source_cutoff_utc: datetime | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        # Service-owned allocation: exactly two uuid4_factory() calls and one
        # utc_now() call, both before R2 - never accepted as already-
        # allocated values from the caller.
        self.receipt_id = self.metadata.uuid4_factory()
        self.retrieval_correlation_id = self.metadata.uuid4_factory()
        self.started_at_utc = self.metadata.utc_now()

    def mark_source_cutoff(self) -> None:
        """R9 - capture source_cutoff_utc independently, only after a real
        source snapshot has happened; never reused from started_at_utc."""
        self.source_cutoff_utc = self.metadata.utc_now()

    def negative(self, stage, outcome_status, reason, final_outcome) -> GovernedRetrievalResultV1:
        self.tracker.record(stage, outcome_status, reason, self.counts)
        self.tracker.fill_not_run(self.counts)
        # Every returned receipt is successfully emitted response data - the
        # RECEIPT_EMITTED stage always records PASS, independent of the
        # retrieval outcome itself (SPEC/receipt-appendix R9).
        self.tracker.record(RetrievalStage.RECEIPT_EMITTED, StageOutcome.PASS, None, self.counts)
        receipt = self.build_receipt(final_outcome, (), None)
        return NEGATIVE_VARIANTS[final_outcome](receipt=receipt)

    def build_receipt(
        self, final_outcome: FinalOutcome, citation_ids: tuple[str, ...], evidence_hash: str | None
    ) -> RetrievalReceiptV1:
        elapsed_ms = max(0, round((time.monotonic() - self._monotonic_start) * 1000))
        # RR1-F9 - finished_at_utc is a THIRD, independent utc_now() call at
        # receipt emission, never the reused start/cutoff timestamp.
        finished_at = self.metadata.utc_now()
        base = dict(
            contract_version="1.0",
            receipt_id=self.receipt_id,
            retrieval_correlation_id=self.retrieval_correlation_id,
            started_at_utc=self.started_at_utc,
            finished_at_utc=finished_at,
            source_cutoff_utc=self.source_cutoff_utc,
            elapsed_ms=elapsed_ms,
            # Appendix nullability timing: corpus_id is populated only once
            # CORPUS_RESOLVED has actually recorded PASS; auth digest only
            # once every assignment stage has passed. self.corpus_id/
            # self.auth_digest are set by the pipeline exactly at those
            # points, never earlier - a negative outcome recorded before
            # CORPUS_RESOLVED=PASS therefore always carries corpus_id=None.
            corpus_id=self.corpus_id if self._corpus_resolved_passed() else None,
            authorization_scope_digest_sha256=self.auth_digest,
            stages=self.tracker.finalize(),
            final_outcome=final_outcome,
            requested_limits=self.requested,
            applied_limits=self.applied_limits,
            counts=self.counts,
            termination=TerminationFactsV1(
                configured_timeout_ms=self.metadata.configured_timeout_ms,
                timed_out=self.timed_out,
                cancelled=self.cancelled,
            ),
            citation_ids=citation_ids,
            evidence_set_hash_sha256=evidence_hash,
        )
        dump = RetrievalReceiptV1.model_construct(**base, receipt_hash_sha256="0" * 64).model_dump(mode="python")
        dump.pop("receipt_hash_sha256")
        return RetrievalReceiptV1(**base, receipt_hash_sha256=receipt_hash(dump))

    def _corpus_resolved_passed(self) -> bool:
        stage = self.tracker._by_stage.get(RetrievalStage.CORPUS_RESOLVED)
        return stage is not None and stage.outcome == StageOutcome.PASS


class RequestInvalid(Exception):
    """Structural request validation failure; carries the exact R2 code."""

    def __init__(self, code: RequestFailureCode) -> None:
        self.code = code
        super().__init__(str(code))


def validate_structure(raw_body: Any) -> GovernedRetrievalRequestV1:
    """R3 stage 1 - bounded structural validation with zero protected reads.

    Raises :class:`RequestInvalid` with the exact R2 failure code. Must never
    call the ledger, the corpus registry, or any other protected surface. No
    raw exception (``TypeError``, ``KeyError``, or any other non-Pydantic,
    non-:class:`RequestValidationError` failure raised by a malformed input
    shape) may escape this function - every failure is classified to one of
    the eight closed R2 codes.
    """
    if not isinstance(raw_body, dict):
        raise RequestInvalid(RequestFailureCode.REQUEST_SHAPE_INVALID)
    if "correlation_id" in raw_body:
        raise RequestInvalid(RequestFailureCode.REQUEST_SHAPE_INVALID)
    try:
        request = GovernedRetrievalRequestV1.model_validate(raw_body)
    except RequestValidationError as exc:
        raise RequestInvalid(exc.code) from exc
    except ValidationError as exc:
        raise RequestInvalid(_classify_validation_error(exc)) from exc
    except RequestInvalid:
        raise
    except Exception as exc:  # noqa: BLE001 - final JSON-wire-safe backstop
        raise RequestInvalid(RequestFailureCode.REQUEST_SHAPE_INVALID) from exc
    return request


def _classify_validation_error(exc: ValidationError) -> RequestFailureCode:
    # Precedence order matters (R2 "Structural validation runs in the listed
    # precedence order"): a message-embedded RequestFailureCode raised by one
    # of our own before/after validators (query normalization,
    # ContextBudgetV1/RetrievalFiltersV1 raising RequestValidationError, whose
    # .args[0] is the code's str()) always takes priority over a field-loc
    # guess, because pydantic reports model-level validator failures with an
    # empty loc.
    known_codes = {code.value: code for code in RequestFailureCode}
    for error in exc.errors(include_input=False, include_url=False):
        message = str(error.get("msg", ""))
        for code_name, code in known_codes.items():
            if code_name in message:
                return code
    for error in exc.errors(include_input=False, include_url=False):
        loc = error.get("loc", ())
        field = str(loc[0]) if loc else ""
        if field == "query":
            return RequestFailureCode.QUERY_INVALID
        if field == "corpus_id":
            return RequestFailureCode.CORPUS_ID_INVALID
        if field == "filters":
            return RequestFailureCode.FILTER_INVALID
        if field == "result_limit":
            return RequestFailureCode.RESULT_LIMIT_INVALID
        if field == "context_budget":
            return RequestFailureCode.CONTEXT_BUDGET_INVALID
    return RequestFailureCode.REQUEST_SHAPE_INVALID


class AuthenticationFailed(Exception):
    """R3 stage 2 - the supplied bearer token did not verify."""


def authenticate(bearer_token: str) -> Principal:
    """R3 stage 2 - resolve the calling :class:`Principal` by calling the
    canonical dependency surface ``workspace_api.dependencies.get_principal``
    with an explicit ``HTTPAuthorizationCredentials`` built from
    ``bearer_token`` - never a direct ``decode_access_token`` call, and never
    an already-constructed :class:`Principal` supplied by a caller.

    Raises :class:`AuthenticationFailed` for a missing, malformed, expired,
    or mis-signed token (``get_principal`` raising ``HTTPException``).
    """
    if not isinstance(bearer_token, str) or not bearer_token:
        raise AuthenticationFailed("missing bearer token")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=bearer_token)
    try:
        return get_principal(credentials)
    except HTTPException as exc:
        raise AuthenticationFailed("invalid bearer token") from exc


# R3 stages 3/4 (authorize_permission, authorize_assignment) live in
# _governed_retrieval_sources to stay within this module's file-size ceiling;
# they have no corpus-specific behavior, matching that module's existing
# StageTracker placement rationale.
