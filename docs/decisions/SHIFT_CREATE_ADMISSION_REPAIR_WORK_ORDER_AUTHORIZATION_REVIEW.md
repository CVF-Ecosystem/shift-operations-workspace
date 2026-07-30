# Independent Authorization Review — Shift Create Admission Repair Work Order

- Review id: `SHIFT-CREATE-ADMISSION-REPAIR-WO-AUTH-REVIEW-001`
- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Date: 2026-07-30
- Risk: R2
- Work Order:
  `docs/work_orders/SHIFT_CREATE_ADMISSION_REPAIR_WORK_ORDER.md`
- Reviewer: Codex, `ORCHESTRATOR / REVIEWER`
- Future implementation worker: Claude
- Disposition:
  `REVIEW_PASS — C1/C2 AND G6 REQUIRED; BUILD STILL PROHIBITED`

## 1. Independence and review boundary

The operator assigned Codex as orchestrator/reviewer and Claude as the future
implementation/repair worker. Independence is from the agent that will
implement and repair the R2 security change: Codex authored and reviewed the
authorization boundary but performed no BUILD; Claude performed no review,
stage, commit, push or self-approval.

This review made no source, test, API, permission, provider, Docker or database
change. It inspected only current source truth, transaction seams, test/evidence
architecture and the proposed authorization ceiling.

## 2. Feasibility reproduced

- `ShiftService`, shifts router and permission module are 166, 133 and 96
  physical lines, leaving bounded room for the exact create path.
- Ledger Protocol, InMemoryLedger and SqlLedger already expose
  `transaction()`, `create_shift(..., unit=...)` and
  `append_audit(..., unit=...)`; no backend or protocol edit is needed.
- current `POST /shifts` accepts exactly the three required query parameters,
  calls `ledger.create_shift(...)` directly and has no JWT dependency.
- the repository-wide OpenAPI proof and the historical P2-C delta proof both
  necessarily observe a later security change on `POST /shifts`; authorizing
  both exact historical test paths is required and sufficient.
- the PostgreSQL runner is exactly 300 lines. One target can be appended
  without compression by removing at most one adjacent blank/obsolete
  target-list comment line; its existing runner test pins the exact tuple.
- the closed P2-C provider runner is 299 lines and does not need modification.
  The Work Order instead authorizes a coherent new shift-create runner/support
  split plus its own adversarial non-live test.
- no migration, canonical model, Ledger implementation, message, Integration
  Edge, auth/JWT, frontend or dependency edit is required.

## 3. Exact ceiling audit

The ceiling contains exactly 19 explicit paths:

- 3 production paths;
- 5 non-live/OpenAPI paths;
- 3 PostgreSQL paths;
- 3 provider-evidence paths;
- 5 receipt/control/catalog paths.

There is no wildcard, conditional path, file-size exception, debt-registry
change or worker-selected filename. The two new runner paths are exact.

Continuity and closure paths are not hidden inside C3; C1, C2, C3 and C4 have
separate commit ownership and timing.

## 4. Finding and repair

### `SCR-WO-AUTH-F1 NON_PORTABLE_FOCUSED_COMMAND` — repaired

The draft rendered the focused pytest command with POSIX backslash
continuations even though this workspace runs PowerShell. That could cause a
worker to run an incomplete gate or manually reinterpret the command.

Repair: the command is now one exact, shell-neutral line. No requirement,
test, path or evidence gate was waived.

The C3 staging sentence was also made unambiguous: a passing build inventory
must equal all 19 authorized paths, not an undefined “19-path subset”.

## 5. SPEC and acceptance coverage

| SPEC range | Work Order control |
|---|---|
| R1-R4 | production paths 1-3; admission/role/API tests |
| R5-R8 | separated InMemory, SQLite and PostgreSQL transaction evidence |
| R9-R11 | new structural delta plus two exact chained golden paths and protected message boundary |
| R12-R14 | new runner/support split, observed call accounting and adversarial sanitization |
| R15-R16 | exact line limits, line-neutral PostgreSQL edit and test separation |
| R17 | bounded receipt/control-mapping/C4 wording |
| AC-01..AC-19 | mandatory evidence matrix, exact ceiling and stop conditions |
| AC-20 | detached parent-worktree rollback rehearsal and normal-revert runbook |
| AC-21 | C4 claim boundary and message tranche continuity |

Provider and PostgreSQL gates remain independently mandatory, matching the
repaired SPEC R13. A prerequisite failure stays truthful and cannot be
reclassified as PASS.

## 6. Review probes

- workspace doctor: PASS WITH NOTE, 24 PASS and one bounded legacy catalog
  warning;
- pinned core: expected commit, public origin, clean and equal to
  `origin/main`;
- session-state: PASS;
- repository validation: PASS;
- catalog check: PASS, 20 modules;
- file-size guard: PASS;
- `git diff --check`: PASS;
- staged paths: zero;
- message and Integration Edge diff: zero.

These are authorization-feasibility probes, not BUILD evidence.

## 7. Disposition and next gate

`REVIEW_PASS` after `SCR-WO-AUTH-F1` closed without waiver.

The only next actions are:

1. Codex, as `COMMIT_STEWARD`, commits/pushes the zero-BUILD C1 authorization
   set;
2. Codex records and separately commits/pushes C2 pre-BUILD continuity;
3. Codex runs G6 from the clean pushed C2 state;
4. only then may Claude declare `IMPLEMENTATION_WORKER`.

Until all four steps pass, BUILD, provider calls and worker file edits remain
unauthorized.
