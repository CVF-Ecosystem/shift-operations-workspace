# BUILD Evidence Receipt — P2-C C3b2 Mutation Preconditions and CustomerRequest Version

- Work Order: `docs/work_orders/P2C_MUTATION_FULL_UI_C3B2_WORK_ORDER.md`
- Work Order Amendment 1: `docs/work_orders/P2C_MUTATION_FULL_UI_C3B2_WORK_ORDER_AMENDMENT_1.md`
- Authorization reviews: `docs/decisions/P2C_C3B2_WORK_ORDER_AUTHORIZATION_REVIEW.md`,
  `docs/decisions/P2C_C3B2_CEILING_AMENDMENT_1_AUTHORIZATION_REVIEW.md`
- DESIGN addendum: `docs/decisions/ADR_2026-08-01_P2C_C3B2_HANDOVER_RUNNER_TEST_CEILING_ADDENDUM.md`
- SPEC Amendment 10: `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_10.md`
- Pre-BUILD parent (first session): `7b04b72ad5f2fa39208d25424d1df50825d9d022`
- Resume checkpoint (Amendment 1 session): `ab235ff3766f1775cffe07976f7e641d9ef3f3b0`
- First independent BUILD review: `REVIEW_CHANGES_REQUIRED` — 5 findings
  (`C3B2-BUILD-REV-F1..F5`), all repaired in the prior repair round
- Second independent BUILD re-review: `REVIEW_CHANGES_REQUIRED` — 1 residual
  finding (`C3B2-BUILD-REREV-F1`), repaired in this round
- Worker role: `REPAIR_WORKER` (external, manually prompted; no Claude CLI/MCP)
- Status: `REPAIR COMPLETE — NOT STAGED, NOT COMMITTED, NOT REVIEWED, NOT FROZEN`

## 1. History: blocker, Amendment 1, first review (F1-F5), second review (residual F1)

The original 82-path BUILD stopped correctly on an out-of-ceiling blocker;
Amendment 1 raised the ceiling to exactly 83 and required a runner-helper
fix. A first repair pass made that fix and reported BUILD-complete. An
**independent BUILD review** returned `REVIEW_CHANGES_REQUIRED` with five
semantic findings (`C3B2-BUILD-REV-F1..F5`): runner fixed-version literals,
`ShiftService.close`/`.freeze` transaction-unit splits, invalid
version/status admission at direct-service boundaries, and
admission-before-lookup ordering drift in handover/report services. A
**second repair pass** closed all five with source-level, same-unit, and
ordering proof tests, and rewrote the BUILD receipt accordingly.

A **second independent BUILD re-review** returned `REVIEW_CHANGES_REQUIRED`
again, with exactly **one residual finding**:

- **C3B2-BUILD-REREV-F1 `STATUS_STRING_COERCION_ADMITTED`** — the F4 repair
  (invalid version/status admission) hardened `assert_status_precondition`
  to reject non-members via a `try: status_type(expected_status) except
  (ValueError, TypeError)` construction check. That check was **insufficient**:
  `ReportStatus` (and every domain status enum in this codebase) is a
  `StrEnum`, whose constructor is deliberately permissive — `ReportStatus("DRAFT")`
  succeeds and returns a real `ReportStatus.DRAFT` member even though the
  caller only ever held a plain `str`. The F4 repair's own test matrix never
  probed a valid-looking string like `"DRAFT"`/`"APPROVED"` (it used
  `"MADE_UP_STATUS"`, which correctly fails construction), so the gap
  survived a fully-green test run. A direct-service caller could therefore
  still pass a raw string and have it silently admitted as if it were a
  genuine enum member the caller actually held.

This receipt documents the repair of that one residual finding, performed in
this round without adding, removing, or otherwise touching any path outside
the exact 83-path ceiling.

## 2. Repair detail — C3B2-BUILD-REREV-F1

### 2.1 `mutation_preconditions.py`

`assert_status_precondition` no longer constructs `status_type(expected_status)`.
It now requires `isinstance(expected_status, status_type)` — a genuine
runtime type check, not a coercing constructor call. `isinstance` has no
"looks like a valid string" leniency: a `str`, `int`, `bool`, `float`, or a
member of an *unrelated* enum type (even one that also subclasses `StrEnum`
and happens to share a string value) all fail the check and are refused with
a controlled 422. Only a value whose runtime type is `status_type` itself
proceeds to the `!=` staleness comparison (409 on mismatch). The docstring
was rewritten to state the exact mechanism and cite the specific coercion
gap this closes. File remains 108 physical lines (well under the 300-line
hard limit).

### 2.2 Real regression found and fixed: `scripts/run_report_live_governance_evidence.py`

Running the full non-live suite after the `mutation_preconditions.py` fix
surfaced three genuine test failures in
`tests/integration/test_report_live_evidence_runner.py` (not a false
positive — the isinstance tightening correctly caught a real caller passing
a raw string at the direct-service boundary). The runner script's
`check_report_freeze_gate`'s `_non_current_submit_review` scenario called
`ReportService(ledger).create_successor(...)` **directly** (not through
HTTP) with `expected_status="DRAFT"` — a plain string, never a genuine
`ReportStatus` member. Under the old permissive coercion this silently
"worked"; under the corrected `isinstance` check it now correctly, and
truthfully, requires a real enum value. The fix threads a genuine
`ReportStatus.DRAFT` import into that call site instead of the string
literal. This is a real fix to a real caller, not a change to the
precondition semantics — the two module-level HTTP helper functions
(`_submit_review`/`_approve`) in the same file keep their string defaults
(`"DRAFT"`/`"IN_REVIEW"`) unchanged and correctly, because those strings
travel through `client.post(json=body)` into the FastAPI/Pydantic HTTP
boundary, which already parses the raw JSON string into a genuine
`ReportStatus` enum member before it ever reaches
`assert_status_precondition` — confirmed by direct inspection of both call
shapes and by the passing HTTP-level tests in the same file. File remains
299 physical lines.

A repo-wide grep for other direct-service `expected_status="..."` string
literals (excluding HTTP JSON body construction) found no further instances.

### 2.3 Focused tests added — `tests/cvf/test_report_approval.py`

The prior repair round's F4 status-invalidity matrix
(`test_report_direct_service_call_with_invalid_expected_status_is_422`,
which lived in `tests/cvf/test_c3b2_mutation_preconditions.py`) is removed
from that file (replaced with a one-line pointer comment) and superseded by
a complete matrix in `test_report_approval.py`, the Report-specific
precondition-ordering test host from the prior repair round:

- `test_submit_review_invalid_expected_status_is_422_leaves_state_unchanged`,
  parametrized over `["DRAFT", "APPROVED", None, 1, True, 1.0, ShiftStatus.OPEN]`
  — covers: valid-looking raw strings (the exact re-review gap), missing,
  int, bool, float, and a genuine member of an **unrelated** enum type
  (`ShiftStatus`, not `ReportStatus`). Each case asserts 422, the Report
  stays `DRAFT` at its original version, and no `report.submit_review` audit
  entry was appended (the pre-existing `report.generate` entry from setup is
  explicitly excluded from the assertion, not asserted away as "zero
  entries" — a bug in an earlier draft of this test was caught and fixed
  during this repair by re-running and reading the failure diff before
  finalizing).
- `test_submit_review_genuine_current_expected_status_is_admitted` — a
  genuine `ReportStatus.DRAFT` (matching current stored status) is admitted
  and the transition to `IN_REVIEW` succeeds.
- `test_submit_review_genuine_but_stale_expected_status_is_409_leaves_state_unchanged`
  — a genuine `ReportStatus.APPROVED` (a real enum member, but not the
  current `DRAFT` status) is a controlled 409, with the Report/audit state
  left exactly as before.

`tests/cvf/test_c3b2_mutation_preconditions.py`: 292 lines (was 300; the
5-case invalid-status test removed, replaced with a 3-line pointer comment
per the file-size ceiling, since the file was already at the exact 300-line
limit and the fuller matrix belongs with the other Report-specific
precondition tests). `tests/cvf/test_report_approval.py`: exactly 300 lines
after adding the three-test matrix and condensing existing content
(single-line imports/bodies, comment-form docstrings, a shared `client`
fixture reused instead of manual `TestClient`/`dependency_overrides`
duplication, and folding the two multi-line `report_snapshot.build_snapshot(...)`
probe-test calls to single lines) — net functional test count in this file
rose from 27 (post-first-repair) to 35.

`python -m pytest -q tests/cvf/test_c3b2_mutation_preconditions.py
tests/cvf/test_report_approval.py` → **64 passed** (29 + 35).

## 3. Exact changed-set proof — 83/83, zero outside, zero staged

Mechanically re-verified after this repair: extracting every `` `path` ``
entry from the Work Order's numbered list plus Amendment 1's addition,
sorting, and diffing against `git status --porcelain`. `comm -23`/`comm -13`
both returned empty — **exactly 83/83, zero outside, zero missing.**
`git diff --cached --stat` was empty at every checkpoint in this repair
session, including immediately before writing this receipt. HEAD remained
`ab235ff3766f1775cffe07976f7e641d9ef3f3b0` throughout (equal to
`origin/main` at session start, unchanged by any operation performed).

## 4. Required order and evidence — fresh post-repair counts

### 4.1 Focused C3b2 + repair-round suites

```bash
python -m pytest -q tests/cvf/test_c3b2_mutation_preconditions.py tests/integration/test_customer_request_version_parity.py tests/unit/test_c3b2_mutation_openapi_contract.py tests/integration/test_handover_live_evidence_runner.py tests/cvf/test_report_approval.py tests/cvf/test_shift_close_governance.py tests/cvf/test_shift_close_freeze_interaction.py tests/cvf/test_handover_vertical.py
```

**143 passed.**

### 4.2 Full Python non-live suite

```bash
python -m pytest -q
```

**1314 passed, 127 skipped.** (An intermediate run, before the
`scripts/run_report_live_governance_evidence.py` fix in section 2.2 above,
showed 4 failures — 1 expected catalog staleness resolved by
`generate_catalog.py --write`, and 3 genuine regressions in
`test_report_live_evidence_runner.py` that were investigated, root-caused to
a real direct-service string-literal caller, and fixed. The count above is
the fresh, fully clean rerun after that fix, not a stale or cherry-picked
number.)

### 4.3 Frontend gates (Node/pnpm, frozen lockfile)

```bash
pnpm --dir apps/workspace-web install --frozen-lockfile   # Done, no lockfile drift
pnpm --dir apps/workspace-web run typecheck                # clean, zero errors
pnpm --dir apps/workspace-web test                          # 3 files, 31 passed
pnpm --dir apps/workspace-web run build                     # tsc -b && vite build succeeded
```

No frontend path changed in this repair round (the residual finding is
entirely backend Python); these gates were rerun per the required order and
confirmed identical to prior counts. Generated
`apps/workspace-web/tsconfig.tsbuildinfo` was removed after the gate
sequence; confirmed absent before writing this receipt.

### 4.4 Disposable PostgreSQL 16, migration reapply, exact cleanup

```bash
python scripts/run_postgres_live_roundtrip.py --json
```

- `container_name`: `cvf-pg-live-d84475c4d3ed` (freshly generated this run,
  uniquely named, loopback-only, no bind mount)
- Migrations first application: **29 applied, 0 skipped**
- Migrations reapply (idempotency proof): **25 applied, 4 skipped**
- Live suite: **117 passed** across the eleven coherent live modules
- `container_absent_after_cleanup`: `true`
- `anonymous_volumes_still_present`: `[]`
- `failure`: `null`

Pre-existing unrelated Docker containers (`quanlyxalan-dashboard-pg-20c187f`,
`cangvu-test-pg`, `vierp-accounting`) were verified present and unchanged
(`docker ps -a`) both before and after this run — same three containers,
same status, byte-identical listing.

### 4.5 Repository, catalog, session, file-size, JSON, diff gates

```bash
python scripts/generate_catalog.py --write   # 20 modules, 12413 LOC
python scripts/check_session_state.py        # SESSION STATE: PASS
python scripts/generate_catalog.py --check   # CATALOG VERIFY: PASS
python scripts/check_file_size.py            # FILE SIZE GUARD: PASS
python scripts/testing/validate_repository.py  # repository validation passed
git diff --check                             # exit 0 (only CRLF-normalization warnings, no conflict markers/trailing whitespace)
python -c "import json; json.load(open('docs/catalog/MODULE_REGISTRY.json'))"  # JSON VALID
```

Workspace doctor:

```bash
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```

**RESULT: PASS WITH NOTE (24 passed, 1 warning(s))** — sole warning is the
pre-existing bounded `LEGACY_PROJECT` governed-catalog-kit note, unrelated to
C3b2 and present in every prior closed tranche's doctor run.

### 4.6 AC-29 isolated exact-parent rehearsal

A detached temporary worktree was created at the exact resume-checkpoint
parent `ab235ff3766f1775cffe07976f7e641d9ef3f3b0` (clean, zero diff at
creation). Inside that isolated worktree:

```bash
python -m pytest -q                            # 1238 passed, 120 skipped
python scripts/testing/validate_repository.py  # repository validation passed
```

This matches the exact pre-BUILD baseline carried forward unchanged since
the Amendment 1 resume checkpoint, confirming the rehearsal parent is
genuinely unmodified by this repair round. The temporary worktree was then
removed (`git worktree remove --force`); `git worktree list` afterward shows
only the primary working tree. The primary working tree's changed-file count
(83), HEAD, and zero-staged state were reconfirmed unchanged after cleanup.

## 5. Zero staged files, no provider call

`git diff --cached --stat` was empty at every checkpoint in this repair
session, including immediately before writing this receipt. No provider
(Alibaba or otherwise) was called at any point — the residual finding is a
backend type-validation defect with no provider surface. No Claude CLI or
MCP delegation occurred; this worker was manually prompted per the
operator's external-worker protocol.

## 6. Bounded nonclaims

This repair proves only:

- `C3B2-BUILD-REREV-F1` is closed: `assert_status_precondition` now requires
  a genuine `isinstance` match against the current status's exact enum type,
  never a coerced/constructed value, verified by a focused test matrix that
  specifically includes the valid-looking-string case the prior matrix
  missed, plus a positive control (genuine current member admitted) and a
  genuine-but-stale control (409, not 422).
- One real regression this fix exposed
  (`scripts/run_report_live_governance_evidence.py`'s direct-service string
  literal) is fixed at its actual call site, not worked around by weakening
  the precondition check.
- Everything proven by the prior BUILD receipt (CustomerRequest version/CAS,
  the eight-route precondition matrix, F1-F5 transaction/ordering repairs,
  OpenAPI zero-delta, frontend `CustomerRequest.version`) remains true and
  was reconfirmed by the fresh full-suite/PostgreSQL/frontend/AC-29 evidence
  in this round — none of it was contradicted or required re-derivation.

This repair does **not** prove, and none of the evidence above should be
read as proving:

- Any React mutation UI, C3c operator UI, or C3d supervisor closeout UI —
  none exists yet.
- Tenant or provider `data_scope` enforcement.
- Production or managed PostgreSQL readiness — the PostgreSQL evidence above
  is bounded to a disposable local container.
- Any new AI/agent-governance claim, or any provider call — none occurred
  and none was required.
- Offline queue or realtime behavior (P2-D) — unaffected and untouched.
- P2-C completion or Phase 2 completion — C3c and C3d remain unauthorized
  and unbuilt.
- That the two pre-existing `extra=forbid`-lacking inputs (`EventInput`,
  `CustomerRequestInput`) were changed or "fixed" — they remain unrelated,
  pre-existing, and byte-identical in that respect.
- That every conceivable coercion/validation gap in the codebase is now
  closed — only the one residual finding the independent re-review actually
  named was investigated and repaired, plus the one real regression that
  fix's own full-suite rerun exposed; this receipt does not claim a broader
  audit of every enum/type boundary in the codebase occurred.

## 7. Return

All Work Order, Amendment 1, first-review repair, and second-review repair
requirements above are satisfied. Zero files staged. No commit, push,
self-review, or FREEZE occurred. No path outside the exact 83-path ceiling
was edited in the final state.

`READY_FOR_INDEPENDENT_P2C_C3B2_BUILD_RE_RE_REVIEW`
