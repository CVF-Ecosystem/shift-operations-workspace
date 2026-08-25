import ast
from pathlib import Path

def test_edge_domain_has_no_prohibited_imports():
    root=Path(__file__).resolve().parents[2]/"apps/integration-edge/src/integration_edge"
    prohibited=("workspace_api","operations_ledger","ai_gateway","ai_providers","governed_rag","governed_retrieval")
    for path in root.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names=[node.module] if isinstance(node,ast.ImportFrom) else [n.name for n in node.names] if isinstance(node,ast.Import) else []
            assert not any((name or "").startswith(prohibited) for name in names),path

def test_no_deployable_adapter_implementation():
    root=Path(__file__).resolve().parents[2]/"apps/integration-edge/src/integration_edge"
    assert not list(root.rglob("*adapter*.py"))
