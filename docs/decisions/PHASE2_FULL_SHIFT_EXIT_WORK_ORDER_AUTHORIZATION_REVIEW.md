# Phase 2 Full-Shift Exit Work Order — Independent Authorization Review

- Review id: `P2-FULL-SHIFT-EXIT-AUTH-REVIEW-001`
- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Role: independent `AUTHORIZATION_REVIEWER`
- Risk: `R2`
- Source baseline reviewed: `e1ac14beaf426ded1b763ff3373b238a065c4694`
- Review date: `2026-08-02`
- Disposition: **`REVIEW_PASS / APPROVED`**
- BUILD authority: **GRANTED only after the five authorization artifacts are
  pushed, a separate pre-BUILD continuity checkpoint is pushed, and fresh G6
  passes**

## Scope reviewed

The review compared current source/governance truth with exactly these four
untracked authorization artifacts:

1. `docs/decisions/INTAKE_2026-08-02_PHASE2_FULL_SHIFT_EXIT.md`
2. `docs/decisions/ADR_2026-08-02_PHASE2_FULL_SHIFT_EXIT.md`
3. `docs/specs/PHASE2_FULL_SHIFT_EXIT_SPEC.md`
4. `docs/work_orders/PHASE2_FULL_SHIFT_EXIT_WORK_ORDER.md`

No implementation suite, browser run, PostgreSQL run or provider call was used
or claimed by this authorization review. Workspace doctor returned `PASS WITH
NOTE` (`24 passed / 1` bounded legacy warning); `HEAD == origin/main` at the
reviewed baseline. The proposed inventory contains exactly 17 unique paths,
and every `NEW`/existing label is mechanically accurate.

## Findings

### P2-EXIT-AUTH-F1 — two mandatory existing-path edits are unnecessary

Work Order section 2 requires every listed path to change materially, including:

- `scripts/testing/run_c3c_web_evidence.py`
- `tests/integration/test_c3c_web_evidence_runner.py`

Current source already provides the exact reusable contract needed by the new
wrapper: `run_harness` accepts `checkpoint`, `playwright_grep` and
`queue_checkpoint`, while `queue_checkpoint_passed` already accepts
`bounded_exercised_and_cleaned` and explicitly delegates the substantive queue
assertions to the selected Playwright spec. The current P2-D wrapper demonstrates
that reuse without editing either shared file. Requiring both paths to change
would force unnecessary churn and violates the Work Order's own rule that an
unnecessary listed edit is `BLOCKED_WORK_ORDER_CEILING`.

Required repair: remove both paths and make the ceiling exactly 15, or state a
new, testable harness behavior that current source demonstrably lacks. Do not
invent a rename-only/comment-only edit to satisfy the ceiling.

### P2-EXIT-AUTH-F2 — provider execution is not actually last

Work Order section 6 says provider execution is last among behavioral gates,
but schedules the AC-14 exact-parent detached rehearsal only after the command
sequence containing the real provider runner. That rehearsal reproduces Python,
frontend and repository baselines and is therefore a behavioral gate. This
contradicts the requested provider-last contract and allows an expensive real
call before the final behavioral prerequisite is known to pass.

Required repair: place the exact-parent rehearsal, its cleanup verification and
all other no-network behavioral gates before
`run_phase2_full_shift_live_governance_evidence.py`. Only non-behavioral receipt
validation/final diff checks may follow the real call. State the order once,
without a later paragraph reversing it.

### P2-EXIT-AUTH-F3 — assignment bootstrap conflicts with the UI/API boundary

SPEC R3 requires the operator to own creation of both shifts while `sup1` and
`sup2` have active assignments. SPEC R9 permits API arrangement only for a
prerequisite with no UI surface. Current UI does expose staffing assignment,
but an unassigned supervisor cannot select an operator-created shift to reach
that surface; the operator does not have supervisor assignment authority. The
documents neither identify this bootstrap constraint nor authorize and label a
bounded API arrangement for it. A worker can therefore either dead-end or
silently substitute API calls for a positive UI action.

Required repair: define the exact actor/page sequence for source and destination
assignment. If API bootstrap is unavoidable, explicitly classify only the
minimum bootstrap calls as arrangement for a UI-inaccessible prerequisite,
list the calls and actors, and still drive every subsequently available
staffing/operational action through the rendered UI. Otherwise revise R3 to a
feasible all-UI ownership sequence without weakening distinct identities.

### P2-EXIT-AUTH-F4 — polling proof does not name a coherent remote mutation

SPEC R4 requires the offline task transition to finish at `IN_PROGRESS`, then
requires a later supervisor mutation to appear through polling; R7 still
requires that task to be `IN_PROGRESS` at final reconnect. Neither SPEC nor Work
Order identifies what the later mutation is or which page must observe it.
Reusing the P2-D remote task-transition pattern would conflict with the already
completed transition/final state, while an arbitrary assignment or Report
mutation could weaken the intended same-lineage composition claim.

Required repair: name the exact later mutation, actor, observing browser page,
expected rendered before/after state and final durable state. Preserve one
lineage, no manual refresh, and the required final open-work snapshot.

### P2-EXIT-AUTH-F5 — transport ambiguity is assigned to an incompatible proof owner

SPEC R8 includes transport ambiguity in the refusal matrix. Work Order section
3 says the governance runner executes all of R8 with a shared provider counter,
while the actual ambiguity boundary is browser transport and the browser runner
is a separate process. The current package provides no defined mechanism by
which the governance runner can execute or observe that browser event, and
`without unintended durable mutation` is too strong for an ambiguous response:
the intended mutation may have committed even though the client cannot know.

Required repair: split ownership explicitly. The real-browser spec must prove
one request, no automatic retry, no queue insertion and outcome-unknown handling;
the governance runner may record only its own zero-call refusal cases before the
integrated admitted proof. Define how the final receipt references the separately
reviewed browser result without claiming a shared in-process counter observed it,
and replace the impossible no-mutation implication with verification of no
duplicate/unintended retry plus reconciliation of the authoritative final state.

## Accepted boundaries

Subject to the findings above, the following parts are correctly bounded:

- `12 hours` means the exact persisted scheduled interval, not a wall-clock soak.
- P2-D composition requires one bounded replay, polling observation and zero
  final queue residue without claiming push, exactly-once or full offline.
- Disposable PostgreSQL 16 uses migration-created schema, real JWT/FastAPI and
  reconnect verification for final records, receipt binding and actor audits;
  no production-readiness claim is made.
- Product/API/schema/migration/dependency/CI paths are protected from BUILD.
- Provider output remains evidence metadata only, with refusal-before-admission,
  exactly one real call and sanitized receipts.
- Independent BUILD review and a separate C4 are required before bounded Phase
  2 closure; post-Phase-2 authority does not carry backward into this BUILD.

## Re-review after repair

Re-review disposition: **`REVIEW_CHANGES_REQUIRED`**. BUILD authority remains
**NOT GRANTED**.

Closed without waiver:

- `P2-EXIT-AUTH-F1`: ceiling is now exactly 15 paths; the two unnecessary
  shared-harness edits were removed.
- `P2-EXIT-AUTH-F2`: exact-parent rehearsal and its cleanup now precede the
  real-provider command; only receipt/final-diff/temp cleanup follows.
- `P2-EXIT-AUTH-F4`: polling now names `sup1` event confirmation, the observing
  operator timeline and final task `IN_PROGRESS` state.
- `P2-EXIT-AUTH-F5`: browser owns ambiguity proof; the governance runner owns
  only its counter and validates a separate sanitized browser result.

### P2-EXIT-AUTH-REREVIEW-F6 — claimed UI-inaccessible bootstrap contradicts current source

The F3 repair authorizes one direct API call by saying the staffing UI is
unreachable before a supervisor assignment. Current source says the opposite:
`SupervisorActions.tsx` documents and implements that **Staffing is always
rendered (works even with no selected operational shift)**, and renders
`StaffingActions` outside the `selectedShiftId` conditional. The dedicated
staffing reads expose the bounded supervisor control plane independently of
ordinary assignment-scoped operational reads. `AssignmentService` likewise
allows a supervisor to staff any shift without first holding an assignment.

Therefore authenticated `sup1` can use the rendered Staffing UI to assign
itself to the operator-created source shift. The proposed API bootstrap is not
UI-inaccessible and violates SPEC R9's no-positive-API-substitution rule.

Required repair: remove the API bootstrap exception from ADR, SPEC R3/R9 and
Work Order section 3. Require `sup1` to use the already-rendered Staffing UI for
its source self-assignment, destination self-assignment and both `sup2`
assignments. Keep API use limited to login and read-only observation. Add the
source self-assignment to the browser action sequence explicitly.

### P2-EXIT-AUTH-REREVIEW-F7 — R4 lost the replay contract sentence

The repaired SPEC R4 currently reads “replays state.” after the reconnect
clause. This is incomplete and dropped the original explicit requirements for
one replay with recorded CAS plus a fresh read rendering committed
`IN_PROGRESS`. AC-04 retains part of that intent, but requirements and
acceptance must not disagree or leave recorded-CAS behavior implicit.

Required repair: restore a complete R4 sentence requiring exactly one replay
with the recorded CAS and a fresh read/render of committed `IN_PROGRESS`, then
continue with the named event-confirmation polling proof.

## Final authorization re-review after F6-F7 repair

Final disposition: **`REVIEW_PASS / APPROVED`**. All findings `F1` through
`F7` are closed without waiver.

- `P2-EXIT-AUTH-F1`: the BUILD ceiling is exactly 15 unique paths (11 NEW,
  four existing), every NEW/existing label matches the current baseline, and
  the two reusable shared-harness paths remain outside the ceiling.
- `P2-EXIT-AUTH-F2`: exact-parent rehearsal and verified temporary-worktree
  cleanup occur before provider admission. The provider runner is the last
  behavioral execution; only sanitized receipt/final-diff validation and
  exact owned-temp cleanup follow.
- `P2-EXIT-AUTH-F3` and `P2-EXIT-AUTH-REREVIEW-F6`: the repaired documents
  match current source. Initially unassigned `sup1` uses the always-rendered
  Staffing UI to assign both `sup1` and distinct `sup2` to source and
  destination. No assignment bootstrap API or other positive-action API
  substitution is authorized; API use is limited to login and labelled
  read-only observation.
- `P2-EXIT-AUTH-F4`: the remote mutation is the exact event confirmation by
  `sup1`; the still-open operator page observes it in the confirmed timeline
  through polling without reload, while the task remains `IN_PROGRESS` for
  the non-empty handover snapshot and final durable state.
- `P2-EXIT-AUTH-F5`: the real browser owns transport ambiguity and proves one
  request, no automatic retry, no queue insertion, visible `outcome_unknown`
  and authoritative-state reconciliation. The governance runner validates a
  separate sanitized browser JSON result without claiming its in-process
  zero-call counter observed the browser process.
- `P2-EXIT-AUTH-REREVIEW-F7`: SPEC R4 now requires exactly one replay with the
  recorded CAS and permits committed `IN_PROGRESS` rendering only after a
  genuine fresh read.

This authorization review ran no implementation suite, browser scenario,
PostgreSQL scenario or provider call and makes no BUILD-evidence claim.
Workspace doctor remains `PASS WITH NOTE` (`24 passed / 1` bounded legacy
warning), and the reviewed source baseline satisfies `HEAD == origin/main ==
e1ac14beaf426ded1b763ff3373b238a065c4694`.

## Next allowed move

Commit and push exactly the four authorization artifacts plus this independent
review receipt. Then create and push the separate pre-BUILD continuity
checkpoint and run fresh G6. Only after those gates pass may an
`IMPLEMENTATION_WORKER` begin the exact 15-path BUILD. No provider call, Phase
2 closure or post-Phase-2 authority is granted at authorization time.
