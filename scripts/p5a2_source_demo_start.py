"""Later Stage B entry point: create one owned synthetic local profile."""
from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

from p5a2_source_demo_common import (COMPOSE, CONTAINER, OWNER, PORTS, PROFILE,
                                     ROOT, RUNTIME, VOLUME, child_env, digest, fail,
                                     inspect, labels_match, owner_lock, process_start,
                                     resource_record, run, write_owner)
from p5a2_source_demo_preflight import prerequisites


def private_file(path: Path, content: str) -> None:
    if sys.platform == "win32":
        user = os.environ.get("USERNAME")
        if not user:
            raise fail("LOCAL_USER_UNKNOWN")
        run(["icacls", str(path.parent), "/inheritance:r", "/grant:r", f"{user}:(OI)(CI)F"])
    else:
        path.parent.chmod(0o700)
    path.write_text(content, encoding="utf-8")
    if sys.platform == "win32":
        run(["icacls", str(path), "/inheritance:r", "/grant:r", f"{user}:F"])
    else:
        path.chmod(0o600)


def start_child(argv: list[str], env: dict[str, str], kind: str,
                resource: dict, state: dict, handles: dict,
                cwd: Path = ROOT) -> tuple[int, str]:
    flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
             if sys.platform == "win32" else 0)
    proc = subprocess.Popen(argv, cwd=cwd, env=child_env(env), stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=flags)
    key = kind + "_pid"
    handles[kind] = proc
    resource[key] = proc.pid
    state["creation_trail"].append({"kind": kind, "id": proc.pid})
    for _ in range(20):
        if proc.poll() is not None:
            resource[key] = None
            state["cleanup_trail"].append({"kind": kind, "id": proc.pid, "result": "EXITED"})
            raise fail("CHILD_EXITED")
        try:
            return proc.pid, process_start(proc.pid)
        except RuntimeError:
            time.sleep(0.1)
    try:
        proc.terminate()
        proc.wait(timeout=5)
        resource[key] = None
        state["cleanup_trail"].append({"kind": kind, "id": proc.pid, "result": "TERMINATED_BY_HANDLE"})
    except (OSError, subprocess.TimeoutExpired):
        state["unverified_child"] = kind
    raise fail("CHILD_IDENTITY_UNAVAILABLE")


def wait_db(dsn: str) -> str:
    import psycopg
    for _ in range(40):
        try:
            with psycopg.connect(dsn, connect_timeout=1) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version(), current_database()")
                    version, database = cur.fetchone()
                    if "PostgreSQL 16" not in version or database != "shiftops_p5a2_source_demo":
                        raise fail("DB_IDENTITY_INVALID")
                    cur.execute("SELECT system_identifier FROM pg_control_system()")
                    system_id = cur.fetchone()[0]
                    return digest({"database": database, "system_identifier": str(system_id)})
        except psycopg.OperationalError:
            time.sleep(0.5)
    raise fail("DB_HEALTH_FAILED")


def wait_http(url: str) -> None:
    for _ in range(40):
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise fail("HTTP_HEALTH_FAILED")


def start() -> dict:
    with owner_lock():
        check = prerequisites()
        nonce = secrets.token_hex(32)
        password = secrets.token_urlsafe(36)
        viewer = secrets.token_urlsafe(36)
        jwt = secrets.token_urlsafe(48)
        secret_path = RUNTIME / "secrets.json"
        if secret_path.exists():
            raise fail("OWNER_CONFLICT")
        image_id = check["image_id"]
        dsn = f"postgresql+psycopg://source_demo:{quote(password, safe='')}@127.0.0.1:5433/shiftops_p5a2_source_demo"
        db_fingerprint = None
        state = {"profile_id": PROFILE, "owner_nonce": nonce,
                 "image_id": image_id,
                 "secret_ref": str(secret_path), "creation_trail": [], "cleanup_trail": []}
        resource = {"volume_id": None, "container_id": None,
                    "api_pid": None, "web_pid": None}
        handles: dict[str, subprocess.Popen] = {}
        env = {"P5A2_DB_PASSWORD": password, "P5A2_OWNER_NONCE": nonce,
               "COMPOSE_DISABLE_ENV_FILE": "1"}
        try:
            private_file(secret_path, json.dumps({"db_password": password,
                                                   "viewer_password": viewer,
                                                   "jwt_secret": jwt}))
            # Preflight is repeated under the lock immediately before creation.
            if any(inspect(k, n) is not None for k, n in (("container", CONTAINER), ("volume", VOLUME))):
                raise fail("OWNER_CONFLICT")
            run(["docker", "compose", "--env-file", os.devnull, "-f", str(COMPOSE), "up", "-d", "--no-build",
                 "--no-recreate", "--pull", "never"], env=env, timeout=90)
            volume = inspect("volume", VOLUME)
            container = inspect("container", CONTAINER)
            if volume is None or not labels_match(volume, nonce):
                raise fail("VOLUME_OWNERSHIP_UNVERIFIED")
            resource["volume_id"] = VOLUME
            state["creation_trail"].append({"kind": "volume", "id": VOLUME})
            if container is None or not labels_match(container, nonce):
                raise fail("CONTAINER_OWNERSHIP_UNVERIFIED")
            cid = container.get("Id")
            if not isinstance(cid, str) or len(cid) != 64 or container.get("Image") != "sha256:" + image_id:
                raise fail("CONTAINER_IDENTITY_INVALID")
            resource["container_id"] = cid
            state["creation_trail"].append({"kind": "container", "id": cid})
            db_fingerprint = wait_db(dsn.replace("postgresql+psycopg://", "postgresql://", 1))
            base_env = {"DATABASE_URL": dsn, "JWT_SECRET_KEY": jwt,
                        "AI_MODE": "NO_AI", "P5A2_SOURCE_DEMO_PROFILE": PROFILE,
                        "PROACTIVE_SOURCE_INSTANCE_ID": PROFILE, "APP_ENV": "source_demo",
                        "CORS_ALLOWED_ORIGINS": "http://127.0.0.1:5174",
                        "PYTHONPATH": str(ROOT / "apps/workspace-api/src")}
            run([sys.executable, "scripts/apply_migrations.py"], env=base_env, timeout=90)
            run([sys.executable, "-m", "workspace_api.demo.seed"],
                env={**base_env, "P5A2_SOURCE_DEMO_VIEWER_PASSWORD": viewer}, timeout=90)
            state["schema_seed_verified"] = True
            # The profile app factory checks the isolated marker before normal imports.
            api_argv = [sys.executable, "-m", "uvicorn", "workspace_api.demo.app:create_app",
                        "--factory", "--host", "127.0.0.1", "--port", "8001"]
            api_pid, api_start = start_child(api_argv, base_env, "api", resource, state, handles)
            state["api_start"] = api_start
            state["api_executable"] = str(Path(sys.executable).resolve())
            wait_http("http://127.0.0.1:8001/health")
            web = ROOT / "apps/workspace-web"
            node = check["node_path"]
            vite = web / "node_modules/vite/bin/vite.js"
            config = web / "vite.source-demo.config.ts"
            out = ROOT / ".venv/p5a2-source-demo-web"
            run([node, str(vite), "build", "--config", str(config), "--outDir", str(out)],
                env={"VITE_API_URL": "http://127.0.0.1:8001"}, timeout=120,
                cwd=web)
            web_argv = [node, str(vite), "preview", "--config", str(config),
                        "--host", "127.0.0.1", "--port", "5174", "--strictPort",
                        "--outDir", str(out)]
            web_pid, web_start = start_child(web_argv, {}, "web", resource, state, handles, cwd=web)
            state["web_start"] = web_start
            state["web_executable"] = str(Path(node).resolve())
            wait_http("http://127.0.0.1:5174/")
            record = resource_record("OWNED_RUNNING", nonce, **resource,
                                     image_id=image_id, db_fingerprint=db_fingerprint)
            state.update(record)
            write_owner(state)
            return {**record, "owner_record_digest": digest(state),
                    "owner_record_path": str(OWNER)}
        except Exception as exc:
            reason = "SEED_FAILED" if state.get("schema_seed_verified") is not True else "HEALTH_FAILED"
            # Reverse only exact owned resources. Retain the named volume and trail.
            cleanup_blocked = False
            for kind, key in (("web", "web_pid"), ("api", "api_pid")):
                pid = resource[key]
                if pid is not None:
                    handle = handles.get(kind)
                    if handle is None or handle.pid != pid:
                        cleanup_blocked = True
                        reason = "CLEANUP_FAILED"
                        break
                    try:
                        if handle.poll() is None:
                            handle.terminate()
                            handle.wait(timeout=5)
                        state["cleanup_trail"].append({"kind": kind, "id": pid})
                        resource[key] = None
                    except (OSError, subprocess.TimeoutExpired):
                        cleanup_blocked = True
                        reason = "CLEANUP_FAILED"
                        break
            current = inspect("container", CONTAINER)
            if not cleanup_blocked and current is not None and labels_match(current, nonce) and resource["container_id"] == current.get("Id"):
                try:
                    run(["docker", "stop", resource["container_id"]], timeout=30)
                    run(["docker", "rm", resource["container_id"]], timeout=30)
                    state["cleanup_trail"].append({"kind": "container", "id": resource["container_id"]})
                    resource["container_id"] = None
                except (RuntimeError, OSError, subprocess.TimeoutExpired):
                    reason = "CLEANUP_FAILED"
            # Keep every remaining verified resource and exact trail for recovery.
            for kind, name, key in (("volume", VOLUME, "volume_id"),
                                    ("container", CONTAINER, "container_id")):
                resource[key] = None
                item = inspect(kind, name)
                if item is not None and labels_match(item, nonce):
                    resource[key] = name if kind == "volume" else item["Id"]
            if any(v is not None for v in resource.values()):
                state.update(resource_record("PARTIAL_OWNED_FAILURE", nonce, **resource,
                                             image_id=image_id, reason=reason))
                state["failure_class"] = type(exc).__name__
                write_owner(state)
            else:
                secret_path.unlink(missing_ok=True)
            raise fail("START_FAILED_OWNERSHIP_RECORDED") from None


if __name__ == "__main__":
    try:
        print(json.dumps(start(), sort_keys=True))
    except Exception:
        print(json.dumps({"status": "REFUSED_OR_FAILED", "reason": "START_FAILED"}))
        raise SystemExit(1)
