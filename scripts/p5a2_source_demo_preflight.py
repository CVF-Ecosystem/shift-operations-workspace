"""Read-only, fail-closed checks for the isolated local source demo."""
from __future__ import annotations

import importlib.util
import json
import os
import secrets
import sys
from pathlib import Path

from p5a2_source_demo_common import (COMPOSE, CONTAINER, OWNER, PORTS, ROOT, VOLUME,
                                     fail, inspect, normalize_image, port_free,
                                     read_owner, resource_record, run)


def prerequisites() -> dict:
    if Path(sys.executable).resolve() != (ROOT / ".venv/Scripts/python.exe").resolve():
        raise fail("PYTHON_ENV_INVALID")
    if any(importlib.util.find_spec(x) is None for x in ("psycopg", "sqlalchemy")):
        raise fail("PYTHON_DEPENDENCY_ABSENT")
    if not COMPOSE.is_file() or not (ROOT / "apps/workspace-web/node_modules").is_dir():
        raise fail("PROFILE_FILES_ABSENT")
    migration_dir = ROOT / "database/migrations"
    if len(tuple(migration_dir.glob("[0-9][0-9][0-9]_*.sql"))) != 11:
        raise fail("MIGRATIONS_ABSENT")
    candidates = [Path(os.environ.get("NVM_HOME", "")) / "v22.14.0/node.exe",
                  Path(os.environ.get("LOCALAPPDATA", "")) / "nvm/v22.14.0/node.exe",
                  Path.home() / "AppData/Local/nvm/v22.14.0/node.exe"]
    node = next((path.resolve() for path in candidates if path.is_file()), None)
    if node is None:
        raise fail("NODE_ABSENT")
    if run([str(node), "--version"]) != "v22.14.0":
        raise fail("NODE_VERSION_INVALID")
    try:
        raw = run(["docker", "image", "inspect", "postgres:16", "--format", "{{.Id}}"])
    except (RuntimeError, OSError):
        raise fail("IMAGE_ABSENT") from None
    image_id = normalize_image(raw)
    if read_owner() is not None or OWNER.exists():
        raise fail("OWNER_CONFLICT")
    if inspect("container", CONTAINER) is not None or inspect("volume", VOLUME) is not None:
        raise fail("OWNER_CONFLICT")
    if not all(port_free(port) for port in PORTS.values()):
        raise fail("PORT_BUSY")
    return {"profile_id": "P5A2-SOURCE-DEMO-LOCAL-1", "image_id": image_id,
            **PORTS, "effect_count": 0, "preflight": "PASS",
            "node_path": str(Path(node).resolve())}


def main() -> int:
    try:
        result = prerequisites()
    except Exception as exc:
        code = str(exc) if type(exc) is RuntimeError else "PROFILE_INVALID"
        reason = code if code in {"IMAGE_ABSENT", "PORT_BUSY", "OWNER_CONFLICT", "SCHEMA_UNKNOWN"} else "PROFILE_INVALID"
        print(json.dumps(resource_record("REFUSED_NO_EFFECT", secrets.token_hex(32),
                                         reason=reason), sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
