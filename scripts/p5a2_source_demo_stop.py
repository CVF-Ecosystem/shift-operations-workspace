"""Later explicit stop: re-probe exact owner resources, retain the volume."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import ctypes
from ctypes import wintypes
from contextlib import ExitStack, contextmanager

from p5a2_source_demo_common import (CONTAINER, LIFECYCLE_FIELDS, PROFILE, VOLUME, check_hex, check_pid,
                                     fail, inspect, labels_match, owner_lock, resource_record,
                                     process_command, process_start, read_owner, run, stop_refusal,
                                     write_owner)


def _replace(owner: dict, record: dict, trail: list) -> dict:
    context = {k: v for k, v in owner.items() if k not in LIFECYCLE_FIELDS}
    context["cleanup_trail"] = trail
    return {**context, **record}


@contextmanager
def _held_process(pid: int, saved_start: str, executable: str, token: str):
    """Hold a Windows kernel handle through identity check and termination."""
    if sys.platform != "win32" or not check_pid(pid) or not isinstance(executable, str):
        raise fail("PROCESS_PROOF_UNAVAILABLE")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD,
                                                   wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD))
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    kernel.TerminateProcess.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x1000 | 0x0001 | 0x00100000, False, pid)
    if not handle:
        raise fail("PROCESS_PROOF_UNAVAILABLE")
    try:
        size = wintypes.DWORD(32768)
        name = ctypes.create_unicode_buffer(size.value)
        if (not kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(size))
                or os.path.normcase(name.value) != os.path.normcase(executable)
                or process_start(pid) != saved_start or token not in process_command(pid)):
            raise fail("PID_REUSED")
        yield kernel, handle
    finally:
        kernel.CloseHandle(handle)


def _terminate(kernel, handle) -> None:
    if kernel.WaitForSingleObject(handle, 0) == 0:
        return
    if not kernel.TerminateProcess(handle, 1) and kernel.WaitForSingleObject(handle, 0) != 0:
        raise fail("PROCESS_STOP_FAILED")
    if kernel.WaitForSingleObject(handle, 5000) != 0:
        raise fail("PROCESS_STOP_FAILED")


def stop(nonce: str) -> dict:
    if not check_hex(nonce):
        raise fail("OWNER_NONCE_INVALID")
    with owner_lock():
        owner = read_owner()
        if owner is None:
            raise fail("OWNER_RECORD_ABSENT")
        if owner.get("owner_nonce") != nonce or owner.get("profile_id") != PROFILE:
            return stop_refusal(owner, nonce, "OWNER_MISMATCH")
        if owner.get("outcome") != "OWNED_RUNNING":
            return stop_refusal(owner, nonce, "UNKNOWN_RESOURCE")
        volume = inspect("volume", VOLUME)
        container = inspect("container", CONTAINER)
        if not volume or not container or not labels_match(volume, nonce) or not labels_match(container, nonce):
            return stop_refusal(owner, nonce, "FOREIGN_RESOURCE")
        if (container.get("Id") != owner.get("container_id")
                or container.get("Image") != "sha256:" + owner.get("image_id", "")
                or not container.get("State", {}).get("Running")):
            return stop_refusal(owner, nonce, "FOREIGN_RESOURCE")
        expected = (("api_pid", "api_start", "api_executable", "workspace_api.demo.app:create_app"),
                    ("web_pid", "web_start", "web_executable", "vite.js"))
        # Hold both exact process handles before the first stop effect.
        try:
            stack = ExitStack()
            held = {pid: stack.enter_context(_held_process(owner.get(pid), owner.get(start),
                        owner.get(exe), token)) for pid, start, exe, token in expected}
        except (RuntimeError, OSError):
            stack.close()
            return stop_refusal(owner, nonce, "PID_REUSED")
        trail = list(owner.get("cleanup_trail", []))
        remaining = {k: owner.get(k) for k in ("container_id", "volume_id", "api_pid", "web_pid")}
        with stack:
            for pid, _, _, _ in reversed(expected):
                value = owner[pid]
                try:
                    _terminate(*held[pid])
                except (RuntimeError, OSError):
                    partial = resource_record("PARTIAL_OWNED_FAILURE", nonce,
                        **remaining, image_id=owner["image_id"], reason="CLEANUP_FAILED")
                    write_owner(_replace(owner, partial, trail))
                    raise fail("CLEANUP_FAILED") from None
                trail.append({"kind": pid.removesuffix("_pid"), "id": value})
                remaining[pid] = None
        try:
            run(["docker", "stop", owner["container_id"]], timeout=30)
            checked = inspect("container", CONTAINER)
            if (not checked or checked.get("Id") != owner["container_id"]
                    or not labels_match(checked, nonce) or checked.get("State", {}).get("Running")):
                raise fail("STOP_VERIFICATION_FAILED")
            run(["docker", "rm", owner["container_id"]], timeout=30)
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            observed = inspect("container", CONTAINER)
            remaining["container_id"] = (owner["container_id"] if observed
                and observed.get("Id") == owner["container_id"]
                and labels_match(observed, nonce) else None)
            partial = resource_record("PARTIAL_OWNED_FAILURE", nonce,
                **remaining, image_id=owner["image_id"], reason="CLEANUP_FAILED")
            write_owner(_replace(owner, partial, trail))
            raise fail("CLEANUP_FAILED") from None
        checked = inspect("container", CONTAINER)
        retained_volume = inspect("volume", VOLUME)
        if checked is not None or retained_volume is None or not labels_match(retained_volume, nonce):
            remaining["container_id"] = (owner["container_id"] if checked
                and checked.get("Id") == owner["container_id"]
                and labels_match(checked, nonce) else None)
            partial = resource_record("PARTIAL_OWNED_FAILURE", nonce,
                **remaining, image_id=owner["image_id"], reason="CLEANUP_FAILED")
            write_owner(_replace(owner, partial, trail))
            raise fail("STOP_VERIFICATION_FAILED")
        trail.append({"kind": "container", "id": owner["container_id"]})
        stopped = {"stopped_container_id": owner["container_id"],
                   "stopped_api_pid": next(item["id"] for item in trail if item["kind"] == "api"),
                   "stopped_web_pid": next(item["id"] for item in trail if item["kind"] == "web")}
        record = resource_record("STOPPED_RETAINED", nonce, volume_id=VOLUME,
            image_id=owner["image_id"], db_fingerprint=owner["db_fingerprint"], stopped=stopped)
        write_owner(_replace(owner, record, trail))
        return record


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: p5a2_source_demo_stop.py OWNER_NONCE")
    try:
        result = stop(sys.argv[1])
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["outcome"] == "STOPPED_RETAINED" else 1)
    except Exception:
        print(json.dumps({"status": "STOP_FAILED", "reason": "STOP_FAILED"}))
        raise SystemExit(1)
