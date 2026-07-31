# ADR Addendum — P2-C C3a1 Review-Repair Test Split

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

`P2C-C3A1-BUILD-RE-REVIEW-BLOCK-F1 TEST_COVERAGE_EXCEEDS_FILE_GUARD`:
the repair worker correctly stopped before creating out-of-ceiling files.
Independent review requires regression coverage for two residual defects:

- assignment primary-key collision must be controlled, must not overwrite
  InMemory history, and must remain distinct from duplicate-active and other
  database constraint failures on InMemory, SQLite and PostgreSQL;
- every invalid JWT `exp`, including finite numeric values outside the host
  timestamp range, must become a controlled authentication failure rather
  than HTTP 500.

The required tests take the three existing test hosts to 323, 342 and 372
lines respectively, above the repository's executable Python limit of 300.
Deleting required cases would weaken the accepted review findings. A debt or
file-size exemption is forbidden.

Mechanical changed-set inspection found exactly 50 changed implementation
paths against the amended 50-path ceiling, with no missing or outside path.
The worker's reported `49/50` was a counting artifact caused by untracked
directory aggregation; it does not create a usable reserve path.

## Decision

Add exactly three feature-owned test companion paths:

1. `tests/cvf/test_assignment_foundation_f1.py`;
2. `tests/integration/test_assignment_ledger_parity_f1.py`;
3. `tests/integration/test_assignment_postgres_live_f1.py`.

The C3a1 ceiling increases from exactly 50 to exactly 53 unique paths. The
companions may contain only the accepted F1/F2 repair coverage and the minimum
fixtures/imports needed to execute it. Existing tests must be moved, not
silently dropped or duplicated merely to inflate counts. All six affected
test files must finish at or below 300 lines.

No implementation requirement, production claim, C3a2 authority, debt entry,
wildcard, reserve or self-review path is added. The partial BUILD remains
unstaged. C3a1 stays blocked until this amendment, its authorization review
and the subsequent continuity-resume checkpoint are committed and pushed.
