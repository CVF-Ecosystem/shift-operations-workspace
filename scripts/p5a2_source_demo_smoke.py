"""Later Stage B physical SQL, JWT and native HTTP two-context receipt."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from p5a2_source_demo_common import (CONTAINER, OWNER, PROFILE, VOLUME,
                                     check_hex, digest, fail, inspect, labels_match,
                                     process_matches, read_owner)


def _http(method: str, path: str, *, payload=None, token=None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request("http://127.0.0.1:8001" + path, data=data,
                      headers=headers, method=method)
    with urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read())


def smoke(nonce: str) -> dict:
    owner = read_owner()
    if owner is None or owner.get("outcome") != "OWNED_RUNNING" or owner.get("owner_nonce") != nonce:
        raise fail("OWNER_MISMATCH")
    container, volume = inspect("container", CONTAINER), inspect("volume", VOLUME)
    if (not container or not volume or container.get("Id") != owner.get("container_id")
            or not labels_match(container, nonce) or not labels_match(volume, nonce)):
        raise fail("RESOURCE_IDENTITY_INVALID")
    if not (process_matches(owner.get("api_pid"), owner.get("api_start"), "workspace_api.demo.app:create_app")
            and process_matches(owner.get("web_pid"), owner.get("web_start"), "vite.js")):
        raise fail("PROCESS_IDENTITY_INVALID")
    secrets_path = Path(owner.get("secret_ref", ""))
    if secrets_path.parent != OWNER.parent:
        raise fail("SECRET_REFERENCE_INVALID")
    secrets = json.loads(secrets_path.read_text(encoding="utf-8"))
    import psycopg
    dsn = ("postgresql://source_demo:" + secrets["db_password"]
           + "@127.0.0.1:5433/shiftops_p5a2_source_demo")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version()")
            db_name, pg_version = cur.fetchone()
            if db_name != "shiftops_p5a2_source_demo" or "PostgreSQL 16" not in pg_version:
                raise fail("DB_IDENTITY_INVALID")
            cur.execute("SELECT system_identifier FROM pg_control_system()")
            if digest({"database": db_name, "system_identifier": str(cur.fetchone()[0])}) != owner["db_fingerprint"]:
                raise fail("DB_FINGERPRINT_INVALID")
            counts = {}
            for table, count in (("users", 1), ("shifts", 36),
                                 ("shift_assignments", 36), ("reports", 37)):
                cur.execute("SELECT count(*) FROM " + table)
                value = cur.fetchone()[0]
                if value != count:
                    raise fail("DB_COUNT_INVALID")
                counts[table] = value
    status, login = _http("POST", "/auth/login", payload={
        "username": "source-demo-viewer", "password": secrets["viewer_password"]})
    if status != 200 or not isinstance(login.get("access_token"), str):
        raise fail("AUTH_FAILED")
    token = login["access_token"]
    # Frozen pre-runtime independently derived receipt digests; no test fixture import.
    cases_expected = (
        ("initial_asof36", "2026-01-02T12:00:00Z",
         "5523c755204ea4ee3e960394306c61d32d75d926806276748f99be481f6b0e64"),
        ("later_asof38", "2026-01-02T14:00:00Z",
         "874e8e5693e1efeea30f92ab26ef48dacb00f0b0efa109f977fd3e8beba6f554"),
    )
    cases = []
    for name, as_of, expected_digest in cases_expected:
        query = urlencode({"query_start": "2026-01-01T00:00:00Z",
                           "query_end": "2026-01-02T12:00:00Z", "run_as_of": as_of})
        status, body = _http("GET", "/proactive/source?" + query, token=token)
        if status != 200 or digest(body) != expected_digest:
            raise fail("SOURCE_ORACLE_MISMATCH")
        cases.append({"case": name, "status": status,
                      "receipt_sha256": digest(body)})
    return {"result": "PHYSICAL_SOURCE_SMOKE_PASS", "profile_id": PROFILE,
            "owner_nonce": nonce, "container_id": owner["container_id"],
            "db_fingerprint": owner["db_fingerprint"], "postgresql_major": 16,
            "counts": counts, "cases": cases, "jwt_login_status": 200,
            "secret_values_recorded": False}


if __name__ == "__main__":
    if len(sys.argv) != 2 or not check_hex(sys.argv[1]):
        raise SystemExit("usage: p5a2_source_demo_smoke.py OWNER_NONCE")
    try:
        print(json.dumps(smoke(sys.argv[1]), sort_keys=True))
    except Exception:
        print(json.dumps({"result": "SMOKE_FAILED", "reason": "SMOKE_FAILED"}))
        raise SystemExit(1)
