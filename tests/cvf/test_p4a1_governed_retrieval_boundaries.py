"""RR1-F9/R12/AC-11 companion of test_p4a1_governed_retrieval.py (Amendment 5
test-only structural split): injected uuid4_factory/utc_now proof, provider-
import static proof, and V1 evolution rejection boundaries."""

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

from governed_retrieval.request_models import GovernedRetrievalRequestV1
from governed_retrieval.result_models import EvidenceAvailableV1
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

# --- RR1-F9: injected uuid4_factory/utc_now proof ---

def test_execution_metadata_uses_injected_uuid4_factory_and_utc_now_not_caller_ids(tmp_path) -> None:
    """RR1-F9: the service calls uuid4_factory exactly twice (distinct real
    UUIDv4 receipt/correlation ids) and independently calls utc_now for
    start/source-cutoff/finish - never a caller-pre-allocated id/timestamp."""
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4 as real_uuid4

    uuid_calls, clock_calls = [], []

    def counting_uuid4_factory():
        value = real_uuid4()
        uuid_calls.append(value)
        return value

    base = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)

    def sequenced_utc_now():
        clock_calls.append(1)
        return base + timedelta(seconds=len(clock_calls))

    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    body = request_body(query="governance", shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope, ledger=ws.ledger,
        metadata=execution_metadata(
            uuid4_factory=counting_uuid4_factory, utc_now=sequenced_utc_now, repository_root=knowledge_root,
        ),
    )
    assert isinstance(result, EvidenceAvailableV1)
    assert len(uuid_calls) == 2 and len(set(uuid_calls)) == 2  # distinct, never reused
    assert all(u.version == 4 for u in uuid_calls)
    assert result.receipt.receipt_id in uuid_calls and result.receipt.retrieval_correlation_id in uuid_calls
    assert len(clock_calls) >= 3  # start, source cutoff, finish - independent captures
    assert result.receipt.finished_at_utc >= result.receipt.started_at_utc
    assert result.receipt.elapsed_ms >= 0

def test_no_p4a1_source_file_imports_a_provider_module() -> None:
    """AC-11: static proof no P4-A1 code path can resolve a provider symbol."""
    provider_tokens = ("openai", "anthropic", "dashscope", "alibaba", "deepseek")
    roots = [
        REPO_ROOT / "packages" / "governed-retrieval" / "src",
    ]
    app_dir = REPO_ROOT / "apps" / "workspace-api" / "src" / "workspace_api" / "application"
    files = []
    for root in roots:
        files += list(root.rglob("*.py"))
    files += list(app_dir.glob("_governed_retrieval_*.py")) + [app_dir / "governed_retrieval.py"]
    offenders = []
    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        for token in provider_tokens:
            if token in text:
                offenders.append(f"{path.name} references {token}")
    assert offenders == [], offenders

# --- R12: V1 evolution rejection ---

def test_request_model_rejects_unknown_enum_value_for_corpus_id() -> None:
    """R2/R3 boundary: corpus_id is a safe-shaped string at bare structural
    validation (registry resolution is deferred to stage-5 post-
    authorization), so a syntactically-valid-but-unregistered future corpus
    id passes here and is rejected only by resolve_and_authorize_corpus."""
    from workspace_api.application._governed_retrieval_sources import (
        CorpusResolutionFailed,
        resolve_and_authorize_corpus,
    )

    request = GovernedRetrievalRequestV1.model_validate(
        {"query": "x", "corpus_id": "SOME_FUTURE_CORPUS_V2", "filters": {"shift_ids": ("a",)}, "context_budget": DEFAULT_BUDGET}
    )
    with pytest.raises(CorpusResolutionFailed):
        resolve_and_authorize_corpus(request)

def test_request_model_rejects_a_new_unknown_field() -> None:
    with pytest.raises(ValidationError):
        GovernedRetrievalRequestV1.model_validate(
            {
                "query": "x", "corpus_id": "PROJECT_KNOWLEDGE_LOCAL_V1", "filters": {"shift_ids": ("a",)},
                "context_budget": DEFAULT_BUDGET, "a_brand_new_field": "should be rejected",
            }
        )
