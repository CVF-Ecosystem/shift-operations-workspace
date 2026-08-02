"""Support module for run_p2c_c3d_live_governance_evidence.py.

P2C-MUTATION-FULL-UI-C3D (SPEC R10): owns provider HTTP, sanitization, safe
endpoint description, provider-call accounting, receipt rendering, AND (to
keep the orchestrator under the 300-line executable limit) the shared
real-HTTP-route-call helpers used by both the refusal matrix and the genuine
closeout builder. Nothing here ever returns, prints, or writes the exact
configured provider key, a bearer/JWT value, or a URL's userinfo/query/
fragment - every provider-derived string is sanitized before it leaves
:func:`call_provider`.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

_BEARER_RE = re.compile(r"Bearer\s+\S+", re.IGNORECASE)
_JWT_RE = re.compile(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")


class ProviderCallCounter:
    """A fresh instance per runner invocation - never a module global, so
    accounting cannot leak or persist across calls/tests."""

    def __init__(self) -> None:
        self.count = 0

    def record(self) -> None:
        self.count += 1


def seed_active_assignment(ledger, shift_id, user_id, role="operator"):
    import workspace_api.domain.models as _dm
    if ledger.get_user_by_id(user_id) is None:
        ledger.add_user(_dm.User(user_id=user_id, username=user_id, password_hash="x", role=role))
    if ledger.get_active_assignment(shift_id, user_id) is None:
        ledger.add_assignment(_dm.ShiftAssignment(shift_id=shift_id, user_id=user_id, assigned_by=user_id))


def new_shift(prefix: str):
    from operations_domain.models import Shift
    now = datetime.now(timezone.utc)
    return Shift(name=f"{prefix} shift", starts_at=now, ends_at=now + timedelta(hours=8))


def new_ledger_and_shift(prefix: str):
    from workspace_api.infrastructure.repository import InMemoryLedger
    ledger = InMemoryLedger()
    shift = new_shift(prefix)
    ledger.create_shift(shift)
    seed_active_assignment(ledger, shift.shift_id, "c3d-ev-op", "operator")
    seed_active_assignment(ledger, shift.shift_id, "c3d-ev-sup1", "shift_supervisor")
    return ledger, shift


def new_ledger_and_shift_unassigned_supervisor(prefix: str):
    """Like new_ledger_and_shift, but c3d-ev-sup1 is a persisted active user
    with NO assignment yet, so the genuine-closeout builder can prove a real
    POST /shifts/{id}/assignments call (not a pre-seeded fixture) produces
    the shift.assignment.manage audit action."""
    from workspace_api.infrastructure.repository import InMemoryLedger
    import workspace_api.domain.models as _dm
    ledger = InMemoryLedger()
    shift = new_shift(prefix)
    ledger.create_shift(shift)
    seed_active_assignment(ledger, shift.shift_id, "c3d-ev-op", "operator")
    if ledger.get_user_by_id("c3d-ev-sup1") is None:
        ledger.add_user(_dm.User(user_id="c3d-ev-sup1", username="c3d-ev-sup1", password_hash="x", role="shift_supervisor"))
    return ledger, shift


def auth_headers(user_id: str, role: str) -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}


def with_ledger(ledger, fn):
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        from fastapi.testclient import TestClient
        return fn(TestClient(app))
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def create_event(client, shift_id, headers, event_type="shift_update", title="closeout event", risk_class="R0"):
    return client.post("/events", json={
        "shift_id": str(shift_id), "event_type": event_type, "title": title, "risk_class": risk_class
    }, headers=headers)


def confirm_event(client, event_id, headers, expected_version=1):
    return client.post(f"/events/{event_id}/confirm", json={"expected_version": expected_version}, headers=headers)


def create_approval(client, headers, record_type, action, record_id):
    return client.post("/approvals", json={"record_type": record_type, "action": action, "record_id": str(record_id)}, headers=headers)


def assign_user(client, shift_id, user_id, headers):
    return client.post(f"/shifts/{shift_id}/assignments", json={"user_id": user_id}, headers=headers)


def report_incident(client, shift_id, headers, summary="closeout incident", risk_class="R1"):
    return client.post("/incidents", json={"shift_id": str(shift_id), "summary": summary, "risk_class": risk_class}, headers=headers)


def ack_incident(client, incident_id, headers, expected_version=1):
    return client.post(f"/incidents/{incident_id}/acknowledge", json={"expected_version": expected_version}, headers=headers)


def create_handover(client, from_id, to_id, headers):
    return client.post("/handovers", json={"from_shift_id": str(from_id), "to_shift_id": str(to_id)}, headers=headers)


def review_handover(client, handover_id, headers, expected_version=1):
    return client.post(f"/handovers/{handover_id}/review", json={"expected_version": expected_version}, headers=headers)


def ack_handover(client, handover_id, headers, expected_version=1):
    return client.post(f"/handovers/{handover_id}/acknowledge", json={"expected_version": expected_version}, headers=headers)


def generate_report(client, shift_id, headers):
    return client.post("/reports", json={"shift_id": str(shift_id)}, headers=headers)


def submit_review(client, report_id, headers, expected_version=1, expected_status="DRAFT"):
    return client.post(f"/reports/{report_id}/submit-review", json={"expected_version": expected_version, "expected_status": expected_status}, headers=headers)


def approve_report(client, report_id, headers, expected_version=1, expected_status="IN_REVIEW"):
    return client.post(f"/reports/{report_id}/approve", json={"expected_version": expected_version, "expected_status": expected_status}, headers=headers)


def close_shift(client, shift_id, headers, expected_version=1):
    return client.post(f"/shifts/{shift_id}/close", json={"expected_version": expected_version}, headers=headers)


def freeze_shift(client, shift_id, headers, *, override=False, expected_version=1):
    body = {"expected_version": expected_version}
    if override:
        body.update({"override_unimplemented_prerequisites": True, "override_reason": "x"})
    return client.post(f"/shifts/{shift_id}/freeze", json=body, headers=headers)


def sanitize_secret_text(text: str | None, *, api_key: str | None = None) -> str:
    if not text:
        return text or ""
    if api_key:
        text = text.replace(api_key, "<redacted-key>")
    text = _BEARER_RE.sub("Bearer <redacted>", text)
    text = _JWT_RE.sub("<redacted-jwt>", text)
    return text


def safe_endpoint_description(endpoint: str) -> str:
    """Scheme + hostname only - no userinfo, port, path, query or fragment."""
    try:
        parts = urlsplit(endpoint)
    except ValueError:
        return "<invalid-endpoint>"
    hostname = parts.hostname or "<unknown-host>"
    return f"{parts.scheme}://{hostname}"


def _clean_endpoint(endpoint: str) -> tuple[str, list[str]]:
    """Split ``endpoint`` into (url-safe-for-request, [secret fragments]) -
    the ONLY form ever handed to Request/urlopen, so a later construction or
    transport exception can never embed credential material smuggled into
    the endpoint's userinfo/query/fragment (mirrors INC-REV-F6)."""
    parts = urlsplit(endpoint)
    secrets = [v for v in (parts.username, parts.password, parts.query, parts.fragment) if v]
    netloc = parts.hostname or ""
    if parts.port:
        netloc = f"{netloc}:{parts.port}"
    clean = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    return clean, secrets


def call_provider(
    *, model: str, api_key: str, endpoint: str, prompt: str, expected_token: str,
    counter: ProviderCallCounter,
) -> dict:
    """One real, non-mocked provider call. Every field of the returned dict
    is already sanitized - callers never need to scrub it again."""
    counter.record()
    started = datetime.now(timezone.utc)
    try:
        clean_endpoint, _endpoint_secrets = _clean_endpoint(endpoint)
        body = json.dumps(
            {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 32}
        ).encode("utf-8")
        req = urllib.request.Request(
            clean_endpoint, data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        return {
            "outcome": "FAIL", "reached_server": True, "http_status": exc.code,
            "expected_token_match": False, "failure_kind": "http_error",
            "started_at": started.isoformat(),
        }
    except Exception:  # noqa: BLE001 - retain only the bounded failure category
        return {
            "outcome": "FAIL", "reached_server": False, "http_status": None,
            "expected_token_match": False, "failure_kind": "transport_error",
            "started_at": started.isoformat(),
        }

    content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
    matched = expected_token in content
    return {
        "outcome": "PASS" if matched else "FAIL",
        "reached_server": True, "http_status": status,
        "expected_token_match": matched,
        "started_at": started.isoformat(),
    }


def render_receipt(
    path: Path, *, gate_results: list[dict], closeout_detail: str, provider_result: dict,
    model: str, safe_endpoint: str, call_count: int,
) -> None:
    overall = "PASS" if provider_result.get("outcome") == "PASS" else "FAIL"
    lines = [
        "# P2-C C3d supervisor closeout - live governance evidence receipt", "",
        f"Overall outcome: {overall}", "",
        "Produced by `scripts/run_p2c_c3d_live_governance_evidence.py` via "
        "`scripts/_p2c_c3d_live_evidence_support.py` "
        "(P2C-MUTATION-FULL-UI-C3D, SPEC R10). Sanitized: contains no API "
        "key, no Authorization header, no JWT, no raw secret, no URL "
        "userinfo/query/fragment.", "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}", f"- Endpoint (host only): {safe_endpoint}", "",
        "## 1. Supervisor closeout refusal matrix (real HTTP route chain, observed provider-call delta)", "",
        "| Case | Outcome | Detail | Provider calls |", "|---|---|---|---|",
    ]
    for r in gate_results:
        lines.append(f"| {r['case']} | {r['outcome']} | {r['detail']} | {r['calls']} |")
    lines += [
        "", "## 2. Durable assigned closeout state and actor-bound audits (real HTTP route chain)", "",
        f"- {closeout_detail}", "", "## 3. Real provider call", "",
        "Reached only because the closeout above genuinely produced a "
        "durable assigned Shift freeze plus every required actor-bound "
        "audit record.", "",
        f"- Outcome: **{provider_result['outcome']}**",
        f"- Reached the provider (got any HTTP response): **{provider_result.get('reached_server', False)}**",
        f"- HTTP status: {provider_result.get('http_status')}",
        f"- Expected token matched: **{provider_result.get('expected_token_match', False)}**",
        f"- Started at: {provider_result.get('started_at')}",
    ]
    if "failure_kind" in provider_result:
        lines.append(f"- Failure category: `{provider_result['failure_kind']}`")
    lines += [
        "", "## 4. Provider-call count (observed, reset per invocation)", "",
        f"- Total provider calls made by this run: **{call_count}**",
        "- Expected: 0 for every refusal case above, exactly 1 after the genuine closeout.",
        "", "## Claim boundary", "",
        "This receipt evidences only that, within the single workspace, an "
        "authenticated actively assigned shift_supervisor uses the C3d "
        "staffing/event/approval/incident/handover/report/freeze controls "
        "while the backend re-authorizes and audits every action on the "
        "proven backends. It does NOT evidence multi-tenant/provider "
        "data_scope, destination-only handover discovery, offline/realtime, "
        "production PostgreSQL, P2-D, full-shift-exit, or Phase-2 completion.", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
