# ADR Addendum 2 — P2-C C3a Repair Scope

- ID: `ADR-2026-07-29-P2C-READ-API-C3A-REPAIR-SCOPE-ADDENDUM-2`
- Parent:
  `docs/decisions/ADR_2026-07-28_P2C_OPERATIONS_CONSOLE_READ_SLICE.md`
- Prior addendum:
  `docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM.md`
- Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Risk: R2
- Phase: DESIGN
- Status: `DESIGN_COMPLETE — REPAIR_SCOPE_ONLY`

## 1. Trigger

Independent review of the Amendment 1 repair
(`docs/decisions/P2C_READ_API_BUILD_EVIDENCE_RECEIPT.md`,
`docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md`) returned
`REVIEW_CHANGES_REQUIRED` with findings `P2C-C3A-REV-F10` through
`P2C-C3A-REV-F19`:

- `F10 LIVE_PROVIDER_EVIDENCE_BLOCKED` — the live receipt's own top line is
  `BLOCKED`, with `0` provider calls, because no `ALIBABA_API_KEY`/
  `DASHSCOPE_API_KEY` is present in this environment. The tranche cannot
  claim AC-16/R16 provider evidence is satisfied.
- `F11 BUILD_RECEIPT_PATH_COUNT_DRIFT` — the receipt's §4 counts 14 modified
  and states "New (8, ...)" while actually listing 8 new-path bullets plus
  the live receipt as a parenthetical; independent count of the real
  worktree is 14 modified + 9 new = 23 paths, and the live receipt itself is
  a separate path the enumeration undercounts.
- `F12 UNDECLARED_JSONSCHEMA_TEST_DEPENDENCY` — `tests/contract/
  test_contract_files.py` and/or its supporting fixtures import `jsonschema`
  and `referencing` for contract validation, but neither package is declared
  in `pyproject.toml`. A fresh interpreter without a pre-warmed environment
  fails at collection.
- `F13 FILE_SIZE_REPAIR_USES_UNAUTHORIZED_COMPRESSION` — `sql_ledger.py`'s
  reduction to 298 lines was achieved in part by compressing an existing
  docstring and two mutation methods unrelated to the event-list query
  extraction that Amendment 1 authorized. Amendment 1 authorized only the
  event-list query extraction into `_event_queries.py`, not mutation
  extraction and not general reformatting to satisfy the guard.
- `F14 OPENAPI_GOLDEN_ENVIRONMENT_DRIFT` — the repair's own evidence ran on
  Python 3.11.9 although `pyproject.toml` requires `>=3.12`. A fresh CPython
  3.13.12 run returns `5 failed, 647 passed, 55 skipped`, all five failures
  in OpenAPI golden/hash assertions traceable to floating FastAPI/Pydantic
  version ranges rather than to any P2C behavior change. A blind digest
  refresh is not an acceptable resolution.
- `F15 OPEN_WORK_SCHEMA_REJECTS_VALID_DOMAIN_RESPONSE` — a valid domain Task
  with `owner_id=None` returns HTTP 200 from the route, but the committed
  `task.schema.json` requires `owner_id` typed only `"string"`, rejecting the
  same response with `None is not of type 'string'`. The current test suite
  avoids the mismatch by always assigning an owner in fixtures instead of
  proving the schema accepts real route output. Both canonical
  `task.schema.json` and `customer-request.schema.json` also type `status`
  as a generic string with no enum vocabulary, so an invalid status value is
  not rejected either.
- `F16 SHIFT_LIST_UNBOUNDED` — a live probe of 501 shifts shows `GET /shifts`
  returns HTTP 200 with all 501 records, violating SPEC R4's 500-record
  ceiling.
- `F17 POSTGRES_LIMIT_PROOF_MISSING` — PostgreSQL 16 live evidence (55/55
  pass, clean cleanup) does not exercise the R4/R15 500/501 ceiling on any
  backend, live or otherwise.
- `F18 LIMIT_TEST_CLAIM_WITHOUT_TEST` — `tests/integration/
  test_p2c_read_api.py`'s docstring claims a 500-record ceiling test exists;
  the file contains no such test for shifts, events or open-work.
- `F19 PREMATURE_LOAD_BEARING_DOCUMENTATION` — `docs/cvf/
  CVF_CONTROL_MAPPING.md` already labels the new read surfaces
  "load-bearing" while the mandatory live-provider proof (R16/AC-16) remains
  `BLOCKED`, not `PASS`.

The repair worker stopped without touching any of these paths; this
addendum authorizes their repair.

## 2. Decision

Authorize exactly four additional C3a paths, bringing the exact ceiling from
25 to 29:

```text
pyproject.toml
packages/operations-ledger/src/operations_ledger/_shift_queries.py
packages/workspace-contracts/tasks/task.schema.json
packages/workspace-contracts/customers/customer-request.schema.json
```

No other path is opened by this addendum. All 25 paths authorized by the
parent Work Order and Amendment 1 remain in scope for repair; this addendum
adds four, not replaces or removes any.

### 2.1 `pyproject.toml` — dependency and interpreter policy only

`pyproject.toml` may be touched only to:

- declare `jsonschema` and `referencing` as dev dependencies, resolving F12;
- implement exactly one of the following two deterministic OpenAPI-drift
  policies — not a floating range paired with a version note, which does not
  make fresh dependency resolution reproducible and can silently reintroduce
  F14:

  a. **exact/bounded constraints** — narrow every package that a probe
     confirms actually changes generated OpenAPI bytes (at minimum FastAPI
     and Pydantic) to exact or tightly bounded version ranges in
     `pyproject.toml`, so a fresh install on CPython 3.13.12 deterministically
     resolves to the versions the golden output was computed against; or
  b. **environment-independent structural proof** — remove reliance on any
     dependency-sensitive full-document hash and replace it with a
     structural delta proof (as already required by R21) that does not
     depend on exact installed versions, while retaining negative protection
     against unrelated drift.

  If (a) is chosen, the SPEC/Work Order must require the worker to: probe
  and name which package(s) actually change the generated OpenAPI bytes;
  apply deterministic constraints rather than a blind hash refresh;
  fresh-install and evidence on CPython 3.13.12; record the exact resolved
  versions in the evidence; and prove that an unrelated path/method/schema/
  security mutation still fails the golden-chain test under the pinned
  versions.
- record CPython `3.13.12` as the review interpreter, resolving the F14
  environment mismatch (the repair evidence ran on 3.11.9 despite the
  `>=3.12` requirement already in the file).

This addendum does not authorize regenerating `uv.lock` or adopting a new
lock strategy in this tranche — that remains explicitly out of scope, per
the same reasoning Amendment 1 applied to lock-file residue. It does not
authorize a blind refresh of any OpenAPI golden hash under either policy;
F14's five failures must be diagnosed and resolved through the deterministic
constraints of policy (a) or the structural proof of policy (b), never a
hash rewrite that launders unrelated drift into the golden chain.

### 2.2 `_shift_queries.py` — narrow extraction only

`_shift_queries.py` may contain only the shift-query and shift-mutation code
extracted from `sql_ledger.py` that is strictly necessary to:

- restore the pre-repair formatting/readability that F13 found compressed
  (the docstring and the two unrelated mutation methods);
- bring both `sql_ledger.py` and this new helper to at most 300 physical
  lines each, without compressing either file to evade the guard;
- change no mutation behavior — the extracted methods must behave
  identically to their pre-extraction form, proven by the existing test
  suite continuing to pass unmodified in assertions.

This follows the same delegation pattern Amendment 1 already established for
`_event_queries.py`. `_shift_queries.py` must not become a second Ledger
implementation, must not own unrelated queries, and must not itself apply
compressed formatting to fit the guard — the point of this file is to let
`sql_ledger.py` return to normal formatting, not to relocate the compression
problem.

### 2.3 Canonical schema correction — nullable fields and enum vocabulary

`packages/workspace-contracts/tasks/task.schema.json` and
`packages/workspace-contracts/customers/customer-request.schema.json` may be
corrected only to:

- accept every value the route/domain model can actually return, including
  `owner_id: null` for `Task` and any other nullable field the canonical
  Pydantic model permits;
- constrain `status` to the canonical `TaskStatus`/`CustomerRequestStatus`
  enum members instead of a generic string, so an invalid status value is
  rejected;
- remain the single source `$ref`'d by `open-work.schema.json` — this
  addendum does not authorize forking a second vocabulary for open-work
  responses.

## 3. Boundaries retained

- The original R1-R19/AC-01-AC-19, and Amendment 1's R20-R22/AC-20-AC-22,
  remain binding in full.
- The Amendment 1 25-path ceiling becomes exactly 29 paths, adding only the
  four paths in §2.
- C3b remains gated; this addendum grants no frontend authority.
- No mutation route, authentication implementation, permission/data-scope
  model, database migration, continuity surface, roadmap or CVF core path is
  opened.
- The 300-line Python and 200-line TypeScript/JavaScript hard limits remain
  unchanged. No debt exception is authorized, and no file may satisfy either
  guard through minification, compressed formatting or suppressed
  discovery — this is a direct, named consequence of F13.
- `GET /shifts`, `GET /events` and each of the three open-work groups
  (`tasks`, `customer_requests`, `incidents`) must enforce SPEC R4's
  500-record ceiling (500 admitted, 501 refused with a controlled 4xx and no
  partial result) as the identical full matrix on InMemory, SQLite and
  PostgreSQL 16 live alike, each driven through the real API/`SqlLedger`
  dependency chain — not merely "at least one" surface or backend case; this
  addendum does not relax R4, it requires the repair to actually prove the
  full matrix on all three backends.
- The tranche may not describe P2C read controls as load-bearing or closed
  while R16/AC-16 live-provider evidence remains `BLOCKED`. If no provider
  credential is available, the repair must stop and report
  `BLOCKED_LIVE_PROVIDER_CREDENTIAL` rather than mock, simulate, or
  self-declare `REVIEW_PASS`.
- Claude remains worker-only: no stage, commit, push or self-approval.

## 4. Next control-chain move

Translate this decision into a SPEC amendment (Amendment 2) and an exact
Work Order amendment (Amendment 2), then obtain independent review of their
feasibility before repair resumes. This addendum authorizes no BUILD/repair
activity by itself.
