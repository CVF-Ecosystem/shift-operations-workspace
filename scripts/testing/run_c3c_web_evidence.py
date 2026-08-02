"""C3c Web Evidence Harness (WO P2C-MUTATION-FULL-UI-C3C-WO-001).

Spawns disposable SQLite DB, seeds test operator user, starts FastAPI backend & Vite preview,
runs static HTTP smoke & Playwright Chromium E2E tests, and cleans up owned resources
(child process trees, temp DB directory, generated test-results/tsbuildinfo artifacts).

P2C-MUTATION-FULL-UI-C3D: `run_harness` now accepts an optional `checkpoint`
label and `playwright_grep` filter so scripts/testing/run_c3d_web_evidence.py
can reuse this exact command construction/readiness/cleanup contract for the
combined operator+supervisor Playwright suite, instead of forking it. Calling
this module directly (checkpoint="C3c") is unchanged: it still runs only the
default Playwright project with no grep filter.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

WORK_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_DIR = os.path.join(WORK_DIR, "apps", "workspace-web")
DIST_DIR = os.path.join(WEB_DIR, "dist")
TEST_RESULTS_DIR = os.path.join(WEB_DIR, "test-results")
TSBUILDINFO = os.path.join(WEB_DIR, "tsconfig.tsbuildinfo")

_SECRET_PATTERN = re.compile(r"(JWT_SECRET_KEY|Authorization|Bearer)\S*", re.IGNORECASE)
_MAX_SANITIZED_LEN = 800


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_for_port(port: int, timeout_sec: float = 15.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    return False


def sanitize_output(text: str) -> str:
    """Redact secrets/paths and bound length before any subprocess text
    reaches JSON evidence. Never place raw stdout/stderr in the receipt."""
    if not text:
        return ""
    redacted = _SECRET_PATTERN.sub("[redacted]", text)
    redacted = redacted.replace(WORK_DIR, "[repo]").replace("\\", "/")
    lines = [line.strip() for line in redacted.splitlines() if line.strip()]
    bounded = " | ".join(lines[-8:])
    return bounded[:_MAX_SANITIZED_LEN]


def kill_process_tree(proc: subprocess.Popen | None, timeout_sec: float = 5.0) -> None:
    """Terminate an owned child and its full descendant tree. `pnpm exec` /
    `powershell -Command` spawn grandchildren (vite, node) that plain
    Popen.terminate() never reaches on Windows, so this always uses taskkill
    against the owned PID tree; falls back to terminate()/kill() if taskkill
    itself is unavailable."""
    if proc is None or proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            capture_output=True, text=True, timeout=timeout_sec
        )
    else:
        proc.terminate()
    try:
        proc.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=timeout_sec)


def remove_owned_artifacts() -> None:
    """Remove only owned generated build/test artifacts, never source."""
    shutil.rmtree(TEST_RESULTS_DIR, ignore_errors=True)
    if os.path.isfile(TSBUILDINFO):
        os.remove(TSBUILDINFO)
    shutil.rmtree(DIST_DIR, ignore_errors=True)


def static_asset_smoke(vite_port: int) -> tuple[bool, list[str]]:
    """Fetch the built HTML and every referenced local JS/CSS asset,
    requiring HTTP 200 for each. Returns (all_ok, checked_asset_paths)."""
    base = f"http://127.0.0.1:{vite_port}"
    with urllib.request.urlopen(f"{base}/") as resp:
        if resp.status != 200:
            return False, []
        html = resp.read().decode("utf-8", errors="replace")
    if "<!doctype html>" not in html.lower():
        return False, []

    asset_paths = sorted(set(re.findall(r'(?:src|href)="(/[^"]+\.(?:js|css))"', html)))
    checked: list[str] = []
    for path in asset_paths:
        try:
            with urllib.request.urlopen(f"{base}{path}", timeout=5) as asset_resp:
                if asset_resp.status != 200:
                    return False, checked
        except OSError:
            return False, checked
        checked.append(path)
    return True, checked


def queue_checkpoint_passed(playwright_passed: bool, queue_checkpoint: str) -> bool:
    """Name the Playwright-owned queue contract without inventing a check.

    C3c/C3d prohibit queue writes. P2-D instead exercises the bounded queue and
    proves cleanup. In both modes the selected browser spec owns the assertion.
    """
    if queue_checkpoint not in {"prohibited", "bounded_exercised_and_cleaned"}:
        return False
    return playwright_passed


def run_harness(as_json: bool = False, checkpoint: str = "C3c", playwright_grep: str | None = None,
                queue_checkpoint: str = "prohibited") -> int:
    tmp_dir = tempfile.mkdtemp(prefix=f"{checkpoint.lower()}_web_evidence_")
    db_path = os.path.join(tmp_dir, f"test_{checkpoint.lower()}.db").replace('\\', '/')
    api_port = find_free_port()
    vite_port = find_free_port()

    api_proc: subprocess.Popen | None = None
    vite_proc: subprocess.Popen | None = None
    success = False
    evidence: dict[str, object] = {
        "checkpoint": checkpoint,
        "api_port": api_port,
        "vite_port": vite_port,
        "static_smoke": False,
        "static_assets_checked": [],
        "playwright_pass": False,
        "queue_checkpoint": queue_checkpoint,
        "queue_checkpoint_pass": False
    }

    try:
        env = os.environ.copy()
        python_paths = [
            WORK_DIR,
            os.path.join(WORK_DIR, "apps", "workspace-api", "src"),
            os.path.join(WORK_DIR, "packages", "cvf-runtime", "src"),
            os.path.join(WORK_DIR, "packages", "operations-ledger", "src"),
            os.path.join(WORK_DIR, "packages", "operations-domain", "src")
        ]
        existing_pp = env.get("PYTHONPATH", "")
        if existing_pp:
            python_paths.append(existing_pp)
        env["PYTHONPATH"] = os.path.pathsep.join(python_paths)
        env["DATABASE_URL"] = f"sqlite:///{db_path}"
        env["JWT_SECRET_KEY"] = f"{checkpoint.lower()}-test-evidence-secret-key-32bytes!!"
        env["VITE_API_URL"] = f"http://127.0.0.1:{api_port}"
        env["VITE_PREVIEW_URL"] = f"http://127.0.0.1:{vite_port}"

        paths_repr = repr(python_paths)

        create_tables_cmd = [
            sys.executable, "-c",
            f"import sys; sys.path[0:0] = {paths_repr}; "
            "from operations_ledger.sql_ledger import make_engine; "
            "from operations_ledger.tables import metadata; "
            f"engine = make_engine('sqlite:///{db_path}'); "
            "metadata.create_all(bind=engine);"
        ]
        res = subprocess.run(create_tables_cmd, cwd=WORK_DIR, env=env, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            evidence["error"] = f"Database tables creation failed: {sanitize_output(res.stderr)}"
            return _finish(evidence, False, as_json)

        seed_cmd = [sys.executable, os.path.join(WORK_DIR, "scripts", "seed_dev_users.py")]
        res = subprocess.run(seed_cmd, cwd=WORK_DIR, env=env, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            evidence["error"] = f"Database seed failed: {sanitize_output(res.stderr)}"
            return _finish(evidence, False, as_json)

        api_cmd = [
            sys.executable, "-m", "uvicorn", "workspace_api.main:app",
            "--host", "127.0.0.1", "--port", str(api_port)
        ]
        api_proc = subprocess.Popen(api_cmd, cwd=WORK_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not wait_for_port(api_port, timeout_sec=20.0):
            evidence["error"] = f"API server readiness timeout on port {api_port}"
            return _finish(evidence, False, as_json)

        build_cmd = [
            "powershell", "-ExecutionPolicy", "Bypass", "-Command",
            f"$env:VITE_API_URL='http://127.0.0.1:{api_port}'; pnpm --dir apps/workspace-web run build"
        ]
        res = subprocess.run(build_cmd, cwd=WORK_DIR, env=env, capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            evidence["error"] = f"Vite build failed: {sanitize_output(res.stderr or res.stdout)}"
            return _finish(evidence, False, as_json)

        preview_cmd = [
            "powershell", "-ExecutionPolicy", "Bypass", "-Command",
            f"pnpm --dir apps/workspace-web exec vite preview --port {vite_port} --host 127.0.0.1"
        ]
        vite_proc = subprocess.Popen(preview_cmd, cwd=WORK_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not wait_for_port(vite_port, timeout_sec=20.0):
            evidence["error"] = f"Vite preview readiness timeout on port {vite_port}"
            return _finish(evidence, False, as_json)

        smoke_ok, checked_assets = static_asset_smoke(vite_port)
        evidence["static_smoke"] = smoke_ok
        evidence["static_assets_checked"] = checked_assets
        if not smoke_ok:
            evidence["error"] = "Static asset smoke failed: built entry or a referenced local JS/CSS asset did not return HTTP 200"
            return _finish(evidence, False, as_json)

        pw_test_cmd = "pnpm --dir apps/workspace-web exec playwright test"
        if playwright_grep:
            escaped_grep = playwright_grep.replace("'", "''")
            pw_test_cmd += f" --grep '{escaped_grep}'"
        pw_cmd = [
            "powershell", "-ExecutionPolicy", "Bypass", "-Command",
            f"$env:VITE_PREVIEW_URL='http://127.0.0.1:{vite_port}'; {pw_test_cmd}"
        ]
        pw_res = subprocess.run(pw_cmd, cwd=WORK_DIR, env=env, capture_output=True, text=True, timeout=600)
        evidence["playwright_pass"] = pw_res.returncode == 0
        evidence["queue_checkpoint_pass"] = queue_checkpoint_passed(
            bool(evidence["playwright_pass"]), queue_checkpoint
        )
        if pw_res.returncode != 0:
            evidence["playwright_failure_summary"] = sanitize_output(pw_res.stderr or pw_res.stdout)

        success = bool(smoke_ok and evidence["playwright_pass"] and evidence["queue_checkpoint_pass"])
        return _finish(evidence, success, as_json)

    finally:
        kill_process_tree(vite_proc)
        kill_process_tree(api_proc)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        remove_owned_artifacts()


def _finish(evidence: dict[str, object], success: bool, as_json: bool) -> int:
    if as_json:
        print(json.dumps(evidence, indent=2))
    else:
        print(f"{evidence['checkpoint']} Web Evidence Result: {'PASS' if success else 'FAIL'}")
        if not success:
            print(json.dumps(evidence, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output evidence as JSON")
    args = parser.parse_args()
    sys.exit(run_harness(as_json=args.json))
