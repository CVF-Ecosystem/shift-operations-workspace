"""Sanitized, bounded test-only observation of the real Windows ACL child."""
import base64
import json
import re
import subprocess
import time


STAGES = {"ENTRY", "IDENTITY", "EXIT_PASS", "EXIT_FAIL"} | {
    f"{stage}_{index}" for stage in ("READ", "OWNER", "RULES", "ENUMERATION", "CHECK")
    for index in (1, 2)
}


def staged_script(encoded, epoch_ms):
    """Add progress writes around exact read-only statements; fail on drift."""
    script = base64.b64decode(encoded, validate=True).decode("utf-16le")
    anchors = [
        ("try {", "try {\n  Write-CvfStage 'ENTRY'"),
        ("  $userSid =", "  Write-CvfStage 'IDENTITY'\n  $userSid ="),
        ("  foreach ($path in @(", "  $cvfIndex = 0\n  foreach ($path in @("),
        ("    $acl = Get-Acl", "    $cvfIndex++\n    Write-CvfStage ('READ_' + $cvfIndex)\n    $acl = Get-Acl"),
        ("    if (-not $acl.AreAccessRulesProtected", "    Write-CvfStage ('OWNER_' + $cvfIndex)\n    if (-not $acl.AreAccessRulesProtected"),
        ("    $rules = $acl.GetAccessRules", "    Write-CvfStage ('RULES_' + $cvfIndex)\n    $rules = $acl.GetAccessRules"),
        ("    foreach ($rule in $rules)", "    Write-CvfStage ('ENUMERATION_' + $cvfIndex)\n    foreach ($rule in $rules)"),
        ("    if (-not $ownerFull)", "    Write-CvfStage ('CHECK_' + $cvfIndex)\n    if (-not $ownerFull)"),
        ("  'PASS'", "  Write-CvfStage 'EXIT_PASS'\n  'PASS'"),
        ("} catch { 'FAIL' }", "} catch { Write-CvfStage 'EXIT_FAIL'; 'FAIL' }"),
    ]
    for old, new in anchors:
        if script.count(old) != 1:
            raise ValueError("diagnostic anchor drift")
        script = script.replace(old, new, 1)
    prefix = f"""
function Write-CvfStage([string]$stage) {{
  $elapsed = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - {epoch_ms}
  [Console]::Out.WriteLine('ACL_STAGE|' + $stage + '|' + $elapsed)
  [Console]::Out.Flush()
}}
"""
    return base64.b64encode((prefix + script).encode("utf-16le")).decode("ascii")


def emit_probe(output, elapsed, outcome):
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    lines = (output or "").splitlines()
    stages = []
    for line in lines:
        match = re.fullmatch(r"ACL_STAGE\|([A-Z_0-9]+)\|([0-9]{1,9})", line)
        if match and match[1] in STAGES:
            stages.append({"stage": match[1], "elapsed_ms": int(match[2])})
    print("ACL_STAGED_DIAGNOSTIC " + json.dumps({
        "elapsed": round(elapsed, 3), "outcome": outcome, "stages": stages,
        "stdout_class": lines[-1] if lines and lines[-1] in {"PASS", "FAIL"} else "OTHER",
    }))


def probe_acl_child(real_run, argv, kwargs):
    started = time.monotonic()
    try:
        copied = list(argv)
        index = copied.index("-EncodedCommand") + 1
        copied[index] = staged_script(copied[index], int(time.time() * 1000))
        result = real_run(copied, **(kwargs | {"timeout": 90}))
    except subprocess.TimeoutExpired as exc:
        emit_probe(exc.stdout, time.monotonic() - started, "TIMEOUT")
    except (OSError, ValueError, UnicodeError):
        emit_probe(None, time.monotonic() - started, "OTHER")
    else:
        emit_probe(result.stdout, time.monotonic() - started,
                   "EXIT_ZERO" if result.returncode == 0 else "EXIT_NONZERO")


def install_acl_observer(monkeypatch, child_module):
    real_run = child_module.run
    probed = False

    def observe(argv, **kwargs):
        nonlocal probed
        if "-EncodedCommand" not in argv:
            return real_run(argv, **kwargs)
        started = time.monotonic()
        try:
            result = real_run(argv, **kwargs)
        except (subprocess.TimeoutExpired, OSError) as exc:
            print("ACL_CHILD_DIAGNOSTIC " + json.dumps({
                "elapsed": round(time.monotonic() - started, 3),
                "outcome": "TIMEOUT" if isinstance(exc, subprocess.TimeoutExpired) else "OSERROR",
            }))
            if isinstance(exc, subprocess.TimeoutExpired) and not probed:
                probed = True
                probe_acl_child(real_run, argv, kwargs)
            raise
        output = result.stdout.strip()
        print("ACL_CHILD_DIAGNOSTIC " + json.dumps({
            "elapsed": round(time.monotonic() - started, 3),
            "returncode": result.returncode,
            "stdout_class": output if output in {"PASS", "FAIL"} else "OTHER",
            "stderr_present": bool(result.stderr),
        }))
        return result

    monkeypatch.setattr(child_module, "run", observe)
