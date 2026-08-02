# Work Order — P2-C C3d Supervisor Closeout

- ID: `P2C-C3D-SUPERVISOR-CLOSEOUT-WO-001`
- Parent tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3d`
- Risk: `R2`
- Source-inspection parent: `8359f3f11bfafb1debd8d64ca8a8f5468adfbff5`
- Parent DESIGN: `docs/decisions/ADR_2026-08-02_P2C_C3D_SUPERVISOR_CLOSEOUT.md`
- Parent SPEC: `docs/specs/P2C_C3D_SUPERVISOR_CLOSEOUT_SPEC.md`
- Status: `REVIEW_PASS / APPROVED — BUILD BLOCKED UNTIL PUSHED PRE-BUILD CHECKPOINT AND G6 PASS`

## 1. Authority

An independent `AUTHORIZATION_REVIEWER` MUST compare this order with current
source, C3c closure, parent DESIGN/SPEC and the exact-path inventory. Only an
explicit `REVIEW_PASS / APPROVED`, a committed/pushed authorization package,
a separate pushed pre-BUILD continuity checkpoint and fresh G6 may authorize
BUILD.

The later `IMPLEMENTATION_WORKER` edits only the exact BUILD paths below and
MUST NOT stage, commit, push, self-review or FREEZE. No automated provider-
named agent CLI/MCP call is authorized. Provider access is authorized only in
the dedicated R10 live-evidence step after every refusal/durability gate.

## 2. Exact 36-path BUILD ceiling

Every path MUST change or be created. There is no wildcard, reserve, optional
or self-review path.

### Frontend contracts, data and coordinator — 7 paths

1. `apps/workspace-web/src/services/supervisorApi.ts` — NEW
2. `apps/workspace-web/src/types/supervisorContracts.ts` — NEW
3. `apps/workspace-web/src/types/operations.ts`
4. `apps/workspace-web/src/app/OperationsConsole.tsx`
5. `apps/workspace-web/src/app/useOperationsData.ts`
6. `apps/workspace-web/src/app/useSupervisorData.ts` — NEW
7. `apps/workspace-web/src/app/styles.css`

### Supervisor feature UI — 7 paths

8. `apps/workspace-web/src/features/supervisor-actions/SupervisorActions.tsx` — NEW
9. `apps/workspace-web/src/features/supervisor-actions/types.ts` — NEW
10. `apps/workspace-web/src/features/supervisor-actions/StaffingActions.tsx` — NEW
11. `apps/workspace-web/src/features/supervisor-actions/EventActions.tsx` — NEW
12. `apps/workspace-web/src/features/supervisor-actions/ApprovalActions.tsx` — NEW
13. `apps/workspace-web/src/features/supervisor-actions/IncidentHandoverActions.tsx` — NEW
14. `apps/workspace-web/src/features/supervisor-actions/ReportFreezeActions.tsx` — NEW

### Frontend component/contract proof — 6 paths

15. `apps/workspace-web/src/tests/App.test.tsx`
16. `apps/workspace-web/src/tests/supervisorApi.test.ts` — NEW
17. `apps/workspace-web/src/tests/supervisorContracts.test.ts` — NEW
18. `apps/workspace-web/src/tests/supervisorStaffing.test.tsx` — NEW
19. `apps/workspace-web/src/tests/supervisorApprovals.test.tsx` — NEW
20. `apps/workspace-web/src/tests/supervisorCloseout.test.tsx` — NEW

### Real-browser/static proof — 6 paths

21. `apps/workspace-web/e2e/operator-flow-helpers.ts`
22. `apps/workspace-web/e2e/supervisor-flow.spec.ts` — NEW
23. `apps/workspace-web/e2e/supervisor-flow-accessibility.spec.ts` — NEW
24. `scripts/testing/run_c3c_web_evidence.py`
25. `scripts/testing/run_c3d_web_evidence.py` — NEW
26. `tests/integration/test_c3d_web_evidence_runner.py` — NEW

### Fresh provider evidence and receipts — 6 paths

27. `scripts/run_p2c_c3d_live_governance_evidence.py` — NEW
28. `scripts/_p2c_c3d_live_evidence_support.py` — NEW
29. `tests/integration/test_p2c_c3d_live_evidence_runner.py` — NEW
30. `docs/decisions/P2C_C3D_BUILD_EVIDENCE_RECEIPT.md` — NEW
31. `docs/decisions/P2C_C3D_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md` — NEW
32. `docs/cvf/CVF_CONTROL_MAPPING.md`

### Generated catalog and harness regression — 4 paths

33. `docs/catalog/MODULE_REGISTRY.json`
34. `docs/catalog/MODULE_CATALOG.md`
35. `tests/integration/test_c3c_web_evidence_runner.py`
36. `apps/workspace-web/src/tests/supervisorMutationState.test.tsx` — NEW

An outside path is `BLOCKED_WORK_ORDER_CEILING`. An unnecessary listed path
requires exact-set contraction; synthetic edits are forbidden. Any required
split path requires reviewed DESIGN->SPEC->WORK_ORDER amendment first.

## 3. Implementation contract

1. `supervisorApi.ts` MUST wrap the existing exported request primitive and
   implement only R2-R6 routes/payloads. It MUST NOT fork auth/error/retry.
2. `useSupervisorData.ts` MUST keep staffing state separate, treat server 403
   as no staffing surface without role ranking, suppress stale responses and
   expose a real rejecting refresh promise.
3. `useOperationsData.ts` MUST retain all Events; only the timeline projection
   remains confirmed-only. Existing C3c behavior must not regress.
4. Supervisor components MUST be feature-owned, reset on selected-shift
   changes, use the shared mutation hook/feedback, reflect capabilities only
   as advisory hints and obey the exact lifecycle/target matrix. Because the
   server capability list has no `approval.create`, its absence MUST NOT hide
   all receipt controls or become client-side refusal authority.
5. Staffing never grants operational visibility. Assignment refresh must make
   newly assigned shifts appear only through the ordinary server read. If a
   refreshed ordinary list omits the selected shift, the coordinator MUST
   clear selection and retained operational state (including self-revoke).
6. Approval payload is exactly three fields for the five POST-supported pairs,
   including `OperationalEvent/event.correct`. Fresh sanitized readiness is
   required only for the four pairs supported by the existing readiness GET;
   `event.correct` performs the operational refresh without inventing a
   readiness route. Report approval revocation uses the existing successor
   endpoint with reason/current version/status.
7. Freeze sends only expected version. No retired override field may exist in
   supervisor DTO, DOM or observed request body.
8. Every TS/TSX file stays <=200 physical lines; no exemption/debt is added.

## 4. Evidence contract

The parameterized owned web harness MUST preserve the C3c runner contract and
run the complete operator+supervisor Playwright suite for C3d. It owns ports,
child processes, SQLite path, build/test artifacts and cleanup; it redacts all
failure output. Its integration tests prove command construction, checkpoint
selection, readiness timeout, failure propagation and cleanup without opening
a browser.

The live-governance runner MUST execute real JWT/FastAPI closeout probes,
observe zero provider calls for all refusal cases, verify final stored state
and exact actor-bound audits, then make exactly one real provider call. Tests
must inject transport and sentinel secrets to prove call ordering, failure
truthfulness and sanitization without making a provider call.

Before that provider call, `scripts/run_postgres_live_roundtrip.py --json`
MUST freshly apply and reapply migrations, run its current full pinned backend
matrix through C3b2 (including assignment, assignment-scope, read and mutation-
precondition coverage), and prove exact owned container/volume cleanup. C3c
and C3d add no PostgreSQL target because their protected backend is unchanged.
The script is execution-only and MUST remain byte-identical in this frontend/
evidence BUILD.

## 5. Protected boundary

Zero diff is mandatory for backend/domain/ledger/database/migrations/OpenAPI;
offline queue; package/lock versions; provider configuration; CI; `.cvf/**`;
roadmap/implementation status/continuity; C3c receipts; and P2-D/full-shift
exit artifacts. C4 truth sync is separate.

## 6. Pre-BUILD G6

From a separate clean pushed checkpoint:

1. verify `HEAD == origin/main`, clean worktree, exact parent and authorization
   ancestry;
2. rehydrate mandatory continuity plus C3d INTAKE/DESIGN/SPEC/WO/review;
3. verify C3c `65b10d2` and its closure commit are ancestors;
4. run full Python and frozen frontend baselines with exact counts;
5. verify Node `22.14.0`, pnpm `9.15.0`, Playwright `1.62.1`, Chromium,
   Docker/PostgreSQL/provider prerequisites and zero owned residue;
6. pass session/catalog/file-size/repository/JSON/diff and doctor 24/1-only
   gates;
7. stop `BLOCKED_G6` before source edit/provider call on any failure.

## 7. Required commands/evidence order

```powershell
pnpm --dir apps/workspace-web install --frozen-lockfile
pnpm --dir apps/workspace-web run typecheck
pnpm --dir apps/workspace-web run test
pnpm --dir apps/workspace-web run build
python -m pytest -q tests/integration/test_c3d_web_evidence_runner.py tests/integration/test_p2c_c3d_live_evidence_runner.py
python scripts/testing/run_c3d_web_evidence.py --json
python -m pytest -q
python scripts/run_postgres_live_roundtrip.py --json
python scripts/run_p2c_c3d_live_governance_evidence.py
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
```

Provider execution occurs only after all refusal and durable-closeout checks.
AC-29 exact-parent rehearsal must restore the recorded G6 baseline and remove
its temporary worktree. The worker reports exact results, changed set, receipt
paths, cleanup, zero staged files and:

`READY_FOR_INDEPENDENT_P2C_C3D_BUILD_REVIEW`

## 8. Stop and claim boundary

STOP on any SPEC stop condition, outside/unneeded path, missing prerequisite,
nonzero refusal call, browser skip/mock, secret/digest leak, retired override,
fake success, backend diff, incomplete cleanup or regression.

This approval still authorizes no BUILD until the pushed pre-BUILD checkpoint
and G6 pass. After a reviewed BUILD, C3d may prove the specified supervisor
controls and final bounded P2-C governance evidence only. P2-C closure still
requires separate C4 truth sync. P2-D, the full-shift exit gate and Phase 2
completion remain open.
