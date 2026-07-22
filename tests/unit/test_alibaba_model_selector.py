from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SELECTOR_PATH = REPO_ROOT / "packages/ai-providers/alibaba/select_model.py"
SPEC = importlib.util.spec_from_file_location("alibaba_select_model", SELECTOR_PATH)
assert SPEC and SPEC.loader
selector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(selector)


def _write_catalog(tmp_path: Path, models: list[dict]) -> Path:
    path = tmp_path / "catalog.json"
    path.write_text(
        json.dumps({"provider": "alibaba_dashscope", "models": models}),
        encoding="utf-8",
    )
    return path


def _model(
    code: str,
    *,
    expires_on: str = "2026-08-01",
    remaining: int = 100,
    enabled: bool = True,
    priority: int = 10,
) -> dict:
    return {
        "model": code,
        "remaining": remaining,
        "total": 100,
        "expires_on": expires_on,
        "enabled": enabled,
        "priority": priority,
    }


def test_operator_snapshot_prefers_soon_expiring_deepseek_model():
    assert selector.select_model(on_date=date(2026, 7, 22)) == "deepseek-v4-flash"


def test_expiration_date_is_ineligible_to_avoid_end_of_day_ambiguity(tmp_path):
    path = _write_catalog(
        tmp_path,
        [_model("expires-today", expires_on="2026-07-22"), _model("valid", priority=20)],
    )
    assert selector.select_model(path, on_date=date(2026, 7, 22)) == "valid"


def test_disabled_and_exhausted_models_are_skipped(tmp_path):
    path = _write_catalog(
        tmp_path,
        [
            _model("disabled", enabled=False),
            _model("exhausted", remaining=0),
            _model("usable", priority=30),
        ],
    )
    assert selector.select_model(path, on_date=date(2026, 7, 22)) == "usable"


def test_priority_then_expiration_then_quota_is_deterministic(tmp_path):
    path = _write_catalog(
        tmp_path,
        [
            _model("later", expires_on="2026-08-03"),
            _model("lower-quota", expires_on="2026-08-02", remaining=50),
            _model("winner", expires_on="2026-08-02", remaining=80),
            _model("lower-priority", expires_on="2026-07-23", priority=20),
        ],
    )
    assert selector.select_model(path, on_date=date(2026, 7, 22)) == "winner"


def test_no_eligible_model_raises_controlled_error(tmp_path):
    path = _write_catalog(tmp_path, [_model("expired", expires_on="2026-07-21")])
    with pytest.raises(selector.CatalogError, match="no eligible Alibaba model"):
        selector.select_model(path, on_date=date(2026, 7, 22))


def test_malformed_expiration_is_rejected(tmp_path):
    path = _write_catalog(tmp_path, [_model("bad-date", expires_on="not-a-date")])
    with pytest.raises(selector.CatalogError, match="invalid expires_on"):
        selector.load_catalog(path)
