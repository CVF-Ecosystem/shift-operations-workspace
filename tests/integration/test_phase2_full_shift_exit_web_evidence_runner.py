import json
import os
from unittest.mock import patch

from scripts.testing import run_phase2_full_shift_exit_web_evidence as runner


def passing_harness(**kwargs):
    run_id = os.environ["PHASE2_BROWSER_EVIDENCE_RUN_ID"]
    assertion_path = os.environ["PHASE2_BROWSER_ASSERTION_PATH"]
    with open(assertion_path, "w", encoding="utf-8") as stream:
        json.dump({
            "schema_version": 1, "producer_id": runner.PRODUCER_ID, "run_id": run_id,
            "browser_contract": {
                "positive_actions": "rendered_ui", "transport_requests": 1,
                "automatic_retries": 0, "queue_insertions": 0,
                "authoritative_reconciliation": True,
            },
            "task_reconciliation": {
                "fresh_get_after_replay": True, "exact_task_id": True,
                "exact_committed_version": True, "status_in_progress": True,
                "dom_after_get": True,
            },
        }, stream)
    print(json.dumps({
        "checkpoint": "P2_FULL_SHIFT_EXIT", "api_port": 41001, "vite_port": 41002,
        "static_smoke": True, "static_assets_checked": ["/assets/app.js"],
        "playwright_pass": True, "queue_checkpoint": "bounded_exercised_and_cleaned",
        "queue_checkpoint_pass": True,
    }))
    return 0


def test_wrapper_selects_only_full_shift_spec_and_writes_sanitized_json(tmp_path):
    target = tmp_path / "browser.json"
    with patch("scripts.testing.run_phase2_full_shift_exit_web_evidence.run_harness", side_effect=passing_harness) as shared:
        assert runner.run_phase2_harness(as_json=False, evidence_json=target) == 0
    shared.assert_called_once_with(
        as_json=True, checkpoint="P2_FULL_SHIFT_EXIT",
        playwright_grep="Phase 2 full-shift exit evidence",
        queue_checkpoint="bounded_exercised_and_cleaned",
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["sanitized"] is True
    assert payload["producer_id"] == runner.PRODUCER_ID
    assert payload["assertions"]["browser_contract"] == {
        "positive_actions": "rendered_ui", "transport_requests": 1,
        "automatic_retries": 0, "queue_insertions": 0,
        "authoritative_reconciliation": True,
    }


def test_wrapper_fails_closed_on_non_json_harness_output(tmp_path):
    target = tmp_path / "browser.json"
    def non_json(**kwargs):
        print("not-json")
        return 0
    with patch("scripts.testing.run_phase2_full_shift_exit_web_evidence.run_harness", side_effect=non_json):
        assert runner.run_phase2_harness(evidence_json=target) == 1
    assert json.loads(target.read_text(encoding="utf-8"))["playwright_pass"] is False


def test_wrapper_rejects_mismatched_run_id_and_unknown_assertion_fields(tmp_path):
    def forged(**kwargs):
        passing_harness(**kwargs)
        path = os.environ["PHASE2_BROWSER_ASSERTION_PATH"]
        payload = json.loads(open(path, encoding="utf-8").read())
        payload["run_id"] = "forged"
        payload["unknown"] = True
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(payload, stream)
        return 0
    with patch("scripts.testing.run_phase2_full_shift_exit_web_evidence.run_harness", side_effect=forged):
        assert runner.run_phase2_harness(evidence_json=tmp_path / "browser.json") == 1


def test_wrapper_rejects_unsanitized_asset_before_labeling_pass(tmp_path):
    for asset in ("/assets/app.js?token=secret", "/assets/app.js#fragment", "/assets\\app.js", "/" + "a" * 200):
        target = tmp_path / (str(abs(hash(asset))) + ".json")
        def harness(**kwargs):
            run_id = os.environ["PHASE2_BROWSER_EVIDENCE_RUN_ID"]
            assertion_path = os.environ["PHASE2_BROWSER_ASSERTION_PATH"]
            with open(assertion_path, "w", encoding="utf-8") as stream:
                json.dump({
                    "schema_version": 1, "producer_id": runner.PRODUCER_ID, "run_id": run_id,
                    "browser_contract": {"positive_actions": "rendered_ui", "transport_requests": 1, "automatic_retries": 0, "queue_insertions": 0, "authoritative_reconciliation": True},
                    "task_reconciliation": {"fresh_get_after_replay": True, "exact_task_id": True, "exact_committed_version": True, "status_in_progress": True, "dom_after_get": True},
                }, stream)
            print(json.dumps({
                "checkpoint": "P2_FULL_SHIFT_EXIT", "api_port": 41001, "vite_port": 41002,
                "static_smoke": True, "static_assets_checked": [asset], "playwright_pass": True,
                "queue_checkpoint": "bounded_exercised_and_cleaned", "queue_checkpoint_pass": True,
            }))
            return 0
        with patch("scripts.testing.run_phase2_full_shift_exit_web_evidence.run_harness", side_effect=harness):
            assert runner.run_phase2_harness(evidence_json=target) == 1
        assert json.loads(target.read_text(encoding="utf-8"))["playwright_pass"] is False
