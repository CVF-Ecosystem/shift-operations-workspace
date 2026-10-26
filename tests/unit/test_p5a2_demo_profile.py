"""Isolated settings and fixed database profile checks; no DB or listener."""

import importlib
import importlib.util
from pathlib import Path

import pytest

from workspace_api.config import Settings
from workspace_api.dependencies import get_proactive_source_coverage


def test_normal_coverage_remains_absent():
    assert get_proactive_source_coverage() is None


def test_demo_marker_disables_dotenv(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("APP_ENV=poisoned\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("P5A2_SOURCE_DEMO_PROFILE", "P5A2-SOURCE-DEMO-LOCAL-1")
    monkeypatch.setenv("JWT_SECRET_KEY", "T" * 40)
    monkeypatch.delenv("APP_ENV", raising=False)
    assert Settings().app_env == "development"


def test_demo_module_requires_exact_marker(monkeypatch):
    monkeypatch.delenv("P5A2_SOURCE_DEMO_PROFILE", raising=False)
    from workspace_api import demo

    path = Path(demo.__file__).with_name("app.py")
    spec = importlib.util.spec_from_file_location("workspace_api.demo._marker_probe", path)
    assert spec and spec.loader
    with pytest.raises(RuntimeError, match="profile marker"):
        spec.loader.exec_module(importlib.util.module_from_spec(spec))


def test_ambient_provider_key_refuses_demo_child(monkeypatch):
    monkeypatch.setenv("P5A2_SOURCE_DEMO_PROFILE", "P5A2-SOURCE-DEMO-LOCAL-1")
    module = importlib.import_module("workspace_api.demo.app")
    monkeypatch.setenv("OPENAI_API_KEY", "inert-test-sentinel")
    with pytest.raises(RuntimeError, match="ambient provider"):
        module._profile_settings()
