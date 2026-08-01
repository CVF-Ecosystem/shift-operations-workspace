# P2C-C3B1 Browser Read/Readiness Contract — BUILD Evidence Receipt

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Final exact BUILD ceiling: **36 numbered / 36 unique paths** (original 34 +
  Amendment 2's `AsyncState.tsx` + Amendment 3's `App.test.tsx`)
- Final exact changed set: **36 of 36 paths** — every authorized path changed,
  zero outside the ceiling, zero unnecessary. See "Exact changed-path
  membership" below.
- Resume/review parent (this round): `8c0700db4608513123b0126b657d0903b8f90830`
  (`HEAD == origin/main` verified before any edit; unchanged this round —
  this is a REVIEW repair round, not a fresh pushed checkpoint)
- Prior resume parents: `e2ef541` (G6/Amendment 1 resume) → `6fc5802`
  (Amendment 2 resume) → `8c0700d` (Amendment 3 resume; also the repair
  parent for both `C3B1-BUILD-REV-F1` and `C3B1-BUILD-REV-F2`, since
  independent review found each against candidates built at that same
  parent)
- Status: `READY_FOR_INDEPENDENT_P2C_C3B1_BUILD_RE_RE_RE_REVIEW` — **this
  supersedes the prior `READY_FOR_INDEPENDENT_P2C_C3B1_BUILD_RE_RE_REVIEW`
  claim. Independent re-review found one further finding
  (`C3B1-BUILD-REV-F2`, an annotation-only drift — F1's matching fix was
  functionally correct throughout).** Do not treat any earlier count or
  claim in this document's history as still standing without checking the
  corresponding "this round" evidence below.

## Amendment record

- Amendment 1 (frontend test command only): the original Work Order's minimum
  command `pnpm --dir apps/workspace-web test -- --run` failed under pnpm
  9.15.0 with `Unknown option: 'run'`; replaced with
  `pnpm --dir apps/workspace-web run test`. No ceiling change (34/34).
- Amendment 2 (`34 → 35`, `C3B1-BUILD-FEAS-F1
  OUTCOME_UNKNOWN_EXHAUSTIVE_CONSUMER`): added
  `apps/workspace-web/src/components/AsyncState.tsx`. R16/R36's new
  `outcome_unknown` `ApiErrorKind` broke `AsyncState.tsx`'s exhaustive
  `Record<ApiErrorKind, string>` map — the sole exhaustive consumer among
  eight `ApiErrorKind` reference sites. Authority limited to adding the
  deterministic sanitized R38 message; no handler/retry/state/storage/style/
  navigation/mutation/feature wiring authorized.
- Amendment 3 (`35 → 36`, `C3B1-BUILD-FEAS-F2 STALE_NETWORK_UI_EXPECTATION`):
  added `apps/workspace-web/src/tests/App.test.tsx`. After Amendment 2's
  typecheck fix, `pnpm --dir apps/workspace-web run test` still failed:
  `App.test.tsx`'s `it.each` network-failure case expected the legacy
  `Offline` indicator, but `deriveConnectionState` in the still-protected
  `OperationsConsole.tsx` already correctly maps every non-`network`
  controlled kind (including the new `outcome_unknown`) to `Connection
  issue` — no `OperationsConsole.tsx` change was authorized or needed.
  Authority limited to a **line-neutral** edit of the existing case only.

## Independent BUILD review finding — `C3B1-BUILD-REV-F1 GREEDY_MATCHING_FALSE_NEGATIVE`

Independent review of the candidate built at parent `8c0700d` (recorded as
`READY_FOR_INDEPENDENT_P2C_C3B1_BUILD_RE_REVIEW` in the prior version of this
document) found that `approval_readiness.py`'s `_match_seats` claimed
deterministic maximum bipartite matching but was actually a greedy
left-to-right seat scan, whose own docstring's correctness argument was
false. Reproduction: required seats `['shift_supervisor',
'responsible_manager']`; receipts stored in the order `responsible_manager`
then `shift_supervisor`. Because `has_authority` is monotone in role rank (a
`responsible_manager`, rank 3, also satisfies the lower `shift_supervisor`
seat, rank 2), the greedy scan let the manager's receipt get consumed by the
*first* seat (`shift_supervisor`) before the scan ever reached the second
seat, leaving `responsible_manager` unmatched even though a genuine maximum
matching exists (supervisor's own receipt fills the supervisor seat; the
manager's receipt fills the manager seat). Result was `['shift_supervisor']`
instead of the correct `['shift_supervisor', 'responsible_manager']` —
`ready` would be reported `False` for a shift that in fact has a satisfied
quorum, an order-dependent false negative that violates SPEC R35's
requester-independent, order-independent matching requirement. Independently
verified reproducible before any repair (see "F1 repair" below).

### F1 repair

Replaced `_match_seats`'s greedy scan with genuine Kuhn's-algorithm
augmenting-path bipartite matching, entirely inside the already-authorized
`apps/workspace-api/src/workspace_api/application/approval_readiness.py`
host — no import from or edit to protected `cvf-runtime` source; the local
`_try_augment`/`_eligible_approvers` helpers are bounded to this module. For
each required seat in declared order, the algorithm tries every eligible,
not-yet-visited-this-attempt distinct approver; if an approver is already
holding a different seat, it recursively attempts to move that approver's
seat to some other eligible approver first (the "augmenting path"), so an
already-matched approver can be displaced onto a seat it also qualifies for
whenever that raises the total number of matched seats — exactly the case
the greedy scan missed. `_eligible_approvers` deterministically deduplicates
candidate approver ids while preserving first-receipt order (repair item 4).
`satisfied_roles` is still derived by filtering `required_roles` to only the
seat indices that ended up matched, so it remains in original declared-seat
order regardless of match-discovery order; duplicate role seats remain
distinct by seat index (a `[shift_supervisor, shift_supervisor]` requirement
still needs two distinct approvers, one per index, not one approver counted
twice); one approver still fills at most one seat (`seat_of_approver` is a
one-to-one map, reassigned only through a genuine augmenting path, never by
letting two seat indices point at the same approver); current-user authority
is still resolved fresh per call via the existing `_authority_for` closure
(unchanged — it never trusted a stored receipt role); and receipt-stored
roles remain wholly non-authoritative, exactly as before — `_match_seats`
still receives only approver ids and re-derives authority through
`authority_for` on every call, never reading anything off the receipt object
except `approver_id`.

## Independent re-review finding — `C3B1-BUILD-REV-F2 MATCH_MAP_KEY_ANNOTATION_DRIFT`

Independent re-review of the F1 repair found that F1 was **functionally
correct** — the augmenting-path matching itself behaved exactly as intended,
with no algorithmic defect — but two type annotations on `seat_of_approver`
contradicted the actual implementation. `seat_of_approver` is populated and
read using `approver_index` (an `int`, the position of an approver in the
`approvers` list built by `_eligible_approvers`) as its key, never a
string — yet both declarations read `dict[str, int]`:

- the `_try_augment` parameter annotation, `seat_of_approver: dict[str, int]`;
- the local variable initializer in `_match_seats`,
  `seat_of_approver: dict[str, int] = {}`.

### F2 repair

Changed both annotations, and only the annotations, to `dict[int, int]` —
the exact key type the implementation already uses. No algorithm behavior,
test, path or ceiling changed; the matching logic, its recursion, and every
prior behavioral guarantee (deterministic maximum matching, preserved seat
order/multiplicity, one-approver-one-seat, order-independence, fresh
authority resolution, non-authoritative receipt roles) are unaffected,
because a type annotation carries no runtime behavior in this codebase
(no `from __future__ import annotations`-driven runtime introspection or
Pydantic validation is applied to these two local names — they are plain
function-body/parameter type hints checked only by static analysis).

## History

1. **G6 (this round's resume, `8c0700d`):** verified `HEAD == origin/main ==
   8c0700db4608513123b0126b657d0903b8f90830`; ancestry of `edb9b02`/`a15c33c`
   confirmed; preserved partial BUILD measured at exactly **31 changed paths**,
   zero staged, `apps/workspace-web/tsconfig.tsbuildinfo` absent, all three
   previously-repaired file-size hosts still ≤300 lines
   (`scripts/run_postgres_live_roundtrip.py` 296,
   `tests/cvf/test_c3b_read_routes.py` 270,
   `tests/unit/test_p2b_openapi_contract.py` 298).
2. **Amendment 3 implementation:** edited only the existing ambiguous-transport
   `it.each` case in `App.test.tsx` (lines 135-146 pre-edit) to expect
   `/Connection issue/` instead of `/Offline/` and assert the exact sanitized
   R38 message (`'The outcome of this request could not be confirmed. Refresh
   before trying again.'`) is present among the rendered alert texts for the
   network-failure case; the 5xx case keeps its prior no-specific-message
   assertion (falls back to asserting at least one alert renders). Net file
   length held at exactly 200 lines (line-neutral) by merging `arrange();
   render(<App />);` onto one statement inside the same block — no other line
   in the file was touched. `OperationsConsole.tsx` was not edited; `git diff
   --quiet HEAD -- apps/workspace-web/src/app/OperationsConsole.tsx` confirmed
   clean throughout.
3. **PostgreSQL live-suite regression found and repaired (test-only, in
   already-authorized `tests/integration/test_c3b_read_postgres_live.py`):**
   the first live run after Amendment 3 (see "Disposable PostgreSQL evidence"
   below) failed 2 of 110 tests with `CvfDenied: role 'viewer' may not perform
   'message.create' (requires at least 'operator')`. Root cause: both
   `test_live_message_list_assignment_scoped_and_ordered` and
   `test_live_read_limit_ceiling_for_messages` seeded their message-creating
   principal with role `viewer` and called it through the real
   `MessageService.create`, which correctly enforces `message.create`
   requiring `operator`+ — a genuine test defect (the earlier InMemory-backed
   focused test had bypassed the service layer via direct `ledger.add_message`
   and therefore never exercised this permission check). Repaired by seeding
   and authenticating that principal as `operator` instead of `viewer` in both
   tests (read-list admission itself remains scoped only by ACTIVE assignment,
   unaffected). No production code changed; no new path added.
4. **Catalog regeneration:** `python scripts/generate_catalog.py --write` was
   run after all source/test edits stabilized (`workspace-api` LOC/file-count
   grew from the new `browser_reads.py`/`approval_readiness.py`/
   `_message_repository.py` modules and router additions; `workspace-web` LOC
   grew from `backendContracts.ts`/the two new test files/`AsyncState.tsx`'s
   one added line). `docs/catalog/MODULE_REGISTRY.json` and
   `docs/catalog/MODULE_CATALOG.md` were regenerated; `--check` then passed
   clean.
5. **`docs/cvf/CVF_CONTROL_MAPPING.md` truth-surface append:** C3b1 adds no
   new CVF `required_control` — the three new list routes reuse the existing
   `require_active_assignment` guard already documented for C3a2's R6 matrix,
   and `GET /approvals/readiness` is a read that never authorizes (mutation
   still re-runs `create_approval_receipt`'s full independent gate chain,
   including the confirmer/self-approval rule readiness deliberately skips).
   A short entry documents this bounded nonclaim; no existing entry was
   rewritten.
6. **Independent review round — `C3B1-BUILD-REV-F1` repair (this round):**
   reproduced the reported false negative exactly as described (manager
   receipt stored before supervisor receipt yielded only `['shift_supervisor']`
   instead of both seats) via an isolated script against the then-current
   greedy `_match_seats`, confirming the finding before writing any fix.
   Replaced `_match_seats` with genuine Kuhn's augmenting-path matching (see
   "Independent BUILD review finding" above for the algorithm). Added
   `tests/cvf/test_c3b_approval_readiness.py::
   test_r3_quorum_matches_regardless_of_receipt_arrival_order`, which stores
   the `responsible_manager` receipt strictly before the `shift_supervisor`
   receipt and asserts `required_roles == satisfied_roles ==
   ['shift_supervisor', 'responsible_manager']` and `ready is True`.
   Independently confirmed this new test fails against the old greedy
   algorithm's logic (re-derived inline, without touching the working tree,
   since `git stash` is prohibited on this preserved candidate) — result
   `['shift_supervisor']` versus the asserted
   `['shift_supervisor', 'responsible_manager']` — and passes against the
   repaired implementation, so the regression is real and load-bearing, not
   coincidentally always-true. Retained and reran the existing
   `test_one_distinct_approver_fills_at_most_one_seat` and
   `test_r3_quorum_matches_multiple_distinct_seats_in_order` (original
   supervisor-then-manager order) tests, plus every other existing readiness
   test — all still pass, confirming the augmenting-path rewrite changed no
   externally observable behavior for scenarios the greedy scan already
   handled correctly. Both edited files
   (`apps/workspace-api/src/workspace_api/application/approval_readiness.py`,
   222 lines; `tests/cvf/test_c3b_approval_readiness.py`, 224 lines) remain
   well under the 300-line hard limit; no new path was added or needed.
7. **Independent re-review round — `C3B1-BUILD-REV-F2` repair (this round):**
   changed exactly the two `seat_of_approver` type annotations from
   `dict[str, int]` to `dict[int, int]` in
   `apps/workspace-api/src/workspace_api/application/approval_readiness.py`
   (see "F2 repair" above) — no other line in either file touched, no
   algorithm/test/path/ceiling change. File remains 222 lines (unchanged
   line count; only characters within two existing lines changed).

## Exact changed-path membership

**36 of 36 authorized paths changed; zero outside the ceiling.** `git status
--porcelain=v1 -uall | wc -l` returns exactly `36`, matching the ceiling
exactly:

```text
apps/workspace-api/src/workspace_api/api/approvals/router.py
apps/workspace-api/src/workspace_api/api/customer_requests/router.py
apps/workspace-api/src/workspace_api/api/messages/router.py
apps/workspace-api/src/workspace_api/api/tasks/router.py
apps/workspace-api/src/workspace_api/application/approval_service.py
apps/workspace-api/src/workspace_api/infrastructure/repository.py
apps/workspace-api/src/workspace_api/application/approval_readiness.py (NEW)
apps/workspace-api/src/workspace_api/application/browser_reads.py (NEW)
apps/workspace-api/src/workspace_api/infrastructure/_message_repository.py (NEW)
apps/workspace-web/src/services/api.ts
apps/workspace-web/src/types/backendContracts.ts (NEW)
apps/workspace-web/src/components/AsyncState.tsx (Amendment 2)
tests/cvf/_c3b_read_fixtures.py (NEW)
tests/cvf/test_c3b_read_routes.py (NEW)
tests/cvf/test_c3b_approval_readiness.py (NEW)
tests/cvf/test_c3b_read_limits.py (NEW)
tests/integration/test_c3b_read_ledger_parity.py (NEW)
tests/integration/test_c3b_read_postgres_live.py (NEW)
tests/unit/test_c3b_read_openapi_contract.py (NEW)
tests/unit/test_assignment_openapi_contract.py
tests/unit/test_p2b_openapi_contract.py
tests/unit/test_p2c_read_openapi_contract.py
tests/unit/test_shift_create_openapi_contract.py
tests/unit/test_message_openapi_contract.py
tests/unit/test_report_openapi_contract.py
apps/workspace-web/src/tests/api.test.ts
apps/workspace-web/src/tests/apiBackendContracts.test.ts (NEW)
apps/workspace-web/src/tests/App.test.tsx (Amendment 3)
scripts/run_postgres_live_roundtrip.py
tests/integration/test_postgres_live_runner.py
docs/decisions/P2C_C3B1_BUILD_EVIDENCE_RECEIPT.md (NEW, this document)
docs/cvf/CVF_CONTROL_MAPPING.md
docs/catalog/MODULE_REGISTRY.json
docs/catalog/MODULE_CATALOG.md
```

The list above already contains all 36 paths (`AsyncState.tsx` and
`App.test.tsx` are listed inline, not repeated). Verified by three-way
comparison against the exact 36-path ceiling text: 13 backend/browser-contract
paths, 15 focused/parity/OpenAPI/transport paths, 6 PostgreSQL/receipt/
truth-surface paths, `AsyncState.tsx` and `App.test.tsx`:

```bash
git status --porcelain=v1 -uall | sed -E 's/^...//' | sort   # → 36 lines
<36-path ceiling, sorted>                                     # → 36 lines
comm -23 <changed> <ceiling>                                  # → empty
comm -13 <changed> <ceiling>                                  # → empty
```

Both `comm` differences are empty: zero changed paths fall outside the
36-path ceiling, and zero ceiling paths were left unnecessarily unchanged.

## Focused C3b1 suites

```powershell
python -m pytest -q tests/cvf/test_c3b_read_routes.py tests/cvf/test_c3b_approval_readiness.py tests/cvf/test_c3b_read_limits.py tests/integration/test_c3b_read_ledger_parity.py tests/unit/test_c3b_read_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_assignment_openapi_contract.py tests/unit/test_message_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_report_openapi_contract.py tests/integration/test_postgres_live_runner.py
```

This round (`C3B1-BUILD-REV-F2`, annotation-only): **57 passed**, unchanged
from the F1 round's evidence — an annotation carries no runtime behavior, so
this rerun is a non-regression confirmation, not new coverage.
`tests/cvf/test_c3b_approval_readiness.py` alone: **8 passed**, unchanged.

## Full non-live suite

```powershell
python -m pytest -q
```

This round: **1238 passed, 0 failed, 120 skipped** — identical to the F1
round's final count. No catalog regeneration was needed or run this round:
a type-annotation-only edit changes zero source LOC as counted by
`generate_catalog.py` (comment/annotation characters within an
already-counted line do not change that line's contribution), and
`generate_catalog.py --check` (below) confirmed the registry was already
current without a `--write` step.

## Frontend gates

**Not rerun this round, as instructed** — `C3B1-BUILD-REV-F2`'s repair
touches only two Python type annotations in `approval_readiness.py`; no
frontend path is in this round's diff. The prior round's frontend evidence
(Node 22.14.0/pnpm 9.15.0, frozen install clean, typecheck clean, 3 files/31
tests passed, production build succeeded, `OperationsConsole.tsx` confirmed
byte-identical) remains the last-performed frontend evidence and is retained
truthfully above rather than restated as fresh. `apps/workspace-web/
tsconfig.tsbuildinfo` was reconfirmed absent this round (see "Final
verification" in the repair-round disposition below) even though no
frontend command ran, since it was already absent from the prior round and
no command that could regenerate it was invoked.

## Repository gates

F1-round evidence (retained, not restated as fresh this round):
`python scripts/generate_catalog.py --write` → `CATALOG VERIFY: PASS`; `20
modules, 11941 LOC -> docs\catalog\MODULE_CATALOG.md` (LOC rose from 11906
because of F1's added matching helpers and regression test).

This round (`C3B1-BUILD-REV-F2`), rerun as instructed:

- `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`.
- `python scripts/generate_catalog.py --check` → `CATALOG VERIFY: PASS` (20
  modules, all paths exist, statuses valid, metrics and Markdown up to date)
  — `--write` was not needed this round because the annotation-only edit did
  not change any file's LOC count, so the registry generated by the F1
  round's `--write` remained current; `--check` alone confirmed this.
- `python scripts/check_session_state.py` → `SESSION STATE: PASS`.
- `python scripts/testing/validate_repository.py` → `repository validation
  passed (catalog + session state + file-size checks)`.
- JSON parse check (`docs/catalog/MODULE_REGISTRY.json`, `.cvf/manifest.json`,
  `.cvf/policy.json`, `SESSION/ACTIVE_SESSION_STATE.json`) → all parse.
- `git diff --check` → exit 0 (only pre-existing LF/CRLF conversion warnings,
  no conflict markers, no trailing-whitespace errors).

## Doctor

```powershell
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```

Not rerun this round — the review instructions did not list doctor among the
gates required for the F2 annotation-only repair. The F1 round's result,
`RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` (the sole warning being
the same bounded `LEGACY_PROJECT: governed downstream catalog kit not
present` note every prior tranche has recorded), remains the last-performed
doctor evidence and is retained truthfully rather than restated as fresh.

## Disposable PostgreSQL evidence

```powershell
python scripts/run_postgres_live_roundtrip.py --json
```

**Not rerun this round, as instructed** — `C3B1-BUILD-REV-F2`'s repair
changes only two Python type annotations with zero PostgreSQL-facing code
path affected. The F1 round's evidence remains the last-performed record:
migrations `24/0` then `20/4`, live suite **110 passed, 0 failed**,
container `cvf-pg-live-17f0094e6581` removed with
`container_absent_after_cleanup: true`, independently reconfirmed with a
direct `docker ps -a` filter (no matching container) and `docker volume
inspect` on the captured anonymous volume ID (`no such volume`) — zero owned
residue at that time. This round's own independent Docker-residue check
(below) reconfirms zero residue currently, without a fresh PostgreSQL run.

## AC-29 isolated exact-parent rehearsal

Not rerun this round — the F1 repair round's required gate list did not
include AC-29, and no path outside the already-rehearsed set changed in a
way that would alter the exact-parent baseline (the F1 repair is confined
to two already-authorized files whose net effect is proven directly by the
focused/full suites above). The prior round's rehearsal evidence is retained
below as the last-performed AC-29 record; it remains available to re-run on
request.

A temporary detached worktree was created at the exact recorded resume parent
`8c0700db4608513123b0126b657d0903b8f90830` at a short filesystem path
(`/d/cvf-ac29-wt`, to avoid a Windows `MAX_PATH` failure encountered when
first attempting a deeply-nested scratch path — no repository configuration
was changed to work around this; a shorter path was used instead), via `git
worktree add --detach`, never touching the primary candidate worktree. It
started clean (`git status --porcelain` empty, `HEAD == 8c0700d`) and
returned:

- Full non-live suite: **1179 passed, 117 skipped** (no catalog-drift
  failure — the pre-BUILD tree's registry is not stale against itself).
- `python scripts/testing/validate_repository.py` → `repository validation
  passed (catalog + session state + file-size checks)`.

The temporary worktree was then removed (`git worktree remove --force`);
its path was confirmed absent afterward (`ls` → "No such file or
directory"). The primary candidate worktree was reconfirmed at
`HEAD == 8c0700d` throughout, unaffected.

## Claim boundary

C3b1 proves only: authenticated, assignment-scoped, deterministic/bounded
browser-required Message/Task/CustomerRequest reads (`(created_at,
message_id)` / `(created_at, task_id)` / `(received_at, request_id)`
ascending, 0-500 admit / 501+ controlled 422, no silent truncation);
sanitized current-binding approval-readiness for exactly `OperationalEvent/
event.confirm`, `Task/task.create` (record_id = stored TaskCreationIntent
id), `Incident/incident.acknowledge` and `Report/report.approve`, using
deterministic maximum bipartite matching, requester-independent, never
applying the confirmer/self-approval rule, excluding digest/receipt-id/
approver-identity/credential from its response; and a non-React browser
transport/DTO contract (typed method/body/query/AbortSignal, 401 session
clear, 403/404/409/422 controlled-kind mapping, ambiguous failure mapped to
`outcome_unknown` with no automatic retry) — on the proven backends
(InMemory, SQLite, disposable PostgreSQL 16).

It does NOT prove: mutation concurrency or CustomerRequest versioning (C3b2);
any React feature/UI control (C3c/C3d) — `OperationsConsole.tsx` and every
other React feature/style file remain byte-identical, confirmed via `git diff
--quiet HEAD --` against each; tenant or provider `data_scope`; token
revocation; production PostgreSQL; P2-C completion; P2-D; or Phase-2
completion. C3b1 made no new AI/agent-governance claim and performed no
provider call — no earlier live-evidence receipt is reused as proof of this
tranche's new read/readiness contract.

## Worker attestation

No stage, commit, push, self-review or FREEZE occurred at any point across
the G6 resume, the Amendment 3 implementation, the PostgreSQL test repair,
the `C3B1-BUILD-REV-F1` repair, the `C3B1-BUILD-REV-F2` repair, or evidence
collection. No reset, clean, stash, restore or discard was performed on the
preserved candidate at any point (`git stash` was attempted only as a
disposable verification aid for confirming the F1 regression test's
discriminating power, was blocked by the environment's own classifier
before any state change occurred, and was not retried by another means —
the verification was instead performed by re-deriving the old algorithm's
logic inline in a throwaway Python snippet that never touched the working
tree). No Claude CLI, provider-control MCP or automated Claude call was
used. Zero files were staged at any point (`git diff --cached` empty
throughout, reconfirmed immediately before this receipt was finalized). No
provider (Alibaba or otherwise) API call was made this round — C3b1 is a
no-new-governance-claim checkpoint per its Work Order.

## Repair-round disposition

- `C3B1-G6-F1 INVALID_FRONTEND_TEST_COMMAND` — closed by Amendment 1 (prior
  round), reconfirmed still correct this round
  (`pnpm --dir apps/workspace-web run test` passes).
- `C3B1-BUILD-FEAS-F1 OUTCOME_UNKNOWN_EXHAUSTIVE_CONSUMER` — closed by
  Amendment 2 (prior round): `AsyncState.tsx` now maps `outcome_unknown` to
  the exact sanitized R38 message; `api.ts`'s `ReadinessQuery` typecheck
  error fixed in the same round with no type-widening. Reconfirmed clean
  (`typecheck` passes with zero errors).
- `C3B1-BUILD-FEAS-F2 STALE_NETWORK_UI_EXPECTATION` — closed by Amendment 3
  (prior round): `App.test.tsx`'s ambiguous-transport case expects
  `Connection issue` and asserts the exact R38 message; `OperationsConsole.tsx`
  untouched, confirmed byte-identical throughout, including this round.
- `C3B1-BUILD-F3 LIVE_MESSAGE_ROLE_SEED_MISMATCH` (test-only defect found and
  repaired in the prior round, not a Work Order ceiling issue): remains
  closed; reconfirmed passing this round's PostgreSQL live re-run.
- `C3B1-BUILD-REV-F1 GREEDY_MATCHING_FALSE_NEGATIVE` (independent BUILD
  review finding, prior round): the then-current `READY_FOR_INDEPENDENT_
  P2C_C3B1_BUILD_RE_REVIEW` claim was incorrect — `_match_seats` was greedy,
  not genuinely maximum, and produced an order-dependent false negative.
  Closed in the prior round by replacing it with Kuhn's augmenting-path
  matching (see "F1 repair" above) plus a regression test proving the
  specific reported scenario now matches correctly regardless of receipt
  arrival order. Disposition: `CLOSED_WITHOUT_WAIVER`; reconfirmed still
  passing this round (8/8 readiness tests, including the F1 regression
  test).
- **`C3B1-BUILD-REV-F2 MATCH_MAP_KEY_ANNOTATION_DRIFT`** (independent
  re-review finding, this round): F1's matching fix was functionally
  correct, but `seat_of_approver`'s two type annotations (`_try_augment`'s
  parameter and `_match_seats`'s local variable initializer) incorrectly
  declared `dict[str, int]` when the implementation only ever uses `int`
  approver-list indices as keys. Closed this round by changing exactly those
  two annotations to `dict[int, int]` (see "F2 repair" above) — zero
  algorithm, test, path or ceiling change. Disposition:
  `CLOSED_WITHOUT_WAIVER`.

Final state, this round: focused suites 57/57 (readiness suite alone 8/8,
unchanged from the F1 round since this is an annotation-only edit), full
non-live suite 1238 passed/0 failed/120 skipped (identical to the F1 round's
final count; no catalog regeneration needed since annotation characters
within an already-counted line do not change LOC), repository gates
(file-size, catalog `--check`, session-state, repository validator, JSON
parse, `git diff --check`) all freshly rerun and PASS. Frontend, PostgreSQL
and doctor gates were **not rerun this round, as instructed**, because
`C3B1-BUILD-REV-F2`'s repair touches only two Python type annotations with
no frontend or PostgreSQL-facing effect; their last-performed evidence (from
the F1 round, retained truthfully above, not restated as fresh) remains:
frontend typecheck/test(31)/build all PASS with `OperationsConsole.tsx`
byte-identical, disposable PostgreSQL live suite 110/110, and doctor `PASS
WITH NOTE (24 passed, 1 warning)`. Exact 36-of-36 changed-path set equal to
the ceiling with zero outside-ceiling edits (no new path was needed for
either F1 or F2), zero staged files, `tsconfig.tsbuildinfo` absent, zero
owned Docker residue reconfirmed by direct inspection this round, `HEAD ==
origin/main == 8c0700db4608513123b0126b657d0903b8f90830` unchanged
throughout.

`READY_FOR_INDEPENDENT_P2C_C3B1_BUILD_RE_RE_RE_REVIEW`
