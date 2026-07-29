"""Non-live tests for run_p2c_read_live_governance_evidence.py (P2C-
OPERATIONS-CONSOLE-READ-SLICE Amendment 1, SPEC R16). None of these call a
real provider or need Docker/PostgreSQL - every case exercises the real
in-process FastAPI/JWT route chain or a monkeypatched transport, asserting
refusal cases make an OBSERVED zero provider calls (not a hard-coded literal)
and that no sentinel secret ever reaches a returned summary, stdout/stderr,
or the receipt file. scripts/ is not on pytest's pythonpath, added here like
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

import run_p2c_read_live_governance_evidence as runner  # noqa: E402

_SENTINEL_KEY = "sk-SENTINEL_p2c9f8e7d3c2b1a0000000000000000000"
_SENTINEL_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.c2lnbmF0dXJlLXBhcnQtc2VudGluZWw"
_ENDPOINT_SENTINEL = "ENDPOINT_SECRET_p2c7c6b5a4938271605f4e3d2c1b0a9f8"


def test_p2c_read_refusal_gate_all_pass_with_observed_zero_calls():
    counter = runner.ProviderCallCounter()
    results = runner.check_p2c_read_refusal_gate(counter)
    assert {r["case"] for r in results} == {
        "anonymous_shifts_read_rejected",
        "malformed_token_shifts_read_rejected",
        "anonymous_events_read_rejected",
        "anonymous_open_work_read_rejected",
    }
    for r in results:
        assert r["outcome"] == "PASS", r
        assert r["calls"] == 0
    assert counter.count == 0  # the shared counter itself never moved


def test_genuine_admitted_reads_construction_succeeds():
    ok, detail = runner.build_admitted_reads_genuine()
    assert ok, detail
    assert "p2c-ev-viewer" in detail


def test_main_dry_run_stops_before_any_provider_call(monkeypatch):
    called = []
    monkeypatch.setattr(runner, "call_provider", lambda **kw: called.append(1))
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


# --- sanitization primitives -------------------------------------------------

def test_sanitize_secret_text_strips_exact_key_bearer_and_jwt():
    text = f"auth failed for Bearer {_SENTINEL_KEY}; jwt was {_SENTINEL_JWT}; raw key {_SENTINEL_KEY}"
    cleaned = runner.sanitize_secret_text(text, api_key=_SENTINEL_KEY)
    assert _SENTINEL_KEY not in cleaned
    assert _SENTINEL_JWT not in cleaned
    assert "Bearer <redacted>" in cleaned


def test_sanitize_secret_text_is_noop_for_empty_text():
    assert runner.sanitize_secret_text("", api_key=_SENTINEL_KEY) == ""
    assert runner.sanitize_secret_text(None, api_key=_SENTINEL_KEY) == ""


def test_safe_endpoint_description_strips_userinfo_query_and_fragment():
    endpoint = f"https://user:{_SENTINEL_KEY}@dashscope-intl.aliyuncs.com:443/v1/chat?token={_SENTINEL_KEY}#frag"
    safe = runner.safe_endpoint_description(endpoint)
    assert safe == "https://dashscope-intl.aliyuncs.com"
    assert _SENTINEL_KEY not in safe


def test_clean_endpoint_strips_userinfo_query_and_fragment():
    endpoint = (
        f"https://{_ENDPOINT_SENTINEL}:{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com"
        f"/v1/chat/completions?token={_ENDPOINT_SENTINEL}#frag-{_ENDPOINT_SENTINEL}"
    )
    clean, secrets = runner._clean_endpoint(endpoint)
    assert clean == "https://dashscope-intl.aliyuncs.com/v1/chat/completions"
    assert _ENDPOINT_SENTINEL not in clean
    assert set(secrets) == {_ENDPOINT_SENTINEL, f"token={_ENDPOINT_SENTINEL}", f"frag-{_ENDPOINT_SENTINEL}"}


# --- sentinel-bearing provider failures --------------------------------------

def _fake_urlopen_http_error(*_a, **_kw):
    body = f"invalid key sk-... Bearer {_SENTINEL_KEY} rejected".encode()
    raise urllib.error.HTTPError("https://x/chat/completions", 401, "Unauthorized", None, io.BytesIO(body))


def test_call_provider_sanitizes_http_error_body_and_counts_exactly_once(monkeypatch):
    monkeypatch.setattr(runner.urllib.request, "urlopen", _fake_urlopen_http_error)
    counter = runner.ProviderCallCounter()
    result = runner.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint="https://x/chat/completions",
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert result["outcome"] == "FAIL"
    assert _SENTINEL_KEY not in result["error"]
    assert "Bearer <redacted>" in result["error"]


def test_call_provider_transport_exception_embedding_full_url_never_leaks_endpoint_sentinel(monkeypatch):
    endpoint = f"https://{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com/v1/chat/completions"

    def _fake_urlopen(req, timeout=60):
        raise RuntimeError(f"connection refused: {req.full_url}")

    monkeypatch.setattr(runner.urllib.request, "urlopen", _fake_urlopen)
    counter = runner.ProviderCallCounter()
    result = runner.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint=endpoint,
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert _ENDPOINT_SENTINEL not in result["error"]
    assert "dashscope-intl.aliyuncs.com" in result["error"]


def test_provider_call_counter_resets_per_instance():
    """SPEC R15-B: accounting is per-invocation, never a persistent module
    global that could carry a stale count across runs/tests."""
    a = runner.ProviderCallCounter()
    a.record()
    a.record()
    b = runner.ProviderCallCounter()
    assert a.count == 2
    assert b.count == 0


def test_render_receipt_end_to_end_never_leaks_sentinel_from_a_failing_call(tmp_path, capsys):
    """Full pipeline: a provider failure carrying the sentinel key must not
    surface in the returned summary, stdout/stderr, or the written receipt."""
    result = {"outcome": "FAIL", "reached_server": True, "http_status": 401,
              "error": f"Bearer <redacted> from {_SENTINEL_KEY}".replace(_SENTINEL_KEY, "<redacted-key>"),
              "started_at": "2026-07-29T00:00:00+00:00"}
    print(f"outcome: {result['outcome']} error: {result.get('error')}")

    receipt_path = tmp_path / "receipt.md"
    runner.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        admitted_detail="admitted ok", provider_result=result, model="sentinel-model",
        safe_endpoint="https://dashscope-intl.aliyuncs.com", call_count=1,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")
    for surface in (captured.out, captured.err, receipt_text):
        assert _SENTINEL_KEY not in surface


def test_write_receipt_is_sanitized(tmp_path):
    provider_result = {"outcome": "PASS", "reached_server": True, "http_status": 200,
                        "response_excerpt": "CVF_P2C_READ_EVIDENCE_OK"}
    receipt_path = tmp_path / "receipt.md"
    runner.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        admitted_detail="admitted ok", provider_result=provider_result, model="some-model",
        safe_endpoint="https://dashscope-intl.aliyuncs.com", call_count=1,
    )
    text = receipt_path.read_text(encoding="utf-8")
    assert "Bearer " not in text
    assert "sk-" not in text
    assert "LIVE EVIDENCE" not in text  # written by main(), not render_receipt()
    assert "Overall outcome: PASS" in text
