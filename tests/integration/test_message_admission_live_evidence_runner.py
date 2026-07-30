"""Non-live tests for run_message_admission_live_governance_evidence.py and
its support module (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC
R16-R18/R22). No real provider/Docker/PostgreSQL - real in-process gate/HTTP
path or a monkeypatched transport; asserts refusal cases make an OBSERVED
zero provider calls and no sentinel secret ever reaches a returned summary,
stdout/stderr, or the receipt file. scripts/ is not on pytest's pythonpath,
added here like every other script-importing test module in this repo."""

from __future__ import annotations

import io
import sys
import urllib.error
from pathlib import Path

import pytest
from operations_domain.models import Message
from workspace_api.infrastructure.repository import InMemoryLedger

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _message_admission_live_evidence_support as support  # noqa: E402
import run_message_admission_live_governance_evidence as runner  # noqa: E402

_SENTINEL_KEY = "sk-SENTINEL_9f8e7d3c2b1a0000000000000000000000"
_SENTINEL_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.c2lnbmF0dXJlLXBhcnQtc2VudGluZWw"
_ENDPOINT_SENTINEL = "ENDPOINT_SECRET_7c6b5a4938271605f4e3d2c1b0a9f8e7"

def test_refusal_gate_cases_all_pass_with_observed_zero_calls():
    counter = support.ProviderCallCounter()
    results = runner.check_message_admission_refusal_gate(counter)
    assert {r["case"] for r in results} == {
        "anonymous_create_rejected", "malformed_token_create_rejected", "viewer_role_create_rejected",
        "sender_mismatch_create_rejected", "non_internal_source_create_rejected",
        "unknown_shift_create_rejected", "frozen_shift_create_rejected",
    }
    for r in results:
        assert r["outcome"] == "PASS", r
        assert r["calls"] == 0
    assert counter.count == 0  # the shared counter itself never moved

def test_refusal_gate_detects_an_injected_refusal_audit(monkeypatch):
    """MAR-BUILD-REV-F3: previously never inspected the audit log, so seven
    injected refusal audits still reported seven PASS."""
    from cvf_runtime.audit import AuditRecord

    original = runner._with_ledger
    _sentinel_audit = AuditRecord(
        actor_id="attacker", actor_role="operator", action="message.create",
        record_type="Message", record_id="00000000-0000-0000-0000-000000000000",
        control_chain=["identity", "permission", "create", "audit"], before_state=None, after_state="RAW",
    )

    def _inject_audit_after(ledger, fn):
        res = original(ledger, fn)
        ledger.append_audit(_sentinel_audit)
        return res

    monkeypatch.setattr(runner, "_with_ledger", _inject_audit_after)
    results = runner.check_message_admission_refusal_gate(support.ProviderCallCounter())
    assert all(r["outcome"] == "FAIL" for r in results), results

def test_genuine_admitted_create_construction_succeeds():
    ok, detail = runner.build_admitted_create_genuine()
    assert ok, detail
    assert "operator" in detail.lower() or "msg-ev-op" in detail

def test_admitted_construction_rejects_a_tampered_actor_audit(monkeypatch):
    """A tampered actor_id on the persisted audit must fail the proof."""
    original_append_audit = InMemoryLedger.append_audit

    def _tamper(self, record, *, unit=None):
        record.actor_id = "someone-else"
        return original_append_audit(self, record, unit=unit)

    monkeypatch.setattr(InMemoryLedger, "append_audit", _tamper)
    ok, detail = runner.build_admitted_create_genuine()
    assert ok is False
    assert "audit fields did not match" in detail

def test_admitted_construction_rejects_an_unexpected_second_message(monkeypatch):
    """An extra unrelated message in the ledger must fail the proof."""
    original_add_message = InMemoryLedger.add_message
    injected = {"done": False}

    def _inject_extra(self, message, *, unit=None):
        result = original_add_message(self, message, unit=unit)
        if not injected["done"]:
            injected["done"] = True
            original_add_message(
                self, Message(shift_id=message.shift_id, sender_id="someone", text="unexpected extra message")
            )
        return result

    monkeypatch.setattr(InMemoryLedger, "add_message", _inject_extra)
    ok, detail = runner.build_admitted_create_genuine()
    assert ok is False
    assert "exactly one persisted message" in detail

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

def test_main_facade_never_leaks_sentinel_for_malformed_configured_endpoint(monkeypatch, capsys):
    """MAR-BUILD-REV-F2 (third branch): main() called safe_endpoint_description
    before call_provider with no failure boundary of its own, so a malformed
    IPv6 base URL raised raw out of main() entirely. Drives the real facade
    (not a direct support-module call); must return non-zero without
    raising, sentinel absent from stdout/stderr/receipt."""
    import types

    fake_select_model = types.ModuleType("select_model")
    fake_select_model.select_model = lambda: "sentinel-model"
    monkeypatch.setitem(sys.modules, "select_model", fake_select_model)
    monkeypatch.setenv("DASHSCOPE_API_KEY", _SENTINEL_KEY)
    monkeypatch.setenv("DASHSCOPE_BASE_URL", f"https://user:{_ENDPOINT_SENTINEL}@[::1:bad")
    monkeypatch.setattr(sys, "argv", ["prog"])
    receipt_path = Path(runner.RECEIPT_PATH.parent) / "_test_main_facade_receipt.md"
    monkeypatch.setattr(runner, "RECEIPT_PATH", receipt_path)

    try:
        rc = runner.main()
        receipt_text = receipt_path.read_text(encoding="utf-8") if receipt_path.exists() else ""
    finally:
        receipt_path.unlink(missing_ok=True)
    assert rc != 0
    captured = capsys.readouterr()
    for surface in (captured.out, captured.err, receipt_text):
        assert _ENDPOINT_SENTINEL not in surface
        assert _SENTINEL_KEY not in surface

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

def test_safe_endpoint_description_fails_closed_on_malformed_ipv6():
    """MAR-BUILD-REV-F2 (third branch): urlsplit/.hostname raising ValueError
    for malformed IPv6 must never propagate or leak the endpoint."""
    endpoint = f"https://user:{_ENDPOINT_SENTINEL}@[::1:bad/v1/chat/completions"
    safe = support.safe_endpoint_description(endpoint)
    assert _ENDPOINT_SENTINEL not in safe

# --- sentinel-bearing provider failures --------------------------------------

def _fake_urlopen_http_error(*_a, **_kw):
    body = f"invalid key sk-... Bearer {_SENTINEL_KEY} rejected".encode()
    raise urllib.error.HTTPError("https://x/chat/completions", 401, "Unauthorized", None, io.BytesIO(body))

def _fake_urlopen_ordinary_exception(*_a, **_kw):
    raise RuntimeError(f"connection reset while sending Bearer {_SENTINEL_KEY}")

@pytest.mark.parametrize("fake_urlopen", [_fake_urlopen_http_error, _fake_urlopen_ordinary_exception])
def test_call_provider_sanitizes_failures_and_counts_exactly_once(fake_urlopen, monkeypatch):
    monkeypatch.setattr(support.urllib.request, "urlopen", fake_urlopen)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint="https://x/chat/completions",
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert result["outcome"] == "FAIL"
    assert _SENTINEL_KEY not in result["error"]

def test_render_receipt_end_to_end_never_leaks_sentinel_from_a_failing_call(tmp_path, capsys):
    result = {"outcome": "FAIL", "reached_server": True, "http_status": 401, "error": "Bearer <redacted>"}
    print(f"outcome: {result['outcome']} error: {result.get('error')}")
    receipt_path = tmp_path / "receipt.md"
    support.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        admitted_detail="admitted ok", provider_result=result, model="sentinel-model",
        safe_endpoint="https://dashscope-intl.aliyuncs.com", call_count=1,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")
    for surface in (captured.out, captured.err, receipt_text):
        assert _SENTINEL_KEY not in surface

def test_provider_call_counter_resets_per_instance():
    a = support.ProviderCallCounter()
    a.record()
    a.record()
    b = support.ProviderCallCounter()
    assert a.count == 2
    assert b.count == 0

# --- endpoint-credential failure leak / MAR-BUILD-REV-F2 (SPEC R22/AC-25) ---

def _sentinel_endpoint() -> str:
    return (
        f"https://{_ENDPOINT_SENTINEL}:{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com"
        f"/v1/chat/completions?token={_ENDPOINT_SENTINEL}#frag-{_ENDPOINT_SENTINEL}"
    )

def test_clean_endpoint_strips_userinfo_query_and_fragment():
    clean, secrets = support._clean_endpoint(_sentinel_endpoint())
    assert clean == "https://dashscope-intl.aliyuncs.com/v1/chat/completions"
    assert _ENDPOINT_SENTINEL not in clean
    assert {_ENDPOINT_SENTINEL, f"token={_ENDPOINT_SENTINEL}", f"frag-{_ENDPOINT_SENTINEL}"} <= set(secrets)

@pytest.mark.parametrize(
    "endpoint_suffix",
    [
        ":99999999/v1/chat/completions",  # out-of-range numeric port -> ValueError at .port access
        f":PORT_{_ENDPOINT_SENTINEL}/v1/chat/completions",  # non-numeric secret-bearing port
        None,  # malformed IPv6, built separately below
    ],
)
def test_call_provider_endpoint_parse_failure_returns_sanitized_failure(endpoint_suffix, tmp_path, capsys):
    """MAR-BUILD-REV-F2: out-of-range port, non-numeric secret-bearing port,
    and malformed IPv6 must all FAIL sanitized, no leak anywhere."""
    counter = support.ProviderCallCounter()
    endpoint = (
        f"https://user:{_ENDPOINT_SENTINEL}@[::1:bad/v1/chat/completions"
        if endpoint_suffix is None
        else f"https://user:{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com{endpoint_suffix}"
    )
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint=endpoint,
        prompt="p", expected_token="OK", counter=counter,
    )
    assert result["outcome"] == "FAIL"
    assert counter.count == 1
    assert _ENDPOINT_SENTINEL not in result["error"]
    assert _SENTINEL_KEY not in result["error"]

    print(f"outcome: {result['outcome']} error: {result.get('error')}", file=sys.stdout)
    receipt_path = tmp_path / "receipt.md"
    support.render_receipt(
        receipt_path, gate_results=[{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}],
        admitted_detail="admitted ok", provider_result=result, model="sentinel-model",
        safe_endpoint="https://dashscope-intl.aliyuncs.com", call_count=counter.count,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")
    for surface in (str(result), captured.out, receipt_text):
        assert _ENDPOINT_SENTINEL not in surface
        assert _SENTINEL_KEY not in surface

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

def test_write_receipt_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RECEIPT_PATH", tmp_path / "receipt.md")
    gate_results = [{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}]
    provider_result = {"outcome": "PASS", "reached_server": True, "http_status": 200, "response_excerpt": "CVF_MESSAGE_ADMISSION_EVIDENCE_OK"}
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
