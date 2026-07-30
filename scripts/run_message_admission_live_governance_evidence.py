#!/usr/bin/env python3
"""Live governance evidence for internal message admission
(MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC section 6/R16-R18). Mirrors
run_shift_create_live_governance_evidence.py's shape: in-process refusal
probes over the real FastAPI/JWT route chain (observed zero provider calls
each), then a genuine operator-JWT create through MessageService.create,
followed by exactly one real, non-mocked provider call.

Provider HTTP, sanitization, safe endpoint description, provider-call
accounting and receipt rendering live in
`_message_admission_live_evidence_support.py`; this module is the
orchestration facade and CLI entrypoint only. Production POST /messages
never imports or invokes anything from either of these two files.
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

from _message_admission_live_evidence_support import (  # noqa: E402
    ProviderCallCounter,
    call_provider,
    render_receipt,
    safe_endpoint_description,
)

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_MESSAGE_ADMISSION_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_MESSAGE_ADMISSION_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "MESSAGE_ADMISSION_TRUST_REPAIR_LIVE_EVIDENCE_RECEIPT.md"


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


def _new_shift(ledger):
    from cvf_runtime.identity import Principal
    from workspace_api.application.shift_service import ShiftService

    now = datetime.now(timezone.utc)
    return ShiftService(ledger).create(
        "Live evidence shift", now, now + timedelta(hours=8), Principal(user_id="msg-ev-setup", role="operator")
    )


def _create(client, shift_id, headers, **body_overrides):
    body = {"shift_id": str(shift_id), "text": "live evidence message"}
    body.update(body_overrides)
    return client.post("/messages", json=body, headers=headers)


def _zero_writes(ledger, *, messages_before: int, audits_before: int) -> bool:
    """MAR-BUILD-REV-F3 repair (SPEC R23): a refusal must leave zero NEW
    message-write AND zero NEW audit-write state relative to the ledger's
    state right after test setup (setup's own shift.create audit is
    legitimate and must not be misread as a refusal leak). The previous gate
    never inspected the audit log at all, so seven injected refusal audits
    still reported seven PASS outcomes (adversarial finding)."""
    return len(ledger.messages) == messages_before and len(ledger._audit.all()) == audits_before


def check_message_admission_refusal_gate(counter: ProviderCallCounter) -> list[dict]:
    """Refusal cases: each records the OBSERVED provider-call delta on the
    shared counter (SPEC R16), never a hard-coded literal - none of these
    code paths can reach call_provider, and this proves it empirically. Each
    also observes zero message-write AND zero audit-write deltas (SPEC R23),
    measured against the ledger's state right after setup."""
    from workspace_api.infrastructure.repository import InMemoryLedger

    results: list[dict] = []

    def _case(name, headers, expected_status, **body_overrides):
        ledger = InMemoryLedger()
        shift = _new_shift(ledger)
        messages_before, audits_before = len(ledger.messages), len(ledger._audit.all())
        before = counter.count
        res = _with_ledger(ledger, lambda c: _create(c, shift.shift_id, headers, **body_overrides))
        outcome = "PASS" if res.status_code == expected_status and _zero_writes(
            ledger, messages_before=messages_before, audits_before=audits_before,
        ) else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    _case("anonymous_create_rejected", {}, 401)
    _case("malformed_token_create_rejected", {"Authorization": "Bearer not-a-jwt"}, 401)
    _case("viewer_role_create_rejected", _auth_headers("msg-ev-viewer", "viewer"), 403)
    _case("sender_mismatch_create_rejected", _auth_headers("msg-ev-op", "operator"), 403, sender_id="forged-executive")
    _case("non_internal_source_create_rejected", _auth_headers("msg-ev-op", "operator"), 422, source="EXTERNAL")

    # unknown/frozen-shift cases need their own ledger/shift handling.
    def _unknown_shift(counter_before):
        import uuid

        ledger = InMemoryLedger()
        messages_before, audits_before = len(ledger.messages), len(ledger._audit.all())
        res = _with_ledger(ledger, lambda c: _create(c, uuid.uuid4(), _auth_headers("msg-ev-op", "operator")))
        outcome = "PASS" if res.status_code == 404 and _zero_writes(
            ledger, messages_before=messages_before, audits_before=audits_before,
        ) else "FAIL"
        results.append({"case": "unknown_shift_create_rejected", "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - counter_before})

    _unknown_shift(counter.count)

    def _frozen_shift(counter_before):
        ledger = InMemoryLedger()
        shift = _new_shift(ledger)
        ledger.close_shift(shift.shift_id)
        ledger.freeze_shift(shift.shift_id)
        messages_before, audits_before = len(ledger.messages), len(ledger._audit.all())
        res = _with_ledger(ledger, lambda c: _create(c, shift.shift_id, _auth_headers("msg-ev-op", "operator")))
        outcome = "PASS" if res.status_code == 409 and _zero_writes(
            ledger, messages_before=messages_before, audits_before=audits_before,
        ) else "FAIL"
        results.append({"case": "frozen_shift_create_rejected", "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - counter_before})

    _frozen_shift(counter.count)
    return results


def build_admitted_create_genuine() -> tuple[bool, str]:
    """Construct a genuine operator-JWT create via a minted token and a real
    HTTP request (SPEC R17). Asserts exactly one persisted message and every
    audit field matches exactly (mirrors SCR-BUILD-REV-F2's shift-create
    repair - a tampered actor or unexpected second message must fail)."""
    from workspace_api.infrastructure.repository import InMemoryLedger

    ledger = InMemoryLedger()
    shift = _new_shift(ledger)
    headers = _auth_headers("msg-ev-op", "operator")

    def _run(client):
        return _create(client, shift.shift_id, headers)

    res = _with_ledger(ledger, _run)
    if res.status_code != 200:
        return False, f"create failed: {res.status_code}"
    body = res.json()

    if len(ledger.messages) != 1:
        return False, f"expected exactly one persisted message, found {len(ledger.messages)}"
    if body["message_id"] not in {str(m) for m in ledger.messages}:
        return False, "the one persisted message does not match the created id"

    audits = ledger.audit_entries_for(body["message_id"])
    if len(audits) != 1:
        return False, f"expected exactly one audit for the created message, found {len(audits)}"
    a = audits[0]
    expected = {
        "actor_id": "msg-ev-op", "actor_role": "operator", "action": "message.create",
        "record_type": "Message", "record_id": body["message_id"],
        "control_chain": ["identity", "permission", "create", "audit"],
        "before_state": None, "after_state": "RAW",
    }
    actual = {
        "actor_id": a.actor_id, "actor_role": a.actor_role, "action": a.action,
        "record_type": a.record_type, "record_id": a.record_id,
        "control_chain": list(a.control_chain), "before_state": a.before_state,
        "after_state": a.after_state,
    }
    if actual != expected:
        return False, f"audit fields did not match exactly: expected {expected}, got {actual}"

    return True, (
        "valid operator JWT (msg-ev-op) admitted POST /messages via a minted "
        "token and a real HTTP request, persisting exactly one message and "
        "one exactly-field-matched actor-bound message.create audit"
    )


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
    parser = argparse.ArgumentParser(description="Message admission live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    counter = ProviderCallCounter()  # fresh per invocation (SPEC R16 parity)

    print("== message admission refusal gate: refusal cases ==")
    gate_results = check_message_admission_refusal_gate(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("MESSAGE ADMISSION REFUSAL GATE CASES FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine admitted create ==")
    ok, detail = build_admitted_create_genuine()
    print(f"  {detail}")
    if not ok:
        print("GENUINE MESSAGE CREATE CONSTRUCTION FAILED", file=sys.stderr)
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
        RECEIPT_PATH, gate_results=gate_results, admitted_detail=detail,
        provider_result=provider_result, model=model, safe_endpoint=safe_endpoint,
        call_count=counter.count,
    )

    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
