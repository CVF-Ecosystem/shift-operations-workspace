# Work Order — P2-A Incident Vertical

ID: `P2A-INCIDENT-WO-001`
Tranche: `P2A-INCIDENT-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — BUILD PROHIBITED UNTIL C1 AND C2 ARE PUSHED

## 1. Roles

- ORCHESTRATOR / SPEC_AUTHOR / WORK_ORDER_AUTHOR: Codex
- IMPLEMENTATION_WORKER: Claude
- independent REVIEWER / COMMIT_STEWARD / CLOSER: Codex

Claude may implement only after Codex records an independent authorization
disposition and both C1 authorization and C2 pre-BUILD continuity commits are
pushed. Claude does not stage, commit, push or self-approve.

## 2. Preconditions (G6)

Before BUILD:

1. Project `HEAD == origin/main` at C2.
2. Staged area empty; tracked tree clean.
3. Only the preserved assessment is untracked, with SHA-256
   `168EA2C7A67A31BAE50C9E4DBE78C2273A692F3A82A1074585E1BDB89B70FDE2`.
4. Core HEAD/origin/manifest all equal
   `27137db4d9aa2aea931ddd2507185d5c24943080`; core clean.
5. Doctor has 24 PASS, zero FAIL and only the bounded legacy catalog warning.
6. Full baseline and repository gates pass.
7. Docker daemon responds and no `cvf-pg-live-*` container from another run
   exists.
8. Required provider credential is present only as an environment
   prerequisite check; never print/read it into evidence or chat.

Any mismatch stops BUILD.

## 3. Authorized C3 BUILD changed set

Exactly these 37 paths are authorized:

1. `database/migrations/005_incidents.sql` — NEW
2. `packages/operations-domain/src/operations_domain/models.py`
3. `packages/operations-domain/src/operations_domain/lifecycle.py`
4. `apps/workspace-api/src/workspace_api/domain/models.py`
5. `apps/workspace-api/src/workspace_api/domain/lifecycle.py`
6. `packages/cvf-runtime/src/cvf_runtime/permission.py`
7. `packages/operations-ledger/src/operations_ledger/ledger.py`
8. `packages/operations-ledger/src/operations_ledger/tables.py`
9. `packages/operations-ledger/src/operations_ledger/_incident_tables.py` — NEW
10. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
11. `packages/operations-ledger/src/operations_ledger/_incident_store.py` — NEW
12. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
13. `apps/workspace-api/src/workspace_api/infrastructure/_incident_repository.py` — NEW
14. `apps/workspace-api/src/workspace_api/application/incident_service.py` — NEW
15. `apps/workspace-api/src/workspace_api/api/incidents/router.py` — NEW
16. `apps/workspace-api/src/workspace_api/main.py`
17. `apps/workspace-api/src/workspace_api/application/approval_receipts.py`
18. `packages/workspace-contracts/incidents/incident.schema.json`
19. `tests/unit/test_operations_domain_shim_identity.py`
20. `tests/unit/test_operations_domain_serialization.py`
21. `apps/workspace-api/src/workspace_api/tests/test_lifecycle.py`
22. `tests/cvf/test_ledger_protocol.py`
23. `tests/cvf/test_incident_vertical.py` — NEW
24. `tests/integration/test_schema_parity_incidents.py` — NEW
25. `tests/integration/test_sql_ledger_incidents.py` — NEW
26. `tests/integration/test_evidence_persistence.py`
27. `tests/integration/test_incident_postgres_live.py` — NEW
28. `tests/unit/test_incident_openapi_contract.py` — NEW
29. `scripts/run_incident_live_governance_evidence.py` — NEW
30. `tests/integration/test_incident_live_evidence_runner.py` — NEW
31. `docs/decisions/P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md` — NEW, generated/sanitized
32. `docs/decisions/P2A_INCIDENT_BUILD_EVIDENCE_RECEIPT.md` — NEW
33. `docs/catalog/MODULE_REGISTRY.json`
34. `docs/catalog/MODULE_CATALOG.md`
35. `docs/cvf/CVF_CONTROL_MAPPING.md`
36. `scripts/run_postgres_live_roundtrip.py` — pytest target-list extension only
37. `tests/integration/test_postgres_live_runner.py` — target-list regression only

No 38th path is conditional. If a required change is outside this set, STOP
and request an authorization amendment.

## 4. Protected paths

Read-only during BUILD:

- migrations 001-004;
- existing PostgreSQL live test module; runner/runner-test behavior outside
  the exact two-module pytest target list;
- handover/report/freeze source, tests and contracts;
- task/event/customer-request services and routers;
- auth/JWT code;
- approval storage schema and migration 004;
- file-size debt baseline/exception registry/guard implementation;
- ADR/SPEC/WORK_ORDER and all continuity surfaces;
- CVF core and `.cvf/**`;
- preserved assessment.

## 5. Required implementation order

1. Add failing domain/lifecycle/contract tests.
2. Add migration/parity negative tests.
3. Add canonical model/lifecycle and migration/table builder.
4. Add ledger mixins and minimal host-file wiring.
5. Add application service/permission/approval receipt target support.
6. Add router/OpenAPI tests.
7. Add live-evidence runner tests before runner implementation.
8. Run focused non-live tests, then full non-live suite.
9. Run disposable PostgreSQL 16 suite and cleanup verification.
10. Run real provider-bound incident governance evidence.
11. Write sanitized receipts from actual results.
12. Update bounded control mapping/catalog truth and regenerate catalog.
13. Run all repository gates and stop for independent review.

## 6. Split-file guards

- Every Python file <= 300 physical lines.
- Host files named in SPEC R11 receive wiring only.
- No debt/exception change.
- New incident test concerns remain separated.
- If a host file would exceed its limit, STOP; do not compress readability,
  concatenate statements or hide logic to satisfy line count.

## 7. Required evidence return

Claude returns:

- G6 facts and exact changed/untracked set;
- focused test commands/results;
- full suite result;
- migration first/reapply counts;
- PostgreSQL live test count and exact cleanup proof;
- provider endpoint family/model/status/expected token and call counts, fully
  sanitized;
- file line counts for every touched Python file;
- validator/catalog/session/file-size/diff/doctor results;
- protected-boundary zero diff;
- assessment hash;
- statement: no stage/commit/push.

Return checkpoint:

`READY_FOR_INDEPENDENT_INCIDENT_BUILD_REVIEW`

## 8. Stop conditions

STOP immediately on:

- any required 38th path;
- migration/source/contract ambiguity;
- production or approval/security defect;
- existing test regression;
- provider prerequisite missing/failure;
- any secret/DSN/password in output;
- Docker resource ownership uncertainty;
- file-size/debt/catalog/session/doctor failure;
- handover/report/freeze semantic diff.

No repair after a stop condition without independent reviewer disposition.

## 9. Commit ownership and closure

After REVIEW_PASS, Codex stages/commits/pushes exactly the 37 C3 paths. C4
updates only the six canonical closure surfaces already used by the prior
tranche:

- `SESSION/ACTIVE_SESSION_STATE.json`
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`
- `SESSION/SESSION_MEMORY.md`
- active handoff
- `IMPLEMENTATION_STATUS.json`
- `docs/implementation/EXECUTION_ROADMAP.md`

C3 and C4 are separate commits. Closure advances only the incident roadmap
item; handovers remain open and become the next governed tranche.

## 10. Authorization review disposition

`INC-AUTH-F1 OVERBROAD_GUARD_TEST_PATHS` and
`INC-AUTH-F2 LIVE_TEST_SPLIT_CONFLICT` were repaired without waiver before
approval. The changed-set count remains exactly 37: two unnecessary guard-test
edits were removed; the split incident PostgreSQL module plus bounded
runner/runner-test target-list changes replace the over-limit design.

Independent authorization disposition: `REVIEW_PASS`. Codex approves this
Work Order under operator-delegated reviewer authority on 2026-07-26. Claude
may begin BUILD only after C1 and the successor C2 continuity acknowledgment
are both present on `origin/main`.

## 11. Amendment 1 — bounded repair order

Status: APPROVED — REPAIR PROHIBITED UNTIL AMENDMENT COMMIT AND CONTINUITY
ACKNOWLEDGMENT ARE PUSHED

The independent BUILD review disposition is `REVIEW_CHANGES_REQUIRED`.
Claude transitions from IMPLEMENTATION_WORKER to REPAIR_WORKER only after
rehydrating the pushed amendment and successor continuity acknowledgment.
No self-approval, stage, commit or push is permitted.

### 11.1 Added final-C3 paths

The original 37 paths remain authorized. Exactly two paths are added:

38. `tests/unit/test_p2b_openapi_contract.py`
39. `scripts/_incident_live_evidence_support.py` — NEW

The final C3 ceiling is exactly 39 paths. No 40th path is conditional.

### 11.2 Findings to repair

1. `INC-REV-F1 OPENAPI_GOLDEN_AUTHORIZATION_GAP`
   - Validate that the generated OpenAPI delta is exactly the five incident
     operations and their reachable canonical schemas.
   - Then update the existing repository-wide golden digest and retain the
     incident-specific exact contract assertions.
2. `INC-REV-F2 LEDGER_PARITY_DIVERGENCE`
   - Normalize duplicate add and missing put behavior across InMemoryLedger
     and SqlLedger as required by SPEC R6-A.
   - Add cross-backend tests, including equal-created-at deterministic order.
3. `INC-REV-F3 SQL_LIST_EVIDENCE_LOSS`
   - Reconstruct incident evidence in SQL list results inside the same
     connection/unit and prove get/list parity.
4. `INC-REV-F4 VERSION_INVARIANT_ABSENT`
   - Enforce `version >= 1` in the canonical model, migration 005 and metadata
     with exact parity and negative SQLite/PostgreSQL coverage.
5. `INC-REV-F5 LIVE_EVIDENCE_SANITIZATION_GAP`
   - Move provider HTTP, sanitization, safe endpoint description and receipt
     rendering into the new support module.
   - Add sentinel-bearing failure tests covering returned summaries,
     stdout/stderr and receipt; reset and observe provider-call accounting.
   - Rerun PostgreSQL 16 and the real provider only after all non-live tests
     pass, then replace both evidence receipts with truthful fresh results.

Repair may modify only affected paths already in the original 37-path set
plus paths 38-39 above. Authorization documents and continuity files are
read-only during repair. Existing migrations 001-004, handover/report/freeze,
auth/JWT, debt/exception registry, CVF core and the preserved assessment
remain protected.

### 11.3 Mandatory return evidence

Return:

- focused cross-backend/parity/OpenAPI/sanitization tests;
- full non-live suite with zero failure/error;
- disposable PostgreSQL 16 migration 001-005 and incident live suite;
- exact Docker cleanup;
- fresh real-provider-bound acknowledgement evidence with observed refusal
  count zero and success count one;
- sentinel secret absence from all runner outputs and receipt;
- all repository gates, line counts, exact 39-path set, zero staged paths,
  protected zero diff and preserved assessment hash.

Stop at:

`READY_FOR_INDEPENDENT_INCIDENT_BUILD_RE_REVIEW`

Any new production/schema/approval/security defect, secret-bearing output,
provider failure, Docker ownership uncertainty or required 40th path is a
STOP condition. Codex independently approves this amendment without waiver
under the operator-delegated reviewer/work-order authority.
