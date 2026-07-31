# ADR Addendum — P2-C C3a2 Exact-Set Ceiling Contraction

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

`C3A2-BUILD-REV-F3 AC32_EXACT_SET_MISMATCH`: independent BUILD review found
that the candidate changes exactly 74 paths while the amended Work Order names
82. All 74 changed paths are inside the ceiling and zero files are staged, but
SPEC AC-32 requires equality rather than subset membership.

The eight unused paths already pass under route-wide enforcement and require
no implementation change:

- `tests/cvf/test_assignment_foundation.py`
- `tests/cvf/test_customer_request_repair.py`
- `tests/cvf/test_customer_request_transitions.py`
- `tests/cvf/test_shift_create_admission.py`
- `tests/integration/test_p2c_read_postgres_limit_live.py`
- `tests/integration/test_shift_create_live_evidence_runner.py`
- `tests/integration/test_shift_create_postgres_live.py`
- `tests/integration/test_shift_create_sqlite.py`

Editing them only to manufacture 82/82 would add no behavior or evidence and
would weaken exact-set governance.

## Decision

Remove exactly those eight paths from the authorized C3a2 BUILD set. The final
exact set is the prior 82 minus those eight, hence exactly 74 unique paths.
This is a contraction only: it adds no path, wildcard, reserve, waiver, debt,
exception or implementation authority.

F1, F2 and F4 repairs remain subject to independent BUILD re-review. Their
current edits stay unstaged and inside the contracted set. The BUILD receipt
must be rewritten from “74 of 82”/subset language to exact 74-of-74 equality
only after this amendment is independently approved, pushed and followed by a
separate four-surface resume checkpoint.

## BUILD state

`HEAD == origin/main == 22e05b5bd68fbb8dafa12c1646d527280692b736` at
authorship. The partial BUILD contains exactly 74 changed paths, zero outside
the prior 82 and zero staged. No implementation edit, provider call, BUILD
commit, push, self-review or FREEZE occurs under this design amendment.
