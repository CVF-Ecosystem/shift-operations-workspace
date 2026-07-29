# SPEC Amendment 1 — P2-C C3a Repair Scope

- ID: `P2C-OPERATIONS-CONSOLE-READ-SLICE-SPEC-AMENDMENT-1`
- Parent:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC.md`
- Design addendum:
  `docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM.md`
- Risk: R2
- Status: `SPEC_COMPLETE — REPAIR_SCOPE_ONLY`

All parent requirements and AC-01 through AC-19 remain binding.

## R20 — SQL event-query split

`SqlLedger.list_events_for_shift` must delegate SQL query/materialization work
to:

```text
packages/operations-ledger/src/operations_ledger/_event_queries.py
```

The split must preserve:

- single-shift filtering;
- deterministic order: non-null `starts_at`, ascending `starts_at`, ascending
  `str(event_id)`;
- evidence materialization;
- transaction/unit behavior and backend parity;
- the existing public Ledger method.

Both touched files must be at most 300 physical lines. The helper may not
become a second Ledger implementation or own unrelated queries.

## R21 — additive OpenAPI golden-chain proof

`tests/unit/test_p2b_openapi_contract.py` may be updated only to extend its
mechanical delta chain for P2-C. Tests must distinguish:

- new `GET /events`;
- new `GET /shifts/{shift_id}/open-work`;
- the new JWT security requirement on existing `GET /shifts`;
- new P2-C-reachable schema components.

Removing those exact deltas from the current OpenAPI document must reproduce
the exact pre-P2-C baseline. A test must fail for an unrelated path, mutation
operation, schema or security change. Updating only a digest constant is not
acceptable evidence.

## R22 — generated lock residue

Because `uv.lock` was absent at the independently verified G5 checkpoint and
appeared only during the interrupted BUILD:

- remove only that exact untracked file;
- do not stage or commit it;
- do not change dependency manifests or lock strategy;
- confirm no other untracked residue is removed under this authority.

## Additional acceptance criteria

- **AC-20:** `_event_queries.py` provides the bounded helper; both it and
  `sql_ledger.py` pass the 300-line guard and all R3 parity/evidence tests.
- **AC-21:** the extended OpenAPI chain mechanically proves only the exact
  P2-C additive delta and retains negative protection against unrelated drift.
- **AC-22:** `uv.lock` is absent, unstaged and uncommitted; no other
  user-owned or untracked path is removed.

## Claim boundary

This amendment repairs feasibility only. It does not widen the read-console
product claim, authorize C3b, or reduce any live PostgreSQL/provider,
regression, cleanup, secret-safety or independent-review requirement.
