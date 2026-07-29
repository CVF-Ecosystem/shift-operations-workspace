# WORK ORDER Amendment 1 — P2-C C3a Repair Scope

- ID: `WO-P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28-AMENDMENT-1`
- Parent:
  `docs/work_orders/P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER.md`
- Design addendum:
  `docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM.md`
- SPEC amendment:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC_AMENDMENT_1.md`
- Risk: R2
- Status: `APPROVED — C3a REPAIR ONLY; C3b remains gated`

## 1. Exact ceiling expansion

The original C3a ceiling is expanded from 23 to exactly 25 possible paths by
adding:

```text
packages/operations-ledger/src/operations_ledger/_event_queries.py
tests/unit/test_p2b_openapi_contract.py
```

Every original C3a path, prohibition, gate, stop condition and claim boundary
remains unchanged. No wildcard or third additional path is granted.

## 2. Authorized repair findings

Claude may transition to `REPAIR_WORKER` for the exact reviewer findings
reported after the interrupted BUILD:

- out-of-ceiling `uv.lock` residue;
- unrecorded worker-role evidence;
- `sql_ledger.py` file-size failure;
- nondeterministic UUID tie expectation;
- invalid Incident fixtures;
- incomplete OpenAPI delta/golden chain;
- weak generic-object open-work schema and untyped FastAPI response;
- missing bounded CVF-control documentation;
- catalog/validator drift caused by the unfinished source set.

Repair remains limited to the amended 25-path ceiling. Continuity remains
closer/reviewer-owned; if recording worker-role evidence requires a
continuity edit, the worker reports it for Codex instead of editing an
excluded path.

## 3. Exact helper boundary

`_event_queries.py` may contain only the SQL event-list query, deterministic
ordering/materialization support and directly required imports. It may not
own mutations, other aggregate queries, schema definitions or authorization.
`SqlLedger.list_events_for_shift` must delegate without changing its public
contract.

## 4. Exact OpenAPI-test boundary

`test_p2b_openapi_contract.py` may change only to preserve and extend the
mechanical golden-chain proof through P2-C. It must not:

- accept unrelated OpenAPI drift;
- delete or weaken predecessor incident/handover assertions;
- replace structural proof with a single current-document hash;
- conceal a mutation-route or authentication-policy change.

## 5. `uv.lock`

The reviewer confirms `uv.lock` was absent at G5 and appeared during the
interrupted BUILD. The worker may remove that exact untracked residue. It is
not part of the 25-path ceiling because it must not survive, stage or commit.
No broad cleanup authority is granted.

## 6. Gates

Before returning to independent review, the worker must additionally prove:

- AC-20 through AC-22 PASS;
- both ledger files respect the 300-line hard limit;
- predecessor and new OpenAPI tests PASS together;
- exact changed set is a subset of the amended 25 paths;
- `uv.lock` and all unauthorized residue are absent;
- zero staged paths.

All original focused/full/PostgreSQL/provider/repository/cleanup gates remain
mandatory. The worker stops at:

`READY_FOR_INDEPENDENT_P2C_READ_API_BUILD_REVIEW`

and does not self-approve, stage, commit, push or begin C3b.

## 7. Amendment commit boundary

This governance amendment is committed separately from the dirty BUILD using
only:

```text
docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM.md
docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC_AMENDMENT_1.md
docs/work_orders/P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER_AMENDMENT_1.md
docs/decisions/P2C_OPERATIONS_CONSOLE_READ_SLICE_AMENDMENT_1_AUTHORIZATION_REVIEW.md
```

No worker-authored implementation/test/documentation path may be staged in
the amendment commit.
