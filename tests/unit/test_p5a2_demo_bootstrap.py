"""Standalone child imports cannot rely on pytest's source-root injection."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from p5a2_source_demo_bootstrap import isolated_child_env, source_path  # noqa: E402


def test_clean_child_seed_import_and_complete_nonphysical_app(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "C:/untrusted/path")
    monkeypatch.setenv("OPENAI_API_KEY", "inert-poison")
    env = isolated_child_env({
        "P5A2_SOURCE_DEMO_PROFILE": "P5A2-SOURCE-DEMO-LOCAL-1",
        "DATABASE_URL": "postgresql+psycopg://source_demo:inert@127.0.0.1:5433/shiftops_p5a2_source_demo",
        "JWT_SECRET_KEY": "T" * 48, "AI_MODE": "NO_AI",
        "PROACTIVE_SOURCE_INSTANCE_ID": "P5A2-SOURCE-DEMO-LOCAL-1",
        "APP_ENV": "source_demo", "CORS_ALLOWED_ORIGINS": "http://127.0.0.1:5174",
    })
    assert env["PYTHONPATH"] == source_path()
    assert "C:/untrusted/path" not in env["PYTHONPATH"]
    assert "OPENAI_API_KEY" not in env
    code = (
        "import workspace_api.demo.seed; "
        "from workspace_api.demo.app import create_app; "
        "app=create_app(nonphysical_test_ledger=object()); "
        "print(app.state.demo_evidence_class)"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                            env=env, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "NONPHYSICAL_IN_PROCESS"


def test_child_refuses_override_or_missing_trusted_source(monkeypatch, tmp_path):
    import pytest
    from p5a2_source_demo_bootstrap import isolated_child_env, source_path

    with pytest.raises(RuntimeError, match="SOURCE_PATH_OVERRIDE"):
        isolated_child_env({"PYTHONPATH": "C:/poison"})
    with pytest.raises(RuntimeError, match="SOURCE_ROOT_INVALID"):
        source_path(tmp_path)
