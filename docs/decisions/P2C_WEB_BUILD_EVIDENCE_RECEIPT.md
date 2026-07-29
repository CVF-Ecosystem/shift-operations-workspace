# P2C Operations Console — C3b Build Evidence Receipt

- Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Control-chain checkpoint: `BUILD — C3b` (repair round 1)
- Worker role: `IMPLEMENTATION_WORKER`, then `REPAIR_WORKER` (Claude)
- Authority: Work Order §4 (28-path C3b ceiling), G7 continuity commit
  `3595fe22be70ba4432a55325ebc74e9ad9b471bd`
- This receipt is evidence input only. It does not self-declare
  `REVIEW_PASS` or approve its own commit; Codex remains the independent
  REVIEWER and sole COMMIT_STEWARD.

## Repair round 1 — findings and disposition

Independent review returned two findings against the initial C3b build.
Both are repaired below, within the same 28-path ceiling and with zero new
paths.

### P2C-C3B-REV-F1 — CONNECTION_SESSION_INDICATOR_MISSING

**Repaired.** `apps/workspace-web/src/app/OperationsConsole.tsx` now derives
a `ConnectionState` (`connecting` | `offline` | `error` | `connected`) from
the existing `shiftsLoading`/`detailLoading` and `shiftsError`/`detailError`
signals — no new network calls or state. The header renders it as
`<span role="status" aria-live="polite" className="connection-indicator connection-indicator--...">`
with the visible text `Session: signed in · <state label>` (`Connecting…`,
`Offline`, `Connection issue`, `Connected`). `apps/workspace-web/src/app/styles.css`
adds `.connection-indicator*` rules (a colored status dot plus text color per
state); no line-limited TS/TSX/JS/JSX file is affected by the CSS change.
The indicator only ever renders inside the already-authenticated
`OperationsConsole`, so "Session: signed in" is truthful by construction —
it carries no per-shift authorization, data_scope, or production-connectivity
claim, and no token/user identifier is interpolated into it. Verified by three
new/extended assertions in `App.test.tsx`: connecting → connected transition,
network-failure → offline indicator, and 5xx → "Connection issue" indicator.

### P2C-C3B-REV-F2 — REQUIRED_COMPONENT_EVIDENCE_INCOMPLETE

**Repaired.** All seven named gaps now have dedicated coverage in
`apps/workspace-web/src/tests/App.test.tsx` (no new test path was created;
`api.test.ts` was reviewed and needed no change — its 8 tests already cover
the unit-level HTTP/session contract this finding did not name):

- rapid shift switching / stale-response suppression — `'suppresses a stale
  response when switching shifts before the first request resolves'`: shift
  `s1`'s `/events` and `/shifts/s1/open-work` responses are held open via
  controlled deferred `Promise`s, the user switches to `s2` and its event
  renders, then the stale `s1` responses are resolved and asserted **not**
  to overwrite the now-current `s2` view;
- login pending state — `'shows a pending state while the login request is
  in flight'`: the login `fetch` is held open, the submit button is asserted
  `disabled` with the label `Signing in…`, then resolved;
- operational loading state — `'shows an operational loading state while
  shift detail is in flight'`: the same deferred-response technique proves
  multiple `Loading…` regions render while `/events` and `/open-work` are
  outstanding, and none remain once both resolve;
- controlled server-error UI state — parametrized (`it.each`) alongside the
  existing network-offline case, asserting a `role="alert"` region and the
  `Connection issue` indicator on a `500` response;
- grouped Task/CustomerRequest/Incident open work — `'renders grouped open
  work, incident summary and handover summary for one shift'` supplies one
  realistic `Task`, `CustomerRequest` and `Incident` DTO via the open-work
  response and asserts all three render inside the `Open work` region;
- incident summary — the same test asserts the `Incident summary` region
  renders `ACKNOWLEDGED: 1` and `R3: 1` from one incident DTO;
- handover summary — the same test asserts the `Handover summary` region
  renders `REVIEWED` from one handover DTO.

All new fixtures use realistic C3a response shapes (exact field names/enum
values from `operations_domain.models`, matching `apps/workspace-web/src/types/operations.ts`).
Test doubles remain `vi.stubGlobal('fetch', ...)` UI/state fixtures only; no
test claims backend JWT verification or any other CVF governance behavior —
that proof remains C3a's.

**Repair defect found and fixed during verification:** the first version of
the loading-state fixture mapped both `/events?shift_id=s1` and
`/incidents?shift_id=s1` to the same `deferShiftId` branch (both URLs contain
the substring `shift_id=s1`), so only one of the two deferred requests was
ever resolvable and the test hung on a permanent `Loading…` state. Narrowed
the match to `/events?shift_id=${defer}` specifically; all 22 tests pass
afterward, including the corrected loading-state assertion.

`apps/workspace-web/src/tests/App.test.tsx` required a full rewrite to add
seven scenarios inside the 200-line ceiling: `describe`-level `fetchMock`
hoisting, single-line DTO factory helpers (`shift`, `event`, `task`,
`customerRequest`, `incident`, `handover`), an overridable `mockReads`
fixture router, and a shared `signInWithSession` helper collapsed three
previously separate tests (session-restore, logout, and their individual
`fetchMock` boilerplate) into fewer, denser tests without losing any
assertion. Final size is exactly 200 lines — at the ceiling, not over it;
no debt-baseline or size-exception entry was used.

## Baseline

- Starting commit: `HEAD == origin/main == 3595fe22be70ba4432a55325ebc74e9ad9b471bd`
  (governance: authorize P2C C3b after C3a review pass).
- Predecessor C3a build commit: `fe2f31236bec1e1e3bcaddbe15463633b0696ab3`
  (independently `REVIEW_PASS`, pushed).
- Worktree clean, zero staged, before the first C3b edit.

## Environment gates (G6)

- Docker responded: Docker Desktop 4.83.0, Engine 29.6.2 (client/server both
  confirmed via `docker version`).
- `node:22.14.0-alpine3.21` resolved exactly; digest
  `sha256:9bef0ef1e268f60627da9ba7d7605e8831d5b56ad07487d24d1aa386336d1944`.
- Host Node was originally `v22.17.0` (non-compliant with the exact pin).
  `nvm-windows` (`CoreyButler.NVMforWindows` 1.2.2) was installed via
  `winget` and used to install Node `22.14.0` alongside the existing
  install. `nvm use` required interactive elevation that could not complete
  non-interactively, so the pinned `22.14.0` binaries were activated for
  every command in this build by prepending their versioned install
  directory directly to `PATH`, bypassing the `nvm` symlink. `node --version`
  reported exactly `v22.14.0` and `pnpm --version` reported exactly `9.15.0`
  (activated via `corepack prepare pnpm@9.15.0 --activate`) for every command
  below.
- CVF core clean and pinned exactly at
  `27137db4d9aa2aea931ddd2507185d5c24943080` (verified against
  `.cvf/manifest.json`'s `cvfCoreCommit`).
- Repository gates (pre-BUILD): `python -m pytest -q` → `678 passed, 65
  skipped`; `validate_repository.py` PASS; `generate_catalog.py --check`
  PASS; `check_session_state.py` PASS; `check_file_size.py` PASS.

## Changed-set ceiling audit

Exactly **27 paths** changed against the 28-path ceiling in Work Order §4;
the one untouched ceiling path is this receipt itself, now created as the
28th.

**Toolchain/CI/docs (9/9 touched):**
`package.json`, `pnpm-lock.yaml` (new), `apps/workspace-web/package.json`,
`apps/workspace-web/tsconfig.json`, `apps/workspace-web/vitest.config.ts`
(new), `infrastructure/docker/Dockerfile.web`, `.github/workflows/ci.yml`,
`apps/workspace-web/README.md`, `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`.

**Console implementation (15/15 touched):**
`apps/workspace-web/src/app/App.tsx`, `.../app/styles.css`,
`.../app/OperationsConsole.tsx` (new), `.../services/api.ts`,
`.../types/operations.ts` (new), `.../components/AsyncState.tsx` (new),
`.../features/authentication/session.ts` (new), `.../authentication/LoginView.tsx`
(new), `.../shift-selection/ShiftSelector.tsx` (new),
`.../shift-timeline/ShiftTimeline.tsx` (new), `.../open-work/OpenWorkPanel.tsx`
(new), `.../incident-room/IncidentSummary.tsx` (new),
`.../shift-handover/HandoverSummary.tsx` (new), `.../tests/setup.ts` (new),
`.../tests/App.test.tsx` (new).

**API test/catalog/receipt (4/4 touched, this file completes the set):**
`apps/workspace-web/src/tests/api.test.ts` (new),
`docs/catalog/MODULE_REGISTRY.json`, `docs/catalog/MODULE_CATALOG.md`,
`docs/decisions/P2C_WEB_BUILD_EVIDENCE_RECEIPT.md` (this file).

No path outside this 28-path list was created, modified, or deleted.
`apps/workspace-web/src/offline/queue.ts` was not touched. No backend
(`apps/workspace-api/**`), auth, `.cvf/**`, `SESSION/**`, or roadmap path was
touched.

## Commands run and results

Initial build (superseded numbers, kept for history): `pnpm install`
generated the lockfile (184 packages); frozen reinstall PASS; typecheck PASS
after adding `vite/client` to `tsconfig.json` `types`; test PASS with 18
tests; build PASS; Docker image `workspace-web-c3b:build-verify` PASS with a
200 OK smoke test and full cleanup; Python regression PASS at 678/65 after
one catalog regeneration; all repository gates PASS.

**Repair round 1 (current):**

| Command | Result |
|---|---|
| `pnpm install --frozen-lockfile` | PASS — lockfile up to date, resolution skipped, 184 packages reused |
| `pnpm --filter workspace-web typecheck` (`tsc -b --noEmit`) | PASS |
| `pnpm --filter workspace-web test` (Vitest + jsdom) | First run: **21/22 passed, 1 failed** (`shows an operational loading state...` — `queryByText` threw on multiple matches). Fixed to `queryAllByText`, which then exposed a real fixture defect (see repair notes above: `/events` and `/incidents` shared a `shift_id=s1` substring match). Fixed the fixture's URL matching. Final run: PASS — 2 files, **22 tests passed**, 0 failed |
| `pnpm --filter workspace-web build` (`tsc -b && vite build`) | PASS — `dist/index.html`, `dist/assets/*.css` (2.08 kB), `dist/assets/*.js` (153.61 kB); build artifact deleted after verification |
| `docker build -f infrastructure/docker/Dockerfile.web -t workspace-web-c3b:repair-verify .` | PASS — multi-stage build completed inside `node:22.14.0-alpine3.21` |
| Container smoke test (`docker run` + `curl`) | PASS — `GET /` returned HTTP 200 |
| `docker rm -f` / `docker rmi` cleanup | PASS — container and image removed; `docker ps -a` / `docker images` show no residue |
| `python -m pytest -q` (pre-catalog-regen) | FAIL — 1 catalog-drift test failed on stale `workspace-web` LOC (expected: real new source from the repair) |
| `python scripts/generate_catalog.py --write` | Regenerated `docs/catalog/MODULE_REGISTRY.json` and `docs/catalog/MODULE_CATALOG.md` (7956 total LOC, up from 7892) |
| `python -m pytest -q` (post-catalog-regen) | PASS — `678 passed, 65 skipped` (matches pre-repair and original baseline exactly; no regression) |
| `python scripts/testing/validate_repository.py` | PASS |
| `python scripts/generate_catalog.py --check` | PASS — 20 modules, all paths exist, metrics/Markdown up to date |
| `python scripts/check_session_state.py` | PASS |
| `python scripts/check_file_size.py` | PASS |
| `git diff --check` | PASS (0 whitespace errors; only line-ending autocrlf notices) |
| JSON parse check on `docs/catalog/MODULE_REGISTRY.json` | PASS |

## Test evidence detail

22 tests across two files, all passing:

- `src/tests/api.test.ts` (8 tests, unchanged by this repair): bearer header
  injected only when a token exists; HTTP 401 maps to `unauthorized`; HTTP
  403/404/409/422/5xx map to distinct controlled kinds; a network failure
  maps to `network` without leaking the raw `TypeError`; a raw
  transport-like object is never rendered as the error message; only the
  sanitized `detail` field is surfaced from a 4xx body; `login()` stores no
  token on failure and returns the token response on success;
  `AbortSignal`-based cancellation is supported and mapped to a `cancelled`
  kind.
- `src/tests/App.test.tsx` (14 tests, 4 net new plus 3 extended for the
  connection indicator): login form renders when no session exists; the
  login button shows a disabled `Signing in…` pending state during an
  in-flight request; a failed login shows a generic message and never
  echoes the submitted password into the DOM; a successful login stores the
  token only in `sessionStorage` and confirms zero `localStorage` keys;
  session restore on mount and logout (clearing token/state, returning to
  login) are proven together; an HTTP 401 on any operational read clears the
  session and returns to login; the connection indicator shows `Connecting…`
  then `Connected`; a parametrized case proves both a network failure
  (`Offline` indicator) and a 5xx read (`Connection issue` indicator) each
  render a `role="alert"` region and the matching indicator text; an
  operational loading state shows `Loading…` in multiple regions while
  shift detail is in flight and clears once resolved; the empty-timeline
  state renders, then only `CONFIRMED`-state events render as timeline facts
  once populated (a `PROPOSED` event in the same response is excluded);
  grouped `Task`/`CustomerRequest`/`Incident` open work, the incident
  severity/status summary, and the handover lifecycle summary all render
  from one combined shift-detail fixture; a stale response from an earlier
  shift selection cannot overwrite a later shift's rendered state; every
  rendered button in the authenticated console is scanned for mutation-verb
  text (create/confirm/approve/transition/close/freeze/acknowledge/review)
  and none is found.

Test doubles are `vi.stubGlobal('fetch', ...)` fixtures exercising this
frontend's own UI/state logic only. No claim is made here that JWT
verification, permission checks, or any other backend governance behavior
is proven by these tests — that proof belongs to C3a's real API/JWT/
PostgreSQL/provider evidence (`P2C_READ_API_BUILD_EVIDENCE_RECEIPT.md`,
`P2C_READ_LIVE_EVIDENCE_RECEIPT.md`), which this receipt does not repeat or
supersede.

## Secret / browser-storage negative scan

- `grep` for `localStorage` across `apps/workspace-web/src` (excluding the
  pre-existing, untouched `offline/queue.ts` and the negative-proof test
  assertions in `App.test.tsx`) returned zero matches in production code.
- `grep` for `Authorization` returned exactly one production site
  (`src/services/api.ts`, the bearer-header injection) and its
  corresponding test assertion using a placeholder value
  (`secret-token-value`), not a real credential.
- `grep` for JWT-shaped literals (`eyJ...`) across
  `apps/workspace-web/src` returned zero matches.
- No password, API key, or raw `Authorization` header value is printed,
  logged, or committed by this receipt or by any file in the changed set.

## File line counts (TS/TSX/JS/JSX, 200-line ceiling)

Largest first, all within the 200-line limit:
`App.test.tsx` **200** (at the ceiling, not over — rewritten during repair
to add 7 required scenarios without exceeding the limit; see repair notes),
`OperationsConsole.tsx` 164 (was 142; +22 for the connection-indicator
derivation and markup), `operations.ts` (types) 141, `api.ts` 102,
`api.test.ts` 101 (unchanged), `LoginView.tsx` 71, `IncidentSummary.tsx` 53,
`OpenWorkPanel.tsx` 51, `AsyncState.tsx` 49, `ShiftTimeline.tsx` 37,
`ShiftSelector.tsx` 35, `HandoverSummary.tsx` 28, `session.ts` 17,
`App.tsx` 14, `vitest.config.ts` 12, `setup.ts` 8. No debt-baseline or
size-exception entry was added; no file required a split or an out-of-ceiling
amendment. `styles.css` (not line-limited; CSS is outside the TS/TSX/JS/JSX
guard) grew from 35 to 43 lines for the indicator's status-dot styling.

## Generated-artifact / Docker cleanup audit

- `apps/workspace-web/dist/` deleted after both the initial and repair-round
  local `pnpm build` verifications.
- `apps/workspace-web/tsconfig.tsbuildinfo` (TypeScript incremental-build
  cache, generated by `tsc -b`) deleted after both rounds; it is not an
  authorized path.
- `node_modules/` (root and `apps/workspace-web/`) confirmed gitignored via
  `git check-ignore -v`; present on disk for local verification only, not
  tracked or staged.
- Docker: both the original `workspace-web-c3b:build-verify` image/container
  and the repair-round `workspace-web-c3b:repair-verify` image/container
  were removed (`docker rm -f`, `docker rmi`); `docker ps -a` and
  `docker images` show no residue tied to this build at any point. No named
  volume was created by this build.

## Exact 28-path ceiling audit (repair round)

`git status --porcelain=v1` after the repair enumerates exactly **28**
changed paths, identical to the original 28-path set — the repair touched
only three already-authorized files
(`apps/workspace-web/src/app/OperationsConsole.tsx`,
`apps/workspace-web/src/app/styles.css`,
`apps/workspace-web/src/tests/App.test.tsx`) plus the catalog regeneration
(`docs/catalog/MODULE_REGISTRY.json`, `docs/catalog/MODULE_CATALOG.md`) and
this receipt; no new path was created or touched outside the ceiling.
`apps/workspace-web/src/tests/api.test.ts` was reviewed per the finding's
authorization but required no change.

## Zero staged confirmation

`git status --porcelain=v1` at the time of writing this receipt shows only
working-tree modifications and untracked new files within the 28-path
ceiling. The staged area is empty — no `git add` was run by this worker at
any point during C3b or this repair round.

## Claim boundary and limitations

- This is a **read-only** authenticated console. It implements no create,
  confirm, transition, approve, correct, review, acknowledge, close, or
  freeze control, and does not activate the offline queue, realtime
  transport, reporting, or AI/RAG/memory/forecasting behavior.
- This receipt does not claim production hosting, browser-matrix
  completeness, per-shift/tenant authorization, PWA/offline/realtime
  support, mutation support, or Phase 2 roadmap completion.
- This receipt does not claim, repeat, or extend the C3a live-governance
  (real JWT/PostgreSQL/provider) evidence; it only proves this frontend's
  own build/test/typecheck/container correctness and its adherence to the
  28-path ceiling and the sessionStorage/error-mapping/confirmed-only-
  timeline/mutation-absence requirements above.
- The exact-pinned Node `22.14.0` was not the host's pre-existing default
  (`22.17.0`); it was installed and activated for this build session via
  `nvm-windows` and a direct `PATH` prepend rather than `nvm use`'s normal
  symlink activation, because the latter required interactive elevation
  unavailable in this non-interactive environment. The Docker image build
  independently used the exact `node:22.14.0-alpine3.21` tag inside the
  container, which does not depend on the host activation method.
- No provider call, no secret read, no backend/auth/permission/data-scope
  change, and no CVF core change occurred during this checkpoint.

## Unresolved findings

`P2C-C3B-REV-F1` and `P2C-C3B-REV-F2` are both repaired with evidence above
(F1: visible accessible connection/session indicator added and covered by
3 tests; F2: all 7 named component/behavior gaps now have dedicated test
coverage, 22/22 tests passing). No new finding was self-identified by this
worker during the repair. Independent re-review may still find additional
issues; this receipt does not foreclose that review, and does not declare
`REVIEW_PASS` on its own authority.

## Required stop state

`READY_FOR_INDEPENDENT_P2C_WEB_BUILD_RE_REVIEW`. This worker did not stage,
commit, push, self-approve, declare FREEZE, or begin C4.
