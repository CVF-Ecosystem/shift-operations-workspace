from unittest.mock import patch

from scripts.testing import run_p2d_web_evidence as runner


def test_p2d_wrapper_selects_only_p2d_and_bounded_queue_checkpoint():
    with patch("scripts.testing.run_p2d_web_evidence.run_harness", return_value=0) as shared:
        assert runner.run_p2d_harness(as_json=True) == 0
    shared.assert_called_once_with(
        as_json=True,
        checkpoint="P2D",
        playwright_grep="P2-D bounded offline and polling evidence",
        queue_checkpoint="bounded_exercised_and_cleaned",
    )


def test_p2d_wrapper_propagates_failure_without_opening_browser():
    with patch("scripts.testing.run_p2d_web_evidence.run_harness", return_value=1):
        assert runner.run_p2d_harness() == 1
