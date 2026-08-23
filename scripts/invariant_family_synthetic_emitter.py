"""Bootstrap synthetic deterministic emitter for the SYNTHETIC-TERMINAL-OUTCOME
invariant family (SPEC R14). Proves generic mechanics only: zero provider or
network calls, not a stand-in for P4-B or any real runtime family.
"""
from __future__ import annotations

import hashlib

# CANONICAL_DIGEST ownership binding (SPEC R11): this consumer's independent
# copy of the owner matrix's canonical SHA-256. The guard recomputes the
# owner file's live canonical_digest() and compares it to this constant; if
# they diverge, the binding is stale and the guard fails closed. This value
# is data a repair/edit to the matrix can accidentally leave behind unchanged
# (proving the check is real, not tautological) - it is not derived from the
# owner file at guard runtime.
OWNER_MATRIX_CANONICAL_DIGEST = "c44e83cf78021be97f2217644ea4209e571347bd665010a56c7eab03ad73ec2c"


def emit_accepted(payload: str) -> dict[str, object]:
    """Deterministic ACCEPTED receipt for a non-empty payload string."""
    if not isinstance(payload, str) or not payload:
        raise ValueError("payload must be a non-empty string")
    return {
        "outcome": "ACCEPTED",
        "payload": payload,
        "provider_attempts": 1,
        "output_digest": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
    }


def emit_refused(reason: str) -> dict[str, object]:
    """Deterministic REFUSED receipt for one of the two synthetic reasons."""
    if reason not in ("POLICY_BLOCKED", "INPUT_INVALID"):
        raise ValueError("reason must be POLICY_BLOCKED or INPUT_INVALID")
    return {
        "outcome": "REFUSED",
        "reason": reason,
        "provider_attempts": 0,
    }


def emit_synthetic_terminal_outcome(kind: str, **kwargs: object) -> dict[str, object]:
    """Single dispatch entry point cited as the matrix emitterAdapter identity."""
    if kind == "ACCEPTED":
        return emit_accepted(str(kwargs["payload"]))
    if kind == "REFUSED":
        return emit_refused(str(kwargs["reason"]))
    raise ValueError(f"unknown synthetic emitter kind: {kind!r}")
