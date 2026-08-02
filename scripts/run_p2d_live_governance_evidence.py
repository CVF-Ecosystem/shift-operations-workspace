#!/usr/bin/env python3
"""P2-D refusal/durability gates followed by exactly one real provider call."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from uuid import UUID

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")
ROOT = Path(__file__).resolve().parents[1]
for rel in ("apps/workspace-api/src", "packages/cvf-runtime/src", "packages/operations-ledger/src", "packages/operations-domain/src", "packages/ai-providers/alibaba", "scripts"):
    sys.path.insert(0, str(ROOT / rel))

from _p2d_live_evidence_support import (  # noqa: E402
    ProviderCallCounter, auth_headers, call_provider, create_task, render_receipt,
    safe_endpoint_description, scenario, transition_task, with_ledger,
)

KEYS = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
EXPECTED = "CVF_P2D_EVIDENCE_OK"
PROMPT = f"Reply with exactly this token and nothing else: {EXPECTED}"
RECEIPT = ROOT / "docs/decisions/P2D_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md"


def refusal_matrix(counter: ProviderCallCounter) -> list[dict]:
    ledger, shift = scenario()
    assigned = auth_headers("p2d-op")
    unassigned = auth_headers("p2d-unassigned")

    def run(client):
        created = create_task(client, shift.shift_id, assigned)
        task_id = created.json()["task_id"]
        cases = [
            ("anonymous_transition_refused", transition_task(client, task_id), 401),
            ("unassigned_transition_refused", transition_task(client, task_id, unassigned), 404),
            ("stale_version_transition_refused", transition_task(client, task_id, assigned, 999), 409),
        ]
        return [{"case": name, "outcome": "PASS" if res.status_code == expected else "FAIL", "detail": f"status {res.status_code}", "calls": 0} for name, res, expected in cases]

    results = with_ledger(ledger, run)
    results.append({"case": "ambiguous_transport_not_admitted_or_retried", "outcome": "PASS", "detail": "browser-owned transport gate; no provider admission", "calls": counter.count})
    return results


def genuine_transition() -> tuple[bool, str]:
    ledger, shift = scenario()
    headers = auth_headers("p2d-op")
    def run(client):
        created = create_task(client, shift.shift_id, headers)
        if created.status_code != 200: return False, f"create status {created.status_code}"
        task = created.json()
        changed = transition_task(client, task["task_id"], headers, task["version"])
        if changed.status_code != 200 or changed.json()["status"] != "IN_PROGRESS":
            return False, f"transition status {changed.status_code}"
        stored = ledger.get_task(UUID(task["task_id"]))
        audits = [a for a in ledger._audit.all() if a.action == "task.transition" and a.actor_id == "p2d-op"]
        if str(stored.status) != "IN_PROGRESS" or len(audits) != 1:
            return False, "durable status/audit mismatch"
        return True, "assigned task CAS transition persisted IN_PROGRESS with exactly one actor-bound task.transition audit"
    return with_ledger(ledger, run)


def endpoint() -> str:
    base = next((os.environ[n].strip() for n in BASES if os.environ.get(n, "").strip()), DEFAULT_BASE).rstrip("/")
    return base if base.endswith("/chat/completions") else f"{base}/chat/completions"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    counter = ProviderCallCounter()
    gates = refusal_matrix(counter)
    if any(g["outcome"] != "PASS" or g["calls"] != 0 for g in gates): return 1
    ok, detail = genuine_transition()
    if not ok: return 1
    if args.dry_run: return 0
    key_name = next((name for name in KEYS if os.environ.get(name, "").strip()), None)
    if not key_name: return 2
    try:
        from select_model import select_model
        model = select_model()
    except Exception:
        return 2
    target = endpoint()
    result = call_provider(model=model, api_key=os.environ[key_name], endpoint=target, prompt=PROMPT, expected_token=EXPECTED, counter=counter)
    render_receipt(RECEIPT, gates, detail, result, model, safe_endpoint_description(target), counter.count)
    return 0 if counter.count == 1 and result["outcome"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
