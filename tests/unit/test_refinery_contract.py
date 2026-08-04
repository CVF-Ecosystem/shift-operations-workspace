from __future__ import annotations

import ast
import json
from pathlib import Path

import yaml

from refinery_bridge.enums import Sensitivity
from refinery_bridge.input_models import RefineryEnvelopeV1

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages" / "refinery-bridge"


def test_yaml_contract_matches_closed_boundary() -> None:
    contract = yaml.safe_load((PACKAGE / "contracts" / "refinery_contract.yaml").read_text())
    assert contract["stages"] == [
        "ENVELOPE", "NORMALIZATION", "TERMINOLOGY", "CLASSIFICATION", "CONFLICT",
        "REDACTION", "DEDUPE", "QUALITY", "CANDIDATE_ADMISSION",
    ]
    assert contract["sensitivity"] == [item.value for item in Sensitivity]
    assert contract["constraints"]["provider_calls"] == 0
    assert contract["constraints"]["network_calls"] == 0
    assert contract["constraints"]["runtime_caller"] is False


def test_sensitivity_exactly_matches_data_policy() -> None:
    policy = yaml.safe_load(
        (ROOT / "packages" / "cvf-application-profile" / "data-policy.yaml").read_text()
    )
    serialized = json.dumps(policy)
    for value in Sensitivity:
        assert value.value in serialized
    discovered = {token for token in ("PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED") if token in serialized}
    assert discovered == {item.value for item in Sensitivity}


def test_reviewed_json_fixtures_are_structurally_complete() -> None:
    negative = json.loads((ROOT / "fixtures" / "refinery" / "normalized_message.json").read_text())
    positive = json.loads((ROOT / "fixtures" / "refinery" / "qualified_time_message.json").read_text())
    for case in (negative, positive):
        RefineryEnvelopeV1.model_validate_json(json.dumps(case["input"], ensure_ascii=False))
    assert "11h40" in negative["input"]["raw_text"]
    assert "23:40" not in negative["input"]["raw_text"]
    assert positive["expected_disposition"] == "CANDIDATE_READY"


def test_package_has_no_forbidden_imports_or_calls() -> None:
    forbidden_imports = {
        "requests", "httpx", "socket", "sqlalchemy", "cvf_runtime", "subprocess",
        "pathlib", "os", "random", "secrets", "time",
    }
    for path in (PACKAGE / "src" / "refinery_bridge").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        assert not (imports & forbidden_imports), (path, imports & forbidden_imports)
