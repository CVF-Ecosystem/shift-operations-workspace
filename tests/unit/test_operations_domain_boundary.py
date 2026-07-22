"""Boundary tests for the extracted operations-domain package (tranche P1-B).

Covers SPEC acceptance criteria AC-01, AC-02, AC-03, AC-05 and AC-15.

The import-isolation test (AC-01) is deliberately NOT a bare `sys.path` wipe.
`operations_domain` legitimately depends on `pydantic`; emptying `sys.path`
would make the import fail for a reason unrelated to the boundary, turning a
green run into a false negative and a red one into a misleading failure. The
isolation removes repository SOURCE ROOTS only, keeps the standard library and
site-packages, and asserts that `pydantic` still imports as a guard proving the
environment was not over-stripped. See SPEC section 4.3.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_SRC = REPO_ROOT / "packages" / "operations-domain" / "src"
DOMAIN_PKG = DOMAIN_SRC / "operations_domain"

MOVED_TYPES = [
    "CustomerRequest",
    "CustomerRequestStatus",
    "Correction",
    "DataState",
    "EvidenceRef",
    "Message",
    "OperationalEvent",
    "RiskClass",
    "Shift",
    "ShiftStatus",
    "Task",
    "TaskStatus",
]
MOVED_FUNCTIONS = [
    "assert_customer_request_transition",
    "assert_task_transition",
    "assert_transition",
]
FORBIDDEN_IN_DOMAIN = (
    "workspace_api",
    "operations_ledger",
    "cvf_runtime",
    "fastapi",
    "sqlalchemy",
)
PRODUCTION_ROOTS = ("apps", "packages", "scripts")
SHIM_MODELS = "apps/workspace-api/src/workspace_api/domain/models.py"
SHIM_LIFECYCLE = "apps/workspace-api/src/workspace_api/domain/lifecycle.py"
# SPEC R5.2 exceptions, asserted by exact path. A third match must fail.
E1_NAMESPACE_INJECTION = "apps/workspace-api/src/workspace_api/infrastructure/ledger_factory.py"
E2_USER_IMPORTERS = {
    "apps/workspace-api/src/workspace_api/infrastructure/repository.py",
    "scripts/seed_dev_users.py",
}

_ISOLATION_PROGRAM = textwrap.dedent(
    """
    import importlib, sys
    from pathlib import Path

    repo_root = Path(sys.argv[1]).resolve()
    allowed = Path(sys.argv[2]).resolve()

    import operations_domain.models as m
    import operations_domain.lifecycle as lc

    # Guard: the environment was NOT over-stripped. If pydantic could not be
    # imported, a passing boundary assertion would prove nothing.
    import pydantic  # noqa: F401

    assert m.Shift.__module__ == "operations_domain.models", m.Shift.__module__
    assert lc.assert_transition.__module__ == "operations_domain.lifecycle"

    forbidden = ("workspace_api", "operations_ledger", "cvf_runtime")
    for name in forbidden:
        assert name not in sys.modules, f"{name} leaked into sys.modules"

    for name in forbidden:
        try:
            importlib.import_module(name)
        except ModuleNotFoundError:
            pass
        else:
            raise AssertionError(f"{name} was importable - repo roots are still on sys.path")

    for entry in sys.path:
        if not entry:
            continue
        p = Path(entry).resolve()
        if p == allowed:
            continue
        assert repo_root not in p.parents and p != repo_root, f"repo path on sys.path: {p}"

    print("ISOLATION_OK")
    """
)


def test_operations_domain_imports_without_any_other_repo_root(tmp_path):
    """AC-01 / AC-15 / R7: repository-scoped import isolation."""
    script = tmp_path / "isolation_probe.py"
    script.write_text(_ISOLATION_PROGRAM, encoding="utf-8")

    env = {
        k: v
        for k, v in __import__("os").environ.items()
        # Drop any inherited path injection rather than extending it.
        if k not in {"PYTHONPATH", "PYTHONSTARTUP"}
    }
    env["PYTHONPATH"] = str(DOMAIN_SRC)

    proc = subprocess.run(
        # -P: do not prepend the script directory or cwd to sys.path.
        # -E is NOT used: it would drop the PYTHONPATH we deliberately set.
        [sys.executable, "-P", str(script), str(REPO_ROOT), str(DOMAIN_SRC)],
        cwd=tmp_path,  # temporary cwd outside the repository
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"isolation subprocess failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert "ISOLATION_OK" in proc.stdout


def _domain_source_files() -> list[Path]:
    return sorted(DOMAIN_PKG.rglob("*.py"))


def test_operations_domain_has_no_reverse_import():
    """AC-02 / R1.2: static scan - the package imports nothing from the repo."""
    files = _domain_source_files()
    assert files, "no source files found under operations_domain"
    offenders = []
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.split(".")[0]
                if root in FORBIDDEN_IN_DOMAIN:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} -> {name}")
    assert offenders == [], f"operations_domain must not import repo/framework code: {offenders}"


def _iter_production_files():
    for root in PRODUCTION_ROOTS:
        for path in sorted((REPO_ROOT / root).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            yield path


def test_exactly_one_canonical_definition_per_moved_name():
    """AC-03 / R2.2, R2.3, R3.1: one ClassDef/FunctionDef, in the right module."""
    locations: dict[str, list[str]] = {n: [] for n in MOVED_TYPES + MOVED_FUNCTIONS}
    for path in _iter_production_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name in locations:
                locations[node.name].append(path.relative_to(REPO_ROOT).as_posix())
            elif isinstance(node, ast.FunctionDef) and node.name in locations:
                locations[node.name].append(path.relative_to(REPO_ROOT).as_posix())

    expected_models = "packages/operations-domain/src/operations_domain/models.py"
    expected_lifecycle = "packages/operations-domain/src/operations_domain/lifecycle.py"
    for name in MOVED_TYPES:
        assert locations[name] == [expected_models], f"{name}: {locations[name]}"
    for name in MOVED_FUNCTIONS:
        assert locations[name] == [expected_lifecycle], f"{name}: {locations[name]}"


def test_runtime_module_attribution_matches_the_canonical_package():
    """AC-03 (runtime half): __module__ points at operations_domain."""
    from operations_domain import lifecycle as lc
    from operations_domain import models as m

    for name in MOVED_TYPES:
        assert getattr(m, name).__module__ == "operations_domain.models", name
    for name in MOVED_FUNCTIONS:
        assert getattr(lc, name).__module__ == "operations_domain.lifecycle", name


def test_production_code_does_not_source_moved_models_from_the_app_package():
    """AC-05 / R5: only the two documented exceptions may remain."""
    moved = set(MOVED_TYPES) | set(MOVED_FUNCTIONS)
    moved_offenders: list[str] = []
    user_importers: set[str] = set()
    namespace_importers: set[str] = set()

    for path in _iter_production_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in (SHIM_MODELS, SHIM_LIFECYCLE):
            continue  # the shims exist to re-export; R5.3
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            module = node.module or ""
            names = {a.name for a in node.names}
            if module in ("workspace_api.domain.models", "workspace_api.domain.lifecycle"):
                leaked = names & moved
                if leaked:
                    moved_offenders.append(f"{rel}:{node.lineno} -> {sorted(leaked)}")
                if "User" in names:
                    user_importers.add(rel)
            elif module == "workspace_api.domain" and "models" in names:
                namespace_importers.add(rel)

    assert moved_offenders == [], (
        "production code must import moved models from operations_domain: " f"{moved_offenders}"
    )
    assert user_importers == E2_USER_IMPORTERS, f"unexpected User importers: {user_importers}"
    assert namespace_importers == {E1_NAMESPACE_INJECTION}, (
        f"unexpected shim-namespace importers: {namespace_importers}"
    )


def test_no_package_imports_the_application_layer():
    """AC-15: nothing under packages/** may import workspace_api."""
    offenders = []
    for path in sorted((REPO_ROOT / "packages").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("workspace_api"):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("workspace_api"):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
    assert offenders == [], f"packages/** must not import the application layer: {offenders}"
