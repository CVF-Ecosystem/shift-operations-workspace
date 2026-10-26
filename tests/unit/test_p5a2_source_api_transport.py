"""Native family, HTTP representation and actual UTF-8 byte limits."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import sys

import pytest

from workspace_api.api.proactive import response as http_response
from workspace_api.application.proactive_source_access import SourceAccess, server_scope
from workspace_api.application.proactive_source_receipt import (
    COHORT_VERSION, READY_FIELDS, REFUSED_FIELDS, validate_source_receipt,
)
from cvf_runtime.identity import Principal

from p5a2_source_api_helpers import api_oracle, frozen_refusal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from invariant_family_contract import canonical_digest, generate_mutations  # noqa: E402


def test_frozen_samples_and_complete_family_mutations_rejected_by_both_consumers():
    matrix_path = ROOT / "docs/cvf/invariants/p5a2-scoped-source-outcomes.json"
    assert canonical_digest(matrix_path) == http_response.P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    samples = [
        ("P5A2_SOURCE_READY", api_oracle()["cases"][0]["expected_receipt"]),
        ("P5A2_SOURCE_REFUSED", frozen_refusal("ACCESS_DENIED")),
    ]
    counts = {}
    for shape, sample in samples:
        validate_source_receipt(sample)
        received, encoded = http_response.prepare_receipt(sample)
        assert received == sample and json.loads(encoded) == sample
        mutations = generate_mutations(matrix, shape, sample)
        assert mutations
        for mutation in mutations:
            with pytest.raises(ValueError):
                validate_source_receipt(mutation.payload)
            closed, wire = http_response.prepare_receipt(mutation.payload)
            assert closed == frozen_refusal("SOURCE_UNAVAILABLE")
            assert json.loads(wire) == closed
        counts[shape] = len(mutations)
    assert sum(counts.values()) >= 84


def test_openapi_field_sets_derive_from_native_representation():
    from workspace_api.main import app
    schema = app.openapi()
    response = schema["paths"]["/proactive/source"]["get"]["responses"]["200"]
    variants = response["content"]["application/json"]["schema"]["anyOf"]
    names = [item["$ref"].split("/")[-1] for item in variants]
    documented = {frozenset(schema["components"]["schemas"][name]["required"])
                  for name in names}
    assert documented == {READY_FIELDS, REFUSED_FIELDS}
    parameters = schema["paths"]["/proactive/source"]["get"]["parameters"]
    assert {item["name"] for item in parameters} == {
        "query_start", "query_end", "run_as_of",
    }
    assert all(item["in"] == "query" and item["required"] is True and
               item["schema"]["maxLength"] == 128 for item in parameters)


def test_nonascii_actor_scope_uses_canonical_utf8_not_ascii_escapes():
    actor = "Ca đêm"
    instance = "PUBLIC-SOURCE-INSTANCE-1"
    canonical = json.dumps({
        "actor_id": actor, "instance_id": instance,
        "cohort_policy_version": COHORT_VERSION,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
       allow_nan=False).encode("utf-8")
    expected = "P5A2-SELF-" + sha256(canonical).hexdigest()
    access = SourceAccess(Principal(user_id=actor, role="viewer"),
                          None, None, instance, None)
    assert server_scope(access).scope_id == expected


def test_incremental_json_byte_limit_is_exact_and_utf8_aware(monkeypatch):
    value = {"text": "Ca đêm"}
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    monkeypatch.setattr(http_response, "MAX_RESPONSE_BYTES", len(encoded))
    assert http_response.bounded_json(value) == encoded
    monkeypatch.setattr(http_response, "MAX_RESPONSE_BYTES", len(encoded) - 1)
    assert http_response.bounded_json(value) is None


def test_actual_1mib_utf8_limit_and_single_byte_overflow():
    # Independent literal UTF-8 byte accounting, with a multibyte prefix.
    prefix = '{"text":"đ'
    suffix = '"}'
    room = 1_048_576 - len(prefix.encode("utf-8")) - len(suffix.encode("utf-8"))
    exact = {"text": "đ" + "x" * room}
    result = http_response.bounded_json(exact)
    assert result is not None and len(result) == 1_048_576
    assert json.loads(result) == exact
    assert http_response.bounded_json({"text": exact["text"] + "x"}) is None


def test_oversized_valid_ready_discards_every_success_byte(monkeypatch):
    ready = api_oracle()["cases"][0]["expected_receipt"]
    full = http_response.bounded_json(ready)
    assert full is not None
    monkeypatch.setattr(http_response, "MAX_RESPONSE_BYTES", len(full) - 1)
    closed, wire = http_response.prepare_receipt(ready)
    assert closed == frozen_refusal("SCOPE_INCOMPLETE")
    assert b"canonical_manifest" not in wire
    assert json.loads(wire) == closed


@pytest.mark.parametrize("reason", [
    "ACCESS_DENIED", "INVALID_WINDOW", "TIME_AMBIGUOUS", "COVERAGE_UNKNOWN",
    "SCOPE_INCOMPLETE", "SNAPSHOT_UNAVAILABLE", "INVALID_LINEAGE",
    "INCOMPATIBLE_POLICY", "SOURCE_UNAVAILABLE",
])
def test_all_nine_frozen_refusals_preserve_exact_http_shape(reason):
    expected = frozen_refusal(reason)
    receipt, wire = http_response.prepare_receipt(expected)
    assert receipt == expected
    assert json.loads(wire) == expected
