# Work Order — P2-D Offline Queue and Realtime Sync

- Work Order id: `P2D-OFFLINE-REALTIME-WO-001`
- Tranche: `P2D-OFFLINE-REALTIME-2026-08-02`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `PROPOSED_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- Source parent: `1f3646aba7d2bc4becea6c156475360331133f29`
- INTAKE: `docs/decisions/INTAKE_2026-08-02_P2D_OFFLINE_REALTIME.md`
- DESIGN: `docs/decisions/ADR_2026-08-02_P2D_OFFLINE_REALTIME.md`
- SPEC: `docs/specs/P2D_OFFLINE_REALTIME_SPEC.md`

## 1. Authority and roles

An independent `AUTHORIZATION_REVIEWER` MUST compare current source, P2-C C4,
ADR/SPEC and this exact inventory. BUILD requires explicit `REVIEW_PASS`, a
committed/pushed authorization package, a separate pushed pre-BUILD continuity
checkpoint and fresh G6.

The later `IMPLEMENTATION_WORKER` edits only the exact BUILD paths below and
MUST NOT stage, commit, push, self-review or FREEZE. The worker may make the
single real provider call only through the dedicated evidence runner after all
ordered refusal/browser/durability gates pass.

## 2. Exact 49-path BUILD ceiling

Every listed path must change materially unless marked NEW. Any outside path,
unnecessary listed edit or path needed but absent is
`BLOCKED_WORK_ORDER_CEILING` and requires DESIGN/SPEC/WORK_ORDER amendment plus
independent review before BUILD continues.

### PWA shell and application integration — 9 paths

1. `apps/workspace-web/README.md`
2. `apps/workspace-web/public/manifest.webmanifest`
3. `apps/workspace-web/public/offline.html`
4. `apps/workspace-web/public/sw.js` — NEW
5. `apps/workspace-web/public/icons/app-icon.svg` — NEW
6. `apps/workspace-web/src/main.tsx`
7. `apps/workspace-web/src/app/App.tsx`
8. `apps/workspace-web/src/app/OperationsConsole.tsx`
9. `apps/workspace-web/src/app/styles.css`

### Session, queue, refresh and UI runtime — 12 paths

10. `apps/workspace-web/src/features/authentication/session.ts`
11. `apps/workspace-web/src/features/operator-actions/useMutationControl.ts`
12. `apps/workspace-web/src/features/operator-actions/MutationFeedback.tsx`
13. `apps/workspace-web/src/services/operatorApi.ts`
14. `apps/workspace-web/src/offline/queue.ts`
15. `apps/workspace-web/src/offline/types.ts` — NEW
16. `apps/workspace-web/src/offline/storage.ts` — NEW
17. `apps/workspace-web/src/offline/sync.ts` — NEW
18. `apps/workspace-web/src/offline/realtime.ts` — NEW
19. `apps/workspace-web/src/offline/refreshCoordinator.ts` — NEW
20. `apps/workspace-web/src/offline/refreshBridge.ts` — NEW
21. `apps/workspace-web/src/offline/ConnectivityRuntime.tsx` — NEW

### Queue/connection presentation — 3 paths

22. `apps/workspace-web/src/offline/OfflineQueuePanel.tsx` — NEW
23. `apps/workspace-web/src/features/connection-health/ConnectionStatus.tsx` — NEW
24. `apps/workspace-web/src/features/connection-health/README.md`

### Frontend unit/contract coverage — 8 paths

25. `apps/workspace-web/src/tests/App.test.tsx`
26. `apps/workspace-web/src/tests/operatorApi.test.ts`
27. `apps/workspace-web/src/tests/operatorMutationState.test.tsx`
28. `apps/workspace-web/src/tests/offlineQueue.test.ts` — NEW
29. `apps/workspace-web/src/tests/offlineSync.test.ts` — NEW
30. `apps/workspace-web/src/tests/realtimeSync.test.ts` — NEW
31. `apps/workspace-web/src/tests/pwaContract.test.ts` — NEW
32. `apps/workspace-web/src/tests/offlineMutationState.test.tsx` — NEW

### Real-browser proof and regressions — 4 paths

33. `apps/workspace-web/e2e/p2d-offline-realtime-helpers.ts` — NEW
34. `apps/workspace-web/e2e/p2d-offline-realtime.spec.ts` — NEW
35. `apps/workspace-web/e2e/operator-flow-accessibility.spec.ts`
36. `apps/workspace-web/e2e/supervisor-flow-accessibility.spec.ts`

### Evidence automation and receipts — 9 paths

37. `scripts/testing/run_c3c_web_evidence.py`
38. `tests/integration/test_c3c_web_evidence_runner.py`
39. `scripts/testing/run_p2d_web_evidence.py` — NEW
40. `tests/integration/test_p2d_web_evidence_runner.py` — NEW
41. `scripts/run_p2d_live_governance_evidence.py` — NEW
42. `scripts/_p2d_live_evidence_support.py` — NEW
43. `tests/unit/test_p2d_live_evidence_support.py` — NEW
44. `docs/decisions/P2D_BUILD_EVIDENCE_RECEIPT.md` — NEW
45. `docs/decisions/P2D_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md` — NEW

### Truth/catalog surfaces — 4 paths

46. `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`
47. `docs/cvf/CVF_CONTROL_MAPPING.md`
48. `docs/catalog/MODULE_REGISTRY.json`
49. `docs/catalog/MODULE_CATALOG.md`

## 3. Implementation contract

### 3.1 PWA/cache boundary

Implement SPEC R1-R2 exactly. `sw.js` handles navigation only, owns one
application-prefixed cache and never caches/intercepts API or non-navigation
traffic. The icon is repository-owned SVG; no generated binary or dependency
change. Offline copy cannot imply arbitrary persistence.

### 3.2 Principal and storage boundary

`ConnectivityRuntime` resolves `api.me()` before activating queue/polling,
stores only tab-scoped principal metadata through `session.ts`, and clears it
with the token. `types.ts`, `queue.ts` and `storage.ts` implement the exact
strict union/parser/namespace/50-item/24-hour rules, including schema version
`1`, five exact states, state-specific `lastErrorKind`, ephemeral bounded
malformed ids and metadata-only `actorUserId`. No raw JSON is rendered or sent.

### 3.3 Mutation wiring

Only the three `operatorApi` transition methods may call an offline
pre-dispatch helper. Offline success raises/returns a typed queued outcome that
`useMutationControl` maps to visible `queued`; it never fabricates a backend
record. Every other operator/supervisor method stays online-only. Existing
online conflict/stale/outcome-unknown behavior must remain byte-for-behavior.

### 3.4 Replay and refresh

`sync.ts` implements R10-R14 and calls typed request functions with recorded
CAS. Only pending dispatches. HTTP success becomes non-replayable
`applied_stale`; a failed confirming read never becomes `outcome_unknown` and
never redispatches. Blocked/ambiguous commands never return to pending or
rewrite CAS: after fresh read they require discard and a new live action. HTTP
5xx/server responses become visibly `blocked/server`, halt FIFO and never
auto-retry.
`refreshCoordinator.ts` serializes every callback per tab; `refreshBridge.ts`
registers the current composite OperationsConsole refresh without global event
payloads. Two-tab browser proof must show recorded CAS admits at most one
commit and visibly blocks the loser, without a cross-tab exactly-once claim.
OperationsConsole must be refactored, if needed, so it remains at or below 200
lines while preserving C3c/C3d stale-response and self-revoke clearing behavior.

### 3.5 Polling runtime

`realtime.ts` owns interval validation, visible/online listeners, immediate
recovery refresh, no-overlap and bounded backoff. `ConnectivityRuntime` owns
its lifecycle. ConnectionStatus/OfflineQueuePanel expose accessible SPEC R18
truth, including known-applied/stale, and never grant authority. Both existing
accessibility specs and the connection-health README must replace obsolete
zero-offline/service-worker assertions with the bounded P2-D contract.

## 4. Evidence contract

The P2-D web runner MUST reuse the C3d harness's command construction,
readiness timeout, sanitization, owned ports/processes and cleanup semantics,
selecting only the dedicated P2-D Playwright spec. Runner unit tests inject
commands/readiness/processes and make no browser/provider call.

The shared C3c runner and its test MUST parameterize the queue checkpoint:
C3c/C3d keep `queue prohibited`, while P2-D requires `bounded queue exercised
and cleaned`. No shared evidence surface may keep claiming that a passing
Playwright suite proves offline storage was never written.

The real-browser spec uses actual login/JWT/FastAPI routes and Chromium network
control. It proves SPEC R20 mechanically, including request counters and a
second authenticated actor plus a two-tab CAS race. Mocks remain limited to
Vitest structure/state tests and cannot satisfy governance claims.

The live-governance runner MUST create a real assigned transition scenario,
exercise anonymous/unassigned/stale-version/ambiguous refusal gates with
explicit provider count zero, verify the admitted transition plus exact actor-
bound audit through current persistence, then make exactly one real provider
call. Receipt output contains model, endpoint class, HTTP status, call count and
bounded evidence only; no key, bearer, raw request/response, DSN, userinfo,
query, fragment or raw exception.

## 5. Protected boundary

Zero diff is mandatory for:

- `apps/workspace-api/**`, `packages/**`, `database/**`, migrations/OpenAPI;
- root/package workspace dependency manifests and lockfile;
- auth/CVF policy/configuration and provider configuration;
- CI, Docker/deployment definitions and external/channel adapters;
- roadmap, implementation status, canonical/mirror continuity and C3d/P2-C
  receipts during BUILD. P2-D C4 truth sync is separate.

## 6. Fresh G6 before BUILD

From a clean pushed pre-BUILD checkpoint:

1. verify `HEAD == origin/main`, worktree clean, exact authorization ancestry;
2. rehydrate mandatory continuity plus this INTAKE/ADR/SPEC/WO/review;
3. verify P2-C C3d `e120a7f` and C4 `1f3646a` are ancestors;
4. record fresh full Python and frozen frontend baselines, not stale counts;
5. verify Node `22.14.0`, pnpm `9.15.0`, Playwright `1.62.1`, Chromium,
   Docker/PostgreSQL/provider prerequisites and zero owned residue;
6. pass JSON/session/catalog/file-size/repository/diff and doctor 24/1-only;
7. stop `BLOCKED_G6` before source edit/provider call on any failure.

## 7. Required evidence order

```powershell
pnpm install --frozen-lockfile
pnpm --filter workspace-web typecheck
pnpm --filter workspace-web test
pnpm --filter workspace-web build
python -m pytest -q tests/integration/test_p2d_web_evidence_runner.py tests/unit/test_p2d_live_evidence_support.py
python scripts/testing/run_p2d_web_evidence.py --json
python -m pytest -q
python scripts/run_postgres_live_roundtrip.py --json
python scripts/run_p2d_live_governance_evidence.py
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
```

Provider execution is last among behavior/evidence gates. AC-24 exact-parent
rehearsal must restore the recorded G6 baselines and remove its temporary
worktree. The worker reports exact counts, receipt paths, cleanup, exact changed
set, zero staged files and:

`READY_FOR_INDEPENDENT_P2D_BUILD_REVIEW`

## 8. Review, failure and closure

Independent review compares INTAKE/ADR/SPEC/WO, source, UI, tests, browser and
live receipts. `REVIEW_CHANGES_REQUIRED` is mandatory for any open AC, hidden
retry, unsupported queue type, actor leak, cache leak, overlapping refresh,
fake realtime/provider success, protected diff, incomplete cleanup or count/
claim drift.

This order authorizes no BUILD until review/package/pre-BUILD/G6 gates pass.
After independent BUILD review/push, only a separate C4 may mark P2-D
`CLOSED_BOUNDED`. Full-shift exit, Phase 2 closure and the post-Phase-2 sequence
remain blocked and require fresh authorization.
