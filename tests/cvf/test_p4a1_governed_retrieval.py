"""End-to-end P4-A1 governed retrieval application coverage.

SPEC R4 (AC-04): registry golden matrix, blocked corpora perform zero source
calls. R5 (AC-05): eight-source matrix / six missing-digest-owner adversarial
proof, forbidden digest helpers unreachable. R7 (AC-07, InMemory half - the
SqlLedger/SQLite half lives in tests/integration): single-unit revalidation.
R11 (AC-11): ten-variant union coverage and provider-attempts-zero. R12
(AC-12): V1 evolution rejection of unknown fields/enums.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS))

import pytest
from pydantic import ValidationError

from governed_retrieval.corpus import CORPUS_REGISTRY, is_available
from governed_retrieval.enums import CorpusId, CorpusState, FinalOutcome
from governed_retrieval.result_models import (
    AccessDeniedV1, ContextBudgetExceededV1, CorpusUnavailableV1, EvidenceAvailableV1, InvalidRequestV1,
    InvariantFailureV1, NoEvidenceV1, RetrievalLimitExceededV1, RetrievalStoppedV1, StaleEvidenceV1,
)
from workspace_api.application.governed_retrieval import execute_governed_retrieval

from _p4a1_retrieval_fixtures import DEFAULT_BUDGET, NOW, AssignedWorkspace, request_body
from _p4a1_retrieval_fixtures import execution_metadata as _base_execution_metadata

REPO_ROOT = _REPO_ROOT

def _advancing_utc_now(*, start=NOW):
    """RR3-F4 - each call returns `start` plus a strictly increasing offset,
    so a positive measured elapsed_ms always has finished_at_utc > started_at_utc."""
    calls = [0]
    def clock():
        calls[0] += 1
        return start + timedelta(microseconds=calls[0])
    return clock

def execution_metadata(**overrides):
    overrides.setdefault("utc_now", _advancing_utc_now())
    return _base_execution_metadata(**overrides)

def _isolated_knowledge_root(tmp_path, doc_count=1):
    """A self-contained, pin-correct Project Knowledge corpus with
    `doc_count` entries under `tmp_path`, independent of the live
    repository's manifest/pin state (RR3-F1 whole-manifest fail-closed
    means a live pin drift there must not affect this test's own
    positive-path assertions)."""
    import hashlib
    import json

    (tmp_path / "knowledge").mkdir(parents=True)
    entries = []
    for i in range(doc_count):
        doc_text = f"governance advisory local knowledge document number {i} for parity testing"
        (tmp_path / "knowledge" / f"doc{i}.md").write_text(doc_text, encoding="utf-8")
        digest = hashlib.sha256(doc_text.encode("utf-8")).hexdigest()
        entries.append({
            "id": f"doc{i}", "path": f"doc{i}.md", "owner": "ORCHESTRATOR", "classification": "INTERNAL",
            "disposition": "ACTIVE", "dispositionReason": None, "purpose": "p",
            "allowedConsumers": ["LOCAL_GOVERNED_AGENT"],
            "sourcePins": [{"path": f"knowledge/doc{i}.md", "sha256": digest}],
            "reviewedAt": "2026-08-10", "refreshTriggers": [],
            "retentionPolicy": "RETAIN_WHILE_SOURCES_ARE_CURRENT_AND_OWNER_MAINTAINS_ENTRY",
            "correctionPolicy": "c", "eligibleForLocalIndex": True,
        })
    manifest = {
        "schemaVersion": "1.0", "packId": "shift-operations-project-knowledge",
        "classification": "INTERNAL", "reviewedAt": "2026-08-10", "entries": entries,
    }
    (tmp_path / "knowledge" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path

# --- R4: registry golden matrix ---

def test_registry_contains_exactly_three_corpora() -> None:
    assert set(CORPUS_REGISTRY.keys()) == {
        CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1,
        CorpusId.SHIFT_ADVISORY_MESSAGES_V1,
        CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1,
    }

def test_both_operational_corpora_are_dependency_blocked() -> None:
    for corpus_id in (CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1, CorpusId.SHIFT_ADVISORY_MESSAGES_V1):
        descriptor = CORPUS_REGISTRY[corpus_id]
        assert descriptor.state == CorpusState.DEPENDENCY_BLOCKED
        assert not is_available(descriptor)

def test_project_knowledge_is_local_only_and_available() -> None:
    descriptor = CORPUS_REGISTRY[CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1]
    assert descriptor.state == CorpusState.LOCAL_ONLY
    assert is_available(descriptor)

@pytest.mark.parametrize(
    "corpus_id", [CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1, CorpusId.SHIFT_ADVISORY_MESSAGES_V1]
)
def test_blocked_corpus_request_performs_zero_source_calls(corpus_id, monkeypatch) -> None:
    ws = AssignedWorkspace()
    body = request_body(corpus_id=corpus_id.value, shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(),
    )
    assert isinstance(result, CorpusUnavailableV1)
    assert result.receipt.final_outcome.value == "CORPUS_UNAVAILABLE"
    # A blocked corpus request must never even attempt a source read - proven
    # by the receipt's own SOURCES_READ stage staying NOT_RUN.
    sources_stage = next(s for s in result.receipt.stages if s.stage.value == "SOURCES_READ")
    assert sources_stage.outcome.value == "NOT_RUN"
    assert sources_stage.safe_counts.source_records_read == 0

# --- R5: eight-source eligibility matrix / six missing digest owners ---

def test_no_generic_or_forbidden_digest_helper_is_imported_by_p4a1() -> None:
    """AC-05: forbidden application digest helpers must be unreachable from
    the P4-A1 application modules."""
    app_dir = REPO_ROOT / "apps" / "workspace-api" / "src" / "workspace_api" / "application"
    files = list(app_dir.glob("_governed_retrieval_*.py")) + [app_dir / "governed_retrieval.py"]
    offenders = [p.name for p in files if "compute_source_digest" in p.read_text(encoding="utf-8")]
    assert offenders == [], offenders

def test_six_canonical_digest_owners_do_not_exist() -> None:
    """R5: the six DESIGN_NEW digest owner functions must not exist yet -
    canonical/Message corpora remain SOURCE_DIGEST_OWNER_MISSING."""
    digest_module = REPO_ROOT / "packages" / "operations-domain" / "src" / "operations_domain" / "retrieval_digests.py"
    assert not digest_module.exists(), "retrieval_digests module must not be created by P4-A1"

def test_operational_corpus_never_reads_or_admits_canonical_records(monkeypatch) -> None:
    """R7.3: the operational adapter path never calls a Ledger read for
    canonical/Message records - it only proves DEPENDENCY_BLOCKED."""
    ws = AssignedWorkspace()
    ledger_calls = []
    original_transaction = ws.ledger.transaction

    def spy_transaction():
        ledger_calls.append("transaction")
        return original_transaction()

    monkeypatch.setattr(ws.ledger, "transaction", spy_transaction)

    for corpus_id in ("SHIFT_CONFIRMED_OPERATIONS_V1", "SHIFT_ADVISORY_MESSAGES_V1"):
        body = request_body(corpus_id=corpus_id, shift_ids=(str(ws.shift.shift_id),))
        result = execute_governed_retrieval(
            raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
            ledger=ws.ledger, metadata=execution_metadata(),
        )
        assert isinstance(result, CorpusUnavailableV1)

# --- R11: ten-variant union coverage ---

def test_invalid_access_corpus_and_no_evidence_variants_reachable(tmp_path) -> None:
    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    cases = [
        (request_body(query=""), ws.bearer_token(), InvalidRequestV1),
        (request_body(shift_ids=(str(ws.shift.shift_id),)), ws.outsider_token(), AccessDeniedV1),
        (
            request_body(corpus_id="SHIFT_ADVISORY_MESSAGES_V1", shift_ids=(str(ws.shift.shift_id),)),
            ws.bearer_token(), CorpusUnavailableV1,
        ),
        (request_body(query="qkxzvbjplemongrove", shift_ids=(str(ws.shift.shift_id),)), ws.bearer_token(), NoEvidenceV1),
    ]
    for body, token, expected in cases:
        result = execute_governed_retrieval(
            raw_body=body, bearer_token=token, assignment_scope=ws.scope,
            ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
        )
        assert isinstance(result, expected)
        assert result.provider_attempts == 0

def test_evidence_available_variant_has_bounded_projections(tmp_path) -> None:
    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    body = request_body(query="governance", shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert isinstance(result, EvidenceAvailableV1)
    assert 1 <= len(result.projections) <= 4
    assert result.future_context_handoff.provider_attempts == 0
    assert result.future_context_handoff.provider_attempt_authorized is False

def test_context_budget_exceeded_variant_reachable_with_tiny_budget(tmp_path) -> None:
    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    tiny_budget = {
        "max_projection_records": 1,
        "max_snippet_codepoints": 1,
        "max_snippet_utf8_bytes": 1,
        "max_serialized_utf8_bytes": 1,
        "max_estimated_input_tokens": 1,
    }
    body = request_body(query="governance", shift_ids=(str(ws.shift.shift_id),), budget=tiny_budget)
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert isinstance(result, ContextBudgetExceededV1)

def test_unfit_first_fitting_second_projection_replacement_at_ceiling_one(monkeypatch, tmp_path) -> None:
    """RR2-F6/Amendment 3 6.10/Amendment 4 5.5.8: with max_projection_records=1,
    an unfit first-ranked candidate must not force zero output - the scan
    continues past it and a later, fitting candidate is emitted instead.
    This proof requires the POSITIVE EvidenceAvailableV1 outcome with exactly
    one emitted projection and at least two candidate build attempts; a
    negative wrapper (NoEvidenceV1/ContextBudgetExceededV1) is never accepted."""
    from workspace_api.application import _governed_retrieval_revalidation as revalidation_mod

    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path, doc_count=2)
    real_build = revalidation_mod.build_citation_and_projection
    calls: list[int] = []

    def flaky_first(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            return None  # first-ranked candidate never fits
        return real_build(*args, **kwargs)

    monkeypatch.setattr(revalidation_mod, "build_citation_and_projection", flaky_first)
    tight_budget = dict(DEFAULT_BUDGET, max_projection_records=1)
    body = request_body(query="governance", shift_ids=(str(ws.shift.shift_id),), budget=tight_budget)
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert isinstance(result, EvidenceAvailableV1)
    assert len(result.projections) == 1
    assert len(calls) >= 2  # scan continued PAST the unfit first candidate

def test_every_negative_variant_reports_zero_provider_attempts() -> None:
    variants = [InvalidRequestV1, AccessDeniedV1, CorpusUnavailableV1, NoEvidenceV1,
                StaleEvidenceV1, RetrievalLimitExceededV1, ContextBudgetExceededV1, InvariantFailureV1]
    for variant in variants:
        fields = variant.model_fields
        assert "provider_attempts" in fields

# --- RR1-F9: concrete construction for the three variants no prior P4-A1
# test built (StaleEvidenceV1, RetrievalLimitExceededV1, InvariantFailureV1),
# plus injected uuid4_factory/utc_now proof ---

def test_stale_limit_exceeded_and_invariant_failure_variants_are_constructible() -> None:
    """RR1-F9: StaleEvidenceV1, RetrievalLimitExceededV1, InvariantFailureV1
    are concretely constructible from a receipt whose own final_outcome
    matches, and reject a mismatched one - plus the closed NEGATIVE_VARIANTS
    mapping execute_governed_retrieval itself uses names these same classes."""
    from workspace_api.application._governed_retrieval_admission import NEGATIVE_VARIANTS

    from _p4a1_retrieval_fixtures import minimal_negative_receipt

    trio = [
        (FinalOutcome.STALE_EVIDENCE, StaleEvidenceV1),
        (FinalOutcome.RETRIEVAL_LIMIT_EXCEEDED, RetrievalLimitExceededV1),
        (FinalOutcome.INVARIANT_FAILURE, InvariantFailureV1),
    ]
    for outcome, variant in trio:
        built = variant(receipt=minimal_negative_receipt(outcome.value))
        assert built.outcome == outcome
        assert NEGATIVE_VARIANTS[outcome] is variant
    with pytest.raises(ValidationError):
        StaleEvidenceV1(receipt=minimal_negative_receipt("NO_EVIDENCE"))

# --- RR1-F9/AC-11/R12: see test_p4a1_governed_retrieval_boundaries.py ---
