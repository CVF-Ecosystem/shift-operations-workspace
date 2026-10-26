"""P5-A binary export OpenAPI delta over the unchanged C3b2 golden."""

from __future__ import annotations

import hashlib
import json
import os

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

_EXPORT_PATH = "/reports/{report_id}/export"
_EXPORT_OPERATION_SHA = "f680820c3a9232ca1528ab0ca8c5f67c9c89a9038dea6993f0664d48daa59535"
_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _strip_p5a_export_delta(doc: dict) -> None:
    """Verify and remove the exact P5-A2 source and P5-A export deltas.

    The source leaf is removed first so the historical export leaf sees its
    unchanged pre-source document. Missing or altered coverage fails before
    deletion; all unrelated paths and schemas remain for golden comparison.
    """
    from test_p5a2_source_openapi_contract import _strip_p5a_source_delta

    _strip_p5a_source_delta(doc)

    paths = doc["paths"]
    assert _EXPORT_PATH in paths, "P5-A export path missing"
    operations = paths[_EXPORT_PATH]
    assert set(operations) == {"get"}, "P5-A export method set changed"
    operation = operations["get"]
    assert operation["security"] == [{"HTTPBearer": []}]
    parameters = operation["parameters"]
    assert [(item["name"], item["in"], item["required"]) for item in parameters] == [
        ("report_id", "path", True),
        ("format", "query", True),
        ("view", "query", True),
    ]
    assert parameters[1]["schema"] == {"type": "string", "enum": ["pdf", "xlsx"]}
    assert parameters[2]["schema"] == {"type": "string", "enum": [
        "shift-summary", "customer-report", "incident-report", "handover-report",
    ]}
    assert set(operation["responses"]) == {"200", "422"}
    assert operation["responses"]["200"]["content"] == {
        "application/pdf": {"schema": {"type": "string", "format": "binary"}},
        _XLSX_MIME: {"schema": {"type": "string", "format": "binary"}},
    }
    assert _sha(operations) == _EXPORT_OPERATION_SHA, "P5-A export operation changed"
    del paths[_EXPORT_PATH]


def test_p5a_export_is_the_only_delta_over_c3b2_golden():
    from test_c3b2_mutation_openapi_contract import GOLDEN_OPENAPI_SHA
    from workspace_api.main import app

    reduced = json.loads(json.dumps(app.openapi()))
    _strip_p5a_export_delta(reduced)
    assert _sha(reduced) == GOLDEN_OPENAPI_SHA


def test_missing_or_altered_export_coverage_is_rejected():
    from workspace_api.main import app

    for mutation in ("missing", "extra_method", "changed_response", "changed_auth",
                     "changed_enum", "changed_mime"):
        doc = json.loads(json.dumps(app.openapi()))
        if mutation == "missing":
            del doc["paths"][_EXPORT_PATH]
        elif mutation == "extra_method":
            doc["paths"][_EXPORT_PATH]["post"] = {"responses": {"200": {}}}
        elif mutation == "changed_response":
            doc["paths"][_EXPORT_PATH]["get"]["responses"]["200"]["description"] = "Changed"
        elif mutation == "changed_auth":
            doc["paths"][_EXPORT_PATH]["get"]["security"] = []
        elif mutation == "changed_enum":
            doc["paths"][_EXPORT_PATH]["get"]["parameters"][1]["schema"]["enum"] = ["pdf"]
        else:
            del doc["paths"][_EXPORT_PATH]["get"]["responses"]["200"]["content"][_XLSX_MIME]
        with pytest.raises(AssertionError):
            _strip_p5a_export_delta(doc)


def test_unrelated_path_cannot_hide_behind_p5a_delta():
    from test_c3b2_mutation_openapi_contract import GOLDEN_OPENAPI_SHA
    from workspace_api.main import app

    reduced = json.loads(json.dumps(app.openapi()))
    reduced["paths"]["/undisclosed-p5a-probe"] = {"get": {"responses": {"200": {}}}}
    _strip_p5a_export_delta(reduced)
    assert _sha(reduced) != GOLDEN_OPENAPI_SHA


def test_unrelated_schema_cannot_hide_behind_p5a_delta():
    from test_c3b2_mutation_openapi_contract import GOLDEN_OPENAPI_SHA
    from workspace_api.main import app

    reduced = json.loads(json.dumps(app.openapi()))
    reduced["components"]["schemas"]["UnrelatedProbe"] = {"type": "object"}
    _strip_p5a_export_delta(reduced)
    assert reduced["components"]["schemas"]["UnrelatedProbe"] == {"type": "object"}
    assert _sha(reduced) != GOLDEN_OPENAPI_SHA


def test_legacy_operation_change_cannot_hide_behind_p5a_delta():
    from test_c3b2_mutation_openapi_contract import GOLDEN_OPENAPI_SHA
    from workspace_api.main import app

    reduced = json.loads(json.dumps(app.openapi()))
    reduced["paths"]["/shifts"]["post"]["summary"] = "Changed legacy operation"
    _strip_p5a_export_delta(reduced)
    assert _sha(reduced) != GOLDEN_OPENAPI_SHA
