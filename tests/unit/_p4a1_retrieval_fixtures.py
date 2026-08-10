"""Shared P4-A1 governed retrieval test fixtures.

CVF control: test-only. No provider, network, or external database access -
every fixture here builds explicit, in-process, deterministic values.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from cvf_runtime.identity import Principal
from operations_domain.models import Shift
from refinery_bridge.controls import ControlBundleV1
from refinery_bridge.input_models import DedupeContextV1, QuarantineRouteV1
from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.application.governed_retrieval import GovernedRetrievalExecutionMetadataV1
from workspace_api.auth.tokens import create_access_token
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger

REPO_ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)

DEFAULT_BUDGET = {
    "max_projection_records": 4,
    "max_snippet_codepoints": 1024,
    "max_snippet_utf8_bytes": 3072,
    "max_serialized_utf8_bytes": 16384,
    "max_estimated_input_tokens": 4096,
}


def control_bundle() -> ControlBundleV1:
    return ControlBundleV1(
        envelope_schema_version="envelope-v1",
        normalization_rules_version="normalization-v1",
        terminology_rules_version="terminology-v1",
        classification_rules_version="classification-v1",
        conflict_rules_version="conflict-v1",
        redaction_rules_version="redaction-v1",
        dedupe_rules_version="dedupe-v1",
        quality_rules_version="quality-v1",
        candidate_admission_rules_version="admission-v1",
    )


def dedupe_context(now: datetime = NOW) -> DedupeContextV1:
    return DedupeContextV1(
        scope_id="p4a1-scope", window_start=now - timedelta(days=1), window_end=now, records=()
    )


def quarantine_route() -> QuarantineRouteV1:
    return QuarantineRouteV1(
        owner_id="quarantine-owner", sink_id="quarantine-sink", policy_version="quarantine-v1",
        retention_days=30, sink_available=True,
    )


def _fixed_uuid4_factory(*, _counter: list[int] = [0]) -> Any:
    """RR1-F9 - a deterministic-but-distinct uuid4 factory: real UUIDv4
    values (so ``version == 4`` checks still pass), never a single reused
    id. Each call returns a genuinely fresh ``uuid4()`` - the service itself
    still owns exactly-twice-per-execution invocation; this fixture merely
    supplies a real, injectable callable rather than a fixed constant."""

    def factory() -> UUID:
        return uuid4()

    return factory


def _fixed_utc_now_factory(*, now: datetime) -> Any:
    """RR1-F9 - a deterministic clock callable: every call returns the same
    fixed ``now`` unless a test supplies its own sequence. Golden/deterministic
    tests inject their own callable via the ``utc_now`` override instead."""

    def clock() -> datetime:
        return now

    return clock


def execution_metadata(
    *, now: datetime = NOW, repository_root: Path = REPO_ROOT, timeout_ms: int = 5000, **overrides
) -> GovernedRetrievalExecutionMetadataV1:
    fields = dict(
        # RR1-F9/Amendment-2 5.6: injected callables, never pre-allocated
        # receipt_id/retrieval_correlation_id/now values. uuid4_factory
        # returns a fresh real UUIDv4 on every call (the service invokes it
        # exactly twice); utc_now defaults to a fixed clock returning `now`
        # for deterministic non-golden tests, but a caller-supplied override
        # (e.g. a genuinely advancing sequence) always wins via **overrides.
        uuid4_factory=_fixed_uuid4_factory(),
        utc_now=_fixed_utc_now_factory(now=now),
        repository_root=repository_root,
        control_bundle=control_bundle(),
        dedupe_context=dedupe_context(now),
        quarantine_route=quarantine_route(),
        configured_timeout_ms=timeout_ms,
        # F11 - explicit test-default: never cancelled unless a test
        # overrides this callable.
        cancellation_check=lambda: False,
    )
    fields.update(overrides)
    return GovernedRetrievalExecutionMetadataV1(**fields)


class AssignedWorkspace:
    """A ledger with one shift, one assigned viewer, and an assignment scope."""

    def __init__(self) -> None:
        self.ledger = InMemoryLedger()
        self.shift = Shift(name="Day", starts_at=NOW, ends_at=NOW + timedelta(hours=8))
        self.ledger.create_shift(self.shift)
        self.ledger.add_user(User(user_id="op1", username="op1", password_hash="x", role="viewer"))
        self.ledger.add_user(
            User(user_id="sup1", username="sup1", password_hash="x", role="shift_supervisor")
        )
        self.ledger.add_assignment(
            ShiftAssignment(shift_id=self.shift.shift_id, user_id="op1", assigned_by="sup1")
        )
        self.principal = Principal(user_id="op1", role="viewer")
        self.scope = AssignmentScope(self.ledger)
        self._outsider: Principal | None = None

    def bearer_token(self) -> str:
        """A real, verifiable JWT for ``self.principal`` - governed retrieval
        never accepts an already-constructed ``Principal`` directly, only a
        wire bearer token it verifies itself (F1)."""
        return create_access_token(self.principal)

    def outsider(self) -> Principal:
        """Idempotent: creates the unassigned ``op2`` user at most once, so
        callers may mix ``outsider()`` and ``outsider_token()`` freely."""
        if self._outsider is None:
            self.ledger.add_user(User(user_id="op2", username="op2", password_hash="x", role="viewer"))
            self._outsider = Principal(user_id="op2", role="viewer")
        return self._outsider

    def outsider_token(self) -> str:
        return create_access_token(self.outsider())


def request_body(
    *,
    query: str = "governance",
    corpus_id: str = "PROJECT_KNOWLEDGE_LOCAL_V1",
    shift_ids: tuple[str, ...] = (),
    budget: dict | None = None,
    result_limit: int | None = None,
) -> dict:
    body = {
        "query": query,
        "corpus_id": corpus_id,
        "filters": {"shift_ids": shift_ids},
        "context_budget": dict(budget or DEFAULT_BUDGET),
    }
    if result_limit is not None:
        body["result_limit"] = result_limit
    return body


def _negative_terminal(outcome):
    """RR2-F5 - the exact single terminal (stage, StageOutcome, reason_code)
    each negative FinalOutcome requires, mirroring receipt_models.py's
    _EXPECTED_TERMINAL grammar (never all-PASS)."""
    from governed_retrieval.enums import FinalOutcome, RetrievalStage, StageOutcome, StageReasonCode

    table = {
        FinalOutcome.INVALID_REQUEST: (RetrievalStage.REQUEST_VALIDATED, StageOutcome.FAIL, StageReasonCode.QUERY_INVALID),
        FinalOutcome.ACCESS_DENIED: (RetrievalStage.AUTHENTICATED, StageOutcome.DENY, StageReasonCode.AUTHENTICATION_FAILED),
        FinalOutcome.CORPUS_UNAVAILABLE: (RetrievalStage.CORPUS_RESOLVED, StageOutcome.FAIL, StageReasonCode.CORPUS_UNAVAILABLE),
        FinalOutcome.NO_EVIDENCE: (RetrievalStage.MATCHED_AND_RANKED, StageOutcome.FAIL, StageReasonCode.NO_EVIDENCE),
        FinalOutcome.STALE_EVIDENCE: (RetrievalStage.REVALIDATED, StageOutcome.FAIL, StageReasonCode.STALE_EVIDENCE),
        FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED: (RetrievalStage.SOURCES_READ, StageOutcome.FAIL, StageReasonCode.RETRIEVAL_LIMIT_EXCEEDED),
        FinalOutcome.RETRIEVAL_TIMEOUT: (RetrievalStage.SOURCES_READ, StageOutcome.FAIL, StageReasonCode.RETRIEVAL_TIMEOUT),
        FinalOutcome.RETRIEVAL_CANCELLED: (RetrievalStage.SOURCES_READ, StageOutcome.FAIL, StageReasonCode.RETRIEVAL_CANCELLED),
        FinalOutcome.CONTEXT_BUDGET_EXCEEDED: (RetrievalStage.PROJECTED, StageOutcome.FAIL, StageReasonCode.CONTEXT_BUDGET_EXCEEDED),
        FinalOutcome.INVARIANT_FAILURE: (RetrievalStage.P3C_ADMITTED, StageOutcome.FAIL, StageReasonCode.INVARIANT_FAILURE),
    }
    return table[outcome]


def minimal_negative_receipt(outcome: str):
    """RR1-F6/RR1-F9/RR2-F5 shared helper: a structurally valid, real-hash
    negative receipt for ``outcome`` with the exact outcome-specific
    first-terminal-then-NOT_RUN stage grammar (never all-PASS) - used by
    multiple test files to construct/reach every result variant without
    duplicating the receipt-hash recomputation boilerplate in each one."""
    from governed_retrieval.enums import FinalOutcome, RetrievalStage, StageOutcome
    from governed_retrieval.evidence_models import RetrievalCountsV1, RetrievalStageReceiptV1, TerminationFactsV1
    from governed_retrieval.hashing import receipt_hash
    from governed_retrieval.receipt_models import RetrievalReceiptV1

    counts = RetrievalCountsV1(
        source_records_read=0, candidates_admitted=0, matches_ranked=0,
        selected_for_revalidation=0, stale_omitted=0, projections_emitted=0, projections_budget_omitted=0,
    )
    final_outcome = FinalOutcome(outcome)
    terminal_stage, terminal_outcome, terminal_reason = _negative_terminal(final_outcome)
    seen_terminal = False
    stages = []
    for s in RetrievalStage:
        if s == terminal_stage:
            stages.append(RetrievalStageReceiptV1(stage=s, outcome=terminal_outcome, reason_code=terminal_reason, safe_counts=counts))
            seen_terminal = True
        elif s == RetrievalStage.RECEIPT_EMITTED:
            stages.append(RetrievalStageReceiptV1(stage=s, outcome=StageOutcome.PASS, reason_code=None, safe_counts=counts))
        elif seen_terminal:
            stages.append(RetrievalStageReceiptV1(stage=s, outcome=StageOutcome.NOT_RUN, reason_code=None, safe_counts=counts))
        else:
            stages.append(RetrievalStageReceiptV1(stage=s, outcome=StageOutcome.PASS, reason_code=None, safe_counts=counts))
    fields = dict(
        contract_version="1.0", receipt_id=uuid4(), retrieval_correlation_id=uuid4(),
        started_at_utc=NOW, finished_at_utc=NOW, source_cutoff_utc=None, elapsed_ms=0,
        corpus_id=None, authorization_scope_digest_sha256=None, stages=tuple(stages),
        final_outcome=final_outcome, requested_limits=None, applied_limits=None, counts=counts,
        termination=TerminationFactsV1(configured_timeout_ms=1000, timed_out=False, cancelled=False),
        citation_ids=(), evidence_set_hash_sha256=None,
    )
    dump = RetrievalReceiptV1.model_construct(**fields, receipt_hash_sha256="0" * 64).model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    fields["receipt_hash_sha256"] = receipt_hash(dump)
    return RetrievalReceiptV1(**fields)
