# P5-A2 source API identity — bounded intake and source audit

docType: worker_return
Self-declared worker-return artifact: yes
Status: COMPLETE_PENDING_REVIEW
Date: 2026-10-26. Root ORCHESTRATOR/SPEC_AUTHOR; R2, provider calls0.

## Product Milestone Binding

Canonical complete current binding is docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md
at dcaca2c02dfdb012cc55b16907b7c6f31fecf305. This assignment settles only G06/G11
source-read API contract and partial G13 test requirements. Full milestone
acceptance, G01–G14 reconciliation, owners and P5-A2/P5-B/C/D destinations are
retained there; Phase5 0/5, operational coverage UNKNOWN, provider HELD.

## Source-backed findings and decisions

| Source | Observed current fact | Contract consequence |
|---|---|---|
| dependencies.py get_principal / get_principal_with_expiry; auth/tokens.py | General decoder validates signature but does not require exp; strict decoder requires finite valid expiry | Reuse strict dependency in new route, no global auth rewrite |
| application/proactive_source.py query_source | Only internal Principal/scope equality checks; coverage None precedes source IO | Server identity/current user/action and assignment checks before diagnostic; retain None as normal default |
| application/proactive_source.py TrustedSourceScope | Dataclass accepts arbitrary scope/instance labels | Compose from trusted server instance and verified actor, no client source/scope IDs |
| main.py | No proactive router mounted | API remains NOT_IMPLEMENTED; current outcome is contract only |
| application/assignment_scope.py; native proactive SQL and memory ports | ACTIVE assignment is actor-bound; native snapshot/fresh cohort ports exist | Reuse bounded metadata ports, no list-all-shifts selector or privileged bypass |
| cvf_runtime/permission.py | Canonical require_action; no proactive source action exists | Future bounded WO registers proactive.source.read; no local role ordering |
| Ledger.get_user_by_id; User.is_active | Current stored user lookup exists | Recheck activity/role and expiry before and after source read |
| ledger_factory.py | No database config falls back to memory; fixture authority not production authority | No silent standing backend, operational completeness or positive SQLite claim |

Source paths are under apps/workspace-api/src/workspace_api and
packages/cvf-runtime/src/cvf_runtime, packages/operations-ledger/src/operations_ledger.
The Luna read-only audit is supplementary; Root owns the contract and independent
reviewer decides acceptance. No application/source/test code was changed.

## Selected design

GET /proactive/source is a read-only source receipt inspection, not an analytical
run or approval endpoint. Three timestamps only; strict JWT + current stored
user + canonical action; server-owned self scope; native bounded cohort query,
source query and final release checks; no accepted operational coverage means
refusal. Positive synthetic HTTP tests require explicit test-only dependency
injection and independently frozen new server context, without changing old
source/body/PG oracles. Existing matrix owns receipt shapes; future HTTP binding
and parity changes need a separate reviewed implementation WO before BUILD.

The prior provider401 and all prior Docker budgets remain spent. No .env,
credential/model change, network acquisition, provider call, database/container,
route/UI implementation or deployment was performed or authorized here.

## Consolidated planning repair1

Independent API-SPEC-F1/F2 clarified in the same existing SPEC: future API
positives need two independent NEW complete receipts for the server scope,
retaining old body/lineage/numeric facts and leaving old oracles unchanged.
The current native coverage mode is SYNTHETIC_FIXTURE only; operational READY
requires separate native mode/family/emitter/validator and source-authority work,
not merely injecting an operational coverage resolver. No runtime path changed.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: NO
