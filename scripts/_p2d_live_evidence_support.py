"""Sanitized provider and real-route support for P2-D live evidence."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

try:  # package import under pytest
    from scripts._p2c_c3d_live_evidence_support import (
        ProviderCallCounter, call_provider, safe_endpoint_description,
    )
except ModuleNotFoundError:  # direct CLI execution adds scripts/ to sys.path
    from _p2c_c3d_live_evidence_support import (  # type: ignore[no-redef]
        ProviderCallCounter, call_provider, safe_endpoint_description,
    )


def auth_headers(user_id: str, role: str = "operator") -> dict[str, str]:
    from cvf_runtime.identity import Principal
    from workspace_api.auth.tokens import create_access_token
    return {"Authorization": f"Bearer {create_access_token(Principal(user_id=user_id, role=role))}"}


def scenario():
    import workspace_api.domain.models as models
    from operations_domain.models import Shift
    from workspace_api.infrastructure.repository import InMemoryLedger
    ledger = InMemoryLedger()
    now = datetime.now(timezone.utc)
    shift = Shift(name="p2d evidence shift", starts_at=now, ends_at=now + timedelta(hours=8))
    ledger.create_shift(shift)
    for user_id in ("p2d-op", "p2d-unassigned"):
        ledger.add_user(models.User(user_id=user_id, username=user_id, password_hash="x", role="operator"))
    ledger.add_assignment(models.ShiftAssignment(shift_id=shift.shift_id, user_id="p2d-op", assigned_by="p2d-op"))
    return ledger, shift


def with_ledger(ledger, callback):
    from fastapi.testclient import TestClient
    from workspace_api.dependencies import get_ledger
    from workspace_api.main import app
    app.dependency_overrides[get_ledger] = lambda: ledger
    try:
        return callback(TestClient(app))
    finally:
        app.dependency_overrides.pop(get_ledger, None)


def create_task(client, shift_id, headers):
    return client.post("/tasks", json={
        "shift_id": str(shift_id), "title": "p2d replay task", "risk_class": "R1"
    }, headers=headers)


def transition_task(client, task_id, headers=None, expected_version=1):
    return client.post(f"/tasks/{task_id}/transition", json={
        "target_status": "IN_PROGRESS", "expected_version": expected_version
    }, headers=headers or {})


def render_receipt(path: Path, gates: list[dict], detail: str, provider: dict,
                   model: str, endpoint: str, calls: int) -> None:
    lines = [
        "# P2-D offline/realtime - live governance evidence receipt", "",
        f"Overall outcome: {provider.get('outcome')}", "",
        "Sanitized receipt: no key, bearer/JWT, raw provider body, URL userinfo/query/fragment or raw exception.", "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Provider: Alibaba DashScope (OpenAI-compatible endpoint)",
        f"- Model: {model}", f"- Endpoint (host only): {endpoint}", "",
        "## Refusal and ambiguity gates", "",
        "| Case | Outcome | Detail | Provider calls |", "|---|---|---|---|",
    ]
    lines.extend(f"| {g['case']} | {g['outcome']} | {g['detail']} | {g['calls']} |" for g in gates)
    lines += [
        "", "## Durable admitted transition", "", f"- {detail}", "",
        "## Real provider call", "", f"- Outcome: **{provider.get('outcome')}**",
        f"- Reached provider: **{provider.get('reached_server', False)}**",
        f"- HTTP status: {provider.get('http_status')}",
        f"- Expected token matched: **{provider.get('expected_token_match', False)}**",
        f"- Total calls: **{calls}** (zero before admission; exactly one after)", "",
        "## Claim boundary", "",
        "This proves one assigned CAS task transition and actor-bound audit remain governed before one real provider call. Browser evidence separately proves bounded offline staging/polling. It does not prove exactly-once, push, full offline, production readiness, full-shift exit or Phase 2 completion.", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
