"""Pinned matrix consumers and the two declared real receipt emitters."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from .errors import ContractViolation, MatrixDriftError

P4C_INGRESS_MATRIX_CANONICAL_DIGEST = (
    "277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b"
)
P4C_OUTBOUND_MATRIX_CANONICAL_DIGEST = (
    "41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6"
)


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


@lru_cache(maxsize=2)
def _load_matrix(filename: str, expected_digest: str) -> Mapping[str, Any]:
    path = _repository_root() / "docs" / "cvf" / "invariants" / filename
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise MatrixDriftError("required invariant matrix is unavailable") from exc
    if hashlib.sha256(raw).hexdigest() != expected_digest:
        raise MatrixDriftError("invariant matrix digest does not match its pin")
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MatrixDriftError("required invariant matrix is invalid") from exc
    return document


def _validate(matrix: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    outcome = receipt.get("outcome")
    matching = [entry for entry in matrix["outcomes"] if entry["outcomeId"] == outcome]
    if len(matching) != 1:
        raise ContractViolation("unknown terminal outcome")
    errors: list[str] = []
    for shape in matching[0]["shapes"]:
        required = set(shape["requiredFields"])
        forbidden = set(shape["forbiddenFields"])
        present = set(receipt)
        if not required.issubset(present):
            errors.append("required field missing")
            continue
        if forbidden.intersection(present):
            errors.append("forbidden field present")
            continue
        valid = True
        for field, domain in shape["fieldDomains"].items():
            if field not in receipt:
                continue
            value = receipt[field]
            if "const" in domain and value != domain["const"]:
                valid = False
            if "enum" in domain and value not in domain["enum"]:
                valid = False
            if domain.get("type") == "STRING" and not isinstance(value, str):
                valid = False
            if domain.get("type") == "INTEGER" and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                valid = False
            if isinstance(value, str) and len(value) < domain.get("minLength", 0):
                valid = False
        if valid:
            return
        errors.append("field domain mismatch")
    raise ContractViolation(errors[0] if errors else "receipt does not match matrix")


def validate_ingress_terminal_receipt(receipt: Mapping[str, Any]) -> None:
    _validate(
        _load_matrix(
            "p4c-ingress-terminal-outcomes.json",
            P4C_INGRESS_MATRIX_CANONICAL_DIGEST,
        ),
        receipt,
    )


def validate_outbound_terminal_receipt(receipt: Mapping[str, Any]) -> None:
    _validate(
        _load_matrix(
            "p4c-outbound-terminal-outcomes.json",
            P4C_OUTBOUND_MATRIX_CANONICAL_DIGEST,
        ),
        receipt,
    )


def emit_ingress_terminal_receipt(outcome: str, **fields: Any):
    from .models import IngressReceipt

    return IngressReceipt(outcome=outcome, **fields)


def emit_outbound_terminal_receipt(outcome: str, **fields: Any):
    from .models import OutboundReceipt

    return OutboundReceipt(outcome=outcome, **fields)
