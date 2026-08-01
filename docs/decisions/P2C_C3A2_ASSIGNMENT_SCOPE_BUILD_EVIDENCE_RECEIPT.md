# P2C-C3A2 Assignment-Scope Route Enforcement — BUILD Evidence Receipt

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Final exact BUILD set: exactly **74 paths** (original 79 + Amendment 1's 2
  ceiling-repair paths + Amendment 2's 1 handover-runner-test path, minus
  Amendment 3's 8 removed paths). This is an exact set, not a ceiling with
  slack — AC-32 requires the changed-path set to equal it exactly, and it
  does (see "Exact changed-path membership" below).
- Resume/review parent (this round): `5063693d095abcc63ca7bfc9d8555f9ffe3300d5`
  (`HEAD == origin/main` verified before any edit)
- Prior resume/review parent: `22e05b5bd68fbb8dafa12c1646d527280692b736`
- Status: `READY_FOR_INDEPENDENT_P2C_C3A2_BUILD_RE_REVIEW`

## Amendment record

- Amendment 1 (`79 → 81`): added `tests/contract/test_contract_files.py` and
  `scripts/run_message_admission_live_governance_evidence.py`.
- Amendment 2 (`81 → 82`): added
  `tests/integration/test_handover_live_evidence_runner.py`.
- Amendment 3 (`82 → 74`,
  `docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER_AMENDMENT_3.md`,
  approved): repairs finding `C3A2-BUILD-REV-F3 AC32_EXACT_SET_MISMATCH` by
  removing exactly 8 paths from the 82-path set, since their existing
  behavior needed no code change and was already independently reverified
  passing. The removed paths are now prohibited, not reserved:
  `tests/cvf/test_assignment_foundation.py`,
  `tests/cvf/test_customer_request_repair.py`,
  `tests/cvf/test_customer_request_transitions.py`,
  `tests/cvf/test_shift_create_admission.py`,
  `tests/integration/test_p2c_read_postgres_limit_live.py`,
  `tests/integration/test_shift_create_live_evidence_runner.py`,
  `tests/integration/test_shift_create_postgres_live.py`,
  `tests/integration/test_shift_create_sqlite.py`. This receipt is rewritten
  under Amendment 3's repair contract to state exact 74-of-74 equality and
  remove any prior suggestion that an authorized 74-path subset of an
  82-path ceiling satisfies AC-32.

## History

1. G6 passed at pre-BUILD parent `6951810`: full non-live 1127/112, repository
   gates PASS, doctor `PASS WITH NOTE 24/1`, Docker/PostgreSQL/provider
   prerequisites available, zero owned residue.
2. Partial BUILD wired the central `assignment_scope.py` guard into all 17
   R6-listed routers/services and stopped without out-of-ceiling edit when the
   full suite exposed two omitted edit hosts (Amendment 1: `79 → 81`).
3. After Amendment 1, the partial BUILD reached 58 changed paths (all
   in-ceiling, zero staged) with `1125 passed / 2 failed / 112 skipped`; both
   failures were confined to
   `tests/integration/test_handover_live_evidence_runner.py`'s two P2-R
   regression scenarios, which minted test-local authenticated principals but
   never persisted the ACTIVE assignments C3a2 now requires (Amendment 2:
   `81 → 82`, finding `C3A2-BUILD-BLOCK-F2`).
4. Resumed from `22e05b5`, verified `HEAD == origin/main`, reconfirmed G6
   (session/catalog/file-size/repository/diff gates PASS; Docker available
   with zero `cvf-pg-live-*` residue; `psycopg` 3.3.4 present;
   `ALIBABA_API_KEY` present), and preserved the existing unstaged partial
   BUILD without reset, stash or discard.
5. Closed `C3A2-BUILD-BLOCK-F2` by editing only the newly authorized
   `tests/integration/test_handover_live_evidence_runner.py`: added explicit
   persisted ACTIVE assignments via the existing `runner._seed` seam —
   `hov-ev-op2`/`hov-ev-sup3` on the source shift and `hov-ev-sup4` on the
   destination shift for the no-report scenario; `hov-ev-op3`/
   `hov-ev-rep-approver2` on the source shift for the ready-report scenario.
   No implicit assignment was added to `_auth_headers`/`_with_ledger`; no
   `AssignmentScope`/enumeration-safe behavior was weakened; no production
   code was touched. Full non-live suite reached **1127 passed, 0 failed, 112
   skipped** immediately after this fix.
6. Authored the six feature-owned enforcement-proof paths plus the
   `docs/cvf/CVF_CONTROL_MAPPING.md` append:
   `tests/cvf/test_assignment_scope_routes.py` (299 lines after later F4
   compaction), `tests/cvf/test_assignment_scope_cross_shift.py` (205 lines),
   `tests/cvf/test_assignment_scope_enumeration.py` (194 lines),
   `tests/integration/test_assignment_scope_postgres_live.py` (135 lines,
   opt-in, skips cleanly without `LIVE_POSTGRES_DATABASE_URL`),
   `tests/integration/test_assignment_scope_live_evidence_runner.py` (184
   lines), `scripts/run_assignment_scope_live_governance_evidence.py` (299
   lines, self-contained per the C3a1 precedent — no companion support module
   is authorized). Full non-live suite reached **1177 passed, 0 failed, 116
   skipped** immediately after authoring. `check_file_size.py`: PASS.
7. Running the disposable PostgreSQL live suite first surfaced 16 real
   regressions: four existing legacy fixture modules
   (`test_message_postgres_live.py`, `test_handover_postgres_live.py`,
   `test_report_postgres_live.py`, `test_incident_postgres_live.py`) minted
   principals and called governed services/routes without ever persisting
   their ACTIVE assignment, per WO section 3.5's fixture-migration
   requirement. Repaired each by adding an explicit persisted-assignment seed
   step (`_seed`/inline `add_user`+`add_assignment`) immediately before the
   now-scoped service/route call, touching no production code. Re-run
   surfaced one further gap (a report/incident approval-receipt approver
   minted mid-test with no assignment) which was repaired the same way. Also
   added the new `tests/integration/test_assignment_scope_postgres_live.py`
   target to `scripts/run_postgres_live_roundtrip.py`'s `LIVE_SUITE_TARGETS`
   tuple and updated `tests/integration/test_postgres_live_runner.py`'s
   exact-tuple pin test from eight to nine modules.
8. During live governance evidence generation, re-running the five
   already-existing (out-of-set) live-evidence scripts
   (`run_handover_live_governance_evidence.py`,
   `run_incident_live_governance_evidence.py`,
   `run_message_admission_live_governance_evidence.py`,
   `run_p2c_read_live_governance_evidence.py`,
   `run_report_live_governance_evidence.py`) regenerated their receipt files
   with fresh timestamps as a side effect. Those five receipt paths are
   outside the BUILD set; the regenerated content was reverted with
   `git checkout --` immediately on discovery. The underlying live evidence
   itself (all five scripts returned `LIVE EVIDENCE PASS`, HTTP 200) is
   reported truthfully as verification proof, without persisting those files.
9. Independent review of the above BUILD returned four findings. F1, F2 and
   F4 were BUILD-quality defects inside the existing 82-path ceiling and were
   repaired in that round; F3 required ceiling authority this worker did not
   have and was reported `BLOCKED_WORK_ORDER_CEILING`:
   - **F1 `COARSE_PERMISSION_ORDERING_REGRESSION`** (real defect, confirmed
     and repaired): `ShiftService.close`/`.freeze`,
     `ReportService.create_successor`, `get_task_creation_intent` and
     `create_approval_receipt` each called `require_active_assignment`
     before their coarse permission/authority check, so an unassigned caller
     with insufficient role received 404 (enumeration-safe refusal) instead
     of 403 (coarse denial) — masking the permission finding rather than
     layering it. Repaired by reordering each site to run the coarse check
     first: `shift_service.py`'s `close`/`freeze` now call `require_action`
     before `require_active_assignment` (pure reorder, zero line-count
     change); `report_service.py`'s `create_successor` now resolves
     `is_revocation` from the already-fetched record and calls
     `require_action` with the correct action name before assignment;
     `task_creation_intents.py`'s `get_task_creation_intent` now checks
     user-active/authority-for-seat before assignment; `approval_receipts.py`'s
     `create_approval_receipt` was restructured so all four record-type
     branches resolve only `shift_id` (no longer call
     `require_active_assignment` per-branch), then a single active-user/
     authority check runs, then one `require_active_assignment` call —
     collapsing 4 call sites to 1 while fixing the order. Three tests whose
     assertions encoded the old (wrong) ordering were corrected to expect the
     coarse-permission status instead:
     `tests/cvf/test_approval_known_principals.py::test_fabricated_approver_id_cannot_create_a_receipt`
     and `::test_unregistered_or_random_uuid_approver_is_not_a_known_user`
     (now expect `CvfDenied`/403, not `OperationalResourceNotFound`/404) and
     `tests/cvf/test_assignment_scope_enumeration.py::test_refused_approval_receipt_leaves_zero_receipts_and_zero_audit`
     (an unassigned, insufficiently-authorized outsider now correctly gets
     403, not 404). No `AssignmentScope`/enumeration-safe behavior for
     missing-vs-inaccessible records was weakened — F1's fix only reorders
     coarse role/authority checks ahead of the fine-grained assignment check,
     the same ordering every other already-correct route in the matrix
     (`event.correct`, `report.approve`, `report.submit_review`) already
     used.
   - **F2 `LIVE_ADMITTED_AUDIT_PROOF_ABSENT`** (real defect, confirmed and
     repaired): `run_assignment_scope_live_governance_evidence.py`'s
     genuine-construction case (`build_admitted_open_work_genuine`) created
     the ACTIVE assignment by calling `ledger.add_assignment(...)` directly
     (not through a governed route) and then only asserted
     `GET /shifts/{id}/open-work` returned 200 — a pure read, which produces
     no audit record at all, so the function's docstring claim of proving
     "the audit trail... is present" was never actually checked by any
     assertion. Repaired by replacing the genuine-construction case with
     `POST /messages` (a real R6 mutation admitted through the same
     assignment_scope guard, function renamed to
     `build_admitted_message_create_genuine`), which now asserts exactly one
     `message.create` audit exists with every field (`actor_id`,
     `actor_role`, `action`, `record_type`, `record_id`, `control_chain`,
     `before_state`, `after_state`) matching an exact expected dict —
     mirroring the proven exact-field-match pattern already used by
     `run_assignment_live_governance_evidence.py`'s C3a1 genuine case. The
     runner's docstring, receipt claim-boundary text and the two dependent
     non-live tests in
     `tests/integration/test_assignment_scope_live_evidence_runner.py` were
     updated to match (the old "mismatched scoped shift" negative test had
     no equivalent under the new route, since message creation discards
     `require_active_assignment`'s return value entirely; replaced with a
     "mutated audit actor" negative test proving the exact-field check
     actually fails closed).
   - **F4 `FOCUSED_MATRIX_GAP`** (real gap, confirmed and repaired): the
     focused assignment-scope route matrix had no case for `event.correct`
     (`POST /corrections/events/{id}`) or `Report /{id}/versions`
     (`POST /reports/{id}/versions`, `ReportService.create_successor`).
     Added `test_event_correct_role_then_assignment_ordering` (proves
     insufficient-role 403 fires before assignment 404, matching the
     already-correct `event.confirm`/`incident.acknowledge` pattern) and
     `test_report_create_version_requires_active_assignment` to
     `tests/cvf/test_assignment_scope_routes.py`, compacting six existing
     verbose test bodies to one-line-assertion form to stay at 299/300
     physical lines (line-neutral repair, no new file).
   - **F3 `AC32_EXACT_SET_MISMATCH`** (real gap; blocked pending amendment,
     now resolved by Amendment 3 — see below): AC-32 requires the exact
     changed-path set to equal the authorized set; that BUILD round touched
     74 of the then-82-path ceiling. The 8 untouched paths needed no code
     change — their existing behavior was already correct and independently
     reverified passing (full non-live suite, disposable PostgreSQL live
     suite, both green) — so satisfying AC-32 required a Work Order Amendment
     3 removing those 8 unnecessary paths from the ceiling rather than a
     fabricated edit to force 82/82. This worker had no ceiling-amendment
     authority and did not attempt one; it stopped with
     `BLOCKED_WORK_ORDER_CEILING` and returned control for Amendment
     authorship/review/approval.

   After F1/F2/F4 (prior round, still valid): focused matrix **38 passed**
   (was 36); full non-live suite **1179 passed, 0 failed, 116 skipped** (was
   1177/0/116); disposable PostgreSQL live suite re-run **106 passed, 0
   failed** (no regression from the F1 reorder); the five other
   live-evidence scripts re-verified via `--dry-run` (which never calls
   `render_receipt`, so no out-of-set receipt regeneration risk) all still
   PASS their refusal gate and genuine construction;
   `run_assignment_scope_live_governance_evidence.py` re-run for real,
   `LIVE EVIDENCE PASS`, HTTP 200, receipt regenerated documenting the
   audited mutation.
10. **Amendment 3 approved and pushed**
    (`docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER_AMENDMENT_3.md`).
    Resumed from the pushed four-surface checkpoint
    `5063693d095abcc63ca7bfc9d8555f9ffe3300d5`, verified
    `HEAD == origin/main == 5063693` and the existing 74-path unstaged BUILD
    preserved (no reset/stash/discard), reconfirmed G6 (session/catalog/
    file-size/repository/diff gates PASS; Docker available with zero
    `cvf-pg-live-*` residue; `psycopg` 3.3.4 present; `ALIBABA_API_KEY`
    present). Verified all 8 removed paths are byte-identical to `HEAD`
    (`git diff --quiet HEAD -- <path>` clean for each). Rewrote this receipt
    from 74-of-82-subset language to exact 74-of-74 equality. Re-ran the
    focused matrix (**38 passed**, unchanged) and full non-live suite
    (**1179 passed, 0 failed, 116 skipped**, unchanged) — Amendment 3 is a
    ceiling-bookkeeping change only, not a code change, so these counts are
    identical to the prior round. Retained the already-recorded fresh post-F2
    live-evidence receipt at
    `docs/decisions/P2C_C3A2_ASSIGNMENT_SCOPE_LIVE_EVIDENCE_RECEIPT.md`
    without another provider call: confirmed
    `scripts/run_assignment_scope_live_governance_evidence.py` is unchanged
    (299 lines, same content) since that receipt was generated and its own
    14-test non-live suite still passes, so per the amendment's repair
    contract ("do not make another provider call merely because the ceiling
    contracted") no new call was made.
11. **Independent re-review returned one further finding,
    `C3A2-BUILD-REREV-F1 REPORT_APPROVAL_SCOPE_ORDERING_INCOMPLETE`**: F1's
    prior repair reordered the coarse authority check ahead of
    `require_active_assignment` in `create_approval_receipt`, but the
    Report branch's *own* embedded lifecycle gate (`not record.is_current or
    status != "IN_REVIEW"` → 409) still ran inline in that branch, before
    both the authority check and the assignment check — so an unassigned
    viewer with no R2 authority got 409 (lifecycle) instead of 403
    (authority), and an unassigned-but-authorized supervisor also got 409
    instead of 404 (assignment). Only an assigned, authorized supervisor
    should ever reach the real 409. Repaired entirely inside the exact
    74-path set: `approval_receipts.py`'s Report branch now only computes
    `report_lifecycle_ok = record.is_current and str(record.status) ==
    "IN_REVIEW"` and stores `shift_id`; the actual 409 raise was moved to
    after the shared `user`-active/authority check and the single
    `require_active_assignment` call, gated on `record_type == "Report" and
    not report_lifecycle_ok`. Net effect on the file: 227 lines (was 226),
    well under the 300-line limit. Added
    `tests/cvf/test_assignment_scope_enumeration.py::test_report_approval_receipt_checks_authority_then_assignment_then_lifecycle`:
    builds a DRAFT (not IN_REVIEW) report via `POST /reports` on a closed
    shift, then proves the exact order against a single `record_id` —
    unassigned+unauthorized operator gets 403, unassigned-but-authorized
    supervisor gets 404, only the same supervisor once assigned gets 409 —
    with zero `approval_receipts`/audit writes at every step (delta-checked
    before and after all three calls). A `_OUTSIDER_SUP` constant
    (`shift_supervisor` role, seeded but never assigned) was added to that
    file's fixture set for the negative cases. Re-verified: focused matrix
    **39 passed** (was 38); full non-live suite **1180 passed, 0 failed, 116
    skipped** (was 1179/0/116, +1 catalog LOC delta from the fix required a
    `generate_catalog.py --write`, then `--check` PASS); disposable
    PostgreSQL live suite re-run **106 passed, 0 failed** again (no
    regression); repository gates all PASS; exact 74-of-74 set equality
    reconfirmed (both changed files were already in the set, so no ceiling
    impact); no new provider call was made (provider-path code and the live
    receipt are unchanged since F2's fix, confirmed again this round).

## Exact changed-path membership

**Exact 74-of-74 equality.** The final BUILD set contains exactly 74 paths
(Amendment 1/2's 82-path union minus Amendment 3's 8 removed paths); the
candidate's changed-path set is exactly those same 74 paths — not a subset,
not a superset. Verified by three-way comparison:

```bash
git status --porcelain=v1 | sed -E 's/^...//' | sort -u       # → 74 lines
<82-path ceiling> minus <Amendment 3's 8 removed paths>        # → 74 lines
comm -23 <changed> <exact-74-set>                               # → empty (no outside-set path)
comm -13 <changed> <exact-74-set>                               # → empty (no unchanged authorized path)
```

Both `comm` differences are empty: zero changed paths fall outside the exact
74-path set, and zero paths in the exact 74-path set were left unchanged.
This is the exact-set equality AC-32 requires — not "a subset of an 82-path
ceiling," which was F3's finding against the prior receipt's language.

The 8 paths Amendment 3 removed are confirmed **byte-identical** to the
resume parent (`git diff --quiet HEAD -- <path>` returns clean for all 8):
`tests/cvf/test_assignment_foundation.py`,
`tests/cvf/test_customer_request_repair.py`,
`tests/cvf/test_customer_request_transitions.py`,
`tests/cvf/test_shift_create_admission.py`,
`tests/integration/test_p2c_read_postgres_limit_live.py`,
`tests/integration/test_shift_create_live_evidence_runner.py`,
`tests/integration/test_shift_create_postgres_live.py`,
`tests/integration/test_shift_create_sqlite.py`. They are prohibited paths
for this checkpoint, not reserved ones — no future C3a2 round may touch them
without a further amendment.

## Focused assignment-scope matrices

```powershell
python -m pytest -q tests/cvf/test_assignment_scope_routes.py tests/cvf/test_assignment_scope_cross_shift.py tests/cvf/test_assignment_scope_enumeration.py
```

**39 passed** (38 before the F1-rereview repair). Covers the exact R6
route/action matrix (shift list/open-work/close/freeze, message create, event
create/list/confirm/correct including the F4-added correction-quorum ordering
case, task creation-intent create/get plus task create/transition,
shift-bound customer-request create/transition, incident
report/get/list/acknowledge/transition, handover
create/get/list/review/acknowledge, Report
generate/get/list/version/submit/approve including the F4-added `/versions`
case, approval receipt creation); cross-shift/stored-target rules (handover
source-vs-destination asymmetry, approval stored-target resolution,
task-intent stored-shift resolution, incident/customer-request stored-shift
trust over any body claim); and enumeration-safe/atomic refusal (401/403
preserved, identical missing-vs-inaccessible 404 body, leak-free
shift/handover lists, refusal-before-mutation atomicity for
message/incident/approval-receipt paths, corrected post-F1 to expect 403 for
the insufficiently-authorized-and-unassigned approval-receipt case, and the
F1-rereview-added exact 403 → 404 → 409 ordering proof for
`report.approve`).

## Full non-live suite

```powershell
python -m pytest -q
```

**1180 passed, 0 failed, 116 skipped** (1179/0/116 before the F1-rereview
repair's one added test). Baseline before the original resume was 1125
passed / 2 failed / 112 skipped, both failures confined to
`test_handover_live_evidence_runner.py` before its F2 fix.

## Repository gates

- `python scripts/check_session_state.py` → `SESSION STATE: PASS`
- `python scripts/generate_catalog.py --check` → `CATALOG VERIFY: PASS` (20
  modules, all paths exist, statuses valid, metrics and Markdown up to date)
- `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`
- `python scripts/testing/validate_repository.py` → `repository validation
  passed (catalog + session state + file-size checks)`
- `git diff --check` → exit 0 (only pre-existing LF/CRLF warnings, no
  conflict markers, no trailing-whitespace errors)

## Disposable PostgreSQL evidence

```powershell
python scripts/run_postgres_live_roundtrip.py --json
```

First run (pre-F1/F2/F4): migrations 24/0 then 20/4 (reapply idempotent);
live suite **16 failed, 90 passed** — all 16 failures were the
legacy-fixture assignment-seeding gap described in History item 7. Container
removed and zero-volume-residue confirmed even on failure.

Second run after the fixture repair: same migrations 24/0 then 20/4; live
suite **106 passed, 0 failed**, including all 4 new
`test_assignment_scope_postgres_live.py` cases (representative read,
mutation, cross-shift-source-vs-destination and supervisor-bar-mutation
routes proven against a real PostgreSQL-backed `SqlLedger`). Container
removed with `container_absent_after_cleanup: true`; independently
reconfirmed zero `cvf-pg-live-*` residue afterward.

Third run after the F1 permission-ordering repair (to prove the reorder
regressed nothing on real PostgreSQL): same migrations 24/0 then 20/4; live
suite **106 passed, 0 failed** again. Container removed with
`container_absent_after_cleanup: true`; independently reconfirmed zero
`cvf-pg-live-*` residue afterward.

Amendment 3 itself changed no production or test code, so the PostgreSQL
live suite was not re-run in that round. Fourth run after the
F1-rereview repair (`approval_receipts.py`'s Report-branch lifecycle
reorder): same migrations 24/0 then 20/4; live suite **106 passed, 0
failed** again — no regression. Container `cvf-pg-live-969a4b50be57`
removed with `container_absent_after_cleanup: true`; independently
reconfirmed zero `cvf-pg-live-*` residue afterward with a direct
`docker ps -a`/`docker volume ls` filter check.

## Live governance evidence

`docs/decisions/P2C_C3A2_ASSIGNMENT_SCOPE_LIVE_EVIDENCE_RECEIPT.md` (the
fresh post-F2 receipt) is retained unchanged this round, per Amendment 3's
repair contract: no provider-path implementation or live-evidence-relevant
code changed since it was generated, so no new provider call was made merely
because the ceiling contracted. It records: 3 refusal cases
(`open_work_denied_without_active_assignment`,
`message_create_denied_without_active_assignment`,
`incident_acknowledge_denied_insufficient_role_before_assignment`) all PASS
at 0 observed provider calls; the genuine ACTIVE-assignment-admitted
operation is `POST /messages`, verified against exactly one
exact-field-matched `message.create` audit record (`actor_id`, `actor_role`,
`action`, `record_type`, `record_id`, `control_chain`, `before_state`,
`after_state` all checked, not merely a 200 status); then exactly 1 real
Alibaba `qwen3.7-max` call returned HTTP 200
(`CVF_ASSIGNMENT_SCOPE_EVIDENCE_OK`). No secret, bearer token, DSN, URL
credential or raw exception appears in the receipt. This round independently
reconfirmed validity by checking `scripts/run_assignment_scope_live_governance_evidence.py`
is unchanged (299 lines) since generation and that its 14-test non-live suite
(`tests/integration/test_assignment_scope_live_evidence_runner.py`) still
passes.

As required verification that C3a2's guard (both the original wiring and the
F1 permission-ordering repair) did not regress the other five already-proven
verticals, their live-evidence scripts were re-run twice in the prior round
— once as real runs (receipts reverted, per the note below) and once via
`--dry-run` after the F1 repair (which returns before `render_receipt` is
ever called, so it cannot regenerate an out-of-set receipt): refusal-gate
PASS at zero calls and genuine admitted construction PASS for all five —
`run_handover_live_governance_evidence.py`,
`run_incident_live_governance_evidence.py`,
`run_message_admission_live_governance_evidence.py`,
`run_p2c_read_live_governance_evidence.py`,
`run_report_live_governance_evidence.py`. Their five receipt files sit
outside the 74-path C3a2 set; the one round of regenerated content from the
real-run pass was reverted with `git checkout --` immediately on discovery
so the changed-path set remains exactly the authorized 74 — this receipt
records the verification result truthfully without persisting those
out-of-set files.

## AC-29 isolated exact-parent rehearsal

A temporary detached worktree was created at the exact recorded resume parent
`22e05b5bd68fbb8dafa12c1646d527280692b736` (via `git worktree add --detach`,
never touching the primary candidate worktree). It started clean and
returned:

- Full non-live suite: **1126 passed, 113 skipped**
- `check_session_state.py`: PASS
- `generate_catalog.py --check`: PASS (20 modules)
- `check_file_size.py`: PASS
- `validate_repository.py`: PASS
- `git diff --check`: exit 0
- `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`:
  **PASS WITH NOTE (24 passed, 1 warning)** — the same bounded
  `LEGACY_PROJECT` catalog-kit note as every prior C3a1/C3a2 doctor run, not
  a new finding.

The temporary worktree was then removed (`git worktree remove --force`) and
pruned (`git worktree prune`); its exact path was confirmed absent
afterward. The primary candidate worktree was reconfirmed at
`HEAD == 22e05b5` with zero staged files and its partial BUILD fully intact
throughout. Not re-run this round: Amendment 3 changed no production/test
code and every gate it touches (repository gates, non-live suite) was
reconfirmed directly above at the new resume parent `5063693`; it remains
available to re-rehearse on request.

## Claim boundary

Unchanged from the Work Order section 8: C3a2 proves only that the existing
single-workspace operational routes in R6/R7 enforce stored ACTIVE shift
assignment, with enumeration-safe refusal and capability non-authority, on
the proven backends (InMemory, SQLite, disposable PostgreSQL 16). It does not
prove tenant isolation, provider `data_scope`, token early revocation,
production/managed PostgreSQL, frontend mutation/full UI, P2-C completion,
P2-D, the full-shift exit gate or Phase-2 completion. The
`run_assignment_scope_live_governance_evidence.py`'s refusal gate and the
PostgreSQL live suite each cover a representative sample of R6 routes, not
every route in the matrix — full-matrix proof lives in
`tests/cvf/test_assignment_scope_*.py`, not the live runner or the live
PostgreSQL suite.

## Worker attestation

No stage, commit, push, self-review or FREEZE occurred during this resume,
the F1/F2/F4 repair round, the Amendment 3 exact-set repair round, or the
F1-rereview repair round. No Claude CLI, provider-control MCP or automated
Claude call was used to reach the provider at any point — every real HTTP
call this session issued was the same kind a human operator's terminal would
issue directly. Zero files were staged at any point (`git diff --cached`
empty throughout).

## Repair-round disposition

F1 (original), F2, F4, F3 and the F1-rereview finding are now all closed:

- F1 (`COARSE_PERMISSION_ORDERING_REGRESSION`), F2
  (`LIVE_ADMITTED_AUDIT_PROOF_ABSENT`) and F4 (`FOCUSED_MATRIX_GAP`) were
  repaired in the first repair round and re-verified in every subsequent
  round with no regression.
- F3 (`AC32_EXACT_SET_MISMATCH`) was closed by Amendment 3: the BUILD set is
  exactly 74 paths, the changed-path set equals it exactly (verified above),
  and this receipt states that equality throughout rather than "a subset of
  an 82-path ceiling."
- `C3A2-BUILD-REREV-F1 REPORT_APPROVAL_SCOPE_ORDERING_INCOMPLETE` is closed:
  the Report branch's embedded lifecycle 409 in `create_approval_receipt` now
  runs strictly after the shared authority 403 and assignment 404 checks, so
  the exact order for `report.approve` matches every other action in the
  matrix. Proven by a new HTTP regression test asserting 403 → 404 → 409 on
  a single unresolved report with zero receipt/audit writes at each step.

Final state: focused matrix 39/39, full non-live suite 1180/0/116, disposable
PostgreSQL live suite 106/0 (fourth run, after the F1-rereview repair), six
live-evidence scripts verified with no regression (one fresh real receipt
retained unchanged since F2, five verified via `--dry-run`/prior real runs
with reverted receipts), all repository gates PASS, exact 74-of-74 set
equality, zero staged files, zero out-of-set edits, all 8 removed paths
byte-identical to `HEAD`.

`READY_FOR_INDEPENDENT_P2C_C3A2_BUILD_RE_REVIEW`
