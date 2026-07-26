# Agent Handoff — P2-A Handover Vertical

## Disposition

- Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
- Control-chain phase: `REVIEW` returned changes; Amendment 2 repair authorized
- Roadmap target: P2-A handovers only
- Risk: R2
- Implementation worker: Claude
- Independent reviewer / commit steward / closer: Codex
- Status: `REVIEW_CHANGES_REQUIRED_F9_F10`

## Prior closure

P2A Incident is settled history:

- C3 `eac28f9edcff0ff8e85e14cb8764b603c917fe6b`;
- C4 `db488e0dd0130bdccc38263ea649b75982b6199b`;
- `FREEZE / CLOSED_BOUNDED`.

Do not reopen or batch incident work into this tranche.

## Authorization

- C1: `2134cd88b06db1ee30394e6f65513d0472b8bf40`
- ADR: `docs/decisions/ADR_2026-07-26_P2A_HANDOVER_VERTICAL.md`
- SPEC: `docs/specs/P2A_HANDOVER_VERTICAL_SPEC.md`
- Work Order: `docs/work_orders/P2A_HANDOVER_VERTICAL_WORK_ORDER.md`
- Independent disposition: `REVIEW_PASS`
- Findings closed without waiver:
  - `HOV-AUTH-F1 DIGEST_SHAPE_AMBIGUOUS`
  - `HOV-AUTH-F2 DESTINATION_AUTHORITY_OVERCLAIM`
  - `HOV-AUTH-F3 FREEZE_DESTINATION_DRIFT`

### Mid-BUILD authorization amendment

The worker correctly stopped without repair when the full suite exposed two
legacy freeze-test paths outside the 39-path ceiling. Codex independently
reproduced `7 failed, 545 passed, 44 skipped, 1 warning`: three unfinished
authorized catalog/OpenAPI failures plus four failures in:

- `tests/cvf/test_atomic_mutation_audit.py`;
- `tests/cvf/test_customer_request_vertical.py`.

`HOV-AUTH-F4 — LEGACY_FREEZE_TEST_SCOPE_OMISSION` is closed without waiver by
C2b `78d17b06d771b6e5e3abc1a27d867bc21f4b3641`:

- `docs/decisions/ADR_2026-07-26_P2A_HANDOVER_LEGACY_FREEZE_TEST_ADDENDUM.md`;
- `docs/specs/P2A_HANDOVER_VERTICAL_SPEC_AMENDMENT_1.md`;
- `docs/work_orders/P2A_HANDOVER_VERTICAL_WORK_ORDER_AMENDMENT_1.md`.

The exact C3 ceiling is now 41 paths: the original 39 plus those two test
paths. No 42nd path is conditional. A production compatibility bypass is
prohibited.

### Independent BUILD review — Amendment 2

Codex independently reran the amended focused suite (`60 passed`) and full
suite (`567 passed, 53 skipped, 1 warning`), verified catalog/session/diff,
and returned `REVIEW_CHANGES_REQUIRED`:

- `HOV-REV-F5 DEBT_RATCHET_BYPASS`;
- `HOV-REV-F6 CONTINUITY_GATE_RED`;
- `HOV-REV-F7 LEDGER_PARITY_AND_IMMUTABILITY_GAP`;
- `HOV-REV-F8 BUILD_RECEIPT_DRIFT`.

Fresh probes proved InMemory accepts duplicate items and missing shift FKs,
while SqlLedger leaks/mislabels integrity errors; immutable snapshot puts are
not backend-identical. File-size/validator also fail on reviewer-owned
`SESSION_MEMORY` 607/600. PostgreSQL/provider re-review stopped on the
production defect.

C2d `cbf053fa9314e3ec63bd78fc3df8c3e014d2fdc7` independently approves:

- `docs/decisions/ADR_2026-07-26_P2A_HANDOVER_REVIEW_REPAIR_ADDENDUM.md`;
- `docs/specs/P2A_HANDOVER_VERTICAL_SPEC_AMENDMENT_2.md`;
- `docs/work_orders/P2A_HANDOVER_VERTICAL_WORK_ORDER_AMENDMENT_2.md`.

C3 is now exactly 44 paths, adding the shared customer fixture module,
customer transition module and dedicated handover ledger-parity module. The
customer debt entry must be removed, never rehashed. No 45th path is
conditional. Codex owns the C2e continuity compaction separately.

### Independent re-review — F9/F10

Amendment 2 repair was re-reviewed from source:

- exact 44-path set: PASS;
- customer-request split/debt removal: PASS;
- dedicated parity suite: 17 passed;
- customer split suite: 29 passed;
- root full suite: 588 passed/53 skipped/1 warning;
- tests-only suite: 584 passed/53 skipped/1 warning;
- catalog/session/file-size/validator/diff: PASS.

Review still returns changes:

- `HOV-REV-F9 PARTIAL_SNAPSHOT_COMPARATOR`: both backends accept item
  `summary`, `evidence` and aggregate `created_at` mutations because the
  comparator only covers `(record_type, record_id, digest)`. R22 requires
  every item/snapshot/evidence field immutable.
- `HOV-REV-F10 REVIEW_COMMAND_SCOPE_MISCLASSIFICATION`: the earlier F8
  diagnosis was reviewer error. `571` root versus `567` tests-only came from
  four app-local tests discovered only by root pytest, not receipt drift.
  Receipts/continuity must correct the history and label command scope.

F9/F10 fit the existing `_handover_repository.py`, `_handover_store.py`,
`test_handover_ledger_parity.py` and build-receipt paths. Exact C3 remains 44;
no Amendment 3 and no 45th path are authorized. PostgreSQL/provider re-review
stops until F9 is repaired.

## Exact BUILD boundary

The final C3 ceiling is exactly 44 paths: Work Order section 3's 39,
Amendment 1's two legacy freeze tests and Amendment 2's three split/parity
test paths. No 45th path is conditional.

Key invariants:

- handover items are server-derived, never caller-supplied;
- mandatory open sources are Task, CustomerRequest and Incident only;
- exact canonical digest fields/encoding are normative;
- reviewer and receiver are distinct authenticated supervisors;
- no destination-shift personnel-assignment claim;
- destination OPEN/source not-FROZEN and snapshot equality are rechecked at
  review, acknowledgement and freeze;
- report override never bypasses handover;
- OperationalEvent completeness is out of scope because it lacks an
  open/resolved semantic;
- all Python remains <=300;
- legacy `test_shift_close_governance.py` is split through the required shared
  fixture module and its debt entry is removed, not rehashed.

## Mandatory evidence

- focused model/lifecycle/API/ledger/parity/freeze/split tests;
- full non-live suite;
- disposable PostgreSQL 16 migration 001-006 round-trip;
- exact Docker cleanup;
- real provider response after valid JWT sender review, distinct receiver
  acknowledgement and freeze;
- refusal paths observed at zero provider calls;
- sanitized live/build receipts;
- protected report/incident/auth/CVF-core zero diff;
- reviewer-owned rollback rehearsal after BUILD.

## G6 and return

After the F9/F10 continuity push, Claude rehydrates this handoff, the parent
authorization and Amendments 1-2; declares `REPAIR_WORKER`; repairs only F9
and F10 inside the existing 44 paths, then reruns all gates.

Claude performs no stage/commit/push and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_REVIEW`

Any stop-condition defect is reported without repair until Codex reviews and
authorizes the next move.

## Claim boundary

Potential closure proves a server-derived, authenticated handover and real
`open_handover_items_linked` freeze prerequisite for open Task,
CustomerRequest and Incident records on InMemoryLedger, SQLite and disposable
local PostgreSQL 16, plus bounded real-provider governance evidence.

It does not implement report approval, OperationalEvent resolution,
destination personnel assignment, UI, production provider routing,
production/managed PostgreSQL readiness, concurrency/load/HA or the complete
Phase 2 exit gate.
