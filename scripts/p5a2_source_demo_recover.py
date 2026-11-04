"""One gated retained-volume recovery; Root owns invocation and evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from p5a2_source_demo_common import (CONTAINER, LIFECYCLE_FIELDS, OWNER, PROFILE, ROOT, VOLUME,
                                     check_hex, digest, fail, owner_lock,
                                     process_matches, resource_record, run, write_owner)
from p5a2_source_demo_recovery_custody import (EXPECTED_NONCE, owner_state,
                                               preflight, secret_file,
                                               volume_identity)
from p5a2_source_demo_recovery_docker import (IMAGE, create_container, inspect,
                                              remove_container, verified_container,
                                              verified_volume)
from p5a2_source_demo_recovery_inventory import (TARGET, inventory,
                                                 post_seed_summary, verify_post_seed_digest)
from p5a2_source_demo_recovery_services import child_settings, start_services

ATTEMPT = ROOT / "docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_AM2_ATTEMPT_2026-10-27.json"
NODE = "C:/Users/DELL/AppData/Local/nvm/v22.14.0/node.exe"
EXPECTED_DB_FINGERPRINT = "afeb7f5ca42aec45a1bdc9f8a6d10c7401a401c080ce4b6097279badb3cadca9"


def reservation(expected_sha: str, owner_digest: str) -> None:
    if not check_hex(expected_sha) or not ATTEMPT.is_file():
        raise fail("RECOVERY_RESERVATION_ABSENT")
    raw = ATTEMPT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise fail("RECOVERY_RESERVATION_CHANGED")
    try:
        marker = json.loads(raw)
    except ValueError:
        raise fail("RECOVERY_RESERVATION_INVALID") from None
    if (type(marker) is not dict
            or marker.get("id") != "P5A2-SYNTHETIC-BACKEND-RECOVERY-AM2-ATTEMPT-20261027"
            or marker.get("status") != "RESERVED_SPENT_NO_RETRY"
            or type(marker.get("maximumRecoveryCalls")) is not int
            or marker.get("maximumRecoveryCalls") != 1
            or marker.get("profileId") != PROFILE
            or marker.get("ownerNonce") != EXPECTED_NONCE
            or marker.get("ownerDigest") != owner_digest
            or marker.get("imageId") != IMAGE):
        raise fail("RECOVERY_RESERVATION_INVALID")


def _node_ready() -> None:
    if not Path(NODE).is_file() or run([NODE, "--version"]) != "v22.14.0":
        raise fail("NODE_VERSION_INVALID")


def _native_seed(dsn: str, env: dict[str, str], viewer: str,
                 before: dict) -> dict:
    snapshot = {key: before[key] for key in (
        "classification", "state_digest", "db_fingerprint", "observed_created_at",
        "table_names", "schema_digest")}
    output = run([sys.executable, "-m", "workspace_api.demo.seed"],
                 env={**env, "P5A2_SOURCE_DEMO_VIEWER_PASSWORD": viewer,
                      "P5A2_SOURCE_DEMO_EXPECTED_SNAPSHOT": json.dumps(snapshot,
                                                                          sort_keys=True)},
                 timeout=90)
    expected = {"EMPTY_COMPATIBLE": "SEEDED", "EXACT_SEEDED": "VERIFY",
                "SOLE_CREATED_AT_MISMATCH": "CREATED_AT_REPAIRED"}[before["classification"]]
    try:
        result = json.loads(output)
    except ValueError:
        raise fail("NATIVE_SEED_RECEIPT_INVALID") from None
    if (type(result) is not dict
            or set(result) != {"result", "state_digest", "db_fingerprint", "family_record"}
            or result.get("result") != expected
            or result.get("db_fingerprint") != before["db_fingerprint"]
            or not check_hex(result.get("state_digest"))
            or type(result.get("family_record")) is not dict):
        raise fail("NATIVE_SEED_STATE_INVALID")
    from invariant_family_contract import load_json_no_dup, matches_shape_exactly

    matrix = load_json_no_dup(ROOT / "docs/cvf/invariants/p5a2-demo-seed-recovery.json")
    expected_outcome = {"SEEDED": "SEEDED_ATOMIC", "VERIFY": "EXACT_VERIFIED",
                        "CREATED_AT_REPAIRED": "CREATED_AT_REPAIRED"}[expected]
    shapes = [shape for outcome in matrix["outcomes"]
              if outcome["outcomeId"] == expected_outcome
              for shape in outcome["shapes"]]
    if len(shapes) != 1 or not matches_shape_exactly(
            shapes[0], result["family_record"], matrix):
        raise fail("NATIVE_SEED_FAMILY_INVALID")
    return result


def _terminate_new_children(resource: dict, state: dict, handles: dict) -> bool:
    for kind in ("web", "api"):
        key = kind + "_pid"
        pid = resource[key]
        if pid is None:
            continue
        handle = handles.get(kind)
        token = "vite.js" if kind == "web" else "workspace_api.demo.app:create_app"
        if handle is None or handle.pid != pid:
            return False
        if handle.poll() is None:
            if not process_matches(pid, state.get(kind + "_start"), token):
                return False
            try:
                handle.terminate()
                handle.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                return False
        state["cleanup_trail"].append({"kind": kind, "id": pid,
                                       "recovery": True})
        resource[key] = None
    return True


def replace_lifecycle(state: dict, record: dict) -> None:
    """Preserve historical context while replacing the one registered shape."""
    for key in LIFECYCLE_FIELDS:
        state.pop(key, None)
    state.update(record)


def _cleanup(resource: dict, state: dict, handles: dict) -> bool:
    if not _terminate_new_children(resource, state, handles):
        return False
    cid = resource["container_id"]
    if cid is not None:
        try:
            remove_container(EXPECTED_NONCE, cid)
        except RuntimeError:
            return False
        state["cleanup_trail"].append({"kind": "container", "id": cid,
                                       "recovery": True})
        resource["container_id"] = None
    return True


def _adopt_lost_create(resource: dict, state: dict, expected_volume: str) -> bool:
    """Recover a Docker run receipt lost after an exact named create."""
    if resource["container_id"] is not None:
        return True
    try:
        current = inspect("container", CONTAINER)
    except RuntimeError:
        state["recovery_unknown_custody"] = "CONTAINER_INSPECT_UNAVAILABLE"
        return False
    if current is None:
        return True
    cid = current.get("Id")
    if not check_hex(cid):
        state["recovery_unknown_custody"] = "CONTAINER_ID_INVALID"
        return False
    try:
        verified_container(EXPECTED_NONCE, cid, running=False)
        if volume_identity(verified_volume(EXPECTED_NONCE)) != expected_volume:
            raise fail("VOLUME_CHANGED_AFTER_CREATE")
    except RuntimeError:
        state["recovery_unknown_custody"] = "CONTAINER_IDENTITY_UNVERIFIED"
        return False
    resource["container_id"] = cid
    state["creation_trail"].append({"kind": "container", "id": cid,
                                    "recovery": True, "receipt": "LOST"})
    return True


def _record_failure(owner: dict, state: dict, resource: dict,
                    stage: str, cleaned: bool, *, reason: str = "SEED_FAILED") -> None:
    # Never claim an absent resource without a fresh exact identity check.
    try:
        current = inspect("container", CONTAINER)
    except RuntimeError:
        current = None
        cleaned = False
        state["recovery_unknown_custody"] = "CONTAINER_INSPECT_UNAVAILABLE"
    if current is not None:
        cid = current.get("Id")
        if cid != resource.get("container_id"):
            cleaned = False
            state["recovery_unknown_custody"] = "CONTAINER_IDENTITY_UNVERIFIED"
            resource["container_id"] = None
        else:
            try:
                verified_container(EXPECTED_NONCE, cid, running=False)
            except RuntimeError:
                cleaned = False
                state["recovery_unknown_custody"] = "CONTAINER_IDENTITY_UNVERIFIED"
                resource["container_id"] = None
    elif resource.get("container_id") is not None and "recovery_unknown_custody" not in state:
        resource["container_id"] = None
    try:
        verified_volume(EXPECTED_NONCE)
    except RuntimeError:
        cleaned = False
        state["recovery_unknown_custody"] = "VOLUME_IDENTITY_UNVERIFIED"
    state["recovery_failure_stage"] = stage
    state["recovery_cleanup_verified"] = cleaned
    reason = "CLEANUP_FAILED" if not cleaned else reason
    record = resource_record("PARTIAL_OWNED_FAILURE", EXPECTED_NONCE,
                             **resource, image_id=IMAGE.removeprefix("sha256:"),
                             reason=reason)
    replace_lifecycle(state, record)
    write_owner(state)


def recover(owner_digest: str, attempt_sha: str) -> dict:
    if not check_hex(owner_digest):
        raise fail("OWNER_DIGEST_INVALID")
    with owner_lock():
        reservation(attempt_sha, owner_digest)
        check = preflight(owner_digest)
        _node_ready()
        owner = owner_state(owner_digest)
        secret = secret_file()
        dsn, env = child_settings(secret)
        resource = {"volume_id": VOLUME, "container_id": None,
                    "api_pid": None, "web_pid": None}
        state = {**owner, "creation_trail": list(owner["creation_trail"]),
                 "cleanup_trail": list(owner["cleanup_trail"])}
        handles = {}
        stage = "CONTAINER_CREATE"
        try:
            cid = create_container(EXPECTED_NONCE)
            resource["container_id"] = cid
            state["creation_trail"].append({"kind": "container", "id": cid,
                                            "recovery": True})
            verified_container(EXPECTED_NONCE, cid)
            if volume_identity(verified_volume(EXPECTED_NONCE)) != check["volume_identity"]:
                raise fail("VOLUME_CHANGED_AFTER_CREATE")
            stage = "DB_READINESS"
            from p5a2_source_demo_start import wait_db
            wait_db(dsn.replace("postgresql+psycopg://", "postgresql://", 1))
            stage = "READ_ONLY_INVENTORY"
            before = inventory(dsn.replace("postgresql+psycopg://", "postgresql://", 1),
                               secret["viewer_password"])
            if before["db_fingerprint"] != EXPECTED_DB_FINGERPRINT:
                raise fail("RETAINED_DB_FINGERPRINT_CHANGED")
            state["recovery_prewrite_fingerprint"] = before["db_fingerprint"]
            state["recovery_prewrite_classification"] = before["classification"]
            state["recovery_prewrite_inventory"] = before
            stage = "NATIVE_SEED_OR_VERIFY"
            seed_receipt = _native_seed(dsn, env, secret["viewer_password"], before)
            stage = "POST_SEED_VERIFICATION"
            after = post_seed_summary(
                dsn.replace("postgresql+psycopg://", "postgresql://", 1),
                before["db_fingerprint"], secret["viewer_password"],
                before["schema_digest"])
            if any(after["counts"][name] != value for name, value in TARGET.items()):
                raise fail("POST_SEED_STATE_INVALID")
            verify_post_seed_digest(after, seed_receipt)
            state["recovery_post_seed_summary"] = after
            stage = "API_WEB_START"
            start_services(NODE, env, resource, state, handles)
            record = resource_record("OWNED_RUNNING", EXPECTED_NONCE,
                                     **resource, image_id=IMAGE.removeprefix("sha256:"),
                                     db_fingerprint=before["db_fingerprint"])
            replace_lifecycle(state, record)
            state["recovery_seed_state"] = seed_receipt["result"]
            state["recovery_seed_family"] = seed_receipt["family_record"]
            write_owner(state)
            return {**record, "owner_record_digest": digest(state),
                    "owner_record_path": str(OWNER),
                    "prewrite_inventory": before,
                    "post_seed_summary": after,
                    "seed_state_digest": seed_receipt["state_digest"],
                    "seed_family_record": seed_receipt["family_record"]}
        except Exception:
            adopted = _adopt_lost_create(resource, state, check["volume_identity"])
            if adopted:
                cleaned = _cleanup(resource, state, handles)
            else:
                _terminate_new_children(resource, state, handles)
                cleaned = False
            _record_failure(owner, state, resource, stage, cleaned)
            raise fail("RECOVERY_FAILED_" + stage) from None


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print(json.dumps({"status": "REFUSED", "stage": "ARGUMENTS"}))
        return 1
    mode, owner_digest = sys.argv[1:3]
    try:
        if mode == "preflight" and len(sys.argv) == 3:
            result = preflight(owner_digest)
            _node_ready()
        elif mode == "recover" and len(sys.argv) == 4:
            result = recover(owner_digest, sys.argv[3])
        else:
            raise fail("ARGUMENTS_INVALID")
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        stage = str(exc) if type(exc) is RuntimeError else "UNEXPECTED_FAILURE"
        print(json.dumps({"status": "REFUSED_OR_FAILED", "stage": stage}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
