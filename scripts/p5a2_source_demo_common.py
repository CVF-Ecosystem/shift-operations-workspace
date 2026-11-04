"""Exact local resource identity and secret-free lifecycle record helpers."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

from invariant_family_contract import canonical_digest, matches_shape_exactly

P5A2_DEMO_LIFECYCLE_MATRIX_CANONICAL_DIGEST = "f323ef1062e791c1c8fa4bff880b765a79547b571b0cfca9083286d680dcef2c"
PROFILE = "P5A2-SOURCE-DEMO-LOCAL-1"
PROJECT = "shift-operations-workspace"
CONTAINER = "shiftops-p5a2-source-demo-db-v1"
VOLUME = "shiftops-p5a2-source-demo-data-v1"
PORTS = {"db_port": 5433, "api_port": 8001, "web_port": 5174}
ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "infrastructure/demo/p5a2-source-postgres.compose.yml"
RUNTIME = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / "shiftops-p5a2-source-demo"
OWNER = RUNTIME / "owner.json"
LOCK = RUNTIME / "owner.lock"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
LABELS = {"cvf.project": PROJECT, "cvf.profile": PROFILE}
MATRIX = ROOT / "docs/cvf/invariants/p5a2-demo-resource-lifecycle.json"
LIFECYCLE_FIELDS = frozenset({"outcome", "profile_id", "owner_nonce", "reason",
    "container_count", "volume_count", "api_count", "web_count",
    "total_owned_count", "effect_count", "container_id", "volume_id",
    "api_pid", "web_pid", "stopped_container_id", "stopped_api_pid",
    "stopped_web_pid", "image_id", "db_fingerprint", "db_port", "api_port",
    "web_port", "owner_record_digest_before", "owner_record_digest_after"})


def accepts_lifecycle_record(record: dict) -> bool:
    """Real adapter to the single registered flat grammar; no second grammar."""
    try:
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        if canonical_digest(MATRIX) != P5A2_DEMO_LIFECYCLE_MATRIX_CANONICAL_DIGEST:
            return False
        return sum(matches_shape_exactly(shape, record, matrix)
                   for outcome in matrix["outcomes"]
                   for shape in outcome["shapes"]) == 1
    except (OSError, KeyError, TypeError, ValueError):
        return False


def fail(code: str) -> RuntimeError:
    return RuntimeError(code)


def digest(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_hex(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def check_pid(value: object) -> bool:
    return type(value) is int and value > 0


def normalize_image(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or not check_hex(value[7:]):
        raise fail("IMAGE_ID_INVALID")
    return value[7:]


def child_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """No ambient .env, provider key, or operator service credential inheritance."""
    keys = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "TEMP", "TMP",
            "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PYTHONUTF8")
    env = {k: os.environ[k] for k in keys if k in os.environ}
    env.update(extra or {})
    return env


def run(argv: list[str], *, env: dict[str, str] | None = None, timeout: int = 30,
        cwd: Path = ROOT) -> str:
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    result = subprocess.run(argv, cwd=cwd, env=child_env(env), capture_output=True,
                            text=True, timeout=timeout, creationflags=flags)
    if result.returncode:
        raise fail("COMMAND_FAILED")
    return result.stdout.strip()


def inspect(kind: str, name: str) -> dict | None:
    if kind not in ("container", "volume"):
        raise fail("INSPECT_KIND_INVALID")
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    result = subprocess.run(["docker", kind, "inspect", name], cwd=ROOT,
                            env=child_env(), capture_output=True, text=True,
                            timeout=15, creationflags=flags)
    if result.returncode:
        return None
    data = json.loads(result.stdout)
    return data[0] if len(data) == 1 else None


def labels_match(item: dict, nonce: str) -> bool:
    labels = item.get("Config", {}).get("Labels") if "Config" in item else item.get("Labels")
    return isinstance(labels, dict) and all(labels.get(k) == v for k, v in LABELS.items()) and labels.get("cvf.owner-nonce") == nonce


def read_owner() -> dict | None:
    if not OWNER.exists():
        return None
    data = json.loads(OWNER.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or set(data) != {"lifecycle_record", "context"}
            or not isinstance(data["lifecycle_record"], dict)
            or not isinstance(data["context"], dict)
            or data["lifecycle_record"].get("profile_id") != PROFILE
            or not accepts_lifecycle_record(data["lifecycle_record"])):
        raise fail("OWNER_CONFLICT")
    return {**data["context"], **data["lifecycle_record"]}


def write_owner(record: dict) -> None:
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    lifecycle = {k: v for k, v in record.items() if k in LIFECYCLE_FIELDS}
    if not accepts_lifecycle_record(lifecycle):
        raise fail("OWNER_LIFECYCLE_INVALID")
    envelope = {"lifecycle_record": lifecycle,
                "context": {k: v for k, v in record.items() if k not in LIFECYCLE_FIELDS}}
    tmp = OWNER.with_suffix(".tmp")
    tmp.write_text(json.dumps(envelope, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, OWNER)


@contextlib.contextmanager
def owner_lock():
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with LOCK.open("x", encoding="ascii") as handle:
            handle.write(str(os.getpid()))
    except FileExistsError:
        raise fail("LOCK_BUSY") from None
    try:
        yield
    finally:
        LOCK.unlink(missing_ok=True)


def port_free(port: int) -> bool:
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def process_identity(pid: object, expected_nonce: str, expected_token: str,
                     *, probe=None) -> bool:
    """Context check requires PID, invocation nonce and tool token in OS command line."""
    if not check_pid(pid) or not check_hex(expected_nonce):
        return False
    if probe is None:
        if sys.platform != "win32":
            return False
        code = "(Get-CimInstance Win32_Process -Filter 'ProcessId=%d').CommandLine" % pid
        try:
            command = run(["powershell", "-NoProfile", "-Command", code], timeout=10)
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            return False
    else:
        command = probe(pid)
    return isinstance(command, str) and expected_nonce in command and expected_token in command


def process_command(pid: object) -> str:
    if not check_pid(pid) or sys.platform != "win32":
        raise fail("PID_INVALID")
    code = "(Get-CimInstance Win32_Process -Filter 'ProcessId=%d').CommandLine" % pid
    return run(["powershell", "-NoProfile", "-Command", code], timeout=10)


def process_start(pid: object) -> str:
    if not check_pid(pid) or sys.platform != "win32":
        raise fail("PID_INVALID")
    code = "(Get-CimInstance Win32_Process -Filter 'ProcessId=%d').CreationDate.ToUniversalTime().ToString('o')" % pid
    return run(["powershell", "-NoProfile", "-Command", code], timeout=10)


def process_matches(pid: object, saved_start: str, token: str) -> bool:
    try:
        return check_pid(pid) and process_start(pid) == saved_start and token in process_command(pid)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return False


def resource_record(outcome: str, nonce: str, *, container_id=None, volume_id=None,
                    api_pid=None, web_pid=None, image_id=None, db_fingerprint=None,
                    reason=None, stopped=None) -> dict:
    """Counters describe IDs still owned after cleanup, never cumulative creation."""
    if not check_hex(nonce):
        raise fail("OWNER_NONCE_INVALID")
    ids = {"container_id": container_id, "volume_id": volume_id,
           "api_pid": api_pid, "web_pid": web_pid}
    bits = {"container_count": int(container_id is not None),
            "volume_count": int(volume_id is not None),
            "api_count": int(api_pid is not None), "web_count": int(web_pid is not None)}
    record = {"outcome": outcome, "profile_id": PROFILE, "owner_nonce": nonce,
              **bits, "total_owned_count": sum(bits.values())}
    if outcome == "REFUSED_NO_EFFECT":
        if any(bits.values()) or reason not in {"IMAGE_ABSENT", "PORT_BUSY", "OWNER_CONFLICT", "PROFILE_INVALID", "SCHEMA_UNKNOWN"}:
            raise fail("REFUSAL_INVALID")
        return {**record, "effect_count": 0, "reason": reason}
    if outcome == "STOP_REFUSED":
        raise fail("USE_STOP_REFUSAL")
    if outcome == "STOPPED_RETAINED":
        if bits != {"container_count": 0, "volume_count": 1, "api_count": 0, "web_count": 0} or not stopped:
            raise fail("STOP_RECORD_INVALID")
        if (set(stopped) != {"stopped_container_id", "stopped_api_pid", "stopped_web_pid"}
                or not check_hex(stopped["stopped_container_id"])
                or not check_pid(stopped["stopped_api_pid"])
                or not check_pid(stopped["stopped_web_pid"])
                or not check_hex(db_fingerprint)):
            raise fail("STOP_RECORD_INVALID")
        record.update(stopped)
        record["db_fingerprint"] = db_fingerprint
    elif outcome == "OWNED_RUNNING":
        if tuple(bits.values()) != (1, 1, 1, 1) or not check_hex(db_fingerprint):
            raise fail("RUNNING_RECORD_INVALID")
        record["db_fingerprint"] = db_fingerprint
    elif outcome == "PARTIAL_OWNED_FAILURE":
        if tuple(bits.values()) not in ((0, 1, 0, 0), (1, 1, 0, 0), (1, 1, 1, 0), (1, 1, 1, 1)):
            raise fail("PARTIAL_PREFIX_INVALID")
        if reason not in {"CONTAINER_START_FAILED", "API_START_FAILED", "WEB_START_FAILED", "HEALTH_FAILED", "SEED_FAILED", "CLEANUP_FAILED"}:
            raise fail("PARTIAL_REASON_INVALID")
        record["reason"] = reason
    else:
        raise fail("OUTCOME_INVALID")
    if volume_id != VOLUME or (container_id is not None and not check_hex(container_id)):
        raise fail("RESOURCE_ID_INVALID")
    if any(v is not None and not check_pid(v) for v in (api_pid, web_pid)):
        raise fail("PID_INVALID")
    if not check_hex(image_id):
        raise fail("IMAGE_ID_INVALID")
    record.update({k: v for k, v in ids.items() if v is not None})
    record.update({"image_id": image_id, **PORTS})
    return record


def stop_refusal(owner: dict, nonce: str, reason: str) -> dict:
    if reason not in {"OWNER_MISMATCH", "FOREIGN_RESOURCE", "PID_REUSED", "UNKNOWN_RESOURCE", "LOCK_BUSY"}:
        raise fail("STOP_REASON_INVALID")
    value = digest(owner)
    return {"outcome": "STOP_REFUSED", "profile_id": PROFILE, "owner_nonce": nonce,
            "reason": reason, "effect_count": 0,
            "owner_record_digest_before": value, "owner_record_digest_after": value}
