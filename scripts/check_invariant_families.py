#!/usr/bin/env python3
"""Deterministic repository guard (SPEC R13): CLI over invariant_family_contract.py and invariant_family_ownership.py. No provider/network/install/database/credential/dynamic-import. Usage: check_invariant_families.py [--json]"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from invariant_family_contract import (  # noqa: E402
    REPO_ROOT, Diagnostic, DuplicateKey, canonical_digest, generate_mutations,
    is_safe_regular_file, load_json_no_dup, matches_shape_exactly, safe_repo_path,
)
from invariant_family_ownership import check_ownership_bindings, required_mutation_ids  # noqa: E402

REGISTRY_PATH = REPO_ROOT / "docs" / "cvf" / "invariants" / "registry.json"
SCHEMA_PATH = REPO_ROOT / "docs" / "cvf" / "invariants" / "invariant-family.schema.json"

def _diag(code: str, path: str, family_id: str, message: str) -> Diagnostic:
    return Diagnostic(code=code, path=path, familyId=family_id, message=message)

# Closed schema validation (SPEC R3/R4) — sanitized: never emits raw values.

def _wrap_defs_schema(full_schema: dict[str, Any], defs_key: str) -> dict[str, Any]:
    # #/$defs/* refs resolve against the full document only as full-document root.
    return {**full_schema, **full_schema["$defs"][defs_key]}

def validate_against_schema(instance: Any, defs_key: str | None = None) -> list[str]:
    full_schema = load_json_no_dup(SCHEMA_PATH)
    schema = full_schema if defs_key is None else _wrap_defs_schema(full_schema, defs_key)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(instance),
        key=lambda e: list(e.absolute_path),
    )
    return [_sanitize_schema_error(e) for e in errors]

def _sanitize_schema_error(error: Any) -> str:
    # Stable location + validator-keyword code only, never raw instance/schema.
    location = "/".join(str(p) for p in error.absolute_path) or "<root>"
    return f"{location}:{error.validator}"

# Matrix semantic checks (SPEC R6, R7, R14); ownership (R11) is in invariant_family_ownership.py.

_DOMAIN_TYPE_PYTHON_TYPES = {"STRING": str, "BOOLEAN": bool, "INTEGER": int, "NUMBER": (int, float)}

def _conditional_value_is_reachable(rule: dict[str, Any], controlling_domain: dict[str, Any] | None) -> bool:
    # F2-R2: an unreachable controllingValue is dead/inapplicable, fail closed.
    if controlling_domain is None:
        return True  # no declared domain to check reachability against
    value = rule.get("controllingValue")
    if "const" in controlling_domain:
        return value == controlling_domain["const"]
    if "enum" in controlling_domain:
        return value in controlling_domain["enum"]
    expected_type = _DOMAIN_TYPE_PYTHON_TYPES.get(controlling_domain.get("type"))
    if expected_type is None:
        return True
    if expected_type is bool:
        return isinstance(value, bool)
    return isinstance(value, expected_type) and not isinstance(value, bool)

def _check_shape_fields(shape: dict[str, Any], matrix_rel: str, family_id: str, all_shape_ids: set[str]) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    sid = shape.get("shapeId")
    required = set(shape.get("requiredFields", []))
    forbidden = set(shape.get("forbiddenFields", []))
    field_domains = shape.get("fieldDomains", {})
    conditional_fields = {r.get("field") for r in shape.get("conditionalRules", [])}
    if required & forbidden:
        diags.append(_diag("IFC_REQUIRED_FORBIDDEN_OVERLAP", matrix_rel, family_id, sid))
    if conditional_fields & (required | forbidden):
        diags.append(_diag("IFC_CONDITIONAL_FIELD_OVERLAP", matrix_rel, family_id, sid))
    known = required | forbidden | conditional_fields
    for f, domain in field_domains.items():
        if f not in known:
            diags.append(_diag("IFC_UNKNOWN_RELATION_FIELD", matrix_rel, family_id, f))
        if domain.get("type") == "NESTED_OBJECT" and domain.get("nestedShapeId") not in all_shape_ids:
            diags.append(_diag("IFC_UNKNOWN_NESTED_SHAPE_TARGET", matrix_rel, family_id, str(domain.get("nestedShapeId"))))
    seen_conditional_fields: set[str] = set()
    for rule in shape.get("conditionalRules", []):
        controlling = rule.get("controllingField")
        governed = rule.get("field")
        if controlling not in known and controlling not in field_domains:
            diags.append(_diag("IFC_UNKNOWN_CONDITIONAL_CONTROLLING_FIELD", matrix_rel, family_id, str(controlling)))
        if governed in seen_conditional_fields:
            diags.append(_diag("IFC_DUPLICATE_CONDITIONAL_OWNERSHIP", matrix_rel, family_id, str(governed)))
        seen_conditional_fields.add(governed)
        if governed not in field_domains:
            diags.append(_diag("IFC_CONDITIONAL_FIELD_HAS_NO_DOMAIN", matrix_rel, family_id, str(governed)))
        if not _conditional_value_is_reachable(rule, field_domains.get(controlling)):
            diags.append(_diag("IFC_UNREACHABLE_CONDITIONAL_RULE", matrix_rel, family_id, str(governed)))
    rel_ids: set[str] = set()
    for rel in shape.get("relations", []):
        rid = rel.get("relationId")
        if rid in rel_ids:
            diags.append(_diag("IFC_DUPLICATE_RELATION_ID", matrix_rel, family_id, rid))
        rel_ids.add(rid)
        for key in ("sourceField", "targetField", "field"):
            operand = rel.get(key)
            if operand is not None and operand not in known:
                diags.append(_diag("IFC_UNKNOWN_RELATION_OPERAND", matrix_rel, family_id, operand))
    return diags

def _check_matrix_semantics(matrix: dict[str, Any], matrix_rel: str, family_id: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    outcome_ids: set[str] = set()
    shape_ids: set[str] = set()
    all_shape_ids = {s.get("shapeId") for o in matrix.get("outcomes", []) for s in o.get("shapes", [])}
    for outcome in matrix.get("outcomes", []):
        oid = outcome.get("outcomeId")
        if oid in outcome_ids:
            diags.append(_diag("IFC_DUPLICATE_OUTCOME_ID", matrix_rel, family_id, oid))
        outcome_ids.add(oid)
        for shape in outcome.get("shapes", []):
            sid = shape.get("shapeId")
            if sid in shape_ids:
                diags.append(_diag("IFC_DUPLICATE_SHAPE_ID", matrix_rel, family_id, sid))
            shape_ids.add(sid)
            diags.extend(_check_shape_fields(shape, matrix_rel, family_id, all_shape_ids))
    if len(matrix.get("outcomes", [])) < 2:
        diags.append(_diag("IFC_TOO_FEW_OUTCOMES", matrix_rel, family_id, "matrix"))
    seen_source_paths: set[str] = set()
    for src in matrix.get("contractSources", []):
        spath = src.get("path", "")
        if spath in seen_source_paths:
            diags.append(_diag("IFC_DUPLICATE_CONTRACT_SOURCE_PATH", matrix_rel, family_id, spath))
        seen_source_paths.add(spath)
        resolved = safe_repo_path(spath)
        if resolved is None or not is_safe_regular_file(resolved):
            diags.append(_diag("IFC_UNSAFE_PATH", matrix_rel, family_id, str(spath)))
        elif canonical_digest(resolved) != src.get("sha256"):
            diags.append(_diag("IFC_STALE_CONTRACT_SOURCE_DIGEST", matrix_rel, family_id, spath))
    for test_path in matrix.get("evidenceTestPaths", []):
        resolved = safe_repo_path(test_path)
        if resolved is None or not is_safe_regular_file(resolved):
            diags.append(_diag("IFC_MISSING_EVIDENCE_TEST", matrix_rel, family_id, test_path))
    diags.extend(check_ownership_bindings(matrix, matrix_rel, family_id))
    return diags

_REGISTRY_MATRIX_AGREEMENT_FIELDS = (("ownerRole", "OWNER"), ("risk", "RISK"), ("lifecycle", "LIFECYCLE"))

def _check_matrix(entry: dict[str, Any], matrix: dict[str, Any], mpath: str, fid: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    if matrix.get("familyId") != fid:
        diags.append(_diag("IFC_REGISTRY_MATRIX_ID_MISMATCH", mpath, fid, str(matrix.get("familyId"))))
    for field, tag in _REGISTRY_MATRIX_AGREEMENT_FIELDS:
        if matrix.get(field) != entry.get(field):
            diags.append(_diag(f"IFC_REGISTRY_MATRIX_{tag}_MISMATCH", mpath, fid, field))
    if entry.get("lifecycle") == "WAIVED_LEGACY":
        waiver = matrix.get("waiver") or {}
        missing = [f for f in ("familyId", "owner", "missingObligation", "reason", "approvalArtifact", "expiryOrRemovalTrigger") if not waiver.get(f)]
        if missing:
            diags.append(_diag("IFC_INCOMPLETE_WAIVER", mpath, fid, ",".join(missing)))
    elif "waiver" in matrix:
        diags.append(_diag("IFC_WAIVER_ON_ACTIVE_LIFECYCLE", mpath, fid, "waiver"))
    diags.extend(_diag(f"IFC_SCHEMA_{c}", mpath, fid, "") for c in validate_against_schema(matrix))
    diags.extend(_check_matrix_semantics(matrix, mpath, fid))
    return diags

def run() -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    registry_rel = "docs/cvf/invariants/registry.json"
    try:
        registry = load_json_no_dup(REGISTRY_PATH)
    except DuplicateKey:
        return [_diag("IFC_DUPLICATE_JSON_KEY", registry_rel, "REGISTRY", "")]
    diags.extend(_diag(f"IFC_REGISTRY_SCHEMA_{c}", registry_rel, "REGISTRY", "") for c in validate_against_schema(registry, "registry"))
    families = registry.get("families", []) if isinstance(registry, dict) else []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for entry in families:
        if not isinstance(entry, dict):
            continue
        fid = entry.get("familyId")
        mpath = entry.get("matrixPath")
        if fid in seen_ids:
            diags.append(_diag("IFC_DUPLICATE_FAMILY_ID", registry_rel, fid, fid))
        seen_ids.add(fid)
        if mpath in seen_paths:
            diags.append(_diag("IFC_DUPLICATE_MATRIX_PATH", registry_rel, fid, mpath))
        seen_paths.add(mpath)
        resolved = safe_repo_path(mpath) if isinstance(mpath, str) else None
        if resolved is None or not is_safe_regular_file(resolved):
            diags.append(_diag("IFC_UNREGISTERED_OR_MISSING_MATRIX", mpath or "?", fid, "matrix path missing/unsafe"))
            continue
        try:
            matrix = load_json_no_dup(resolved)
        except DuplicateKey:
            diags.append(_diag("IFC_DUPLICATE_JSON_KEY", mpath, fid, ""))
            continue
        diags.extend(_check_matrix(entry, matrix, mpath, fid))
    matrices_dir = REPO_ROOT / "docs" / "cvf" / "invariants"
    non_matrix_names = {"registry.json", SCHEMA_PATH.name}
    if matrices_dir.is_dir():
        for candidate in sorted(matrices_dir.glob("*.json")):
            if candidate.name in non_matrix_names:
                continue
            rel = candidate.relative_to(REPO_ROOT).as_posix()
            if rel not in seen_paths:
                diags.append(_diag("IFC_UNREGISTERED_ON_DISK_MATRIX", rel, "?", rel))
    return diags

# Conformance-summary mechanics (SPEC R12): judges each surface against the
# case's EXPECTED disposition, not mere inter-surface agreement.

def _judge_case(
    surfaces: dict[str, Any], shape: dict[str, Any], instance: dict[str, Any], expected: bool,
) -> dict[str, Any]:
    per_validator = {name: bool(surface(shape, instance)) for name, surface in surfaces.items()}
    all_correct = all(result == expected for result in per_validator.values())
    return {"perValidator": per_validator, "expected": expected, "allCorrect": all_correct}

def build_conformance_summary(
    matrix: dict[str, Any],
    matrix_canonical_digest: str,
    matrix_rel: str,
    emit: Any,
    surfaces: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # Every surface is judged against the case's EXPECTED disposition, not
    # mere inter-surface agreement. Ownership is always computed here from
    # production check_ownership_bindings (F3-R2) - never a caller-supplied
    # boolean, which could default a broken binding to PASS.
    surfaces = surfaces or {"python_contract": lambda s, i: matches_shape_exactly(s, i, matrix)}
    ownership_ok = not check_ownership_bindings(matrix, matrix_rel, matrix.get("familyId", "?"))
    outcomes: list[dict[str, Any]] = []
    overall_pass = True
    for outcome in matrix["outcomes"]:
        for shape in outcome["shapes"]:
            positive = emit(outcome["outcomeId"])
            bound_to_intended_shape = matches_shape_exactly(shape, positive, matrix)
            match_count = sum(
                1 for o2 in matrix["outcomes"] for s2 in o2["shapes"]
                if matches_shape_exactly(s2, positive, matrix)
            )
            positive_ok = bound_to_intended_shape and match_count == 1
            positive_judgement = _judge_case(surfaces, shape, positive, expected=True)
            mutations = generate_mutations(matrix, shape["shapeId"], positive)
            generated_ids = [m.mutationId for m in mutations]
            required_ids = required_mutation_ids(matrix, shape["shapeId"], positive)
            corpus_complete = bool(mutations) and len(set(generated_ids)) == len(generated_ids) and set(generated_ids) == required_ids
            mutation_results = []
            all_mutations_correct = True
            operator_counts: dict[str, int] = {}
            for m in mutations:
                operator_counts[m.operator] = operator_counts.get(m.operator, 0) + 1
                judgement = _judge_case(surfaces, shape, m.payload, expected=False)
                all_mutations_correct = all_mutations_correct and judgement["allCorrect"]
                mutation_results.append({
                    "mutationId": m.mutationId, "operator": m.operator,
                    "perValidator": judgement["perValidator"], "allCorrect": judgement["allCorrect"],
                })
            parity_ok = len(surfaces) < 2 or (positive_judgement["allCorrect"] and all_mutations_correct)
            shape_pass = positive_ok and positive_judgement["allCorrect"] and corpus_complete and all_mutations_correct and parity_ok
            overall_pass = overall_pass and shape_pass
            outcomes.append({
                "outcomeId": outcome["outcomeId"], "shapeId": shape["shapeId"],
                "positiveBoundToIntendedShape": bound_to_intended_shape,
                "positiveMatchedExactlyOne": positive_ok,
                "positivePerValidator": positive_judgement["perValidator"],
                "mutationCorpusComplete": corpus_complete,
                "mutationCount": len(mutations),
                "requiredMutationIdCount": len(required_ids),
                "mutationCountByOperator": dict(sorted(operator_counts.items())),
                "mutations": sorted(mutation_results, key=lambda r: r["mutationId"]),
                "parityOk": parity_ok,
                "shapePass": shape_pass,
            })
    overall_pass = overall_pass and ownership_ok
    return {
        "familyId": matrix["familyId"],
        "matrixCanonicalDigest": matrix_canonical_digest,
        "parityMode": matrix.get("parityMode"),
        "validatorSurfaces": sorted(surfaces.keys()),
        "ownershipResult": "PASS" if ownership_ok else "FAIL",
        "outcomes": sorted(outcomes, key=lambda o: (o["outcomeId"], o["shapeId"])),
        "result": "PASS" if overall_pass else "FAIL",
    }

def main(argv: list[str]) -> int:
    if len(argv) > 1 or (argv and argv[0] != "--json"):
        print("IFC_UNKNOWN_ARGUMENT: usage: check_invariant_families.py [--json]", file=sys.stderr)
        return 2
    ordered = sorted(run(), key=lambda d: (d.code, d.path, d.familyId))
    if argv:
        payload = {"result": "FAIL" if ordered else "PASS", "diagnostics": [{"code": d.code, "path": d.path, "familyId": d.familyId, "message": d.message} for d in ordered]}
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    elif ordered:
        for d in ordered:
            print(f"{d.code}\t{d.path}\t{d.familyId}\t{d.message}")
    else:
        print("INVARIANT FAMILY CHECK: PASS")
    return 1 if ordered else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
