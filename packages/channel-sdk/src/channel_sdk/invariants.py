"""Pinned P4-D adapter-result invariant loader and validator."""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

P4D_ADAPTER_RESULT_MATRIX_CANONICAL_DIGEST = "f09811c29e94de7a93300a1dc4aa8ed6eae3a9bd83418840089c5156224bfb6d"


@lru_cache(maxsize=1)
def adapter_result_matrix() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[4] / "docs/cvf/invariants/p4d-adapter-result-outcomes.json"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != P4D_ADAPTER_RESULT_MATRIX_CANONICAL_DIGEST:
        raise RuntimeError("P4-D adapter-result matrix digest mismatch")
    return json.loads(raw)


def validate_adapter_result(value: Mapping[str, Any]) -> None:
    candidates = [o for o in adapter_result_matrix()["outcomes"] if o["outcomeId"] == value.get("status")]
    if len(candidates) != 1:
        raise ValueError("unknown adapter result status")
    shape = candidates[0]["shapes"][0]
    keys = set(value)
    if keys != set(shape["requiredFields"]) or set(shape["forbiddenFields"]) & keys:
        raise ValueError("adapter result shape mismatch")
    for field, domain in shape["fieldDomains"].items():
        item = value[field]
        if domain["type"] == "STRING" and not isinstance(item, str):
            raise ValueError("adapter result field type mismatch")
        if domain["type"] == "BOOLEAN" and type(item) is not bool:
            raise ValueError("adapter result field type mismatch")
        if "const" in domain and item != domain["const"]:
            raise ValueError("adapter result constant mismatch")
        if "enum" in domain and item not in domain["enum"]:
            raise ValueError("adapter result enum mismatch")
        if "pattern" in domain and re.fullmatch(domain["pattern"], item) is None:
            raise ValueError("adapter result pattern mismatch")
