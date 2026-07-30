# Independent Review — Shift Create Admission Repair SPEC

- Review id: `SHIFT-CREATE-ADMISSION-REPAIR-SPEC-REVIEW-001`
- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Date: 2026-07-30
- Phase reviewed: `SPEC`
- Reviewer: Codex, `ORCHESTRATOR / REVIEWER`
- Future implementation worker: Claude
- Disposition: `REVIEW_PASS — WORK_ORDER AUTHORING ONLY`

## 1. Independence and boundary

The operator assigned Codex as reviewer/orchestrator and Claude as the future
implementation/repair worker. Codex performed no BUILD. Claude performed no
review, stage, commit, push or self-approval.

This review changed planning/continuity artifacts only. It made no provider
call, read no provider credential, ran no Docker/PostgreSQL container and
changed no source, test, API contract or permission implementation.

## 2. Inputs reviewed

- `docs/decisions/INTAKE_2026-07-29_SHIFT_CREATE_ADMISSION_REPAIR.md`;
- `docs/decisions/ADR_2026-07-29_SHIFT_CREATE_ADMISSION_REPAIR.md`;
- `docs/specs/SHIFT_CREATE_ADMISSION_REPAIR_SPEC.md`;
- active handoff and canonical/mirror session state;
- current shifts and messages routers;
- current `ShiftService`, permission map and canonical `Shift`;
- Ledger Protocol, InMemory transaction and SqlLedger transaction/audit paths;
- current OpenAPI operation for `POST /shifts`;
- PostgreSQL and P2-C provider-evidence runners and their non-live tests.

## 3. Reproduced source truth

At review time:

- `POST /shifts` has no bearer security, accepts exactly the three required
  query parameters `name`, `starts_at`, `ends_at`, has no request body and
  advertises responses 200/422;
- the route calls `ledger.create_shift(...)` directly;
- `ShiftService` has governed close/freeze methods but no create method;
- the permission map has no `shift.create`;
- Ledger, InMemoryLedger and SqlLedger already expose compatible
  `transaction`, `create_shift(..., unit=...)` and
  `append_audit(..., unit=...)` seams;
- `POST /messages` remains anonymous and trusts caller-supplied `sender_id`;
- `shift_service.py`, shifts router and permission map are 166, 133 and 96
  physical lines respectively;
- the existing PostgreSQL runner is exactly 300 lines and the P2-C provider
  runner is 299, so the Work Order must authorize an exact split/new support
  path or a line-neutral change rather than relying on hidden compression or
  a file-size exception.

## 4. Finding and repair

### `SCR-SPEC-REV-F1 EVIDENCE_RUNNER_COUPLING_AMBIGUITY` — repaired

Original R13 required the admitted provider proof to “satisfy R5-R8”. Read
literally, that coupled provider evidence to the separate PostgreSQL
owned-container gate. This contradicted the ADR's separate evidence bullets
and could misclassify a Docker/PostgreSQL prerequisite failure as a provider
failure.

Repair:

- R13 now requires the admitted provider runner to satisfy R5-R6 before its
  exactly-one real call;
- R7/R8 remain mandatory but explicitly separate closure gates;
- provider and PostgreSQL prerequisite failures remain independently truthful.

No requirement was waived and the acceptance criteria remain AC-01 through
AC-21.

## 5. Intake/design coverage

| Intake finding | SPEC disposition |
|---|---|
| `SCR-INTAKE-F1 DIRECT_LEDGER_MUTATION` | R3, R5, R6; AC-05 through AC-08 |
| `SCR-INTAKE-F2 AUTHORITY_UNDEFINED` | R1, R4; AC-01 through AC-03 |
| `SCR-INTAKE-F3 INPUT_CONTRACT` | R2, R9; AC-04, AC-11 |
| `SCR-INTAKE-F4 ADJACENT_MESSAGE_BYPASS` | Scope, R11, R17; AC-13, AC-21 |
| `SCR-INTAKE-F5 GOVERNANCE_EVIDENCE` | R12-R14; AC-14 through AC-16 |
| `SCR-INTAKE-F6 BACKEND_PARITY` | R7-R8; AC-08 through AC-10 |

The SPEC does not silently absorb message admission, weaken the role
hierarchy, add a migration, change query compatibility or claim production
readiness.

## 6. Review probes

- Focused existing shift atomicity/governance/OpenAPI suite:
  `34 passed`.
- Current OpenAPI probe:
  `security=null`, three required query parameters, no request body,
  responses `200,422`.
- Session-state check: PASS.
- Catalog check: PASS, 20 modules.
- File-size guard: PASS.
- `git diff --check`: PASS.
- Staged paths: zero.

The focused tests reproduce the predecessor baseline only. They do not prove
the future create-admission behavior and are not presented as BUILD evidence.

## 7. Disposition

`REVIEW_PASS` on R1-R17 and AC-01 through AC-21 after
`SCR-SPEC-REV-F1` closed without waiver.

This disposition authorizes only the next control-chain action: author a
bounded Work Order with an exact changed-set ceiling, explicit runner split
paths, G6 preconditions, evidence commands, stop conditions and commit
ownership.

It does not authorize BUILD, provider calls, source/test/contract edits,
staging, committing or pushing.
