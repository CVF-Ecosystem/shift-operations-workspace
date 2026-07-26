# Work Order — CVF File-Split Guard Hardening

Status: APPROVED — BUILD AWAITS C1/C2 PUSH AND FRESH G6
Work Order ID: `CVF-FSG-WO-001`
Risk: R2
Implementation worker: Claude
Independent reviewer / commit steward: Codex

## 1. Objective

Implement `CVF-FSG-SPEC-001` so executable file splitting is enforced by
repository gates, repay the seven oversized files touched by P2B C3, and
ratchet untouched legacy debt by exact digest.

## 2. Preconditions

Before the first BUILD edit, Claude must:

1. rehydrate mandatory CVF continuity and declare `IMPLEMENTATION_WORKER`;
2. verify `HEAD == origin/main` at the post-C2 commit;
3. verify zero tracked modifications;
4. verify the only untracked path is the preserved assessment with SHA-256
   `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`;
5. run doctor and accept only `24 PASS`, zero FAIL and the one bounded legacy
   catalog-kit warning;
6. run the full suite and record its actual post-C2 baseline;
7. run `python scripts/check_file_size.py --warn` and record the debt set;
8. verify every allowed path below exists or is explicitly marked NEW.

Any mismatch is a stop condition.

## 3. C3 BUILD changed-set ceiling

Only these 24 paths are authorized:

### Guard and evidence

1. `scripts/check_file_size.py`
2. `docs/reference/FILE_SIZE_GUARD.md`
3. `docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json`
4. `docs/reference/FILE_SPLIT_DEBT_BASELINE.json` — NEW
5. `tests/integration/test_file_size_guard.py` — NEW

### Approval application split

6. `apps/workspace-api/src/workspace_api/application/approval_service.py`
7. `apps/workspace-api/src/workspace_api/application/approval_receipts.py` — NEW
8. `apps/workspace-api/src/workspace_api/application/task_creation_intents.py` — NEW

### In-memory ledger split

9. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
10. `apps/workspace-api/src/workspace_api/infrastructure/_approval_store.py` — NEW

### SQL ledger split

11. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
12. `packages/operations-ledger/src/operations_ledger/_approval_store.py` — NEW

### Live-evidence script split

13. `scripts/run_approval_governance_evidence.py`
14. `scripts/_approval_governance_evidence_support.py` — NEW

### P2B acceptance-test split

15. `tests/cvf/test_approver_identity_reconciliation.py`
16. `tests/cvf/_approver_identity_support.py` — NEW
17. `tests/cvf/test_approver_identity_receipts.py` — NEW
18. `tests/cvf/test_approver_identity_task_intents.py` — NEW

### Schema/OpenAPI test split

19. `tests/integration/test_schema_parity.py`
20. `tests/integration/test_schema_parity_approval_receipts.py` — NEW
21. `tests/unit/test_operations_domain_serialization.py`
22. `tests/unit/test_p2b_openapi_contract.py` — NEW

### Generator-owned catalog

23. `docs/catalog/MODULE_REGISTRY.json`
24. `docs/catalog/MODULE_CATALOG.md`

Catalog files may be changed only by
`python scripts/generate_catalog.py --write`, and only for exact authorized
metric/file-count drift.

No other path is conditionally allowed.

## 4. Extraction constraints

1. Keep `approval_service.py` as the compatibility facade for all existing
   imports.
2. Keep `InMemoryLedger` and `SqlLedger` public classes and method signatures.
3. Helpers may be functions/mixins, but cannot own a second independent
   business-rule implementation.
4. Do not compress statements, delete assertions, merge tests artificially or
   remove comments solely to pass line limits.
5. Split tests by coherent behavior; every pre-split test node must remain
   discoverable, allowing module-name relocation but no semantic deletion.
6. No file may enter the debt baseline if it was touched by P2B C3.
7. No executable path may enter the exception registry.
8. The debt baseline is exactly the four paths enumerated by SPEC R12; no fifth
   path is permitted.
9. `scripts/testing/validate_repository.py`, `.githooks/pre-commit`,
   `.github/workflows/ci.yml` and `Makefile` are read-only evidence surfaces
   and must remain byte-identical.

## 5. Required implementation order

1. Add failing guard tests for SPEC AC-01 through AC-12.
2. Harden checker and registries until negative tests pass.
3. Split the seven immediate target files without behavior change.
4. Independently compute the remaining debt baseline.
5. Run focused P2B/schema/OpenAPI suites.
6. Regenerate catalog.
7. Run the complete evidence bundle.
8. Stop at `READY_FOR_INDEPENDENT_BUILD_REVIEW`.

## 6. Required evidence

Claude must return:

- exact changed path set and path count;
- G6 Git/core/assessment/doctor/full-suite baseline;
- guard focused-test result;
- list of all executable files and line counts at/above warnings;
- debt baseline entries with independently computed hashes;
- before/after test-node inventory for split test modules;
- focused P2B, schema parity and OpenAPI results;
- root full-suite result;
- validator/session/catalog/file-size/diff results;
- confirmation of no provider call, secret read or PostgreSQL run;
- confirmation nothing was staged, committed or pushed.

## 7. Reviewer probes

Codex will independently:

1. recompute every governed line count and debt digest;
2. create temporary negative fixtures for all bypass classes;
3. test a same-line-count content change against legacy debt;
4. test an executable exception attempt;
5. compare pre-/post-split test node inventory;
6. verify import compatibility and exact OpenAPI/response schemas;
7. run focused and full suites;
8. verify catalog drift and the 24-path ceiling;
9. perform AC-24 revert rehearsal in a temporary sibling worktree.

Claude's own successful tests are evidence input, not reviewer approval.

## 8. Stop conditions

Stop immediately if:

- any required split needs a 25th path;
- a public signature/schema/behavior changes;
- a test must be deleted or weakened;
- a C3-touched oversized file cannot reach the limit cleanly;
- the debt set cannot be reproduced deterministically;
- catalog regeneration produces unrelated field drift;
- doctor gains a new warning/failure;
- any provider/secret/PostgreSQL operation appears necessary;
- the assessment changes;
- staging, commit or push occurs.

Report the condition; do not widen scope or weaken the guard.

## 9. Commit discipline

- C1: ADR + SPEC + WORK_ORDER only, after independent authorization review.
- C2: pre-BUILD continuity and new active handoff only.
- C3: BUILD only, after independent `REVIEW_PASS`.
- C4: FREEZE continuity/status/roadmap only.

Claude owns no commit action. Codex owns commits and pushes after review.

## 10. C4 closure ceiling

C4 may change only:

1. `SESSION/ACTIVE_SESSION_STATE.json`
2. `SESSION/SESSION_MEMORY.md`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. the active split-guard handoff
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`

No source, test, guard, catalog or authorization artifact belongs in C4.

## 11. Claim boundary

This tranche proves repository-enforced split limits and extraction
compatibility only. It does not prove governance of AI/agent behavior, invoke
a provider, read a secret, verify PostgreSQL or close Phase 1.

## 12. Authorization gate

BUILD remains prohibited until Codex:

1. independently reviews this exact ADR/SPEC/WORK_ORDER;
2. records `REVIEW_PASS`;
3. explicitly approves this Work Order;
4. commits/pushes C1 separately;
5. commits/pushes C2 pre-BUILD continuity;
6. directs Claude to run fresh G6 on the post-C2 HEAD.

## 13. Authorization receipt

Independent review initially found and repaired without waiver:

- `FSG-AUTH-F1 AMBIGUOUS_DEBT_SET`;
- `FSG-AUTH-F2 UNNECESSARY_ROUTE_SURFACE_WRITE_SCOPE`.

Re-review disposition: `REVIEW_PASS`.

Under the operator-delegated reviewer and Work Order approval authority, Codex
approves this Work Order intact on 2026-07-26.

This approval is conditional on separate C1 and C2 commits being pushed and a
fresh G6 at the actual post-C2 HEAD. It is not permission to build from the
current uncommitted authorization working tree.
