import json
import hashlib
import sys
from types import SimpleNamespace

from scripts import _phase2_full_shift_live_evidence_support as support
from scripts import run_phase2_full_shift_live_governance_evidence as runner


def browser_file(tmp_path):
    path = tmp_path / "browser.json"
    harness = {
        "checkpoint": "P2_FULL_SHIFT_EXIT", "api_port": 41001, "vite_port": 41002,
        "static_smoke": True, "static_assets_checked": ["/assets/app.js"],
        "playwright_pass": True, "queue_checkpoint": "bounded_exercised_and_cleaned",
        "queue_checkpoint_pass": True,
    }
    assertions = {
        "schema_version": 1, "producer_id": support.PRODUCER_ID, "run_id": "00000000-0000-4000-8000-000000000002",
        "browser_contract": {
            "positive_actions": "rendered_ui", "transport_requests": 1,
            "automatic_retries": 0, "queue_insertions": 0,
            "authoritative_reconciliation": True,
        },
        "task_reconciliation": {
            "fresh_get_after_replay": True, "exact_task_id": True,
            "exact_committed_version": True, "status_in_progress": True,
            "dom_after_get": True,
        },
    }
    path.write_text(json.dumps({
        "schema_version": 1, "producer_id": support.PRODUCER_ID, "run_id": "00000000-0000-4000-8000-000000000002",
        "checkpoint": "P2_FULL_SHIFT_EXIT", "playwright_pass": True,
        "queue_checkpoint": "bounded_exercised_and_cleaned", "queue_checkpoint_pass": True,
        "sanitized": True,
        "spec_sha256": hashlib.sha256(support.SPEC_PATH.read_bytes()).hexdigest(),
        "harness_payload": harness, "harness_sha256": support.canonical_digest(harness),
        "assertions": assertions,
    }), encoding="utf-8")
    return path


def test_refusal_matrix_zero_calls_and_integrated_scenario_is_durable():
    counter = support.ProviderCallCounter()
    gates = runner.refusal_matrix(counter)
    assert all(gate["outcome"] == "PASS" and gate["calls"] == 0 for gate in gates)
    passed, detail = support.integrated_scenario()
    assert passed and "12-hour" in detail


def test_refusal_matrix_fails_if_whole_ledger_fingerprint_changes(monkeypatch):
    original = runner.ledger_fingerprint
    invocation = 0

    def changed_after_request(ledger):
        nonlocal invocation
        invocation += 1
        fingerprint = original(ledger)
        if invocation % 2 == 0:
            fingerprint["sha256"] = "0" * 64
        return fingerprint

    monkeypatch.setattr(runner, "ledger_fingerprint", changed_after_request)
    gates = runner.refusal_matrix(support.ProviderCallCounter())
    assert gates and all(gate["outcome"] == "FAIL" for gate in gates)


def test_integrated_scenario_rejects_wrong_actor_even_when_actions_exist(monkeypatch):
    ledger = support.new_ledger()
    original = ledger.append_audit

    def tamper_actor(record, *, unit=None):
        if record.action == "report.freeze":
            record = record.model_copy(update={"actor_id": "wrong-actor"})
        return original(record, unit=unit)

    monkeypatch.setattr(ledger, "append_audit", tamper_actor)
    monkeypatch.setattr(support, "new_ledger", lambda: ledger)
    passed, _ = support.integrated_scenario()
    assert passed is False


def test_dry_run_validates_browser_and_never_calls_provider(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(runner, "call_provider", lambda **kwargs: called.append(kwargs))
    assert runner.main(["--browser-evidence-json", str(browser_file(tmp_path)), "--dry-run"]) == 0
    assert called == []


def test_provider_admission_requires_exact_parent_rehearsal(tmp_path, monkeypatch):
    monkeypatch.delenv("PHASE2_EXACT_PARENT_REHEARSAL", raising=False)
    monkeypatch.setattr(runner, "refusal_matrix", lambda counter: [])
    monkeypatch.setattr(runner, "integrated_scenario", lambda: (True, "durable"))
    assert runner.main(["--browser-evidence-json", str(browser_file(tmp_path))]) == 4


def test_provider_admission_refuses_third_call_when_replacement_already_exists(tmp_path, monkeypatch):
    receipt = tmp_path / "receipt.md"
    receipt.write_text("INVALIDATED_BY_REVIEW_FAIL\n\n## Replacement provider attempt reservation\n", encoding="utf-8")
    called = []
    monkeypatch.setenv("PHASE2_EXACT_PARENT_REHEARSAL", "PASS")
    monkeypatch.setattr(runner, "RECEIPT", receipt)
    monkeypatch.setattr(runner, "refusal_matrix", lambda counter: [])
    monkeypatch.setattr(runner, "integrated_scenario", lambda: (True, "durable"))
    monkeypatch.setattr(runner, "call_provider", lambda **kwargs: called.append(kwargs))
    assert runner.main(["--browser-evidence-json", str(browser_file(tmp_path))]) == 5
    assert called == []


def _admitted_runner(tmp_path, monkeypatch, receipt):
    monkeypatch.setenv("PHASE2_EXACT_PARENT_REHEARSAL", "PASS")
    monkeypatch.setenv("ALIBABA_API_KEY", "test-only-not-a-real-key")
    monkeypatch.setitem(sys.modules, "select_model", SimpleNamespace(select_model=lambda: "test-model"))
    monkeypatch.setattr(runner, "RECEIPT", receipt)
    monkeypatch.setattr(runner, "refusal_matrix", lambda counter: [])
    monkeypatch.setattr(runner, "integrated_scenario", lambda: (True, "durable"))
    return ["--browser-evidence-json", str(browser_file(tmp_path))]


def test_call_success_receipt_failure_burns_slot_and_rerun_cannot_call(tmp_path, monkeypatch):
    receipt = tmp_path / "receipt.md"
    receipt.write_text("INVALIDATED_BY_REVIEW_FAIL\n", encoding="utf-8")
    argv = _admitted_runner(tmp_path, monkeypatch, receipt)
    calls = []

    def fake_call(**kwargs):
        kwargs["counter"].record()
        calls.append(1)
        return {"outcome": "PASS", "reached_server": True, "http_status": 200, "expected_token_match": True}

    monkeypatch.setattr(runner, "call_provider", fake_call)
    monkeypatch.setattr(runner, "render_receipt", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("crash")))
    assert runner.main(argv) == 5
    assert len(calls) == 1 and "RESERVED_BEFORE_NETWORK" in receipt.read_text(encoding="utf-8")
    assert runner.main(argv) == 5
    assert len(calls) == 1


def test_provider_failure_is_recorded_not_accepted_and_rerun_cannot_call(tmp_path, monkeypatch):
    receipt = tmp_path / "receipt.md"
    receipt.write_text("INVALIDATED_BY_REVIEW_FAIL\n", encoding="utf-8")
    argv = _admitted_runner(tmp_path, monkeypatch, receipt)
    calls = []

    def fake_call(**kwargs):
        kwargs["counter"].record()
        calls.append(1)
        return {"outcome": "FAIL", "reached_server": True, "http_status": 500, "expected_token_match": False}

    monkeypatch.setattr(runner, "call_provider", fake_call)
    assert runner.main(argv) == 1
    text = receipt.read_text(encoding="utf-8")
    assert "NOT_ACCEPTED_PROVIDER_FAILURE" in text and "Accepted final calls: **0**" in text
    assert runner.main(argv) == 5
    assert len(calls) == 1


def test_invalid_browser_evidence_fails_before_refusals(tmp_path, monkeypatch):
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"playwright_pass": true}', encoding="utf-8")
    called = []
    monkeypatch.setattr(runner, "refusal_matrix", lambda counter: called.append(counter))
    assert runner.main(["--browser-evidence-json", str(invalid), "--dry-run"]) == 3
    assert called == []
