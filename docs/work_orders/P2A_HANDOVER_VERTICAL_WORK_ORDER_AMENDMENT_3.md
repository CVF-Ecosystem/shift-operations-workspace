# Work Order Amendment 3 — P2-A Handover Rollback Portability

ID: `P2A-HANDOVER-WO-AMENDMENT-3`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — REPAIR PROHIBITED UNTIL C2f AND C2g ARE PUSHED
Amends: parent Work Order and Amendments 1-2

## 1. Accepted finding

`HOV-REV-F13 ROLLBACK_REHEARSAL_EOL_NONPORTABILITY` is accepted without
waiver. The committed-parent AC-21 rehearsal passes its test baseline but
fails the file-size gate because raw-byte SHA-256 changes under LF-to-CRLF
checkout conversion.

## 2. Exact amended C3 changed set

The existing 44 paths remain authorized. Add exactly:

45. `scripts/check_file_size.py`
46. `tests/integration/test_file_size_guard.py`
47. `docs/reference/FILE_SIZE_GUARD.md`

Final C3 is exactly 47 paths. No 48th path is conditional.

## 3. Repair scope

After C2f/C2g are pushed, Claude may declare `REPAIR_WORKER` and:

1. make debt SHA-256 newline-representation-neutral exactly per R24;
2. add/adjust integration coverage for AC-31/AC-32 without weakening existing
   negative tests;
3. document the canonical digest rule;
4. keep `scripts/check_file_size.py` and
   `tests/integration/test_file_size_guard.py` <=300 physical lines;
5. correct the BUILD receipt to record F13 and the 47-path ceiling;
6. rerun all parent/amended focused, full, repository, PostgreSQL and provider
   gates, then stop for independent review.

No debt entry may be added, restored or rehashed. Do not use `.gitattributes`,
machine-local Git configuration or a special rollback command to hide the
portability defect.

## 4. Mandatory evidence

- focused file-size guard suite, including LF/CRLF equivalence and unchanged
  non-EOL mutation rejection;
- full root and tests-only non-live suites;
- file-size, catalog, session-state, validator, diff and doctor gates;
- disposable PostgreSQL 16 and exact cleanup;
- real provider evidence;
- reviewer-owned fresh-worktree AC-34 rehearsal after repair.

## 5. Stop conditions

STOP on:

- a required 48th path;
- any debt add/rehash/restore;
- raw-byte digest remaining checkout-dependent;
- non-EOL content mutation becoming accepted;
- any touched Python file above 300 lines;
- red gate, receipt drift or secret-bearing output.

## 6. Commit graph and role

- C2f: exactly this Amendment 3 ADR/SPEC/Work Order set.
- C2g: reviewer-owned continuity acknowledgment and repair route.
- C3: exactly 47 BUILD paths after independent REVIEW_PASS.
- C4: closure remains separate.

Claude performs no stage, commit, push or self-approval and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_REVIEW`

## 7. Independent approval

Codex independently reproduced F13 and approves this exact 47-path repair
boundary under the operator-delegated reviewer/work-order authority.
