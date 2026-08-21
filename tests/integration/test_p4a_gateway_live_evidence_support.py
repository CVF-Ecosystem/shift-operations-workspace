"""P4-A SPEC R13 support tests - live-runner mechanics without any call.

NOT GOVERNANCE PROOF: these exercise sanitization, call budgeting, and refusal
request shapes offline. The governance proof is the single live run itself,
recorded in docs/decisions/P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md.

No test in this file performs network I/O.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _p4a_gateway_live_evidence_support import (  # noqa: E402
    CANARY_SCHEMA,
    KEY_ENV_NAMES,
    REFUSAL_CASES,
    CallBudget,
    LiveEvidenceError,
    canonical,
    extract_json_object,
    key_presence,
    refusal_request,
    run_refusals,
    safe_origin,
    sanitize,
    scan_for_secrets,
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


class TestSafeOrigin:
    def test_strips_path_query_and_credentials(self):
        url = "https://user:pass@host.example.com/compatible-mode/v1/chat/completions?k=v"
        assert safe_origin(url) == "https://host.example.com"

    def test_keeps_scheme_and_host(self):
        assert safe_origin("https://dashscope-intl.aliyuncs.com/x") == (
            "https://dashscope-intl.aliyuncs.com"
        )


class TestSanitize:
    @pytest.mark.parametrize(
        "text",
        [
            "Authorization: Bearer abcdef1234567890",
            "key sk-abcdef1234567890",
            "API_KEY=supersecretvalue",
            "https://user:password@host/path",
        ],
    )
    def test_secret_shapes_are_redacted(self, text):
        assert "[REDACTED]" in sanitize(text)

    def test_literal_env_value_is_redacted(self, monkeypatch):
        monkeypatch.setenv(KEY_ENV_NAMES[0], "UNUSUALVALUE123456")
        assert "UNUSUALVALUE123456" not in sanitize("token UNUSUALVALUE123456 tail")

    def test_length_is_bounded(self):
        assert len(sanitize("x" * 1000, limit=50)) == 50


class TestScanForSecrets:
    def test_clean_text_has_no_hits(self):
        assert scan_for_secrets("http_status 200; attempts 1") == []

    def test_bearer_token_detected(self):
        assert scan_for_secrets("Bearer abcdef1234567890")

    def test_literal_env_value_detected(self, monkeypatch):
        monkeypatch.setenv(KEY_ENV_NAMES[1], "ANOTHERSECRET99999")
        hits = scan_for_secrets("leak ANOTHERSECRET99999")
        assert any(hit.startswith("literal:") for hit in hits)


class TestKeyPresence:
    def test_absent_when_unset(self, monkeypatch):
        for name in KEY_ENV_NAMES:
            monkeypatch.delenv(name, raising=False)
        assert key_presence() == (False, None)

    def test_reports_name_not_value(self, monkeypatch):
        monkeypatch.delenv(KEY_ENV_NAMES[1], raising=False)
        monkeypatch.setenv(KEY_ENV_NAMES[0], "secret-value")
        present, name = key_presence()
        assert present is True and name == KEY_ENV_NAMES[0]


class TestCallBudget:
    def test_single_reservation_allowed(self):
        budget = CallBudget(limit=1)
        budget.reserve()
        assert budget.reserved == 1

    def test_second_reservation_refused(self):
        budget = CallBudget(limit=1)
        budget.reserve()
        with pytest.raises(LiveEvidenceError):
            budget.reserve()

    def test_second_physical_call_refused(self):
        budget = CallBudget(limit=1)
        budget.record_physical()
        with pytest.raises(LiveEvidenceError):
            budget.record_physical()


class TestExtractJsonObject:
    def test_plain_object_parsed(self):
        assert extract_json_object('{"status":"ok","checked":1}') == {
            "status": "ok",
            "checked": 1,
        }

    def test_code_fence_tolerated(self):
        content = '```json\n{"status": "ok", "checked": 1}\n```'
        assert extract_json_object(content)["status"] == "ok"

    def test_surrounding_prose_tolerated(self):
        assert extract_json_object('Sure: {"status":"ok","checked":1} done')["checked"] == 1

    @pytest.mark.parametrize("content", ["", "no json here", "[1,2,3]", "{not json}"])
    def test_unparseable_content_raises(self, content):
        with pytest.raises(LiveEvidenceError):
            extract_json_object(content)


class TestRefusalRequests:
    def test_all_mandated_cases_build_and_are_distinct(self):
        shapes = set()
        for case in REFUSAL_CASES:
            request = refusal_request(case, "model-a")
            shapes.add(
                (
                    request.ai_mode,
                    request.context_facts.classification,
                    request.context_facts.evidence_count,
                    request.context_facts.minimization_proven,
                    request.budget_facts.spent_today_usd_millis,
                    request.termination_facts.kill_switch_active,
                )
            )
        assert len(REFUSAL_CASES) == 6
        assert len(shapes) == 6, "each refusal case must exercise a distinct condition"

    def test_unknown_case_rejected(self):
        with pytest.raises(LiveEvidenceError):
            refusal_request("NOT_A_CASE", "model-a")

    def test_refusals_reach_provider_zero_times(self):
        """The mandated refusal set must be zero-call against a guard adapter."""
        budget = CallBudget(limit=1)
        rows = run_refusals("model-a", budget, _GuardProvider)

        assert len(rows) == 6
        for row in rows:
            assert row["accepted"] is False, row
            assert row["provider_attempts"] == 0, row
            assert row["adapter_calls"] == 0, row
            assert row["gateway_attempts"] == 0, row
        assert budget.physical == 0, "no physical call may occur during refusals"


class TestCanarySchema:
    def test_schema_is_closed_and_minimal(self):
        assert CANARY_SCHEMA["type"] == "object"
        assert CANARY_SCHEMA["additionalProperties"] is False
        assert set(CANARY_SCHEMA["required"]) == {"status", "checked"}

    def test_canonical_and_hash_are_deterministic(self):
        first = sha256_hex(canonical({"b": 1, "a": 2}))
        second = sha256_hex(canonical({"a": 2, "b": 1}))
        assert first == second and len(first) == 64
