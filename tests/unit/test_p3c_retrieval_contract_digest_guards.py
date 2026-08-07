from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from retrieval_contracts.constructor import construct_retrieval_contract
from test_p3c_retrieval_contract_constructor import make_input

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages" / "retrieval-contracts" / "src" / "retrieval_contracts"


def golden_bytes(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def test_content_chunk_and_revalidation_digests_recompute_independently() -> None:
    result = construct_retrieval_contract(make_input())
    content = hashlib.sha256(result.redacted_normalized_text.encode("utf-8")).hexdigest()
    assert content == result.content_digest_sha256
    lifecycle = result.lifecycle.model_dump(
        mode="json", exclude={"revalidation_token"}
    )
    chunk_preimage = {
        "contract_version": result.contract_version,
        "truth_class": result.truth_class.value,
        "source_reference": result.source_reference.model_dump(mode="json"),
        "field_selector": result.field_selector,
        "candidate_fingerprint": result.provenance.candidate_fingerprint.model_dump(
            mode="json"
        ),
        "scope": result.scope.model_dump(mode="json"),
        "lifecycle": lifecycle,
        "content_digest_sha256": result.content_digest_sha256,
    }
    assert hashlib.sha256(golden_bytes(chunk_preimage)).hexdigest() == result.chunk_id
    token_preimage = {
        "chunk_id": result.chunk_id,
        "source_digest": result.source_reference.source_digest_sha256,
        "source_version": result.source_reference.version.model_dump(mode="json"),
        "source_lifecycle": result.lifecycle.source_status,
        "parent_shift_id": result.lifecycle.parent_shift_id,
        "parent_shift_version": result.lifecycle.parent_shift_version,
        "parent_shift_status": result.lifecycle.parent_shift_status,
        "report_status": result.lifecycle.report_status,
        "report_snapshot_digest": result.lifecycle.report_snapshot_digest,
        "correction_lineage": None,
        "retention_disposition": result.retention.disposition.value,
        "retention_owner_id": result.retention.owner_id,
        "retention_policy_version": result.retention.policy_version,
        "retention_evidence_id": result.retention.source_evidence_id,
    }
    expected = hashlib.sha256(golden_bytes(token_preimage)).hexdigest()
    assert expected == result.lifecycle.revalidation_token

    stale = dict(token_preimage, source_lifecycle="STALE")
    assert hashlib.sha256(golden_bytes(stale)).hexdigest() != expected


def test_advisory_source_digest_matches_source_owner_bytes() -> None:
    item = make_input()
    result = construct_retrieval_contract(item)
    owned = hashlib.sha256(item.source.text.encode("utf-8")).hexdigest()
    assert owned == item.envelope.source_fingerprint.sha256
    assert owned == result.source_reference.source_digest_sha256


def test_dependency_graph_and_private_helpers_are_fail_closed() -> None:
    forbidden_roots = {
        "workspace_api", "operations_ledger", "cvf_runtime", "fastapi", "sqlalchemy",
        "requests", "httpx", "socket", "os", "pathlib", "subprocess", "random",
        "secrets", "time",
    }
    private_names = {"_canonical_bytes", "_recompute_record_digest"}
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not ({alias.name.split(".")[0] for alias in node.names} & forbidden_roots)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_roots
                assert not ({alias.name for alias in node.names} & private_names)
            if isinstance(node, ast.Attribute):
                assert node.attr not in private_names
            if isinstance(node, ast.Name):
                assert node.id not in private_names


def test_no_generic_source_model_dump_digest_substitution() -> None:
    constructor = (PACKAGE / "constructor.py").read_text(encoding="utf-8")
    tree = ast.parse(constructor)
    canonical_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "canonical_sha256"
    ]
    assert len(canonical_calls) == 2
    assert "source.model_dump" not in constructor


def test_reverse_dependencies_do_not_import_retrieval_contracts() -> None:
    for relative in ("packages/refinery-bridge/src", "packages/operations-domain/src"):
        for path in (ROOT / relative).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            assert not any(name == "retrieval_contracts" or name.startswith("retrieval_contracts.") for name in imports)


def test_package_contains_no_io_calls() -> None:
    forbidden_calls = {"open", "exec", "eval", "compile", "__import__", "getenv", "system"}
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        called = {
            node.func.id for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not (called & forbidden_calls)
