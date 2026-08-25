"""RR2-F3/F1 companion of test_p4a1_retrieval_authorization.py (Amendment 5
test-only structural split): zero-call structural-failure short-circuit,
pre-R2 identity/time allocation, and single-ledger-unit reuse proof."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS))

from workspace_api.application import _governed_retrieval_admission as admission
from workspace_api.application.governed_retrieval import execute_governed_retrieval

from _p4a1_retrieval_fixtures import NOW, AssignedWorkspace, request_body
from _p4a1_retrieval_fixtures import execution_metadata as _base_execution_metadata

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

def _isolated_knowledge_root(tmp_path):
    """A self-contained, pin-correct one-entry Project Knowledge corpus
    under `tmp_path`, independent of the live repository's manifest/pin
    state (RR3-F1 whole-manifest fail-closed means a live pin drift there
    must not affect this test's own positive-path assertions)."""
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

def test_structural_validation_failure_makes_zero_authorization_calls(monkeypatch) -> None:
    ws = AssignedWorkspace()
    calls: list[str] = []
    monkeypatch.setattr(
        admission, "authenticate",
        lambda *a, **k: calls.append("authenticate") or (_ for _ in ()).throw(RuntimeError("unreachable")),
    )
    body = request_body(query="")  # invalid: empty query
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(),
    )
    assert type(result).__name__ == "InvalidRequestV1"
    assert calls == []

def test_identity_and_start_time_allocated_before_r2_even_on_invalid_request() -> None:
    """RR2-F3/RR2-F6: a spy on uuid4_factory/utc_now proves the service
    allocates distinct UUIDv4 identities AND the start clock even for a
    request that will fail R2 - never deferred until after validation."""
    from datetime import datetime, timezone
    from uuid import uuid4 as real_uuid4

    ws = AssignedWorkspace()
    uuid_calls, clock_calls = [], []

    def counting_uuid4_factory():
        value = real_uuid4()
        uuid_calls.append(value)
        return value

    def counting_utc_now():
        clock_calls.append(1)
        return datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc) + timedelta(microseconds=len(clock_calls))

    body = request_body(query="")  # invalid: empty query -> R2 must fail
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope, ledger=ws.ledger,
        metadata=execution_metadata(uuid4_factory=counting_uuid4_factory, utc_now=counting_utc_now),
    )
    assert type(result).__name__ == "InvalidRequestV1"
    assert len(uuid_calls) == 2 and len(set(uuid_calls)) == 2
    assert result.receipt.receipt_id in uuid_calls and result.receipt.retrieval_correlation_id in uuid_calls
    assert len(clock_calls) >= 1

def test_one_ledger_unit_reused_through_assignment_and_final_check(monkeypatch, tmp_path) -> None:
    """F1: one Ledger.transaction() call; the SAME unit passed to every
    require_shift call (initial admission and final R7 re-verification)."""
    ws = AssignedWorkspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    transaction_calls: list[int] = []
    original_transaction = ws.ledger.transaction

    def spy_transaction():
        transaction_calls.append(1)
        return original_transaction()

    monkeypatch.setattr(ws.ledger, "transaction", spy_transaction)
    seen_units: list[object] = []
    original_require_shift = ws.scope.require_shift

    def spy_require_shift(shift_id, principal, *, unit=None):
        seen_units.append(unit)
        return original_require_shift(shift_id, principal, unit=unit)

    monkeypatch.setattr(ws.scope, "require_shift", spy_require_shift)
    body = request_body(shift_ids=(str(ws.shift.shift_id),))
    result = execute_governed_retrieval(
        raw_body=body, bearer_token=ws.bearer_token(), assignment_scope=ws.scope,
        ledger=ws.ledger, metadata=execution_metadata(repository_root=knowledge_root),
    )
    assert type(result).__name__ == "EvidenceAvailableV1"
    assert len(transaction_calls) == 1
    assert len(seen_units) >= 2
    assert len({id(u) for u in seen_units}) == 1
