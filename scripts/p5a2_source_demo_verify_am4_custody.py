"""AM4 exact retained owner and no-secret-read external preflight."""
from __future__ import annotations

from p5a2_source_demo_common import (CONTAINER, OWNER, PORTS, PROFILE, RUNTIME,
                                     VOLUME, digest, fail, port_free, read_owner)
from p5a2_source_demo_recovery_custody import (AM2_CONTAINER, EXPECTED_NONCE,
                                                EXPECTED_RUNTIME, SECRET,
                                                secret_custody, volume_identity)
from p5a2_source_demo_recovery_docker import (IMAGE, inspect, verified_image,
                                              verified_volume)

AM4_OWNER_DIGEST = "fe9b89263d8e4f17f87238940622bd73fa9598e3df70e23c46b5a80b4737f158"
AM4_VOLUME_IDENTITY = "7a9aebeaff0294132dde49494509a97a291de44811793cc845fa802f1e8aa304"
AM3_CONTAINER = "e8e2de751a2c5d068570c7717b8c8392ba3654442d95a7d93aca45297b09913d"
FIRST_CONTAINER = "fccef8401c3bceb3f8333418339d20f3f9f5d64c6535dfa08f64ab319ee28b3b"
RECOVERY_CONTAINER = "dee30bee86b3cd5395ca06188f586b869dbf329529701c296efa7c3b4bb49747"

CREATION_TRAIL = [
    {"kind": "volume", "id": VOLUME},
    {"kind": "container", "id": FIRST_CONTAINER},
    {"kind": "container", "id": RECOVERY_CONTAINER, "recovery": True},
    {"kind": "container", "id": AM2_CONTAINER, "recovery": True},
    {"kind": "api", "id": 12612}, {"kind": "web", "id": 38184},
    {"kind": "container", "id": AM3_CONTAINER, "recovery": True, "verify_only": True},
    {"kind": "api", "id": 13120}, {"kind": "web", "id": 16216},
]
CLEANUP_TRAIL = [
    {"kind": "container", "id": FIRST_CONTAINER},
    {"kind": "container", "id": RECOVERY_CONTAINER, "recovery": True},
    {"kind": "web", "id": 38184, "result": "ALREADY_ABSENT_VERIFIED", "am2": True},
    {"kind": "api", "id": 12612, "result": "ALREADY_ABSENT_VERIFIED", "am2": True},
    {"kind": "container", "id": AM2_CONTAINER,
     "result": "REMOVED_STOPPED_EXACT_OWNED", "am2": True},
    {"kind": "web", "id": 16216, "result": "HELD_HANDLE_EXIT_CONFIRMED", "am3": True},
    {"kind": "api", "id": 13120, "result": "HELD_HANDLE_EXIT_CONFIRMED", "am3": True},
    {"kind": "container", "id": AM3_CONTAINER,
     "result": "REMOVED_EXACT_OWNED", "am3": True},
]


def am4_owner_state(expected_digest: str) -> dict:
    if expected_digest != AM4_OWNER_DIGEST or RUNTIME.resolve() != EXPECTED_RUNTIME.resolve():
        raise fail("AM4_OWNER_DIGEST_INVALID")
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
            or owner.get("creation_trail") != CREATION_TRAIL
            or owner.get("cleanup_trail") != CLEANUP_TRAIL):
        raise fail("AM4_OWNER_STATE_INVALID")
    if (digest(owner) != expected_digest or not OWNER.is_file()
            or OWNER.is_symlink() or RUNTIME.is_symlink()):
        raise fail("AM4_OWNER_CUSTODY_INVALID")
    return owner


def am4_preflight(expected_digest: str) -> dict:
    am4_owner_state(expected_digest)
    verified_image()
    volume = verified_volume(EXPECTED_NONCE)
    actual_volume_identity = volume_identity(volume)
    if actual_volume_identity != AM4_VOLUME_IDENTITY:
        raise fail("AM4_VOLUME_CHANGED")
    if inspect("container", CONTAINER) is not None:
        raise fail("CONTAINER_CONFLICT")
    if not all(port_free(port) for port in PORTS.values()):
        raise fail("PORT_BUSY")
    secret_custody()
    return {"preflight": "PASS", "profile_id": PROFILE,
            "owner_nonce": EXPECTED_NONCE, "owner_digest": expected_digest,
            "volume_id": VOLUME, "volume_identity": actual_volume_identity,
            "image_id": IMAGE, "ports": PORTS}
