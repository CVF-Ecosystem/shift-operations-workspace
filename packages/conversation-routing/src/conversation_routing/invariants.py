"""Pinned matrix consumer for P4-E placement outcomes (SPEC section 2). This
module is the sole place conversation-routing loads/validates against
`P4E-CONVERSATION-PLACEMENT-OUTCOMES`; it never restates its outcome grammar.
The placement family consumes a pinned mapping-family result but does not
duplicate its rules (SPEC section 2 / DESIGN section 11).
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


class ContractViolation(Exception):
    """A receipt/result did not conform to its pinned invariant matrix."""


class MatrixDriftError(ContractViolation):
    """A pinned invariant matrix file is missing, unreadable, or its digest
    no longer matches its pin (SPEC section 2: digest drift stops BUILD)."""


P4E_PLACEMENT_MATRIX_CANONICAL_DIGEST = (
    "fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56"
)


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


@lru_cache(maxsize=1)
def _load_matrix() -> Mapping[str, Any]:
    path = _repository_root() / "docs" / "cvf" / "invariants" / "p4e-placement-outcomes.json"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise MatrixDriftError("required invariant matrix is unavailable") from exc
    if hashlib.sha256(raw).hexdigest() != P4E_PLACEMENT_MATRIX_CANONICAL_DIGEST:
        raise MatrixDriftError("invariant matrix digest does not match its pin")
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MatrixDriftError("required invariant matrix is invalid") from exc
    return document


def validate_placement_decision(receipt: Mapping[str, Any]) -> None:
    matrix = _load_matrix()
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
                if re.fullmatch(domain["pattern"], value) is None:
                    valid = False
            if isinstance(value, str) and len(value) < domain.get("minLength", 0):
                valid = False
        if valid:
            return
        errors.append("field domain mismatch")
    raise ContractViolation(errors[0] if errors else "receipt does not match matrix")


def emit_placement_decision(outcome: str, **fields: Any):
    from .models import PlacementDecisionReceipt

    return PlacementDecisionReceipt(outcome=outcome, **fields)
