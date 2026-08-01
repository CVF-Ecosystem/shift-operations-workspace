# Work Order — P2-C C3c Operator Mutation UI

- ID: `P2C-MUTATION-FULL-UI-C3C-WO-001`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3c`
- Risk: `R2`
- Reviewed implementation parent: `a992c44fa16003d5de27feb6fbcf34cd1f83d7aa`
- Parent DESIGN: `docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md`
- Parent SPEC: `docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`
- Status: `APPROVED — BUILD ONLY AFTER PUSHED PRE-BUILD CHECKPOINT AND G6`

## 1. Authority and boundary

The operator delegated Work Order approval authority to Codex. An independent
`AUTHORIZATION_REVIEWER` MUST compare this exact-path order with the pushed
C3b1/C3b2 closure, current frontend and route contracts, DESIGN/SPEC R18-R21,
R26-R33 and AC-19..AC-22/AC-27/AC-29..AC-33.

The later `IMPLEMENTATION_WORKER` may edit only the exact BUILD paths below and
MUST NOT stage, commit, push, self-review or FREEZE. No Claude CLI, provider MCP
or automated Claude call is authorized. C3c implements operator controls only;
it adds no supervisor/staffing/approval/confirm/acknowledge/freeze/correction
control, offline/realtime behavior or P2-C completion claim.

## 2. Exact 38-path BUILD ceiling

Every path below MUST change or be created. There is no wildcard, reserve,
optional path or self-review path.

### Frontend transport, contracts and read coordinator — 8 paths

1. `apps/workspace-web/package.json`
2. `pnpm-lock.yaml`
3. `apps/workspace-web/src/services/api.ts`
4. `apps/workspace-web/src/services/operatorApi.ts` — NEW
5. `apps/workspace-web/src/types/operations.ts`
6. `apps/workspace-web/src/types/backendContracts.ts`
7. `apps/workspace-web/src/app/OperationsConsole.tsx`
8. `apps/workspace-web/src/app/useOperationsData.ts` — NEW

### Operator feature and presentation — 12 paths

9. `apps/workspace-web/src/app/styles.css`
10. `apps/workspace-web/src/features/operator-actions/OperatorActions.tsx` — NEW
11. `apps/workspace-web/src/features/operator-actions/MutationFeedback.tsx` — NEW
12. `apps/workspace-web/src/features/operator-actions/useMutationControl.ts` — NEW
13. `apps/workspace-web/src/features/operator-actions/types.ts` — NEW
14. `apps/workspace-web/src/features/operator-actions/ShiftActions.tsx` — NEW
15. `apps/workspace-web/src/features/operator-actions/MessageEventActions.tsx` — NEW
16. `apps/workspace-web/src/features/operator-actions/TaskActions.tsx` — NEW
17. `apps/workspace-web/src/features/operator-actions/CustomerRequestActions.tsx` — NEW
18. `apps/workspace-web/src/features/operator-actions/IncidentActions.tsx` — NEW
19. `apps/workspace-web/src/features/operator-actions/HandoverActions.tsx` — NEW
20. `apps/workspace-web/src/features/operator-actions/ReportActions.tsx` — NEW

### Component and contract proof — 7 paths

21. `apps/workspace-web/src/tests/App.test.tsx`
22. `apps/workspace-web/src/tests/api.test.ts`
23. `apps/workspace-web/src/tests/apiBackendContracts.test.ts`
24. `apps/workspace-web/src/tests/operatorApi.test.ts` — NEW
25. `apps/workspace-web/src/tests/operatorMutationState.test.tsx` — NEW
26. `apps/workspace-web/src/tests/operatorActionsCore.test.tsx` — NEW
27. `apps/workspace-web/src/tests/operatorActionsLifecycle.test.tsx` — NEW

### Real-browser and static-smoke proof — 7 paths

28. `apps/workspace-web/playwright.config.ts` — NEW
29. `apps/workspace-web/e2e/operator-flow-helpers.ts` — NEW
30. `apps/workspace-web/e2e/operator-flow.spec.ts` — NEW
31. `scripts/testing/run_c3c_web_evidence.py` — NEW
32. `tests/integration/test_c3c_web_evidence_runner.py` — NEW
33. `docs/decisions/P2C_C3C_BUILD_EVIDENCE_RECEIPT.md` — NEW
34. `docs/cvf/CVF_CONTROL_MAPPING.md`

### Generated catalogs — 2 paths

35. `docs/catalog/MODULE_REGISTRY.json`
36. `docs/catalog/MODULE_CATALOG.md`

### Browser-proof regression splits — 2 paths

37. `apps/workspace-web/src/tests/operatorActionsReports.test.tsx` — NEW
38. `apps/workspace-web/e2e/operator-flow-accessibility.spec.ts` — NEW

A required path outside this list is `BLOCKED_WORK_ORDER_CEILING`. Stop before
editing it. Resume requires reviewed DESIGN→SPEC→WORK_ORDER amendment and a
renewed exact approval. If a listed path proves unnecessary, stop for exact-set
contraction; synthetic edits are forbidden.

## 3. Implementation contract

### 3.1 Real route coverage and typed contracts

The selected-shift console MUST expose real controls for all R18 actions:

- create a shift using the existing query-parameter `POST /shifts` contract,
  refresh the assigned shift list and select the created shift;
- append internal message; create event;
- create task intent and create task, retaining an intent id ephemerally when
  required but never rendering or persisting its payload digest;
- create and transition a shift-bound CustomerRequest;
- report and transition an incident;
- create a handover from the selected shift to a different selected target;
- generate, create successor version and submit a Report;
- close the selected shift with its current stored version.

Small feature-owned DTOs MUST mirror the actual Pydantic/browser response
shapes, including CustomerRequest version and Report version/status. No caller
field may invent actor, approval, digest, status, version or authority. The
single existing request primitive remains bearer-authenticated, sanitized and
no-retry. `operatorApi.ts` may consume an exported primitive; it MUST NOT fork
auth, error mapping, query encoding or retry logic.

Capability reads are advisory presentation input only. Every submit calls the
real backend, and direct 401/403/404/409/422 remains authoritative. Approval-
needed conflict text may name only a safe next action such as waiting for an
authorized approval and refreshing readiness; it MUST expose no digest,
receipt identity, credential or caller-declared approval field.

### 3.2 Mutation state and refresh semantics

- Each control permits at most one in-flight submit. Its submit button and
  relevant fields are disabled while pending.
- Successful mutation refreshes all affected canonical reads plus selected-
  shift capabilities. Controlled conflict also refreshes them before another
  attempt becomes available.
- `outcome_unknown` disables repeat until an explicit fresh read succeeds.
  It never automatically retries and never assumes success or failure.
- Cancellation remains distinct from ambiguous outcome. A stale response from
  an old shift selection cannot commit into the new selection.
- Mutation state is React memory only. No local/session persistent queue,
  service worker, background sync, interval/push subscription or realtime
  client is introduced.
- `apps/workspace-web/src/offline/queue.ts` remains byte-identical, unimported
  and empty at runtime; source and browser proof MUST check this boundary.

### 3.3 Operator/supervisor separation

C3c may render only actions permitted by the R18 operator surface. It MUST NOT
render staffing add/revoke, event confirm/correct, approval receipt, incident
acknowledge, handover review/acknowledge, Report approve/revoke or shift
freeze. Those remain C3d. Server-returned capabilities may hide or disable an
R18 control but never elevate authority.

Closing a shift or another operator action may legitimately return a governed
conflict because a later supervisor prerequisite is absent. That is a valid
real-route outcome only if the UI shows the bounded safe next action and does
not claim the mutation succeeded.

### 3.4 Accessibility and presentation

Every form control has a programmatic label; error/help text is associated by
`aria-describedby`; pending and result announcements use appropriate live
regions; all actions work by keyboard; focus moves to the bounded feedback on
failure. Empty, loading, offline, forbidden, not-found, conflict, invalid,
server and outcome-unknown states remain distinguishable without rendering raw
transport data. Layout MUST remain usable at narrow and desktop widths.

All TS/TSX files stay <=200 physical lines. `OperationsConsole.tsx` remains a
small coordinator; data loading/refresh and mutation UI are feature-owned.

### 3.5 Browser, database and evidence harness

Add the pinned Playwright test dependency and lockfile delta only; no runtime
browser library. The governed evidence runner MUST:

1. create an owned temporary directory and disposable SQLite database;
2. set a non-secret test JWT value without printing it, create schema through
   canonical SQLAlchemy metadata, and seed only the fixed dev operator needed
   for the run;
3. start the real FastAPI app and built Vite preview on runner-owned ports;
4. perform static HTTP smoke on the built entry and referenced assets;
5. run Playwright Chromium against those processes and real API routes;
6. prove the R18 route calls, mutation state, bounded conflict, keyboard/
   label behavior and absence of offline queue/storage/retry behavior;
7. terminate only owned child processes and remove only the owned temporary
   directory on success or failure.

The runner MUST redact secrets, credentials, database paths containing
userinfo/query/fragment and raw subprocess exceptions. Its integration test
must prove command construction, readiness timeout, failure propagation and
cleanup without launching a browser. Browser installation availability is a
G6 prerequisite; unavailable required Chromium is `BLOCKED_G6`, not a skip.

C3c changes no backend persistence or route implementation, so no fresh
PostgreSQL behavior claim or provider call is required or authorized. Full
Python regression protects the already-proven backend contract.

## 4. Protected boundary

Zero diff is mandatory for all backend/domain/ledger/database/migration code;
authentication/session storage semantics; staffing and supervisor features;
`apps/workspace-web/src/offline/queue.ts`; provider configuration; CI; `.cvf/**`;
roadmap/continuity and prior receipts. No tenant/data-scope, production
PostgreSQL, offline/realtime, supervisor, C3d, P2-C or Phase-2 claim is
authorized.

## 5. Pre-BUILD G6

From a separate clean pushed pre-BUILD continuity commit:

1. verify `HEAD == origin/main`, clean worktree and record the exact parent;
2. rehydrate manifest/policy/memory/state/handoff/DESIGN/SPEC/WO/review;
3. verify C3b1/C3b2 BUILD and closure commits are ancestors;
4. verify core/manifest/origin pin and doctor `PASS WITH NOTE 24/1` only;
5. run full Python and frozen frontend baseline, recording exact counts;
6. install/check the pinned Playwright Chromium prerequisite without changing
   tracked files, and record Node/pnpm/Playwright/browser versions;
7. pass session/catalog/file-size/repository/JSON/diff gates and verify no
   owned process/container/temp residue or secret output.

Any failure is `BLOCKED_G6`; no source edit or provider call.

## 6. Required order and evidence

1. typed contracts and operator API over the existing request primitive;
2. read/capability refresh coordinator with stale-response suppression;
3. bounded mutation hook/feedback and small action components;
4. isolated contract/state/accessibility/layout tests;
5. real FastAPI + SQLite + Vite + Chromium runner and browser flows;
6. full Python, frozen frontend, production build and static smoke;
7. AC-29 isolated exact-parent rehearsal, catalogs and repository gates;
8. truthful BUILD receipt with exact changed set, failures and repairs.

Minimum commands include:

```powershell
python -m pytest -q tests/integration/test_c3c_web_evidence_runner.py
python -m pytest -q
pnpm --dir apps/workspace-web install --frozen-lockfile
pnpm --dir apps/workspace-web run typecheck
pnpm --dir apps/workspace-web test -- --run
pnpm --dir apps/workspace-web run build
python scripts/testing/run_c3c_web_evidence.py --json
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
```

The worker return MUST report exact results, actual changed set, browser/static
smoke evidence and owned cleanup, zero staged files and:

`READY_FOR_INDEPENDENT_P2C_C3C_BUILD_REVIEW`

## 7. Stop conditions and claim boundary

STOP on parent/continuity drift; an outside or unnecessary ceiling path; hard-
limit overflow; a fake/unwired control; caller-declared authority; digest or
secret rendering; retry/queue/storage/realtime behavior; missing refresh after
success/conflict; repeat after outcome-unknown without fresh read; inaccessible
form state; mocked browser API; browser skip; incomplete cleanup; regression;
or pressure to combine C3c with C3d.

The worker MUST NOT stage, commit, push, self-review or FREEZE. Codex becomes
`COMMIT_STEWARD` only after independent BUILD `REVIEW_PASS`.

C3c may prove only the listed operator controls and their ephemeral browser
state against real FastAPI routes on disposable SQLite plus protected backend
regression. It does not prove supervisor controls, offline/realtime, tenant or
provider data scope, production PostgreSQL, C3d, P2-C or Phase-2 completion.
