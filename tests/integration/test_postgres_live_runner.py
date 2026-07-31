"""Non-live unit tests for scripts/run_postgres_live_roundtrip.py.

None of these need Docker, psycopg or a database; every Docker/psycopg-
facing function is monkeypatched."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_postgres_live_roundtrip as runner  # noqa: E402


# --- command construction / redaction / naming / parsing --------------------

def test_redact_masks_credentials_including_at_sign_in_password():
    url = "postgresql+psycopg://user:s3cr3t@pw@127.0.0.1:5432/db"
    assert runner.redact(url) == "postgresql+psycopg://<redacted>@127.0.0.1:5432/db"
    assert "s3cr3t" not in runner.redact(url)


def test_docker_run_cmd_has_no_volume_and_is_loopback_only():
    cmd = runner.docker_run_cmd("cvf-pg-live-test", 55123, "pw")
    assert "-v" not in cmd and "--mount" not in cmd
    assert "127.0.0.1:55123:5432" in cmd
    assert "0.0.0.0" not in " ".join(cmd)
    assert cmd[cmd.index("--name") + 1] == "cvf-pg-live-test"


def test_container_names_are_prefixed_and_unique():
    names = {runner.new_container_name() for _ in range(5)}
    assert len(names) == 5
    assert all(n.startswith(runner.CONTAINER_PREFIX) for n in names)


def test_free_loopback_port_is_actually_bindable():
    port = runner.free_loopback_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))  # raises if not truly free


def test_live_suite_targets_pin_all_six_coherent_modules():
    """Exactly these six live modules - not a broader glob, no silent drop."""
    assert runner.LIVE_SUITE_TARGETS == (
        "tests/integration/test_sql_ledger_postgres_live.py",
        "tests/integration/test_incident_postgres_live.py",
        "tests/integration/test_handover_postgres_live.py",
        "tests/integration/test_shift_create_postgres_live.py",
        "tests/integration/test_message_postgres_live.py",
        "tests/integration/test_report_postgres_live.py",
    )


def test_parse_migration_counts_extracts_applied_and_skipped():
    output = "001_foundation.sql: ok\ndone - 12 statement(s) applied, 3 already present\n"
    assert runner.parse_migration_counts(output) == (12, 3)
    with pytest.raises(Exception):
        runner.parse_migration_counts("no summary line here")


# --- PG-REV-F2/Finding 2: failure-output sanitization (SPEC R15/R32, AC-25) -

def test_sanitize_output_scrubs_sentinel_password_and_full_url():
    password = "SENTINEL_PW_9f8e7d3c2b1a"
    url = f"postgresql+psycopg://cvf_live:{password}@127.0.0.1:55555/cvf_live_roundtrip"
    plain_url = f"postgresql://cvf_live:{password}@127.0.0.1:55555/cvf_live_roundtrip"
    text = f"E   live_database_url = '{url}'\nE   or plain form {plain_url}\nE   raw password {password} embedded\n"
    cleaned = runner.sanitize_output(text, password=password, database_url=url)
    assert password not in cleaned and url not in cleaned and plain_url not in cleaned
    assert "<redacted-password>" in cleaned and "<redacted-database-url>" in cleaned


def test_sanitize_output_is_a_noop_for_empty_text():
    assert runner.sanitize_output("", password="pw", database_url="postgresql://x") == ""


# --- PG-REV-F3: cleanup ownership (SPEC R16, AC-26/AC-27) -------------------

def test_start_container_never_invokes_docker_run_on_name_collision(monkeypatch):
    monkeypatch.setattr(runner, "container_exists", lambda name: True)
    calls: list[list[str]] = []
    monkeypatch.setattr(runner, "_run", lambda cmd, **kw: calls.append(cmd))
    with pytest.raises(runner.LiveRoundTripError):
        runner.start_container("collides-with-something", 12345, "pw")
    assert calls == []  # docker run was never invoked


def test_run_once_skips_cleanup_when_container_was_never_created(monkeypatch):
    def _raise(*_a, **_kw):
        raise runner.LiveRoundTripError("simulated docker run failure")

    monkeypatch.setattr(runner, "start_container", _raise)
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))
    summary = runner.run_once("postgresql+psycopg://u:p@127.0.0.1:1/db", "never-created", 1, "pw")
    assert cleanup_calls == []  # cleanup must never target a container that was never created
    assert summary["container_absent_after_cleanup"] is True
    assert summary["cleanup_skipped_reason"]
    assert summary["failure"]


def _stub_ready(monkeypatch, volumes=(), returncode=0, stdout="ok"):
    """Common run_once stubbing: creation, readiness, live suite, cleanup-check all succeed."""
    monkeypatch.setattr(runner, "start_container", lambda *a, **kw: None)
    monkeypatch.setattr(runner, "container_volumes", lambda name: list(volumes))
    monkeypatch.setattr(runner, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner, "wait_ready_via_database", lambda url: None)
    monkeypatch.setattr(runner, "container_exists", lambda name: False)
    fake_result = subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")
    monkeypatch.setattr(runner, "run_live_suite", lambda url: fake_result)


def test_run_once_invokes_cleanup_and_reports_success_when_container_created(monkeypatch):
    _stub_ready(monkeypatch, volumes=["anon-vol-1"], stdout="1 passed")
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [{"attempt": "first", "applied": 1, "skipped": 0}])
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))
    summary = runner.run_once("postgresql+psycopg://u:p@127.0.0.1:1/db", "really-created", 1, "pw")
    assert cleanup_calls == [("really-created", ["anon-vol-1"])]
    assert summary["container_absent_after_cleanup"] is True
    assert summary["failure"] is None


def test_run_once_reports_failure_when_anonymous_volume_survives_cleanup(monkeypatch):
    _stub_ready(monkeypatch, volumes=["stubborn-vol"])
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [])
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: (True, ["stubborn-vol"]))
    summary = runner.run_once("postgresql+psycopg://u:p@127.0.0.1:1/db", "leaky", 1, "pw")
    assert summary["container_absent_after_cleanup"] is False
    assert "stubborn-vol" in summary["failure"]


# --- PG-REV-F6: no unsanitized traceback/output can ever escape -------------

_F6_PASSWORD = "SENTINEL_PW_F6_9a8b7c6d5e4f"
_F6_URL = f"postgresql+psycopg://cvf_live:{_F6_PASSWORD}@127.0.0.1:59999/cvf_live_roundtrip"


def _assert_sentinel_absent_everywhere(summary: dict, captured) -> None:
    surfaces = [json.dumps(summary), captured.out, captured.err, summary.get("live_suite_tail") or "", summary.get("failure") or ""]
    for surface in surfaces:
        assert _F6_PASSWORD not in surface and _F6_URL not in surface


def test_run_once_sanitizes_sentinel_from_a_failing_subprocess_result(monkeypatch, capsys):
    _stub_ready(monkeypatch)
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [])
    fake_result = subprocess.CompletedProcess(
        args=[], returncode=1,
        stdout=f"FAILED ...\nlive_database_url = '{_F6_URL}'\n",
        stderr=f"connection error using password {_F6_PASSWORD}\n",
    )
    monkeypatch.setattr(runner, "run_live_suite", lambda url: fake_result)
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))
    summary = runner.run_once(_F6_URL, "f6-subprocess", 59999, _F6_PASSWORD)
    captured = capsys.readouterr()
    assert cleanup_calls == [("f6-subprocess", [])]  # cleanup still ran on failure
    assert summary["failure"] == "live suite did not pass"
    _assert_sentinel_absent_everywhere(summary, captured)


def test_run_once_sanitizes_sentinel_when_an_ordinary_exception_is_raised(monkeypatch, capsys):
    """PG-REV-F6 + Finding 2: a non-LiveRoundTripError embedding the PLAIN
    `postgresql://` DSN (not just the original `+psycopg` URL) must sanitize fully."""
    _stub_ready(monkeypatch)
    plain_dsn = f"postgresql://cvf_live:{_F6_PASSWORD}@127.0.0.1:59999/cvf_live_roundtrip"

    def _boom(url):
        raise RuntimeError(f"connection failed for {plain_dsn}")

    monkeypatch.setattr(runner, "apply_migrations_twice", _boom)
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))
    summary = runner.run_once(_F6_URL, "f6-exception", 59999, _F6_PASSWORD)
    captured = capsys.readouterr()
    assert cleanup_calls == [("f6-exception", [])]  # cleanup still ran despite the raw exception
    assert summary["container_absent_after_cleanup"] is True
    assert summary["failure"] and "RuntimeError" in summary["failure"]
    assert "database_url_redacted" not in summary and "postgresql://" not in json.dumps(summary)
    _assert_sentinel_absent_everywhere(summary, captured)


# --- P2R repair: wait_ready survives the postgres init-then-restart race ---

def test_wait_ready_requires_stability_not_a_single_success(monkeypatch):
    """A single pg_isready success (pre-restart window) must not be enough."""
    calls = {"n": 0}

    def _fake_isready(name):
        calls["n"] += 1
        return calls["n"] not in (2,)  # poll 2 fails (mid-restart), rest succeed

    monkeypatch.setattr(runner, "_pg_isready", _fake_isready)
    monkeypatch.setattr(runner.time, "sleep", lambda s: None)
    runner.wait_ready("some-container", timeout_s=30, stability_checks=3)
    assert calls["n"] >= 5  # reset after the poll-2 blip, then 3 more in a row


def _fake_clock(monkeypatch):
    """Deterministic elapsing clock: each `sleep(s)` advances `monotonic()`."""
    fake_now = [0.0]
    monkeypatch.setattr(runner.time, "sleep", lambda s: fake_now.__setitem__(0, fake_now[0] + 1))
    monkeypatch.setattr(runner.time, "monotonic", lambda: fake_now[0])


def test_wait_ready_never_returns_on_a_single_isready_success(monkeypatch):
    """One success alone must never satisfy readiness when stability_checks > 1."""
    responses = iter([True])  # exactly one success, then permanently False
    monkeypatch.setattr(runner, "_pg_isready", lambda name: next(responses, False))
    _fake_clock(monkeypatch)
    with pytest.raises(runner.LiveRoundTripError, match="did not become durably ready"):
        runner.wait_ready("some-container", timeout_s=5, stability_checks=3)


def test_wait_ready_raises_after_timeout_if_never_ready(monkeypatch):
    monkeypatch.setattr(runner, "_pg_isready", lambda name: False)
    _fake_clock(monkeypatch)
    with pytest.raises(runner.LiveRoundTripError, match="did not become durably ready"):
        runner.wait_ready("never-ready", timeout_s=5, stability_checks=3)


# --- Finding 3: internal pg_isready stability alone is not proof of FINAL ---

class _NullCtx:
    """Fake connection/cursor: only execute/fetchone/cursor matter here."""

    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def execute(self, *_a): pass
    def fetchone(self): return (1,)
    def cursor(self): return self


def _fake_psycopg(connect_fn):
    return type("FakePsycopg", (), {"connect": staticmethod(connect_fn)})


def test_run_once_requires_database_readiness_even_when_internal_poll_is_ready(monkeypatch):
    """Internal `wait_ready` success alone must not be sufficient: `run_once`
    must fail if `wait_ready_via_database` never succeeds."""
    _stub_ready(monkeypatch)  # internal poll ready; override the DB check below

    def _never_reachable(url):
        raise runner.LiveRoundTripError("database not reachable on the mapped port within 1s (OperationalError)")

    monkeypatch.setattr(runner, "wait_ready_via_database", _never_reachable)
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: (True, []))
    summary = runner.run_once("postgresql+psycopg://u:p@127.0.0.1:1/db", "final-check", 1, "pw")
    assert summary["failure"] and "not reachable on the mapped port" in summary["failure"]


def test_wait_ready_via_database_succeeds_once_a_real_connection_succeeds(monkeypatch):
    """Positive control: success is driven by the connection attempt, not polling."""
    monkeypatch.setitem(sys.modules, "psycopg", _fake_psycopg(lambda url, **kw: _NullCtx()))
    runner.wait_ready_via_database("postgresql+psycopg://u:p@127.0.0.1:1/db", timeout_s=5)


_F2_PW = "SENTINEL_PW_F2_1a2b3c4d5e6f"
_F2_URL_PSYCOPG = f"postgresql+psycopg://cvf_live:{_F2_PW}@127.0.0.1:59998/cvf_live_roundtrip"
_F2_URL_PLAIN = f"postgresql://cvf_live:{_F2_PW}@127.0.0.1:59998/cvf_live_roundtrip"
_F2_SECRETS = (_F2_PW, "cvf_live", "postgresql://", "postgresql+psycopg://", "127.0.0.1", "59998", "cvf_live_roundtrip", _F2_URL_PSYCOPG, _F2_URL_PLAIN)


def _assert_f2_secrets_absent(text: str) -> None:
    """Finding 2: no username/password/scheme/host/port/db/either complete URL."""
    for secret in _F2_SECRETS:
        assert secret not in text, f"leaked {secret!r} in: {text!r}"


def test_wait_ready_via_database_never_leaks_dsn_on_timeout(monkeypatch):
    """Finding 2: raised message never includes raw driver text - only a fixed message + class."""
    def _refused(conninfo, **kw):
        raise RuntimeError(f"connection to {conninfo} refused")

    monkeypatch.setitem(sys.modules, "psycopg", _fake_psycopg(_refused))
    _fake_clock(monkeypatch)
    with pytest.raises(runner.LiveRoundTripError) as exc:
        runner.wait_ready_via_database(_F2_URL_PSYCOPG, timeout_s=3)
    _assert_f2_secrets_absent(str(exc.value))
    assert "RuntimeError" in str(exc.value) and "not reachable on the mapped port" in str(exc.value)


def test_run_once_summary_never_contains_a_database_url(monkeypatch):
    """Finding 2: no `database_url_redacted` (or any DSN-bearing field) in the public summary."""
    _stub_ready(monkeypatch)
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [])
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: (True, []))
    summary = runner.run_once(_F2_URL_PSYCOPG, "f2-run", 1, _F2_PW)
    assert "database_url_redacted" not in summary
    _assert_f2_secrets_absent(json.dumps(summary))
