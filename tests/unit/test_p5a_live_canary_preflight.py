"""Credential-free structural checks; these are never live governance proof."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _p5a_live_preflight as preflight
import _p5a_live_transport as transport
import run_p5a_live_governance_evidence as runner


def test_default_readiness_never_uses_key_marker_transport_or_fixed_evidence(monkeypatch, capsys):
    observed = {"calls": 0}

    def harmless_preflight():
        observed["calls"] += 1
        return runner._initial_envelope(), "WORKTREE_DIRTY"

    def forbidden(*_args, **_kwargs):
        pytest.fail("default readiness crossed an effect boundary")

    monkeypatch.setattr(runner, "run_preflight", harmless_preflight)
    for name in ("read_current_user_key", "reserve_marker", "one_post", "_write_evidence"):
        monkeypatch.setattr(runner, name, forbidden)
    assert runner.main([]) == 2
    assert observed["calls"] == 1
    printed = json.loads(capsys.readouterr().out)
    assert printed["readiness"] == "BLOCKED_ZERO_CALL"
    assert printed["safe_reason"] == "WORKTREE_DIRTY"


def test_probe_environment_excludes_inherited_credentials_and_dotenv(monkeypatch):
    monkeypatch.setenv("ALIBABA_API_KEY", "structural-never-used")
    monkeypatch.setenv("JWT_SECRET_KEY", "also-not-inherited")
    env = preflight._probe_env()
    assert "ALIBABA_API_KEY" not in env
    assert env["JWT_SECRET_KEY"] == "p5a-a7-synthetic-local-only-20261024"
    original = preflight.os.path.lexists
    monkeypatch.setattr(preflight.os.path, "lexists", lambda path: True if path == preflight.ROOT / ".env" else original(path))
    with pytest.raises(ValueError, match="API_PROBE_MISMATCH"):
        preflight._run_api_probe()


def test_existing_or_uncertain_marker_is_spent(monkeypatch, tmp_path):
    marker = tmp_path / "attempt.json"
    monkeypatch.setattr(transport, "MARKER", marker)
    assert transport.marker_present() is False
    marker.write_text("reserved", encoding="utf-8")
    assert transport.marker_present() is True
    marker.unlink()
    original = Path.lstat

    def uncertain(path):
        if path == marker:
            raise PermissionError("ambiguous marker access")
        return original(path)

    monkeypatch.setattr(Path, "lstat", uncertain)
    assert transport.marker_present() is True


def test_marker_precedes_preflight_key_and_transport(monkeypatch):
    monkeypatch.setattr(runner, "marker_present", lambda: True)

    def forbidden(*_args, **_kwargs):
        pytest.fail("spent marker crossed another boundary")

    for name in ("run_preflight", "read_current_user_key", "reserve_marker", "one_post"):
        monkeypatch.setattr(runner, name, forbidden)
    monkeypatch.setattr(runner, "_emit", lambda *args, **kwargs: (args[0], args[2]))
    outcome, reason = runner.execute("a" * 40, "3173 passed")
    assert (outcome, reason) == ("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "MARKER_ALREADY_EXISTS")


def test_root_attestation_rejects_different_commit_and_empty_gate():
    envelope = runner._initial_envelope()
    envelope.update(status="COMPLETE", commit="a" * 40)
    assert runner._release_bound(envelope, "b" * 40, "3173 passed") is False
    envelope.update(status="COMPLETE")
    assert runner._release_bound(envelope, "a" * 40, "") is False


def test_real_local_api_probe_reports_wire_codes_and_nonmutation():
    observations = preflight._run_api_probe()
    assert [item["status"] for item in observations] == [401, 404, 422, 200]
    assert observations[0]["error_code"] is None
    assert observations[1]["error_code"] is None
    assert observations[2]["error_code"] == "EXPORT_INVALID_PARAMETER"
    assert observations[3]["before_digest"] == observations[3]["after_digest"]


def test_terminal_writer_is_exclusive_and_rejects_secret_bytes(monkeypatch, tmp_path):
    target = tmp_path / "structural-receipt.json"
    monkeypatch.setattr(runner, "RECEIPT", target)
    with pytest.raises(ValueError, match="secret material"):
        runner._write_evidence({"body": "test-key"}, key="test-key")
    assert not target.exists()
    runner._write_evidence({"safe": True}, key="test-key")
    with pytest.raises(FileExistsError):
        runner._write_evidence({"safe": True}, key="test-key")
    assert json.loads(target.read_text(encoding="utf-8")) == {"safe": True}


def test_wrapper_keeps_public_cost_basis_outside_closed_receipt():
    receipt = {"outcome": "RESERVED_NOT_ACCEPTED_OR_UNKNOWN"}
    wrapper = runner._wrapper(receipt, runner._initial_envelope())
    basis = wrapper["cost_estimate_basis"]
    assert basis["formula"] == "prompt_tokens * 50 + completion_tokens * 400"
    assert basis["input_nano_usd_per_token"] == 50
    assert basis["output_nano_usd_per_token"] == 400
    assert basis["ceiling_nano_usd"] == 10_000_000
    assert basis["admission_id"] == "P5A-A7-ONE-CANARY-20261023"
    assert "estimate, not invoice" in basis["claim"]
    assert "cost_estimate_basis" not in receipt
