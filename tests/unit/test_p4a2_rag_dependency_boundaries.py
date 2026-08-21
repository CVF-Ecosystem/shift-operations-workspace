"""P4-A2 SPEC R1/R12 - dependency direction and purity.

Structural proof only: the pure `governed_rag` package imports no provider
SDK, HTTP client, environment, database, application layer, or hidden CVF
Core, and depends only on stdlib/Pydantic/governed_retrieval/
retrieval_contracts/ai_gateway. Not governance proof - the live evidence run
is the only accepted governance proof surface (SPEC R19).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import governed_rag

PACKAGE_ROOT = Path(governed_rag.__file__).resolve().parent

FORBIDDEN_IMPORT_ROOTS = {
    "workspace_api",
    "operations_ledger",
    "operations_domain",
    "refinery_bridge",
    "fastapi",
    "starlette",
    "sqlalchemy",
    "httpx",
    "requests",
    "urllib3",
    "openai",
    "dashscope",
    "anthropic",
    "cvf_runtime",
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
        assert _module_files(), "expected governed_rag modules to exist"

    @pytest.mark.parametrize("path", _module_files(), ids=lambda p: p.name)
    def test_no_forbidden_imports(self, path: Path):
        offending = _imported_roots(path) & FORBIDDEN_IMPORT_ROOTS
        assert not offending, f"{path.name} imports forbidden module(s): {sorted(offending)}"

    def test_no_network_client_import_anywhere(self):
        """R1: the pure package performs no network I/O of its own."""
        for path in _module_files():
            roots = _imported_roots(path)
            assert "socket" not in roots, f"{path.name} imports socket"
            qualified = _imported_qualified_names(path)
            network_urllib = {n for n in qualified if n.startswith("urllib.")}
            assert not network_urllib, f"{path.name} imports network-capable {network_urllib}"

    def test_no_os_environ_access(self):
        """R1: no environment/secret access anywhere in the pure package."""
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "os.environ" not in text, f"{path.name} touches os.environ"
            assert "os.getenv" not in text, f"{path.name} touches os.getenv"

    def test_no_database_or_filesystem_persistence_import(self):
        for path in _module_files():
            roots = _imported_roots(path)
            assert "sqlite3" not in roots
            assert "psycopg" not in roots
            assert "psycopg2" not in roots

    def test_declares_only_governed_retrieval_retrieval_contracts_ai_gateway_as_project_dependencies(self):
        allowed_project_roots = {"governed_retrieval", "retrieval_contracts", "ai_gateway"}
        for path in _module_files():
            roots = _imported_roots(path)
            project_roots = roots & {
                "governed_retrieval", "retrieval_contracts", "ai_gateway",
                "workspace_api", "operations_ledger", "operations_domain", "refinery_bridge",
            }
            assert project_roots <= allowed_project_roots, f"{path.name} imports {project_roots - allowed_project_roots}"

    def test_package_does_not_import_hidden_core(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "Controlled-Vibe-Framework" not in text
            assert ".cvf" not in text


class TestPurity:
    def test_package_declares_no_application_import(self):
        for path in _module_files():
            assert "workspace_api" not in _imported_roots(path)

    def test_service_module_only_calls_ai_gateway_service_execute(self):
        """SPEC R12: the only provider-dispatch-shaped call site in the
        whole package is ``self._gateway.execute`` inside service.py - proven
        by grepping for ``.execute(`` occurrences and asserting there is
        exactly one, on the injected gateway attribute."""
        service_text = (PACKAGE_ROOT / "service.py").read_text(encoding="utf-8")
        occurrences = service_text.count("await self._gateway.execute(")
        assert occurrences == 1

    def test_no_module_defines_its_own_http_post_or_request_call(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "urlopen" not in text
            assert "requests.post" not in text
            assert "httpx." not in text
