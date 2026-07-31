"""Non-live tests for run_shift_create_live_governance_evidence.py and its
support module (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29, SPEC R12-R14).
None of these call a real provider or need Docker/PostgreSQL - every case
exercises the real in-process gate/HTTP code path or a monkeypatched
transport, asserting refusal cases make an OBSERVED zero provider calls (not
a hard-coded literal) and that no sentinel secret ever reaches a returned
summary, stdout/stderr, or the receipt file. scripts/ is not on pytest's
pythonpath, added here like every other script-importing test module in this
repo.
"""

from __future__ import annotations

import io
import sys
import urllib.error
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _shift_create_live_evidence_support as support  # noqa: E402
import run_shift_create_live_governance_evidence as runner  # noqa: E402

_SENTINEL_KEY = "sk-SENTINEL_9f8e7d3c2b1a0000000000000000000000"
_SENTINEL_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.c2lnbmF0dXJlLXBhcnQtc2VudGluZWw"
_ENDPOINT_SENTINEL = "ENDPOINT_SECRET_7c6b5a4938271605f4e3d2c1b0a9f8e7"

# P2C-MUTATION-FULL-UI-C3A1 (SPEC R31): no test-only ledger-seeding
# monkeypatch here - the real runner (now in-ceiling, Amendment 1) seeds its
# own "shift-ev-op"/"shift-ev-viewer" users before calling ShiftService.create,
# so these tests exercise its real, unmodified behavior.


def test_refusal_gate_cases_all_pass_with_observed_zero_calls():
    counter = support.ProviderCallCounter()
    results = runner.check_shift_create_refusal_gate(counter)
    assert {r["case"] for r in results} == {
        "anonymous_create_rejected",
        "malformed_token_create_rejected",
        "viewer_role_create_rejected",
        "invalid_window_create_rejected",
    }
    for r in results:
        assert r["outcome"] == "PASS", r
        assert r["calls"] == 0
    assert counter.count == 0  # the shared counter itself never moved


def test_genuine_admitted_create_construction_succeeds():
    ok, detail = runner.build_admitted_create_genuine()
    assert ok, detail
    assert "operator" in detail.lower() or "shift-ev-op" in detail


# --- SCR-BUILD-REV-F2: admission proof must not underassert R5/R6 -----------

def test_admitted_construction_rejects_a_tampered_actor_audit(monkeypatch):
    """A tampered actor_id on the persisted audit must fail the proof, not
    silently pass because only `action` was checked."""
    from workspace_api.infrastructure.repository import InMemoryLedger

    original_append_audit = InMemoryLedger.append_audit

    def _tamper(self, record, *, unit=None):
        record.actor_id = "someone-else"
        return original_append_audit(self, record, unit=unit)

    monkeypatch.setattr(InMemoryLedger, "append_audit", _tamper)
    ok, detail = runner.build_admitted_create_genuine()
    assert ok is False
    assert "audit fields did not match" in detail


def test_admitted_construction_rejects_an_unexpected_second_shift(monkeypatch):
    """An extra, unrelated shift silently present in the ledger must fail the
    proof - "exactly one persisted shift" is a hard requirement, not merely
    "the created shift can be found"."""
    from datetime import datetime, timedelta, timezone

    from operations_domain.models import Shift
    from workspace_api.infrastructure.repository import InMemoryLedger

    original_create_shift = InMemoryLedger.create_shift
    injected = {"done": False}

    def _inject_extra(self, shift, *, unit=None):
        result = original_create_shift(self, shift, unit=unit)
        if not injected["done"]:
            injected["done"] = True
            now = datetime.now(timezone.utc)
            original_create_shift(self, Shift(name="unexpected extra shift", starts_at=now, ends_at=now + timedelta(hours=1)))
        return result

    monkeypatch.setattr(InMemoryLedger, "create_shift", _inject_extra)
    ok, detail = runner.build_admitted_create_genuine()
    assert ok is False
    assert "exactly one persisted shift" in detail


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


# --- sanitization primitives -------------------------------------------------

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


# --- sentinel-bearing provider failures --------------------------------------

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
    a = support.ProviderCallCounter()
    a.record()
    a.record()
    b = support.ProviderCallCounter()
    assert a.count == 2
    assert b.count == 0


def test_render_receipt_end_to_end_never_leaks_sentinel_from_a_failing_call(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen_http_error)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="sentinel-model", api_key=_SENTINEL_KEY, endpoint="https://dashscope-intl.aliyuncs.com/v1/chat/completions",
        prompt="p", expected_token="OK", counter=counter,
    )
    print(f"outcome: {result['outcome']} error: {result.get('error')}")

    receipt_path = tmp_path / "receipt.md"
    support.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        admitted_detail="admitted ok", provider_result=result, model="sentinel-model",
        safe_endpoint=support.safe_endpoint_description("https://dashscope-intl.aliyuncs.com/v1/chat/completions"),
        call_count=counter.count,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")

    for surface in (captured.out, captured.err, receipt_text):
        assert _SENTINEL_KEY not in surface


# --- endpoint-credential failure leak ----------------------------------------

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
    assert "dashscope-intl.aliyuncs.com" in result["error"]


def test_endpoint_sentinel_absent_from_summary_stdout_stderr_and_receipt(tmp_path, monkeypatch, capsys):
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
        admitted_detail="admitted ok", provider_result=result, model="sentinel-model",
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
    provider_result = {"outcome": "PASS", "reached_server": True, "http_status": 200, "response_excerpt": "CVF_SHIFT_CREATE_EVIDENCE_OK"}
    support.render_receipt(
        tmp_path / "receipt.md", gate_results=gate_results, admitted_detail="admitted ok",
        provider_result=provider_result, model="some-model",
        safe_endpoint=support.safe_endpoint_description(runner._endpoint()), call_count=1,
    )
    text = (tmp_path / "receipt.md").read_text(encoding="utf-8")
    assert "Bearer " not in text
    assert "sk-" not in text
    assert "LIVE EVIDENCE" not in text
    assert "Overall outcome: PASS" in text
