"""Integration tests for repair round 2 (F2-R1, F3-R1): production
run_parity, build_conformance_summary expected-disposition judging (the
three mandatory F3-R1 adversarial probes), and real ownership-binding
enforcement. Split out of test_invariant_family_repository_guard.py, which
covers round-0/round-1 baseline coverage for the same guard entry point.

NOTE (repair round 2, out-of-band authorization): this path was created by
explicit operator confirmation during REPAIR_WORKER round 2 because
test_invariant_family_repository_guard.py could not absorb the F2-R1/F3-R1
additions under the 300-line ceiling without removing assertions, and no
sibling exact-27 test path existed to redistribute into. It was NOT
authorized through the standard CVF DESIGN/Work-Order amendment chain and is
outside the tranche's exact-27 Work Order ceiling as originally authorized.
See the round-2 worker return for the full authorization record and the
explicit residual finding this creates for independent rereview.
"""
from __future__ import annotations
import copy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_invariant_families as guard  # noqa: E402
import invariant_family_contract as ifc  # noqa: E402
import invariant_family_ownership as ownership  # noqa: E402
import invariant_family_synthetic_emitter as emitter  # noqa: E402

MATRIX_PATH = REPO_ROOT / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
MATRIX_REL = "docs/cvf/invariants/synthetic-terminal-outcome.json"
MATRIX = ifc.load_json_no_dup(MATRIX_PATH)

def _agree(shape: dict, instance: dict) -> bool:
    return ifc.matches_shape_exactly(shape, instance, MATRIX)

def test_parity_helper_detects_false_acceptance() -> None:
    # Production ifc.run_parity, not a local reimplementation: a mutated
    # (invalid) instance where one surface wrongly accepts must disagree.
    shape = MATRIX["outcomes"][0]["shapes"][0]
    valid = emitter.emit_accepted("z")
    mutation = ifc.generate_mutations(MATRIX, "ACCEPTED_VALID", valid)[0]
    surfaces = [_agree, lambda s, i: True]
    assert not ifc.run_parity(surfaces, shape, mutation.payload)

def test_parity_helper_detects_false_rejection() -> None:
    shape = MATRIX["outcomes"][0]["shapes"][0]
    valid = emitter.emit_accepted("z")
    assert not ifc.run_parity([_agree, lambda s, i: False], shape, valid)

def test_parity_helper_agrees_when_surfaces_actually_agree() -> None:
    shape = MATRIX["outcomes"][0]["shapes"][0]
    valid = emitter.emit_accepted("z")
    assert ifc.run_parity([_agree, _agree], shape, valid)

def _f3_emit(outcome_id: str) -> dict:
    return emitter.emit_accepted("f3-probe") if outcome_id == "ACCEPTED" else emitter.emit_refused("POLICY_BLOCKED")


def _f3_broken_emit(outcome_id: str) -> dict:
    if outcome_id == "ACCEPTED":
        return {"outcome": "ACCEPTED", "payload": "x", "provider_attempts": 1, "output_digest": "0" * 64}
    return emitter.emit_refused("POLICY_BLOCKED")


def test_production_conformance_summary_passes_on_real_emitter() -> None:
    # F3-R1: exercises the real reusable helper end-to-end, not a test-local
    # stand-in — proves emitted positives are bound to their intended shape,
    # judged against every declared validator's actual accept/reject verdict
    # (not merely agreement between validators), the full mutation corpus
    # runs and every mutation is correctly judged, and the summary carries
    # per-validator results, mutation counts by operator, parity and
    # ownership.
    digest = ifc.canonical_digest(MATRIX_PATH)
    surfaces = {"python_contract": lambda s, i: ifc.matches_shape_exactly(s, i, MATRIX), "second_agreeing_surface": lambda s, i: ifc.matches_shape_exactly(s, i, MATRIX)}
    summary = guard.build_conformance_summary(MATRIX, digest, MATRIX_REL, _f3_emit, surfaces=surfaces)
    assert summary["result"] == "PASS"
    assert summary["ownershipResult"] == "PASS"
    assert sorted(summary["validatorSurfaces"]) == ["python_contract", "second_agreeing_surface"]
    assert len(summary["outcomes"]) == 2
    for o in summary["outcomes"]:
        assert o["positiveBoundToIntendedShape"] is True
        assert o["mutationCorpusComplete"] is True
        assert o["mutationCount"] > 0
        assert sum(o["mutationCountByOperator"].values()) == o["mutationCount"]
        assert all(m["allCorrect"] for m in o["mutations"])
        assert all(set(m["perValidator"]) == {"python_contract", "second_agreeing_surface"} for m in o["mutations"])


def test_production_conformance_summary_fails_on_broken_emitter() -> None:
    # F3-R1: induced-failure proof — a real digest mismatch must surface as
    # an overall FAIL, not be silently swallowed.
    summary = guard.build_conformance_summary(MATRIX, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_broken_emit)
    assert summary["result"] == "FAIL"


def test_production_conformance_summary_fails_when_all_validators_false_accept_mutations() -> None:
    # F3-R1 probe 1 (Work Order 19.3.3): supplying two validators that
    # accept every mutation must return FAIL through production code, not a
    # false PASS from mere validator agreement.
    always_accept = {"v1": lambda s, i: True, "v2": lambda s, i: True}
    summary = guard.build_conformance_summary(MATRIX, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_emit, surfaces=always_accept)
    assert summary["result"] == "FAIL"
    assert any(not m["allCorrect"] for o in summary["outcomes"] for m in o["mutations"])


def test_production_conformance_summary_fails_when_all_validators_false_reject_positives() -> None:
    # F3-R1 probe 2: supplying two validators that reject every positive
    # must return FAIL, even though both validators agree with each other.
    always_reject = {"v1": lambda s, i: False, "v2": lambda s, i: False}
    summary = guard.build_conformance_summary(MATRIX, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_emit, surfaces=always_reject)
    assert summary["result"] == "FAIL"
    assert any(not o["positivePerValidator"]["v1"] for o in summary["outcomes"])


def test_production_conformance_summary_fails_on_zero_mutation_corpus() -> None:
    # F3-R1 probe 3: excluding every applicable mutation operator produces
    # an empty/incomplete corpus, which must independently fail regardless
    # of what the (correctly judged) positive and any remaining cases show.
    starved = copy.deepcopy(MATRIX)
    for outcome in starved["outcomes"]:
        for shape in outcome["shapes"]:
            starved["mutationPolicy"]["excludedOperators"] = starved["mutationPolicy"].get("excludedOperators", []) + [
                {"operator": op, "shapeId": shape["shapeId"], "reason": "induced-empty-corpus-probe", "independentReviewRequired": True}
                for op in ("DELETE_REQUIRED_FIELD", "ADD_FORBIDDEN_FIELD", "ADD_UNKNOWN_FIELD", "REPLACE_DISCRIMINATOR", "WRONG_TYPE", "CONST_MISMATCH", "ENUM_MISMATCH", "MIN_LENGTH_VIOLATION", "PATTERN_MISMATCH", "COUNTER_MUTATION")
            ]
    summary = guard.build_conformance_summary(starved, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_emit)
    assert summary["result"] == "FAIL"
    assert any(not o["mutationCorpusComplete"] for o in summary["outcomes"])


def test_ownership_binding_rejects_missing_owner_file() -> None:
    mutated = copy.deepcopy(MATRIX)
    mutated["ownershipBindings"][0]["ownerPath"] = "docs/cvf/invariants/does-not-exist.json"
    diags = ownership.check_ownership_bindings(mutated, "test", "F")
    assert any(d.code == "IFC_UNSAFE_OWNER_PATH" for d in diags)


def test_ownership_binding_rejects_stale_canonical_digest() -> None:
    original = ownership.extract_module_symbol
    ownership.extract_module_symbol = lambda path, symbol: "0" * 64
    try:
        diags = ownership.check_ownership_bindings(
            MATRIX, "docs/cvf/invariants/synthetic-terminal-outcome.json", MATRIX["familyId"],
        )
    finally:
        ownership.extract_module_symbol = original
    assert any(d.code == "IFC_STALE_OWNERSHIP_DIGEST" for d in diags)


def test_ownership_binding_proves_real_owner_to_consumer_digest_match() -> None:
    # Positive proof the CANONICAL_DIGEST binding is non-self-confirming:
    # the consumer's embedded constant is independent data that must equal
    # the owner's live recomputed digest, not a value derived at guard time.
    diags = ownership.check_ownership_bindings(
        MATRIX, "docs/cvf/invariants/synthetic-terminal-outcome.json", MATRIX["familyId"],
    )
    assert diags == []
    declared = ownership.extract_module_symbol(
        REPO_ROOT / "scripts" / "invariant_family_synthetic_emitter.py", "OWNER_MATRIX_CANONICAL_DIGEST",
    )
    assert declared == ifc.canonical_digest(MATRIX_PATH)


# --- F1-R3: required-operator obligation is independent of the generator ----

def _drop_operator(operator: str):
    original = ifc.generate_mutations

    def wrapped(matrix: dict, shape_id: str, valid: dict) -> list:
        return [m for m in original(matrix, shape_id, valid) if m.operator != operator]

    return wrapped


def test_summary_fails_when_counter_mutation_branch_is_lost(monkeypatch) -> None:
    # Both production aliases are patched together so no unpatched alias can
    # act as an accidental oracle; the independent obligation still requires
    # COUNTER_MUTATION, so the summary must fail.
    wrapped = _drop_operator("COUNTER_MUTATION")
    monkeypatch.setattr(ifc, "generate_mutations", wrapped)
    monkeypatch.setattr(guard, "generate_mutations", wrapped)
    summary = guard.build_conformance_summary(MATRIX, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_emit)
    assert summary["result"] == "FAIL"
    assert any(not o["mutationCorpusComplete"] for o in summary["outcomes"])


def test_summary_fails_when_one_side_relation_branch_is_lost(monkeypatch) -> None:
    wrapped = _drop_operator("ONE_SIDE_RELATION_CHANGE")
    monkeypatch.setattr(ifc, "generate_mutations", wrapped)
    monkeypatch.setattr(guard, "generate_mutations", wrapped)
    summary = guard.build_conformance_summary(MATRIX, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_emit)
    assert summary["result"] == "FAIL"
    assert any(not o["mutationCorpusComplete"] for o in summary["outcomes"])


# --- F3-R3: ADAPTER_ASSERTION is a load-bearing AST binding proof ----------

_ADAPTER = "tests/integration/test_invariant_family_repository_guard_repair_round2.py"


def _adapter_binding(fn: str) -> dict:
    return {
        "ownershipBindings": [{
            "bindingId": "B", "ownerPath": "docs/cvf/invariants/synthetic-terminal-outcome.json",
            "consumers": [{"consumerPath": _ADAPTER, "strategy": "ADAPTER_ASSERTION",
                           "adapterTestPath": _ADAPTER, "assertionFunction": fn}],
        }]
    }


def _assert_true_with_unused_owner_string() -> None:
    unused = "docs/cvf/invariants/synthetic-terminal-outcome.json"
    assert True


def _owner_only_in_comment() -> None:
    # docs/cvf/invariants/synthetic-terminal-outcome.json
    assert MATRIX["familyId"] == MATRIX["familyId"]


def _owner_not_in_assert_dataflow() -> None:
    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))["familyId"]
    assert MATRIX["familyId"] == MATRIX["familyId"]


def _constant_only_comparison() -> None:
    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))["familyId"]
    assert owner_value == "SYNTHETIC-TERMINAL-OUTCOME"


def _wrong_owner_path() -> None:
    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/registry.json"))["schemaVersion"]
    assert owner_value == MATRIX["schemaVersion"]


def test_adapter_assertion_rejects_lexical_and_unbound_proofs() -> None:
    for fn in ("_assert_true_with_unused_owner_string", "_owner_only_in_comment", "_owner_not_in_assert_dataflow", "_constant_only_comparison", "_wrong_owner_path"):
        diags = ownership.check_ownership_bindings(_adapter_binding(fn), "t", "F")
        assert any(d.code == "IFC_ASSERTION_NOT_BOUND_TO_OWNER" for d in diags)


# --- F1-R4: exact mutation-id obligations (single-case removal) -------------
def test_summary_fails_when_single_mutation_case_removed(monkeypatch) -> None:
    original = ifc.generate_mutations
    for mid in ("ACCEPTED_VALID::COUNTER_MUTATION::provider_attempts_minus_one", "ACCEPTED_VALID::DELETE_REQUIRED_FIELD::payload"):
        wrapped = lambda m, s, v, _m=mid: [x for x in original(m, s, v) if x.mutationId != _m]
        monkeypatch.setattr(ifc, "generate_mutations", wrapped)
        monkeypatch.setattr(guard, "generate_mutations", wrapped)
        assert guard.build_conformance_summary(MATRIX, ifc.canonical_digest(MATRIX_PATH), MATRIX_REL, _f3_emit)["result"] == "FAIL"


# --- F3-R4: declared consumer binding (equality + consumer path) ------------
def _adapter_inequality_proof() -> None:
    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))["familyId"]
    consumer_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/registry.json"))["families"][0]["familyId"]
    assert owner_value != consumer_value


def _adapter_unrelated_global_proof() -> None:
    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))["familyId"]
    consumer_value = MATRIX
    assert owner_value == consumer_value


def test_adapter_assertion_rejects_non_allowlisted_reads() -> None:
    for fn in ("_adapter_inequality_proof", "_adapter_unrelated_global_proof", "_adapter_evil_module_proof", "_adapter_local_shadow_proof"):
        diags = ownership.check_ownership_bindings(_adapter_binding(fn), "t", "F")
        assert any(d.code == "IFC_ASSERTION_NOT_BOUND_TO_OWNER" for d in diags)


def _adapter_evil_module_proof() -> None:
    owner_value = evil.load_json_no_dup(evil.safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))
    consumer_value = evil.load_json_no_dup(evil.safe_repo_path("docs/cvf/invariants/registry.json"))
    assert owner_value == consumer_value


def _adapter_local_shadow_proof() -> None:
    owner_value = load_json_no_dup(safe_repo_path("docs/cvf/invariants/synthetic-terminal-outcome.json"))
    consumer_value = load_json_no_dup(safe_repo_path("docs/cvf/invariants/registry.json"))
    assert owner_value == consumer_value


def test_adapter_assertion_rejects_ifc_binding_shadows(tmp_path: Path, monkeypatch) -> None:
    srcs = [
        "import invariant_family_contract as ifc\nimport evil as ifc\n\ndef probe():\n    assert True\n",
        "import invariant_family_contract as ifc\n\nifc = None\n\ndef probe():\n    assert True\n",
        "import invariant_family_contract as ifc\n\ndef probe(ifc):\n    assert True\n",
        "import invariant_family_contract as ifc\n\ndef probe(value):\n    match value:\n        case [*ifc]: pass\n    assert True\n",
        "import invariant_family_contract as ifc\n\ndef probe(value):\n    match value:\n        case {**ifc}: pass\n    assert True\n",
        "def binder():\n    import invariant_family_contract as ifc\n\ndef probe():\n    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/synthetic-terminal-outcome.json'))\n    consumer_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/registry.json'))\n    assert owner_value == consumer_value\n",
        "import invariant_family_contract as ifc\nfrom evil import *\n\ndef probe():\n    owner_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/synthetic-terminal-outcome.json'))\n    consumer_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/registry.json'))\n    assert owner_value == consumer_value\n",
        "import invariant_family_contract as ifc\n\ndef outer():\n    def probe():\n        owner_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/synthetic-terminal-outcome.json'))\n        consumer_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/registry.json'))\n        assert owner_value == consumer_value\n",
        "import invariant_family_contract as ifc\n\nclass Holder:\n    def probe(self):\n        owner_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/synthetic-terminal-outcome.json'))\n        consumer_value = ifc.load_json_no_dup(ifc.safe_repo_path('docs/cvf/invariants/registry.json'))\n        assert owner_value == consumer_value\n",
    ]
    for index, src in enumerate(srcs):
        (tmp_path / "fixture.py").write_text(src, encoding="utf-8")
        monkeypatch.setattr(ifc, "REPO_ROOT", tmp_path)
        code = ownership._verify_adapter_assertion({"adapterTestPath": "fixture.py", "assertionFunction": "probe"}, "docs/cvf/invariants/synthetic-terminal-outcome.json", "docs/cvf/invariants/registry.json")
        assert code == ("IFC_MISSING_ASSERTION_FUNCTION" if index >= len(srcs) - 2 else "IFC_ASSERTION_NOT_BOUND_TO_OWNER")
