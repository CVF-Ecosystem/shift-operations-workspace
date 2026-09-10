"""P4-E pinned matrix contract tests (SPEC AC-01): schema, ownership-pin,
positive corpus, and deterministic one-fact mutation for all three
registered families - `P4E-MAPPING-ACTION-OUTCOMES`,
`P4E-IDENTITY-RESOLUTION-OUTCOMES`, `P4E-CONVERSATION-PLACEMENT-OUTCOMES`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from identity_mapping.invariants import (
    P4E_IDENTITY_RESOLUTION_MATRIX_CANONICAL_DIGEST,
    P4E_MAPPING_ACTION_MATRIX_CANONICAL_DIGEST,
    emit_identity_resolution_result,
    emit_mapping_action_receipt,
)
from conversation_routing.invariants import (
    P4E_PLACEMENT_MATRIX_CANONICAL_DIGEST,
    emit_placement_decision,
)

ROOT = Path(__file__).resolve().parents[2]
MATRIX_DIR = ROOT / "docs" / "cvf" / "invariants"

CASES = (
    ("p4e-mapping-action-outcomes.json", P4E_MAPPING_ACTION_MATRIX_CANONICAL_DIGEST, emit_mapping_action_receipt),
    ("p4e-identity-resolution-outcomes.json", P4E_IDENTITY_RESOLUTION_MATRIX_CANONICAL_DIGEST, emit_identity_resolution_result),
    ("p4e-placement-outcomes.json", P4E_PLACEMENT_MATRIX_CANONICAL_DIGEST, emit_placement_decision),
)


def _positive(shape: dict) -> dict:
    result = {}
    for field in shape["requiredFields"]:
        domain = shape["fieldDomains"][field]
        if "const" in domain:
            result[field] = domain["const"]
        elif "enum" in domain:
            result[field] = domain["enum"][0]
        elif "pattern" in domain and domain.get("type") == "STRING":
            result[field] = "a" * 64
        elif domain.get("type") == "INTEGER":
            result[field] = 1
        elif domain.get("type") == "BOOLEAN":
            result[field] = True
        else:
            result[field] = "x"
    return result


@pytest.mark.parametrize("filename,expected_digest,emitter", CASES)
def test_matrix_digest_matches_pin(filename, expected_digest, emitter):
    raw = (MATRIX_DIR / filename).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected_digest


@pytest.mark.parametrize("filename,expected_digest,emitter", CASES)
def test_matrix_is_closed_top_level_object_with_required_registry_fields(filename, expected_digest, emitter):
    matrix = json.loads((MATRIX_DIR / filename).read_text(encoding="utf-8"))
    assert matrix["closedTopLevelObject"] is True
    assert matrix["ownerRole"] == "SPEC_AUTHOR"
    assert matrix["risk"] == "R2"
    assert matrix["lifecycle"] == "ACTIVE"
    assert len(matrix["applicabilityTriggers"]) >= 4


@pytest.mark.parametrize("filename,expected_digest,emitter", CASES)
def test_raw_real_emitter_positive_per_outcome(filename, expected_digest, emitter):
    matrix = json.loads((MATRIX_DIR / filename).read_text(encoding="utf-8"))
    for outcome in matrix["outcomes"]:
        shape = outcome["shapes"][0]
        raw = _positive(shape)
        outcome_value = raw.pop("outcome")
        emitted = emitter(outcome_value, **raw)
        dumped = emitted.model_dump(exclude_none=True)
        assert dumped["outcome"] == outcome["outcomeId"]
        for field, value in raw.items():
            assert dumped[field] == value


@pytest.mark.parametrize("filename,expected_digest,emitter", CASES)
def test_one_fact_mutation_per_required_field_is_rejected(filename, expected_digest, emitter):
    """SPEC AC-01: deterministic one-fact mutation for every field and
    closed outcome - removing exactly one required field must fail closed."""
    matrix = json.loads((MATRIX_DIR / filename).read_text(encoding="utf-8"))
    for outcome in matrix["outcomes"]:
        shape = outcome["shapes"][0]
        for missing_field in shape["requiredFields"]:
            if missing_field == "outcome":
                continue
            raw = _positive(shape)
            outcome_value = raw.pop("outcome")
            raw.pop(missing_field)
            with pytest.raises(Exception):
                emitter(outcome_value, **raw)


@pytest.mark.parametrize("filename,expected_digest,emitter", CASES)
def test_forbidden_field_present_is_rejected(filename, expected_digest, emitter):
    matrix = json.loads((MATRIX_DIR / filename).read_text(encoding="utf-8"))
    for outcome in matrix["outcomes"]:
        shape = outcome["shapes"][0]
        if not shape["forbiddenFields"]:
            continue
        raw = _positive(shape)
        outcome_value = raw.pop("outcome")
        raw[shape["forbiddenFields"][0]] = "unexpected"
        with pytest.raises(Exception):
            emitter(outcome_value, **raw)


def test_placement_family_consumes_but_does_not_duplicate_mapping_rules():
    """DESIGN section 11: the placement family consumes a pinned
    mapping-family result but does not duplicate its rules - the two
    matrices are not the same outcome vocabulary, and neither restates the
    other's action/reason enum verbatim."""
    mapping = json.loads((MATRIX_DIR / "p4e-mapping-action-outcomes.json").read_text(encoding="utf-8"))
    placement = json.loads((MATRIX_DIR / "p4e-placement-outcomes.json").read_text(encoding="utf-8"))
    mapping_outcomes = {o["outcomeId"] for o in mapping["outcomes"]}
    placement_outcomes = {o["outcomeId"] for o in placement["outcomes"]}
    assert mapping_outcomes != placement_outcomes
    assert "action" not in json.dumps(placement)
    assert "target_kind" not in json.dumps(mapping)
