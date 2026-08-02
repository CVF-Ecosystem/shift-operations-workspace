import json
import hashlib

import pytest

from scripts import _phase2_full_shift_live_evidence_support as support


def valid_payload():
    harness = {
        "checkpoint": "P2_FULL_SHIFT_EXIT", "api_port": 41001, "vite_port": 41002,
        "static_smoke": True, "static_assets_checked": ["/assets/app.js"],
        "playwright_pass": True, "queue_checkpoint": "bounded_exercised_and_cleaned",
        "queue_checkpoint_pass": True,
    }
    assertions = {
        "schema_version": 1, "producer_id": support.PRODUCER_ID, "run_id": "00000000-0000-4000-8000-000000000001",
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
    }
    return {
        "schema_version": 1, "producer_id": support.PRODUCER_ID, "run_id": "00000000-0000-4000-8000-000000000001",
        "checkpoint": "P2_FULL_SHIFT_EXIT", "playwright_pass": True,
        "queue_checkpoint": "bounded_exercised_and_cleaned", "queue_checkpoint_pass": True,
        "sanitized": True,
        "spec_sha256": hashlib.sha256(support.SPEC_PATH.read_bytes()).hexdigest(),
        "harness_payload": harness, "harness_sha256": support.canonical_digest(harness),
        "assertions": assertions,
    }


def test_browser_evidence_validation_is_strict(tmp_path):
    target = tmp_path / "browser.json"
    target.write_text(json.dumps(valid_payload()), encoding="utf-8")
    assert support.validate_browser_evidence(target)["transport_ambiguity_pass"] is True
    payload = valid_payload()
    payload["assertions"]["browser_contract"]["automatic_retries"] = 1
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="BLOCKED_BROWSER_EVIDENCE_INVALID"):
        support.validate_browser_evidence(target)


@pytest.mark.parametrize("mutation", ["run_id", "spec_sha256", "harness_sha256", "unknown", "forged_counter"])
def test_browser_evidence_provenance_fails_closed(tmp_path, mutation):
    payload = valid_payload()
    if mutation == "run_id":
        payload["assertions"]["run_id"] = "other"
    elif mutation == "spec_sha256":
        payload["spec_sha256"] = "0" * 64
    elif mutation == "harness_sha256":
        payload["harness_sha256"] = "0" * 64
    elif mutation == "unknown":
        payload["unknown"] = True
    else:
        payload["assertions"]["browser_contract"]["transport_requests"] = 2
    target = tmp_path / "browser.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="BLOCKED_BROWSER_EVIDENCE_INVALID"):
        support.validate_browser_evidence(target)


def test_receipt_contains_only_bounded_sanitized_metadata(tmp_path):
    target = tmp_path / "receipt.md"
    target.write_text("# Historical\n\nINVALIDATED_BY_REVIEW_FAIL\n\n- HTTP status: 200\n", encoding="utf-8")
    attempt_id = "00000000-0000-4000-8000-000000000003"
    support.reserve_replacement_attempt(target, attempt_id)
    support.render_receipt(
        target, [{"case": "anonymous", "outcome": "PASS", "status": 401, "calls": 0}],
        "durable", {"checkpoint": "P2_FULL_SHIFT_EXIT"},
        {"outcome": "PASS", "reached_server": True, "http_status": 200, "expected_token_match": True},
        "model", "https://example.com", 1, attempt_id,
    )
    text = target.read_text(encoding="utf-8")
    assert "# Historical" in text and "Replacement outcome: PASS" in text
    assert "Tranche physical calls: **2**" in text and "Accepted final calls: **1**" in text
    assert "Bearer " not in text and "Authorization" not in text and "postgresql" not in text


def test_receipt_refuses_overwrite_or_third_call(tmp_path):
    target = tmp_path / "receipt.md"
    target.write_text("INVALIDATED_BY_REVIEW_FAIL\n", encoding="utf-8")
    attempt_id = "00000000-0000-4000-8000-000000000004"
    support.reserve_replacement_attempt(target, attempt_id)
    with pytest.raises(ValueError, match="BLOCKED_PROVIDER_RECEIPT_HISTORY"):
        support.reserve_replacement_attempt(target, "00000000-0000-4000-8000-000000000005")


def test_failed_provider_result_is_not_accepted_and_blocks_reuse(tmp_path):
    target = tmp_path / "receipt.md"
    target.write_text("INVALIDATED_BY_REVIEW_FAIL\n", encoding="utf-8")
    attempt_id = "00000000-0000-4000-8000-000000000006"
    support.reserve_replacement_attempt(target, attempt_id)
    support.render_receipt(
        target, [], "durable", {"checkpoint": "P2_FULL_SHIFT_EXIT"},
        {"outcome": "FAIL", "reached_server": True, "http_status": 500, "expected_token_match": False},
        "model", "endpoint", 1, attempt_id,
    )
    text = target.read_text(encoding="utf-8")
    assert "NOT_ACCEPTED_PROVIDER_FAILURE" in text and "Accepted final calls: **0**" in text
    with pytest.raises(ValueError, match="BLOCKED_PROVIDER_RECEIPT_HISTORY"):
        support.render_receipt(
            target, [], "durable", {"checkpoint": "P2_FULL_SHIFT_EXIT"},
            {"outcome": "PASS"}, "model", "endpoint", 1, attempt_id,
        )
