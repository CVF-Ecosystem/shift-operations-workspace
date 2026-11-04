"""Start the two approved loopback children after SQL acceptance."""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote

from p5a2_source_demo_bootstrap import source_path
from p5a2_source_demo_common import PROFILE, ROOT, fail
from p5a2_source_demo_start import start_child, wait_http


def child_settings(secret: dict[str, str]) -> tuple[str, dict[str, str]]:
    password = quote(secret["db_password"], safe="")
    dsn = ("postgresql+psycopg://source_demo:" + password
           + "@127.0.0.1:5433/shiftops_p5a2_source_demo")
    env = {"DATABASE_URL": dsn, "JWT_SECRET_KEY": secret["jwt_secret"],
           "AI_MODE": "NO_AI", "P5A2_SOURCE_DEMO_PROFILE": PROFILE,
           "PROACTIVE_SOURCE_INSTANCE_ID": PROFILE, "APP_ENV": "source_demo",
           "CORS_ALLOWED_ORIGINS": "http://127.0.0.1:5174",
           "PYTHONPATH": source_path(), "PYTHONNOUSERSITE": "1",
           "PYTHONDONTWRITEBYTECODE": "1"}
    return dsn, env


def start_services(node: str, env: dict[str, str], resource: dict,
                   state: dict, handles: dict) -> None:
    api_argv = [sys.executable, "-m", "uvicorn", "workspace_api.demo.app:create_app",
                "--factory", "--host", "127.0.0.1", "--port", "8001"]
    pid, started = start_child(api_argv, env, "api", resource, state, handles)
    state.update({"api_start": started, "api_executable": str(Path(sys.executable).resolve())})
    wait_http("http://127.0.0.1:8001/health")
    web = ROOT / "apps/workspace-web"
    vite = web / "node_modules/vite/bin/vite.js"
    config = web / "vite.source-demo.config.ts"
    output = ROOT / ".venv/p5a2-source-demo-web"
    if not Path(node).is_file() or not vite.is_file() or not config.is_file():
        raise fail("WEB_DEPENDENCY_ABSENT")
    from p5a2_source_demo_common import run
    run([node, str(vite), "build", "--config", str(config), "--outDir", str(output)],
        env={"VITE_API_URL": "http://127.0.0.1:8001"}, timeout=120, cwd=web)
    web_argv = [node, str(vite), "preview", "--config", str(config),
                "--host", "127.0.0.1", "--port", "5174", "--strictPort",
                "--outDir", str(output)]
    _, started = start_child(web_argv, {}, "web", resource, state, handles, cwd=web)
    state.update({"web_start": started, "web_executable": str(Path(node).resolve())})
    wait_http("http://127.0.0.1:5174/")
