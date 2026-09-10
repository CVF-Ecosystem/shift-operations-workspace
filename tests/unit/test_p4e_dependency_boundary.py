"""P4-E dependency direction and negative-import proof (SPEC R18, AC-11,
AC-16). identity-mapping imports no Workspace API type; conversation-routing
consumes an identity read port and never mutates mappings; Integration Edge
may emit sender evidence but never imports either P4-E package; the
process-local proposal repository is not reachable from Workspace API's
production composition; customer/vessel scaffolds remain untouched.
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _imported_names(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
        elif isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
    return names


def test_identity_mapping_imports_no_workspace_api_or_ledger_backend():
    root = REPO_ROOT / "packages/identity-mapping/src/identity_mapping"
    prohibited = ("workspace_api", "operations_ledger", "sqlalchemy", "fastapi")
    for path in root.rglob("*.py"):
        for name in _imported_names(path):
            assert not any((name or "").startswith(p) for p in prohibited), (path, name)


def test_conversation_routing_imports_no_workspace_api_or_ledger_backend():
    root = REPO_ROOT / "packages/conversation-routing/src/conversation_routing"
    prohibited = ("workspace_api", "operations_ledger", "sqlalchemy", "fastapi")
    for path in root.rglob("*.py"):
        for name in _imported_names(path):
            assert not any((name or "").startswith(p) for p in prohibited), (path, name)


def test_conversation_routing_service_never_calls_mapping_mutation_methods():
    """SPEC R18: conversation-routing consumes an identity read port and
    never mutates mappings - its service source must not reference any of
    the mapping write actions identity_mapping.service exposes."""
    source = (
        REPO_ROOT / "packages/conversation-routing/src/conversation_routing/service.py"
    ).read_text(encoding="utf-8")
    forbidden_calls = ("propose_mapping", "confirm_mapping", "reject_mapping", "revoke_mapping",
                        "privacy_delete_mapping", ".propose(", ".confirm(", ".reject(", ".revoke(")
    for call in forbidden_calls:
        assert call not in source, call


def test_integration_edge_never_imports_either_p4e_package():
    root = REPO_ROOT / "apps/integration-edge/src/integration_edge"
    prohibited = ("identity_mapping", "conversation_routing")
    for path in root.rglob("*.py"):
        for name in _imported_names(path):
            assert not any((name or "").startswith(p) for p in prohibited), (path, name)


def test_p4e_packages_never_import_provider_sdks():
    prohibited_prefixes = ("openai", "anthropic", "boto3", "google")
    for pkg in ("identity-mapping/src/identity_mapping", "conversation-routing/src/conversation_routing"):
        root = REPO_ROOT / "packages" / pkg
        for path in root.rglob("*.py"):
            for name in _imported_names(path):
                assert not any((name or "").startswith(p) for p in prohibited_prefixes), (path, name)


def test_customer_vessel_scaffolds_remain_documentation_only():
    """Manifest protected exclusion: no new path under either scaffold
    directory, and each contains only its README."""
    for name in ("customer-router", "vessel-router"):
        directory = REPO_ROOT / "packages/conversation-routing" / name
        files = sorted(p.name for p in directory.rglob("*") if p.is_file())
        assert files == ["README.md"], (name, files)


def test_production_composition_uses_ledger_repository_when_durable_backend_configured():
    """SPEC R10/AC-16: a real import/composition probe. Imports the actual
    Workspace API composition function and inspects the concrete bound
    repository type - never a source-comment assertion or string scan. The
    default test/dev environment has no ``DATABASE_URL`` (pre-existing,
    documented ``ledger_factory.py`` "offline/degraded mode", unrelated to
    P4-E), so this exercises the composition function with an injected
    durable Ledger rather than asserting a claim the ambient environment
    cannot support - the full durable-vs-degraded matrix is covered in
    ``test_p4e_workspace_composition.py``."""
    sys.path.insert(0, str(REPO_ROOT / "apps/workspace-api/src"))
    sys.path.insert(0, str(REPO_ROOT / "apps/integration-edge/src"))
    sys.path.insert(0, str(REPO_ROOT / "packages/identity-mapping/src"))
    sys.path.insert(0, str(REPO_ROOT / "packages/conversation-routing/src"))
    sys.path.insert(0, str(REPO_ROOT / "packages/channel-sdk/src"))
    sys.path.insert(0, str(REPO_ROOT / "packages/cvf-runtime/src"))
    sys.path.insert(0, str(REPO_ROOT / "packages/operations-ledger/src"))
    sys.path.insert(0, str(REPO_ROOT / "packages/operations-domain/src"))

    import workspace_api.main as main_module
    import workspace_api.dependencies as dependencies_module
    from workspace_api.external_ingress.repository import (
        InMemoryExternalIngressRepository,
        LedgerExternalIngressRepository,
    )
    from operations_ledger.sql_ledger import SqlLedger, make_engine
    from operations_ledger.tables import metadata
    from workspace_api.domain import models as domain_models

    engine = make_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    durable_ledger = SqlLedger("sqlite:///:memory:", models=domain_models, engine=engine)

    original_get_ledger = dependencies_module.get_ledger
    dependencies_module.get_ledger = lambda: durable_ledger
    try:
        service = main_module._compose_external_ingress_service()
    finally:
        dependencies_module.get_ledger = original_get_ledger

    assert isinstance(service.repository, LedgerExternalIngressRepository)
    assert not isinstance(service.repository, InMemoryExternalIngressRepository)
    assert type(service.repository) is not InMemoryExternalIngressRepository
