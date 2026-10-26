#!/usr/bin/env python3
"""One owned disposable PostgreSQL rehearsal for the P5-A2 PUBLIC fixture."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_postgres_live_roundtrip as base  # noqa: E402

TARGET = "tests/integration/test_p5a2_docker_backend.py"


def local_image_id() -> str:
    """Image acquisition belongs to admitted Stage B, outside this runner."""
    result = base._run(["docker", "image", "inspect", base.IMAGE, "--format", "{{.Id}}"])
    if result.returncode or not result.stdout.strip():
        raise base.LiveRoundTripError("BLOCKED_WITH_REASON: PostgreSQL image absent")
    return result.stdout.strip()


def container_image_id(name: str) -> str:
    result = base._run(["docker", "inspect", name, "--format", "{{.Image}}"])
    if result.returncode or not result.stdout.strip():
        raise base.LiveRoundTripError("container image identity unavailable")
    return result.stdout.strip()


def server_version(name: str) -> str:
    result = base._run(["docker", "exec", name, "psql", "-U", base.POSTGRES_USER,
                        "-d", base.POSTGRES_DB, "-tAc", "SHOW server_version"])
    if result.returncode or not result.stdout.strip():
        raise base.LiveRoundTripError("PostgreSQL server version unavailable")
    return result.stdout.strip()


def run_target(database_url: str) -> subprocess.CompletedProcess:
    # No ambient provider/API keys or .env contents enter the child.
    allowed = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "TMPDIR", "VIRTUAL_ENV")
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    env[base.LIVE_URL_ENV] = database_url
    env["PYTHONNOUSERSITE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", TARGET],
        cwd=base.REPO_ROOT, env=env, capture_output=True, text=True,
    )


def run_once(database_url: str, name: str, port: int, password: str, image_id: str) -> dict:
    summary: dict = {"image": base.IMAGE, "image_id": image_id, "container_name": name, "host_port": port}
    created = False
    volumes: list[str] = []
    failure: str | None = None
    try:
        base.start_container(name, port, password)
        created = True
        actual_image = container_image_id(name)
        summary["container_image_id"] = actual_image
        if actual_image != image_id:
            raise base.LiveRoundTripError("container image differs from inspected image")
        volumes = base.container_volumes(name)
        if not volumes:
            raise base.LiveRoundTripError("anonymous volume identity unavailable")
        base.wait_ready(name)
        base.wait_ready_via_database(database_url)
        summary["server_version"] = server_version(name)
        migration_files = sorted(p.name for p in (base.REPO_ROOT / "database" / "migrations").glob("*.sql"))
        if any(not any(name.startswith(f"{n:03d}_") for name in migration_files) for n in range(1, 12)):
            raise base.LiveRoundTripError("required migrations 001-011 absent")
        summary["migration_files"] = migration_files
        summary["migrations"] = base.apply_migrations_twice(database_url)
        result = run_target(database_url)
        summary["target_returncode"] = result.returncode
        output = base.sanitize_output(result.stdout + "\n" + result.stderr,
                                      password=password, database_url=database_url)
        summary["target_tail"] = "\n".join(output.splitlines()[-60:])
        if result.returncode or "1 passed" not in result.stdout or "skipped" in result.stdout:
            failure = "P5-A2 SQL target failed or skipped"
    except Exception:
        failure = base.sanitize_output(traceback.format_exc(), password=password,
                                       database_url=database_url)
    finally:
        if created:
            try:
                rm_ok, still = base.remove_container(name, volumes)
                absent = not base.container_exists(name)
                summary["anonymous_volumes_captured"] = volumes
                summary["anonymous_volumes_still_present"] = still
                summary["container_absent_after_cleanup"] = rm_ok and absent and bool(volumes) and not still
                if not summary["container_absent_after_cleanup"]:
                    failure = failure or "owned resource cleanup incomplete"
            except Exception:
                summary["container_absent_after_cleanup"] = False
                failure = failure or base.sanitize_output(traceback.format_exc(),
                                                          password=password, database_url=database_url)
        else:
            summary["container_absent_after_cleanup"] = True
            summary["cleanup_skipped_reason"] = "container creation not confirmed; no deletion authority"
    summary["failure"] = failure
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        docker = base.check_docker_daemon()
        driver = base.check_psycopg()
        image_id = local_image_id()
    except Exception as exc:
        # Prerequisite errors never include a generated URL/password.
        summary = {"failure": f"BLOCKED_WITH_REASON: {type(exc).__name__}",
                   "container_absent_after_cleanup": True}
        print(json.dumps(summary) if args.json else summary["failure"])
        return 1
    name = base.new_container_name()
    port = base.free_loopback_port()
    password = secrets.token_urlsafe(24)
    url = f"postgresql+psycopg://{base.POSTGRES_USER}:{password}@127.0.0.1:{port}/{base.POSTGRES_DB}"
    summary = {"docker_server_version": docker, "psycopg_version": driver}
    summary.update(run_once(url, name, port, password, image_id))
    print(json.dumps(summary, indent=2) if args.json else
          "\n".join(f"{k}: {v}" for k, v in summary.items() if k != "target_tail"))
    return 0 if not summary["failure"] and summary["container_absent_after_cleanup"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
