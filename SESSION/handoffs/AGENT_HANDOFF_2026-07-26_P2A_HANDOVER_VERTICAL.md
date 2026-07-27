# Agent Handoff — P2-A Handover Vertical

## Disposition

- Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
- Control-chain phase: `FREEZE`
- Roadmap target: P2-A handovers only
- Risk: R2
- Implementation worker: Claude
- Independent reviewer / commit steward / closer: Codex
- Status: `CLOSED_BOUNDED`

## Prior closure

P2A Incident is settled history:

- C3 `eac28f9edcff0ff8e85e14cb8764b603c917fe6b`;
- C4 `db488e0dd0130bdccc38263ea649b75982b6199b`;
- `FREEZE / CLOSED_BOUNDED`.

Do not reopen or batch incident work into this tranche.

## Final closure

- Independent disposition: `REVIEW_PASS`; all `HOV-AUTH-F1..F4` and
  `HOV-REV-F5..F15` closed without waiver.
- C3: `8485ef95ec837138d9279d71f03388d1215c0306`, exactly 47 authorized paths,
  pushed to `origin/main`.
- Independent evidence: focused 117; root 610/53 skipped; tests-only 606/53
  skipped; PostgreSQL 16 live 53 with exact cleanup; bounded real provider
  evidence HTTP 200 with four refusal zero-call cases and one admitted call;
  repository and doctor gates PASS.
- Claim boundary remains the parent/amended boundary. This does not prove
  report approval, destination assignment, UI, managed PostgreSQL, production
  provider routing, load/concurrency/HA or Phase 2 completion.
- C4 records this FREEZE separately and augments the future roadmap. The next
  governed move is fresh INTAKE for P2-C frontend; no BUILD authority carries
  forward.

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

### Independent re-re-re-review — F11/F12

Codex rehydrated continuity on 2026-07-27 and independently checked the F9/F10
repair:

- exact 44-path set, authorization cleanliness, assessment hash and 0 staged:
  PASS;
- dedicated parity suite: 35 passed;
- F10 collection scope: PASS — root collected 659, tests-only collected 655,
  and the exact four root-only nodes are
  `apps/workspace-api/src/workspace_api/tests/test_lifecycle.py`;
- PostgreSQL/provider/full exit gates: not rerun after the new defect stop.

Review still returns changes:

- `HOV-REV-F11 MULTISET_COLLAPSE_IMMUTABILITY`: `_items_key` returns a set and
  `_evidence_key` returns a frozenset. Both discard multiplicity. Independent
  probes proved both InMemoryLedger and SqlLedger accept an identical duplicate
  item and an identical duplicate evidence entry through `put_handover`.
  Stored data remains unchanged, but R22 requires every snapshot/evidence
  mutation to be rejected, not silently accepted.
- `HOV-REV-F12 BUILD_RECEIPT_WORKTREE_DRIFT`: current Git truth is 24 modified
  tracked paths plus 20 new BUILD paths = exact 44, plus the separately
  preserved assessment = 45 status entries and 21 untracked paths. The BUILD
  receipt incorrectly says only the assessment was untracked at the fresh
  repair checkpoint and later uses `23 modified + 20 new + 1 assessment` while
  calling the result 44 non-assessment paths.

F11/F12 fit the existing `_handover_repository.py`, `_handover_store.py`,
`test_handover_ledger_parity.py` and BUILD-receipt paths. Comparison must remain
order-independent but become multiplicity-sensitive. Tests must cover identical
duplicate item and evidence mutations on both backends and every Python file
must remain <=300. Exact C3 remains 44; no Amendment 3 and no 45th path are
authorized.

### Independent re-review — F13 / Amendment 3

Codex independently verified the F11/F12 repair:

- exact 44 BUILD paths and corrected worktree arithmetic: PASS;
- duplicate item/evidence rejection plus order-only acceptance on both
  backends: PASS;
- focused 171 passed; root 610 passed/53 skipped; tests-only 606 passed/53
  skipped; repository gates PASS;
- PostgreSQL 16 live 53 passed, migrations 21/0 then 17/4, cleanup exact;
- four provider refusal cases at 0 calls and one genuine Alibaba HTTP 200 call.

AC-21 rehearsal at committed parent `6850e6e` returned the expected tests-only
baseline (`507 passed, 44 skipped, 1 warning`) but file-size/validator failed:

- LF primary file SHA-256: `59288b5c...` (matches baseline);
- fresh Windows worktree under `core.autocrlf=true`: CRLF SHA-256
  `04e4039e...`;
- logical content and line count are identical;
- both temporary worktrees were removed successfully.

Finding: `HOV-REV-F13 ROLLBACK_REHEARSAL_EOL_NONPORTABILITY`.

Amendment 3 C2f `fd5367b146b40a85eb78edde6bf75aa73ab4310d`
authorizes exactly:

45. `scripts/check_file_size.py`;
46. `tests/integration/test_file_size_guard.py`;
47. `docs/reference/FILE_SIZE_GUARD.md`.

Debt SHA becomes UTF-8/universal-newline canonical (CRLF/lone CR → LF) while
all non-EOL mutations remain digest failures. Existing LF digests are not
rehashed. No debt entry, `.gitattributes` workaround or 48th path is allowed.

## Exact BUILD boundary

The final C3 ceiling is exactly 47 paths: Work Order section 3's 39,
Amendment 1's two legacy freeze tests, Amendment 2's three split/parity paths
and Amendment 3's three guard portability paths. No 48th path is conditional.

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

After the Amendment 3 C2f and F13 continuity C2g pushes, Claude rehydrates this
handoff, the parent authorization and Amendments 1-3; declares
`REPAIR_WORKER`; repairs only F13 inside the exact 47 paths, then reruns all
gates.

Claude performs no stage/commit/push and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_REVIEW`

Any stop-condition defect is reported without repair until Codex reviews and
authorizes the next move.

### Independent receipt re-review — F14 / Amendment 4

Claude's F13 implementation correctly hashes UTF-8 logical text through
universal-newline translation. Codex independently ran the focused suite
(`36 passed`) and reproduced the resulting gate stop:

- `scripts/generate_catalog.py` recorded SHA `a46bd98d...` equals the current
  worktree's raw CRLF bytes;
- its unchanged Git blob and canonical logical text both hash to
  `fff6229d...`;
- the other debt entry remains unchanged and canonical;
- direct file-size gate fails only on the stale `generate_catalog.py` value.

Finding:
`HOV-REV-F14 PREEXISTING_CANONICAL_DEBT_DIGEST_DRIFT`.

Amendment 4 C2h `781f75c` authorizes exactly one scalar correction in the
already-authorized `docs/reference/FILE_SPLIT_DEBT_BASELINE.json`: replace
that entry's SHA with
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
No other field, entry, digest or source may change. Exact C3 remains 47.

After this continuity C2i push, Claude rehydrates the parent authorization and
Amendments 1-4, declares `REPAIR_WORKER`, applies only that scalar correction,
updates the BUILD receipt, reruns all mandatory gates, and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_RE_REVIEW`

### Reviewer-owned F15 closure

The F14 repair was correct and its worker gates found
`HOV-REV-F15 REVIEWER_CONTINUITY_HARD_LIMIT_BREACH`: reviewer-owned C2i
`a217b12` had expanded `SESSION/SESSION_MEMORY.md` from 599 to 601 lines.
This was not a BUILD defect and required no C3 path or exception.

Codex closed F15 without waiver at `eaccf7a` by compacting only the duplicated
front-door F14 summary. The memory is now 599 lines. Fresh independent
evidence after that correction:

- exact authorized BUILD set: 47/47, no missing/extra path, staged 0;
- focused guard/handover/parity/schema/SQL: 117 passed;
- root: 610 passed, 53 skipped; tests-only: 606 passed, 53 skipped;
- PostgreSQL 16: 53 passed, migrations 21/0 then 17/4, cleanup exact;
- file-size, validator, catalog, session-state and diff checks: PASS;
- secret-safe diff scan: PASS;
- doctor: 24 PASS and the one bounded legacy warning.

The existing worker receipt truthfully records its earlier stop but is now
stale after reviewer disposition. Claude may change only that already-
authorized BUILD receipt to record F15 closure/current HEAD and the clean
checkpoint, rerun non-live receipt/repository checks, and stop at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_RE_REVIEW`

## Claim boundary

Potential closure proves a server-derived, authenticated handover and real
`open_handover_items_linked` freeze prerequisite for open Task,
CustomerRequest and Incident records on InMemoryLedger, SQLite and disposable
local PostgreSQL 16, plus bounded real-provider governance evidence.

It does not implement report approval, OperationalEvent resolution,
destination personnel assignment, UI, production provider routing,
production/managed PostgreSQL readiness, concurrency/load/HA or the complete
Phase 2 exit gate.
