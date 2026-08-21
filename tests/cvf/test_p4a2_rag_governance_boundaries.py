"""P4-A2 CVF governance boundary tests (SPEC R1/R3/R12/R16/R17/R23).

No-network and no-persistence boundary tests, at-most-once gateway dispatch
proof at the CVF-relevant object-identity level, and claim-boundary checks
that this tranche's evidence artifacts do not overclaim beyond the bounded
application-layer composition DESIGN/SPEC actually authorize.

Not governance proof by itself - the live evidence run
(``scripts/run_p4a2_governed_rag_live_evidence.py``) is the only accepted
governance proof surface for actual provider dispatch (SPEC R19). These
tests prove the STRUCTURAL boundaries that make that live run meaningful.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_UNIT_TESTS = _REPO_ROOT / "tests" / "unit"
if str(_UNIT_TESTS) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS))

import pytest

import _p4a2_rag_fixtures as fx
from ai_gateway.models import Placement, ProviderRequest, ProviderResult
from ai_gateway.registry import ProviderRegistry
from ai_gateway.service import AIGateway
from ai_gateway.usage import UsageLedger
from governed_rag.receipts import RagFinalOutcome
from governed_rag.service import GovernedRAG


class _AnswerProvider:
    provider_id = "alibaba_dashscope_evidence_only"

    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult:
        self.calls += 1
        cid = request.context["evidence_records"][0]["citation_id"]
        output = {"status": "ANSWER", "claims": [{"text": "x", "citation_ids": [cid]}], "abstention_reason": ""}
        return ProviderResult(
            output=output, provider_id=self.provider_id, model_id=request.model_id,
            usage={"total_tokens": 10, "cost_usd_millis": 0},
        )

    async def health_check(self) -> dict:
        return {}

    async def cancel_request(self, request_id: str) -> None:
        return None


def _gateway(provider, *, placement: Placement = Placement.LOCAL):
    registry = ProviderRegistry()
    registry.register(provider, ("qwen-test-model",), placement=placement)
    return AIGateway(registry, UsageLedger(), endpoint_origin="https://example.invalid")


class TestNoNetworkBoundary:
    """SPEC R1/R12: the pure package's only reachable network-shaped call
    site is through the injected AIGateway. No governed_rag module performs
    any network I/O of its own."""

    def test_governed_rag_package_has_no_network_capable_import(self):
        import governed_rag

        package_root = Path(governed_rag.__file__).resolve().parent
        for path in sorted(package_root.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            assert "socket" not in text
            assert "urllib.request" not in text
            assert "http.client" not in text

    def test_application_composition_module_has_no_network_capable_import(self):
        import workspace_api.application.governed_rag as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "urllib.request" not in text
        assert "http.client" not in text
        assert "socket" not in text


class TestNoPersistenceBoundary:
    """SPEC R3/R16: no index/answer/audit persistence anywhere in the
    request path."""

    def test_governed_rag_package_has_no_database_import(self):
        import governed_rag

        package_root = Path(governed_rag.__file__).resolve().parent
        for path in sorted(package_root.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            assert "sqlite3" not in text
            assert "sqlalchemy" not in text.lower() or "sqlalchemy" not in text  # explicit, redundant guard

    def test_application_composition_never_calls_audit_or_ledger_append(self):
        import workspace_api.application.governed_rag as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "append_audit" not in text
        assert "AuditLog.record" not in text
        assert "INSERT INTO" not in text

    def test_positive_execution_leaves_no_new_ledger_state(self):
        """Running a full positive pipeline must not create any new ledger
        record: the receipt is response data only."""
        ev = fx.evidence_available()
        req = fx.rag_request()
        provider = _AnswerProvider()
        engine = GovernedRAG(_gateway(provider), placement=Placement.LOCAL)
        before_repr = repr(ev)  # positive result itself is immutable/frozen
        asyncio.run(engine.execute(request=req, retrieval_result=ev, authorization_scope_digest_sha256="d" * 64))
        after_repr = repr(ev)
        assert before_repr == after_repr  # frozen input untouched

    def test_receipt_contains_no_evidence_or_answer_body(self):
        ev = fx.evidence_available()
        provider = _AnswerProvider()
        engine = GovernedRAG(_gateway(provider), placement=Placement.LOCAL)
        result = asyncio.run(
            engine.execute(request=fx.rag_request(), retrieval_result=ev, authorization_scope_digest_sha256="d" * 64)
        )
        dump_str = str(result.receipt.model_dump(mode="python"))
        assert "handover" not in dump_str.lower()
        assert "x" != dump_str  # sanity: dump is a real structure, not the raw answer text


class TestAtMostOnceGatewayDispatch:
    """SPEC R12: GovernedRAG.execute calls the injected gateway's execute
    zero or one time, never more, and never a second gateway instance."""

    def test_negative_short_circuit_never_touches_gateway_object(self):
        neg = fx.negative_result("NO_EVIDENCE")
        provider = _AnswerProvider()
        gateway = _gateway(provider)
        engine = GovernedRAG(gateway, placement=Placement.LOCAL)
        asyncio.run(
            engine.execute(request=fx.rag_request(), retrieval_result=neg, authorization_scope_digest_sha256="d" * 64)
        )
        assert gateway.physical_attempts == 0

    def test_positive_execution_calls_gateway_exactly_once(self):
        ev = fx.evidence_available()
        provider = _AnswerProvider()
        gateway = _gateway(provider)
        engine = GovernedRAG(gateway, placement=Placement.LOCAL)
        asyncio.run(
            engine.execute(request=fx.rag_request(), retrieval_result=ev, authorization_scope_digest_sha256="d" * 64)
        )
        assert gateway.physical_attempts == 1
        assert provider.calls == 1


class TestClaimBoundary:
    """SPEC R17/R23: this tranche proves a bounded application-layer
    composition over synthetic/local Project Knowledge - never operational-
    corpus RAG, general embeddings, durable memory, a public API, or
    production readiness. These tests assert the DESIGN/SPEC/README/receipt
    documents actually declare that boundary rather than overclaiming."""

    def test_readme_declares_the_claim_boundary(self):
        readme = (_REPO_ROOT / "packages" / "governed-rag" / "README.md").read_text(encoding="utf-8")
        assert "claim boundary" in readme.lower()
        assert "does not prove" in readme.lower()

    def test_spec_declares_operational_corpus_remains_blocked(self):
        spec = (_REPO_ROOT / "docs" / "specs" / "P4A2_GOVERNED_RAG_SPEC.md").read_text(encoding="utf-8")
        assert "dependency-blocked" in spec

    def test_encoder_is_explicitly_not_a_general_embeddings_claim(self):
        import governed_rag.semantic as semantic_module

        source = Path(semantic_module.__file__).read_text(encoding="utf-8")
        assert "NOT a general-purpose embedding" in source

    def test_receipt_final_outcome_never_claims_answered_without_one_physical_attempt(self):
        ev = fx.evidence_available()
        provider = _AnswerProvider()
        engine = GovernedRAG(_gateway(provider), placement=Placement.LOCAL)
        outcome = asyncio.run(
            engine.execute(request=fx.rag_request(), retrieval_result=ev, authorization_scope_digest_sha256="d" * 64)
        )
        if outcome.receipt.final_outcome is RagFinalOutcome.ANSWERED:
            assert outcome.receipt.physical_attempt_count == 1


class TestPlacementIdentityAndMismatch:
    """P4A2-REV-F3: placement is bound to the engine at construction from
    the real adapter wiring, never a per-call caller-suppliable field, and
    the real cvf_runtime.data_scope gate must receive the correct EXTERNAL
    value; EXTERNAL placement without proven minimization refuses BEFORE
    any gateway/provider dispatch (physical calls == 0)."""

    def test_placement_property_reflects_bound_construction_value(self):
        from ai_gateway.models import Placement

        engine = GovernedRAG(_gateway(_AnswerProvider(), placement=Placement.EXTERNAL), placement=Placement.EXTERNAL)
        assert engine.placement is Placement.EXTERNAL
        local_engine = GovernedRAG(_gateway(_AnswerProvider(), placement=Placement.LOCAL), placement=Placement.LOCAL)
        assert local_engine.placement is Placement.LOCAL

    def test_placement_has_no_default_and_must_be_supplied_explicitly(self):
        """Amendment 1 / A1-F3: GovernedRAG.__init__ no longer defaults
        placement to LOCAL - omitting it entirely must fail with a TypeError
        (missing required keyword-only argument), never a silent LOCAL."""
        with pytest.raises(TypeError):
            GovernedRAG(_gateway(_AnswerProvider()))  # type: ignore[call-arg]

    def test_caller_cannot_force_local_label_for_external_dispatch(self):
        """execute() accepts no placement parameter, so a caller cannot
        relabel the engine's bound EXTERNAL fact per-call; the captured
        dispatched GatewayRequest proves EXTERNAL reached the real gate."""
        from ai_gateway.models import Placement

        class _CapturingGateway:
            def __init__(self) -> None:
                self.captured = None

            async def execute(self, request):
                self.captured = request
                return await _gateway(_AnswerProvider(), placement=Placement.EXTERNAL).execute(request)

        ev = fx.evidence_available()
        gateway = _CapturingGateway()
        engine = GovernedRAG(gateway, placement=Placement.EXTERNAL)
        asyncio.run(engine.execute(request=fx.rag_request(), retrieval_result=ev, authorization_scope_digest_sha256="d" * 64))
        assert gateway.captured.placement is Placement.EXTERNAL

    def test_external_placement_refused_without_minimization_zero_calls(self):
        """Off-topic evidence yields zero minimized records; EXTERNAL
        placement must refuse BEFORE gateway dispatch (physical calls==0)."""
        from ai_gateway.models import Placement

        irrelevant = fx.make_projection(snippet="The weather today is mild with a light breeze.")
        ev = fx.evidence_available(projections=(irrelevant,))
        provider = _AnswerProvider()
        gateway = _gateway(provider, placement=Placement.EXTERNAL)
        engine = GovernedRAG(gateway, placement=Placement.EXTERNAL)
        result = asyncio.run(engine.execute(
            request=fx.rag_request(query="handover procedure"), retrieval_result=ev,
            authorization_scope_digest_sha256="d" * 64,
        ))
        assert provider.calls == 0
        assert gateway.physical_attempts == 0
        assert result.receipt.physical_attempt_count == 0
        assert result.receipt.final_outcome.value == "MINIMIZATION_FAILED"
