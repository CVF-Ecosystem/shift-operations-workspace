#!/usr/bin/env python3
"""Live governance evidence for the P2-C C3d supervisor closeout vertical
(P2C-MUTATION-FULL-UI-C3D, SPEC R10): in-process refusal probes over the real
FastAPI/JWT route chain (observed zero provider calls each), then a genuine
staffing-assigned supervisor closeout - event confirm, approval receipt,
incident acknowledge, handover review/acknowledge, report approve, shift
close/freeze - followed by exactly one real provider call. Provider HTTP/
sanitization/receipt rendering AND the shared real-route-call helpers live in
`_p2c_c3d_live_evidence_support.py`; this module is orchestration+CLI only."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-do-not-use-in-production")

REPO_ROOT = Path(__file__).resolve().parents[1]
for _rel in (
    "apps/workspace-api/src", "packages/cvf-runtime/src", "packages/operations-ledger/src",
    "packages/operations-domain/src", "packages/ai-providers/alibaba",
):
    sys.path.insert(0, str(REPO_ROOT / _rel))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _p2c_c3d_live_evidence_support import (  # noqa: E402
    ProviderCallCounter, ack_handover, ack_incident, approve_report, assign_user,
    auth_headers, call_provider, close_shift, confirm_event, create_approval,
    create_event, create_handover, freeze_shift, generate_report,
    new_ledger_and_shift, new_ledger_and_shift_unassigned_supervisor, new_shift,
    render_receipt, report_incident, review_handover, safe_endpoint_description,
    seed_active_assignment, submit_review, with_ledger,
)

KEY_ENV_NAMES = ("ALIBABA_API_KEY", "DASHSCOPE_API_KEY")
BASE_URL_ENV_NAMES = ("ALIBABA_BASE_URL", "DASHSCOPE_BASE_URL")
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
PROMPT = "Reply with exactly this token and nothing else: CVF_C3D_EVIDENCE_OK"
EXPECTED_TOKEN = "CVF_C3D_EVIDENCE_OK"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P2C_C3D_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md"


def check_c3d_refusal_matrix(counter: ProviderCallCounter) -> list[dict]:
    """SPEC R10 refusal matrix: each records the OBSERVED provider-call delta
    on the shared counter - none of these code paths can reach
    call_provider, and this proves it empirically."""
    results: list[dict] = []
    op = auth_headers("c3d-ev-op", "operator")
    sup1 = auth_headers("c3d-ev-sup1", "shift_supervisor")

    def _case(name, ledger, run, expected_statuses=(403,)):
        before = counter.count
        res = with_ledger(ledger, run)
        outcome = "PASS" if res.status_code in expected_statuses else "FAIL"
        results.append({"case": name, "outcome": outcome, "detail": f"refused: status {res.status_code}", "calls": counter.count - before})

    ledger, shift = new_ledger_and_shift("wrong-role")
    def _wrong_role(client):
        inc_res = report_incident(client, shift.shift_id, op)
        return ack_incident(client, inc_res.json()["incident_id"], op, expected_version=inc_res.json()["version"])
    _case("wrong_role_operator_cannot_acknowledge_incident", ledger, _wrong_role, (403,))

    ledger, shift = new_ledger_and_shift("unassigned-staffing")
    _case("unassigned_operator_cannot_use_staffing", ledger, lambda c: c.get("/staffing/shifts", headers=op), (403,))

    ledger, shift = new_ledger_and_shift("stale-confirm")
    def _stale_confirm(client):
        ev_res = create_event(client, shift.shift_id, op)
        return confirm_event(client, ev_res.json()["event_id"], sup1, expected_version=999)
    _case("stale_version_event_confirm_rejected", ledger, _stale_confirm, (409,))

    ledger, shift = new_ledger_and_shift("missing-approval")
    def _missing_approval(client):
        # R2 needs evidence (satisfied) AND an event.confirm quorum receipt
        # (absent) to reach CONFIRMED - confirm itself is refused.
        ev_res = client.post("/events", json={
            "shift_id": str(shift.shift_id), "event_type": "shift_update", "title": "needs approval",
            "risk_class": "R2", "evidence": [{"source_type": "message", "source_id": "m-1"}]
        }, headers=op)
        event_id = ev_res.json()["event_id"]
        return confirm_event(client, event_id, sup1, expected_version=ev_res.json()["version"])
    _case("missing_approval_confirm_rejected", ledger, _missing_approval, (409,))

    ledger, shift = new_ledger_and_shift("wrong-destination")
    def _wrong_destination(client):
        dest = new_shift("dest-refusal")
        ledger.create_shift(dest)
        ho_res = create_handover(client, shift.shift_id, dest.shift_id, op)
        handover_id = ho_res.json()["handover_id"]
        review_handover(client, handover_id, sup1, expected_version=ho_res.json()["version"])
        # sup1 has no assignment on the destination shift: enumeration-safe
        # 404 (AssignmentScope.require_shift), not a role-based 403.
        return ack_handover(client, handover_id, sup1, expected_version=ho_res.json()["version"] + 1)
    _case("wrong_destination_assignment_acknowledge_rejected", ledger, _wrong_destination, (404,))

    ledger, shift = new_ledger_and_shift("not-closed-freeze")
    _case("non_closed_shift_freeze_rejected", ledger, lambda c: freeze_shift(c, shift.shift_id, sup1), (409,))

    ledger, shift = new_ledger_and_shift("retired-override")
    def _retired_override(client):
        close_res = close_shift(client, shift.shift_id, sup1)
        return freeze_shift(client, shift.shift_id, sup1, override=True, expected_version=close_res.json()["version"])
    _case("retired_override_field_refused", ledger, _retired_override, (422,))

    return results


def build_genuine_supervisor_closeout() -> tuple[bool, str]:
    """Construct a genuine staffing-assigned supervisor closeout via minted
    JWTs and real HTTP requests: assign, confirm an event, create an
    approval receipt, acknowledge an incident, review/acknowledge a
    handover, approve a report, then close/freeze the shift - verifying
    durable stored state plus actor-bound audits before returning."""
    ledger, shift = new_ledger_and_shift_unassigned_supervisor("genuine")
    op = auth_headers("c3d-ev-op", "operator")
    sup1 = auth_headers("c3d-ev-sup1", "shift_supervisor")

    def _run(client):
        assign_res = assign_user(client, shift.shift_id, "c3d-ev-sup1", sup1)
        if assign_res.status_code not in (200, 201):
            return False, f"self-assign failed: {assign_res.status_code}"

        # R2: only risk class with a real approval-quorum seat (R0/R1 have none).
        ev_res = client.post("/events", json={
            "shift_id": str(shift.shift_id), "event_type": "shift_update", "title": "genuine closeout event",
            "risk_class": "R2", "evidence": [{"source_type": "message", "source_id": "m-genuine"}]
        }, headers=op)
        if ev_res.status_code != 200:
            return False, f"event create failed: {ev_res.status_code}"
        event_id = ev_res.json()["event_id"]

        # F15/SPEC R3.4: a quorum is never satisfied by the confirmer alone -
        # the receipt approver must be a distinct shift_supervisor from sup1,
        # who then performs the confirm itself.
        seed_active_assignment(ledger, shift.shift_id, "c3d-ev-approver-confirm", "shift_supervisor")
        approver_confirm = auth_headers("c3d-ev-approver-confirm", "shift_supervisor")
        approval_res = create_approval(client, approver_confirm, "OperationalEvent", "event.confirm", event_id)
        if approval_res.status_code not in (200, 201):
            return False, f"approval receipt failed: {approval_res.status_code}"

        confirm_res = confirm_event(client, event_id, sup1, expected_version=ev_res.json()["version"])
        if confirm_res.status_code != 200 or confirm_res.json()["state"] != "CONFIRMED":
            return False, f"confirm failed: {confirm_res.status_code}"

        inc_res = report_incident(client, shift.shift_id, op)
        if inc_res.status_code != 200:
            return False, f"incident report failed: {inc_res.status_code}"
        incident_id = inc_res.json()["incident_id"]
        ack_res = ack_incident(client, incident_id, sup1, expected_version=inc_res.json()["version"])
        if ack_res.status_code != 200 or ack_res.json()["status"] != "ACKNOWLEDGED":
            return False, f"incident acknowledge failed: {ack_res.status_code}"

        dest = new_shift("genuine-dest")
        ledger.create_shift(dest)
        seed_active_assignment(ledger, dest.shift_id, "c3d-ev-sup2", "shift_supervisor")
        sup2 = auth_headers("c3d-ev-sup2", "shift_supervisor")
        assign_user(client, dest.shift_id, "c3d-ev-sup2", sup2)
        ho_res = create_handover(client, shift.shift_id, dest.shift_id, op)
        if ho_res.status_code != 200:
            return False, f"handover create failed: {ho_res.status_code}"
        handover_id = ho_res.json()["handover_id"]
        review_res = review_handover(client, handover_id, sup1, expected_version=ho_res.json()["version"])
        if review_res.status_code != 200:
            return False, f"handover review failed: {review_res.status_code}"
        ack_ho_res = ack_handover(client, handover_id, sup2, expected_version=review_res.json()["version"])
        if ack_ho_res.status_code != 200 or not ack_ho_res.json()["acknowledged"]:
            return False, f"handover acknowledge failed: {ack_ho_res.status_code}"

        close_res = close_shift(client, shift.shift_id, sup1)
        if close_res.status_code != 200:
            return False, f"close failed: {close_res.status_code}"

        gen_res = generate_report(client, shift.shift_id, sup1)
        if gen_res.status_code != 201:
            return False, f"report generate failed: {gen_res.status_code}"
        report_id = gen_res.json()["report_id"]
        report_version = gen_res.json()["version"]
        review_rep_res = submit_review(client, report_id, sup1, expected_version=report_version)
        if review_rep_res.status_code != 200:
            return False, f"report submit-review failed: {review_rep_res.status_code}"

        seed_active_assignment(ledger, shift.shift_id, "c3d-ev-approver", "shift_supervisor")
        approver = auth_headers("c3d-ev-approver", "shift_supervisor")
        rep_approval_res = create_approval(client, approver, "Report", "report.approve", report_id)
        if rep_approval_res.status_code not in (200, 201):
            return False, f"report approval receipt failed: {rep_approval_res.status_code}"

        approve_res = approve_report(client, report_id, sup1, expected_version=report_version)
        if approve_res.status_code != 200 or approve_res.json()["status"] != "APPROVED":
            return False, f"report approve failed: {approve_res.status_code}"

        freeze_res = freeze_shift(client, shift.shift_id, sup1, expected_version=close_res.json()["version"])
        if freeze_res.status_code != 200 or freeze_res.json()["status"] != "FROZEN":
            return False, f"freeze failed: {freeze_res.status_code}"

        stored_shift = ledger.get_shift(shift.shift_id)
        if str(stored_shift.status) != "FROZEN":
            return False, "stored shift status is not FROZEN after freeze"

        actions = {a.action for a in ledger._audit.all()}
        required_actions = {
            "shift.assignment.manage", "event.confirm", "incident.acknowledge",
            "shift.close", "shift.freeze",
        }
        missing = required_actions - actions
        if missing:
            return False, f"missing actor-bound audit actions: {sorted(missing)}"

        return True, (
            "genuine staffing-assigned closeout: c3d-ev-sup1 self-assigned, "
            "confirmed an event with a durable approval receipt, acknowledged "
            "an incident, reviewed and (via c3d-ev-sup2) acknowledged a "
            "cross-shift handover, approved a distinct-receipt END_SHIFT "
            "report, then closed and froze the shift - verified via a fresh "
            "stored-shift read (status FROZEN) and every required "
            "actor-bound audit action present"
        )

    return with_ledger(ledger, _run)


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
    parser = argparse.ArgumentParser(description="P2-C C3d supervisor closeout live governance evidence")
    parser.add_argument("--dry-run", action="store_true", help="run without calling provider")
    args = parser.parse_args()

    counter = ProviderCallCounter()

    print("== C3d supervisor closeout refusal matrix ==")
    gate_results = check_c3d_refusal_matrix(counter)
    for r in gate_results:
        print(f"  {r['case']}: {r['outcome']} - {r['detail']}")
    if any(r["outcome"] != "PASS" for r in gate_results) or any(r["calls"] != 0 for r in gate_results):
        print("C3D REFUSAL MATRIX FAILED", file=sys.stderr)
        return 1

    print("== constructing a genuine staffing-assigned supervisor closeout ==")
    ok, detail = build_genuine_supervisor_closeout()
    print(f"  {detail}")
    if not ok:
        print("GENUINE C3D CLOSEOUT CONSTRUCTION FAILED", file=sys.stderr)
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
    except Exception:
        print("READY_FOR_LIVE_EVIDENCE: model selection failed", file=sys.stderr)
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
        RECEIPT_PATH, gate_results=gate_results, closeout_detail=detail,
        provider_result=provider_result, model=model, safe_endpoint=safe_endpoint,
        call_count=counter.count,
    )

    if counter.count != 1 or provider_result["outcome"] != "PASS":
        return 1
    print("LIVE EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
