"""Non-live unit tests for scripts/run_postgres_live_roundtrip.py.

Split out of test_sql_ledger_postgres_live.py (Amendment 1, WO 14.3 step 1)
purely to respect the file-size guard after adding the sanitization and
cleanup-ownership repair tests - not a behavior change to any pre-existing
test. None of these need Docker, psycopg or a database; every Docker-facing
function is monkeypatched. scripts/ is not on pytest's pythonpath, added
here like every other script-importing test module in this repo.

The P2C R27 live PostgreSQL 500/501 matrix that was temporarily appended
here during Amendment 2 repair (making this file 315 lines) has moved to
its own authorized module, tests/integration/test_p2c_read_postgres_limit_live.py
(Amendment 3), restoring this file to its original runner-test-only scope.
"""

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


def test_live_suite_targets_pin_all_five_coherent_modules():
    """P2A-INCIDENT-VERTICAL (INC-AUTH-F2) + P2A-HANDOVER-VERTICAL +
    SHIFT-CREATE-ADMISSION-REPAIR + MESSAGE-ADMISSION-TRUST-REPAIR: the
    runner must execute exactly the existing PostgreSQL live module plus the
    split incident, handover, shift-create and message modules - not a
    broader glob, and not a silent drop of any of the five."""
    assert runner.LIVE_SUITE_TARGETS == (
        "tests/integration/test_sql_ledger_postgres_live.py",
        "tests/integration/test_incident_postgres_live.py",
        "tests/integration/test_handover_postgres_live.py",
        "tests/integration/test_shift_create_postgres_live.py",
        "tests/integration/test_message_postgres_live.py",
    )


def test_parse_migration_counts_extracts_applied_and_skipped():
    output = "001_foundation.sql: ok\ndone - 12 statement(s) applied, 3 already present\n"
    assert runner.parse_migration_counts(output) == (12, 3)
    with pytest.raises(Exception):
        runner.parse_migration_counts("no summary line here")


# --- PG-REV-F2: failure-output sanitization (SPEC R15, AC-25) ---------------

def test_sanitize_output_scrubs_sentinel_password_and_full_url():
    password = "SENTINEL_PW_9f8e7d3c2b1a"
    url = f"postgresql+psycopg://cvf_live:{password}@127.0.0.1:55555/cvf_live_roundtrip"
    text = (
        f"E   live_database_url = '{url}'\n"
        f"E   some other line embedding the raw password {password} directly\n"
    )
    cleaned = runner.sanitize_output(text, password=password, database_url=url)
    assert password not in cleaned
    assert url not in cleaned
    assert "<redacted-password>" in cleaned or "<redacted>" in cleaned


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


def test_run_once_invokes_cleanup_and_reports_success_when_container_created(monkeypatch):
    monkeypatch.setattr(runner, "start_container", lambda *a, **kw: None)
    monkeypatch.setattr(runner, "container_volumes", lambda name: ["anon-vol-1"])
    monkeypatch.setattr(runner, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [{"attempt": "first", "applied": 1, "skipped": 0}])
    fake_result = subprocess.CompletedProcess(args=[], returncode=0, stdout="1 passed", stderr="")
    monkeypatch.setattr(runner, "run_live_suite", lambda url: fake_result)
    monkeypatch.setattr(runner, "container_exists", lambda name: False)
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))

    summary = runner.run_once("postgresql+psycopg://u:p@127.0.0.1:1/db", "really-created", 1, "pw")

    assert cleanup_calls == [("really-created", ["anon-vol-1"])]
    assert summary["container_absent_after_cleanup"] is True
    assert summary["failure"] is None


def test_run_once_reports_failure_when_anonymous_volume_survives_cleanup(monkeypatch):
    monkeypatch.setattr(runner, "start_container", lambda *a, **kw: None)
    monkeypatch.setattr(runner, "container_volumes", lambda name: ["stubborn-vol"])
    monkeypatch.setattr(runner, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [])
    fake_result = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
    monkeypatch.setattr(runner, "run_live_suite", lambda url: fake_result)
    monkeypatch.setattr(runner, "container_exists", lambda name: False)
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: (True, ["stubborn-vol"]))

    summary = runner.run_once("postgresql+psycopg://u:p@127.0.0.1:1/db", "leaky", 1, "pw")

    assert summary["container_absent_after_cleanup"] is False
    assert "stubborn-vol" in summary["failure"]


# --- PG-REV-F6: no unsanitized traceback/output can ever escape -------------

_F6_PASSWORD = "SENTINEL_PW_F6_9a8b7c6d5e4f"
_F6_URL = f"postgresql+psycopg://cvf_live:{_F6_PASSWORD}@127.0.0.1:59999/cvf_live_roundtrip"


def _assert_sentinel_absent_everywhere(summary: dict, captured) -> None:
    surfaces = [
        json.dumps(summary),
        captured.out,
        captured.err,
        summary.get("live_suite_tail") or "",
        summary.get("failure") or "",
    ]
    for surface in surfaces:
        assert _F6_PASSWORD not in surface
        assert _F6_URL not in surface


def test_run_once_sanitizes_sentinel_from_a_failing_subprocess_result(monkeypatch, capsys):
    monkeypatch.setattr(runner, "start_container", lambda *a, **kw: None)
    monkeypatch.setattr(runner, "container_volumes", lambda name: [])
    monkeypatch.setattr(runner, "wait_ready", lambda name: None)
    monkeypatch.setattr(runner, "apply_migrations_twice", lambda url: [])
    fake_result = subprocess.CompletedProcess(
        args=[], returncode=1,
        stdout=f"FAILED ...\nlive_database_url = '{_F6_URL}'\n",
        stderr=f"connection error using password {_F6_PASSWORD}\n",
    )
    monkeypatch.setattr(runner, "run_live_suite", lambda url: fake_result)
    monkeypatch.setattr(runner, "container_exists", lambda name: False)
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))

    summary = runner.run_once(_F6_URL, "f6-subprocess", 59999, _F6_PASSWORD)
    captured = capsys.readouterr()

    assert cleanup_calls == [("f6-subprocess", [])]  # cleanup still ran on failure
    assert summary["failure"] == "live suite did not pass"
    _assert_sentinel_absent_everywhere(summary, captured)


def test_run_once_sanitizes_sentinel_when_an_ordinary_exception_is_raised(monkeypatch, capsys):
    """PG-REV-F6 regression: before the fix, a non-LiveRoundTripError raised
    here (simulating a raw SQLAlchemy/driver failure in apply_migrations)
    propagated straight out of run_once, past all sanitization, and cleanup
    was never reached."""
    monkeypatch.setattr(runner, "start_container", lambda *a, **kw: None)
    monkeypatch.setattr(runner, "container_volumes", lambda name: [])
    monkeypatch.setattr(runner, "wait_ready", lambda name: None)

    def _boom(url):
        raise RuntimeError(f"connection failed for {url}")

    monkeypatch.setattr(runner, "apply_migrations_twice", _boom)
    monkeypatch.setattr(runner, "container_exists", lambda name: False)
    cleanup_calls: list[tuple] = []
    monkeypatch.setattr(runner, "remove_container", lambda name, vols: cleanup_calls.append((name, vols)) or (True, []))

    summary = runner.run_once(_F6_URL, "f6-exception", 59999, _F6_PASSWORD)
    captured = capsys.readouterr()

    assert cleanup_calls == [("f6-exception", [])]  # cleanup still ran despite the raw exception
    assert summary["container_absent_after_cleanup"] is True
    assert summary["failure"] and "RuntimeError" in summary["failure"]
    _assert_sentinel_absent_everywhere(summary, captured)
