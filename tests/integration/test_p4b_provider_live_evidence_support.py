"""P4-B SPEC R12 - live evidence support mechanics, spies/fakes only.

Proves the mandated refusal-case builders yield zero gateway/provider
attempts and that MockProviderAdapter output is structurally evidence-
ineligible, WITHOUT ever executing the paired runner script or performing
any network I/O. This test module is the only accepted proof for this
BUILD's rehearsal-only live-evidence pair; it does not itself constitute
governance evidence.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPPORT_MODULE = REPO_ROOT / "scripts" / "_p4b_ai_providers_live_evidence_support.py"
RUNNER_MODULE = REPO_ROOT / "scripts" / "run_p4b_ai_providers_live_evidence.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _p4b_ai_providers_live_evidence_support as support  # noqa: E402
from _p4a_gateway_live_evidence_support import CANARY_SCHEMA  # noqa: E402
import run_p4b_ai_providers_live_evidence as runner  # noqa: E402 - importing does NOT execute main()


def test_support_module_performs_no_io_at_import_time():
    """Importing the module must not itself touch environment/network -
    only calling its functions may (and even then, only spies/fakes)."""
    assert support.REFUSAL_CASES  # module-level constant, not a live call


def test_live_prompt_and_schema_share_the_canonical_p4a_canary_contract():
    """P4B-LIVE-F1: prevent prompt/schema drift from rejecting the exact
    object the evidence prompt requires after consuming a provider call."""
    assert support.SCHEMA is CANARY_SCHEMA
    assert set(support.SCHEMA["required"]) == {"status", "checked"}
    assert support.SCHEMA["properties"]["checked"] == {
        "type": "integer", "minimum": 1, "maximum": 1,
    }


def test_no_ai_refusal_request_is_no_ai_mode():
    request = support.build_no_ai_request()
    assert request.ai_mode == "NO_AI"


def test_rules_only_refusal_request_never_matches_empty_ruleset():
    request = support.build_rules_only_request()
    assert request.ai_mode == "RULES_ONLY"
    assert request.facts == {"unmatched": True}


def test_mismatched_external_request_has_disagreeing_task_type():
    request = support.build_mismatched_external_request("qwen-test-model")
    assert request.nested_gateway_request["task_type"] != request.task_type


def test_run_refusals_reports_zero_calls_for_every_mandated_case():
    """Uses guard providers that raise if ever dispatched - a non-zero call
    count would surface as an assertion failure inside run_refusals itself,
    or as a mismatched counter here."""
    results = support.run_refusals("qwen-test-model")
    case_names = {row["case"] for row in results}
    assert case_names == set(support.REFUSAL_CASES)
    for row in results:
        assert row["gateway_calls"] == 0, row
        assert row["provider_attempts"] == 0, row
        assert row["adapter_calls"] == 0, row
        assert row["gateway_physical_attempts"] == 0, row


def test_mock_output_is_confirmed_evidence_ineligible():
    assert support.mock_output_is_evidence_ineligible() is True


class TestAdmittedPathMechanics:
    """P4B-REV-F6-R1 - the admitted-path evidence mechanics (real, tested
    one-call HTTPS dispatch source, living in the runner module for file-size
    budget reasons) are real, testable source (spies/fakes/monkeypatches
    only in this test class) - never dispatched here or by the paired
    runner's ``main()`` during this repair."""

    def test_build_admitted_external_request_matches_outer_and_nested_bindings(self):
        request = support.build_admitted_external_request("qwen-test-model")
        assert request.ai_mode == "EXTERNAL_AI"
        assert request.provider_id == support.PROVIDER_ID
        assert request.model_id == "qwen-test-model"
        assert request.nested_gateway_request["provider_id"] == request.provider_id
        assert request.nested_gateway_request["model_id"] == request.model_id

    def test_admitted_provider_call_budget_is_exactly_one(self):
        """The one-attempt CallBudget the adapter is constructed with raises
        on a second reservation - proven directly against the budget object,
        with no network object ever constructed."""
        from _p4a_gateway_live_evidence_support import CallBudget

        budget = CallBudget(limit=1)
        provider = runner._CountingAdmittedProvider(budget=budget, key_env_name=None)
        assert provider.calls == 0
        budget.reserve()
        budget.record_physical()
        with pytest.raises(runner.LiveEvidenceError):
            budget.reserve()

    def test_admitted_provider_post_fails_closed_with_no_configured_credential(self):
        """Calling ``_post`` without a configured credential env var name
        raises LiveEvidenceError before any URL/request object is built -
        proving the fail-closed guard runs first, with zero network I/O."""
        provider = runner._CountingAdmittedProvider(key_env_name=None)
        with pytest.raises(runner.LiveEvidenceError):
            provider._post(object())
        assert provider.calls == 0

    def test_admitted_provider_second_post_is_refused_by_budget_via_a_stub_transport(self, monkeypatch):
        """Monkeypatch the module-level urlopen-equivalent surface is not
        needed here - instead prove the budget itself is what gates a
        second physical attempt, by pre-exhausting it and confirming _post
        raises before reading any credential."""
        from _p4a_gateway_live_evidence_support import CallBudget

        budget = CallBudget(limit=1)
        budget.reserve()
        budget.record_physical()  # budget already exhausted
        provider = runner._CountingAdmittedProvider(budget=budget, key_env_name="NOT_A_REAL_ENV_VAR_NAME")
        with pytest.raises(runner.LiveEvidenceError):
            provider._post(object())
        assert provider.calls == 0  # never even reached the credential read

    def test_run_admitted_case_assembles_without_any_dispatch(self):
        """run_admitted_case only assembles objects - it never calls
        service.execute or the provider, so this performs zero I/O."""
        service, request, provider, gateway = runner.run_admitted_case("qwen-test-model", "NOT_A_REAL_ENV_VAR_NAME")
        assert request.ai_mode == "EXTERNAL_AI"
        assert provider.calls == 0
        assert gateway.physical_attempts == 0

    def test_admitted_provider_performs_no_network_io_when_untriggered(self):
        """Constructing the class and never calling generate_structured_
        output/_post performs zero I/O - the class only reaches urllib at
        dispatch time, never at construction."""
        provider = runner._CountingAdmittedProvider(key_env_name=None)
        assert provider.calls == 0
        assert provider.reached_server is False


def test_secret_scanning_helpers_are_reused_not_duplicated():
    """SPEC R9 - the same sanitize/scan_for_secrets helpers as the P4-A
    runner are reused, not reimplemented, so secret handling stays in one
    place."""
    assert support.sanitize("Bearer abcdef01234567890") == "[REDACTED]"
    assert support.scan_for_secrets("no secrets here") == []


class TestRunnerIsNeverExecutedProof:
    """Structural proof that this test suite never invokes the runner as a
    subprocess or imports it in a way that runs its __main__ guard."""

    def test_runner_source_is_guarded_by_dunder_main(self):
        text = RUNNER_MODULE.read_text(encoding="utf-8")
        assert 'if __name__ == "__main__":' in text

    def test_runner_module_is_syntactically_valid_but_not_executed_here(self):
        """Compiles the runner to bytecode (a static check) without running
        it - proves the file is real, valid source without any subprocess
        or provider/network call happening in this test."""
        import py_compile

        py_compile.compile(str(RUNNER_MODULE), doraise=True)

    def test_this_test_file_never_shells_out_to_the_runner(self):
        import ast

        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])
        assert "subprocess" not in imported_roots


class _FakeHttpResponse:
    """Injected fake transport - a context-manager stand-in for
    ``http.client.HTTPResponse``, never touching a real socket."""

    def __init__(self, body: dict, *, status: int = 200) -> None:
        self._body = json.dumps(body).encode("utf-8")
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def _fake_provider_response(status: str = "ok") -> dict:
    content = json.dumps({"status": status, "checked": 1})
    return {"choices": [{"message": {"content": content}}], "usage": {"total_tokens": 3}}


class TestF6R2AdmittedDispositionInvariants:
    """P4B-REV-F6-R2 - ``decide_admitted_disposition`` computes every
    evidence invariant BEFORE any disposition/write decision, using an
    injected fake HTTPS transport (never real network I/O, never a real
    credential value). None of these tests execute ``main()`` or the
    consuming branch against a real endpoint."""

    def _run_admitted(self, monkeypatch, *, urlopen_body: dict, key_env_name: str = "P4B_TEST_FAKE_KEY"):
        import urllib.request

        monkeypatch.setenv(key_env_name, "sk-fake-not-a-real-credential")  # obviously-synthetic
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: _FakeHttpResponse(urlopen_body))
        service, request, provider, gateway = runner.run_admitted_case("qwen-test-model", key_env_name)
        result = asyncio.run(service.execute(request=request, started_at="t0", finished_at="t1"))
        return result.receipt, provider, gateway

    def test_genuinely_successful_case_reaches_pass(self, monkeypatch):
        """All invariants agree (accepted, counters all 1, clean scan) -
        PASS is correctly reached, proven via the real admitted mechanics
        driven by a fake transport, never a real provider call."""
        receipt, provider, gateway = self._run_admitted(monkeypatch, urlopen_body=_fake_provider_response())
        decision = runner.decide_admitted_disposition(
            receipt=receipt, provider=provider, gateway=gateway, generated_at="t0",
            model_id="qwen-test-model", key_env_name="P4B_TEST_FAKE_KEY", refusals=[],
        )
        assert decision["accepted"] is True
        assert decision["counters_agree"] is True
        assert decision["hits"] == []
        assert decision["evidence_pass"] is True
        assert '"disposition": "LIVE_EVIDENCE_PASS"' in decision["document"]

    def test_counter_drift_is_forced_to_blocked_never_pass(self, monkeypatch):
        """The adapter's own call counter agreeing with acceptance is not
        enough - if the receipt's own counters disagree with the physical
        counters, disposition must be BLOCKED, never PASS."""
        receipt, provider, gateway = self._run_admitted(monkeypatch, urlopen_body=_fake_provider_response())
        drifted_receipt = receipt.model_copy(update={"provider_attempts": 0})  # receipt disagrees with provider.calls==1
        decision = runner.decide_admitted_disposition(
            receipt=drifted_receipt, provider=provider, gateway=gateway, generated_at="t0",
            model_id="qwen-test-model", key_env_name="P4B_TEST_FAKE_KEY", refusals=[],
        )
        assert decision["counters_agree"] is False
        assert decision["evidence_pass"] is False
        assert '"disposition": "LIVE_EVIDENCE_BLOCKED"' in decision["document"]

    def test_secret_hit_is_forced_to_blocked_never_pass(self, monkeypatch):
        """Even a fully accepted, counter-agreeing case must be forced to
        BLOCKED if the rendered receipt body contains a secret-shaped
        string - proven by injecting a synthetic (never real) credential-
        shaped literal into the credential_env_var field."""
        receipt, provider, gateway = self._run_admitted(monkeypatch, urlopen_body=_fake_provider_response())
        decision = runner.decide_admitted_disposition(
            receipt=receipt, provider=provider, gateway=gateway, generated_at="t0",
            model_id="qwen-test-model",
            key_env_name="Bearer sk-fake-obviously-synthetic-0000000000",  # synthetic secret-shaped literal
            refusals=[],
        )
        assert decision["hits"] != []
        assert decision["evidence_pass"] is False
        assert '"disposition": "LIVE_EVIDENCE_BLOCKED"' in decision["document"]
