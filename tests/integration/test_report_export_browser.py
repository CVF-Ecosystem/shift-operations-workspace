"""Run explicitly from project root for disposable real-API/browser proof.

Invocation: .venv/Scripts/python.exe tests/integration/test_report_export_browser.py
No automatic browser/server/provider action occurs during pytest collection.
Outputs synthetic evidence under ignored .venv/p5a-browser-*; no real credentials.
"""

from test_report_export_browser_support import (
    BROWSER_JS,
    isolated_environment,
    selected_sources,
    verify_download_bytes,
)


def main():
    import hashlib
    import json
    import os
    import socket
    import sqlite3
    import subprocess
    import sys
    import time
    import tomllib
    from pathlib import Path

    import httpx

    ROOT = Path.cwd()
    OUT = ROOT / ".venv" / f"p5a-browser-{time.time_ns()}"
    OUT.mkdir()
    PY = Path(sys.executable)
    (OUT / "browser.cjs").write_text(BROWSER_JS, encoding="utf-8")
    env = isolated_environment(ROOT)
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    paths = [str(ROOT / p) for p in config["tool"]["pytest"]["ini_options"]["pythonpath"]]
    for p in reversed(paths):
        sys.path.insert(0, p)

    def port():
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def state():
        with sqlite3.connect(OUT / "browser.sqlite") as c:
            names = [
                r[0]
                for r in c.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
            ]
            data = {
                n: sorted([list(r) for r in c.execute('SELECT * FROM "' + n + '"')], key=repr)
                for n in names
            }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        ).hexdigest()

    def stop(p):
        if p and p.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(p.pid), "/T", "/F"],
                check=False,
                capture_output=True,
                timeout=15,
            )
            p.wait(timeout=15)

    api_port, web_port = port(), port()
    env.update(
        PYTHONPATH=os.pathsep.join(paths),
        DATABASE_URL="sqlite:///" + (OUT / "browser.sqlite").as_posix(),
        JWT_SECRET_KEY="p5a-disposable-review-only-20261023-32bytes!",
        AI_MODE="NO_AI",
        APP_ENV="development",
        VITE_API_URL=f"http://127.0.0.1:{api_port}",
        P5A_WEB=f"http://127.0.0.1:{web_port}",
        P5A_PROOF_DIR=str(OUT),
    )
    node_dir = Path(os.environ["LOCALAPPDATA"]) / "nvm/v22.14.0"
    assert (node_dir / "node.exe").is_file()
    env["PATH"] = str(node_dir) + os.pathsep + env["PATH"]
    os.environ.update({k: env[k] for k in ["DATABASE_URL", "JWT_SECRET_KEY", "AI_MODE", "APP_ENV"]})
    from operations_ledger.sql_ledger import make_engine
    from operations_ledger.tables import metadata

    engine = make_engine(env["DATABASE_URL"])
    metadata.create_all(engine)
    engine.dispose()
    seed = subprocess.run(
        [str(PY), "scripts/seed_dev_users.py"],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        timeout=40,
    )
    assert seed.returncode == 0, "Synthetic seed failed"
    api = web = None
    receipt = {"claim": "Local actual-format/browser evidence only; no CVF live governance proof"}
    receipt["source_hashes"] = selected_sources(ROOT)
    receipt["browser_script_sha256"] = hashlib.sha256(
        (OUT / "browser.cjs").read_bytes()
    ).hexdigest()
    try:
        with (OUT / "api.log").open("w") as log:
            api = subprocess.Popen(
                [
                    str(PY),
                    "-m",
                    "uvicorn",
                    "workspace_api.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(api_port),
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=log,
            )
        client = httpx.Client(base_url=env["VITE_API_URL"], timeout=25)
        for _ in range(150):
            try:
                if client.get("/health").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        else:
            raise AssertionError("API readiness failure")

        def call(method, path, **kw):
            r = client.request(method, path, **kw)
            assert r.is_success, (method, path, r.status_code, r.text[:300])
            return r.json()

        token = call("POST", "/auth/login", json={"username": "sup1", "password": "sup1-devpass"})[
            "access_token"
        ]
        client.headers["Authorization"] = "Bearer " + token
        shift = call(
            "POST",
            "/shifts",
            params={
                "name": "P5-A — Ca kiểm chứng tải báo cáo",
                "starts_at": "2026-10-23T00:00:00Z",
                "ends_at": "2026-10-23T08:00:00Z",
            },
        )
        sid = shift["shift_id"]
        ref = {"source_type": "synthetic", "source_id": "p5a-independent-browser-reference"}
        event = call(
            "POST",
            "/events",
            json={
                "shift_id": sid,
                "event_type": "shift_update",
                "title": "Xác nhận ca trực — Tiếng Việt",
                "description": "Dữ liệu tổng hợp: <b>không phải HTML</b> và =1+1",
                "risk_class": "R0",
                "evidence": [ref],
            },
        )
        call(
            "POST",
            f"/events/{event['event_id']}/confirm",
            json={"expected_version": event["version"]},
        )
        call(
            "POST",
            "/customer-requests",
            json={
                "shift_id": sid,
                "customer_id": "Khách hàng tổng hợp",
                "summary": "Yêu cầu hỗ trợ bến cảng",
                "details": '=HYPERLINK("https://example.invalid","literal")',
            },
        )
        call(
            "POST",
            "/tasks",
            json={
                "shift_id": sid,
                "title": "+Công việc cần bàn giao",
                "description": "Chuỗi dài: " + "abcdef" * 70,
                "risk_class": "R0",
                "evidence": [ref],
            },
        )
        call(
            "POST",
            "/incidents",
            json={
                "shift_id": sid,
                "summary": "Sự cố tổng hợp — đã ghi nhận",
                "risk_class": "R0",
                "evidence": [ref],
            },
        )
        dest = call(
            "POST",
            "/shifts",
            params={
                "name": "P5-A — Ca nhận tổng hợp",
                "starts_at": "2026-10-23T08:00:00Z",
                "ends_at": "2026-10-23T16:00:00Z",
            },
        )
        call("POST", "/handovers", json={"from_shift_id": sid, "to_shift_id": dest["shift_id"]})
        call("POST", f"/shifts/{sid}/close", json={"expected_version": shift["version"]})
        first = call("POST", "/reports", json={"shift_id": sid})
        current = call(
            "POST",
            f"/reports/{first['report_id']}/versions",
            json={
                "expected_version": first["version"],
                "expected_status": first["status"],
                "reason": "Synthetic history proof",
            },
        )
        history = call("GET", "/reports", params={"shift_id": sid, "include_history": "true"})
        (OUT / "persisted-reports.json").write_text(
            json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        env["P5A_SHIFT_ID"] = sid
        env["P5A_REPORT_ID"] = current["report_id"]
        env["P5A_HISTORICAL_ID"] = first["report_id"]
        receipt["before_digest"] = state()
        with (OUT / "vite.log").open("w") as log:
            web = subprocess.Popen(
                [
                    "node",
                    "apps/workspace-web/node_modules/vite/bin/vite.js",
                    "apps/workspace-web",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(web_port),
                    "--strictPort",
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=log,
            )
        for _ in range(100):
            try:
                if httpx.get(env["P5A_WEB"]).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        else:
            raise AssertionError("Web readiness failure")
        run = subprocess.run(
            ["node", str(OUT / "browser.cjs")],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
        )
        (OUT / "browser-output.log").write_text(run.stdout + "\n" + run.stderr, encoding="utf-8")
        assert run.returncode == 0, "Browser proof failed; inspect bounded local log"
        receipt["browser"] = json.loads(run.stdout)
        receipt["after_digest"] = state()
        assert receipt["before_digest"] == receipt["after_digest"]
        verify_download_bytes(OUT, history, receipt["browser"]["downloads"])
        assert receipt["source_hashes"] == selected_sources(ROOT)
        final_script_hash = hashlib.sha256((OUT / "browser.cjs").read_bytes()).hexdigest()
        assert receipt["browser_script_sha256"] == final_script_hash
        receipt["result"] = "PASS"
        receipt["evidence_directory"] = str(OUT)
        receipt["python"] = sys.version.split()[0]
        receipt["node"] = subprocess.check_output(
            [str(node_dir / "node.exe"), "--version"], text=True
        ).strip()
        print(json.dumps(receipt, ensure_ascii=False))
    finally:
        stop(web)
        stop(api)
        receipt["owned_processes_stopped"] = all(
            p is None or p.poll() is not None for p in [web, api]
        )
        (OUT / "browser-receipt.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
