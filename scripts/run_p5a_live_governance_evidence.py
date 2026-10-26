#!/usr/bin/env python3
"""Explicit, one-use P5-A A7 canary; root alone owns --execute.

Default invocation is credential-free readiness. Import is inert. Structural
tests provide no provider result and cannot satisfy the A7 live gate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p5a_live_contract import (
    ADMISSION_ID,
    ENDPOINT,
    canonical_bytes,
    request_body,
    sanitized_response,
    sha256,
    terminal_receipt,
    validate_response,
)
from _p5a_live_preflight import CHECKS, gate_child, run_preflight
from _p5a_live_transport import (
    RECEIPT,
    MarkerError,
    marker_present,
    one_post,
    read_current_user_key,
    reserve_marker,
)

ROOT = Path(__file__).resolve().parents[1]
COUNTERS = ("marker_reservations", "key_read_attempts", "transport_attempts",
            "responses", "accepted_responses", "retry_count", "redirect_count",
            "fallback_count")


def zero_counts() -> dict[str, int]:
    return {name: 0 for name in COUNTERS}


def _initial_envelope() -> dict:
    return {
        "schema_version": "1.0", "status": "PARTIAL_PREFLIGHT", "commit": None,
        "clean_worktree": False, "source_hashes": {},
        "checks": [{"name": name, "state": "NOT_RUN", "reason": None} for name in CHECKS],
        "api_observations": [],
    }


def _write_evidence(wrapper: dict, *, key: str | None = None) -> None:
    """Exclusive terminal write; existing evidence is never replaced."""
    data = canonical_bytes(wrapper) + b"\n"
    if key and key.encode("utf-8") in data:
        raise ValueError("secret material would persist")
    if b'"Authorization"' in data or b'"authorization"' in data:
        raise ValueError("authorization header would persist")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(RECEIPT, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def _wrapper(receipt: dict, envelope: dict, request: str | None = None,
             response: str | None = None, capture: dict | None = None) -> dict:
    return {
        "schema_version": "1.0", "claim_boundary": "One admitted PUBLIC synthetic digest-echo call only",
        "terminal_receipt": receipt, "gate_observation_envelope": envelope,
        "sanitized_request_body": request, "sanitized_response_body": response,
        "response_capture": capture,
        "outcome_unknown": receipt["outcome"] == "RESERVED_NOT_ACCEPTED_OR_UNKNOWN",
        "cost_estimate_basis": {
            "version": "P5A-20261023-short-input-Singapore-v1",
            "formula": "prompt_tokens * 50 + completion_tokens * 400",
            "unit": "nano-USD", "input_nano_usd_per_token": 50,
            "output_nano_usd_per_token": 400, "ceiling_nano_usd": 10_000_000,
            "price_reference_url": "https://www.alibabacloud.com/help/en/model-studio/qwen-flash",
            "price_checked_at": "2026-10-23", "admission_id": ADMISSION_ID,
            "claim": "Published short-input Singapore list price; estimate, not invoice or quota proof",
        },
    }


def _emit(outcome: str, stage: str, reason: str, envelope: dict, counts: dict,
          *, request: str | None = None, response: str | None = None,
          capture: dict | None = None, key: str | None = None, **fields: object) -> dict:
    digest = sha256(canonical_bytes(envelope))
    receipt = terminal_receipt(outcome, stage, reason, digest, counts, **fields)
    wrapper = _wrapper(receipt, envelope, request, response, capture)
    _write_evidence(wrapper, key=key)
    return receipt


def _release_bound(envelope: dict, commit: str, full_gate_result: str) -> bool:
    """Record root's explicit reviewed-source gate attestation, not CI proof."""
    valid = (envelope["status"] == "COMPLETE" and commit == envelope["commit"]
             and len(full_gate_result) <= 160 and full_gate_result.strip() == full_gate_result
             and full_gate_result.isprintable() and "passed" in full_gate_result)
    envelope["a7_source_release_attestation"] = {
        "reviewed_commit": commit, "normal_full_gate_result": full_gate_result,
        "authority": "root_supplied_after_independent_source_review",
    }
    if not valid:
        envelope["status"] = "PARTIAL_PREFLIGHT"
        envelope["checks"][2].update(state="FAIL", reason="SOURCE_HASH_MISMATCH")
    return valid


def execute(reviewed_commit: str, full_gate_result: str) -> dict:
    """One explicit effect path. Worker/tests must never invoke it."""
    counts = zero_counts()
    if marker_present():
        counts["marker_reservations"] = 1
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "MARKER_RESERVATION",
                     "MARKER_ALREADY_EXISTS", _initial_envelope(), counts)
    envelope, failed = run_preflight()
    if failed or not _release_bound(envelope, reviewed_commit, full_gate_result):
        if marker_present():
            counts["marker_reservations"] = 1
            return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "MARKER_RESERVATION",
                         "MARKER_ALREADY_EXISTS", envelope, counts)
        return _emit("PRECALL_BLOCKED_ZERO_CALL", "PREFLIGHT",
                     failed or "SOURCE_HASH_MISMATCH", envelope, counts)
    digest = sha256(canonical_bytes(envelope))
    try:
        reserve_marker(ADMISSION_ID, reviewed_commit, digest)
    except MarkerError as exc:
        if exc.reserved:
            counts["marker_reservations"] = 1
            return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "MARKER_RESERVATION",
                         exc.reason, envelope, counts)
        return _emit("PRECALL_BLOCKED_ZERO_CALL", "PREFLIGHT",
                     "MARKER_RESERVATION_FAILED", envelope, counts)
    counts["marker_reservations"] = 1
    counts["key_read_attempts"] = 1
    try:
        key = read_current_user_key()
    except ValueError as exc:
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "KEY_LOOKUP",
                     str(exc), envelope, counts)
    except Exception:  # noqa: BLE001 -- never expose credential-store exception text
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "KEY_LOOKUP",
                     "KEY_READ_FAILED", envelope, counts)
    try:
        body = request_body(digest)
    except ValueError:
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "REQUEST_PREPARATION",
                     "REQUEST_BUILD_FAILED", envelope, counts, key=key)
    request_text = body.decode("utf-8")
    request_sha = sha256(body)
    result = one_post(ENDPOINT, body, key)
    counts["transport_attempts"] = int(result.get("attempted", False))
    if not counts["transport_attempts"]:
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "REQUEST_PREPARATION",
                     "CLIENT_CONFIGURATION_FAILED", envelope, counts,
                     request=request_text, key=key)
    if result["kind"] != "response":
        reason = "NETWORK_TIMEOUT" if result["kind"] == "timeout" else "CLIENT_ERROR"
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "TRANSPORT", reason,
                     envelope, counts, request=request_text, key=key,
                     sanitized_request_sha256=request_sha)
    counts["responses"] = 1
    status, raw = result["status"], result["body"]
    capture = {"body_size": result["size"], "raw_sha256": result["sha256"],
               "complete_within_64k": raw is not None}
    if raw is None:
        return _emit("RESERVED_NOT_ACCEPTED_OR_UNKNOWN", "RESPONSE_VALIDATION",
                     "RESPONSE_CAPTURE_INCOMPLETE", envelope, counts, request=request_text,
                     capture=capture, key=key, sanitized_request_sha256=request_sha,
                     sanitized_response_sha256=result["sha256"], http_status=status,
                     usage_state="NOT_PARSED")
    response_text, response_sha = sanitized_response(raw, key)
    reason, fields = validate_response(status, raw, digest)
    if reason == "NONE":
        counts["accepted_responses"] = 1
        outcome = "ACCEPTED_SINGLE_RESPONSE"
        stage = "ACCEPTED"
    else:
        outcome = "RESERVED_NOT_ACCEPTED_OR_UNKNOWN"
        stage = "RESPONSE_VALIDATION"
        fields = {name: value for name, value in fields.items() if name not in
                  {"model", "choice_count", "finish_reason", "gate_digest_echo"}}
        if fields.get("usage_state") != "VALID":
            for name in ("prompt_tokens", "completion_tokens", "total_tokens",
                         "estimated_cost_nano_usd"):
                fields.pop(name, None)
    return _emit(outcome, stage, reason, envelope, counts, request=request_text,
                 response=response_text, capture=capture, key=key,
                 sanitized_request_sha256=request_sha,
                 sanitized_response_sha256=response_sha, **fields)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="root-owned admitted one-use effect")
    parser.add_argument("--reviewed-source-commit")
    parser.add_argument("--source-full-gate-result")
    parser.add_argument("--_gate-child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args._gate_child:
        try:
            print(json.dumps(gate_child(), sort_keys=True, separators=(",", ":")))
            return 0
        except Exception:  # noqa: BLE001 -- child must not print raw API probe errors
            return 1
    if not args.execute:
        if args.reviewed_source_commit or args.source_full_gate_result:
            parser.error("release attestation requires --execute")
        envelope, reason = run_preflight()
        print(json.dumps({"readiness": "READY_ZERO_CALL" if reason is None else "BLOCKED_ZERO_CALL",
                          "safe_reason": reason, "gate_observation_sha256":
                          sha256(canonical_bytes(envelope))}, sort_keys=True))
        return 0 if reason is None else 2
    if not args.reviewed_source_commit or not args.source_full_gate_result:
        parser.error("--execute requires root-reviewed source commit and full-gate result")
    try:
        receipt = execute(args.reviewed_source_commit, args.source_full_gate_result)
    except Exception:  # noqa: BLE001 -- never print possible credential/transport errors
        # Unknown after reservation is terminal. Never retry or print raw errors.
        print("P5A_A7_TERMINAL_UNKNOWN; inspect the fixed marker/evidence paths")
        return 3
    print(json.dumps({"outcome": receipt["outcome"], "terminal_reason": receipt["terminal_reason"]},
                     sort_keys=True))
    return 0 if receipt["outcome"] == "ACCEPTED_SINGLE_RESPONSE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
