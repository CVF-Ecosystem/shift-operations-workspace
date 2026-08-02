"""Real-browser Phase 2 exit wrapper over the unchanged shared harness."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.run_c3c_web_evidence import run_harness  # noqa: E402

PRODUCER_ID = "phase2-full-shift-exit-playwright-v1"
SPEC_PATH = REPO_ROOT / "apps/workspace-web/e2e/phase2-full-shift-exit.spec.ts"
HARNESS_KEYS = {
    "checkpoint", "api_port", "vite_port", "static_smoke", "static_assets_checked",
    "playwright_pass", "queue_checkpoint", "queue_checkpoint_pass",
}
ASSERTION_KEYS = {"schema_version", "producer_id", "run_id", "browser_contract", "task_reconciliation"}
CONTRACT_KEYS = {"positive_actions", "transport_requests", "automatic_retries", "queue_insertions", "authoritative_reconciliation"}
TASK_KEYS = {"fresh_get_after_replay", "exact_task_id", "exact_committed_version", "status_in_progress", "dom_after_get"}


def _canonical_digest(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_harness(payload: dict) -> None:
    if set(payload) != HARNESS_KEYS:
        raise ValueError("BLOCKED_HARNESS_SCHEMA")
    if not (
        payload["checkpoint"] == "P2_FULL_SHIFT_EXIT"
        and payload["static_smoke"] is True
        and payload["playwright_pass"] is True
        and payload["queue_checkpoint"] == "bounded_exercised_and_cleaned"
        and payload["queue_checkpoint_pass"] is True
        and isinstance(payload["api_port"], int)
        and isinstance(payload["vite_port"], int)
        and isinstance(payload["static_assets_checked"], list)
        and all(
            isinstance(item, str) and item.startswith("/") and len(item) <= 200
            and "?" not in item and "#" not in item and "\\" not in item
            for item in payload["static_assets_checked"]
        )
    ):
        raise ValueError("BLOCKED_HARNESS_RESULT")


def _validate_assertions(payload: dict, run_id: str) -> None:
    if set(payload) != ASSERTION_KEYS or payload.get("schema_version") != 1:
        raise ValueError("BLOCKED_ASSERTION_SCHEMA")
    if payload.get("producer_id") != PRODUCER_ID or payload.get("run_id") != run_id:
        raise ValueError("BLOCKED_ASSERTION_PROVENANCE")
    contract = payload.get("browser_contract")
    task = payload.get("task_reconciliation")
    if not isinstance(contract, dict) or set(contract) != CONTRACT_KEYS:
        raise ValueError("BLOCKED_ASSERTION_CONTRACT_SCHEMA")
    if contract != {
        "positive_actions": "rendered_ui", "transport_requests": 1,
        "automatic_retries": 0, "queue_insertions": 0,
        "authoritative_reconciliation": True,
    }:
        raise ValueError("BLOCKED_ASSERTION_CONTRACT")
    if not isinstance(task, dict) or set(task) != TASK_KEYS or not all(value is True for value in task.values()):
        raise ValueError("BLOCKED_TASK_RECONCILIATION")


def run_phase2_harness(*, as_json: bool = False, evidence_json: Path | None = None) -> int:
    # Product contract accepts only 5..60 seconds; use the minimum valid
    # interval so the test proves real polling instead of an invalid-value
    # fallback to 15 seconds.
    os.environ.setdefault("VITE_POLL_INTERVAL_SECONDS", "5")
    run_id = str(uuid.uuid4())
    capture = io.StringIO()
    prior_run_id = os.environ.get("PHASE2_BROWSER_EVIDENCE_RUN_ID")
    prior_assertion_path = os.environ.get("PHASE2_BROWSER_ASSERTION_PATH")
    with tempfile.TemporaryDirectory(prefix="phase2_browser_assertions_") as owned_dir:
        assertion_path = Path(owned_dir) / "playwright-assertions.json"
        os.environ["PHASE2_BROWSER_EVIDENCE_RUN_ID"] = run_id
        os.environ["PHASE2_BROWSER_ASSERTION_PATH"] = str(assertion_path)
        try:
            with contextlib.redirect_stdout(capture):
                code = run_harness(
                    as_json=True,
                    checkpoint="P2_FULL_SHIFT_EXIT",
                    playwright_grep="Phase 2 full-shift exit evidence",
                    queue_checkpoint="bounded_exercised_and_cleaned",
                )
        finally:
            if prior_run_id is None:
                os.environ.pop("PHASE2_BROWSER_EVIDENCE_RUN_ID", None)
            else:
                os.environ["PHASE2_BROWSER_EVIDENCE_RUN_ID"] = prior_run_id
            if prior_assertion_path is None:
                os.environ.pop("PHASE2_BROWSER_ASSERTION_PATH", None)
            else:
                os.environ["PHASE2_BROWSER_ASSERTION_PATH"] = prior_assertion_path
        raw = capture.getvalue().strip()
        try:
            harness = json.loads(raw)
            if code != 0 or not isinstance(harness, dict):
                raise ValueError("BLOCKED_HARNESS_FAILURE")
            _validate_harness(harness)
            assertions = json.loads(assertion_path.read_text(encoding="utf-8"))
            if not isinstance(assertions, dict):
                raise ValueError("BLOCKED_ASSERTION_TYPE")
            _validate_assertions(assertions, run_id)
            payload = {
                "schema_version": 1,
                "producer_id": PRODUCER_ID,
                "run_id": run_id,
                "checkpoint": harness["checkpoint"],
                "playwright_pass": harness["playwright_pass"],
                "queue_checkpoint": harness["queue_checkpoint"],
                "queue_checkpoint_pass": harness["queue_checkpoint_pass"],
                "sanitized": True,
                "spec_sha256": hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
                "harness_payload": harness,
                "harness_sha256": _canonical_digest(harness),
                "assertions": assertions,
            }
        except (OSError, ValueError, json.JSONDecodeError):
            payload = {
                "schema_version": 1, "producer_id": PRODUCER_ID,
                "checkpoint": "P2_FULL_SHIFT_EXIT", "playwright_pass": False,
                "queue_checkpoint_pass": False, "sanitized": True,
            }
            code = 1
    serialized = json.dumps(payload, indent=2)
    if evidence_json is not None:
        evidence_json.parent.mkdir(parents=True, exist_ok=True)
        evidence_json.write_text(serialized + "\n", encoding="utf-8")
    if as_json:
        print(serialized)
    return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--evidence-json", type=Path)
    args = parser.parse_args()
    raise SystemExit(run_phase2_harness(as_json=args.json, evidence_json=args.evidence_json))
