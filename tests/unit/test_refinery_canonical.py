from datetime import datetime, timezone
import hashlib

import pytest

from pydantic import ValidationError

from refinery_bridge.canonical import (
    candidate_fingerprint,
    canonical_json_bytes,
    collision_suspected,
    dedupe_content_fingerprint,
    source_fingerprint,
    triples_equal,
)
from refinery_bridge.input_models import DedupeRecordV1, SourceFingerprintV1


def test_canonical_json_exact_bytes() -> None:
    value = {"z": 1, "a": "Tiếng Việt", "labels": ["a", "b"]}
    assert canonical_json_bytes(value) == (
        '{"a":"Tiếng Việt","labels":["a","b"],"z":1}'.encode()
    )


@pytest.mark.parametrize("invalid", [{"a": None}, {"a": 1.5}, {1: "a"}])
def test_canonical_json_rejects_invalid_values(invalid: dict[object, object]) -> None:
    with pytest.raises(ValueError):
        canonical_json_bytes(invalid)  # type: ignore[arg-type]


def test_source_and_candidate_fingerprints_are_reproducible() -> None:
    source = source_fingerprint("abc")
    assert source.sha256 == hashlib.sha256(b"abc").hexdigest()
    assert source.byte_length == 3
    first = candidate_fingerprint({"schema_version": "1.0", "value": "x"})
    second = candidate_fingerprint({"value": "x", "schema_version": "1.0"})
    assert first == second


def test_collision_predicate_complete_vectors() -> None:
    base = SourceFingerprintV1(sha256="a" * 64, sha512="b" * 128, byte_length=1)
    same = base.model_copy()
    length_diff = base.model_copy(update={"byte_length": 2})
    sha256_only = base.model_copy(update={"sha512": "c" * 128})
    sha512_only = base.model_copy(update={"sha256": "d" * 64})
    neither = SourceFingerprintV1(sha256="d" * 64, sha512="c" * 128, byte_length=1)
    assert triples_equal(base, same)
    assert collision_suspected(base, length_diff)
    assert collision_suspected(base, sha256_only)
    assert collision_suspected(base, sha512_only)
    assert not collision_suspected(base, neither)


def test_all_typed_fingerprints_have_independent_golden_bytes() -> None:
    source_bytes = "Tiếng Việt".encode("utf-8")
    source = source_fingerprint("Tiếng Việt")
    assert (source.sha256, source.sha512, source.byte_length) == (
        hashlib.sha256(source_bytes).hexdigest(), hashlib.sha512(source_bytes).hexdigest(), len(source_bytes)
    )
    preimage = {"schema_version": "1.0", "value": "x"}
    golden = b'{"schema_version":"1.0","value":"x"}'
    for typed in (dedupe_content_fingerprint(preimage), candidate_fingerprint(preimage)):
        assert (typed.sha256, typed.sha512, typed.byte_length) == (
            hashlib.sha256(golden).hexdigest(), hashlib.sha512(golden).hexdigest(), len(golden)
        )
    with pytest.raises(ValidationError):
        DedupeRecordV1(
            scope_id="scope", prior_source_id="prior",
            observed_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
            source_fingerprint=candidate_fingerprint(preimage),
        )
