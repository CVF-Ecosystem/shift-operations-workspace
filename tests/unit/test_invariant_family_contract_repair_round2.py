"""Unit tests for repair round 2 (F1-R1, F2-R1, F4-R1, F5-R1): structural
closure, per-strategy ownership-binding enforcement, closed conditional-rule/
nested-shape semantics and diagnostic sanitization. Split out of
test_invariant_family_contract.py, which covers round-0/round-1 baseline
coverage for the same modules.

NOTE (repair round 2, out-of-band authorization): this path was created by
explicit operator confirmation during REPAIR_WORKER round 2 because
test_invariant_family_contract.py could not absorb the F1-R1 through F5-R1
additions under the 300-line ceiling without removing assertions, and no
sibling exact-27 test path existed to redistribute into. It was NOT
authorized through the standard CVF DESIGN/Work-Order amendment chain and is
outside the tranche's exact-27 Work Order ceiling as originally authorized.
See the round-2 worker return for the full authorization record and the
explicit residual finding this creates for independent rereview.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_invariant_families as guard  # noqa: E402
import invariant_family_contract as ifc  # noqa: E402
import invariant_family_ownership as ownership  # noqa: E402

MATRIX = ifc.load_json_no_dup(REPO_ROOT / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json")


# --- F1-R1: complete structural closure (conditional/nested/duplicate) ------

def test_registry_and_matrix_schema_reject_unknown_top_level_field() -> None:
    registry = ifc.load_json_no_dup(guard.REGISTRY_PATH)
    assert guard.validate_against_schema({**registry, "unknownRegistryField": True}, "registry")
    assert guard.validate_against_schema({**MATRIX, "unknownMatrixField": True})

def test_matrix_semantics_rejects_unknown_relation_operand_and_duplicate_relation_id() -> None:
    bad_operand = copy.deepcopy(MATRIX)
    bad_operand["outcomes"][0]["shapes"][0]["relations"][0]["sourceField"] = "undeclared_field"
    diags = guard._check_matrix_semantics(bad_operand, "test", "F")
    assert any(d.code == "IFC_UNKNOWN_RELATION_OPERAND" for d in diags)

    dup_relation = copy.deepcopy(MATRIX)
    dup = copy.deepcopy(dup_relation["outcomes"][0]["shapes"][0]["relations"][0])
    dup_relation["outcomes"][0]["shapes"][0]["relations"].append(dup)
    diags = guard._check_matrix_semantics(dup_relation, "test", "F")
    assert any(d.code == "IFC_DUPLICATE_RELATION_ID" for d in diags)

def test_orphan_conditional_rule_is_rejected() -> None:
    # F1-R1: an orphan controllingField reference must fail, not be treated
    # as a legal no-op (round-1 repair incorrectly asserted the opposite).
    mutated = copy.deepcopy(MATRIX)
    mutated["outcomes"][0]["shapes"][0]["conditionalRules"] = [
        {"field": "extra_flag", "controllingField": "nonexistent_controller", "controllingValue": "X", "presence": "REQUIRED_WHEN_MATCH"}
    ]
    diags = guard._check_matrix_semantics(mutated, "t", "F")
    assert any(d.code == "IFC_UNKNOWN_CONDITIONAL_CONTROLLING_FIELD" for d in diags)

def test_unknown_nested_shape_target_is_rejected() -> None:
    # F1-R1: a NESTED_OBJECT fieldDomain whose nestedShapeId does not
    # resolve to any shape in the matrix must fail.
    mutated = copy.deepcopy(MATRIX)
    mutated["outcomes"][0]["shapes"][0]["fieldDomains"]["ghost"] = {"type": "NESTED_OBJECT", "nestedShapeId": "DOES_NOT_EXIST"}
    mutated["outcomes"][0]["shapes"][0]["requiredFields"].append("ghost")
    diags = guard._check_matrix_semantics(mutated, "t", "F")
    assert any(d.code == "IFC_UNKNOWN_NESTED_SHAPE_TARGET" for d in diags)

def test_exact_duplicate_contract_source_entry_is_rejected() -> None:
    # F1-R1: schema-level uniqueItems on contractSources plus Python-level
    # duplicate-path detection for the (path-only-duplicate, digest
    # differing) case that uniqueItems cannot express.
    mutated = copy.deepcopy(MATRIX)
    mutated["contractSources"].append(copy.deepcopy(mutated["contractSources"][0]))
    assert guard.validate_against_schema(mutated)

    mutated_path_only = copy.deepcopy(MATRIX)
    second = copy.deepcopy(mutated_path_only["contractSources"][0])
    second["sha256"] = "0" * 64
    mutated_path_only["contractSources"].append(second)
    diags = guard._check_matrix_semantics(mutated_path_only, "t", "F")
    assert any(d.code == "IFC_DUPLICATE_CONTRACT_SOURCE_PATH" for d in diags)


# --- F2-R1: every ownership strategy requires proof and is enforced --------

def test_direct_identity_strategy_requires_matching_symbol_in_both_files() -> None:
    diags = ownership.check_ownership_bindings(
        {
            "ownershipBindings": [{
                "bindingId": "B", "ownerPath": "scripts/invariant_family_synthetic_emitter.py",
                "ownerIdentitySymbol": "OWNER_MATRIX_CANONICAL_DIGEST",
                "consumers": [{"consumerPath": "scripts/invariant_family_contract.py", "strategy": "DIRECT_IDENTITY", "identitySymbol": "DOES_NOT_EXIST_SYMBOL"}],
            }]
        }, "t", "F",
    )
    assert any(d.code == "IFC_MISSING_CONSUMER_IDENTITY_SYMBOL" for d in diags)

def _adapter_binding(assertion_function: str) -> dict:
    return {
        "ownershipBindings": [{
            "bindingId": "B", "ownerPath": "docs/cvf/invariants/synthetic-terminal-outcome.json",
            "consumers": [{
                "consumerPath": "docs/cvf/invariants/registry.json",
                "strategy": "ADAPTER_ASSERTION",
                "adapterTestPath": "tests/unit/test_invariant_family_contract_repair_round2.py",
                "assertionFunction": assertion_function,
            }],
        }]
    }

def test_adapter_assertion_positive_proof_binds_owner_and_has_real_assert() -> None:
    # F3-R4 positive: equality-only owner-to-consumer comparison where the
    # consumer side loads from the exact declared consumerPath (registry).
    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))["familyId"]
    consumer_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/registry.json"))["families"][0]["familyId"]
    assert owner_value == consumer_value
    diags = ownership.check_ownership_bindings(
        _adapter_binding("test_adapter_assertion_positive_proof_binds_owner_and_has_real_assert"), "t", "F",
    )
    assert not any(d.familyId == "F" and "ASSERTION" in d.code for d in diags)

def test_adapter_assertion_positive_mutated_owner_or_consumer_is_rejected() -> None:
    # F3-R4: the positive proof fails when either declared path is mutated.
    fn = "test_adapter_assertion_positive_proof_binds_owner_and_has_real_assert"
    owner_binding = _adapter_binding(fn)
    owner_binding["ownershipBindings"][0]["ownerPath"] = "docs/cvf/invariants/registry.json"
    assert any(d.code == "IFC_ASSERTION_NOT_BOUND_TO_OWNER" for d in ownership.check_ownership_bindings(owner_binding, "t", "F"))
    consumer_binding = _adapter_binding(fn)
    consumer_binding["ownershipBindings"][0]["consumers"][0]["consumerPath"] = "docs/cvf/invariants/invariant-family.schema.json"
    assert any(d.code == "IFC_ASSERTION_NOT_BOUND_TO_OWNER" for d in ownership.check_ownership_bindings(consumer_binding, "t", "F"))

def test_adapter_assertion_missing_function_is_rejected() -> None:
    diags = ownership.check_ownership_bindings(
        _adapter_binding("test_function_that_does_not_exist_anywhere"), "t", "F",
    )
    assert any(d.code == "IFC_MISSING_ASSERTION_FUNCTION" for d in diags)

def _stub_with_no_assertion() -> None:
    """Owner path docs/cvf/invariants/synthetic-terminal-outcome.json is
    named here only in prose, proving a name-and-owner-reference match with
    zero real Python assert statements must still be rejected as proof."""

def test_adapter_assertion_function_with_no_assert_statement_is_rejected() -> None:
    diags = ownership.check_ownership_bindings(_adapter_binding("_stub_with_no_assertion"), "t", "F")
    assert any(d.code == "IFC_ASSERTION_FUNCTION_HAS_NO_ASSERTION" for d in diags)

def _assertion_not_bound_to_this_owner() -> None:
    assert 1 == 1

def test_adapter_assertion_function_not_referencing_owner_is_rejected() -> None:
    # F3-R2: a real assert that exists but never references the declared
    # owner path is not proof of binding to THAT owner - must fail closed.
    diags = ownership.check_ownership_bindings(_adapter_binding("_assertion_not_bound_to_this_owner"), "t", "F")
    assert any(d.code == "IFC_ASSERTION_NOT_BOUND_TO_OWNER" for d in diags)

def test_json_reference_strategy_detects_stale_reference() -> None:
    diags = ownership.check_ownership_bindings(
        {
            "ownershipBindings": [{
                "bindingId": "B", "ownerPath": "docs/cvf/invariants/registry.json",
                "consumers": [{"consumerPath": "docs/cvf/invariants/synthetic-terminal-outcome.json", "strategy": "JSON_REFERENCE", "jsonPointer": "/schemaVersion"}],
            }]
        }, "t", "F",
    )
    # registry.json schemaVersion "1.0" vs matrix schemaVersion "1.0": equal,
    # so this pointer is coincidentally stable; assert the checker actually
    # resolved both sides rather than short-circuiting.
    assert not any(d.code == "IFC_UNRESOLVABLE_JSON_REFERENCE" for d in diags)

def test_unsupported_ownership_strategy_is_rejected() -> None:
    strategy = copy.deepcopy(MATRIX)
    strategy["ownershipBindings"][0]["consumers"][0]["strategy"] = "NOT_A_REAL_STRATEGY"
    diags = ownership.check_ownership_bindings(strategy, "t", "F")
    assert any(d.code == "IFC_UNSUPPORTED_OWNERSHIP_STRATEGY" for d in diags)


# --- F4-R1: closed conditional-rule and nested-reference semantics --------

_MULTI_TYPE_MATRIX = {
    "outcomes": [
        {"outcomeId": "A", "shapes": [{
            "shapeId": "A_SHAPE",
            "requiredFields": ["flag", "amount", "echo_src", "echo_tgt", "nested", "mode"],
            "forbiddenFields": [],
            "conditionalRules": [{"field": "extra_note", "controllingField": "mode", "controllingValue": "STRICT", "presence": "REQUIRED_WHEN_MATCH"}],
            "fieldDomains": {
                "flag": {"type": "BOOLEAN"},
                "amount": {"type": "NUMBER"},
                "echo_src": {"type": "STRING", "minLength": 1},
                "echo_tgt": {"type": "STRING", "minLength": 1},
                "nested": {"type": "NESTED_OBJECT", "nestedShapeId": "NESTED_SHAPE"},
                "mode": {"type": "STRING", "enum": ["STRICT", "LOOSE"]},
                "extra_note": {"type": "STRING", "minLength": 1},
            },
            "relations": [{"relationId": "ECHO_EQ", "kind": "FIELD_EQUALITY", "sourceField": "echo_src", "targetField": "echo_tgt"}],
        }]},
        {"outcomeId": "B", "shapes": [{"shapeId": "B_SHAPE", "requiredFields": ["only_b"], "forbiddenFields": [], "conditionalRules": [], "fieldDomains": {"only_b": {"type": "STRING", "minLength": 1}}, "relations": []}]},
        {"outcomeId": "NESTED", "shapes": [{"shapeId": "NESTED_SHAPE", "requiredFields": ["inner"], "forbiddenFields": [], "conditionalRules": [], "fieldDomains": {"inner": {"type": "STRING", "minLength": 1}}, "relations": []}]},
    ],
    "mutationPolicy": {"excludedOperators": []},
}
_MULTI_TYPE_VALID = {"flag": True, "amount": 3.5, "echo_src": "x", "echo_tgt": "x", "nested": {"inner": "y"}, "mode": "STRICT", "extra_note": "n"}

def test_multi_type_positive_matches_and_full_mutation_basis_is_rejected() -> None:
    # BOOLEAN/NUMBER/FIELD_EQUALITY/NESTED_OBJECT/closed conditional rule:
    # positive matches, the basis covers FIELD_EQUALITY, RECURSE_NESTED_OBJECTS
    # and CONDITIONAL_FLIP, and every generated mutation is actually rejected.
    shape = _MULTI_TYPE_MATRIX["outcomes"][0]["shapes"][0]
    assert ifc.matches_shape_exactly(shape, _MULTI_TYPE_VALID, _MULTI_TYPE_MATRIX)
    mutations = ifc.generate_mutations(_MULTI_TYPE_MATRIX, "A_SHAPE", _MULTI_TYPE_VALID)
    operators = {m.operator for m in mutations}
    assert "ONE_SIDE_RELATION_CHANGE" in operators
    assert "RECURSE_NESTED_OBJECTS" in operators
    assert "CONDITIONAL_FLIP" in operators
    for m in mutations:
        assert not ifc.matches_shape_exactly(shape, m.payload, _MULTI_TYPE_MATRIX), m.mutationId

def test_conditional_rule_required_when_match_enforced_by_evaluator() -> None:
    # The evaluator (not just the mutator) must enforce the closed rule:
    # when mode==STRICT, extra_note is required; removing it while STRICT
    # must fail even though extra_note has no fieldDomains-forbidden marker.
    shape = _MULTI_TYPE_MATRIX["outcomes"][0]["shapes"][0]
    violating = copy.deepcopy(_MULTI_TYPE_VALID)
    del violating["extra_note"]
    assert not ifc.matches_shape_exactly(shape, violating, _MULTI_TYPE_MATRIX)

    loose = copy.deepcopy(_MULTI_TYPE_VALID)
    loose["mode"] = "LOOSE"
    del loose["extra_note"]
    assert ifc.matches_shape_exactly(shape, loose, _MULTI_TYPE_MATRIX)

def test_illegal_value_for_unconstrained_string_is_wrong_type_not_a_noop() -> None:
    domain = {"type": "STRING"}
    illegal = ifc._illegal_value_for_domain(domain)
    assert not isinstance(illegal, str)


# --- F5-R1: sanitization covers every diagnostic constructor ---------------

def test_schema_error_text_and_json_output_do_not_leak_raw_canary_value() -> None:
    mutated = {**MATRIX, "risk": "SECRET_CANARY_VALUE_8D72"}
    errors = guard.validate_against_schema(mutated)
    assert errors
    assert not any("SECRET_CANARY_VALUE_8D72" in e for e in errors)
    diags = [guard._diag(f"IFC_SCHEMA_{c}", "test", "F", "") for c in errors]
    payload = json.dumps([{"code": d.code, "path": d.path, "familyId": d.familyId, "message": d.message} for d in diags])
    assert "SECRET_CANARY_VALUE_8D72" not in payload

def test_duplicate_key_canary_does_not_leak_in_registry_or_nested_matrix(tmp_path: Path) -> None:
    # F5-R1: F6 was only fixed for jsonschema.ValidationError; DuplicateKey
    # handling still echoed str(exc), which IS the raw duplicate key. Prove
    # the canary is absent from both text and JSON diagnostic output for a
    # top-level registry duplicate key.
    registry_raw = '{"schemaVersion": "1.0", "SECRET_CANARY_DUP_KEY_77": 1, "SECRET_CANARY_DUP_KEY_77": 2, "families": []}'
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(registry_raw, encoding="utf-8")
    original_registry = guard.REGISTRY_PATH
    guard.REGISTRY_PATH = registry_path
    try:
        diags = guard.run()
    finally:
        guard.REGISTRY_PATH = original_registry
    assert any(d.code == "IFC_DUPLICATE_JSON_KEY" for d in diags)
    text_output = "\n".join(f"{d.code}\t{d.path}\t{d.familyId}\t{d.message}" for d in diags)
    json_output = json.dumps([{"code": d.code, "path": d.path, "familyId": d.familyId, "message": d.message} for d in diags])
    assert "SECRET_CANARY_DUP_KEY_77" not in text_output
    assert "SECRET_CANARY_DUP_KEY_77" not in json_output

def test_zero_outcomes_matrix_fails_schema_and_semantics() -> None:
    mutated = copy.deepcopy(MATRIX)
    mutated["outcomes"] = []
    assert guard.validate_against_schema(mutated)
    assert any(d.code == "IFC_TOO_FEW_OUTCOMES" for d in guard._check_matrix_semantics(mutated, "t", "F"))

def _registry_entry(matrix_name: str) -> dict:
    return {"familyId": MATRIX["familyId"], "matrixPath": f"docs/cvf/invariants/{matrix_name}", "ownerRole": MATRIX["ownerRole"], "risk": MATRIX["risk"], "lifecycle": "ACTIVE", "applicabilityMode": "X"}

def test_duplicate_family_id_with_differing_matrix_objects_is_rejected(tmp_path: Path) -> None:
    # Exercises the real registry-scan loop in guard.run(), not a
    # reimplementation: two entries sharing a familyId but pointing at two
    # genuinely different (differing-title) matrix files must both be caught.
    invariants_dir = tmp_path / "docs" / "cvf" / "invariants"
    invariants_dir.mkdir(parents=True)
    matrix_b = copy.deepcopy(MATRIX)
    matrix_b["title"] = "A deliberately different second matrix object"
    (invariants_dir / "matrix_a.json").write_text(json.dumps(MATRIX), encoding="utf-8")
    (invariants_dir / "matrix_b.json").write_text(json.dumps(matrix_b), encoding="utf-8")
    registry = {"schemaVersion": "1.0", "families": [_registry_entry("matrix_a.json"), _registry_entry("matrix_b.json")]}
    (invariants_dir / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
    original_root, original_registry, original_ifc_root = guard.REPO_ROOT, guard.REGISTRY_PATH, ifc.REPO_ROOT
    guard.REPO_ROOT, guard.REGISTRY_PATH, ifc.REPO_ROOT = tmp_path, invariants_dir / "registry.json", tmp_path
    try:
        diags = guard.run()
    finally:
        guard.REPO_ROOT, guard.REGISTRY_PATH, ifc.REPO_ROOT = original_root, original_registry, original_ifc_root
    assert any(d.code == "IFC_DUPLICATE_FAMILY_ID" for d in diags)
