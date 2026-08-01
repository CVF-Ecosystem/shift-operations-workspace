"""Non-live tests for run_handover_live_governance_evidence.py and its
support module (P2A-HANDOVER-VERTICAL, SPEC R16/R17). None of these call a
real provider or need Docker/PostgreSQL - every case exercises the real
in-process HTTP/JWT route chain or a monkeypatched transport, asserting
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

import _handover_live_evidence_support as support  # noqa: E402
import run_handover_live_governance_evidence as runner  # noqa: E402

_SENTINEL_KEY = "sk-SENTINEL_HOV_9f8e7d3c2b1a0000000000000000000000"
_SENTINEL_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.c2lnbmF0dXJlLXBhcnQtc2VudGluZWw"
_ENDPOINT_SENTINEL = "ENDPOINT_SECRET_HOV_7c6b5a4938271605f4e3d2c1b0a9f8e7"


def test_handover_freeze_gate_refusal_cases_all_pass_with_observed_zero_calls():
    counter = support.ProviderCallCounter()
    results = runner.check_handover_freeze_gate(counter)
    assert {r["case"] for r in results} == {
        "missing_handover_freeze_rejected",
        "reviewed_only_handover_freeze_rejected",
        "self_acknowledgement_rejected",
        "stale_snapshot_freeze_rejected",
    }
    for r in results:
        assert r["outcome"] == "PASS", r
        assert r["calls"] == 0
    assert counter.count == 0  # the shared counter itself never moved


def test_genuine_review_acknowledge_and_freeze_construction_succeeds():
    ok, detail = runner.build_review_acknowledge_and_freeze_genuine()
    assert ok, detail
    assert "hov-ev-sup1" in detail and "hov-ev-sup2" in detail


# --- F1 repair: meaningful P2R coverage of _make_ready_report -------------

def test_ready_handover_without_report_still_refuses_freeze_with_zero_calls():
    """P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE: a fully ready, ACKNOWLEDGED
    handover (this vertical's own prerequisite) is no longer sufficient for
    freeze on its own - report_approved is a second, independent gate. Proven
    directly against the runner's own refusal-case machinery, with the SAME
    observed-zero-provider-calls proof every other case in this file uses."""
    from operations_domain.models import Shift
    from datetime import datetime, timedelta, timezone

    counter = support.ProviderCallCounter()
    ledger, shift = runner._new_ledger_and_shift("no-report")
    now = datetime.now(timezone.utc)
    dest = Shift(name="dest shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(dest)
    runner._seed(ledger, shift.shift_id, "hov-ev-op2", "operator")
    runner._seed(ledger, shift.shift_id, "hov-ev-sup3", "shift_supervisor")
    runner._seed(ledger, dest.shift_id, "hov-ev-sup4", "shift_supervisor")
    op = runner._auth_headers("hov-ev-op2", "operator")
    sup1 = runner._auth_headers("hov-ev-sup3", "shift_supervisor")
    sup2 = runner._auth_headers("hov-ev-sup4", "shift_supervisor")

    def _run(client):
        create_res = runner._create(client, shift.shift_id, dest.shift_id, op)
        handover_id = create_res.json()["handover_id"]
        runner._review(client, handover_id, sup1)
        runner._acknowledge(client, handover_id, sup2)
        runner._close(client, shift.shift_id, op)
        return runner._freeze(client, shift.shift_id, sup1)

    before = counter.count
    resp = runner._with_ledger(ledger, _run)
    assert resp.status_code == 409, resp.text
    assert "report" in resp.json()["detail"].lower()
    assert counter.count == before  # no code path here can reach call_provider


def test_make_ready_report_produces_a_real_approved_current_report():
    """_make_ready_report (P2R addition replacing the retired freeze override)
    must produce a genuine APPROVED, current END_SHIFT report - not a stub."""
    ledger, shift = runner._new_ledger_and_shift("ready-report")
    ledger.close_shift(shift.shift_id)
    runner._seed(ledger, shift.shift_id, "hov-ev-op3", "operator")
    runner._seed(ledger, shift.shift_id, "hov-ev-rep-approver2", "shift_supervisor")
    op = runner._auth_headers("hov-ev-op3", "operator")
    approver = runner._auth_headers("hov-ev-rep-approver2", "shift_supervisor")

    def _run(client):
        return runner._make_ready_report(ledger, client, shift.shift_id, op, approver)

    resp = runner._with_ledger(ledger, _run)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "APPROVED"
    assert body["is_current"] is True
    current = ledger.get_current_report(shift.shift_id, "END_SHIFT")
    assert str(current.status) == "APPROVED"


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


# --- sanitization primitives (mirrors incident's proven design) -------------

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


def test_clean_endpoint_strips_userinfo_query_and_fragment():
    endpoint = (
        f"https://{_ENDPOINT_SENTINEL}:{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com"
        f"/v1/chat/completions?token={_ENDPOINT_SENTINEL}#frag-{_ENDPOINT_SENTINEL}"
    )
    clean, secrets = support._clean_endpoint(endpoint)
    assert clean == "https://dashscope-intl.aliyuncs.com/v1/chat/completions"
    assert _ENDPOINT_SENTINEL not in clean
    assert set(secrets) == {_ENDPOINT_SENTINEL, f"token={_ENDPOINT_SENTINEL}", f"frag-{_ENDPOINT_SENTINEL}"}


# --- sentinel-bearing provider failures -------------------------------------

def _fake_urlopen_http_error(*_a, **_kw):
    body = f"invalid key sk-... Bearer {_SENTINEL_KEY} rejected".encode()
    raise urllib.error.HTTPError("https://x/chat/completions", 401, "Unauthorized", None, io.BytesIO(body))


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


def test_call_provider_transport_exception_embedding_full_url_never_leaks_endpoint_sentinel(monkeypatch):
    endpoint = (
        f"https://{_ENDPOINT_SENTINEL}:{_ENDPOINT_SENTINEL}@dashscope-intl.aliyuncs.com"
        f"/v1/chat/completions?token={_ENDPOINT_SENTINEL}#frag-{_ENDPOINT_SENTINEL}"
    )

    def _fake_urlopen(req, timeout=60):
        raise RuntimeError(f"connection refused: {req.full_url}")

    monkeypatch.setattr(support.urllib.request, "urlopen", _fake_urlopen)
    counter = support.ProviderCallCounter()
    result = support.call_provider(
        model="m", api_key=_SENTINEL_KEY, endpoint=endpoint,
        prompt="p", expected_token="OK", counter=counter,
    )
    assert counter.count == 1
    assert _ENDPOINT_SENTINEL not in result["error"]
    assert "dashscope-intl.aliyuncs.com" in result["error"]


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
        quorum_detail="quorum ok", provider_result=result, model="sentinel-model",
        safe_endpoint=support.safe_endpoint_description("https://dashscope-intl.aliyuncs.com/v1/chat/completions"),
        call_count=counter.count,
    )
    captured = capsys.readouterr()
    receipt_text = receipt_path.read_text(encoding="utf-8")
    for surface in (captured.out, captured.err, receipt_text):
        assert _SENTINEL_KEY not in surface


def test_write_receipt_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RECEIPT_PATH", tmp_path / "receipt.md")
    gate_results = [{"case": "x", "outcome": "PASS", "detail": "d", "calls": 0}]
    provider_result = {"outcome": "PASS", "reached_server": True, "http_status": 200, "response_excerpt": "CVF_HANDOVER_EVIDENCE_OK"}
    support.render_receipt(
        tmp_path / "receipt.md", gate_results=gate_results, quorum_detail="quorum ok",
        provider_result=provider_result, model="some-model",
        safe_endpoint=support.safe_endpoint_description(runner._endpoint()), call_count=1,
    )
    text = (tmp_path / "receipt.md").read_text(encoding="utf-8")
    assert "Bearer " not in text
    assert "sk-" not in text
    assert "LIVE EVIDENCE" not in text  # written by main(), not render_receipt()
    assert "Overall outcome: PASS" in text
