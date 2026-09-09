#!/usr/bin/env python3
"""One-shot disposable PostgreSQL 16 live round-trip runner, scoped to
P4-E (completion-rereview R4). Reuses ``run_postgres_live_roundtrip.py``'s
exact security-sensitive functions (docker/psycopg checks, unique
container/dynamic loopback port/ephemeral credential, no bind/named
volume, sanitized output, cleanup-only-what-this-run-created) unchanged -
this module only supplies P4-E's own live-suite target list and applies
migrations 001-011 (every migration, not just 001-004) since P4-E depends
on the users/shifts/incidents/assignments tables migrations 001-010
establish."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

import run_postgres_live_roundtrip as base  # noqa: E402

P4E_LIVE_SUITE_TARGETS = (
    "tests/integration/test_p4e_postgres_live.py",
    "tests/integration/test_p4e_postgres_live_claim_cas.py",
)


class LocalImageMissing(base.LiveRoundTripError):
    """completion-rereview2 F4: distinct from every other
    ``LiveRoundTripError`` - signals BLOCKED_WITH_REASON before any
    container/network action, never a generic failure."""


def ensure_local_image_only(image: str = base.IMAGE) -> str:
    """completion-rereview2 F4: path 102 must fail closed when the local
    ``postgres:16-alpine`` image is absent - it must NOT call or inherit
    ``base.ensure_image()``'s ``docker pull`` fallback. This is a pure
    local, read-only ``docker image inspect``; a miss raises
    ``LocalImageMissing`` before ``start_container``/network access ever
    runs, matching the authorization review's required precondition."""
    inspect = base._run(["docker", "image", "inspect", image, "--format", "{{.Id}}"])
    if inspect.returncode != 0:
        raise LocalImageMissing(
            f"BLOCKED_WITH_REASON: local image {image!r} is absent and this runner "
            "never pulls an image - run `docker pull postgres:16-alpine` yourself "
            "first if that is actually intended, then rerun this script"
        )
    return inspect.stdout.strip()


def run_p4e_live_suite(database_url: str):
    import os
    import subprocess

    env = os.environ.copy()
    env[base.LIVE_URL_ENV] = database_url
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-v", *P4E_LIVE_SUITE_TARGETS],
        capture_output=True, text=True, cwd=str(base.REPO_ROOT), env=env,
    )


def run_once(database_url: str, container_name: str, port: int, password: str) -> dict:
    """Same structure as ``base.run_once`` (cleanup only when this run's
    own ``start_container`` succeeded), pointed at the P4-E live suite and
    migrations 001-011 (every migration, applied twice for idempotency)."""
    import traceback

    summary: dict = {"image": base.IMAGE, "container_name": container_name, "host_port": port}
    created = False
    volumes: list[str] = []
    failure: str | None = None
    try:
        base.start_container(container_name, port, password)
        created = True
        volumes = base.container_volumes(container_name)
        base.wait_ready(container_name)
        base.wait_ready_via_database(database_url)
        summary["migrations"] = base.apply_migrations_twice(database_url)
        result = run_p4e_live_suite(database_url)
        stdout = base.sanitize_output(result.stdout, password=password, database_url=database_url)
        stderr = base.sanitize_output(result.stderr, password=password, database_url=database_url)
        summary["live_suite_returncode"] = result.returncode
        summary["live_suite_tail"] = "\n".join(stdout.splitlines()[-80:])
        if result.returncode != 0:
            print(stdout)
            print(stderr, file=sys.stderr)
            failure = "P4-E live suite did not pass"
    except Exception:
        failure = base.sanitize_output(traceback.format_exc(), password=password, database_url=database_url)
    finally:
        if created:
            rm_ok, still_present = base.remove_container(container_name, volumes)
            summary["anonymous_volumes_captured"] = volumes
            summary["anonymous_volumes_still_present"] = still_present
            summary["container_absent_after_cleanup"] = (
                rm_ok and not base.container_exists(container_name) and not still_present
            )
            if not rm_ok:
                failure = failure or "docker rm -f -v did not report success"
            elif still_present:
                failure = failure or f"anonymous volume(s) survived cleanup: {still_present}"
        else:
            summary["container_absent_after_cleanup"] = True
            summary["cleanup_skipped_reason"] = "container was never created by this run"
        summary["failure"] = failure
    return summary


def main(argv: list[str] | None = None) -> int:
    import argparse
    import secrets

    parser = argparse.ArgumentParser(description="Disposable PostgreSQL 16 live round-trip, scoped to P4-E")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    summary: dict = {}
    try:
        summary["docker_server_version"] = base.check_docker_daemon()
        summary["psycopg_version"] = base.check_psycopg()
        summary["image_id"] = ensure_local_image_only()
    except LocalImageMissing as exc:
        summary["failure"] = str(exc)
        summary["container_absent_after_cleanup"] = True
        summary["cleanup_skipped_reason"] = "no container was ever created - local image was absent"
        print(json.dumps(summary, indent=2) if args.json
              else "\n".join(f"{k}: {v}" for k, v in summary.items()))
        return 1
    except base.LiveRoundTripError as exc:
        summary["failure"] = str(exc)
        summary["container_absent_after_cleanup"] = True
        print(json.dumps(summary, indent=2) if args.json
              else "\n".join(f"{k}: {v}" for k, v in summary.items()))
        return 1

    container_name = base.new_container_name()
    port = base.free_loopback_port()
    password = secrets.token_urlsafe(24)
    database_url = f"postgresql+psycopg://{base.POSTGRES_USER}:{password}@127.0.0.1:{port}/{base.POSTGRES_DB}"

    summary.update(run_once(database_url, container_name, port, password))

    print(json.dumps(summary, indent=2) if args.json
          else "\n".join(f"{k}: {v}" for k, v in summary.items() if k != "live_suite_tail"))
    return 0 if not summary.get("failure") and summary.get("container_absent_after_cleanup") else 1


if __name__ == "__main__":
    raise SystemExit(main())
