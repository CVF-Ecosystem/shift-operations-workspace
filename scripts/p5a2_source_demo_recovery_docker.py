"""Exact local Docker identity checks for retained-volume recovery."""
from __future__ import annotations

import json
import subprocess
import sys

from p5a2_source_demo_common import CONTAINER, PROFILE, PROJECT, ROOT, VOLUME, child_env, fail

DOCKER = "C:/Users/DELL/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe"
HOST = "npipe:////./pipe/dockerDesktopLinuxEngine"
IMAGE = "sha256:f4610795587492cd4fb887c2dc3de301b813278bb6f616992061141b5f15ac36"
PGDATA = "/var/lib/postgresql/data"


def docker(*args: str, timeout: int = 30) -> str:
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        result = subprocess.run([DOCKER, "--host", HOST, *args], cwd=ROOT,
                                env=child_env(), capture_output=True, text=True,
                                timeout=timeout, creationflags=flags)
    except (OSError, subprocess.TimeoutExpired):
        raise fail("DOCKER_UNAVAILABLE") from None
    if result.returncode:
        # Never echo command output: it can include environment or resource data.
        raise fail("DOCKER_COMMAND_FAILED")
    return result.stdout.strip()


def inspect(kind: str, name: str) -> dict | None:
    if kind not in {"container", "volume", "image"}:
        raise fail("INSPECT_KIND_INVALID")
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        result = subprocess.run([DOCKER, "--host", HOST, kind, "inspect", name],
                                cwd=ROOT, env=child_env(), capture_output=True,
                                text=True, timeout=15, creationflags=flags)
    except (OSError, subprocess.TimeoutExpired):
        raise fail("DOCKER_UNAVAILABLE") from None
    if result.returncode:
        if "No such " + kind in result.stderr:
            return None
        raise fail("DOCKER_INSPECT_FAILED")
    try:
        items = json.loads(result.stdout)
        if isinstance(items, list) and len(items) == 1 and isinstance(items[0], dict):
            return items[0]
    except (TypeError, ValueError):
        pass
    raise fail("DOCKER_INSPECT_INVALID")


def verified_volume(nonce: str) -> dict:
    volume = inspect("volume", VOLUME)
    if volume is None:
        raise fail("VOLUME_ABSENT")
    labels = volume.get("Labels")
    if (not isinstance(labels, dict) or labels.get("cvf.project") != PROJECT
            or labels.get("cvf.profile") != PROFILE
            or labels.get("cvf.owner-nonce") != nonce
            or volume.get("Name") != VOLUME
            or volume.get("Driver") != "local"
            or not isinstance(volume.get("Mountpoint"), str)
            or not volume.get("Mountpoint")):
        raise fail("VOLUME_IDENTITY_INVALID")
    return volume


def verified_image() -> None:
    image = inspect("image", IMAGE)
    if image is None or image.get("Id") != IMAGE:
        raise fail("IMAGE_IDENTITY_INVALID")


def verified_container(nonce: str, expected_id: str, *, running: bool = True) -> dict:
    item = inspect("container", CONTAINER)
    if item is None or item.get("Id") != expected_id or item.get("Image") != IMAGE:
        raise fail("CONTAINER_IDENTITY_INVALID")
    labels = item.get("Config", {}).get("Labels")
    if (not isinstance(labels, dict) or labels.get("cvf.project") != PROJECT
            or labels.get("cvf.profile") != PROFILE
            or labels.get("cvf.owner-nonce") != nonce):
        raise fail("CONTAINER_LABEL_INVALID")
    mounts = item.get("Mounts")
    if (not isinstance(mounts, list) or len(mounts) != 1
            or mounts[0].get("Type") != "volume"
            or mounts[0].get("Name") != VOLUME
            or mounts[0].get("Destination") != PGDATA
            or mounts[0].get("RW") is not True):
        raise fail("CONTAINER_MOUNT_INVALID")
    bindings = item.get("HostConfig", {}).get("PortBindings")
    if bindings != {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "5433"}]}:
        raise fail("CONTAINER_PORT_INVALID")
    if running and not item.get("State", {}).get("Running"):
        raise fail("CONTAINER_NOT_RUNNING")
    return item


def create_container(nonce: str) -> str:
    # Bypass the official image entrypoint: it may initdb an empty volume.
    # PG_VERSION must be the retained v16 cluster before postgres is exec'd.
    guard = (f'test "$(cat {PGDATA}/PG_VERSION 2>/dev/null)" = 16 '
             f'&& exec gosu postgres postgres -D {PGDATA}')
    cid = docker("run", "--detach", "--name", CONTAINER, "--pull", "never",
                 "--network", "bridge", "--publish", "127.0.0.1:5433:5432",
                 "--mount", f"type=volume,source={VOLUME},target={PGDATA}",
                 "--label", f"cvf.project={PROJECT}",
                 "--label", f"cvf.profile={PROFILE}",
                 "--label", f"cvf.owner-nonce={nonce}",
                 "--entrypoint", "/bin/sh", IMAGE, "-ec", guard, timeout=90)
    if len(cid) != 64 or any(char not in "0123456789abcdef" for char in cid):
        raise fail("CONTAINER_CREATE_ID_INVALID")
    return cid


def remove_container(nonce: str, cid: str) -> None:
    item = verified_container(nonce, cid, running=False)
    if item.get("State", {}).get("Running"):
        docker("stop", cid, timeout=30)
    verified_container(nonce, cid, running=False)
    docker("rm", cid, timeout=30)
    if inspect("container", CONTAINER) is not None:
        raise fail("CONTAINER_REMOVE_UNVERIFIED")
