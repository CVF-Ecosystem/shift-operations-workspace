# Work Order — P2-A Handover Vertical

ID: `P2A-HANDOVER-WO-001`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — BUILD PROHIBITED UNTIL C1 AND C2 ARE PUSHED

## 1. Roles

- ORCHESTRATOR / SPEC_AUTHOR / WORK_ORDER_AUTHOR: Codex
- IMPLEMENTATION_WORKER: Claude
- independent REVIEWER / COMMIT_STEWARD / CLOSER: Codex

Claude performs no stage, commit, push or self-approval. BUILD begins only
after independent authorization REVIEW_PASS, C1 authorization push and C2
pre-BUILD continuity push.

## 2. G6 preconditions

1. Project `HEAD == origin/main` at C2.
2. Staged area empty; tracked tree clean.
3. Only preserved assessment untracked, SHA-256
   `168EA2C7A67A31BAE50C9E4DBE78C2273A692F3A82A1074585E1BDB89B70FDE2`.
4. Core HEAD/origin/manifest equal
   `27137db4d9aa2aea931ddd2507185d5c24943080`; core clean.
5. Doctor 24 PASS, zero FAIL, only bounded legacy catalog warning.
6. Baseline `511 passed, 44 skipped, 1 warning`; repository gates PASS.
7. Docker responds; no foreign `cvf-pg-live-*` resource.
8. Provider credential presence checked without printing its value.

Any mismatch stops BUILD.

## 3. Exact authorized C3 changed set

Exactly these 39 paths:

1. `database/migrations/006_handovers.sql` — NEW
2. `packages/operations-domain/src/operations_domain/models.py`
3. `packages/operations-domain/src/operations_domain/lifecycle.py`
4. `apps/workspace-api/src/workspace_api/domain/models.py`
5. `apps/workspace-api/src/workspace_api/domain/lifecycle.py`
6. `packages/cvf-runtime/src/cvf_runtime/permission.py`
7. `packages/operations-ledger/src/operations_ledger/ledger.py`
8. `packages/operations-ledger/src/operations_ledger/tables.py`
9. `packages/operations-ledger/src/operations_ledger/_handover_tables.py` — NEW
10. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
11. `packages/operations-ledger/src/operations_ledger/_handover_store.py` — NEW
12. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
13. `apps/workspace-api/src/workspace_api/infrastructure/_handover_repository.py` — NEW
14. `apps/workspace-api/src/workspace_api/application/handover_service.py` — NEW
15. `apps/workspace-api/src/workspace_api/api/handovers/router.py` — NEW
16. `apps/workspace-api/src/workspace_api/main.py`
17. `packages/workspace-contracts/handovers/handover.schema.json`
18. `apps/workspace-api/src/workspace_api/application/shift_service.py`
19. `tests/cvf/test_ledger_protocol.py`
20. `tests/cvf/test_handover_vertical.py` — NEW
21. `tests/integration/test_schema_parity_handovers.py` — NEW
22. `tests/integration/test_sql_ledger_handovers.py` — NEW
23. `tests/integration/test_handover_postgres_live.py` — NEW
24. `tests/unit/test_p2b_openapi_contract.py`
25. `tests/cvf/test_freeze_invariant.py`
26. `tests/cvf/test_shift_close_governance.py`
27. `tests/cvf/_shift_close_fixtures.py` — NEW
28. `tests/cvf/test_shift_close_freeze_interaction.py` — NEW
29. `docs/reference/FILE_SPLIT_DEBT_BASELINE.json`
30. `scripts/run_handover_live_governance_evidence.py` — NEW
31. `scripts/_handover_live_evidence_support.py` — NEW
32. `tests/integration/test_handover_live_evidence_runner.py` — NEW
33. `docs/decisions/P2A_HANDOVER_LIVE_EVIDENCE_RECEIPT.md` — NEW
34. `docs/decisions/P2A_HANDOVER_BUILD_EVIDENCE_RECEIPT.md` — NEW
35. `docs/catalog/MODULE_REGISTRY.json`
36. `docs/catalog/MODULE_CATALOG.md`
37. `docs/cvf/CVF_CONTROL_MAPPING.md`
38. `scripts/run_postgres_live_roundtrip.py` — target-list change only
39. `tests/integration/test_postgres_live_runner.py` — target-list regression

No 40th path is conditional.

## 4. Protected paths

- migrations 001-005;
- existing PostgreSQL core/incident live modules;
- incident/customer/task/event services, routers and semantics;
- report source/contracts;
- auth/JWT and approval receipt implementation/schema;
- file-size guard, approved allowlist, exception registry, remaining three
  debt entries and their files;
- ADR/SPEC/WORK_ORDER and continuity during BUILD;
- CVF core and `.cvf/**`;
- preserved assessment.

## 5. Required implementation order

1. Add failing model/lifecycle/snapshot/contract tests.
2. Add migration/parity negative tests.
3. Split legacy shift-close test and remove only its debt entry.
4. Add canonical types, migration and table builder.
5. Add ledger mixins and wiring.
6. Add service, permission actions, router and OpenAPI assertions.
7. Replace only the handover half of freeze override with real readiness.
8. Add live-evidence tests before runner/support implementation.
9. Run focused then full non-live suite.
10. Run PostgreSQL 16 and exact cleanup.
11. Run real provider evidence.
12. Write truthful sanitized receipts.
13. Regenerate catalog/control truth and run every gate.
14. Stop for independent review.

## 6. Non-negotiable implementation details

- Caller never supplies handover items/digests/status/actors.
- Snapshot source types and open predicates are exact.
- Digest and item order are deterministic across backends.
- Review/ack/freeze revalidate exact membership and digest.
- Canonical digest fields/encoding match SPEC R3 byte-for-byte.
- Source not-FROZEN and destination OPEN are rechecked at every governed
  transition and freeze.
- Receiver differs from reviewer.
- Do not claim receiver assignment to destination shift; no assignment
  registry exists.
- Report override never bypasses handover.
- All combined mutation/audit operations use one transaction.
- Python files stay <=300 without compression.
- Legacy shift-close split uses the required shared fixture module; debt
  baseline loses only that compliant path.

## 7. Mandatory evidence return

- G6 facts and exact 39-path list;
- focused suite results by concern;
- full non-live result;
- migration first/reapply counts;
- PostgreSQL live count and cleanup proof;
- provider model/host/status/token and observed call counts, sanitized;
- every touched Python line count;
- validator/catalog/session/file-size/diff/doctor results;
- protected zero diff and assessment hash;
- zero staged, no commit/push.

Return checkpoint:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_REVIEW`

## 8. Stop conditions

STOP on:

- required 40th path;
- ambiguity in open-work or digest semantics;
- migration/source/OpenAPI drift;
- report override still bypassing handover;
- production/freeze/identity/security defect;
- secret-bearing output;
- provider/PostgreSQL/Docker failure;
- file >300, remaining debt drift or repository gate failure;
- existing regression.

No repair after STOP without independent reviewer disposition.

## 9. Commit and closure ownership

After REVIEW_PASS, Codex stages/commits/pushes exactly the 39 C3 paths.

C4 separately updates only:

- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- `SESSION/SESSION_MEMORY.md`;
- active handoff;
- `IMPLEMENTATION_STATUS.json`;
- `docs/implementation/EXECUTION_ROADMAP.md`.

Potential closure marks handovers closed bounded and identifies the next
roadmap move without claiming Phase 2 exit gate unless report/start-to-freeze
evidence is separately satisfied.

## 10. Independent authorization disposition

Authorization review findings:

- `HOV-AUTH-F1 DIGEST_SHAPE_AMBIGUOUS`;
- `HOV-AUTH-F2 DESTINATION_AUTHORITY_OVERCLAIM`;
- `HOV-AUTH-F3 FREEZE_DESTINATION_DRIFT`.

All were repaired in ADR/SPEC/this Work Order without waiver. Independent
disposition: `REVIEW_PASS`. Codex approves this exact 39-path Work Order under
the operator-delegated reviewer authority on 2026-07-26.

Status becomes `APPROVED — BUILD PROHIBITED UNTIL C1 AND C2 ARE PUSHED`.
