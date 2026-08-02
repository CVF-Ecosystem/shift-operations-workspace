"""C3d Web Evidence Harness (WO P2C-C3D-SUPERVISOR-CLOSEOUT-WO-001).

Reuses run_c3c_web_evidence.run_harness's exact command construction,
readiness/timeout, sanitization and owned-resource cleanup contract
(WO section 4: "MUST preserve the C3c runner contract") with checkpoint="C3d"
so this module never forks port/process/cleanup logic. It runs the complete
combined operator+supervisor Playwright suite (all e2e/*.spec.ts files) since
Playwright's default `test` command already picks up every spec in testDir;
no --grep filter is needed for this checkpoint.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.run_c3c_web_evidence import run_harness  # noqa: E402


def run_c3d_harness(as_json: bool = False) -> int:
    return run_harness(as_json=as_json, checkpoint="C3d", playwright_grep=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output evidence as JSON")
    args = parser.parse_args()
    sys.exit(run_c3d_harness(as_json=args.json))
