"""One-use Windows marker, CurrentUser key lookup, and bounded single POST.

No function in this module executes at import. The root-owned explicit effect
calls these only after the committed-source and local-gate preflight passes.
"""

from __future__ import annotations

import ctypes
import hashlib
import multiprocessing
import os
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from _p5a_live_contract import canonical_bytes

ROOT = Path(__file__).resolve().parents[1]
MARKER = ROOT / "docs/decisions/P5A_REPORTING_ENGINE_LIVE_ATTEMPT_2026-10-23.json"
RECEIPT = ROOT / "docs/decisions/P5A_REPORTING_ENGINE_LIVE_EVIDENCE_2026-10-23.json"
MAX_RESPONSE_BYTES = 65_536


class MarkerError(RuntimeError):
    def __init__(self, reason: str, reserved: bool):
        super().__init__(reason)
        self.reason = reason
        self.reserved = reserved


def marker_present() -> bool:
    """A dangling marker or uncertain access is a spent/unknown reservation."""
    try:
        MARKER.lstat()
    except FileNotFoundError:
        return False
    except OSError:
        return True
    return True


def reserve_marker(admission_id: str, commit: str, digest: str) -> None:
    """Windows CREATE_NEW + write-through + file flush, without reset path."""
    if sys.platform != "win32":
        raise MarkerError("MARKER_RESERVATION_FAILED", reserved=False)
    data = canonical_bytes({
        "version": "1.0", "admission_id": admission_id, "reviewed_commit": commit,
        "gate_observation_sha256": digest, "reserved_at_utc": datetime.now(UTC).isoformat(),
    }) + b"\n"
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                                   ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                   ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.WriteFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
    kernel.WriteFile.restype = ctypes.c_int
    kernel.FlushFileBuffers.argtypes = [ctypes.c_void_p]
    kernel.FlushFileBuffers.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    handle = kernel.CreateFileW(str(MARKER), 0x40000000, 0, None, 1, 0x80000000, None)
    if handle == ctypes.c_void_p(-1).value:
        error = ctypes.get_last_error()
        if error in (80, 183) or marker_present():
            raise MarkerError("MARKER_ALREADY_EXISTS", reserved=True)
        raise MarkerError("MARKER_RESERVATION_FAILED", reserved=False)
    try:
        written = ctypes.c_uint32()
        buffer = ctypes.create_string_buffer(data)
        if not kernel.WriteFile(handle, buffer, len(data), ctypes.byref(written), None):
            raise MarkerError("MARKER_CREATE_AMBIGUOUS", reserved=True)
        if written.value != len(data):
            raise MarkerError("MARKER_CREATE_AMBIGUOUS", reserved=True)
        if not kernel.FlushFileBuffers(handle):
            raise MarkerError("MARKER_SYNC_FAILED", reserved=True)
    finally:
        kernel.CloseHandle(handle)


def read_current_user_key() -> str:
    """Only post-marker explicit effect may call this; no process-env fallback."""
    if sys.platform != "win32":
        raise ValueError("KEY_READ_FAILED")
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as handle:
            value, kind = winreg.QueryValueEx(handle, "ALIBABA_API_KEY")
    except FileNotFoundError as exc:
        raise ValueError("KEY_MISSING") from exc
    except OSError as exc:
        raise ValueError("KEY_READ_FAILED") from exc
    if kind != winreg.REG_SZ or not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("KEY_READ_FAILED")
    return value


def _child_post(endpoint: str, body: bytes, key: str, expiry: float, started, conn) -> None:
    """The only transport site. The key reaches this child over spawn IPC only."""
    try:
        runtime = {name: os.environ[name] for name in ("SystemRoot", "WINDIR", "PATH", "TEMP", "TMP")
                   if name in os.environ}
        os.environ.clear()
        os.environ.update(runtime)
        import httpx

        digest = hashlib.sha256()
        saved = bytearray()
        count = 0
        with httpx.Client(verify=True, trust_env=False, follow_redirects=False,
                          timeout=httpx.Timeout(60.0)) as client:
            if time.monotonic() >= expiry:
                conn.send({"kind": "timeout"})
                return
            started.set()  # exactly before the sole POST invocation
            with client.stream("POST", endpoint, content=body, headers={
                "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                "Accept-Encoding": "identity",
            }) as response:
                for chunk in response.iter_bytes():
                    count += len(chunk)
                    digest.update(chunk)
                    if count <= MAX_RESPONSE_BYTES:
                        saved.extend(chunk)
                conn.send({"kind": "response", "status": response.status_code,
                           "size": count, "sha256": digest.hexdigest(),
                           "body": bytes(saved) if count <= MAX_RESPONSE_BYTES else None})
    except Exception:  # noqa: BLE001 -- provider exceptions must not cross IPC
        try:
            conn.send({"kind": "transport_error"})
        except (BrokenPipeError, OSError):
            pass
    finally:
        conn.close()


def one_post(endpoint: str, body: bytes, key: str, *, deadline_seconds: float = 60.0) -> dict:
    """Hard provider window including spawn, DNS, TLS, POST, read, and IPC.

    The marker remains spent even if the child never signals POST. The returned
    attempted bit is the child's immediately-before-POST signal. Child cleanup
    may take a small bounded interval after the provider window has expired.
    """
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    started = ctx.Event()
    began = time.monotonic()
    expiry = began + deadline_seconds
    process = ctx.Process(target=_child_post, args=(endpoint, body, key, expiry, started, child),
                          daemon=True)
    launched = False
    result: dict = {"kind": "transport_error"}
    try:
        process.start()
        launched = True
        child.close()
        remaining = max(0.0, expiry - time.monotonic())
        box: list[object] = []

        def receive() -> None:
            try:
                if parent.poll(remaining):
                    box.append(parent.recv())
            except (EOFError, OSError):
                pass

        watcher = threading.Thread(target=receive, daemon=True)
        watcher.start()
        watcher.join(max(0.0, expiry - time.monotonic()))
        if watcher.is_alive():
            result = {"kind": "timeout"}
        else:
            process.join(timeout=max(0.0, expiry - time.monotonic()))
            result = box[0] if box else {"kind": "transport_error"}
    except (OSError, RuntimeError):
        result = {"kind": "transport_error"}
    finally:
        if launched and process.is_alive():
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=3)
            if process.is_alive():
                raise RuntimeError("transport child did not terminate")
        parent.close()
        child.close()
    return {**result, "attempted": started.is_set()}
