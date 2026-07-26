# CVF File-Split Guard Hardening Specification

Status: APPROVED SPECIFICATION — BUILD AWAITS C1/C2 GATES  
Spec ID: `CVF-FSG-SPEC-001`  
Tranche: `CVF-FILE-SPLIT-GUARD-HARDENING-2026-07-26`

## 1. Intended behavior

The repository shall fail automatically when executable source/test files
exceed their hard size limit, unless an unchanged pre-existing debt record
matches the file byte-for-byte.

This specification distinguishes intended guard behavior from the current
implementation, which warns at 300 Python lines but fails only above 400.

## 2. Scope

### 2.1 In scope

- strict executable-code thresholds;
- JavaScript/JSX coverage;
- fail-closed debt-baseline and exception-registry validation;
- digest-bound no-growth legacy debt;
- behavior-preserving split of the seven C3-touched Python files above 300;
- negative tests for bypasses;
- existing validator/hook/CI route verification;
- catalog metric regeneration caused by new helper modules.

### 2.2 Out of scope

- semantic product changes;
- database migrations or schema changes;
- API/OpenAPI changes;
- CVF control-policy changes;
- splitting historical ADR/SPEC/WORK_ORDER documents;
- refactoring legacy oversized code not touched by C3;
- PostgreSQL live verification;
- provider calls or secrets;
- split enforcement based on complexity, token count or generated minified
  assets.

## 3. Normative guard contract

### R1 — thresholds

The strict hard limits are:

- Python: 300 lines;
- TypeScript/TSX/JavaScript/JSX: 200 lines.

Warnings occur at 250 and 160 respectively. Markdown retains 400/600.

### R2 — deterministic line count

Line counting must be deterministic for LF and CRLF content and must not add an
extra phantom line solely because a file ends with a newline. Empty files count
as zero lines.

### R3 — scan boundary

The guard scans repository files with governed suffixes and skips only the
documented build/cache/VCS directories and `__init__.py`. Paths are normalized
to POSIX repository-relative form.

### R4 — debt schema

`docs/reference/FILE_SPLIT_DEBT_BASELINE.json` must exist and parse. It contains
schema version, target limits and unique debt entries with:

`path`, `sha256`, `lineCount`, `hardLimit`, `reason`, `requiredSplit`.

### R5 — debt semantics

For every debt entry:

- path must be normalized, inside the repository and a regular tracked file;
- suffix must be executable and governed;
- current line count must remain above its hard limit;
- recorded hard limit must equal current policy;
- exact SHA-256 and line count must match current content.

Any mismatch fails. A missing oversized executable not in the baseline fails.
A debt entry for a now-compliant or missing file is stale and fails until
removed.

### R6 — exceptions

The exception registry must exist, parse and contain unique normalized paths.
No executable suffix may be excepted. Required fields and positive integer
limits are validated. Directory traversal, absolute paths and missing targets
fail.

### R7 — CLI

Default execution is strict. `--warn` adds warning output but does not weaken
failure behavior. Unknown arguments fail with non-zero status.

### R8 — output

Failures identify the policy surface and path without dumping file contents,
secrets or environment values. Success prints `FILE SIZE GUARD: PASS`.

## 4. Split compatibility contract

### R9 — public facades

Existing import routes and callable names remain valid, including
`workspace_api.application.approval_service` and the public `SqlLedger` and
`InMemoryLedger` classes.

### R10 — behavior preservation

Splits are extraction-only. The following remain byte-/schema-/behavior
compatible where applicable:

- approval receipt scope and digest calculation;
- quorum and self-approval decisions;
- task-creation intent behavior;
- dual-ledger transaction/rollback behavior;
- live-evidence refusal/provider-call cardinality;
- schema parity assertions;
- OpenAPI document and exact response schemas.

### R11 — immediate target

Each of the seven C3-touched oversized Python files named in the ADR must be
300 lines or fewer after BUILD. New helper/test modules must also be compliant.

### R12 — legacy target

Every other current executable file above 300 lines must appear exactly once
in the debt baseline with its post-C2 SHA-256 and line count. The closed set is
exactly:

1. `scripts/generate_catalog.py`
2. `scripts/run_identity_live_governance_evidence.py`
3. `tests/cvf/test_customer_request_vertical.py`
4. `tests/cvf/test_shift_close_governance.py`

No C3-touched or fifth file may be placed in that baseline.

## 5. Acceptance criteria

- **AC-01:** `.py` at 300 passes; 301 fails.
- **AC-02:** `.ts/.tsx/.js/.jsx` at 200 pass; 201 fail.
- **AC-03:** LF/CRLF/final-newline/empty line counts are deterministic.
- **AC-04:** unchanged digest-bound legacy debt passes.
- **AC-05:** same-line-count content edit to legacy debt fails.
- **AC-06:** reduced-but-still-oversized legacy debt fails.
- **AC-07:** debt reduced to compliant size plus stale entry fails until the
  entry is removed; after removal it passes.
- **AC-08:** oversized new/unregistered executable fails.
- **AC-09:** missing/malformed/duplicate/traversal/absolute debt entries fail.
- **AC-10:** missing/malformed/duplicate/traversal/absolute exception entries
  fail.
- **AC-11:** executable exception attempt fails.
- **AC-12:** unknown CLI argument fails; `--warn` cannot turn a failure into
  success.
- **AC-13:** all seven immediate target files and all new executable files are
  within limit.
- **AC-14:** the debt baseline contains only the remaining legacy debt set,
  with independently recomputed SHA-256 and line counts.
- **AC-15:** focused guard negative-test suite passes.
- **AC-16:** P2B focused suite remains 116 passed or increases only by the
  newly split equivalent tests; no test case is silently deleted.
- **AC-17:** root `python -m pytest -q` passes with zero failures/errors.
- **AC-18:** repository validator, session-state, catalog, file-size and
  `git diff --check` pass.
- **AC-19:** CI, pre-commit and repository validator all route to the strict
  default guard, verified read-only; those route files remain byte-identical.
- **AC-20:** public imports, OpenAPI and exact approval response schemas remain
  unchanged.
- **AC-21:** catalog is regenerated only from the generator and contains only
  metric/file-count drift caused by authorized source files.
- **AC-22:** assessment path remains untracked, unstaged, byte-identical and
  outside every commit.
- **AC-23:** no provider call, secret read, PostgreSQL run or governance-AI
  claim occurs.
- **AC-24:** revert rehearsal restores the post-C2 parent tree and the recorded
  test baseline, then cleans the temporary worktree.

## 6. Required negative probes

Tests must use temporary repositories/fixtures and prove at least:

1. new 301-line Python rejection;
2. byte edit with unchanged debt line count rejection;
3. executable exception rejection;
4. malformed JSON fail-closed;
5. missing registry/baseline fail-closed;
6. path traversal rejection;
7. stale baseline rejection;
8. `--warn` does not weaken failure.

The production repository must not be destructively mutated for these probes.

## 7. Evidence boundary

This tranche proves repository file-split enforcement and behavior-preserving
extraction. It does not prove CVF governs AI/agent behavior, so mandatory live
provider evidence is not triggered. No provider call is permitted.

## 8. Review disposition

Independent authorization review: `REVIEW_PASS` after `FSG-AUTH-F1` and
`FSG-AUTH-F2` were repaired without waiver. This specification is normative
for `CVF-FSG-WO-001`.
