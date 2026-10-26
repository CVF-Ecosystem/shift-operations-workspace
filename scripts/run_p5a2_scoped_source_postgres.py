#!/usr/bin/env python3
"""One sealed, owned PostgreSQL experiment for the P5-A2 scoped source."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_postgres_live_roundtrip as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ADMISSION = ROOT / "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ADMISSION_2026-10-26.json"
EFFECT_WO = ROOT / "docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_EFFECT_WORK_ORDER.md"
TARGET = "tests/integration/test_p5a2_scoped_source_postgres_live.py"
IMAGE_ID = "sha256:f4610795587492cd4fb887c2dc3de301b813278bb6f616992061141b5f15ac36"
CONTEXT_ENV = "P5A2_PG_OWNED_CONTEXT"
BASELINE = "8dc39e119e4c343a18c2f16375448eebf22467bf"
SOURCE_PINS_DIGEST = "57e2855582dc88e2d72d69e3b6dd396ac61513a414868efa219a04ce85dce62a"
ATTEMPT_REL = "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ATTEMPT_2026-10-26.json"
OBS_REL = ".venv/p5a2-scoped-source-pg-observation-20261026.json"
EVIDENCE_REL = "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_EVIDENCE_2026-10-26.json"
ALLOWED_CHANGED = frozenset({
    "CVF_SESSION/ACTIVE_SESSION_STATE.json", "IMPLEMENTATION_STATUS.json",
    "SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json", "SESSION/ACTIVE_SESSION_STATE.json",
    "SESSION/SESSION_MEMORY.md", "SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md",
    "docs/INDEX.md", "docs/implementation/EXECUTION_ROADMAP.md",
    "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ADMISSION_2026-10-26.json",
    "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md",
    "docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md",
    "docs/specs/P5A2_SCOPED_SOURCE_POSTGRES_SPEC.md",
    "docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_EFFECT_WORK_ORDER.md",
    "docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_WORK_ORDER.md",
    "knowledge/PROJECT_CONTEXT.md", "knowledge/GOVERNANCE_BOUNDARIES.md", "knowledge/manifest.json",
    "docs/catalog/MODULE_REGISTRY.json", "docs/catalog/MODULE_CATALOG.md",
    "tests/fixtures/p5a2_scoped_source_pg_oracle.json",
    "scripts/run_p5a2_scoped_source_postgres.py",
    "tests/integration/p5a2_scoped_source_pg_fixture.py",
    "tests/integration/p5a2_scoped_source_pg_probes.py",
    TARGET, "tests/unit/test_p5a2_scoped_source_postgres_runner.py",
})


def _inside(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise base.LiveRoundTripError("admission path escapes project")
    return path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sealed_admission() -> dict:
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    effect_status = next((line.strip() for line in EFFECT_WO.read_text(encoding="utf-8").splitlines()
                          if line.startswith("Status: ")), "")
    policy = admission.get("containerCreationPolicy")
    if (admission.get("status") != "SOURCE_REVIEWED" or
            effect_status != "Status: APPROVED_FOR_EXECUTION" or
            admission.get("id") != "P5A2-SCOPED-SOURCE-PG-20261026" or
            admission.get("baselineCommit") != BASELINE or
            admission.get("image") != "postgres:16-alpine" or
            admission.get("imageId") != IMAGE_ID or admission.get("psycopgVersion") != "3.3.4" or
            any(admission.get(k) != v for k, v in {
                "imagePulls": 0, "packageInstalls": 0, "providerCalls": 0,
                "automaticRetries": 0, "maxWrapperInvocations": 1,
                "maxContainers": 1, "maxTargetInvocations": 1,
                "loopbackOnly": True, "realCredentialsAllowed": False,
                "attemptPath": ATTEMPT_REL, "observationPath": OBS_REL,
            }.items()) or policy != {"pull": "never", "imageArgument": "EXACT_IMAGE_ID",
                                     "existingResources": "DO_NOT_REUSE_OR_DELETE"}):
        raise base.LiveRoundTripError("sealed source/effect admission absent")
    pins = admission.get("harnessPins")
    required = {
        "scripts/run_p5a2_scoped_source_postgres.py",
        "tests/integration/p5a2_scoped_source_pg_fixture.py",
        "tests/integration/p5a2_scoped_source_pg_probes.py",
        TARGET, "tests/unit/test_p5a2_scoped_source_postgres_runner.py",
    }
    if not isinstance(pins, dict) or set(pins) != required:
        raise base.LiveRoundTripError("exact reviewed harness pins absent")
    if (len(admission.get("sourcePins", {})) != 38 or
            hashlib.sha256(json.dumps(admission["sourcePins"], sort_keys=True,
                separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest() != SOURCE_PINS_DIGEST or
            any(not re.fullmatch(r"[0-9a-f]{64}", digest) for digest in pins.values())):
        raise base.LiveRoundTripError("protected pin set changed")
    for relative, digest in {**admission["sourcePins"], **pins}.items():
        if _sha(_inside(relative)) != digest:
            raise base.LiveRoundTripError("sealed source pin mismatch")
    migrations = {path.relative_to(ROOT).as_posix() for path in
                  (ROOT / "database/migrations").glob("*.sql")}
    pinned_migrations = {name for name in admission["sourcePins"]
                         if name.startswith("database/migrations/") and name.endswith(".sql")}
    if migrations != pinned_migrations or len(migrations) != 11:
        raise base.LiveRoundTripError("exact migrations 001-011 unavailable")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                            capture_output=True, text=True, check=False)
    if status.returncode or status.stdout.strip():
        raise base.LiveRoundTripError("tracked/untracked project worktree is not clean")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", BASELINE, "HEAD"],
                              cwd=ROOT, capture_output=True, check=False)
    diff = subprocess.run(["git", "diff", "--name-only", BASELINE, "HEAD"],
                          cwd=ROOT, capture_output=True, text=True, check=False)
    if ancestor.returncode or diff.returncode or not set(diff.stdout.splitlines()) <= ALLOWED_CHANGED:
        raise base.LiveRoundTripError("protected baseline diff changed")
    marker = _inside(admission["attemptPath"])
    observation = _inside(admission["observationPath"])
    if marker.exists() or observation.exists() or _inside(EVIDENCE_REL).exists():
        raise base.LiveRoundTripError("experiment attempt already reserved or observed")
    return admission


def docker_run_cmd(name: str, port: int, password: str, image_id: str = IMAGE_ID) -> list[str]:
    if image_id != IMAGE_ID or not 1 <= port <= 65535 or not name.startswith(base.CONTAINER_PREFIX):
        raise base.LiveRoundTripError("invalid owned container request")
    return ["docker", "run", "--pull=never", "-d", "--name", name,
            "-e", f"POSTGRES_DB={base.POSTGRES_DB}",
            "-e", f"POSTGRES_USER={base.POSTGRES_USER}",
            "-e", f"POSTGRES_PASSWORD={password}",
            "-p", f"127.0.0.1:{port}:5432", image_id]


def run_target(url: str, context: dict) -> subprocess.CompletedProcess:
    allowed = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "TMPDIR", "VIRTUAL_ENV")
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    env["PYTHONNOUSERSITE"] = "1"
    env[base.LIVE_URL_ENV] = url
    env[CONTEXT_ENV] = json.dumps(context, sort_keys=True, separators=(",", ":"))
    return subprocess.run([sys.executable, "-m", "pytest", "-q", TARGET],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)


def _inspect(name: str, field: str) -> str:
    result = base._run(["docker", "inspect", name, "--format", field])
    if result.returncode or not result.stdout.strip():
        raise base.LiveRoundTripError("owned container identity unavailable")
    return result.stdout.strip()


def _reserve(admission: dict, name: str, port: int, nonce: str) -> Path:
    marker = _inside(admission["attemptPath"])
    body = {"admission_sha256": _sha(ADMISSION), "container_name": name,
            "host_port": port, "image_id": IMAGE_ID, "nonce": nonce,
            "reservation": "SPENT_ONCE"}
    with os.fdopen(os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w",
                   encoding="utf-8") as stream:
        json.dump(body, stream, sort_keys=True)
        stream.write("\n")
    return marker


def _port_binding(name: str, port: int) -> None:
    raw = _inspect(name, "{{json .HostConfig.PortBindings}}")
    if json.loads(raw) != {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(port)}]}:
        raise base.LiveRoundTripError("owned loopback port binding mismatch")


def _persist_result(result: dict) -> None:
    path = _inside(EVIDENCE_REL)
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w",
                   encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")


def run_once(admission: dict, name: str, port: int, password: str, nonce: str) -> dict:
    url = f"postgresql+psycopg://{base.POSTGRES_USER}:{password}@127.0.0.1:{port}/{base.POSTGRES_DB}"
    result: dict = {"image_id": IMAGE_ID, "container_name": name, "host_port": port,
                    "target": TARGET, "container_absent_after_cleanup": False}
    owned_id = None
    volumes: list[str] = []
    failure = None
    try:
        inspected = base._run(["docker", "image", "inspect", IMAGE_ID, "--format", "{{.Id}}"])
        if inspected.returncode or inspected.stdout.strip() != IMAGE_ID:
            raise base.LiveRoundTripError("cached exact image unavailable")
        if base.container_exists(name):
            raise base.LiveRoundTripError("owned container name collision")
        started = base._run(docker_run_cmd(name, port, password))
        if started.returncode or not started.stdout.strip():
            raise base.LiveRoundTripError("owned container creation failed")
        owned_id = started.stdout.strip()
        if _inspect(name, "{{.Id}}") != owned_id or _inspect(name, "{{.Image}}") != IMAGE_ID:
            raise base.LiveRoundTripError("created container identity mismatch")
        _port_binding(name, port)
        volumes = base.container_volumes(name)
        if not volumes:
            raise base.LiveRoundTripError("owned anonymous volume identity unavailable")
        result["container_id"] = owned_id
        result["anonymous_volumes_captured"] = volumes
        base.wait_ready(name)
        base.wait_ready_via_database(url)
        version = base._run(["docker", "exec", name, "psql", "-U",
            base.POSTGRES_USER, "-d", base.POSTGRES_DB, "-tAc", "SHOW server_version"])
        if version.returncode or not version.stdout.strip():
            raise base.LiveRoundTripError("PostgreSQL server version unavailable")
        result["server_version"] = version.stdout.strip()
        result["migrations"] = base.apply_migrations_twice(url)
        context = {"nonce": nonce, "container_name": name, "container_id": owned_id,
                   "image_id": IMAGE_ID, "host_port": port, "admission_sha256": _sha(ADMISSION)}
        target = run_target(url, context)
        result["target_returncode"] = target.returncode
        result["target_tail"] = "\n".join(base.sanitize_output(target.stdout + "\n" + target.stderr,
            password=password, database_url=url).splitlines()[-50:])
        if target.returncode or "1 passed" not in target.stdout or "skipped" in target.stdout:
            raise base.LiveRoundTripError("physical source target failed or skipped")
        observation = _inside(admission["observationPath"])
        if not observation.is_file():
            raise base.LiveRoundTripError("physical observation absent")
        raw = observation.read_text(encoding="utf-8")
        if password in raw or url in raw or "postgresql://" in raw or "postgresql+psycopg://" in raw:
            raise base.LiveRoundTripError("secret-bearing physical observation")
        if not json.loads(raw).get("completed"):
            raise base.LiveRoundTripError("physical observation incomplete")
        result["observation_sha256"] = _sha(observation)
    except Exception as exc:
        failure = base.sanitize_output(f"{type(exc).__name__}: {exc}",
                                       password=password, database_url=url)
    finally:
        if owned_id is None:
            result["cleanup_skipped_reason"] = "no owned container identity confirmed"
            result["container_absent_after_cleanup"] = False
        else:
            try:
                if _inspect(name, "{{.Id}}") != owned_id:
                    raise base.LiveRoundTripError("owned container identity changed before cleanup")
                removed = base._run(["docker", "rm", "-f", "-v", owned_id])
                still = [volume for volume in volumes if base.volume_exists(volume)]
                absent = not base.container_exists(name)
                result["anonymous_volumes_still_present"] = still
                result["container_absent_after_cleanup"] = (removed.returncode == 0 and absent
                    and bool(volumes) and not still)
                if not result["container_absent_after_cleanup"]:
                    failure = failure or "owned resource cleanup incomplete"
            except Exception as exc:
                failure = failure or base.sanitize_output(f"{type(exc).__name__}: {exc}",
                                                          password=password, database_url=url)
    result["failure"] = failure
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    reserved = False
    try:
        admission = sealed_admission()
        name, port, nonce = base.new_container_name(), base.free_loopback_port(), secrets.token_hex(24)
        _reserve(admission, name, port, nonce)
        reserved = True
        if base.check_psycopg() != admission["psycopgVersion"]:
            raise base.LiveRoundTripError("cached driver version mismatch")
        docker = base.check_docker_daemon()
        result = run_once(admission, name, port, secrets.token_urlsafe(24), nonce)
        result["docker_server_version"] = docker
    except Exception as exc:
        result = {"failure": f"BLOCKED_WITH_REASON: {type(exc).__name__}",
                  "container_absent_after_cleanup": False}
    if reserved:
        _persist_result(result)
    print(json.dumps(result, sort_keys=True) if args.json else result)
    return 0 if not result["failure"] and result["container_absent_after_cleanup"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
