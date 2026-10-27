"""Exact owner and private local credential custody for one recovery."""
from __future__ import annotations

import base64
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from p5a2_source_demo_common import (CONTAINER, OWNER, PORTS, PROFILE, RUNTIME,
                                     VOLUME, child_env, digest, fail, port_free,
                                     read_owner)
from p5a2_source_demo_recovery_docker import IMAGE, inspect, verified_image, verified_volume

EXPECTED_NONCE = "3bf4a4c5d48d0f4ffc8a96a5aecfccaae6c07a9820cf8f7cf8757cf500ead999"
AM2_CONTAINER = "877cd8fcbc82eb7404c76fa2575e77ddd61976539083f5aad0f57b147c9ad532"
AM3_OWNER_DIGEST = "3af5e4892aaea7bfe64422ed7f3b237a6d54f910c8e2d0dbc68e6e925b9599ab"
AM3_VOLUME_IDENTITY = "7a9aebeaff0294132dde49494509a97a291de44811793cc845fa802f1e8aa304"
SECRET = RUNTIME / "secrets.json"
EXPECTED_RUNTIME = Path("C:/Users/DELL/AppData/Local/shiftops-p5a2-source-demo")


def owner_state(expected_digest: str) -> dict:
    if RUNTIME.resolve() != EXPECTED_RUNTIME.resolve():
        raise fail("RUNTIME_PATH_INVALID")
    owner = read_owner()
    if (owner is None or owner.get("profile_id") != PROFILE
            or owner.get("outcome") != "PARTIAL_OWNED_FAILURE"
            or owner.get("owner_nonce") != EXPECTED_NONCE
            or owner.get("volume_id") != VOLUME
            or owner.get("image_id") != IMAGE.removeprefix("sha256:")
            or any(owner.get(key) for key in ("container_id", "api_pid", "web_pid"))
            or owner.get("total_owned_count") != 1
            or owner.get("secret_ref") != str(SECRET)
            or owner.get("creation_trail") != [
                {"kind": "volume", "id": VOLUME},
                {"kind": "container", "id": "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"},
                {"kind": "container", "id": "dee30bee86b3cd5395ca06188f586b869dbf329529701c296efa7c3b4bb49747",
                 "recovery": True}]
            or owner.get("cleanup_trail") != [
                {"kind": "container", "id": "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"},
                {"kind": "container", "id": "dee30bee86b3cd5395ca06188f586b869dbf329529701c296efa7c3b4bb49747",
                 "recovery": True}]):
        raise fail("OWNER_STATE_INVALID")
    if digest(owner) != expected_digest:
        raise fail("OWNER_DIGEST_CHANGED")
    if not OWNER.is_file() or OWNER.is_symlink() or RUNTIME.is_symlink():
        raise fail("OWNER_CUSTODY_INVALID")
    return owner


def am3_owner_state(expected_digest: str) -> dict:
    """Bind the cleaned AM2 volume-only owner without weakening old recovery."""
    if expected_digest != AM3_OWNER_DIGEST or RUNTIME.resolve() != EXPECTED_RUNTIME.resolve():
        raise fail("AM3_OWNER_DIGEST_INVALID")
    owner = read_owner()
    if (owner is None or owner.get("profile_id") != PROFILE
            or owner.get("owner_nonce") != EXPECTED_NONCE
            or owner.get("outcome") != "PARTIAL_OWNED_FAILURE"
            or owner.get("reason") != "HEALTH_FAILED"
            or owner.get("volume_id") != VOLUME
            or owner.get("image_id") != IMAGE.removeprefix("sha256:")
            or any(owner.get(key) for key in ("container_id", "api_pid", "web_pid"))
            or [owner.get(key) for key in ("volume_count", "container_count",
                                           "api_count", "web_count", "total_owned_count")]
               != [1, 0, 0, 0, 1]
            or owner.get("secret_ref") != str(SECRET)
            or owner.get("creation_trail") != [
                {"kind": "volume", "id": VOLUME},
                {"kind": "container", "id": "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"},
                {"kind": "container", "id": "dee30bee86b3cd5395ca06188f586b869dbf329529701c296efa7c3b4bb49747",
                 "recovery": True},
                {"kind": "container", "id": AM2_CONTAINER, "recovery": True},
                {"kind": "api", "id": 12612},
                {"kind": "web", "id": 38184}]
            or owner.get("cleanup_trail") != [
                {"kind": "container", "id": "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"},
                {"kind": "container", "id": "dee30bee86b3cd5395ca06188f586b869dbf329529701c296efa7c3b4bb49747",
                 "recovery": True},
                {"kind": "web", "id": 38184, "result": "ALREADY_ABSENT_VERIFIED", "am2": True},
                {"kind": "api", "id": 12612, "result": "ALREADY_ABSENT_VERIFIED", "am2": True},
                {"kind": "container", "id": AM2_CONTAINER,
                 "result": "REMOVED_STOPPED_EXACT_OWNED", "am2": True}]):
        raise fail("AM3_OWNER_STATE_INVALID")
    if digest(owner) != expected_digest or not OWNER.is_file() or OWNER.is_symlink() or RUNTIME.is_symlink():
        raise fail("AM3_OWNER_CUSTODY_INVALID")
    return owner


def am3_preflight(expected_digest: str) -> dict:
    am3_owner_state(expected_digest)
    verified_image()
    volume = verified_volume(EXPECTED_NONCE)
    if volume_identity(volume) != AM3_VOLUME_IDENTITY:
        raise fail("AM3_VOLUME_CHANGED")
    if inspect("container", CONTAINER) is not None:
        raise fail("CONTAINER_CONFLICT")
    if not all(port_free(port) for port in PORTS.values()):
        raise fail("PORT_BUSY")
    secret_custody()
    return {"preflight": "PASS", "profile_id": PROFILE,
            "owner_nonce": EXPECTED_NONCE, "owner_digest": expected_digest,
            "volume_id": VOLUME, "volume_identity": volume_identity(volume),
            "image_id": IMAGE, "ports": PORTS}


def secret_custody() -> None:
    if (SECRET != RUNTIME / "secrets.json" or not SECRET.is_file()
            or SECRET.is_symlink() or RUNTIME.is_symlink()
            or SECRET.stat().st_nlink != 1):
        raise fail("SECRET_CUSTODY_INVALID")
    if sys.platform == "win32":
        if not windows_private_acl(RUNTIME, SECRET):
            raise fail("SECRET_ACL_INVALID")
    elif SECRET.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise fail("SECRET_ACL_INVALID")
    return None


def windows_private_acl(folder: Path, file: Path) -> bool:
    """Return only PASS/FAIL; never return or log raw ACL principals/rights."""
    if sys.platform != "win32":
        return False
    def literal(path: Path) -> str:
        return "'" + str(path).replace("'", "''") + "'"
    script = f"""
try {{
  $userSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  # OWNER RIGHTS denotes this object's owner; owner and explicit user FullControl are checked below.
  $allowed = @($userSid, 'S-1-5-18', 'S-1-5-32-544', 'S-1-3-4')
  foreach ($path in @({literal(folder)}, {literal(file)})) {{
    $acl = Get-Acl -LiteralPath $path -ErrorAction Stop
    if (-not $acl.AreAccessRulesProtected -or
        $acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $userSid) {{ throw 'ACL' }}
    $rules = $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])
    $ownerFull = $false
    foreach ($rule in $rules) {{
      if ($rule.IsInherited -or
          $rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
          $rule.IdentityReference.Value -notin $allowed) {{ throw 'ACL' }}
      if ($rule.IdentityReference.Value -eq $userSid -and
          (($rule.FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -eq
           [Security.AccessControl.FileSystemRights]::FullControl)) {{ $ownerFull = $true }}
    }}
    if (-not $ownerFull) {{ throw 'ACL' }}
  }}
  'PASS'
}} catch {{ 'FAIL' }}
"""
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    try:
        result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive",
                                 "-EncodedCommand", encoded], env=child_env(),
                                capture_output=True, text=True, timeout=10,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and result.stdout.strip() == "PASS"


def secret_file() -> dict[str, str]:
    secret_custody()
    try:
        data = json.loads(SECRET.read_text(encoding="utf-8"))
        if (not isinstance(data, dict)
                or set(data) != {"db_password", "viewer_password", "jwt_secret"}
                or any(not isinstance(value, str) or len(value) < 32 for value in data.values())):
            raise ValueError("invalid")
        return data
    except (OSError, UnicodeError, ValueError):
        raise fail("SECRET_FILE_INVALID") from None


def preflight(expected_digest: str) -> dict:
    owner = owner_state(expected_digest)
    verified_image()
    volume = verified_volume(EXPECTED_NONCE)
    if inspect("container", CONTAINER) is not None:
        raise fail("CONTAINER_CONFLICT")
    if not all(port_free(port) for port in PORTS.values()):
        raise fail("PORT_BUSY")
    # The physical executor may read values only after source checkpoint and
    # reservation. Preflight checks custody without reading secret contents.
    secret_custody()
    return {"preflight": "PASS", "profile_id": PROFILE,
            "owner_nonce": EXPECTED_NONCE, "owner_digest": expected_digest,
            "volume_id": VOLUME, "volume_identity": volume_identity(volume),
            "image_id": IMAGE, "ports": PORTS}


def volume_identity(volume: dict) -> str:
    fields = ("Name", "CreatedAt", "Mountpoint", "Driver", "Labels")
    if any(field not in volume for field in fields):
        raise fail("VOLUME_IDENTITY_INCOMPLETE")
    return digest({field: volume[field] for field in fields})
