import sys

from scripts import _p2d_live_evidence_support as support
from scripts import run_p2d_live_governance_evidence as runner


def test_refusals_observe_zero_calls_and_genuine_transition_is_durable():
    counter = support.ProviderCallCounter()
    gates = runner.refusal_matrix(counter)
    assert all(g["outcome"] == "PASS" and g["calls"] == 0 for g in gates)
    ok, detail = runner.genuine_transition()
    assert ok and "actor-bound" in detail


def test_dry_run_never_calls_provider(monkeypatch):
    called = []
    monkeypatch.setattr(runner, "call_provider", lambda **kwargs: called.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["runner", "--dry-run"])
    assert runner.main() == 0
    assert called == []


def test_receipt_is_bounded_and_sanitized(tmp_path):
    target = tmp_path / "receipt.md"
    support.render_receipt(target, [{"case": "x", "outcome": "PASS", "detail": "status 401", "calls": 0}], "durable", {"outcome": "PASS", "reached_server": True, "http_status": 200, "expected_token_match": True}, "model", "https://example.com", 1)
    text = target.read_text(encoding="utf-8")
    assert "Overall outcome: PASS" in text
    assert "Bearer " not in text and "Authorization" not in text
