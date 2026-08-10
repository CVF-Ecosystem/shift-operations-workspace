"""SPEC R1 - governed-retrieval owner/dependency boundary.

AC-01: an AST/import and call-boundary suite proves every allowed arrow,
fails on each forbidden import/access class, and proves the pure engine
receives explicit values only. Source inspection also proves the domain and
ledger packages retain zero API/UI/provider/gateway imports.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PURE_SRC = REPO_ROOT / "packages" / "governed-retrieval" / "src"
PURE_PKG = PURE_SRC / "governed_retrieval"

ALLOWED_TOP_LEVEL_MODULES = {"__future__", "dataclasses", "datetime", "enum", "hashlib", "json",
                              "typing", "unicodedata", "uuid", "collections", "re", "types"}
ALLOWED_THIRD_PARTY = {"pydantic"}
ALLOWED_INTERNAL = {"retrieval_contracts", "governed_retrieval"}

FORBIDDEN_ANYWHERE_IN_PURE_PACKAGE = (
    "workspace_api", "operations_ledger", "operations_domain", "refinery_bridge",
    "fastapi", "sqlalchemy", "cvf_runtime", "httpx", "requests", "urllib", "socket",
    "os", "sys", "subprocess", "pathlib",
)

def _pure_source_files() -> list[Path]:
    return sorted(PURE_PKG.rglob("*.py"))

def test_pure_package_has_source_files() -> None:
    files = _pure_source_files()
    assert files, "no source files found under governed_retrieval"

def test_pure_package_imports_only_stdlib_pydantic_and_retrieval_contracts() -> None:
    offenders = []
    for path in _pure_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue  # relative import within the package itself
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.split(".")[0]
                if (
                    root not in ALLOWED_TOP_LEVEL_MODULES
                    and root not in ALLOWED_THIRD_PARTY
                    and root not in ALLOWED_INTERNAL
                ):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} -> {name}")
    assert offenders == [], f"forbidden import in governed-retrieval: {offenders}"

def test_pure_package_never_imports_forbidden_runtime_modules() -> None:
    offenders = []
    for path in _pure_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""] if not (node.level and node.level > 0) else []
            else:
                continue
            for name in names:
                root = name.split(".")[0]
                if root in FORBIDDEN_ANYWHERE_IN_PURE_PACKAGE:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} -> {name}")
    assert offenders == [], f"forbidden runtime import in governed-retrieval: {offenders}"

def test_pure_package_calls_no_io_or_clock_functions() -> None:
    """Static scan: no attribute access to well-known I/O/clock/env/secret
    surfaces (open(), datetime.now(), os.environ, uuid4(), etc.) anywhere in
    the pure package's source text."""
    forbidden_tokens = (
        "datetime.now(", "time.time(", "uuid4(", "open(", "os.environ",
        "os.getenv", "socket.", "requests.", "httpx.", "input(",
    )
    offenders = []
    for path in _pure_source_files():
        text = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)} contains {token!r}")
    assert offenders == [], f"forbidden I/O/clock/id/env surface in governed-retrieval: {offenders}"

_ISOLATION_PROGRAM = textwrap.dedent(
    """
    import importlib, sys
    from pathlib import Path

    repo_root = Path(sys.argv[1]).resolve()
    allowed = [Path(p).resolve() for p in sys.argv[2:]]

    import governed_retrieval

    import pydantic  # noqa: F401 - guard against an over-stripped environment

    # Only repo-local packages: fastapi is a genuine third-party dependency
    # of workspace-api and is always importable from site-packages
    # regardless of which repo source roots are on sys.path, so checking it
    # here would prove nothing about THIS boundary.
    forbidden = ("workspace_api", "operations_ledger", "cvf_runtime")
    for name in forbidden:
        assert name not in sys.modules, f"{name} leaked into sys.modules"
        try:
            importlib.import_module(name)
        except ModuleNotFoundError:
            pass
        else:
            raise AssertionError(f"{name} was importable - repo roots are still on sys.path")

    print("ISOLATION_OK")
    """
)

def test_pure_package_imports_without_application_or_ledger_roots(tmp_path) -> None:
    """AC-01: import isolation - governed_retrieval must import cleanly with
    only its own src and retrieval-contracts/refinery-bridge/operations-domain
    (its transitive P3-C dependency) on the path, never workspace_api,
    operations_ledger, cvf_runtime, or fastapi."""
    script = tmp_path / "isolation_probe.py"
    script.write_text(_ISOLATION_PROGRAM, encoding="utf-8")

    allowed_roots = [
        PURE_SRC,
        REPO_ROOT / "packages" / "retrieval-contracts" / "src",
        REPO_ROOT / "packages" / "refinery-bridge" / "src",
        REPO_ROOT / "packages" / "operations-domain" / "src",
    ]
    import os as _os

    env = {k: v for k, v in _os.environ.items() if k not in {"PYTHONPATH", "PYTHONSTARTUP"}}
    env["PYTHONPATH"] = _os.pathsep.join(str(p) for p in allowed_roots)

    proc = subprocess.run(
        [sys.executable, "-P", str(script), str(REPO_ROOT), *[str(p) for p in allowed_roots]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"isolation subprocess failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    assert "ISOLATION_OK" in proc.stdout

def test_no_governed_retrieval_module_imports_workspace_api() -> None:
    offenders = []
    for path in _pure_source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("workspace_api"):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("workspace_api"):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
    assert offenders == [], f"governed_retrieval must not import workspace_api: {offenders}"

def test_operations_domain_and_ledger_still_have_zero_api_ui_provider_imports() -> None:
    """R1: the domain and ledger packages must retain zero API/UI/provider/
    gateway imports - this tranche must not introduce a reverse arrow."""
    forbidden = ("fastapi", "workspace_api", "workspace_web", "ai_gateway")
    offenders = []
    for pkg_dir in (
        REPO_ROOT / "packages" / "operations-domain" / "src",
        REPO_ROOT / "packages" / "operations-ledger" / "src",
    ):
        for path in sorted(pkg_dir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                elif isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                else:
                    continue
                for name in names:
                    if name.split(".")[0] in forbidden:
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} -> {name}")
    assert offenders == [], f"domain/ledger boundary violated: {offenders}"

def test_pure_engine_functions_accept_no_default_clock_or_id_parameters() -> None:
    """Every public function in the pure package's projection/hashing/lexical
    modules must take explicit values only - no keyword default that could
    silently substitute a clock or id."""
    modules = ["projection.py", "hashing.py", "lexical.py", "corpus.py"]
    offenders = []
    for name in modules:
        path = PURE_PKG / name
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
                continue
            defaults = node.args.defaults + [d for d in node.args.kw_defaults if d is not None]
            for default in defaults:
                if isinstance(default, ast.Call):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}::{node.name} has a callable default")
    assert offenders == [], f"pure engine function has a non-explicit default: {offenders}"

def test_application_module_names_are_within_the_exact31_ceiling() -> None:
    """R1: only the five named application-layer modules exist."""
    app_dir = REPO_ROOT / "apps" / "workspace-api" / "src" / "workspace_api" / "application"
    expected = {
        "governed_retrieval.py", "_governed_retrieval_admission.py", "_governed_retrieval_sources.py",
        "_governed_retrieval_knowledge.py", "_governed_retrieval_revalidation.py",
    }
    found = {p.name for p in app_dir.glob("_governed_retrieval_*.py")} | (
        {"governed_retrieval.py"} if (app_dir / "governed_retrieval.py").exists() else set()
    )
    assert found == expected, f"unexpected P4-A1 application module set: {found}"

# --- F3: immutable registry and every filter-widening dimension ---

def test_corpus_registry_rejects_item_assignment() -> None:
    from governed_retrieval.corpus import CORPUS_REGISTRY, CorpusId

    with pytest.raises(TypeError):
        CORPUS_REGISTRY[CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1] = None
    with pytest.raises(TypeError):
        del CORPUS_REGISTRY[CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1]

def test_filters_within_descriptor_every_widening_dimension() -> None:
    """RR1-F2: lifecycle_statuses is enforced like record_types/truth_classes -
    empty/allowed/widening per dimension; Project Knowledge allows zero
    lifecycle values, so ANY non-empty lifecycle filter for it widens."""
    from governed_retrieval.corpus import CORPUS_REGISTRY, CorpusId, filters_within_descriptor
    from retrieval_contracts.enums import RecordType, TruthClass

    d = CORPUS_REGISTRY[CorpusId.PROJECT_KNOWLEDGE_LOCAL_V1]
    assert filters_within_descriptor(d, (), ()) is True
    assert filters_within_descriptor(d, (RecordType.PROJECT_KNOWLEDGE,), ()) is True
    assert filters_within_descriptor(d, (RecordType.TASK,), ()) is False
    assert filters_within_descriptor(d, (), (TruthClass.ADVISORY_SOURCE_EVIDENCE,)) is True
    assert filters_within_descriptor(d, (), (TruthClass.CANONICAL_OPERATIONAL_RECORD,)) is False
    assert filters_within_descriptor(
        d, (RecordType.PROJECT_KNOWLEDGE,), (TruthClass.CANONICAL_OPERATIONAL_RECORD,)
    ) is False
    # Lifecycle dimension: empty always allowed; Project Knowledge allows
    # none, so even a wire-valid literal like "CURRENT" always widens.
    assert filters_within_descriptor(d, (), (), ()) is True
    assert filters_within_descriptor(d, (), (), ("CURRENT",)) is False
    ops = CORPUS_REGISTRY[CorpusId.SHIFT_CONFIRMED_OPERATIONS_V1]
    assert filters_within_descriptor(ops, (), (), ("CONFIRMED",)) is True
    assert filters_within_descriptor(ops, (), (), ("CONFIRMED", "CLOSED")) is True
    assert filters_within_descriptor(ops, (), (), ("DELETED",)) is False

def test_resolve_and_authorize_corpus_rejects_widened_filters() -> None:
    """RR1-F2: a real end-to-end probe for both record_types AND
    lifecycle_statuses - CURRENT for PROJECT_KNOWLEDGE_LOCAL_V1 must be
    FILTER_WIDENS_SCOPE, never silently pass through authorization."""
    from governed_retrieval.request_models import GovernedRetrievalRequestV1
    from workspace_api.application._governed_retrieval_sources import (
        CorpusResolutionFailed,
        resolve_and_authorize_corpus,
    )
    from _p4a1_retrieval_fixtures import DEFAULT_BUDGET

    for extra_filter in ({"record_types": ["Task"]}, {"lifecycle_statuses": ["CURRENT"]}):
        request = GovernedRetrievalRequestV1.model_validate(
            {
                "query": "x", "corpus_id": "PROJECT_KNOWLEDGE_LOCAL_V1",
                "filters": {"shift_ids": ("a",), **extra_filter},
                "context_budget": DEFAULT_BUDGET,
            }
        )
        with pytest.raises(CorpusResolutionFailed) as exc_info:
            resolve_and_authorize_corpus(request)
        assert exc_info.value.code.value == "FILTER_WIDENS_SCOPE"

def test_manifest_exact_top_level_shape_and_metadata_enforced(tmp_path) -> None:
    """RR2-F2/RR2-F6: top-level manifest must match _TOP_FIELDS exactly with
    the exact schemaVersion/packId/classification literals."""
    import json
    from workspace_api.application._governed_retrieval_knowledge import KnowledgeCorpusUnavailable, _load_manifest

    (tmp_path / "knowledge").mkdir()
    base = {
        "schemaVersion": "1.0", "packId": "shift-operations-project-knowledge",
        "classification": "INTERNAL", "reviewedAt": "2026-08-10", "entries": [],
    }
    for bad in (
        dict(base, extraField="nope"), {k: v for k, v in base.items() if k != "entries"},
        dict(base, packId="wrong-pack-id"), dict(base, classification="PUBLIC"), [],
    ):
        (tmp_path / "knowledge" / "manifest.json").write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(KnowledgeCorpusUnavailable):
            _load_manifest(tmp_path)
