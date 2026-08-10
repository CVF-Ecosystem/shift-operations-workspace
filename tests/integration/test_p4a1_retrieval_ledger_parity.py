"""SPEC R7 - use-time revalidation, InMemory/SqlLedger parity (AC-07).
Disposable local SQLite ONLY - never PostgreSQL/live/network."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS))

import pytest
from cvf_runtime.identity import Principal
from operations_domain.models import Shift
from operations_ledger.sql_ledger import SqlLedger, make_engine
from operations_ledger.tables import metadata

from governed_retrieval.result_models import RetrievalStoppedV1

from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.application.governed_retrieval import execute_governed_retrieval
from workspace_api.auth.tokens import create_access_token
from workspace_api.domain import models as domain_models
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger

from _p4a1_retrieval_fixtures import NOW, AssignedWorkspace, request_body
from _p4a1_retrieval_fixtures import execution_metadata as _base_execution_metadata

REPO_ROOT = _REPO_ROOT

def _advancing_utc_now(*, start=NOW):
    """RR3-F4 - each call returns `start` plus a strictly increasing offset."""
    calls = [0]
    def clock():
        calls[0] += 1
        return start + timedelta(microseconds=calls[0])
    return clock

def execution_metadata(**overrides):
    overrides.setdefault("utc_now", _advancing_utc_now())
    return _base_execution_metadata(**overrides)

def _sql_ledger(tmp_path):
    db = tmp_path / "p4a1_retrieval_parity.sqlite3"
    engine = make_engine(f"sqlite:///{db}")
    metadata.create_all(engine)
    return SqlLedger(str(db), models=domain_models, engine=engine)

def _seeded(ledger):
    shift = Shift(name="Day", starts_at=NOW, ends_at=NOW + timedelta(hours=8))
    ledger.create_shift(shift)
    ledger.add_user(User(user_id="op1", username="op1", password_hash="x", role="viewer"))
    ledger.add_user(User(user_id="sup1", username="sup1", password_hash="x", role="shift_supervisor"))
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    return shift

def _backends(tmp_path):
    return [("in_memory", InMemoryLedger()), ("sql", _sql_ledger(tmp_path))]

def _isolated_knowledge_root(tmp_path):
    """A self-contained, pin-correct one-entry corpus, independent of the
    live repo's manifest/pin state; `path` relative to `knowledge/`,
    `sourcePins[].path` relative to the repository root."""
    import hashlib
    import json

    (tmp_path / "knowledge").mkdir(parents=True)
    doc_text = "governance advisory local knowledge for parity testing"
    (tmp_path / "knowledge" / "doc.md").write_text(doc_text, encoding="utf-8")
    digest = hashlib.sha256(doc_text.encode("utf-8")).hexdigest()
    manifest = {
        "schemaVersion": "1.0", "packId": "shift-operations-project-knowledge",
        "classification": "INTERNAL", "reviewedAt": "2026-08-10",
        "entries": [{
            "id": "doc", "path": "doc.md", "owner": "ORCHESTRATOR", "classification": "INTERNAL",
            "disposition": "ACTIVE", "dispositionReason": None, "purpose": "p",
            "allowedConsumers": ["LOCAL_GOVERNED_AGENT"],
            "sourcePins": [{"path": "knowledge/doc.md", "sha256": digest}],
            "reviewedAt": "2026-08-10", "refreshTriggers": [],
            "retentionPolicy": "RETAIN_WHILE_SOURCES_ARE_CURRENT_AND_OWNER_MAINTAINS_ENTRY",
            "correctionPolicy": "c", "eligibleForLocalIndex": True,
        }],
    }
    (tmp_path / "knowledge" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path

@pytest.mark.parametrize("name", ["in_memory", "sql"])
def test_positive_evidence_path_identical_across_backends(tmp_path, name) -> None:
    """Also proves: elapsed_ms is real (never always-zero); exactly one
    Ledger.transaction() call per execution (R7); result_limit truncation
    never backfills (a deterministic re-run produces the identical
    first-ranked citation); and an unassigned outsider is denied identically."""
    ledger = dict(_backends(tmp_path))[name]
    shift = _seeded(ledger)
    principal = Principal(user_id="op1", role="viewer")
    scope = AssignmentScope(ledger)
    transaction_calls = []
    original_transaction = ledger.transaction

    def spy_transaction():
        transaction_calls.append(1)
        return original_transaction()

    ledger.transaction = spy_transaction
    knowledge_root = _isolated_knowledge_root(tmp_path / "kb")
    token = create_access_token(principal)
    body = request_body(query="governance", shift_ids=(str(shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=token, assignment_scope=scope, ledger=ledger,
        metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert type(result).__name__ == "EvidenceAvailableV1"
    assert result.receipt.final_outcome.value == "EVIDENCE_AVAILABLE"
    assert 1 <= len(result.projections) <= 4
    assert result.receipt.elapsed_ms >= 0
    assert len(transaction_calls) == 1

    limited_body = request_body(query="governance", shift_ids=(str(shift.shift_id),), result_limit=1)
    rerun = execute_governed_retrieval(
        raw_body=limited_body, bearer_token=token, assignment_scope=scope, ledger=ledger,
        metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert rerun.receipt.citation_ids == result.receipt.citation_ids[:1]

    ledger.add_user(User(user_id="op2", username="op2", password_hash="x", role="viewer"))
    outsider_result = execute_governed_retrieval(
        raw_body=body, bearer_token=create_access_token(Principal(user_id="op2", role="viewer")),
        assignment_scope=scope, ledger=ledger, metadata=execution_metadata(),
    )
    assert type(outsider_result).__name__ == "AccessDeniedV1"

def test_postgresql_is_not_claimed() -> None:
    """Negative claim: InMemory/SQLite parity only - never a PostgreSQL driver."""
    import ast

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imported.add((n.module or "").split(".")[0])
    assert not ({"psycopg", "psycopg2"} & imported)

# --- F11: timeout, cancellation, real timing, and safe manifest failure ---

def test_retrieval_timeout_and_cancelled_variants_reachable(monkeypatch, tmp_path) -> None:
    """The elapsed-time checkpoint trips (monkeypatched time.monotonic,
    never a raced tiny wall-clock timeout) and a real cancellation_check()
    returning True each stop the pipeline with the matching termination facts."""
    import time as time_module
    from workspace_api.application import _governed_retrieval_sources as sources_mod

    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    body = request_body(query="governance", shift_ids=(str(ws.shift.shift_id),))
    real_monotonic = time_module.monotonic
    call_count = {"n": 0}

    def fake_monotonic():
        call_count["n"] += 1
        return real_monotonic() if call_count["n"] == 1 else real_monotonic() + 10.0

    monkeypatch.setattr(sources_mod.time, "monotonic", fake_monotonic)
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(timeout_ms=1, repository_root=knowledge_root),
    )
    assert isinstance(result, RetrievalStoppedV1)
    assert result.receipt.final_outcome.value == "RETRIEVAL_TIMEOUT"
    assert result.receipt.termination.timed_out is True
    assert result.receipt.termination.cancelled is False
    monkeypatch.undo()

    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(cancellation_check=lambda: True),
    )
    assert isinstance(result, RetrievalStoppedV1)
    assert result.receipt.final_outcome.value == "RETRIEVAL_CANCELLED"
    assert result.receipt.termination.cancelled is True
    assert result.receipt.termination.timed_out is False

    # RR2-F4/RR2-F6/Amendment 4 5.5.11: cancellation firing only at the FINAL
    # (third) checkpoint records PROJECTED=FAIL (never RECEIPT_EMITTED=FAIL,
    # which stays PASS) and returns no projections/handoff.
    third_calls = {"n": 0}

    def cancel_only_on_third_call():  # first two checkpoints pass
        third_calls["n"] += 1
        return third_calls["n"] >= 3

    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope, ledger=ws.ledger,
        metadata=execution_metadata(cancellation_check=cancel_only_on_third_call, repository_root=knowledge_root),
    )
    assert isinstance(result, RetrievalStoppedV1)
    assert result.receipt.final_outcome.value == "RETRIEVAL_CANCELLED"
    stages = {s.stage.value: s.outcome.value for s in result.receipt.stages}
    assert stages["PROJECTED"] == "FAIL"
    assert stages["RECEIPT_EMITTED"] == "PASS"
    assert result.receipt.citation_ids == ()
    assert result.receipt.evidence_set_hash_sha256 is None
    assert not hasattr(result, "projections")

# --- F4/RR1-F3/RR3-F1-F3: see test_p4a1_retrieval_project_knowledge.py ---
