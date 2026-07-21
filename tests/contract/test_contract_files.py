import json
from pathlib import Path

def test_json_contracts_are_parseable():
    root = Path(__file__).resolve().parents[2] / "packages" / "workspace-contracts"
    files = list(root.rglob("*.json"))
    assert files
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))
