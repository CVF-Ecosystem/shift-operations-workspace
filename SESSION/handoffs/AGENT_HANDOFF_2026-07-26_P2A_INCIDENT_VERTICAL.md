# Agent Handoff — P2-A Incident Vertical

## Disposition

- Tranche: `P2A-INCIDENT-VERTICAL-2026-07-26`
- Control-chain phase: `REVIEW_CHANGES_REQUIRED`, repair authorized
- Roadmap target: P2-A incidents only
- Risk: R2
- Implementation worker: Claude
- Independent reviewer / commit steward / closer: Codex
- Status: `AUTHORIZED_PENDING_REPAIR_G6`

## Split boundary

This tranche implements incidents only. Handovers remain a separate successor
because they also change the `open_handover_items_linked` freeze prerequisite.
No handover/report/freeze implementation is authorized here.

## Authorization

- C1: `893b5c3bc4d031f5618cef3be3a35ad919e7ae1a`
- ADR:
  `docs/decisions/ADR_2026-07-26_P2A_INCIDENT_VERTICAL.md`
- SPEC: `docs/specs/P2A_INCIDENT_VERTICAL_SPEC.md`
- Work Order:
  `docs/work_orders/P2A_INCIDENT_VERTICAL_WORK_ORDER.md`
- Independent disposition: `REVIEW_PASS`
- Findings closed without waiver:
  - `INC-AUTH-F1 OVERBROAD_GUARD_TEST_PATHS`
  - `INC-AUTH-F2 LIVE_TEST_SPLIT_CONFLICT`

## BUILD contract

The C3 ceiling is exactly 37 paths in Work Order section 3. No 38th path is
conditional. Near-limit host files receive wiring only:

- `_incident_tables.py` owns Table construction;
- `_incident_store.py` owns SqlLedger incident methods;
- `_incident_repository.py` owns InMemoryLedger incident methods;
- all Python files remain <= 300 lines;
- debt baseline and exception registry are read-only.

Incident reporting is immediate and audited. Risk/evidence/authenticated
durable approval applies to the protected acknowledgement action against the
already-persisted Incident. Caller-supplied approver identity/receipts remain
prohibited.

## Mandatory evidence

- full non-live suite and repository gates;
- disposable PostgreSQL 16 migration 001-005 round-trip;
- exact Docker cleanup;
- real provider response bound to a successful JWT-authenticated R2 incident
  acknowledgement;
- refusal paths make zero provider calls, success makes exactly one;
- sanitized live/build receipts;
- protected handover/report/freeze zero diff;
- rollback rehearsal is reviewer-owned after BUILD.

No mock provider result can close the governance claim. Missing provider
credentials or a provider failure is a truthful STOP, not permission to
downgrade evidence.

## G6 and return

After C2 is pushed, Claude must rehydrate this handoff plus ADR/SPEC/WORK_ORDER,
declare `IMPLEMENTATION_WORKER`, run every Work Order section 2 precondition,
and implement only the approved set.

Claude performs no stage/commit/push and stops at:

`READY_FOR_INDEPENDENT_INCIDENT_BUILD_REVIEW`

Any stop-condition defect is reported without repair until Codex reviews and
authorizes the next move.

## Claim boundary

Potential closure proves one governed incident vertical on InMemoryLedger,
SQLite and disposable local PostgreSQL 16, with real provider-bound governance
evidence. It does not implement handovers/reports/UI or prove production/
managed-PostgreSQL/provider invocation from a production API endpoint.

## Independent BUILD review and Amendment 1

The first independent review reproduced the full-suite stop
(`483 passed, 43 skipped, 1 failed`) and returned
`REVIEW_CHANGES_REQUIRED`. Findings:

- `INC-REV-F1 OPENAPI_GOLDEN_AUTHORIZATION_GAP`
- `INC-REV-F2 LEDGER_PARITY_DIVERGENCE`
- `INC-REV-F3 SQL_LIST_EVIDENCE_LOSS`
- `INC-REV-F4 VERSION_INVARIANT_ABSENT`
- `INC-REV-F5 LIVE_EVIDENCE_SANITIZATION_GAP`

Independent probes confirmed InMemory duplicate overwrite, SQL list evidence
loss (`get=1`, `list=0`) and acceptance of `version=0`. No PostgreSQL or
provider rerun was performed after the static/full-suite stop.

Authorization Amendment 1 is committed and pushed at
`e1856fc7a05c4967bf633fd656bda85ec94089e6`. It adds exactly:

- `tests/unit/test_p2b_openapi_contract.py`
- `scripts/_incident_live_evidence_support.py`

Final C3 ceiling is exactly 39 paths; no 40th path is conditional. Claude
transitions to `REPAIR_WORKER`, rehydrates the amended ADR/SPEC/WORK_ORDER,
runs fresh G6, repairs F1-F5 without waiver, reruns non-live gates before
fresh PostgreSQL/provider evidence, performs no stage/commit/push, and stops
at:

`READY_FOR_INDEPENDENT_INCIDENT_BUILD_RE_REVIEW`

## Independent repair re-review — second disposition

The independent repair re-review confirms:

- exact 39-path ceiling, zero staged paths and protected zero diff;
- focused non-live `167 passed`;
- full non-live `507 passed, 44 skipped, 1 warning`;
- repository gates and doctor PASS;
- PostgreSQL 16 live `44 passed`, migrations 18/0 then 15/3, exact cleanup;
- fresh real provider call PASS, HTTP 200, exactly one call after five
  observed-zero-call refusal cases.

Closure nevertheless stops on one independently reproduced security defect:

- `INC-REV-F6 ENDPOINT_CREDENTIAL_FAILURE_LEAK`: when a transport exception
  includes `req.full_url`, URL-only credential material in userinfo/query/
  fragment survives `sanitize_secret_text` if it differs from the API key.
  The returned error can then flow into a failure receipt. Independent probe:
  `ENDPOINT_SENTINEL_LEAK=True`.

This is incomplete repair of the already-authorized R15-A/F5 scope, not a new
path requirement. Claude remains `REPAIR_WORKER` and may modify only:

- `scripts/_incident_live_evidence_support.py`;
- `tests/integration/test_incident_live_evidence_runner.py`;
- `docs/decisions/P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md`;
- `docs/decisions/P2A_INCIDENT_BUILD_EVIDENCE_RECEIPT.md`.

The repair must sanitize or safely reject URL userinfo/query/fragment before
any request-construction or transport exception can escape; use an endpoint
sentinel distinct from the API-key sentinel and force an exception containing
the full raw URL. Prove absence from returned error, stdout/stderr and receipt.
Run non-live gates before replacing the live receipt with a fresh real call.
No 40th path, stage, commit, push or self-approval. Stop at:

`READY_FOR_INDEPENDENT_INCIDENT_BUILD_RE_RE_REVIEW`
