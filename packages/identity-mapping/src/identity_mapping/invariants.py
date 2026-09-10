"""Pinned matrix consumers for P4-E mapping-action and identity-resolution
outcomes (SPEC section 2). This module is the sole place identity-mapping
loads/validates against `P4E-MAPPING-ACTION-OUTCOMES` and
`P4E-IDENTITY-RESOLUTION-OUTCOMES`; it never restates their outcome grammar.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


class ContractViolation(Exception):
    """A receipt/result did not conform to its pinned invariant matrix."""


class MatrixDriftError(ContractViolation):
    """A pinned invariant matrix file is missing, unreadable, or its digest
    no longer matches its pin (SPEC section 2: digest drift stops BUILD)."""


P4E_MAPPING_ACTION_MATRIX_CANONICAL_DIGEST = (
    "ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a"
)
P4E_IDENTITY_RESOLUTION_MATRIX_CANONICAL_DIGEST = (
    "4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc"
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
            if domain.get("type") == "BOOLEAN" and not isinstance(value, bool):
                valid = False
            if "pattern" in domain and isinstance(value, str):
                import re

                if re.fullmatch(domain["pattern"], value) is None:
                    valid = False
            if isinstance(value, str) and len(value) < domain.get("minLength", 0):
                valid = False
        if valid:
            return
        errors.append("field domain mismatch")
    raise ContractViolation(errors[0] if errors else "receipt does not match matrix")


def validate_mapping_action_receipt(receipt: Mapping[str, Any]) -> None:
    _validate(
        _load_matrix(
            "p4e-mapping-action-outcomes.json",
            P4E_MAPPING_ACTION_MATRIX_CANONICAL_DIGEST,
        ),
        receipt,
    )


def validate_identity_resolution_result(result: Mapping[str, Any]) -> None:
    _validate(
        _load_matrix(
            "p4e-identity-resolution-outcomes.json",
            P4E_IDENTITY_RESOLUTION_MATRIX_CANONICAL_DIGEST,
        ),
        result,
    )


def emit_mapping_action_receipt(outcome: str, **fields: Any):
    from .models import MappingActionReceipt

    return MappingActionReceipt(outcome=outcome, **fields)


def emit_identity_resolution_result(outcome: str, **fields: Any):
    from .models import IdentityResolutionResult

    return IdentityResolutionResult(outcome=outcome, **fields)
