"""Non-live tests for run_incident_live_governance_evidence.py and its
support module (P2A-INCIDENT-VERTICAL, SPEC R14/R15-A/R15-B). None of these
call a real provider or need Docker/PostgreSQL - every case exercises the
real in-process gate/HTTP code path or a monkeypatched transport, asserting
refusal cases make an OBSERVED zero provider calls (not a hard-coded literal)
and that no sentinel secret ever reaches a returned summary, stdout/stderr, or
the receipt file. scripts/ is not on pytest's pythonpath, added here like
every other script-importing test module in this repo.
"""

from __future__ import annotations

import io
import sys
import urllib.error
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _incident_live_evidence_support as support  # noqa: E402
import run_incident_live_governance_evidence as runner  # noqa: E402

_SENTINEL_KEY = "sk-SENTINEL_9f8e7d3c2b1a0000000000000000000000"
_SENTINEL_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.c2lnbmF0dXJlLXBhcnQtc2VudGluZWw"
# INC-REV-F6: deliberately DISTINCT from _SENTINEL_KEY - this one lives only
# in the endpoint URL's userinfo/query/fragment, never in the API key.
_ENDPOINT_SENTINEL = "ENDPOINT_SECRET_7c6b5a4938271605f4e3d2c1b0a9f8e7"


def test_incident_gate_refusal_cases_all_pass_with_observed_zero_calls():
    counter = support.ProviderCallCounter()
    results = runner.check_incident_gate(counter)
    assert {r["case"] for r in results} == {
        "insufficient_evidence_rejected",
        "fabricated_approval_rejected",
        "self_approval_rejected",
        "inactive_approver_rejected",
        "stale_version_rejected",
    }
    for r in results:
        assert r["outcome"] == "PASS", r
        assert r["calls"] == 0
    assert counter.count == 0  # the shared counter itself never moved


def test_genuine_acknowledgement_construction_succeeds():
    ok, detail = runner.build_and_acknowledge_genuine()
    assert ok, detail
    assert "inc-ev-sup2" in detail and "inc-ev-sup1" in detail


def test_main_dry_run_stops_before_any_provider_call(monkeypatch):
    called = []
    monkeypatch.setattr(support, "call_provider", lambda **kw: called.append(1))
    monkeypatch.setattr(sys, "argv", ["prog", "--dry-run"])
    assert runner.main() == 0
    assert called == []


def test_main_reports_blocked_when_credential_missing(monkeypatch):
    for name in runner.KEY_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(sys, "argv", ["prog"])
    assert runner.main() == 2


def test_key_present_detects_either_env_var(monkeypatch):
    for name in runner.KEY_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    present, _ = runner._key_present()
    assert present is False
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sentinel-value-not-a-real-key")
    present, name = runner._key_present()
    assert present is True and name == "DASHSCOPE_API_KEY"


# --- INC-REV-F5: sanitization primitives ------------------------------------

def test_sanitize_secret_text_strips_exact_key_bearer_and_jwt():
    text = f"auth failed for Bearer {_SENTINEL_KEY}; jwt was {_SENTINEL_JWT}; raw key {_SENTINEL_KEY}"
    cleaned = support.sanitize_secret_text(text, api_key=_SENTINEL_KEY)
    assert _SENTINEL_KEY not in cleaned
    assert _SENTINEL_JWT not in cleaned
    assert "Bearer <redacted>" in cleaned


def test_sanitize_secret_text_is_noop_for_empty_text():
    assert support.sanitize_secret_text("", api_key=_SENTINEL_KEY) == ""
    assert support.sanitize_secret_text(None, api_key=_SENTINEL_KEY) == ""


def test_safe_endpoint_description_strips_userinfo_query_and_fragment():
    endpoint = f"https://user:{_SENTINEL_KEY}@dashscope-intl.aliyuncs.com:443/v1/chat?token={_SENTINEL_KEY}#frag"
    safe = support.safe_endpoint_description(endpoint)
    assert safe == "https://dashscope-intl.aliyuncs.com"
    assert _SENTINEL_KEY not in safe


# --- INC-REV-F5: sentinel-bearing provider failures -------------------------

def _fake_urlopen_http_error(*_a, **_kw):
    body = f"invalid key sk-... Bearer {_SENTINEL_KEY} rejected".encode()
    raise urllib.error.HTTPError("https://x/chat/completions", 401, "Unauthorized", None, io.BytesIO(body))


def _fake_urlopen_ordinary_exception(*_a, **_kw):
    raise RuntimeError(f"connection reset while sending Bearer {_SENTINEL_KEY}")


def test_call_provider_sanitizes_http_error_body_and_counts_exactly_once(monkeypatch):
    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen_http_error)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint="https://x/chat/completions",
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert result["outcome"] == "FAIL"
    assert _SENTINEL_KEY not in result["error"]
    assert "Bearer <redacted>" in result["error"]


def test_call_provider_sanitizes_ordinary_exception_and_counts_exactly_once(monkeypatch):
    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen_ordinary_exception)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint="https://x/chat/completions",
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert _SENTINEL_KEY not in result["error"]


def test_provider_call_counter_resets_per_instance():
    """SPEC R15-B: accounting is per-invocation, never a persistent module
    global that could carry a stale count across runs/tests."""
    monkeypatch_counter_a = support.ProviderCallCounter()
    monkeypatch_counter_a.record()
    monkeypatch_counter_a.record()
    monkeypatch_counter_b = support.ProviderCallCounter()
    assert monkeypatch_counter_a.count == 2
    assert monkeypatch_counter_b.count == 0


def test_render_receipt_end_to_end_never_leaks_sentinel_from_a_failing_call(tmp_path, monkeypatch, capsys):
    """Full pipeline: a provider failure carrying the sentinel key must not
    surface in the returned summary, stdout/stderr, or the written receipt."""
    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen_http_error)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="sentinel-model", api_key=_SENTINEL_KEY, endpoint="https://dashscope-intl.aliyuncs.com/v1/chat/completions",
        prompt="p", expected_token="OK", counter=counter,
    )
    print(f"outcome: {result['outcome']} error: {result.get('error')}")  # simulates the runner's own stdout line

    receipt_path = tmp_path / "receipt.md"
    support.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        quorum_detail="quorum ok", provider_result=result, model="sentinel-model",
        safe_endpoint=support.safe_endpoint_description("https://dashscope-intl.aliyuncs.com/v1/chat/completions"),
        call_count=counter.count,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")

    for surface in (captured.out, captured.err, receipt_text):
        assert _SENTINEL_KEY not in surface


# --- INC-REV-F6: endpoint-credential failure leak ---------------------------

def _sentinel_endpoint() -> str:
    return (
        f"https://{_ENDPOINT_SENTINEL}:{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com"
        f"/v1/chat/completions?token={_ENDPOINT_SENTINEL}#frag-{_ENDPOINT_SENTINEL}"
    )


def test_clean_endpoint_strips_userinfo_query_and_fragment():
    clean, secrets = support._clean_endpoint(_sentinel_endpoint())
    assert clean == "https://dashscope-intl.aliyuncs.com/v1/chat/completions"
    assert _ENDPOINT_SENTINEL not in clean
    assert set(secrets) == {_ENDPOINT_SENTINEL, f"token={_ENDPOINT_SENTINEL}", f"frag-{_ENDPOINT_SENTINEL}"}


def test_call_provider_transport_exception_embedding_full_url_never_leaks_endpoint_sentinel(monkeypatch):
    """The exception is built FROM req.full_url itself (mirroring real
    urllib behaviour) - proving the absence is structural (the endpoint was
    already clean by the time Request() was built), not incidental."""
    def _fake_urlopen(req, timeout=60):
        raise RuntimeError(f"connection refused: {req.full_url}")

    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint=_sentinel_endpoint(),
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert _ENDPOINT_SENTINEL not in result["error"]
    assert "dashscope-intl.aliyuncs.com" in result["error"]  # the clean host is still informative


def test_call_provider_request_construction_failure_never_leaks_endpoint_sentinel(monkeypatch):
    """Covers construction failures, not just transport ones: the fake
    Request() constructor raises using the exact url it received - which is
    already the cleaned endpoint, thanks to _clean_endpoint running first."""
    def _fake_request_ctor(url, *a, **kw):
        raise ValueError(f"cannot construct request for url={url}")

    monkeypatch.setattr(support.urllib.request, "Request", _fake_request_ctor)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint=_sentinel_endpoint(),
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert _ENDPOINT_SENTINEL not in result["error"]


def test_endpoint_sentinel_absent_from_summary_stdout_stderr_and_receipt(tmp_path, monkeypatch, capsys):
    """Full pipeline, end to end: a transport exception embedding the real
    req.full_url of a credential-laden endpoint must not leak that endpoint
    sentinel into the returned summary, stdout, stderr, or the receipt."""
    def _fake_urlopen(req, timeout=60):
        raise RuntimeError(f"connection refused: {req.full_url}")

    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="sentinel-model", api_key=_SENTINEL_KEY, endpoint=_sentinel_endpoint(),
        prompt="p", expected_token="OK", counter=counter,
    )
    print(f"outcome: {result['outcome']} error: {result.get('error')}", file=sys.stdout)
    print(f"outcome: {result['outcome']}", file=sys.stderr)

    receipt_path = tmp_path / "receipt.md"
    support.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        quorum_detail="quorum ok", provider_result=result, model="sentinel-model",
        safe_endpoint=support.safe_endpoint_description(_sentinel_endpoint()), call_count=counter.count,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")

    import json as _json
    surfaces = [_json.dumps(result), captured.out, captured.err, receipt_text]
    for surface in surfaces:
        assert _ENDPOINT_SENTINEL not in surface


def test_write_receipt_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RECEIPT_PATH", tmp_path / "receipt.md")
    gate_results = [{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}]
    provider_result = {"outcome": "PASS", "reached_server": True, "http_status": 200, "response_excerpt": "CVF_INCIDENT_EVIDENCE_OK"}
    support.render_receipt(
        tmp_path / "receipt.md", gate_results=gate_results, quorum_detail="quorum ok",
        provider_result=provider_result, model="some-model",
        safe_endpoint=support.safe_endpoint_description(runner._endpoint()), call_count=1,
    )
    text = (tmp_path / "receipt.md").read_text(encoding="utf-8")
    # No raw key/token material - the sentence *mentioning* "Authorization
    # header" as a claim-boundary statement is fine, an actual header value
    # ("Bearer <token>") is not.
    assert "Bearer " not in text
    assert "sk-" not in text
    assert "LIVE EVIDENCE" not in text  # written by main(), not render_receipt()
    assert "Overall outcome: PASS" in text
