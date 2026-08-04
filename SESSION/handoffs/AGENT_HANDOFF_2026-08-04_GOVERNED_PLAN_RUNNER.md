# Agent Handoff — Governed Plan Runner

## Disposition

- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Parent: P3-A Refinery `CLOSED_BOUNDED` at FREEZE `3c53882`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Active role: `COMMIT_STEWARD`
- Status: `AUTHORIZATION_REVIEW_PASS_CHECKPOINT_PENDING`

## Intent and boundary

The operator requested an immediate project-local fix for mechanical workflow
failures whose latency and quota cost exceeded their product value. The runner
validates and simulates argv/byte plans before R2, then provides atomic local
execution and deterministic receipts. It changes no CVF core or policy
semantics and grants no retry of consumed approvals.

## Authority candidate

- ADR: `docs/decisions/ADR_2026-08-04_GOVERNED_PLAN_RUNNER.md`
  (`4c273fc8f0fb984ffa4b2ce0061b981ccb89efd6097ddb873780f82aefa9ed97`)
- SPEC: `docs/specs/GOVERNED_PLAN_RUNNER_SPEC.md`
  (`b26b90388e5b41c58aa11d2f245a3ee590fb82fafd347c496c6b7187f1611260`)
- Work Order: `docs/work_orders/GOVERNED_PLAN_RUNNER_WORK_ORDER.md`
  (`352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`)
- BUILD ceiling: exact eight paths; zero provider/network/remote-ingest calls.

## Next governed move

Initial review `57e1ead6…fe63` is FAIL/GPR-AUTH-F1: reviewer invoked `uv`,
created `.venv`/`uv.lock`, downloaded `pydantic-core` and installed 26 packages
despite zero-network scope. Generated residues were removed, no waiver. Fresh
local-only review `7357cd56…d409` closed F1 but found F2: dependency-complete
Python is 3.11.9 while ADR required >=3.12. ADR now uses compatible >=3.11;
that review granted no BUILD/stage/commit/push authority.

Final local-only review `f7408e2d…ee5f` PASS; F1/F2 closed without waiver,
findings NONE. Push exact10 governance paths, then stop for fresh exact R2.
