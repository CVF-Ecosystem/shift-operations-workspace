"""Bind the existing native smoke to the admitted local Docker transport."""
from __future__ import annotations

import json
import sys

import p5a2_source_demo_smoke as native_smoke
from p5a2_source_demo_common import check_hex
from p5a2_source_demo_recovery_custody import EXPECTED_NONCE
from p5a2_source_demo_recovery_docker import inspect as local_inspect


def smoke(nonce: str) -> dict:
    if not check_hex(nonce) or nonce != EXPECTED_NONCE:
        raise RuntimeError("OWNER_NONCE_INVALID")
    original = native_smoke.inspect
    native_smoke.inspect = local_inspect
    try:
        return native_smoke.smoke(nonce)
    finally:
        native_smoke.inspect = original


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"result": "SMOKE_REFUSED", "reason": "ARGUMENTS_INVALID"}))
        return 1
    try:
        print(json.dumps(smoke(sys.argv[1]), sort_keys=True))
        return 0
    except Exception:
        print(json.dumps({"result": "SMOKE_FAILED", "reason": "SMOKE_FAILED"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
