# P4-E Identity And Conversation Routing Exact Manifest Amendment 1

Status: PENDING_INDEPENDENT_AUTHORIZATION_REVIEW

Date: 2026-09-10

Risk ceiling: R2

## Purpose

Preserve all useful uncommitted P4-E repair work while correcting the exact
manifest authority after completion review round 3 found fifteen necessary
implementation paths outside the original 94-path ceiling.

This amendment is additive. It does not renumber, delete, rename, or weaken any
of the original 94 entries in
`docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_2026-09-09.md`.

## Source Evidence

| Source | SHA-256 | Use |
|---|---|---|
| Original exact manifest | `edb56012d87e7c4e9b3c715feba6d32a65a90b70064c9fa7d0d3b2abdc03a846` | Frozen 94-path predecessor |
| Original Work Order | `b83eef2bd29ce9a9e436e68050efaab0ed4d9174ee645a56b66a53c83bbe9891` | Predecessor execution contract |
| Worker return generation 2 | `a7b0142a30643e84826dc2cb8efb3643161141cf376082fc1cd6125790a2b343` | Returned implementation and claims |
| Completion review through round 3 | `4ba551a174d696613f476e9f0c5682984409c0667386765f0f1c2182d640de18` | Finding and exact-path reconciliation owner |
| CVF return-time closeability learning | material commit `3fcd426dc7c2c6d03fc915b884711df118a0563f` | Governs amendment/repair routing |

## Effective Product Exact Ceiling

The effective P4-E product packet ceiling is the original 94 paths plus the
following exact 15 worker-owned paths, for 109 unique product-packet paths
total. These paths were observed in the current uncommitted changed set and are
ordinary implementation topology inside the accepted P4-E product directories,
tests, local PostgreSQL proof, and zero-provider boundary.

95. `apps/integration-edge/src/integration_edge/webhook/router.py`
96. `apps/workspace-api/src/workspace_api/application/_p4e_target_eligibility.py`
97. `apps/workspace-api/src/workspace_api/application/p4e_placement_processor.py`
98. `apps/workspace-api/src/workspace_api/infrastructure/_p4e_repository.py`
99. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
100. `packages/operations-ledger/pyproject.toml`
101. `packages/operations-ledger/src/operations_ledger/p4e_transaction_store.py`
102. `scripts/run_p4e_postgres_live_roundtrip.py`
103. `tests/integration/_p4e_webhook_helpers.py`
104. `tests/integration/test_p4e_claim_owner_cas.py`
105. `tests/integration/test_p4e_command_audit_and_idempotency.py`
106. `tests/integration/test_p4e_inmemory_parity.py`
107. `tests/integration/test_p4e_postgres_live_claim_cas.py`
108. `tests/integration/test_p4e_webhook_sender_aware_ingress.py`
109. `tests/integration/test_p4e_webhook_sender_aware_negative.py`

## Amendment Control-Plane Paths

The operator's 2026-09-10 amendment approval separately authorizes these exact
control-plane paths. They are not worker implementation paths and do not count
toward the 109-path product packet ceiling:

- `.cvf/manifest.json`
- `AGENTS.md`
- `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_AMENDMENT_1_2026-09-10.md`
- `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_1_2026-09-10.md`
- `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_1_AUTHORIZATION_REVIEW_2026-09-10.md`

Original paths 83-92 remain the exact continuity/status write surfaces for
activation. The active handoff is updated in place at original path 88; no
successor handoff path is created. The authorization reviewer owns only the
new authorization-review path above. The orchestrator/session-sync steward
owns the two amendment drafts, provenance pins, and original paths 83-92.

## Ownership And Boundary

- `REPAIR_WORKER` owns original paths 15-80 plus additive paths 95-109.
- Original paths 1-14 remain settled governance inputs and are read-only to the
  worker.
- Original paths 81-82 remain independent-reviewer owned.
- Original paths 83-94 remain closer/session-sync owned.
- Catalog paths 93-94 remain closer-owned and are not worker repair paths.
- No additional worker implementation path, deletion, rename, provider call,
  credential read, dependency install, public action, deployment, shared
  database, Phase 5, XR1, or catalog schema migration is authorized.
- Local disposable PostgreSQL through the operator-provided Docker runtime is
  authorized for test evidence; cleanup evidence is required.

## Closeability Reconciliation

| Mandatory result | Phase owner | Legitimate write surface | Closeability disposition |
|---|---|---|---|
| Security, CAS, backend and test repair | REPAIR_WORKER | original 15-80 plus 95-109 | CLOSEABLE after independent amendment acceptance |
| Worker-return correction | REPAIR_WORKER | original path 80 | CLOSEABLE |
| Independent repair review | INDEPENDENT_COMPLETION_REVIEWER | original path 82 | CLOSEABLE |
| Catalog regeneration | CLOSER | original paths 93-94 only | Runs after technical review acceptance, before final full-suite/closure claim |
| Final full regression and repository gates | CLOSER | evidence only; catalog writes limited to 93-94 | CLOSEABLE after catalog regeneration |
| Session/status synchronization | SESSION_SYNC_STEWARD | original paths 83-92 | Only after final acceptance |

When all worker-owned tests pass and the only remaining failure is deterministic
catalog drift that can be resolved solely by the later closer-owned canonical
generator, the worker must keep the contract-compatible terminal verdict
`BLOCKED_WITH_REASON` and record supplemental disposition
`technicalRepairDisposition: COMPLETE_PENDING_CATALOG_AND_REVIEW`. The
supplemental disposition is not a terminal verdict, closure, or commit authority.

## Activation Preconditions

Repair dispatch is unlawful until all of the following are true in one
control-plane commit:

1. independent authorization review accepts both amendment drafts;
2. `.cvf/manifest.json`, `AGENTS.md`, the active rule pack, and current
   continuity agree on private-provenance source commit
   `fe62894f861c34a25a16c6267f557bf771ea9e2c`;
3. original paths 83-92 identify this accepted amendment and the repair worker
   as the next governed move; and
4. control-plane staging/commit contains none of the uncommitted worker source,
   tests, worker return, or completion-review implementation evidence.

## Operator Authorization

On 2026-09-10 the operator accepted the plan to absorb the finding into CVF
first, synchronize the project, issue one consolidated exact-manifest/Work
Order amendment, independently review it, and only then repair the project.
That approval authorizes this explicit 15-path expansion; it does not authorize
any broader path family or automatic future expansion.

## Rollback Boundary

If this amendment is rejected, remove only this amendment and its paired Work
Order amendment/continuity projection. Preserve the original 94-path manifest,
all uncommitted worker source, both existing review artifacts, and historical
commits. Do not delete useful worker work merely to make the old manifest fit.

## Claim Boundary

This amendment proposes an exact authority correction only. It does not accept
the current implementation, close any round-3 finding, authorize commit, or
prove PostgreSQL, provider, deployment, or production behavior.
