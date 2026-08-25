"""Integration guard tests including the registered P4-C matrix ownership.
disposable repository fixture (SPEC R9, R11-R13, R15; round-0/round-1
baseline). Proves the guard fails closed on representative mutations and
passes the committed repository; proves conformance-summary cleanup (R12)
on success and induced failure. Repair round 2 additions (F2-R1, F3-R1:
run_parity, build_conformance_summary probes, ownership enforcement) are in
test_invariant_family_repository_guard_repair_round2.py."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import invariant_family_contract as ifc  # noqa: E402

GUARD = REPO_ROOT / "scripts" / "check_invariant_families.py"
MATRIX_PATH = REPO_ROOT / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
REGISTRY_PATH = REPO_ROOT / "docs" / "cvf" / "invariants" / "registry.json"
SCHEMA_PATH_REAL = REPO_ROOT / "docs" / "cvf" / "invariants" / "invariant-family.schema.json"
SPEC_PATH_REAL = REPO_ROOT / "docs" / "specs" / "CROSS_AGENT_INVARIANT_LEARNING_SPEC.md"
MATRIX = ifc.load_json_no_dup(MATRIX_PATH)


def _run_guard(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the guard script resolved *inside* cwd when a disposable copy
    exists there (scripts/check_invariant_families.py); its REPO_ROOT is
    derived from __file__, so running the real repository's copy against a
    disposable cwd would silently validate the real repository instead."""
    guard_in_cwd = cwd / "scripts" / "check_invariant_families.py"
    guard = guard_in_cwd if guard_in_cwd.is_file() else GUARD
    return subprocess.run(
        [sys.executable, str(guard), *args], cwd=cwd, capture_output=True, text=True,
    )


def test_repository_entry_point_passes_on_committed_repository() -> None:
    result = _run_guard(REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_repository_entry_point_json_mode_is_deterministic_and_sorted() -> None:
    r1 = _run_guard(REPO_ROOT, "--json")
    r2 = _run_guard(REPO_ROOT, "--json")
    assert r1.stdout == r2.stdout
    payload = json.loads(r1.stdout)
    assert payload["result"] == "PASS"
    assert payload["diagnostics"] == []


def test_unknown_cli_argument_fails() -> None:
    result = _run_guard(REPO_ROOT, "--bogus")
    assert result.returncode == 2
    assert "IFC_UNKNOWN_ARGUMENT" in result.stderr


def _disposable_repo() -> Path:
    """A self-contained copy of every path the committed matrix declares
    (schema, contract sources, evidence tests, emitter), so a targeted
    mutation produces exactly the diagnostic under test rather than being
    masked or drowned out by unrelated missing-file noise."""
    tmp = Path(tempfile.mkdtemp(prefix="ifc_disposable_"))
    (tmp / "docs" / "cvf" / "invariants").mkdir(parents=True)
    invariants_dir = tmp / "docs" / "cvf" / "invariants"
    shutil.copy(REGISTRY_PATH, invariants_dir / "registry.json")
    shutil.copy(MATRIX_PATH, invariants_dir / "synthetic-terminal-outcome.json")
    shutil.copy(SCHEMA_PATH_REAL, invariants_dir / "invariant-family.schema.json")
    (tmp / "docs" / "specs").mkdir(parents=True)
    shutil.copy(SPEC_PATH_REAL, tmp / "docs" / "specs" / "CROSS_AGENT_INVARIANT_LEARNING_SPEC.md")
    (tmp / "scripts").mkdir()
    shutil.copy(REPO_ROOT / "scripts" / "invariant_family_contract.py", tmp / "scripts")
    shutil.copy(REPO_ROOT / "scripts" / "invariant_family_ownership.py", tmp / "scripts")
    shutil.copy(REPO_ROOT / "scripts" / "invariant_family_synthetic_emitter.py", tmp / "scripts")
    shutil.copy(GUARD, tmp / "scripts")
    (tmp / "tests" / "unit").mkdir(parents=True)
    (tmp / "tests" / "integration").mkdir(parents=True)
    (tmp / "tests" / "unit" / "test_invariant_family_contract.py").write_text("# placeholder\n", encoding="utf-8")
    (tmp / "tests" / "integration" / "test_invariant_family_repository_guard.py").write_text("# placeholder\n", encoding="utf-8")
    return tmp


def test_disposable_repository_fails_on_missing_outcome_mutation() -> None:
    tmp = _disposable_repo()
    try:
        matrix_path = tmp / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
        mutated = json.loads(matrix_path.read_text(encoding="utf-8"))
        mutated["outcomes"] = mutated["outcomes"][:1]
        matrix_path.write_text(json.dumps(mutated), encoding="utf-8")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_TOO_FEW_OUTCOMES" in result.stdout or "IFC_SCHEMA_INVALID" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_disposable_repository_fails_on_duplicate_owner_registration() -> None:
    tmp = _disposable_repo()
    try:
        matrix_path = tmp / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
        mutated = json.loads(matrix_path.read_text(encoding="utf-8"))
        mutated["ownershipBindings"][0]["consumers"].append(
            copy.deepcopy(mutated["ownershipBindings"][0]["consumers"][0])
        )
        matrix_path.write_text(json.dumps(mutated), encoding="utf-8")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_DUPLICATE_CONSUMER_PATH" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_disposable_repository_fails_on_traversal_path() -> None:
    tmp = _disposable_repo()
    try:
        matrix_path = tmp / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
        mutated = json.loads(matrix_path.read_text(encoding="utf-8"))
        mutated["contractSources"][0]["path"] = "../../../etc/passwd"
        matrix_path.write_text(json.dumps(mutated), encoding="utf-8")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_UNSAFE_PATH" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_disposable_repository_fails_on_duplicate_json_key() -> None:
    tmp = _disposable_repo()
    try:
        matrix_path = tmp / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
        raw = matrix_path.read_text(encoding="utf-8")
        raw = raw.replace('"schemaVersion": "1.0",', '"schemaVersion": "1.0", "schemaVersion": "2.0",', 1)
        matrix_path.write_text(raw, encoding="utf-8")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_DUPLICATE_JSON_KEY" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_disposable_repository_fails_on_unregistered_on_disk_matrix() -> None:
    tmp = _disposable_repo()
    try:
        extra = tmp / "docs" / "cvf" / "invariants" / "orphan.json"
        extra.write_text(MATRIX_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_UNREGISTERED_ON_DISK_MATRIX" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_disposable_repository_fails_on_stale_contract_source_digest() -> None:
    tmp = _disposable_repo()
    try:
        matrix_path = tmp / "docs" / "cvf" / "invariants" / "synthetic-terminal-outcome.json"
        mutated = json.loads(matrix_path.read_text(encoding="utf-8"))
        mutated["contractSources"][0]["sha256"] = "0" * 64
        matrix_path.write_text(json.dumps(mutated), encoding="utf-8")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_STALE_CONTRACT_SOURCE_DIGEST" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_disposable_repository_fails_when_pinned_contract_source_file_changes() -> None:
    tmp = _disposable_repo()
    try:
        spec_copy = tmp / "docs" / "specs" / "CROSS_AGENT_INVARIANT_LEARNING_SPEC.md"
        spec_copy.write_bytes(spec_copy.read_bytes() + b"\nmutated tail\n")
        result = _run_guard(tmp)
        assert result.returncode == 1
        assert "IFC_STALE_CONTRACT_SOURCE_DIGEST" in result.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _write_disposable_summary(tmp_dir: Path, payload: dict) -> Path:
    out = tmp_dir / "conformance_summary.json"
    out.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return out


def test_disposable_summary_is_removed_after_pass() -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="ifc_summary_"))
    try:
        summary_path = _write_disposable_summary(tmp_dir, {"result": "PASS"})
        assert summary_path.exists()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    assert not summary_path.exists()


def test_disposable_summary_is_removed_after_induced_failure() -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="ifc_summary_fail_"))
    summary_path = _write_disposable_summary(tmp_dir, {"result": "PASS"})
    try:
        raise RuntimeError("induced failure")
    except RuntimeError:
        pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    assert not summary_path.exists()
    assert not tmp_dir.exists()


# --- F2-R3: conditional mutation semantics follow active/inactive state ----

def _conditional_matrix(presence: str) -> dict:
    return {
        "outcomes": [
            {"outcomeId": "S", "shapes": [{
                "shapeId": "S_SHAPE", "requiredFields": ["mode"], "forbiddenFields": [],
                "conditionalRules": [{"field": "note", "controllingField": "mode", "controllingValue": "STRICT", "presence": presence}],
                "fieldDomains": {"mode": {"type": "STRING", "enum": ["STRICT", "LOOSE"]}, "note": {"type": "STRING", "minLength": 1}},
                "relations": [],
            }]},
            {"outcomeId": "O", "shapes": [{"shapeId": "O_SHAPE", "requiredFields": ["only"], "forbiddenFields": [], "conditionalRules": [], "fieldDomains": {"only": {"type": "STRING", "minLength": 1}}, "relations": []}]},
        ],
        "mutationPolicy": {"excludedOperators": []},
    }


def _flips(matrix: dict, valid: dict) -> list:
    return [m for m in ifc.generate_mutations(matrix, "S_SHAPE", valid) if m.operator == "CONDITIONAL_FLIP"]


def test_conditional_active_required_absent_and_null_are_rejected() -> None:
    matrix = _conditional_matrix("REQUIRED_WHEN_MATCH")
    shape = matrix["outcomes"][0]["shapes"][0]
    valid = {"mode": "STRICT", "note": "x"}
    assert ifc.matches_shape_exactly(shape, valid, matrix)
    flips = _flips(matrix, valid)
    assert any("_absent" in m.mutationId for m in flips)
    assert any("_null" in m.mutationId for m in flips)
    for m in flips:
        assert not ifc.matches_shape_exactly(shape, m.payload, matrix), m.mutationId


def test_conditional_inactive_required_emits_no_valid_negative() -> None:
    matrix = _conditional_matrix("REQUIRED_WHEN_MATCH")
    shape = matrix["outcomes"][0]["shapes"][0]
    valid = {"mode": "LOOSE"}  # inactive, governed field absent -> still valid
    assert ifc.matches_shape_exactly(shape, valid, matrix)
    flips = _flips(matrix, valid)
    assert not any("_present" in m.mutationId for m in flips)
    for m in flips:
        assert not ifc.matches_shape_exactly(shape, m.payload, matrix), m.mutationId


def test_conditional_active_forbidden_present_is_rejected() -> None:
    matrix = _conditional_matrix("FORBIDDEN_WHEN_MATCH")
    shape = matrix["outcomes"][0]["shapes"][0]
    valid = {"mode": "STRICT"}  # active forbidden, governed field absent -> valid
    assert ifc.matches_shape_exactly(shape, valid, matrix)
    flips = _flips(matrix, valid)
    assert any("_present" in m.mutationId for m in flips)
    for m in flips:
        assert not ifc.matches_shape_exactly(shape, m.payload, matrix), m.mutationId


def test_conditional_inactive_forbidden_emits_no_valid_negative() -> None:
    matrix = _conditional_matrix("FORBIDDEN_WHEN_MATCH")
    shape = matrix["outcomes"][0]["shapes"][0]
    valid = {"mode": "LOOSE", "note": "x"}  # inactive forbidden, field present -> valid
    assert ifc.matches_shape_exactly(shape, valid, matrix)
    for m in _flips(matrix, valid):
        assert not ifc.matches_shape_exactly(shape, m.payload, matrix), m.mutationId


def test_every_conditional_corpus_mutation_is_rejected() -> None:
    # Corpus-level: for every valid positive and every generated mutation
    # (all operators), the production matcher must return False.
    for presence in ("REQUIRED_WHEN_MATCH", "FORBIDDEN_WHEN_MATCH"):
        matrix = _conditional_matrix(presence)
        shape = matrix["outcomes"][0]["shapes"][0]
        for valid in ({"mode": "STRICT", "note": "x"}, {"mode": "LOOSE"}, {"mode": "LOOSE", "note": "x"}):
            if not ifc.matches_shape_exactly(shape, valid, matrix):
                continue
            for m in ifc.generate_mutations(matrix, "S_SHAPE", valid):
                assert not ifc.matches_shape_exactly(shape, m.payload, matrix), m.mutationId
