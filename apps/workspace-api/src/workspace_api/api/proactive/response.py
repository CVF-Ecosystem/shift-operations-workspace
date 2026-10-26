"""Bounded HTTP projection of the native scoped-source receipt."""

from __future__ import annotations

import json

from fastapi import Response
from pydantic import ConfigDict, create_model

from workspace_api.application.proactive_source_receipt import (
    READY_FIELDS, REFUSED_FIELDS, emit_source_refused, validate_source_receipt,
)

P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST = "6fec188950fe752ac438e2952ec3d4e2ffd3b4156efa0b9a2e06e1048c568754"
MAX_RESPONSE_BYTES = 1_048_576
NO_CACHE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


def _structural_model(name: str, fields: frozenset[str]):
    """Project native field presence/types for docs; native validator owns rules."""
    count_fields = {"eligible_count", "selected_count", "candidate_version_count",
                    "max_snapshot_incident_refs"}
    return create_model(
        name, __config__=ConfigDict(extra="forbid"),
        **{key: (int if key in count_fields else str, ...)
           for key in sorted(fields)},
    )


ReadyReceipt = _structural_model("P5A2ReadyReceipt", READY_FIELDS)
RefusedReceipt = _structural_model("P5A2RefusedReceipt", REFUSED_FIELDS)


def bounded_json(receipt: dict) -> bytes | None:
    """Incrementally encode actual UTF-8 bytes without releasing a prefix."""
    parts: list[bytes] = []
    size = 0
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    for fragment in encoder.iterencode(receipt):
        chunk = fragment.encode("utf-8")
        size += len(chunk)
        if size > MAX_RESPONSE_BYTES:
            return None
        parts.append(chunk)
    return b"".join(parts)


def prepare_receipt(receipt: dict) -> tuple[dict, bytes]:
    try:
        validate_source_receipt(receipt)
        encoded = bounded_json(receipt)
    except Exception:
        receipt = emit_source_refused("SOURCE_UNAVAILABLE")
        encoded = bounded_json(receipt)
    if encoded is None:
        receipt = emit_source_refused("SCOPE_INCOMPLETE")
        encoded = bounded_json(receipt)
    assert encoded is not None
    return receipt, encoded


def receipt_response(encoded: bytes) -> Response:
    return Response(content=encoded, status_code=200, media_type="application/json",
                    headers=NO_CACHE)


def error_response(status: int) -> Response:
    detail = {401: "Authentication required", 403: "Access denied",
              422: "Invalid request"}[status]
    return Response(content=json.dumps({"detail": detail}, separators=(",", ":")),
                    status_code=status, media_type="application/json", headers=NO_CACHE)
