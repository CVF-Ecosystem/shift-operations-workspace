"""One AM4 exact verify-only runtime; Root owns the effect and evidence."""
from __future__ import annotations

import hashlib
import json
import sys

from p5a2_source_demo_common import (OWNER, PROFILE, ROOT, VOLUME, check_hex,
                                     digest, fail, owner_lock, resource_record,
                                     write_owner)
from p5a2_source_demo_recover import (_adopt_lost_create, _cleanup,
                                      _node_ready, _record_failure,
                                      replace_lifecycle)
from p5a2_source_demo_recovery_custody import (EXPECTED_NONCE, secret_file,
                                                volume_identity)
from p5a2_source_demo_recovery_docker import (IMAGE, create_container,
                                              verified_container, verified_volume)
from p5a2_source_demo_recovery_inventory import inventory, post_seed_summary
from p5a2_source_demo_recovery_services import child_settings, start_services
from p5a2_source_demo_verify_am4_custody import (AM4_OWNER_DIGEST,
                                                  am4_owner_state, am4_preflight)
from p5a2_source_demo_verify_guard import (FINGERPRINT, SCHEMA_DIGEST,
                                           STATE_DIGEST, verify_only)

ATTEMPT = ROOT / "docs/decisions/P5A2_UI_COMPLETION_AM4_ATTEMPT_2026-10-27.json"
MARKER_ID = "P5A2-UI-COMPLETION-AM4-ATTEMPT-20261027"
NODE = "C:/Users/DELL/AppData/Local/nvm/v22.14.0/node.exe"
MARKER_KEYS = {"id", "status", "maximumVerifyRuntimeCalls", "profileId",
               "ownerNonce", "ownerDigest", "imageId", "volumeIdentity",
               "expectedDatabaseFingerprint", "expectedSchemaDigest",
               "expectedStateDigest"}


def reservation(expected_sha: str, owner_digest: str, volume_id: str) -> None:
    if not check_hex(expected_sha) or not ATTEMPT.is_file():
        raise fail("AM4_RESERVATION_ABSENT")
    raw = ATTEMPT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise fail("AM4_RESERVATION_CHANGED")
    try:
        marker = json.loads(raw)
    except ValueError:
        raise fail("AM4_RESERVATION_INVALID") from None
    if (type(marker) is not dict or set(marker) != MARKER_KEYS
            or marker["id"] != MARKER_ID
            or marker["status"] != "RESERVED_SPENT_NO_RETRY"
            or type(marker["maximumVerifyRuntimeCalls"]) is not int
            or marker["maximumVerifyRuntimeCalls"] != 1
            or marker["profileId"] != PROFILE
            or marker["ownerNonce"] != EXPECTED_NONCE
            or marker["ownerDigest"] != owner_digest
            or marker["imageId"] != IMAGE
            or marker["volumeIdentity"] != volume_id
            or marker["expectedDatabaseFingerprint"] != FINGERPRINT
            or marker["expectedSchemaDigest"] != SCHEMA_DIGEST
            or marker["expectedStateDigest"] != STATE_DIGEST):
        raise fail("AM4_RESERVATION_INVALID")


def verify_runtime(owner_digest: str, attempt_sha: str) -> dict:
    if owner_digest != AM4_OWNER_DIGEST or not check_hex(attempt_sha):
        raise fail("AM4_ARGUMENTS_INVALID")
    with owner_lock():
        check = am4_preflight(owner_digest)
        reservation(attempt_sha, owner_digest, check["volume_identity"])
        _node_ready()
        owner = am4_owner_state(owner_digest)
        secret = secret_file()
        dsn, env = child_settings(secret)
        pg_dsn = dsn.replace("postgresql+psycopg://", "postgresql://", 1)
        resource = {"volume_id": VOLUME, "container_id": None,
                    "api_pid": None, "web_pid": None}
        state = {**owner, "creation_trail": list(owner["creation_trail"]),
                 "cleanup_trail": list(owner["cleanup_trail"])}
        handles: dict = {}
        stage = "CONTAINER_CREATE"
        try:
            cid = create_container(EXPECTED_NONCE)
            resource["container_id"] = cid
            state["creation_trail"].append({"kind": "container", "id": cid,
                                            "recovery": True, "verify_only": True})
            verified_container(EXPECTED_NONCE, cid)
            if volume_identity(verified_volume(EXPECTED_NONCE)) != check["volume_identity"]:
                raise fail("AM4_VOLUME_CHANGED_AFTER_CREATE")
            stage = "DB_READINESS"
            from p5a2_source_demo_start import wait_db
            wait_db(pg_dsn)
            stage = "READ_ONLY_INVENTORY"
            before = inventory(pg_dsn, secret["viewer_password"])
            stage = "VERIFY_ONLY_GUARD"
            receipt, after = verify_only(
                before, lambda: post_seed_summary(pg_dsn, FINGERPRINT,
                                                  secret["viewer_password"],
                                                  SCHEMA_DIGEST))
            state["am4_pre_service_inventory"] = before
            state["am4_pre_service_summary"] = after
            stage = "API_WEB_START"
            start_services(NODE, env, resource, state, handles)
            record = resource_record("OWNED_RUNNING", EXPECTED_NONCE,
                                     **resource, image_id=IMAGE.removeprefix("sha256:"),
                                     db_fingerprint=FINGERPRINT)
            replace_lifecycle(state, record)
            state["am4_verify_result"] = receipt["result"]
            state["am4_verify_family"] = receipt["family_record"]
            write_owner(state)
            return {**record, "owner_record_digest": digest(state),
                    "owner_record_path": str(OWNER),
                    "pre_service_inventory": before,
                    "pre_service_summary": after,
                    "verification_state_digest": receipt["state_digest"],
                    "verification_family_record": receipt["family_record"],
                    "application_data_writes": 0}
        except Exception:
            adopted = _adopt_lost_create(resource, state, check["volume_identity"])
            cleaned = _cleanup(resource, state, handles) if adopted else False
            _record_failure(owner, state, resource, stage, cleaned,
                            reason="HEALTH_FAILED")
            raise fail("AM4_VERIFY_RUNTIME_FAILED_" + stage) from None


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print(json.dumps({"status": "REFUSED", "stage": "ARGUMENTS"}))
        return 1
    mode, owner_digest = sys.argv[1:3]
    try:
        if mode == "preflight" and len(sys.argv) == 3:
            result = am4_preflight(owner_digest)
            _node_ready()
        elif mode == "verify" and len(sys.argv) == 4:
            result = verify_runtime(owner_digest, sys.argv[3])
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
