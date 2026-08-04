from __future__ import annotations

import hashlib
import json
from typing import Any, TypeVar

from .input_models import (
    CandidateFingerprintV1,
    DedupeContentFingerprintV1,
    FingerprintV1,
    SourceFingerprintV1,
)

FingerprintType = TypeVar("FingerprintType", bound=FingerprintV1)


def _validate_json_value(value: Any) -> None:
    if value is None or isinstance(value, float):
        raise ValueError("null and float values are forbidden")
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("mapping keys must be strings")
        for nested in value.values():
            _validate_json_value(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _validate_json_value(nested)
    elif not isinstance(value, (str, int, bool)):
        raise ValueError("unsupported canonical value")


def canonical_json_bytes(preimage: dict[str, Any]) -> bytes:
    _validate_json_value(preimage)
    return json.dumps(
        preimage,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fingerprint(data: bytes, cls: type[FingerprintType]) -> FingerprintType:
    return cls(
        sha256=hashlib.sha256(data).hexdigest(),
        sha512=hashlib.sha512(data).hexdigest(),
        byte_length=len(data),
    )


def source_fingerprint(raw_text: str) -> SourceFingerprintV1:
    return _fingerprint(raw_text.encode("utf-8", errors="strict"), SourceFingerprintV1)


def dedupe_content_fingerprint(preimage: dict[str, Any]) -> DedupeContentFingerprintV1:
    return _fingerprint(canonical_json_bytes(preimage), DedupeContentFingerprintV1)


def candidate_fingerprint(preimage: dict[str, Any]) -> CandidateFingerprintV1:
    return _fingerprint(canonical_json_bytes(preimage), CandidateFingerprintV1)


def triples_equal(left: FingerprintV1, right: FingerprintV1) -> bool:
    return (
        left.sha256 == right.sha256
        and left.sha512 == right.sha512
        and left.byte_length == right.byte_length
    )


def collision_suspected(left: FingerprintV1, right: FingerprintV1) -> bool:
    return not triples_equal(left, right) and (
        left.sha256 == right.sha256 or left.sha512 == right.sha512
    )
