import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
            names.append("DYNAMIC_IMPORT")
    return names


def test_only_main_imports_concrete_channel_adapters():
    edge = ROOT / "apps/integration-edge/src/integration_edge"
    owners = []
    for path in edge.rglob("*.py"):
        if any(name == "channel_adapters" or name.startswith("channel_adapters.") for name in imports(path)):
            owners.append(path.relative_to(ROOT).as_posix())
    assert owners == ["apps/integration-edge/src/integration_edge/main.py"]


def test_sdk_and_adapters_dependency_direction_has_no_reverse_or_dynamic_import():
    sdk = ROOT / "packages/channel-sdk/src/channel_sdk"
    adapters = ROOT / "packages/channel-adapters/src/channel_adapters"
    for path in sdk.rglob("*.py"):
        names = imports(path)
        assert not any(name.startswith("channel_adapters") for name in names)
        assert "DYNAMIC_IMPORT" not in names
    for path in adapters.rglob("*.py"):
        names = imports(path)
        assert not any(name.startswith("integration_edge") for name in names)
        assert "DYNAMIC_IMPORT" not in names


def test_legacy_interface_is_unmodified_and_unimported():
    legacy = ROOT / "packages/channel-sdk/adapter-interface/adapter.py"
    assert legacy.exists()
    searched = list((ROOT / "apps/integration-edge/src").rglob("*.py"))
    searched += list((ROOT / "packages/channel-sdk/src").rglob("*.py"))
    searched += list((ROOT / "packages/channel-adapters/src").rglob("*.py"))
    assert all("adapter-interface" not in path.read_text(encoding="utf-8") for path in searched)


def test_adapter_package_has_no_http_client_vendor_or_plugin_dependency():
    text = (ROOT / "packages/channel-adapters/pyproject.toml").read_text(encoding="utf-8")
    assert "requests" not in text and "httpx" not in text and "entry_points" not in text
    assert 'dependencies = ["pydantic==2.10.6", "channel-sdk>=0.1.0"]' in text
