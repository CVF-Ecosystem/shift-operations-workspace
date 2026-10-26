# P5-A2 G11 source-inspection UI worker return

Status: COMPLETE_PENDING_REVIEW
Self-declared worker-return artifact: yes
Date: 2026-10-26
Role: IMPLEMENTATION_WORKER
Risk: R2; live evidence required YES for AI governance claims
Installed Core: `../.Controlled-Vibe-Framework-CVF@aa672d11910ae1982557e4810a2a8002a611e9e6` (read-only)
Dispatch: `86d4ac461d93c2468530c990ad192e29d63ba91f`
Dedicated dispatch continuity: `74923de2fc0ca0ea603f68a032a8bc6c25367aa9`

## Product Milestone Binding

P5-A2's observable outcome remains integrated, authorized, scheduled signals,
forecasts, history, freshness, uncertainty, abstention and lineage, followed by
exact human run/version/source approval before durable recommendation or action.
This worker implemented only G11 manual self-window source caller and safe
rendering, with stale/session drills. The API's default coverage refusal is
truthful; fixture-backed READY is explicitly labeled `Dữ liệu thử nghiệm`.
Source acceptance awaits independent review. Phase 5 stays 0/5.

| Gap | Remaining truth, owner and roadmap destination |
|---|---|
| G01/A7 | One provider 401 spent; A7 BLOCKED. Root/operator, P5-A A7 then P5-A2. |
| G02 | Operational RAG/context/index/citations BLOCKED. Backend/Root, P5-A2 context. |
| G03 | Business and cohort fit open. Backend/operator, P5-A2 method. |
| G04 | Native fixture and PG source accepted; operational integration UNKNOWN. Backend/Root, P5-A2 source. |
| G05 | Production mode, authority, coverage, retention and positive SQLite UNKNOWN; known default refusal does not depend on positive coverage. Backend/Root/operator, P5-A2 coverage. |
| G06 | Native and bounded HTTP identity/fresh release accepted; later use-time access open. Backend/Root, P5-A2 approval. |
| G07 | Scheduler, claim and recovery open. Backend/Root, P5-A2 runtime. |
| G08 | Pure signals accepted; operational quality open. Backend/operator, P5-A2 signals. |
| G09 | Pure forecasts accepted; operational accuracy open. Backend/operator, P5-A2 forecasting. |
| G10 | Pure residual/drift accepted; monitoring and display open. Backend/UI/Root, P5-A2 quality and P5-B. |
| G11 | Bounded source route accepted; this source UI awaits review; other integrated flows open. UI/Root, P5-A2 application. |
| G12 | Exact human approval open. Backend/UI/operator, P5-A2 approval. |
| G13 | Native fixture failures accepted; this UI's stale/session drills await review; integrated drills open. Backend/Root, P5-A2 drills. |
| G14 | Live AI-governance proof HELD. Root/operator, separately admitted P5-A2 REVIEW. |

P5-B dashboard/search/observability remains backend/UI/Root; P5-C backup,
resilience, security and performance remains backend/Root/operator; P5-D
deployment, Shadow Mode and release remains Root/operator. Stop after independent
bounded G11 source UI acceptance and normal closure; return to operational
source/coverage DESIGN with effects separately admitted.

## Implementation and claim boundary

`OperationsConsole` mounts the panel immediately after `ShiftSelector`,
independent of selected shift. Inputs begin empty and require manual submission
of three strict UTC `datetime-local` values. No source call is made by mount,
shift selection, refresh, polling or the offline queue. The source-only GET
uses the current token and verified principal, exactly three UTC query keys,
`cache: no-store` and `AbortSignal`; the generic `api.ts` is unchanged.

The browser receives the authorized raw backend receipt. A flat registered
consumer validates exact fields, versions, domains, count equality, actor,
window and WebCrypto SHA-256 over the exact UTF-8 manifest, then returns only
counts/window or a fixed refusal reason. It does not parse deep manifest lineage.
No raw manifest, IDs, digest or arbitrary server detail enters React state,
DOM, logs, storage or queue. Missing crypto/invalid receipts have a fixed safe
unavailable message. All nine refusal reasons have fixed Vietnamese labels.
Session notification aborts and invalidates current reads on token/principal
change and clear; input edit, resubmit and unmount do likewise. A late 401
cannot clear a newer token/principal. No forecasting, report, approval,
durable recommendation or operational coverage is claimed.

No provider call, credential/`.env`/model/CSV change, Docker/database,
package install, browser session, deployment, production or public effect.
The real API may send raw authorized receipt fields to the browser; the privacy
claim begins at flat validation and safe projection, not at network receipt.

## Evidence and retained failures

- Exact cached Node `22.14.0`, process-local PATH; all commands from the
  project root. First inert `tsc -b --noEmit` had four type errors (one
  `URLSearchParams` interface mismatch, three absent Node builtin typings in
  browser tsconfig). All were repaired in scope. Its unlisted
  `tsconfig.tsbuildinfo` was removed. Subsequent inert typecheck passed.
- First focused CLI invocation used a duplicated config path with `--root`
  and failed before tests. The corrected five-module focused run: 16 passed,
  one timed out at 5 seconds because the test retyped identical inputs nine
  times. The test now enters the window once; targeted module: 3 passed.
- Full installed frontend suite: **26 files, 145 tests passed**. The five new
  modules contribute 17 tests; no skip or xfail. Two complete frozen READY
  contexts project to exact safe values, all nine frozen refusals render, and
  **54 READY plus 30 REFUSED** pre-frozen mutations are rejected by the actual
  TypeScript consumer. Native LF matrix hash is recomputed from raw matrix
  text in a test and compared with the real exported consumer pin.
- Explicit race tests cover ignored abort, resubmit, input edit, token change,
  termination, unmount abort and late 401. Tests cover current actor/window,
  missing/failing crypto, digest mismatch, boolean/fraction count rejection,
  safe error rendering, no mount source call and old-session protection.
- Typecheck `tsc -p apps/workspace-web/tsconfig.json --noEmit`: PASS.
  The attempted cached-path `npm.cmd` build launcher did not exist and did
  not start a build; the exact cached Node Vite CLI production build then
  passed (77 modules transformed, 1.47 seconds).
- `python scripts/check_invariant_families.py`: PASS;
  `python scripts/check_file_size.py`: PASS; `git diff --check`: PASS.
  Core inheritance preflight: zero violations. Root owns the normal full
  Python hook, catalog checks, commit and independent review.

The original failures above are retained as observations, not current gates.

## Exact worker manifest

SHA-256 is over actual file bytes; line counts are current text lines. Worker
changed only these 14 authorized UI paths and this return. Root owns the
matrix, three old pins, catalog, review and continuity changes.

| Path | Lines | SHA-256 |
|---|---:|---|
| `apps/workspace-web/src/types/proactiveSource.ts` | 28 | `b7a971ce66ffe4d772e6e714a53e51d9b72fbad6d91e7a8fade4d428567ae0e4` |
| `apps/workspace-web/src/features/proactive-source/sourceReceipt.ts` | 73 | `33f3fb4b473c5e68e626a8fa8ee8907e37924b10931e9da0b67eb7523341ca1b` |
| `apps/workspace-web/src/services/proactiveSourceApi.ts` | 43 | `95bcf9415bfa21cd138fba66121271f0562282cfc6b33d28fac5620526b6301b` |
| `apps/workspace-web/src/features/proactive-source/useProactiveSourceRead.ts` | 101 | `f75e89366181bb7504d787c4d7e1134ab3db89ce23ea0e1fac73c0f3367258c6` |
| `apps/workspace-web/src/features/proactive-source/ProactiveSourcePanel.tsx` | 45 | `3e9f5b0c2e809b7a7a89ad3c2c1a2134f8399b2446dbda52cbed053ae75e35be` |
| `apps/workspace-web/src/app/OperationsConsole.tsx` | 187 | `3542ca5b0c31ba5ae446871520cfff75ff17dc09b696f650cf15a2e7bea48c2e` |
| `apps/workspace-web/src/features/authentication/session.ts` | 46 | `9467dcf8c2ed51fcda0c9fb1a55839800ab84c43c5a2c2b51ae0a15a1c6fd4dc` |
| `apps/workspace-web/src/app/styles.css` | 98 | `9bc2ea0e76191001d0009300524cec3fa076b3675fd461aa476b7d372b815683` |
| `apps/workspace-web/src/tests/proactiveSourceTestData.ts` | 28 | `bda6b7e823286de332033a4554703112ccc8e1842728fba44b7ef3671f188e6e` |
| `apps/workspace-web/src/tests/proactiveSourceReceipt.test.ts` | 64 | `d02e33d049aba23ea0e67a11706cb1db5c8857f50f060aff2c48d0645eadfb71` |
| `apps/workspace-web/src/tests/proactiveSourceApi.test.ts` | 60 | `bd5dc03b699e7dbb81e19b21c03a6689cbef8fcb566a0ab4fb24b83f5b48667e` |
| `apps/workspace-web/src/tests/proactiveSourcePanel.test.tsx` | 73 | `21f334a7c1f9e2f5ac598736b27b9406632706b4658531c14da438256e87c5d8` |
| `apps/workspace-web/src/tests/proactiveSourceRaces.test.tsx` | 81 | `57353ad5d1177701b57c355b1c2590f04906a930a39c1a8722c37afb0919030f` |
| `apps/workspace-web/src/tests/proactiveSourceConsole.test.tsx` | 29 | `ad57c7fd670fd728c518dafa2440a70d352a612e5f31fb73f5d762c25eb358bb` |

Manifest delta: NONE outside the authorized 14 source/test paths and this
worker-return artifact. Maximum TS/TSX executable is 187 lines, below 200.

## Agent Operation Trace Block

| Field | Evidence |
|---|---|
| Actor | IMPLEMENTATION_WORKER |
| Provider or surface | local project files and installed cached Node |
| Session or invocation | P5A2-SOURCE-UI-20261026 BUILD |
| Working directory | shift-operations-workspace project root |
| Command or tool surface | exact file edits, focused/full Vitest, TypeScript, Vite, read-only native guards |
| Target paths | exact 14 worker paths and this return |
| Allowed scope source | admitted P5A2_SOURCE_UI_WORK_ORDER.md and independent authorization; clean dispatch split range and independent family materialization |
| Before status evidence | no source UI or source request on mount; current matrix old pin until binding |
| After status evidence | bounded source UI and tests built, independent source acceptance pending |
| Diff evidence | exact 14-row manifest above; Root changes separately owned |
| Approval boundary | no external effects or durable action |
| Claim boundary | safe transient UI only; no operational readiness, provider governance or milestone closure |
| Agent type | implementation worker |
| Invocation ID | P5A2-SOURCE-UI-20261026 |
| Expected manifest | 14 worker paths plus return |
| Actual changed set | 14 worker paths plus return |
| Manifest delta | NONE |

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: NO

The verified pinned Core `check_recheck` is invoked standalone for this
self-declared worker return. The ordinary CLI/hook does not scan this legacy
`docs/decisions/` return path; no automatic coverage is claimed. Independent
review and Root normal gates remain before material commit or closure.
