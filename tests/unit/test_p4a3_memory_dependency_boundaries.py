"""P4-A3 SPEC R1/R10 - dependency direction and purity.

Structural proof only: the pure ``application_memory`` package imports no
workspace application, provider SDK, HTTP client, environment, database, other
project packages, or hidden CVF Core, and depends only on stdlib/Pydantic/
retrieval_contracts. Not governance proof.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import application_memory

PACKAGE_ROOT = Path(application_memory.__file__).resolve().parent

FORBIDDEN_IMPORT_ROOTS = {
    "workspace_api",
    "operations_ledger",
    "operations_domain",
    "refinery_bridge",
    "governed_retrieval",
    "ai_gateway",
    "governed_rag",
    "cvf_runtime",
    "fastapi",
    "starlette",
    "sqlalchemy",
    "httpx",
    "requests",
    "urllib3",
    "openai",
    "dashscope",
    "anthropic",
}


def _module_files() -> list[Path]:
    return sorted(PACKAGE_ROOT.glob("*.py"))


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _imported_qualified_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                names.add(node.module)
    return names


class TestDependencyDirection:
    def test_package_has_modules(self):
        assert _module_files()

    @pytest.mark.parametrize("path", _module_files(), ids=lambda p: p.name)
    def test_no_forbidden_imports(self, path: Path):
        offending = _imported_roots(path) & FORBIDDEN_IMPORT_ROOTS
        assert not offending, f"{path.name} imports forbidden module(s): {sorted(offending)}"

    def test_no_network_client_import_anywhere(self):
        for path in _module_files():
            roots = _imported_roots(path)
            assert "socket" not in roots, f"{path.name} imports socket"
            qualified = _imported_qualified_names(path)
            assert not {n for n in qualified if n.startswith("urllib.")}, f"{path.name} imports urllib"

    def test_no_os_environ_access(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "os.environ" not in text, f"{path.name} touches os.environ"
            assert "os.getenv" not in text, f"{path.name} touches os.getenv"

    def test_no_database_import(self):
        for path in _module_files():
            roots = _imported_roots(path)
            assert "sqlite3" not in roots
            assert "psycopg" not in roots
            assert "psycopg2" not in roots

    def test_declares_only_retrieval_contracts_as_project_dependency(self):
        for path in _module_files():
            roots = _imported_roots(path)
            project_roots = roots & {
                "retrieval_contracts", "workspace_api", "operations_ledger", "operations_domain",
                "refinery_bridge", "governed_retrieval", "ai_gateway", "governed_rag", "cvf_runtime",
            }
            assert project_roots <= {"retrieval_contracts"}, f"{path.name} imports {project_roots - {'retrieval_contracts'}}"

    def test_package_does_not_import_hidden_core(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "Controlled-Vibe-Framework" not in text
            assert ".cvf" not in text


class TestPurity:
    def test_package_declares_no_application_import(self):
        for path in _module_files():
            assert "workspace_api" not in _imported_roots(path)

    def test_no_module_defines_http_post_or_request(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "urlopen" not in text
            assert "requests.post" not in text
            assert "httpx." not in text
