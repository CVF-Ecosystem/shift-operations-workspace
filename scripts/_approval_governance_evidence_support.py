"""Support helpers for `run_approval_governance_evidence.py`.

Split out (CVF-FILE-SPLIT-GUARD-HARDENING) to keep the entrypoint script under
the hard line limit: gate-refusal probing, authenticated-quorum construction,
and receipt rendering all live here unchanged; the entrypoint script imports
them by name and keeps the real provider call (`call_alibaba`) and `main()`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md"


def _new_ledger_shift_event(risk_class, *, evidence_count=1):
    from operations_domain.models import DataState, EvidenceRef, OperationalEvent, Shift
    from workspace_api.infrastructure.repository import InMemoryLedger

    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="Live-evidence shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    event = OperationalEvent(
        shift_id=shift.shift_id,
        event_type="equipment_downtime",
        title="Live-evidence probe",
        risk_class=risk_class,
        state=DataState.PROPOSED,
        evidence=[EvidenceRef(source_type="message", source_id=f"m{i}") for i in range(evidence_count)],
    )
    ledger.add_event(event)
    return ledger, event


def _register_user(ledger, user_id, role, *, is_active=True):
    import workspace_api.domain.models as _domain_models
    ledger.add_user(_domain_models.User(user_id=user_id, username=user_id, password_hash="x", role=role, is_active=is_active))


def _auth_headers(user_id: str, role: str) -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}


def check_approval_gate() -> list[dict]:
    """Exercise approval gate via TestClient and real minted JWTs."""
    from fastapi.testclient import TestClient
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app

    results: list[dict] = []

    def _rec(client, headers, rtype, action, rid):
        return client.post("/approvals", json={"record_type": rtype, "action": action, "record_id": str(rid)}, headers=headers)

    # 1. Fabricated: zero receipts for an R3 record.
    ledger, event = _new_ledger_shift_event("R3")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        results.append({"case": "fabricated_approval_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 2. Wrong role: active real user below required seat.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-op1", "operator")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = _rec(client, _auth_headers("evidence-op1", "operator"), "OperationalEvent", "event.confirm", event.event_id)
        results.append({"case": "wrong_role_rejected", "outcome": "PASS" if res.status_code == 403 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 3. Inactive user.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup2", "shift_supervisor", is_active=False)
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        res = _rec(client, _auth_headers("evidence-sup2", "shift_supervisor"), "OperationalEvent", "event.confirm", event.event_id)
        results.append({"case": "inactive_user_rejected", "outcome": "PASS" if res.status_code == 403 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 4. Self-approval: R2 needs one seat, confirmer fills it alone.
    ledger, event = _new_ledger_shift_event("R2")
    _register_user(ledger, "evidence-sup1", "shift_supervisor")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        headers = _auth_headers("evidence-sup1", "shift_supervisor")
        _rec(client, headers, "OperationalEvent", "event.confirm", event.event_id)
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=headers)
        results.append({"case": "self_approval_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 5. Insufficient quorum: R3 needs two seats, one filled.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup3", "shift_supervisor")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        _rec(client, _auth_headers("evidence-sup3", "shift_supervisor"), "OperationalEvent", "event.confirm", event.event_id)
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        results.append({"case": "insufficient_quorum_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    # 6. Replay: receipts bound to a version that has since advanced.
    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup4", "shift_supervisor")
    _register_user(ledger, "evidence-mgr1", "responsible_manager")
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        _rec(client, _auth_headers("evidence-sup4", "shift_supervisor"), "OperationalEvent", "event.confirm", event.event_id)
        _rec(client, _auth_headers("evidence-mgr1", "responsible_manager"), "OperationalEvent", "event.confirm", event.event_id)
        ledger.events[event.event_id].version += 1
        res = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        results.append({"case": "replay_stale_version_rejected", "outcome": "PASS" if res.status_code == 409 else "FAIL", "detail": f"refused: status {res.status_code}", "calls": 0})
    finally:
        app.dependency_overrides.pop(get_ledger, None)

    return results


def build_and_confirm_valid_quorum() -> tuple[bool, str]:
    """Construct genuine authenticated R3 quorum via minted JWTs & HTTP."""
    from fastapi.testclient import TestClient
    from operations_domain.models import DataState
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app

    ledger, event = _new_ledger_shift_event("R3")
    _register_user(ledger, "evidence-sup5", "shift_supervisor")
    _register_user(ledger, "evidence-mgr2", "responsible_manager")
    _register_user(ledger, "evidence-sup1", "shift_supervisor")

    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        client = TestClient(app)
        r1 = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=_auth_headers("evidence-sup5", "shift_supervisor"))
        if r1.status_code != 201: return False, f"receipt 1 failed: {r1.status_code}"
        r2 = client.post("/approvals", json={"record_type": "OperationalEvent", "action": "event.confirm", "record_id": str(event.event_id)}, headers=_auth_headers("evidence-mgr2", "responsible_manager"))
        if r2.status_code != 201: return False, f"receipt 2 failed: {r2.status_code}"
        cres = client.post(f"/events/{event.event_id}/confirm", json={}, headers=_auth_headers("evidence-sup1", "shift_supervisor"))
        if cres.status_code != 200: return False, f"confirm failed with HTTP {cres.status_code}"
        confirmed = ledger.get_event(event.event_id)
        if confirmed.state != DataState.CONFIRMED: return False, f"confirm state={confirmed.state}"
        return True, "distinct authenticated approvers (evidence-sup5, evidence-mgr2) satisfied the R3 quorum via minted JWTs and HTTP requests"
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def write_receipt(gate_results, quorum_detail, provider_result, model, endpoint, call_count) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# P2-B approver-identity control - live governance evidence receipt",
        "",
        f"Overall outcome: {overall}",
        "",
        "Produced by `scripts/run_approval_governance_evidence.py`",
        "(P2B-APPROVER-IDENTITY-RECONCILIATION, SPEC section 7). Sanitized: contains no API key, no Authorization header, no JWT, no password, no raw secret.",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}",
        f"- Endpoint: {endpoint}",
        "",
        "## 1. Gate-refusal cases (in-process, real code path, 0 provider calls each)",
        "",
        "| Case | Outcome | Detail | Provider calls |",
        "|---|---|---|---|",
    ]
    for r in gate_results:
        lines.append(f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |")
    lines += [
        "",
        "## 2. Authenticated-quorum construction (real code path)",
        "",
        f"- {quorum_detail}",
        "",
        "## 3. Real provider call",
        "",
        "Reached only because the quorum above genuinely satisfied the R3 requirement.",
        "",
        f"- Outcome: **{provider_result['outcome']}**",
        f"- Reached the provider (got any HTTP response): **{provider_result.get('reached_server', False)}**",
        f"- HTTP status: {provider_result.get('http_status')}",
        f"- Started at: {provider_result.get('started_at')}",
    ]
    if "response_excerpt" in provider_result:
        lines.append(f"- Response excerpt: `{provider_result['response_excerpt']}`")
    if "error" in provider_result:
        lines.append(f"- Error: `{provider_result['error']}`")
    lines += [
        "",
        "## 4. Provider-call count (self-asserted)",
        "",
        f"- Total provider calls made by this run: **{call_count}**",
        "- Expected: 0 for every gate-refusal case above, exactly 1 after the valid quorum.",
        "",
        "## Claim boundary",
        "",
        "This receipt evidences that the `approval` control - authenticated,",
        "server-derived, scope-bound receipts evaluated by a deterministic,",
        "order-invariant quorum matcher - correctly refuses fabricated, wrong-role,",
        "inactive-user, self-approval, insufficient-quorum, and replayed approvals",
        "before any provider call, and correctly admits a genuine, distinct-approver",
        "quorum through the real application code path. It does NOT evidence that any",
        "production endpoint calls a provider in production (none do). It does not",
        "evidence PostgreSQL production verification (remains NOT LIVE VERIFIED).",
        "",
    ]
    RECEIPT_PATH.write_text("\n".join(lines), encoding="utf-8")
