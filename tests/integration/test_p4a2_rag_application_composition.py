"""P4-A2 SPEC R3 - execute_governed_rag application composition integration.

Exercises the real P4-A1 pipeline (real bearer-token auth, real assignment
scope, real InMemoryLedger, a real isolated PROJECT_KNOWLEDGE_LOCAL_V1
manifest under an isolated tmp repository root) through the real
GovernedRAG.execute path with a fake gateway (mechanics only, not governance
proof). Proves query/result continuity, no HTTP route, no persistence, and
a real end-to-end ANSWERED/zero-attempt outcome.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS))

import pytest
from cvf_runtime.identity import Principal

from ai_gateway.models import Placement, ProviderRequest, ProviderResult
from ai_gateway.registry import ProviderRegistry
from ai_gateway.service import AIGateway
from ai_gateway.usage import UsageLedger
from governed_rag.receipts import RagFinalOutcome

from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.application.governed_rag import execute_governed_rag
from workspace_api.auth.tokens import create_access_token
from workspace_api.domain.models import ShiftAssignment, User
from workspace_api.infrastructure.repository import InMemoryLedger

from _p4a2_rag_fixtures import rag_request
from _p4a1_retrieval_fixtures import NOW, request_body
from _p4a1_retrieval_fixtures import execution_metadata as _base_execution_metadata
from operations_domain.models import Shift
from datetime import timedelta


def _advancing_utc_now(*, start=NOW):
    """RR3-F4 - each call returns `start` plus a strictly increasing offset,
    so a real ``elapsed_ms > 0`` receipt can validate (mirrors the P4-A1
    integration test precedent's own clock fixture)."""
    calls = [0]

    def clock():
        calls[0] += 1
        return start + timedelta(microseconds=calls[0])

    return clock


def execution_metadata(**overrides):
    overrides.setdefault("utc_now", _advancing_utc_now())
    return _base_execution_metadata(**overrides)


def _isolated_knowledge_root(tmp_path: Path) -> Path:
    (tmp_path / "knowledge").mkdir(parents=True)
    doc_text = "Shift handover requires a written summary of open incidents and escalation status."
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


class _AnswerProvider:
    """NOT PROOF - mechanics-only fake for integration wiring."""

    provider_id = "alibaba_dashscope_evidence_only"

    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        self.calls += 1
        cid = request.context["evidence_records"][0]["citation_id"]
        output = {"status": "ANSWER", "claims": [{"text": "Handover requires a written summary.", "citation_ids": [cid]}], "abstention_reason": ""}
        return ProviderResult(
            output=output, provider_id=self.provider_id, model_id=request.model_id,
            usage={"total_tokens": 10, "cost_usd_millis": 0},
        )

    async def health_check(self) -> dict:
        return {}

    async def cancel_request(self, request_id: str) -> None:
        return None


def _gateway(provider):
    registry = ProviderRegistry()
    registry.register(provider, ("qwen-test-model",), placement=Placement.LOCAL)
    return AIGateway(registry, UsageLedger(), endpoint_origin="https://example.invalid")


def _seeded_workspace():
    ledger = InMemoryLedger()
    shift = Shift(name="Day", starts_at=NOW, ends_at=NOW.replace(hour=20))
    ledger.create_shift(shift)
    ledger.add_user(User(user_id="op1", username="op1", password_hash="x", role="viewer"))
    ledger.add_user(User(user_id="sup1", username="sup1", password_hash="x", role="shift_supervisor"))
    ledger.add_assignment(ShiftAssignment(shift_id=shift.shift_id, user_id="op1", assigned_by="sup1"))
    principal = Principal(user_id="op1", role="viewer")
    scope = AssignmentScope(ledger)
    return ledger, shift, principal, scope


def test_end_to_end_answered_through_real_p4a1_pipeline(tmp_path):
    ledger, shift, principal, scope = _seeded_workspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    token = create_access_token(principal)
    query = "handover procedure"
    body = request_body(query=query, shift_ids=(str(shift.shift_id),))
    provider = _AnswerProvider()
    gateway = _gateway(provider)

    outcome = asyncio.run(
        execute_governed_rag(
            raw_body=body,
            rag_request=rag_request(query=query),
            bearer_token=token,
            assignment_scope=scope,
            ledger=ledger,
            metadata=execution_metadata(repository_root=knowledge_root),
            gateway=gateway,
            placement=Placement.LOCAL,
        )
    )
    assert provider.calls == 1
    assert outcome.receipt.final_outcome is RagFinalOutcome.ANSWERED
    assert outcome.answer is not None
    assert outcome.answer.status.value == "ANSWER"


def test_query_continuity_mismatch_raises_before_any_p4a1_call():
    ledger, shift, principal, scope = _seeded_workspace()
    token = create_access_token(principal)
    body = request_body(query="one query", shift_ids=(str(shift.shift_id),))
    provider = _AnswerProvider()
    gateway = _gateway(provider)

    with pytest.raises(ValueError):
        asyncio.run(
            execute_governed_rag(
                raw_body=body,
                rag_request=rag_request(query="a different query"),
                bearer_token=token,
                assignment_scope=scope,
                ledger=ledger,
                metadata=execution_metadata(),
                gateway=gateway,
                placement=Placement.LOCAL,
            )
        )
    assert provider.calls == 0


def test_unassigned_outsider_is_denied_with_zero_gateway_attempts():
    ledger, shift, principal, scope = _seeded_workspace()
    ledger.add_user(User(user_id="op2", username="op2", password_hash="x", role="viewer"))
    outsider = Principal(user_id="op2", role="viewer")
    token = create_access_token(outsider)
    query = "handover procedure"
    body = request_body(query=query, shift_ids=(str(shift.shift_id),))
    provider = _AnswerProvider()
    gateway = _gateway(provider)

    outcome = asyncio.run(
        execute_governed_rag(
            raw_body=body,
            rag_request=rag_request(query=query),
            bearer_token=token,
            assignment_scope=scope,
            ledger=ledger,
            metadata=execution_metadata(),
            gateway=gateway,
            placement=Placement.LOCAL,
        )
    )
    assert provider.calls == 0
    assert outcome.receipt.final_outcome is RagFinalOutcome.RETRIEVAL_NOT_POSITIVE
    assert outcome.receipt.physical_attempt_count == 0


def test_no_evidence_short_circuits_before_gateway(tmp_path):
    ledger, shift, principal, scope = _seeded_workspace()
    knowledge_root = _isolated_knowledge_root(tmp_path)
    token = create_access_token(principal)
    query = "zzyzx quokka unrelated nonmatching gibberish token"
    body = request_body(query=query, shift_ids=(str(shift.shift_id),))
    provider = _AnswerProvider()
    gateway = _gateway(provider)

    outcome = asyncio.run(
        execute_governed_rag(
            raw_body=body,
            rag_request=rag_request(query=query),
            bearer_token=token,
            assignment_scope=scope,
            ledger=ledger,
            metadata=execution_metadata(repository_root=knowledge_root),
            gateway=gateway,
            placement=Placement.LOCAL,
        )
    )
    assert provider.calls == 0
    assert outcome.receipt.physical_attempt_count == 0
    assert outcome.receipt.final_outcome is RagFinalOutcome.RETRIEVAL_NOT_POSITIVE


def test_execute_governed_rag_never_persists_or_opens_a_route():
    """Structural: the module declares no FastAPI router/dependency and no
    database write call anywhere in its own source."""
    import workspace_api.application.governed_rag as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "APIRouter" not in source
    assert "@router" not in source
    assert ".add_route(" not in source
    assert "INSERT INTO" not in source
    assert "ledger.append_audit" not in source
    assert "AuditLog.record" not in source
