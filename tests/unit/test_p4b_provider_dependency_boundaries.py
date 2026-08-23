"""P4-B SPEC R10 - dependency direction and purity.

Structural proof only: the pure ``ai_providers`` package imports no
workspace application, provider SDK, HTTP client, socket, environment,
filesystem, database, other unrelated project package, or hidden CVF Core,
and depends only on stdlib/Pydantic/``ai_gateway``. Not governance proof.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_providers

PACKAGE_ROOT = Path(ai_providers.__file__).resolve().parent

FORBIDDEN_IMPORT_ROOTS = {
    "workspace_api",
    "operations_ledger",
    "operations_domain",
    "refinery_bridge",
    "governed_retrieval",
    "governed_rag",
    "application_memory",
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

    def test_declares_only_ai_gateway_as_project_dependency(self):
        for path in _module_files():
            roots = _imported_roots(path)
            project_roots = roots & {
                "ai_gateway", "workspace_api", "operations_ledger", "operations_domain",
                "refinery_bridge", "governed_retrieval", "governed_rag", "cvf_runtime",
            }
            assert project_roots <= {"ai_gateway"}, f"{path.name} imports {project_roots - {'ai_gateway'}}"

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

    def test_no_filesystem_write_call(self):
        for path in _module_files():
            text = path.read_text(encoding="utf-8")
            assert "open(" not in text
            assert "write_text" not in text
            assert "write_bytes" not in text


class TestApplicationCompositionBoundary:
    """The one-file application composition (SPEC R10) opens no route,
    reads no environment, and imports nothing beyond ai_providers itself."""

    def test_composition_module_has_no_environment_or_route_import(self):
        import workspace_api.application.ai_provider_modes as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "os.environ" not in text
        assert "os.getenv" not in text
        assert "APIRouter" not in text
        assert "@router" not in text
        assert "fastapi" not in text.lower()

    def test_composition_module_persists_nothing(self):
        import workspace_api.application.ai_provider_modes as module

        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "INSERT INTO" not in text
        assert "session.add" not in text
        assert "session.commit" not in text


class TestObjectIdentity:
    """Relocated from test_p4b_provider_service.py for file-size budget -
    proves ProviderModeService never constructs a second gateway/registry of
    its own (SPEC R6/R8): the exposed properties are the same objects the
    caller injected."""

    def test_gateway_and_registry_properties_are_the_same_injected_instances(self):
        from ai_gateway.models import Placement
        from ai_providers.models import ProviderKind, ProviderMetadataV1
        from ai_providers.registry import ProviderAdapterRegistry
        from ai_providers.rules_only import RuleSetV1
        from ai_providers.service import ProviderModeService

        class _Gateway:
            async def execute(self, request):
                raise AssertionError("never called by this identity-only test")

        registry = ProviderAdapterRegistry()
        registry.register(ProviderMetadataV1(
            provider_id="p1", kind=ProviderKind.EXTERNAL_GATEWAY, placement=Placement.LOCAL,
            model_ids=("m1",), evidence_eligible=True,
        ))
        gateway = _Gateway()
        service = ProviderModeService(rule_set=RuleSetV1(()), registry=registry, gateway=gateway)
        assert service.gateway is gateway
        assert service.registry is registry
