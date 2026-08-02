# Phase 2 full-shift exit — BUILD evidence receipt

- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Work Order: `P2-FULL-SHIFT-EXIT-WO-001`
- BUILD parent: `3b0a14204069e32dbb50b695c9306910c2266282`
- Risk: `R2`
- Status: `FINAL_REVIEW_PASS_READY_FOR_BUILD_COMMIT`

## Bounded changed set

The candidate changes exactly the 15 paths authorized by the Work Order: 11
new evidence/test/receipt paths and four existing runner/truth surfaces.
Product source, API/OpenAPI, domain/ledger, database/migrations, dependencies,
lockfile, auth/CVF policy, provider configuration, CI/deployment, roadmap,
status and continuity remain zero-diff. No file is staged.

## Historical evidence completed before the invalidated first provider call

- Fresh G6 at the pushed parent: Node `22.14.0`, pnpm `9.15.0`, Playwright
  `1.62.1`, Chromium present, Docker server `29.6.2`, provider credential
  present without disclosure, zero owned process residue and zero provider call.
- Frontend baseline: typecheck PASS, `119/119` tests PASS, production build PASS.
- Python baseline before BUILD: `1356 passed, 127 skipped`.
- Dedicated evidence contracts: `8 passed`.
- Real Chromium/FastAPI wrapper: PASS with checkpoint
  `P2_FULL_SHIFT_EXIT`, bounded queue PASS and sanitized ambiguity contract
  (one request, zero automatic retry, zero queue insertion, explicit fresh-read
  reconciliation).
- Disposable PostgreSQL 16 final clean run: migrations `29 applied / 0 skipped`,
  reapply `25 applied / 4 skipped`, live suite `118 passed`; engine reconnect
  verified the 12-hour lineage, FROZEN Shift/current Report, confirmed event,
  IN_PROGRESS task, unchanged non-empty ACKNOWLEDGED handover, distinct `sup2`
  Report receipt and actor-bound audits. Container absent and anonymous-volume
  residue zero after cleanup.
- Final main-worktree full Python: `1364 passed, 128 skipped`; catalog/session/
  repository/file-size/diff gates PASS.
- Exact-parent detached rehearsal at `3b0a142`: exact candidate `15/15`, Node
  `22.14.0`, pnpm `9.15.0`, Playwright `1.62.1`, frontend `119/119`, Python
  `1363 passed, 129 skipped`, catalog/session/repository/file-size/diff PASS,
  doctor `24 PASS / 1 bounded legacy warning`. The registered worktree and its
  owned temporary hidden-core clone were both removed; `git worktree` returned
  to the main worktree only.
- Governance dry-run over the real browser JSON: PASS with zero provider calls.
- Final admitted live runner: all 12 refusal cases PASS at provider delta zero;
  genuine 12-hour integrated durable scenario PASS; exactly one Alibaba
  DashScope call reached HTTP 200 using `qwen3.7-max`, matched the bounded
  sentinel, and wrote the sanitized live receipt.

## Failed attempts retained truthfully

Three browser attempts failed before the final PASS: an operator assertion
incorrectly targeted the supervisor-only event list; an invalid two-second
poll interval fell back to 15 seconds; and a final observation used the wrong
handover query parameter. Two PostgreSQL attempts then failed inside the new
test: the helper initially rejected the route's truthful `201 Created`, and
the audit expectation invented `event.create` even though the canonical
control mapping assigns the protected event audit to `EventService.confirm`.
The first detached rehearsal attempt also exposed file-size overruns at 601/600
and 302/300; its misleading shell completion marker was rejected because the
individual gate exit codes had not been fail-fast. Formatting was reduced
without semantic change and the entire rehearsal was rerun with per-gate exit
checks to the verified PASS above. All owned containers/anonymous volumes and
temporary worktrees/core clones from failed attempts were removed. No provider
call occurred during any failed attempt.

During Amendment 1 verification, the first deliberately short shell timeout
left an older wrapper process able to overwrite the owned main JSON with its
FAIL fallback; a compound PowerShell command then masked that dry-run's nonzero
code with a later read-only command. The stale file was detected before
pre-call review, rejected by the strict validator and replaced by a fresh
producer-bound run (`adb2dbf4-48a8-4b9d-a93e-f952f62dac12`). Validator and
governance dry-run were rerun as standalone fail-fast commands and both PASS.
No provider call occurred.

## Claim boundary and remaining order

Independent BUILD review returned `REVIEW_FAIL` without waiver after the live
call. It found: refusal cases checked status/counter but not full pre/post
durable immutability and one Report-gate case could stop at the handover gate;
the browser JSON hardcoded its own ambiguity/sanitization attestation without
producer provenance; PostgreSQL reconnect did not compare the complete
immutable handover snapshot, all six receipt bindings and exact action→actor
audits; and browser replay did not prove a genuine task GET landed before
rendering `IN_PROGRESS`.

These findings invalidated `READY_FOR_INDEPENDENT...` and the admission-order
claim of the first live receipt. The physical provider call remains recorded
truthfully; it was not undone or silently relabelled.

## Amendment 1 repair evidence

Human authority, independently reviewed Amendment 1 and the pre-repair
continuity checkpoint are pushed separately at `22d6bd7` and `9dbf6de` (with
the one-line file-size continuity correction at `ba8adae`). Repair closed all
four accepted BUILD findings without waiver:

- every one of the 12 refusal cases now runs on an isolated ledger and compares
  exact collection counts plus a canonical whole-ledger digest/content for
  shifts, assignments, events, tasks, ordered handover items, reports,
  approval receipts and the complete audit ledger before/after;
- Playwright writes an owned exact-schema run-id artifact after its real
  assertions pass; the wrapper binds that producer output to the selected spec
  and exact allowlisted harness payload with SHA-256; admission recomputes all
  bindings and fails on missing/mismatched run id, source/harness digest,
  unknown fields or forged counters;
- replay now proves a successful post-commit task GET containing the exact task
  id, committed version and `IN_PROGRESS`, and only then asserts the same DOM
  task; optimistic/local/stale/different-task evidence cannot pass;
- PostgreSQL reconnect compares every handover item field and order, all six
  Report receipt scope fields plus exact approver id/role, and the exact
  target/action/actor/count audit multiset, including four assignment audits
  and `approval.create`. The in-memory admission scenario uses the same exact
  multiset and rejects a wrong actor even when all action names exist;
- replacement admission reserves the sole remaining slot in a process-locked,
  append-only, flushed and `fsync`'d receipt transaction before network
  dispatch. Any reservation or result blocks every rerun, including a crash
  after provider success but before result rendering. The result append is
  separately locked/durable and records `ACCEPTED` only for one reached-server
  PASS with exact-token match; provider failure records zero accepted calls;
- PostgreSQL reconnect additionally proves the exact ACTIVE
  `p2-op`/`p2-sup1`/`p2-sup2` assignment set on both shifts, including both
  automatic creator assignments required by Amendment A1-F3;
- the browser producer enforces the same bounded asset sanitation contract as
  admission (leading slash, length <= 200, no query/fragment/backslash) before
  it can label or write a passing sanitized artifact.

The independent pre-call review that discovered these three residual gaps
returned `REVIEW_FAIL` and was later superseded by the fresh re-review below.
Focused negative
coverage for durable reservation crash/restart, provider FAIL accounting,
rerun prohibition and producer-side asset sanitation is `22 passed`.

Current repaired evidence: dedicated negative/contract suite `22 passed`; real
Chromium/FastAPI producer-bound wrapper PASS; governance dry-run PASS with all
12 isolated refusals and provider counter zero; exact Node `22.14.0` / pnpm
`9.15.0` typecheck, `119/119` frontend tests and production build PASS; full
Python `1378 passed / 128 skipped`; disposable PostgreSQL 16 `118 passed`,
migrations `29/0` then `25/4`, container absent and anonymous-volume residue
zero; catalog/session/repository/file-size/diff gates PASS.

The superseding fresh detached rehearsal at exact parent `ba8adae` contained exactly
the same 15 candidate paths and passed: contract `22/22`, real browser
producer-bound evidence (run `64950567-c56b-4c72-9596-cc46b95d05b7`), frontend
`119/119`, full Python `1378/128 skipped`,
governance dry-run, catalog/session/repository/file-size/diff and doctor
`24 PASS / 1 bounded legacy warning`. Its browser JSON, build artifacts,
registered worktree and residual dependency directory were removed; worktree
list returned to the primary workspace only.

The first physical provider call remains `INVALIDATED_BY_REVIEW_FAIL`.
Exactly one replacement was prohibited until the independent pre-call
`REVIEW_PASS` recorded below and is now authorized; a third call is forbidden.
Phase 2 remains open. No
wall-clock soak, push/exactly-once, fully-offline, production-readiness, Phase
3 or external-channel claim is made.

## Independent pre-call re-review

Independent reviewer verdict: `PRE-CALL REVIEW_PASS` — no open finding and no
waiver. The reviewer independently verified the durable locked reservation,
crash/provider-failure/rerun coverage and truthful accounting; exact ACTIVE
assignment state for both shifts after PostgreSQL reconnect; producer-side
asset sanitation; continued closure of F1-F4; exact 15-path scope; zero staged
or protected drift; and the evidence/gates recorded above. Amendment 1 now
authorizes the sole remaining replacement provider call. A third physical call
remains forbidden.

## Replacement provider execution

The authorized runner durably reserved attempt
`ecf2b066-438a-415d-9f6b-718cd8cc47ae` before network dispatch, then made the
sole replacement call. Result: `PASS`, provider reached, HTTP 200, expected
token matched, disposition `ACCEPTED`. Tranche accounting is now exactly two
physical calls (the retained invalidated first call plus this replacement) and
one accepted final call. A deliberate rerun returned the fail-closed admission
code `5` without another provider call, proving the third-call prohibition on
the persisted receipt state. Final independent post-call review remains
required before any tranche closeout disposition.

## Independent final post-call review

Verdict: `FINAL REVIEW_PASS` — no open finding and no waiver. The reviewer
verified reservation/result order and identical attempt id; all acceptance
predicates; physical `2` / accepted `1` accounting with the first call retained
as invalidated; persisted third-call prohibition; sanitized receipts; synced
claim boundaries; exact 15-path candidate; zero staged/protected drift; and
complete owned temp/worktree/Docker cleanup. Phase 2 and separate C4 remain
open until the reviewed BUILD is committed/pushed and C4 truth sync completes.
