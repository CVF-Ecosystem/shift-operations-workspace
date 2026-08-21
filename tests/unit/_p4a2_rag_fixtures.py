"""Shared P4-A2 governed-RAG test fixtures.

CVF control: test-only. No provider, network, or external database access -
every fixture here builds explicit, in-process, deterministic values.
Directly constructs a positive P4-A1 ``EvidenceAvailableV1`` result (rather
than exercising the whole P4-A1 pipeline, which ``_p4a1_retrieval_fixtures``
already covers) so P4-A2 unit tests can focus on P4-A2's own logic while
still exercising the REAL ``EvidenceAvailableV1``/``RetrievalReceiptV1``
Pydantic cross-validators - a forged fixture that violated those bindings
would fail to construct at all, which is itself part of the SPEC R4/R5
"forged positive rejected" proof surface used elsewhere.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from governed_retrieval.enums import RetrievalStage, StageOutcome
from governed_retrieval.evidence_models import (
    CitationV1,
    EvidenceProjectionV1,
    RetrievalCountsV1,
    RetrievalLimitsV1,
    RetrievalStageReceiptV1,
    TerminationFactsV1,
)
from governed_retrieval.hashing import citation_id as compute_citation_id
from governed_retrieval.hashing import evidence_set_hash as compute_evidence_set_hash
from governed_retrieval.hashing import receipt_hash as compute_retrieval_receipt_hash
from governed_retrieval.projection import estimate_tokens, serialized_projection_bytes
from governed_retrieval.receipt_models import FutureContextHandoffV1, RetrievalReceiptV1
from governed_retrieval.result_models import EvidenceAvailableV1
from retrieval_contracts.canonical import sha256_bytes
from retrieval_contracts.contract_models import VersionBindingV1
from retrieval_contracts.enums import RecordType, TruthClass, VersionKind

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
LIMITS = RetrievalLimitsV1(
    result_limit=10,
    max_projection_records=4,
    max_snippet_codepoints=1024,
    max_snippet_utf8_bytes=3072,
    max_serialized_utf8_bytes=16384,
    max_estimated_input_tokens=4096,
)


def make_citation(
    *,
    record_id: str = "pk-001",
    snippet: str = "Shift handover requires a written summary of open incidents.",
    truth_class: TruthClass = TruthClass.ADVISORY_SOURCE_EVIDENCE,
    field_selector: str = "document",
    version_string: str = "pin-1",
) -> tuple[CitationV1, str]:
    digest = sha256_bytes(snippet.encode("utf-8"))
    citation = CitationV1(
        chunk_id="a" * 64,
        content_digest_sha256=digest,
        source_digest_sha256="b" * 64,
        version=VersionBindingV1(kind=VersionKind.SOURCE_VERSION_STRING, source_version_string=version_string),
        truth_class=truth_class,
        record_type=RecordType.PROJECT_KNOWLEDGE,
        record_id=None,
        source_id=record_id,
        field_selector=field_selector,
        revalidation_token="c" * 64,
        source_cutoff_utc=NOW,
        snippet_digest_sha256=digest,
        snippet_start_codepoint=0,
        snippet_end_codepoint=len(snippet),
    )
    return citation, snippet


def make_projection(
    *,
    record_id: str = "pk-001",
    snippet: str = "Shift handover requires a written summary of open incidents.",
    truth_class: TruthClass = TruthClass.ADVISORY_SOURCE_EVIDENCE,
    field_selector: str = "document",
    version_string: str = "pin-1",
) -> EvidenceProjectionV1:
    citation, text = make_citation(
        record_id=record_id, snippet=snippet, truth_class=truth_class,
        field_selector=field_selector, version_string=version_string,
    )
    return EvidenceProjectionV1(
        citation=citation,
        truth_class=citation.truth_class,
        field_selector=citation.field_selector,
        sensitivity="LOW",
        content_snippet=text,
        snippet_start_codepoint=citation.snippet_start_codepoint,
        snippet_end_codepoint=citation.snippet_end_codepoint,
        snippet_digest_sha256=citation.snippet_digest_sha256,
        projection_complete=True,
    )


def _stage_receipts(counts: RetrievalCountsV1) -> tuple[RetrievalStageReceiptV1, ...]:
    return tuple(
        RetrievalStageReceiptV1(stage=stage, outcome=StageOutcome.PASS, reason_code=None, safe_counts=counts)
        for stage in RetrievalStage
    )


def evidence_available(
    *,
    projections: tuple[EvidenceProjectionV1, ...] | None = None,
    authorization_scope_digest_sha256: str = "d" * 64,
    corpus_id: str = "PROJECT_KNOWLEDGE_LOCAL_V1",
) -> EvidenceAvailableV1:
    """A fully valid, real-hash positive P4-A1 result with one or more
    projections, for tests that need a genuine ``EvidenceAvailableV1``
    rather than a forged/short-circuited one."""
    from governed_retrieval.enums import CorpusId, FinalOutcome

    if projections is None:
        projections = (make_projection(),)

    citation_dumps = [p.citation.model_dump(mode="python") for p in projections]
    projection_dumps = [p.model_dump(mode="python") for p in projections]
    evidence_hash = compute_evidence_set_hash(citation_dumps, projection_dumps)
    citation_ids = tuple(compute_citation_id(d) for d in citation_dumps)
    serialized_bytes = serialized_projection_bytes(projection_dumps)
    snippet_codepoints = sum(p.snippet_end_codepoint - p.snippet_start_codepoint for p in projections)

    counts = RetrievalCountsV1(
        source_records_read=len(projections), candidates_admitted=len(projections),
        matches_ranked=len(projections), selected_for_revalidation=len(projections),
        stale_omitted=0, projections_emitted=len(projections), projections_budget_omitted=0,
    )
    stages = _stage_receipts(counts)
    termination = TerminationFactsV1(configured_timeout_ms=5000, timed_out=False, cancelled=False)

    fields = dict(
        contract_version="1.0", receipt_id=uuid4(), retrieval_correlation_id=uuid4(),
        started_at_utc=NOW, finished_at_utc=NOW, source_cutoff_utc=NOW, elapsed_ms=0,
        corpus_id=CorpusId(corpus_id), authorization_scope_digest_sha256=authorization_scope_digest_sha256,
        stages=stages, final_outcome=FinalOutcome.EVIDENCE_AVAILABLE, requested_limits=LIMITS, applied_limits=LIMITS,
        counts=counts, termination=termination, citation_ids=citation_ids,
        evidence_set_hash_sha256=evidence_hash,
    )
    dump = RetrievalReceiptV1.model_construct(**fields, receipt_hash_sha256="0" * 64).model_dump(mode="python")
    dump.pop("receipt_hash_sha256")
    fields["receipt_hash_sha256"] = compute_retrieval_receipt_hash(dump)
    receipt = RetrievalReceiptV1(**fields)

    handoff = FutureContextHandoffV1(
        retrieval_receipt_hash_sha256=receipt.receipt_hash_sha256,
        evidence_set_hash_sha256=evidence_hash,
        citation_ids=citation_ids,
        classifications=("INTERNAL",),
        sensitivities=tuple(sorted({p.sensitivity for p in projections})),
        serialized_context_bytes=serialized_bytes,
        snippet_codepoints=snippet_codepoints,
        projection_count=len(projections),
        estimated_input_tokens=estimate_tokens(serialized_bytes),
        applied_limits=LIMITS,
        elapsed_ms=receipt.elapsed_ms,
        configured_timeout_ms=termination.configured_timeout_ms,
        timed_out=False,
        cancelled=False,
    )
    return EvidenceAvailableV1(receipt=receipt, projections=projections, future_context_handoff=handoff)


def negative_result(outcome: str):
    """Delegates to the shared P4-A1 fixture helper for every non-positive
    ``GovernedRetrievalResultV1`` variant, so P4-A2's SPEC R4 zero-attempt
    short-circuit tests exercise the SAME real, cross-validated negative
    receipts P4-A1's own test suite uses."""
    import importlib
    import sys
    from pathlib import Path

    tests_unit = str(Path(__file__).resolve().parent)
    if tests_unit not in sys.path:
        sys.path.insert(0, tests_unit)
    p4a1_fixtures = importlib.import_module("_p4a1_retrieval_fixtures")
    from governed_retrieval import result_models

    receipt = p4a1_fixtures.minimal_negative_receipt(outcome)
    variant_name = {
        "NO_EVIDENCE": "NoEvidenceV1",
        "ACCESS_DENIED": "AccessDeniedV1",
        "CORPUS_UNAVAILABLE": "CorpusUnavailableV1",
        "STALE_EVIDENCE": "StaleEvidenceV1",
        "RETRIEVAL_LIMIT_EXCEEDED": "RetrievalLimitExceededV1",
        "RETRIEVAL_TIMEOUT": "RetrievalStoppedV1",
        "RETRIEVAL_CANCELLED": "RetrievalStoppedV1",
        "CONTEXT_BUDGET_EXCEEDED": "ContextBudgetExceededV1",
        "INVALID_REQUEST": "InvalidRequestV1",
        "INVARIANT_FAILURE": "InvariantFailureV1",
    }[outcome]
    variant_cls = getattr(result_models, variant_name)
    if variant_name == "RetrievalStoppedV1":
        return variant_cls(receipt=receipt, outcome=outcome)
    return variant_cls(receipt=receipt)


def rag_request(**overrides):
    from governed_rag.models import ContextBudgetPolicyV1, GovernedRagRequestV1

    fields = dict(
        query="handover procedure",
        corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        provider_id="alibaba_dashscope_evidence_only",
        model_id="qwen-test-model",
        context_budget_policy=ContextBudgetPolicyV1(
            max_minimized_records=4,
            max_context_codepoints=1500,
            max_context_utf8_bytes=4000,
            max_context_estimated_tokens=900,
        ),
    )
    fields.update(overrides)
    return GovernedRagRequestV1(**fields)


def seeded_workspace():
    """A real InMemoryLedger with one shift and one assigned viewer, for the
    live-evidence runner's admitted path (``scripts/run_p4a2_governed_rag_
    live_evidence.py``). Constructing ``User``/``InMemoryLedger`` lives here,
    not in the runner or its support script, because
    ``tests/unit/test_operations_domain_boundary.py`` enforces a closed
    allowlist of production files (``apps``/``packages``/``scripts``) that
    may import ``User`` directly - ``tests/`` is outside that boundary."""
    from datetime import timedelta as _timedelta

    from cvf_runtime.identity import Principal
    from workspace_api.application.assignment_scope import AssignmentScope
    from workspace_api.auth.tokens import create_access_token
    from workspace_api.domain.models import ShiftAssignment, User
    from workspace_api.infrastructure.repository import InMemoryLedger
    from operations_domain.models import Shift

    ledger = InMemoryLedger()
    shift = Shift(name="Day", starts_at=NOW, ends_at=NOW + _timedelta(hours=8))
    ledger.create_shift(shift)
    ledger.add_user(User(user_id="op1", username="op1", password_hash="x", role="viewer"))
    ledger.add_user(User(user_id="sup1", username="sup1", password_hash="x", role="shift_supervisor"))
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    principal = Principal(user_id="op1", role="viewer")
    scope = AssignmentScope(ledger)
    token = create_access_token(principal)
    return ledger, shift, scope, token
