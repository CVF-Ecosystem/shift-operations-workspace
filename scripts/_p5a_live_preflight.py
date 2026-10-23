"""Credential-free P5-A A7 source, gate, and synthetic API preflight."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from _p5a_live_contract import ADMISSION_ID, ENDPOINT, MODEL, sha256, strict_json

ROOT = Path(__file__).resolve().parents[1]
ADMISSION = ROOT / "docs/decisions/P5A_REPORTING_ENGINE_LIVE_ADMISSION_2026-10-23.json"
LOCAL_EVIDENCE = ROOT / "docs/decisions/P5A_REPORTING_ENGINE_LOCAL_EVIDENCE_2026-10-23.json"
ADMISSION_SHA = "87595a703e06b9e4267a843d15ef900efdf77bca0c070cf3e72f6acec5e7fd0b"
CHECKS = ("admission", "local_evidence", "source_binding", "clean_worktree",
          "inheritance", "invariant_family", "api_probe")
LIVE_FILES = (
    "scripts/run_p5a_live_governance_evidence.py",
    "scripts/_p5a_live_contract.py",
    "scripts/_p5a_live_preflight.py",
    "scripts/_p5a_live_transport.py",
)
API_FILES = (
    "apps/workspace-api/src/workspace_api/main.py",
    "apps/workspace-api/src/workspace_api/dependencies.py",
    "apps/workspace-api/src/workspace_api/auth/tokens.py",
    "apps/workspace-api/src/workspace_api/api/reports/router.py",
    "apps/workspace-api/src/workspace_api/application/report_export.py",
    "apps/workspace-api/src/workspace_api/application/report_service.py",
    "apps/workspace-api/src/workspace_api/application/assignment_scope.py",
    "apps/workspace-api/src/workspace_api/infrastructure/repository.py",
)
SOURCE_DIRS = (
    "apps/workspace-api/src", "apps/workspace-worker/src", "apps/integration-edge/src",
    "packages/identity-mapping/src", "packages/conversation-routing/src",
    "packages/channel-sdk/src", "packages/channel-adapters/src",
    "packages/application-memory/src", "packages/cvf-runtime/src",
    "packages/operations-ledger/src", "packages/operations-domain/src",
    "packages/refinery-bridge/src", "packages/retrieval-contracts/src",
    "packages/governed-retrieval/src", "packages/ai-gateway/src",
    "packages/governed-rag/src", "packages/ai-providers/src",
    "packages/reporting-engine/src",
)


def _universal(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL,
                                   timeout=20)


def _blob_hash(path: str) -> str:
    blob = _git("show", f"HEAD:{path}")
    return sha256(blob if path.endswith((".ttf", "LICENSE_DEJAVU")) else _universal(blob))


def _check_admission() -> dict:
    data = ADMISSION.read_bytes()
    if sha256(_universal(data)) != ADMISSION_SHA:
        raise ValueError("ADMISSION_MISMATCH")
    value = strict_json(data)
    expected = {
        "admissionId": ADMISSION_ID, "status": "HUMAN_APPROVED_SOURCE_REVIEW_PENDING",
        "model": MODEL, "endpoint": ENDPOINT, "credentialSource":
        "Windows CurrentUser Environment/ALIBABA_API_KEY",
        "classification": "PUBLIC_SYNTHETIC_ONLY", "maxProviderAttempts": 1,
        "maxOutputTokens": 64, "maxInputTokensReserved": 256, "maxRetries": 0,
        "allowRedirects": False, "allowFallback": False, "timeoutSeconds": 60,
        "payAsYouGoCeilingUsd": "0.01",
    }
    if not isinstance(value, dict) or any(value.get(k) != v for k, v in expected.items()):
        raise ValueError("ADMISSION_MISMATCH")
    if value.get("humanApproval", {}).get("answer") != "Cho phép đúng giới hạn trên":
        raise ValueError("ADMISSION_MISMATCH")
    return value


def _check_evidence(admission: dict) -> dict:
    data = LOCAL_EVIDENCE.read_bytes()
    if sha256(_universal(data)) != admission["localEvidenceCanonicalSha256"]:
        raise ValueError("LOCAL_EVIDENCE_MISMATCH")
    value = strict_json(data)
    if not isinstance(value, dict) or value.get("materialCommit") != admission["localProductMaterialCommit"]:
        raise ValueError("LOCAL_EVIDENCE_MISMATCH")
    return value


def _check_sources(evidence: dict) -> tuple[str, dict[str, str]]:
    commit = _git("rev-parse", "HEAD").decode().strip()
    if not commit or not _git("merge-base", "--is-ancestor", evidence["materialCommit"], commit) == b"":
        raise ValueError("SOURCE_HASH_MISMATCH")
    old = evidence["committedSourceBinding"]["sourceSha256"]
    hashes = {}
    for path, expected in old.items():
        actual = _blob_hash(path)
        if actual != expected:
            raise ValueError("SOURCE_HASH_MISMATCH")
        hashes[path] = actual
    for path in LIVE_FILES + API_FILES:
        hashes[path] = _blob_hash(path)
    return commit, dict(sorted(hashes.items()))


def _check_clean() -> None:
    if _git("status", "--porcelain=v1", "--untracked-files=all").strip():
        raise ValueError("WORKTREE_DIRTY")


def _check_script(script: str, expected: str) -> None:
    arguments = [sys.executable, str(ROOT / script)]
    if "inheritance" in script:
        arguments.append("--enforce")
    result = subprocess.run(arguments, cwd=ROOT,
                            capture_output=True, text=True, timeout=45, check=False)
    if result.returncode != 0 or expected not in result.stdout:
        raise ValueError("INHERITANCE_CHECK_FAILED" if "inheritance" in script
                         else "INVARIANT_CHECK_FAILED")


def _probe_env() -> dict[str, str]:
    names = ("SystemRoot", "WINDIR", "PATH", "TEMP", "TMP")
    result = {name: os.environ[name] for name in names if name in os.environ}
    result["JWT_SECRET_KEY"] = "p5a-a7-synthetic-local-only-20261024"
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    return result


def _run_api_probe() -> list[dict]:
    # BaseSettings in the production composition declares env_file='.env'.
    # Refuse before import rather than reading any root dotenv contents.
    if os.path.lexists(ROOT / ".env"):
        raise ValueError("API_PROBE_MISMATCH")
    runner = ROOT / "scripts/run_p5a_live_governance_evidence.py"
    result = subprocess.run([sys.executable, "-I", str(runner), "--_gate-child"],
                            cwd=ROOT, env=_probe_env(), capture_output=True, timeout=45, check=False)
    if result.returncode != 0:
        raise ValueError("API_PROBE_MISMATCH")
    value = strict_json(result.stdout)
    if not isinstance(value, list) or [item.get("status") for item in value] != [401, 404, 422, 200]:
        raise ValueError("API_PROBE_MISMATCH")
    if [item.get("case") for item in value] != ["missing_bearer", "unknown_report",
                                                "invalid_option", "valid_pdf"]:
        raise ValueError("API_PROBE_MISMATCH")
    good = value[-1]
    if good.get("mime") != "application/pdf" or not good.get("byte_count", 0) > 0:
        raise ValueError("API_PROBE_MISMATCH")
    if good.get("before_digest") != good.get("after_digest"):
        raise ValueError("API_PROBE_MISMATCH")
    return value


def run_preflight() -> tuple[dict, str | None]:
    envelope: dict = {
        "schema_version": "1.0", "status": "PARTIAL_PREFLIGHT", "commit": None,
        "clean_worktree": False, "source_hashes": {},
        "checks": [{"name": name, "state": "NOT_RUN", "reason": None} for name in CHECKS],
        "api_observations": [],
    }
    try:
        admission = _check_admission()
        envelope["checks"][0]["state"] = "PASS"
        evidence = _check_evidence(admission)
        envelope["checks"][1]["state"] = "PASS"
        commit, hashes = _check_sources(evidence)
        envelope.update(commit=commit, source_hashes=hashes)
        envelope["checks"][2]["state"] = "PASS"
        _check_clean()
        envelope["clean_worktree"] = True
        envelope["checks"][3]["state"] = "PASS"
        _check_script("scripts/check_cvf_core_machine_inheritance.py", "COMPLIANT")
        envelope["checks"][4]["state"] = "PASS"
        _check_script("scripts/check_invariant_families.py", "INVARIANT FAMILY CHECK: PASS")
        envelope["checks"][5]["state"] = "PASS"
        envelope["api_observations"] = _run_api_probe()
        envelope["checks"][6]["state"] = "PASS"
        envelope["local_full_gate_result"] = evidence["fullPrecommit"]["result"]
        envelope["status"] = "COMPLETE"
        return envelope, None
    except (OSError, ValueError, subprocess.SubprocessError, KeyError, TypeError) as exc:
        index = next((i for i, item in enumerate(envelope["checks"])
                      if item["state"] == "NOT_RUN"), len(CHECKS) - 1)
        reason = str(exc)
        if reason not in {"ADMISSION_MISMATCH", "LOCAL_EVIDENCE_MISMATCH",
                          "SOURCE_HASH_MISMATCH", "WORKTREE_DIRTY", "INHERITANCE_CHECK_FAILED",
                          "INVARIANT_CHECK_FAILED", "API_PROBE_MISMATCH"}:
            reason = ("ADMISSION_MISMATCH", "LOCAL_EVIDENCE_MISMATCH", "SOURCE_HASH_MISMATCH",
                      "WORKTREE_DIRTY", "INHERITANCE_CHECK_FAILED", "INVARIANT_CHECK_FAILED",
                      "API_PROBE_MISMATCH")[index]
        envelope["checks"][index].update(state="FAIL", reason=reason)
        return envelope, reason


def gate_child() -> list[dict]:
    """Run only the real local FastAPI route on a disposable synthetic ledger."""
    for relative in SOURCE_DIRS:
        sys.path.insert(0, str(ROOT / relative))
    from cvf_runtime.identity import Principal
    from fastapi.testclient import TestClient
    from operations_domain.assignment_models import ShiftAssignment
    from operations_domain.models import Shift
    from operations_domain.report_digest import canonical_bytes as report_bytes
    from workspace_api.application.report_service import ReportService
    from workspace_api.auth.tokens import create_access_token
    from workspace_api.dependencies import get_ledger
    from workspace_api.infrastructure.repository import InMemoryLedger, User
    from workspace_api.main import app

    ledger = InMemoryLedger()
    now = datetime.now(UTC)
    shift = Shift(name="PUBLIC synthetic A7", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    ledger.add_user(User(user_id="a7-op", username="a7-op", password_hash="x", role="operator"))
    ledger.add_assignment(ShiftAssignment(
        shift_id=shift.shift_id, user_id="a7-op", assigned_by="a7-op"))
    ledger.close_shift(shift.shift_id)
    report = ReportService(ledger).generate(shift.shift_id, Principal(user_id="a7-op", role="operator"))
    record = lambda: sha256(report_bytes(ledger.get_report(report.report_id).model_dump(mode="json")))
    before = record()
    bearer = {"Authorization": "Bearer " + create_access_token(Principal(user_id="a7-op", role="operator"))}
    path = f"/reports/{report.report_id}/export"
    query = {"format": "pdf", "view": "shift-summary"}
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        with TestClient(app) as client:
            missing = client.get(path, params=query)
            unknown = client.get(f"/reports/{uuid4()}/export", params=query, headers=bearer)
            invalid = client.get(path, params={"format": "bad", "view": "bad"}, headers=bearer)
            good = client.get(path, params=query, headers=bearer)
        if (missing.status_code, unknown.status_code, invalid.status_code, good.status_code) != (401, 404, 422, 200):
            raise ValueError("API_PROBE_MISMATCH")
        if (missing.json().get("detail") != "Missing bearer token"
                or unknown.json().get("detail") != "Report not found"
                or invalid.json().get("detail", {}).get("code") != "EXPORT_INVALID_PARAMETER"):
            raise ValueError("API_PROBE_MISMATCH")
        after = record()
        if before != after or not good.content.startswith(b"%PDF"):
            raise ValueError("API_PROBE_MISMATCH")
        return [
            {"case": "missing_bearer", "status": 401, "error_code": None,
             "derived_classification": "AUTH_REFUSED"},
            {"case": "unknown_report", "status": 404, "error_code": None,
             "derived_classification": "NOT_FOUND"},
            {"case": "invalid_option", "status": 422, "error_code": "EXPORT_INVALID_PARAMETER"},
            {"case": "valid_pdf", "status": 200, "mime": good.headers["content-type"].split(";")[0],
             "byte_count": len(good.content), "sha256": sha256(good.content),
             "before_digest": before, "after_digest": after},
        ]
    finally:
        app.dependency_overrides.pop(get_ledger, None)
