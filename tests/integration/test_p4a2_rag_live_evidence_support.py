"""P4-A2 SPEC R19/R20 support tests - live-runner mechanics without any call.

NOT GOVERNANCE PROOF: these exercise the synthetic knowledge fixture, refusal
case wiring, and call budgeting offline. The governance proof is the single
live run itself, recorded in
docs/decisions/P4A2_GOVERNED_RAG_LIVE_EVIDENCE_RECEIPT.md.

No test in this file performs network I/O.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _p4a2_governed_rag_live_evidence_support import (  # noqa: E402
    REFUSAL_CASES,
    CallBudget,
    LiveEvidenceError,
    build_synthetic_knowledge_root,
    execution_metadata,
    key_presence,
    p4a1_request_body,
    rag_request,
    run_refusals,
    safe_origin,
    sanitize,
    scan_for_secrets,
    seeded_workspace,
    sha256_hex,
)


class _GuardProvider:
    """NOT GOVERNANCE PROOF: local fake. Any dispatch here fails the test."""

    provider_id = "test-guard"

    def __init__(self, budget: CallBudget) -> None:
        self._budget = budget
        self.calls = 0

    async def generate_structured_output(self, request):
        self.calls += 1
        raise LiveEvidenceError("a refusal case reached the provider")

    async def health_check(self) -> dict:
        raise LiveEvidenceError("health_check is not authorized")

    async def cancel_request(self, request_id: str) -> None:
        return None


class TestSyntheticKnowledgeFixture:
    def test_builds_valid_isolated_manifest(self, tmp_path):
        root = build_synthetic_knowledge_root(tmp_path)
        assert (root / "knowledge" / "manifest.json").exists()
        assert (root / "knowledge" / "doc.md").exists()

    def test_contains_no_real_operational_identifiers(self, tmp_path):
        root = build_synthetic_knowledge_root(tmp_path)
        text = (root / "knowledge" / "doc.md").read_text(encoding="utf-8")
        assert "customer" not in text.lower()
        assert "@" not in text  # no email-shaped content
        assert "ssn" not in text.lower()

    def test_p4a1_admits_the_synthetic_manifest(self, tmp_path):
        """The exact P4-A1 knowledge-corpus pipeline must accept this
        fixture end to end (zero physical provider calls involved here)."""
        root = build_synthetic_knowledge_root(tmp_path)
        ledger, shift, scope, token = seeded_workspace()
        body = p4a1_request_body(query="handover procedure", shift_ids=(str(shift.shift_id),))

        from workspace_api.application.governed_retrieval import execute_governed_retrieval

        result = execute_governed_retrieval(
            raw_body=body, bearer_token=token, assignment_scope=scope, ledger=ledger,
            metadata=execution_metadata(repository_root=root),
        )
        assert type(result).__name__ == "EvidenceAvailableV1"


class TestSeededWorkspace:
    def test_returns_real_ledger_shift_scope_and_token(self):
        ledger, shift, scope, token = seeded_workspace()
        assert shift is not None
        assert isinstance(token, str) and token
        assert scope is not None


class TestRagRequestBuilder:
    def test_builds_valid_governed_rag_request(self):
        req = rag_request(query="handover", model_id="qwen-test-model")
        assert req.query == "handover"
        assert req.provider_id == "alibaba_dashscope_evidence_only"


class TestRefusalCasesZeroCall:
    def test_all_mandated_p4a2_cases_present(self):
        assert len(REFUSAL_CASES) >= 6

    def test_refusal_cases_reach_provider_zero_times(self, tmp_path):
        budget = CallBudget(limit=1)
        rows = run_refusals("qwen-test-model", budget, _GuardProvider, tmp_path)

        assert len(rows) == len(REFUSAL_CASES)
        for row in rows:
            assert row["accepted"] is False, row
            assert row["provider_attempts"] == 0, row
            assert row["adapter_calls"] == 0, row
            assert row["gateway_attempts"] == 0, row
        assert budget.physical == 0, "no physical call may occur during refusals"

    def test_each_refusal_case_has_a_distinct_reason_code(self, tmp_path):
        budget = CallBudget(limit=1)
        rows = run_refusals("qwen-test-model", budget, _GuardProvider, tmp_path)
        reasons = {row["reason_code"] for row in rows}
        assert len(reasons) == len(REFUSAL_CASES), "each mandated case should exercise a distinct refusal reason"


class TestCallBudgetReuse:
    def test_single_reservation_allowed(self):
        budget = CallBudget(limit=1)
        budget.reserve()
        assert budget.reserved == 1

    def test_second_reservation_refused(self):
        budget = CallBudget(limit=1)
        budget.reserve()
        with pytest.raises(LiveEvidenceError):
            budget.reserve()


class TestSecretSafetyReuse:
    def test_sanitize_redacts_secret_shapes(self):
        assert "[REDACTED]" in sanitize("Authorization: Bearer abcdef1234567890")

    def test_scan_for_secrets_detects_bearer_token(self):
        assert scan_for_secrets("Bearer abcdef1234567890")

    def test_safe_origin_strips_credentials(self):
        url = "https://user:pass@host.example.com/compatible-mode/v1/chat/completions"
        assert safe_origin(url) == "https://host.example.com"


class TestKeyPresenceReuse:
    def test_reports_presence_without_revealing_value(self, monkeypatch):
        monkeypatch.setenv("ALIBABA_API_KEY", "some-secret-value")
        present, name = key_presence()
        assert present is True
        assert name == "ALIBABA_API_KEY"
