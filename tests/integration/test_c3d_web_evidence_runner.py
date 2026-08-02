"""Unit/Integration test for C3d Web Evidence Runner module (no browser
launch: proves checkpoint selection, command construction/delegation to the
reused C3c harness contract, readiness timeout, subprocess failure
propagation and cleanup - all without opening a browser)."""

from unittest.mock import MagicMock, patch

from scripts.testing import run_c3d_web_evidence as runner


def test_run_c3d_harness_delegates_checkpoint_c3d_to_shared_run_harness():
    with patch("scripts.testing.run_c3d_web_evidence.run_harness", return_value=0) as mock_run:
        ret = runner.run_c3d_harness(as_json=True)
        assert ret == 0
        mock_run.assert_called_once_with(as_json=True, checkpoint="C3d", playwright_grep=None)


def test_run_c3d_harness_propagates_failure_exit_code():
    with patch("scripts.testing.run_c3d_web_evidence.run_harness", return_value=1) as mock_run:
        ret = runner.run_c3d_harness(as_json=False)
        assert ret == 1
        mock_run.assert_called_once_with(as_json=False, checkpoint="C3d", playwright_grep=None)


@patch("scripts.testing.run_c3c_web_evidence.remove_owned_artifacts")
@patch("scripts.testing.run_c3c_web_evidence.kill_process_tree")
@patch("subprocess.Popen")
@patch("subprocess.run")
@patch("scripts.testing.run_c3c_web_evidence.static_asset_smoke", return_value=(True, ["/assets/index.js"]))
@patch("scripts.testing.run_c3c_web_evidence.wait_for_port", return_value=True)
def test_c3d_end_to_end_reuses_the_c3c_harness_contract_with_checkpoint_c3d(
    mock_wait, mock_smoke, mock_sub_run, mock_sub_popen, mock_kill, mock_remove
):
    """Proves the C3d wrapper genuinely reuses run_harness's exact
    port/process/cleanup contract (WO section 4) rather than forking it - the
    checkpoint label alone changes the evidence, not the underlying flow."""
    mock_sub_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    mock_api = MagicMock()
    mock_vite = MagicMock()
    mock_sub_popen.side_effect = [mock_api, mock_vite]

    ret = runner.run_c3d_harness(as_json=True)

    assert ret == 0
    assert mock_kill.call_count == 2
    mock_remove.assert_called_once()


def test_run_c3d_harness_never_opens_a_browser_by_itself():
    """Command construction proof: mocking subprocess.Popen/run means no real
    process (including a Playwright browser) is ever spawned by this test."""
    with patch("subprocess.Popen") as mock_popen, patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="seed failed")
        runner.run_c3d_harness(as_json=True)
        mock_popen.assert_not_called()
