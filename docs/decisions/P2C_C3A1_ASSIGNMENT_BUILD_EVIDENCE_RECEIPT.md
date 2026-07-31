# P2C-C3A1 Assignment/Staffing Foundation — BUILD Evidence Receipt

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Amended ceiling: exactly **53 paths** (48 original + 2 legacy live-runner
  repairs [Amendment 1] + 3 F1-amendment test-split companions [Amendment 2])
- Status: `INDEPENDENT_FINAL_REVIEW_PASS — READY_FOR_COMMIT_STEWARD`

## History

1. Original G6 (parent `00e16f5000521f30b9f655128d049be25508f7c2`) passed;
   BUILD hit a real ceiling conflict and correctly stopped with
   `BLOCKED_WORK_ORDER_CEILING`.
2. Amendment 1 (`REVIEW_PASS`) added exactly two legacy live-runner script
   paths, making the 50-path ceiling. BUILD resumed from checkpoint
   `f73f13a7f75d0ad852af09d3a4e1014351cdabc1` and reached
   `READY_FOR_INDEPENDENT_P2C_C3A1_BUILD_REVIEW` with: focused **53 passed**;
   full non-live **1071 passed, 95 skipped**; disposable PostgreSQL 16 live
   **85 passed** (migrations 24/0 then 20/4, exact cleanup); fresh live
   governance evidence PASS. These pre-repair-round-1 counts are historical
   only, not current proof.
3. **Independent BUILD review round 1 returned `CHANGES_REQUIRED`**, finding
   three real defects (F1, F2, F3). BUILD repaired all three (missing-
   reference prevalidation both backends, missing/non-numeric `exp` →
   controlled `TokenError`, atomic CAS revoke), reaching **64 passed**
   focused / **1084 passed, 100 skipped** full non-live / **90 passed**
   disposable PostgreSQL, and returned
   `READY_FOR_INDEPENDENT_P2C_C3A1_BUILD_RE_REVIEW`. These round-1-repair
   counts are also historical only, not current proof.
4. **Independent BUILD review round 2 returned `CHANGES_REQUIRED`** on that
   repair, finding the round-1 F1/F2 fixes were each incomplete:
   - **F1 residual gap:** reference prevalidation did not make duplicate-
     active the only constraint capable of failing during INSERT. A
     primary-key collision on `assignment_id` (e.g. a previously revoked
     assignment's id reused) was still possible; InMemory accepted it and
     silently overwrote history, and SQL's blanket `except IntegrityError`
     mislabeled it as `"duplicate active assignment..."` — the WRONG,
     conflated error. The round-1 receipt's claim that prevalidation made
     duplicate-active "the only remaining path that can still raise from
     the insert itself" was **false**; corrected in the round-2 repair
     below.
   - **F2 residual gap:** `exp` validation accepted every int/float and
     called `datetime.fromtimestamp(exp, tz=timezone.utc)` unconditionally.
     A platform-unrepresentable numeric `exp` (`10**30`, `1e100`, `inf`)
     raised an uncaught `OverflowError`, still reaching `/auth/me` as HTTP
     500 instead of a controlled 401.
   - F3 (atomic CAS revoke) was **accepted as closed** and explicitly not
     reopened except for regressions caused by the F1/F2 residual repairs
     (none occurred, in round 2 or round 3).
5. BUILD repaired both round-2 residual gaps, but the required new test
   coverage pushed three existing test files (`test_assignment_foundation.py`,
   `test_assignment_ledger_parity.py`, `test_assignment_postgres_live.py`)
   past the 300-line `.py` hard file-size limit, which has no exception-
   registry path for executables. The worker's own `git status --short`
   count in the moment read as 49/50 (1 free slot, 3 needed) and BUILD
   stopped with `BLOCKED_WORK_ORDER_CEILING` on that basis. **That 49/50
   figure was itself imprecise** — `git status --short`'s single `??` line
   for the untracked `apps/workspace-api/src/workspace_api/api/staffing/`
   directory aggregates two real files (`__init__.py` and `router.py`) into
   one displayed line. An independent expanded inventory (directory markers
   expanded to individual files, `__pycache__` excluded) proved the tranche
   was actually at **exactly 50/50 paths**, not 49/50, at that point. The
   ceiling-conflict block correctly identified real unmet need (3 new paths
   for 3 oversized files with no other compliant option) regardless of
   whether the free-slot count reported in the moment was 0 or 1 — this
   receipt no longer repeats the imprecise 49/50 figure as repository truth
   anywhere.
6. **Work Order Amendment 2** (reviewed, approved, committed, pushed;
   resume checkpoint `a5dd51ead9215a922ddb2ccc7355aa4ba971d46b`, verified
   `HEAD == origin/main` at BUILD resume) raised the ceiling to exactly 53
   paths (the verified 50 plus exactly 3), authorizing exactly three new
   companion files: `tests/cvf/test_assignment_foundation_f1.py`,
   `tests/integration/test_assignment_ledger_parity_f1.py`,
   `tests/integration/test_assignment_postgres_live_f1.py`. BUILD moved the
   accepted F1/F2 tests into those companions, reran every gate, and
   regenerated fresh live evidence.
7. **Independent BUILD review round 3 returned `CHANGES_REQUIRED`** on that
   repair, finding one further real defect:
   - **F4 — invalid lifecycle not controlled or backend-equivalent:** SPEC
     R3 requires invalid-lifecycle failures to use controlled, backend-
     equivalent errors with no partial write. A `ShiftAssignment` mutated
     after construction (`assignment.status = "NOT_A_REAL_STATUS"`) was
     accepted and stored verbatim by InMemory (no equivalent constraint
     existed there at all) while SQLite raised a raw, unclassified
     `sqlalchemy.exc.IntegrityError` straight through `add_assignment` —
     neither controlled nor equivalent across backends. Also flagged: the
     existing live-PostgreSQL CHECK-constraint tests used a raw
     `conn.execute`, which proves the migration's CHECK constraint exists
     but does NOT exercise `add_assignment` or
     `_classify_assignment_insert_conflict` at all.
   - Independently reported alongside F4, as governance/session-continuity
     drift rather than a BUILD finding: the Amendment-2 resume checkpoint
     had accidentally left `SESSION/SESSION_MEMORY.md` at 601/600 lines
     (1 over the `.md` hard limit), which is why `check_file_size.py` and
     `scripts/testing/validate_repository.py` reported a FAIL in the
     round-2 receipt even though every C3a1-owned path was compliant.
     Codex, acting as governance/session steward (not this BUILD worker),
     repaired only that one continuity file in commit
     `9520c57359a6dd7fddb8a665e2cf159c8b326a9a` — a session/governance-layer
     fix outside this worker's BUILD scope, touching no path in the 53-path
     C3a1 ceiling and not altering that ceiling. BUILD resumed from that
     commit as its required parent (verified `HEAD == origin/main` at
     round-3 resume) and both gates now report clean file-size/validator
     results — see "Repository gates" below.
8. BUILD repaired F4 (this receipt, round 3) strictly inside the existing
   53-path ceiling — no new path was needed, since the fix and its test
   coverage fit inside files already in the changed set — reran every gate,
   the full disposable PostgreSQL suite (including the two new F4
   real-PostgreSQL tests), and regenerated fresh live governance evidence
   because runtime assignment validation changed again. This receipt
   records that round-3 repair and its fresh counts truthfully.
9. **Independent BUILD review round 4 returned `CHANGES_REQUIRED`** after
   proving the F4 field checks still admitted impossible combinations:
   direct `add_assignment` accepted REVOKED/version 1, ACTIVE/version 2 and
   ACTIVE rows carrying revoke metadata. Those states cannot be produced by
   the governed lifecycle: creation starts ACTIVE/version 1 without revoke
   metadata, and only `revoke_assignment` derives the revoked state.
10. At the operator's explicit request, Codex transitioned to
    `REPAIR_WORKER` and closed F5 inside the existing 53 paths. No Claude CLI,
    staging, commit, push, self-review or FREEZE occurred during this repair.
    The final evidence below supersedes round 3 while preserving its counts
    as historical evidence.
11. The operator authorized a fresh Codex sub-agent as an independent,
    read-only reviewer. It returned `CHANGES_REQUIRED`: mutable required
    fields (`assignment_id=None`, `assigned_at=None`) still produced InMemory
    acceptance versus raw SQL NOT NULL errors; AC-29 exact-parent rehearsal
    was absent; and the receipt named the wrong doctor entrypoint.
12. Codex `REPAIR_WORKER` closed F6 with complete strict domain revalidation,
    added parity/live tests, ran the missing exact-parent rehearsal, used the
    correct doctor command and regenerated every final evidence surface. The
    same independent reviewer must re-review before commit/push.

## F4 repair (round 3)

### F4 — invalid lifecycle shape rejected identically on both backends

- `packages/operations-domain/src/operations_domain/assignment_models.py`
  (62 lines): new `assert_assignment_lifecycle_valid(assignment)` — pydantic
  does NOT re-validate a model's own fields on plain attribute assignment
  (`assignment.status = "X"`) unless `model_config = ConfigDict(
  validate_assignment=True)` is set, which it isn't here (matching every
  other domain model in this codebase). The function checks `status` is a
  real `AssignmentStatus` member (`ACTIVE`/`REVOKED`) and `version` is a
  non-bool `int >= 1`, raising a controlled `ValueError` naming the exact
  invalid field. Both backends call this SAME function, so an invalid
  lifecycle shape is rejected identically everywhere, before either backend
  attempts any write.
- `apps/workspace-api/src/workspace_api/infrastructure/_assignment_repository.py`
  (InMemory, 128 lines): `add_assignment` now calls
  `assert_assignment_lifecycle_valid(assignment)` first, before the
  reference checks and before any dict write.
- `packages/operations-ledger/src/operations_ledger/_assignment_store.py`
  (SQL, 247 lines): `add_assignment` now calls
  `assert_assignment_lifecycle_valid(assignment)` before opening a
  connection at all (a pure in-Python check needs no transaction), so an
  invalid lifecycle shape never reaches the reference prevalidation, the
  INSERT, or `_classify_assignment_insert_conflict`. The classifier itself
  is unchanged and unaffected: it still only ever sees a genuine PK or
  partial-unique-index `IntegrityError`, since a lifecycle-invalid row can
  no longer reach the INSERT to trip anything else. Duplicate-assignment_id
  and duplicate-active classification (F1) remain fully distinct and
  unregressed — confirmed by rerunning every F1 test in this round (see
  below).
- The migration's own CHECK constraints (`shift_assignments_status_check`,
  `shift_assignments_version_check`) are unchanged and remain in place as
  defense in depth for any caller that bypasses `add_assignment` entirely
  (e.g. a raw `conn.execute` against the table directly).
- New coverage (parity, both backends, in
  `tests/integration/test_assignment_ledger_parity_f1.py`):
  `test_invalid_status_is_controlled_and_equivalent_both_backends`,
  `test_version_below_one_is_controlled_and_equivalent_both_backends`,
  `test_invalid_lifecycle_rejection_leaves_no_partial_write`,
  `test_backend_remains_usable_after_invalid_lifecycle_rejection` — proving,
  parametrized across `in_memory`/`sql`: (1) invalid status controlled and
  equivalent, (2) version below one controlled and equivalent, (3) no
  partial write from either failure, (4) the backend accepts a subsequent
  valid assignment afterward.
- New coverage (real PostgreSQL, in
  `tests/integration/test_assignment_postgres_live_f1.py`):
  `test_live_add_assignment_rejects_invalid_status_before_reaching_insert`
  and `test_live_add_assignment_rejects_version_below_one_before_reaching_
  insert` — both drive `sql_ledger.add_assignment(...)` (the real ledger
  path), NOT a raw `conn.execute`, proving the SAME controlled
  invalid-status/version `ValueError`, no partial write, and (for the
  version case) that the backend accepts a subsequent valid assignment
  afterward. The two PRE-EXISTING raw-`conn.execute` CHECK-constraint tests
  in `test_assignment_postgres_live.py`
  (`test_assignment_status_outside_check_constraint_rejected`,
  `test_assignment_version_below_one_rejected_by_live_database_check`) are
  retained, unchanged, honestly as CHECK-constraint-only proof (their names
  already said exactly that) with an added one-line comment pointing to the
  real ledger-path tests above and stating explicitly that they do not
  exercise `add_assignment` or the classifier — no claim was ever made, and
  none is made now, that a raw-INSERT test proves classifier passthrough.

## F5 repair — coherent creation state

`assert_assignment_lifecycle_valid` now validates the `add_assignment`
creation boundary as one coherent state, not merely independent field types.
Only ACTIVE/version 1 with absent `revoked_by` and `revoked_at` is accepted.
The canonical model can still represent stored REVOKED history, but only
`revoke_assignment` may produce and persist that state.

The InMemory/SQLite companion adds ten parametrized cases covering direct
REVOKED/version 1, direct well-formed-looking REVOKED/version 2, ACTIVE/version
2, ACTIVE with revoked actor and ACTIVE with revoked timestamp. Every case
proves controlled rejection, zero partial rows and a subsequent valid add.
The PostgreSQL companion adds the same five cases through the real ledger
path.

## F6 repair — strict complete-record validation

After the lifecycle/coherence checks, the persistence boundary now strictly
revalidates the complete mutable `ShiftAssignment` record through its
canonical Pydantic model. Validation errors are converted to a controlled
field-naming `ValueError` before either backend writes. This closes the
independently reproduced `assignment_id=None` and `assigned_at=None` parity
gap and also protects every other required canonical field from post-
construction mutation.

Four InMemory/SQLite parametrized cases and two real-PostgreSQL cases prove
both reproduced fields are rejected equivalently, leave no partial row and
permit a subsequent valid add. The SQL NOT NULL/type constraints remain
defense in depth for callers bypassing the ledger boundary.

## Test-file split (Amendment 2, exactly 3 new companion paths — unchanged in round 3)

The F1/F2 residual-gap test coverage in round 2 pushed three existing files
past the 300-line `.py` hard limit. Per Amendment 2, the accepted tests were
moved (not duplicated, not weakened) into three new companions. Round 3's
F4 coverage was added inside these same six files (no new path needed):

- Host `tests/cvf/test_assignment_foundation.py` (292 lines) → companion
  `tests/cvf/test_assignment_foundation_f1.py` (84 lines): the two F2
  `/auth/me` HTTP regressions (missing-exp, huge-numeric-exp), plus one
  net-new HTTP regression for non-finite/boolean exp (inf/-inf/nan/bool →
  401), same `client` fixture pattern. Untouched in round 3.
- Host `tests/integration/test_assignment_ledger_parity.py` (249 lines) →
  companion `tests/integration/test_assignment_ledger_parity_f1.py`
  (196 lines, round 3): the four F1-amendment duplicate-assignment_id
  parity tests, plus four new F4 invalid-lifecycle parity tests (round 3);
  imports `_backends`/`_shift`/`_user` from the host rather than
  duplicating them.
- Host `tests/integration/test_assignment_postgres_live.py` (300 lines,
  round 3 — one clarifying comment added, module docstring trimmed by an
  equal amount to stay exactly at the limit) → companion
  `tests/integration/test_assignment_postgres_live_f1.py` (158 lines,
  round 3): the three F1-amendment real-PostgreSQL tests, plus two new F4
  real-ledger-path tests (round 3); imports the host's
  `live_database_url`/`sql_ledger` fixtures and `_shift`/`_user` helpers.

No test body, assertion, or parametrization was deleted, weakened, or
replaced with prose to fit any limit in any round — only docstrings/comments
were tightened (verbatim assertions preserved) and the split itself. The
`scripts/run_postgres_live_roundtrip.py` (300 lines) and
`tests/integration/test_postgres_live_runner.py` (300 lines) changes from
Amendment 2 (wiring the eighth live module in and its pinned-module-list
test) are unchanged in round 3.

## Exact changed-path inventory (53-path amended ceiling)

Independent expanded inventory (directory markers expanded to individual
files, `__pycache__` excluded) proved the tranche was at **exactly 50/50
paths before Amendment 2** — see step 5 above for why the worker's own
in-the-moment `git status --short` read as 49/50. Amendment 2 added exactly
three new paths on top of that verified 50, for the current 53-path
ceiling. F4 (round 3) added zero new paths — every change fit inside the
53 already authorized. `git status --porcelain --untracked-files=all`
(directory markers expanded, `__pycache__` excluded) shows **exactly 53
paths**, 0 staged, matching the ceiling with set-equality — no path touched
outside the authorized 53.

## Final post-repair verification (fresh Codex REPAIR_WORKER reruns)

### Expanded focused C3a1 suite

```
python -m pytest -q tests/unit/test_assignment_model.py tests/unit/test_assignment_openapi_contract.py tests/cvf/test_assignment_foundation.py tests/cvf/test_assignment_foundation_f1.py tests/integration/test_assignment_ledger_parity.py tests/integration/test_assignment_ledger_parity_f1.py tests/integration/test_schema_parity_assignments.py tests/cvf/test_auth_tokens.py
```

Result: **121 passed** (117 before F6; +4 strict required-field parity cases,
zero regressions).

### Full non-live regression

```
python -m pytest -q
```

The F5 first run truthfully failed only the expected generator-owned catalog
drift test: **1122 passed, 110 skipped, 1 failed**. After each final source
repair the authorized catalog generator was refreshed. The final F6 complete
rerun returned **1127 passed, 112 skipped**, zero failures and zero
regressions.

### Repository gates (final repair, fresh — all PASS)

- `check_session_state.py`: **PASS**.
- `generate_catalog.py --check`: **PASS** (20 modules, metrics/Markdown
  current — regenerated via `--write` after F4's new code/test lines, then
  reverified via `--check`).
- `check_file_size.py`: **PASS**. The round-2 receipt's FAIL was
  `SESSION/SESSION_MEMORY.md` at 601/600 lines, a pre-existing governance/
  session-continuity file outside the 53-path C3a1 changed set. That file
  was repaired (back to compliant) by Codex as governance/session steward
  in commit `9520c57359a6dd7fddb8a665e2cf159c8b326a9a`, this round's
  required resume parent — not by this BUILD worker and not by touching any
  C3a1-owned path. With that repair in place, the gate now reports a clean
  PASS with zero exceptions.
- `scripts/testing/validate_repository.py` (correct path; this receipt does
  not claim `testing/validate_repository.py` alone was run — the invocation
  used throughout this round was the full repo-relative path above): **PASS**
  — `repository validation passed (catalog + session state + file-size
  checks)`, zero errors.
- `git diff --check`: **clean** (exit 0).
- CVF workspace doctor used the correct project entrypoint,
  `powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1`:
  **PASS WITH NOTE (24 passed, 1 bounded legacy warning)** and
  `FRESH_CLONE_CONTINUITY_PASS`. The prior receipt text naming a sibling
  `scripts/doctor.ts` was incorrect and is superseded here.
- `.py` module file-size check (informational, all ≤300, final figures):
  `_assignment_store.py` 247 lines; `_assignment_repository.py` 128 lines;
  `assignment_models.py` 88 lines; `test_assignment_ledger_parity_f1.py`
  251 lines; `test_assignment_postgres_live_f1.py` 214 lines;
  `test_assignment_postgres_live.py` 300 lines (exactly at the limit).

### Disposable PostgreSQL 16 live suite (final repair, fresh)

- Migrations: **first 24 applied/0 skipped**, **reapply 20 applied/4
  skipped** (unchanged shape — no migration file changed in round 3).
- Live suite runner (all 8 coherent modules, including
  `test_assignment_postgres_live_f1.py`): **PASS** with
  `live_suite_returncode: 0`, including the F5/F6 PostgreSQL cases,
  `test_concurrent_revoke_exactly_one_winner_and_exactly_one_audit` (F3,
  unchanged, no regression) and every F1 duplicate-assignment_id/
  duplicate-active classification test (unregressed by the F4 lifecycle
  check now running earlier in `add_assignment`).
- Container `container_absent_after_cleanup: true`; anonymous volume
  captured (`9dfadc6af3df5bc498e92ee0285a674b2af9582fe375d0c707bfd65fc3001fb8`)
  and confirmed removed (`anonymous_volumes_still_present: []`); Docker
  volume count before and after this round's run: **12**, unchanged — no
  pre-existing container/volume touched.

### Live governance evidence (final repair, fresh)

See `docs/decisions/P2C_C3A1_ASSIGNMENT_LIVE_EVIDENCE_RECEIPT.md`,
regenerated **after** the F6 runtime repair (timestamp
`2026-07-31T15:37:03Z`, superseding every prior receipt of the same name).
Summary: 3 refusal cases at zero provider calls; one genuine
durable staffing assignment plus exact-field-matched actor-bound audit
verified; then exactly one real Alibaba `qwen3.7-max` call returned HTTP
200.

### AC-29 exact-parent rollback rehearsal

A temporary detached worktree at the true final BUILD parent
`9520c57359a6dd7fddb8a665e2cf159c8b326a9a` started clean and returned
**998 passed, 87 skipped**. Session, catalog, file-size, repository validator
and diff gates all passed. The worktree was removed and pruned; its exact path
was confirmed absent afterward. The candidate working tree retained exact
53/53 membership and zero staged paths.

### Independent final review disposition

An operator-authorized, read-only Codex reviewer independent of the F5/F6
implementation returned `REVIEW_PASS` after first finding and then verifying
closure of F6, AC-29, the doctor entrypoint and the final control-mapping
drift. Its final inspection reconfirmed exact 53/53 membership, zero staged
or outside paths, clean diff and PASS for session/catalog/file-size/repository
gates. Commit/push is therefore permitted only in the separate
`COMMIT_STEWARD` role; C3a2 remains unauthorized pending its own Work Order.

## Claim boundary

Unchanged from the Work Order section 8 and from every prior receipt: C3a1
proves only a single-workspace assignment persistence/staffing foundation,
advisory session/capability reads, and atomic creator assignment for newly
created shifts on the proven backends — now additionally proven to reject
missing references, to correctly distinguish duplicate-assignment_id from
duplicate-active-assignment (never conflating the two, never overwriting
history, on both backends and real PostgreSQL), to convert every
non-finite/out-of-range/malformed `exp` claim into a controlled 401 (never
500), to resolve concurrent revoke races to exactly one winner with exactly
one audit record, and to reject invalid fields, mutated required canonical
fields and impossible creation-state combinations identically with no partial
write on both backends and real PostgreSQL through the real ledger path. It
does NOT prove
existing operational routes are assignment-scoped (C3a2), tenant isolation,
provider `data_scope`, fixed-token early revocation, production PostgreSQL
readiness, frontend mutation, P2-C completion, P2-D, or Phase-2 completion.
