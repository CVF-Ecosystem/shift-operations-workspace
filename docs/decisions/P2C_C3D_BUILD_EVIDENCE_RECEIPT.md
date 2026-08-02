# Build Evidence Receipt — P2-C C3d Supervisor Closeout

- ID: `P2C-C3D-SUPERVISOR-CLOSEOUT-WO-001`
- Checkpoint: `C3d`
- Risk: `R2`
- BUILD parent: `6429f59c0e579b9199b563bc4a2ae287e32b2909`
- Status: `INDEPENDENT_REVIEW_PASS — READY_FOR_COMMIT_STEWARD`

## 1. Implementation disposition

The worker implemented the authorized supervisor closeout surface within the
Work Order's exact 36-path ceiling. The result connects the existing backend
staffing, event confirmation/correction, approval, incident, handover, Report
and freeze routes to a feature-owned supervisor UI. Backend authorization and
precondition checks remain authoritative; capabilities are advisory only.

Codex took over an incomplete worker tree after implementation and most local
tests existed. The takeover retained that work, repaired the real-browser
flow and coordinator refresh defects inside the same authorized paths, and
completed all remaining evidence. No provider-named worker CLI/MCP was used.

Repairs made during takeover included refreshing staffing and ordinary shift
reads after shift creation, using exact/scoped browser locators, arranging a
distinct real Report approval receipt for report approval, using a distinct
assigned receiving supervisor for cross-shift acknowledgement, reloading
after direct API arrangement, and asserting the backend's enumeration-safe
wrong-destination refusal and actual successor lifecycle.

## 1a. Independent review findings and bounded repair

The first independent BUILD review returned `REVIEW_FAIL` with four HIGH
findings. All were repaired without waiver and without expanding the exact
36-path ceiling:

1. `C3D-BUILD-REV-F1 STAFFING_HISTORY_STALE_RESPONSE`: assignment-history
   reads now use a monotonically increasing request token plus the current
   target-shift ref. Neither a late success nor a late failure for an
   abandoned shift can commit. A behavioral test holds shift A's Promise,
   switches to shift B, commits B, then resolves A and proves A never appears.
2. `C3D-BUILD-REV-F2 FIVE_PAIR_BROWSER_PROOF_INCOMPLETE`: real Chromium now
   submits all five exact three-field approval payloads through
   `ApprovalActions`: `event.confirm`, `event.correct`, `task.create`,
   `incident.acknowledge` and `report.approve`. Every target is a real stored
   backend record/intent and the Report is genuinely current `IN_REVIEW`.
3. `C3D-BUILD-REV-F3 BROWSER_REFUSAL_SUCCESS_PROOF_VACUOUS`: the stale test
   now loads version 1 into the UI, mutates the record externally, then sends
   that stale UI precondition and observes HTTP 409. Separate browser cases
   prove R2 incident acknowledgement without a receipt is refused and a
   correction succeeds through the UI only after a real R2 event, distinct
   approval receipts, acknowledged handover, approved Report and frozen Shift
   have been arranged through the real API.
4. `C3D-BUILD-REV-F4 PROVIDER_BODY_RETENTION`: provider body and exception
   text never leave `call_provider`. Returned/rendered evidence contains only
   outcome, reachability, HTTP status, expected-token-match boolean, bounded
   failure category and timestamp. The retained live receipt was sanitized
   in place from the already-observed result; **no second provider call** was
   made. Non-live injected-transport tests prove success bodies, HTTP error
   bodies and transport exception text are absent from returned summaries and
   receipts. Independent re-review found two residual exception surfaces;
   model-selection failures now emit only a fixed category, while malformed
   endpoint parsing is inside the same bounded transport-failure handler.
   Sentinel-bearing tests prove neither exception value can reach output.

This repair is returned for independent re-review; the repair worker does not
self-close any finding.

## 2. Exact changed set and protected boundary

- Exact Work Order set: **36/36 paths present**.
- Missing authorized paths: **0**.
- Outside paths: **0**.
- Staged paths: **0**.
- Backend/domain/ledger/database/migrations/OpenAPI: **zero diff**.
- Offline queue, package/lock versions, provider configuration, CI, `.cvf/**`,
  continuity, implementation status, roadmap, C3c receipts, P2-D and
  full-shift-exit artifacts: **zero diff**.
- Protected `scripts/run_postgres_live_roundtrip.py`: **byte-identical**.

## 3. Frontend and browser evidence

The final candidate was run with the pinned local toolchain: Node `22.14.0`,
pnpm `9.15.0`, Playwright `1.62.1` and installed Chromium.

- Frozen frontend install: **PASS**.
- Typecheck: **PASS**.
- Component/contract tests: **92 passed**.
- Production build: **PASS**.
- C3d runner integration tests: **21 passed**.
- `python scripts/testing/run_c3d_web_evidence.py --json`: **PASS** against
  real FastAPI plus Chromium, including built root/static assets, complete
  operator+supervisor suite, and `offline_queue_clean: true`.
- File-size guard: **PASS**; every touched TS/TSX file is at most 200 physical
  lines.

The browser run uses real project routes and disposable SQLite arrangement;
it is not governance evidence for the provider call or PostgreSQL. A stale
FastAPI/Vite process tree left by the interrupted worker was identified by
exact workspace command line and port ownership, terminated, and not counted
as evidence.

One final browser invocation launched from a shell that did not carry the
pinned Node directory timed out waiting for Vite and was recorded as a failed
attempt, not a pass. It left no owned process or port residue. The evidence
above is the subsequent complete rerun with the Node `22.14.0` directory
explicitly prepended to that shell's PATH.

## 4. Backend and PostgreSQL regression evidence

- Full Python suite after catalog regeneration: **1351 passed, 127 skipped**.
- Disposable PostgreSQL 16 roundtrip: **PASS**.
- First migration application: **29 applied, 0 skipped**.
- Idempotent reapplication: **25 applied, 4 skipped**.
- Pinned live backend matrix: **117 passed**.
- Owned container absent after run and anonymous-volume residue: **0**.

One earlier full-Python attempt found only generated catalog drift after the
final source LOC changed. It reported 1347 passes plus that single drift
failure. The catalog was regenerated through the authorized generator, and
the fresh full-suite result above passed without waiver.

## 5. Live governance evidence

The dry run first proved the complete refusal/durability chain without a
provider call. The live runner was then invoked exactly once:

- Seven real HTTP refusal cases: **PASS**, with statuses
  `403, 403, 409, 409, 404, 409, 422` and **0 provider calls**.
- Genuine staffing-assigned closeout reached durable `FROZEN` state with all
  required actor-bound audits: **PASS**.
- Real provider: Alibaba DashScope, model `qwen3.7-max`.
- Provider response: HTTP **200**, expected bounded sentinel returned.
- Provider-call count for the invocation: **exactly 1**.
- Sanitized receipt:
  `docs/decisions/P2C_C3D_LIVE_GOVERNANCE_EVIDENCE_RECEIPT.md`.

No second live provider invocation is required or authorized for final local
regression gates.

## 6. AC-29 exact-parent rehearsal

A detached temporary worktree at exact BUILD parent
`6429f59c0e579b9199b563bc4a2ae287e32b2909` passed:

- Python baseline: **1326 passed, 128 skipped**.
- Frozen frontend install: **PASS**.
- Frontend baseline: **58 passed**.
- Frontend typecheck and production build: **PASS**.
- Repository validation: **PASS**.

The temporary worktree registration was removed. Windows initially retained
part of its pnpm directory; the exact owned `%TEMP%` target was revalidated
and removed with a path-safe fallback. Final checks showed the path absent,
only the primary worktree registered, primary HEAD unchanged and zero staged
files.

## 7. Cleanup and claim boundary

The worker owns no remaining disposable PostgreSQL container/volume, backend
or Vite process, temporary rehearsal worktree, `dist`, `test-results`, or
TypeScript build-info artifact. No secret, Authorization header, JWT, raw
provider body, URL query/fragment or credential digest is recorded in either
receipt.

This BUILD does not claim independent review, commit, push, C3d FREEZE, P2-C
completion, P2-D completion, full-shift exit, or Phase 2 completion. C4 truth
sync remains the later bounded move after reviewed C3d closure. The worker did
not stage, commit, push, self-review or FREEZE.

`READY_FOR_INDEPENDENT_P2C_C3D_BUILD_REVIEW`
