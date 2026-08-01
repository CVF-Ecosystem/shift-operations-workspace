#!/usr/bin/env python3
"""Live governance evidence for the incident vertical (P2A-INCIDENT-VERTICAL,
SPEC section 6/R14). Mirrors run_approval_governance_evidence.py's shape:
in-process refusal probes (observed zero provider calls each), then a genuine
authenticated R2 acknowledgement through the real FastAPI/JWT route chain,
followed by exactly one real, non-mocked provider call.

INC-REV-F5 (Amendment 1): provider HTTP, sanitization, safe endpoint
description, provider-call accounting and receipt rendering all live in
`_incident_live_evidence_support.py`; this module is the orchestration
facade and CLI entrypoint only.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

REPO_ROOT = Path(__file__).resolve().parents[1]
for _rel in (
    "apps/workspace-api/src",
    "packages/cvf-runtime/src",
    "packages/operations-ledger/src",
    "packages/operations-domain/src",
    "packages/ai-providers/alibaba",
):
    sys.path.insert(0, str(REPO_ROOT / _rel))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _incident_live_evidence_support import (  # noqa: E402
    ProviderCallCounter,
    call_provider,
    render_receipt,
    safe_endpoint_description,
)

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_INCIDENT_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_INCIDENT_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md"


def _new_ledger_shift_incident(risk_class="R2", *, evidence_count=1):
    from operations_domain.models import EvidenceRef, Incident, Shift
    from workspace_api.infrastructure.repository import InMemoryLedger

    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Live-evidence shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    incident = Incident(
        shift_id=shift.shift_id, risk_class=risk_class, summary="Live-evidence probe",
        evidence=[EvidenceRef(source_type="message", source_id=f"m{i}") for i in range(evidence_count)],
    )
    ledger.add_incident(incident)
    return ledger, incident


def _register_user(ledger, user_id, role, *, is_active=True, shift_id=None):
    import workspace_api.domain.models as _domain_models
    ledger.add_user(_domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role, is_active=is_active))
    if shift_id is not None:
        ledger.add_assignment(_domain_models.ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def _auth_headers(user_id: str, role: str) -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}


def _with_ledger(ledger, fn):
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app

    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        from fastapi.testclient import TestClient
        return fn(TestClient(app))
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def _rec(client, headers, incident_id):
    return client.post("/approvals", json={"record_type": "Incident", "action": "incident.acknowledge", "record_id": str(incident_id)}, headers=headers)


def _ack(client, headers, incident_id):
    return client.post(f"/incidents/{incident_id}/acknowledge", json={}, headers=headers)


def check_incident_gate(counter: ProviderCallCounter) -> list[dict]:
    """Refusal cases: each records the OBSERVED provider-call delta on the
    shared counter (SPEC R15-B), never a hard-coded literal - none of these
    code paths can reach call_provider, and this proves it empirically
    rather than assuming it."""
    results: list[dict] = []

    def _case(name, ledger, run):
        before = counter.count
        res = _with_ledger(ledger, run)
        outcome = "PASS" if res.status_code == 409 else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    ledger, incident = _new_ledger_shift_incident(evidence_count=0)
    _register_user(ledger, "inc-ev-sup1", "shift_supervisor", shift_id=incident.shift_id)
    _case("insufficient_evidence_rejected", ledger, lambda c: _ack(c, _auth_headers("inc-ev-sup1", "shift_supervisor"), incident.incident_id))

    ledger, incident = _new_ledger_shift_incident()
    _register_user(ledger, "inc-ev-sup1", "shift_supervisor", shift_id=incident.shift_id)
    _case("fabricated_approval_rejected", ledger, lambda c: _ack(c, _auth_headers("inc-ev-sup1", "shift_supervisor"), incident.incident_id))

    ledger, incident = _new_ledger_shift_incident()
    _register_user(ledger, "inc-ev-sup1", "shift_supervisor", shift_id=incident.shift_id)

    def _self(client):
        headers = _auth_headers("inc-ev-sup1", "shift_supervisor")
        _rec(client, headers, incident.incident_id)
        return _ack(client, headers, incident.incident_id)

    _case("self_approval_rejected", ledger, _self)

    ledger, incident = _new_ledger_shift_incident()
    _register_user(ledger, "inc-ev-sup2", "shift_supervisor", shift_id=incident.shift_id)
    _register_user(ledger, "inc-ev-sup1", "shift_supervisor", shift_id=incident.shift_id)

    def _inactive(client):
        _rec(client, _auth_headers("inc-ev-sup2", "shift_supervisor"), incident.incident_id)
        ledger.users["inc-ev-sup2"].is_active = False
        return _ack(client, _auth_headers("inc-ev-sup1", "shift_supervisor"), incident.incident_id)

    _case("inactive_approver_rejected", ledger, _inactive)

    ledger, incident = _new_ledger_shift_incident()
    _register_user(ledger, "inc-ev-sup2", "shift_supervisor", shift_id=incident.shift_id)
    _register_user(ledger, "inc-ev-sup1", "shift_supervisor", shift_id=incident.shift_id)

    def _stale(client):
        _rec(client, _auth_headers("inc-ev-sup2", "shift_supervisor"), incident.incident_id)
        stale = ledger.get_incident(incident.incident_id)
        stale.version += 1
        ledger.put_incident(stale)
        return _ack(client, _auth_headers("inc-ev-sup1", "shift_supervisor"), incident.incident_id)

    _case("stale_version_rejected", ledger, _stale)

    return results


def build_and_acknowledge_genuine() -> tuple[bool, str]:
    """Construct a genuine authenticated R2 acknowledgement via minted JWTs
    and real HTTP requests (SPEC R14)."""
    ledger, incident = _new_ledger_shift_incident()
    _register_user(ledger, "inc-ev-sup2", "shift_supervisor", shift_id=incident.shift_id)
    _register_user(ledger, "inc-ev-sup1", "shift_supervisor", shift_id=incident.shift_id)

    def _run(client):
        r1 = client.post(
            "/approvals",
            json={"record_type": "Incident", "action": "incident.acknowledge", "record_id": str(incident.incident_id)},
            headers=_auth_headers("inc-ev-sup2", "shift_supervisor"),
        )
        if r1.status_code != 201:
            return False, f"receipt failed: {r1.status_code}"
        ack = client.post(f"/incidents/{incident.incident_id}/acknowledge", json={}, headers=_auth_headers("inc-ev-sup1", "shift_supervisor"))
        if ack.status_code != 200:
            return False, f"acknowledge failed with HTTP {ack.status_code}"
        if ack.json()["status"] != "ACKNOWLEDGED":
            return False, f"acknowledge status={ack.json()['status']}"
        return True, "distinct authenticated approver (inc-ev-sup2) and confirmer (inc-ev-sup1) satisfied the R2 quorum via minted JWTs and HTTP requests"

    return _with_ledger(ledger, _run)


def _key_present() -> tuple[bool, str | None]:
    for name in KEY_ENV_NAMES:
        if os.environ.get(name, "").strip():
            return True, name
    return False, None


def _endpoint() -> str:
    base_url = next(
        (os.environ[n].strip() for n in BASE_URL_ENV_NAMES if os.environ.get(n, "").strip()),
        DEFAULT_BASE_URL,
    ).rstrip("/")
    return base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"


def main() -> int:
    parser = argparse.ArgumentParser(description="Incident live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    counter = ProviderCallCounter()  # fresh per invocation (SPEC R15-B)

    print("== incident approval gate: refusal cases ==")
    gate_results = check_incident_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("INCIDENT GATE REFUSAL CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine authenticated acknowledgement ==")
    ack_ok, ack_detail = build_and_acknowledge_genuine()
    print(f"  {ack_detail}")
    if not ack_ok:
        print("GENUINE ACKNOWLEDGEMENT CONSTRUCTION FAILED", file=sys.stderr)
        return 1

    present, key_env_name = _key_present()
    print(f"== provider credential present: {present} ==")
    if args.dry_run:
        return 0
    if not present:
        print("READY_FOR_LIVE_EVIDENCE: no provider key", file=sys.stderr)
        return 2

    try:
        from select_model import select_model
        model = select_model()
    except Exception as exc:
        print(f"READY_FOR_LIVE_EVIDENCE: model select failed: {exc}", file=sys.stderr)
        return 2

    endpoint = _endpoint()
    safe_endpoint = safe_endpoint_description(endpoint)
    print(f"== calling provider (model={model}, endpoint={safe_endpoint}) ==")
    provider_result = call_provider(
        model=model, api_key=os.environ[key_env_name], endpoint=endpoint,
        prompt=PROMPT, expected_token=EXPECTED_TOKEN, counter=counter,
    )
    print(f"  outcome: {provider_result['outcome']} (http {provider_result.get('http_status')})")
    render_receipt(
        RECEIPT_PATH, gate_results=gate_results, quorum_detail=ack_detail,
        provider_result=provider_result, model=model, safe_endpoint=safe_endpoint,
        call_count=counter.count,
    )

    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
