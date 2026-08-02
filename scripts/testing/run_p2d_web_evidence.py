"""P2-D real-browser evidence wrapper over the shared C3c process harness."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.run_c3c_web_evidence import run_harness  # noqa: E402


def run_p2d_harness(as_json: bool = False) -> int:
    os.environ.setdefault("VITE_POLL_INTERVAL_SECONDS", "5")
    return run_harness(
        as_json=as_json,
        checkpoint="P2D",
        playwright_grep="P2-D bounded offline and polling evidence",
        queue_checkpoint="bounded_exercised_and_cleaned",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sys.exit(run_p2d_harness(as_json=args.json))
