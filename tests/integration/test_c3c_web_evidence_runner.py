"""Unit/Integration test for C3c Web Evidence Runner module (no browser
launch: proves command construction, readiness timeout, subprocess failure
propagation, child-tree cleanup and artifact cleanup only)."""

import os
from unittest.mock import MagicMock, patch

from scripts.testing import run_c3c_web_evidence as runner


def test_find_free_port():
    port = runner.find_free_port()
    assert isinstance(port, int)
    assert 1024 < port < 65535


def test_wait_for_port_timeout():
    port = runner.find_free_port()
    assert not runner.wait_for_port(port, timeout_sec=0.1)


def test_sanitize_output_redacts_secrets_paths_and_bounds_length():
    raw = f"JWT_SECRET_KEY=super-secret Authorization: Bearer abc.def.ghi at {runner.WORK_DIR}\\nested" + ("x" * 2000)
    out = runner.sanitize_output(raw)
    assert "[redacted]" in out
    assert "super-secret" not in out
    assert runner.WORK_DIR not in out
    assert len(out) <= runner._MAX_SANITIZED_LEN


def test_sanitize_output_empty_input():
    assert runner.sanitize_output("") == ""


def test_offline_queue_clean_derives_from_playwright_pass_not_hardcoded():
    assert runner.offline_queue_clean(True) is True
    assert runner.offline_queue_clean(False) is False


def test_kill_process_tree_uses_taskkill_on_windows(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    proc = MagicMock()
    proc.poll.return_value = None
    proc.pid = 4242
    with patch("subprocess.run") as mock_run:
        runner.kill_process_tree(proc, timeout_sec=1.0)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[:2] == ["taskkill", "/PID"]
        assert "/T" in args and "/F" in args
    proc.wait.assert_called_once()


def test_kill_process_tree_noop_when_already_exited():
    proc = MagicMock()
    proc.poll.return_value = 0
    with patch("subprocess.run") as mock_run:
        runner.kill_process_tree(proc)
        mock_run.assert_not_called()


def test_kill_process_tree_noop_when_proc_is_none():
    runner.kill_process_tree(None)  # must not raise


def test_remove_owned_artifacts_removes_test_results_tsbuildinfo_and_dist(tmp_path, monkeypatch):
    fake_results = tmp_path / "test-results"
    fake_results.mkdir()
    (fake_results / "trace.zip").write_bytes(b"x")
    fake_tsbuildinfo = tmp_path / "tsconfig.tsbuildinfo"
    fake_tsbuildinfo.write_text("{}")
    fake_dist = tmp_path / "dist"
    fake_dist.mkdir()
    (fake_dist / "index.html").write_text("<!doctype html>")

    monkeypatch.setattr(runner, "TEST_RESULTS_DIR", str(fake_results))
    monkeypatch.setattr(runner, "TSBUILDINFO", str(fake_tsbuildinfo))
    monkeypatch.setattr(runner, "DIST_DIR", str(fake_dist))

    runner.remove_owned_artifacts()

    assert not fake_results.exists()
    assert not fake_tsbuildinfo.exists()
    assert not fake_dist.exists()


def test_remove_owned_artifacts_is_a_noop_when_nothing_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "TEST_RESULTS_DIR", str(tmp_path / "absent-results"))
    monkeypatch.setattr(runner, "TSBUILDINFO", str(tmp_path / "absent.tsbuildinfo"))
    monkeypatch.setattr(runner, "DIST_DIR", str(tmp_path / "absent-dist"))
    runner.remove_owned_artifacts()  # must not raise


@patch("scripts.testing.run_c3c_web_evidence.remove_owned_artifacts")
@patch("scripts.testing.run_c3c_web_evidence.kill_process_tree")
@patch("subprocess.Popen")
@patch("subprocess.run")
@patch("scripts.testing.run_c3c_web_evidence.static_asset_smoke", return_value=(True, ["/assets/index.js"]))
@patch("scripts.testing.run_c3c_web_evidence.wait_for_port", return_value=True)
def test_run_harness_success_cleans_up_child_trees_and_artifacts(
    mock_wait, mock_smoke, mock_sub_run, mock_sub_popen, mock_kill, mock_remove
):
    mock_sub_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    mock_api = MagicMock()
    mock_vite = MagicMock()
    mock_sub_popen.side_effect = [mock_api, mock_vite]

    ret = runner.run_harness(as_json=True)

    assert ret == 0
    assert mock_kill.call_count == 2
    mock_remove.assert_called_once()


@patch("scripts.testing.run_c3c_web_evidence.remove_owned_artifacts")
@patch("scripts.testing.run_c3c_web_evidence.kill_process_tree")
@patch("subprocess.Popen")
@patch("subprocess.run")
@patch("scripts.testing.run_c3c_web_evidence.wait_for_port", return_value=False)
def test_run_harness_reports_readiness_timeout_and_still_cleans_up(
    mock_wait, mock_sub_run, mock_sub_popen, mock_kill, mock_remove
):
    mock_sub_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    mock_sub_popen.return_value = MagicMock()

    ret = runner.run_harness(as_json=True)

    assert ret == 1
    mock_remove.assert_called_once()


@patch("scripts.testing.run_c3c_web_evidence.remove_owned_artifacts")
@patch("scripts.testing.run_c3c_web_evidence.kill_process_tree")
@patch("subprocess.run")
def test_run_harness_propagates_seed_subprocess_failure_without_raw_output(mock_sub_run, mock_kill, mock_remove, capsys):
    mock_sub_run.side_effect = [
        MagicMock(returncode=0, stdout="", stderr=""),
        MagicMock(returncode=1, stdout="", stderr="JWT_SECRET_KEY=leak traceback line one\nline two")
    ]

    ret = runner.run_harness(as_json=True)

    assert ret == 1
    mock_remove.assert_called_once()
    printed = capsys.readouterr().out
    assert "JWT_SECRET_KEY=leak" not in printed
    assert "[redacted]" in printed
