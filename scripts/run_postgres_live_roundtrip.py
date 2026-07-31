#!/usr/bin/env python3
"""One-shot disposable PostgreSQL 16 live round-trip runner.

P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26 (SPEC section 3, ADR section 2).
Starts a uniquely named PostgreSQL 16 container on a dynamic loopback port -
no bind/named volume passed to `docker run`; the image's own declared VOLUME
still creates an anonymous one per container, verified gone after cleanup
too. Applies migrations 001-004 twice (never metadata.create_all()), runs
the opt-in live suite, then always removes that container. No PRE-EXISTING
container/image/volume/database is touched; credential/URL never printed.

Failure output is always sanitized (PG-REV-F2/F3/F6); cleanup targets only a
container this run created. `wait_ready` requires STABLE polls (image
restarts once after init scripts); `wait_ready_via_database` (Finding 3)
then proves the FINAL server is reachable on the mapped port - never via
raw driver text (Finding 2: fixed message + exception class name only).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIRS = (
    "packages/operations-ledger/src", "packages/cvf-runtime/src",
    "packages/operations-domain/src", "apps/workspace-api/src", "scripts",
)
for _rel in _SRC_DIRS:
    sys.path.insert(0, str(REPO_ROOT / _rel))

IMAGE = "postgres:16-alpine"
CONTAINER_PREFIX = "cvf-pg-live-"
POSTGRES_DB = "cvf_live_roundtrip"
POSTGRES_USER = "cvf_live"
READY_TIMEOUT_S = 60
LIVE_URL_ENV = "LIVE_POSTGRES_DATABASE_URL"


class LiveRoundTripError(RuntimeError):
    """Fail-closed error for any prerequisite/orchestration/cleanup failure."""


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def redact(url: str) -> str:
    """Never let a credential or full database URL reach output (SPEC R4)."""
    return re.sub(r"//[^/]*@", "//<redacted>@", url)


# Finding 2: scrubs ANY postgresql(+psycopg):// URI anywhere in text, not
# just an exact match against one known `database_url` (psycopg's own DSN
# form differs from SQLAlchemy's `+psycopg` variant).
_PG_URI = re.compile(r"postgresql(?:\+psycopg)?://[^\s'\"]*")


def sanitize_output(text: str, *, password: str, database_url: str) -> str:
    """Scrub the password and any PostgreSQL URI from output (SPEC R4/R15/R32)."""
    if not text:
        return text
    if password:
        text = text.replace(password, "<redacted-password>")
    if database_url:
        text = text.replace(database_url, redact(database_url))
    return _PG_URI.sub("<redacted-database-url>", text)


def check_docker_daemon() -> str:
    result = _run(["docker", "info", "--format", "{{.ServerVersion}}"])
    if result.returncode != 0:
        raise LiveRoundTripError("BLOCKED_DOCKER_DAEMON_UNAVAILABLE")
    return result.stdout.strip()


def check_psycopg() -> str:
    import psycopg
    return psycopg.__version__


def ensure_image(image: str = IMAGE) -> str:
    inspect = _run(["docker", "image", "inspect", image, "--format", "{{.Id}}"])
    if inspect.returncode != 0:
        pulled = _run(["docker", "pull", image])
        if pulled.returncode != 0:
            raise LiveRoundTripError(f"failed to pull {image}: {pulled.stderr.strip()}")
        inspect = _run(["docker", "image", "inspect", image, "--format", "{{.Id}}"])
        if inspect.returncode != 0:
            raise LiveRoundTripError(f"image {image} still not present after pull")
    return inspect.stdout.strip()


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def new_container_name() -> str:
    return f"{CONTAINER_PREFIX}{uuid.uuid4().hex[:12]}"


def container_exists(name: str) -> bool:
    result = _run(["docker", "ps", "-a", "--filter", f"name=^/{name}$", "--format", "{{.Names}}"])
    return name in result.stdout.split()


def docker_run_cmd(name: str, port: int, password: str) -> list[str]:
    """No -v/--mount (SPEC R2), loopback-only publish."""
    return [
        "docker", "run", "-d", "--name", name,
        "-e", f"POSTGRES_DB={POSTGRES_DB}", "-e", f"POSTGRES_USER={POSTGRES_USER}",
        "-e", f"POSTGRES_PASSWORD={password}", "-p", f"127.0.0.1:{port}:5432", IMAGE,
    ]


def start_container(name: str, port: int, password: str) -> None:
    """Raises before invoking `docker run` on a name collision (SPEC R16/AC-26)."""
    if container_exists(name):
        raise LiveRoundTripError(f"container name collision, refusing to reuse: {name}")
    result = _run(docker_run_cmd(name, port, password))
    if result.returncode != 0:
        raise LiveRoundTripError(f"docker run failed: {result.stderr.strip()}")


def _pg_isready(name: str) -> bool:
    return _run(["docker", "exec", name, "pg_isready", "-U", POSTGRES_USER, "-d", POSTGRES_DB]).returncode == 0


def wait_ready(name: str, timeout_s: int = READY_TIMEOUT_S, *, stability_checks: int = 3) -> None:
    """F6: one `pg_isready` success is not proof - see `wait_ready_via_database`."""
    deadline = time.monotonic() + timeout_s
    consecutive = 0
    while time.monotonic() < deadline:
        if _pg_isready(name):
            consecutive += 1
            if consecutive >= stability_checks:
                return
        else:
            consecutive = 0
        time.sleep(1)
    raise LiveRoundTripError(f"PostgreSQL did not become durably ready within {timeout_s}s")


def wait_ready_via_database(database_url: str, timeout_s: int = READY_TIMEOUT_S) -> None:
    """Finding 3: proves readiness via the mapped port/database (psycopg
    wants a plain DSN, not `+psycopg`). Finding 2: the raw exception is
    NEVER surfaced (embeds the full DSN) - only a fixed message + class name."""
    import psycopg
    conninfo = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    deadline = time.monotonic() + timeout_s
    last_error_class = "no attempt made"
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(conninfo, connect_timeout=3) as conn, conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return
        except Exception as exc:  # noqa: BLE001 - only the class name ever escapes
            last_error_class = type(exc).__name__
            time.sleep(1)
    raise LiveRoundTripError(f"database not reachable on the mapped port within {timeout_s}s ({last_error_class})")


def container_volumes(name: str) -> list[str]:
    """Anonymous volumes captured live so cleanup can verify removal (SPEC R16)."""
    fmt = '{{range .Mounts}}{{if eq .Type "volume"}}{{.Name}} {{end}}{{end}}'
    result = _run(["docker", "inspect", name, "--format", fmt])
    return result.stdout.split() if result.returncode == 0 else []


def volume_exists(name: str) -> bool:
    return _run(["docker", "volume", "inspect", name]).returncode == 0


def remove_container(name: str, volumes: list[str]) -> tuple[bool, list[str]]:
    """(rm_succeeded, volumes_still_present) - both must be (True, []) (SPEC R16/AC-27)."""
    result = _run(["docker", "rm", "-f", "-v", name])
    still_present = [v for v in volumes if volume_exists(v)]
    return result.returncode == 0, still_present


def parse_migration_counts(output: str) -> tuple[int, int]:
    m = re.search(r"done - (\d+) statement\(s\) applied, (\d+) already present", output)
    if not m:
        raise LiveRoundTripError(f"could not parse migration summary: {output[-300:]!r}")
    return int(m.group(1)), int(m.group(2))


def apply_migrations_twice(database_url: str) -> list[dict]:
    from apply_migrations import apply_all
    summaries = []
    for attempt in ("first", "reapply"):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            apply_all(database_url)
        applied, skipped = parse_migration_counts(buf.getvalue())
        summaries.append({"attempt": attempt, "applied": applied, "skipped": skipped})
    return summaries


# Each vertical's live module is coherent but separate; all run in one pass.
LIVE_SUITE_TARGETS = (
    "tests/integration/test_sql_ledger_postgres_live.py",
    "tests/integration/test_incident_postgres_live.py",
    "tests/integration/test_handover_postgres_live.py",
    "tests/integration/test_shift_create_postgres_live.py",
    "tests/integration/test_message_postgres_live.py",
    "tests/integration/test_report_postgres_live.py",
)

def run_live_suite(database_url: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env[LIVE_URL_ENV] = database_url
    return _run([sys.executable, "-m", "pytest", "-v", *LIVE_SUITE_TARGETS], cwd=str(REPO_ROOT), env=env)


def run_once(database_url: str, container_name: str, port: int, password: str) -> dict:
    """Cleanup runs only when `start_container` actually created this
    container - never on a collision or failed `docker run` (SPEC R16/AC-26)."""
    summary: dict = {"image": IMAGE, "container_name": container_name, "host_port": port}
    created = False
    volumes: list[str] = []
    failure: str | None = None
    try:
        start_container(container_name, port, password)
        created = True
        volumes = container_volumes(container_name)
        wait_ready(container_name)
        wait_ready_via_database(database_url)
        summary["migrations"] = apply_migrations_twice(database_url)
        result = run_live_suite(database_url)
        stdout = sanitize_output(result.stdout, password=password, database_url=database_url)
        stderr = sanitize_output(result.stderr, password=password, database_url=database_url)
        summary["live_suite_returncode"] = result.returncode
        summary["live_suite_tail"] = "\n".join(stdout.splitlines()[-60:])
        if result.returncode != 0:
            print(stdout)
            print(stderr, file=sys.stderr)
            failure = "live suite did not pass"
    except Exception:
        # Broad on purpose (PG-REV-F6): sanitize before reaching output - a
        # raw driver/SQLAlchemy exception repr can leak the DSN.
        failure = sanitize_output(traceback.format_exc(), password=password, database_url=database_url)
    finally:
        if created:
            rm_ok, still_present = remove_container(container_name, volumes)
            summary["anonymous_volumes_captured"] = volumes
            summary["anonymous_volumes_still_present"] = still_present
            summary["container_absent_after_cleanup"] = (
                rm_ok and not container_exists(container_name) and not still_present
            )
            if not rm_ok:
                failure = failure or "docker rm -f -v did not report success"
            elif still_present:
                failure = failure or f"anonymous volume(s) survived cleanup: {still_present}"
        else:
            summary["container_absent_after_cleanup"] = True
            summary["cleanup_skipped_reason"] = "container was never created by this run (collision or failed docker run)"
        summary["failure"] = failure
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Disposable PostgreSQL 16 live round-trip")
    parser.add_argument("--json", action="store_true", help="print a machine-readable summary")
    args = parser.parse_args(argv)

    summary: dict = {
        "docker_server_version": check_docker_daemon(),
        "psycopg_version": check_psycopg(),
        "image_id": ensure_image(),
    }
    container_name = new_container_name()
    port = free_loopback_port()
    password = secrets.token_urlsafe(24)
    database_url = f"postgresql+psycopg://{POSTGRES_USER}:{password}@127.0.0.1:{port}/{POSTGRES_DB}"

    summary.update(run_once(database_url, container_name, port, password))

    print(json.dumps(summary, indent=2) if args.json else "\n".join(f"{k}: {v}" for k, v in summary.items() if k != "live_suite_tail"))
    return 0 if not summary.get("failure") and summary.get("container_absent_after_cleanup") else 1


if __name__ == "__main__":
    raise SystemExit(main())
