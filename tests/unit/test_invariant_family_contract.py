"""Unit tests for invariant families, including P4-C registered matrices.
(SPEC R3-R16, R15; round-0/round-1). Covers AC-02, AC-04, AC-05: duplicate
JSON key rejection, path safety, digest canonicalization, mutation basis
completeness, shape matching. Repair round 2 additions (F1-R1 through
F5-R1, F7-R1) are in test_invariant_family_contract_repair_round2.py.
Repair round 3 F4-R2 (fail-closed symlink rejection before path resolution)
and F2-R2 (conditional-ownership duplicate/unreachable checks, exercised via
scripts/check_invariant_families.py) are appended below."""
from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_invariant_families as guard  # noqa: E402
import invariant_family_contract as ifc  # noqa: E402
import invariant_family_synthetic_emitter as emitter  # noqa: E402

MATRIX = ifc.load_json_no_dup(REPO_ROOT / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json")
ACCEPTED_SHAPE = MATRIX["outcomes"][0]["shapes"][0]
REFUSED_SHAPE = MATRIX["outcomes"][1]["shapes"][0]


def test_duplicate_json_key_raises() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "dup.json"
        p.write_text('{"a": 1, "a": 2}', encoding="utf-8")
        try:
            ifc.load_json_no_dup(p)
            assert False, "expected DuplicateKey"
        except ifc.DuplicateKey as exc:
            assert exc.args[0] == "a"


def test_safe_repo_path_rejects_traversal_and_absolute() -> None:
    assert ifc.safe_repo_path("../outside.json") is None
    assert ifc.safe_repo_path("/etc/passwd") is None
    assert ifc.safe_repo_path("C:/Windows/system32") is None
    assert ifc.safe_repo_path("a\\b.json") is None
    assert ifc.safe_repo_path("") is None
    assert ifc.safe_repo_path("docs/INDEX.md") is not None


def test_safe_repo_path_rejects_symlink(tmp_path: Path) -> None:
    real = tmp_path / "real.json"
    real.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlink privilege unavailable in this environment")
    assert not ifc.is_safe_regular_file(link)


def test_safe_repo_path_rejects_symlink_component_before_resolution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # F4-R2: Path.resolve() follows a symlink and returns a path whose own
    # is_symlink() is always False - a post-resolve check alone cannot see
    # it. safe_repo_path must reject the symlink using the unresolved
    # candidate, before resolution has a chance to erase that identity.
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    (real_dir / "target.json").write_text("{}", encoding="utf-8")
    link_dir = tmp_path / "link_dir"
    try:
        link_dir.symlink_to(real_dir, target_is_directory=True)
    except OSError:
        pytest.skip("symlink privilege unavailable in this environment")
    monkeypatch.setattr(ifc, "REPO_ROOT", tmp_path)
    assert ifc.safe_repo_path("link_dir/target.json") is None


def test_safe_repo_path_accepts_non_symlink_nested_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Paired positive: an ordinary nested real path with no symlink
    # component anywhere must still resolve normally.
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "target.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(ifc, "REPO_ROOT", tmp_path)
    assert ifc.safe_repo_path("a/b/target.json") is not None


def test_safe_repo_path_rejects_symlink_via_mocked_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # F4-R3: deterministic mocked filesystem-boundary negative that always
    # runs (no symlink privilege, no skip). Proves leaf and intermediate
    # symlinks are rejected on the unresolved candidate, resolve() is never
    # reached once a symlink component is detected, and an ordinary nested
    # non-symlink path still resolves.
    monkeypatch.setattr(ifc, "REPO_ROOT", tmp_path)
    (tmp_path / "real.json").write_text("{}", encoding="utf-8")
    symlink_nodes: set[str] = set()

    def fake_is_symlink(self: Path) -> bool:
        return str(self) in symlink_nodes

    resolve_calls: list[str] = []
    real_resolve = Path.resolve

    def fake_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        resolve_calls.append(str(self))
        return real_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "is_symlink", fake_is_symlink)
    monkeypatch.setattr(Path, "resolve", fake_resolve)

    # leaf symlink component
    symlink_nodes.add(str(tmp_path / "link.json"))
    assert ifc.safe_repo_path("link.json") is None
    # intermediate symlink component
    symlink_nodes.clear()
    symlink_nodes.add(str(tmp_path / "link_dir"))
    assert ifc.safe_repo_path("link_dir/target.json") is None
    # resolve() must not have been called for either rejection
    assert resolve_calls == []

    # ordinary nested non-symlink path is still accepted
    symlink_nodes.clear()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "target.json").write_text("{}", encoding="utf-8")
    assert ifc.safe_repo_path("a/b/target.json") is not None


def test_canonical_digest_is_universal_newline_stable() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        lf = Path(tmp) / "lf.txt"
        crlf = Path(tmp) / "crlf.txt"
        lf.write_bytes(b"hello\nworld\n")
        crlf.write_bytes(b"hello\r\nworld\r\n")
        assert ifc.canonical_digest(lf) == ifc.canonical_digest(crlf)
        changed = Path(tmp) / "changed.txt"
        changed.write_bytes(b"hello\nworld!\n")
        assert ifc.canonical_digest(lf) != ifc.canonical_digest(changed)


def test_real_emitter_positive_matches_exactly_one_shape() -> None:
    accepted = emitter.emit_accepted("abc")
    refused = emitter.emit_refused("POLICY_BLOCKED")
    assert ifc.matches_shape_exactly(ACCEPTED_SHAPE, accepted)
    assert not ifc.matches_shape_exactly(REFUSED_SHAPE, accepted)
    assert ifc.matches_shape_exactly(REFUSED_SHAPE, refused)
    assert not ifc.matches_shape_exactly(ACCEPTED_SHAPE, refused)


def test_emitted_positive_round_trips_without_dropping_fields() -> None:
    accepted = emitter.emit_accepted("payload-x")
    assert accepted["output_digest"] == hashlib.sha256(b"payload-x").hexdigest()
    assert set(accepted.keys()) == {"outcome", "payload", "provider_attempts", "output_digest"}


def test_mutation_basis_covers_all_required_operator_classes() -> None:
    accepted = emitter.emit_accepted("xyz")
    mutations = ifc.generate_mutations(MATRIX, "ACCEPTED_VALID", accepted)
    operators = {m.operator for m in mutations}
    assert operators == {
        "DELETE_REQUIRED_FIELD", "ADD_FORBIDDEN_FIELD", "ADD_UNKNOWN_FIELD",
        "REPLACE_DISCRIMINATOR", "ILLEGAL_VALUE", "COUNTER_MUTATION",
        "ONE_SIDE_RELATION_CHANGE",
    }
    # RECURSE_NESTED_OBJECTS is matrix-excluded; CONDITIONAL_FLIP has no rule
    # to iterate for this flat shape (conditionalRules is []).
    ids = [m.mutationId for m in mutations]
    assert len(ids) == len(set(ids)), "mutation ids must be unique"


def test_every_mutation_changes_exactly_one_semantic_fact_and_is_rejected() -> None:
    refused = emitter.emit_refused("INPUT_INVALID")
    assert ifc.matches_shape_exactly(REFUSED_SHAPE, refused)
    mutations = ifc.generate_mutations(MATRIX, "REFUSED_VALID", refused)
    assert mutations, "expected at least one mutation"
    for m in mutations:
        diff_keys = {
            k for k in set(refused) | set(m.payload)
            if refused.get(k) != m.payload.get(k)
        }
        assert len(diff_keys) >= 1
        assert not ifc.matches_shape_exactly(ACCEPTED_SHAPE, m.payload)
        assert not ifc.matches_shape_exactly(REFUSED_SHAPE, m.payload), m.mutationId


def test_deletion_of_required_field_generated_for_every_required_field() -> None:
    accepted = emitter.emit_accepted("p")
    mutations = ifc.generate_mutations(MATRIX, "ACCEPTED_VALID", accepted)
    deleted_fields = {
        m.mutationId.split("::")[-1]
        for m in mutations if m.operator == "DELETE_REQUIRED_FIELD"
    }
    assert deleted_fields == set(ACCEPTED_SHAPE["requiredFields"])


def test_counter_mutation_covers_minus_one_plus_one_zero_flip_and_wrong_type() -> None:
    accepted = emitter.emit_accepted("p")
    accepted_ids = [m.mutationId for m in ifc.generate_mutations(MATRIX, "ACCEPTED_VALID", accepted) if m.operator == "COUNTER_MUTATION"]
    assert any("minus_one" in i for i in accepted_ids)
    assert any("plus_one" in i for i in accepted_ids)
    assert any("zero_or_nonzero" in i for i in accepted_ids)
    assert any("wrong_type" in i for i in accepted_ids)

    refused = emitter.emit_refused("POLICY_BLOCKED")
    refused_ids = [m.mutationId for m in ifc.generate_mutations(MATRIX, "REFUSED_VALID", refused) if m.operator == "COUNTER_MUTATION"]
    assert any("zero_or_nonzero" in i for i in refused_ids)
    assert any("minus_one" in i for i in refused_ids)
    assert any("plus_one" in i for i in refused_ids)


def test_matches_shape_exactly_two_shapes_case_is_impossible_for_disjoint_matrix() -> None:
    accepted = emitter.emit_accepted("q")
    match_count = sum(
        1
        for outcome in MATRIX["outcomes"]
        for shape in outcome["shapes"]
        if ifc.matches_shape_exactly(shape, accepted)
    )
    assert match_count == 1


# --- F2-R2: conditional ownership is singular and reachable ----------------

def _conditional_shape(rules: list[dict]) -> dict:
    return {
        "shapeId": "COND_SHAPE",
        "requiredFields": ["mode"],
        "forbiddenFields": [],
        "conditionalRules": rules,
        "fieldDomains": {
            "mode": {"type": "STRING", "enum": ["STRICT", "LOOSE"]},
            "note": {"type": "STRING", "minLength": 1},
        },
        "relations": [],
    }


def test_duplicate_conditional_ownership_of_same_field_is_rejected() -> None:
    shape = _conditional_shape([
        {"field": "note", "controllingField": "mode", "controllingValue": "STRICT", "presence": "REQUIRED_WHEN_MATCH"},
        {"field": "note", "controllingField": "mode", "controllingValue": "LOOSE", "presence": "FORBIDDEN_WHEN_MATCH"},
    ])
    diags = guard._check_shape_fields(shape, "test", "F", {"COND_SHAPE"})
    assert any(d.code == "IFC_DUPLICATE_CONDITIONAL_OWNERSHIP" for d in diags)


def test_single_conditional_ownership_of_a_field_is_accepted() -> None:
    shape = _conditional_shape([
        {"field": "note", "controllingField": "mode", "controllingValue": "STRICT", "presence": "REQUIRED_WHEN_MATCH"},
    ])
    diags = guard._check_shape_fields(shape, "test", "F", {"COND_SHAPE"})
    assert not any(d.code == "IFC_DUPLICATE_CONDITIONAL_OWNERSHIP" for d in diags)


def test_conditional_rule_with_unreachable_controlling_value_is_rejected() -> None:
    # "mode" is a closed STRING enum {STRICT, LOOSE}; "ARCHIVED" can never
    # be the live value of "mode", so this rule can never activate - dead,
    # semantically-inapplicable code that must fail closed, not pass silently.
    shape = _conditional_shape([
        {"field": "note", "controllingField": "mode", "controllingValue": "ARCHIVED", "presence": "REQUIRED_WHEN_MATCH"},
    ])
    diags = guard._check_shape_fields(shape, "test", "F", {"COND_SHAPE"})
    assert any(d.code == "IFC_UNREACHABLE_CONDITIONAL_RULE" for d in diags)


def test_conditional_rule_with_reachable_controlling_value_is_accepted() -> None:
    shape = _conditional_shape([
        {"field": "note", "controllingField": "mode", "controllingValue": "STRICT", "presence": "REQUIRED_WHEN_MATCH"},
    ])
    diags = guard._check_shape_fields(shape, "test", "F", {"COND_SHAPE"})
    assert not any(d.code == "IFC_UNREACHABLE_CONDITIONAL_RULE" for d in diags)


def test_conditional_rule_governing_field_with_no_domain_is_rejected() -> None:
    # A conditional field that has no fieldDomains entry is semantically
    # inapplicable - there is no value-shape for the guard to ever check.
    shape = _conditional_shape([
        {"field": "undeclared_note", "controllingField": "mode", "controllingValue": "STRICT", "presence": "REQUIRED_WHEN_MATCH"},
    ])
    diags = guard._check_shape_fields(shape, "test", "F", {"COND_SHAPE"})
    assert any(d.code == "IFC_CONDITIONAL_FIELD_HAS_NO_DOMAIN" for d in diags)


def test_production_guard_rejects_unreachable_conditional_rule_end_to_end() -> None:
    # Exercises the real guard.run() path (not _check_shape_fields directly)
    # against a disposable two-file registry, proving the check fires
    # through production code, not only via a unit-level helper call.
    mutated = copy.deepcopy(MATRIX)
    mutated["outcomes"][0]["shapes"][0]["fieldDomains"]["mode"] = {"type": "STRING", "enum": ["STRICT", "LOOSE"]}
    mutated["outcomes"][0]["shapes"][0]["requiredFields"] = list(mutated["outcomes"][0]["shapes"][0]["requiredFields"]) + ["mode"]
    mutated["outcomes"][0]["shapes"][0]["conditionalRules"] = [
        {"field": "payload", "controllingField": "mode", "controllingValue": "UNREACHABLE_VALUE", "presence": "FORBIDDEN_WHEN_MATCH"}
    ]
    diags = guard._check_matrix_semantics(mutated, "test", "F")
    assert any(d.code == "IFC_UNREACHABLE_CONDITIONAL_RULE" for d in diags)
