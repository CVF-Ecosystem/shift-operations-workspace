# ADR Addendum — P2-C C3a Repair Scope

- ID: `ADR-2026-07-29-P2C-READ-API-C3A-REPAIR-SCOPE`
- Parent:
  `docs/decisions/ADR_2026-07-28_P2C_OPERATIONS_CONSOLE_READ_SLICE.md`
- Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Risk: R2
- Phase: DESIGN
- Status: `DESIGN_COMPLETE — REPAIR_SCOPE_ONLY`

## 1. Trigger

The interrupted C3a BUILD exposed two authorization defects:

1. adding the required SQL event-list query raised
   `packages/operations-ledger/src/operations_ledger/sql_ledger.py` from its
   pre-BUILD 299 lines to 325 lines, violating the 300-line hard guard; and
2. the additive P2-C OpenAPI delta necessarily invalidates the retained
   mechanical golden-chain assertions in
   `tests/unit/test_p2b_openapi_contract.py`, but that test was omitted from
   the original C3a ceiling.

The worker stopped without modifying either unlisted repair path.

## 2. Decision

Authorize exactly two additional C3a paths:

```text
packages/operations-ledger/src/operations_ledger/_event_queries.py
tests/unit/test_p2b_openapi_contract.py
```

`_event_queries.py` owns the SQL event-query/select/materialization mechanics
needed by `SqlLedger.list_events_for_shift`. `sql_ledger.py` remains the
public ledger implementation and delegates to that helper. This follows the
existing `_evidence.py`, `_rows.py`, `_incident_store.py` and
`_handover_store.py` split pattern.

The OpenAPI golden-chain test may change only to prove the reviewed additive
P2-C delta mechanically. A blind digest refresh is prohibited. After removing
the exact P2-C paths, schema and `GET /shifts` read-security delta, the
document must reduce to the exact pre-P2-C baseline. Unrelated mutation,
schema or security drift must still fail.

## 3. `uv.lock` disposition

Codex's recorded G5 check immediately before the interrupted BUILD showed a
clean worktree with no `uv.lock`. The file appeared only after BUILD began,
despite carrying older filesystem metadata. It is therefore a generated or
materialized C3a attempt artifact, not a pre-existing operator artifact at
the governed checkpoint.

`uv.lock` is not authorized, must not be staged or committed, and may be
removed by the repair worker as exact out-of-scope BUILD residue. No other
untracked path receives deletion authority from this finding.

## 4. Boundaries retained

- The original R1-R19 and AC-01-AC-19 remain binding.
- The original 23-path C3a ceiling becomes 25 paths, adding only the two
  paths above.
- C3b remains gated.
- No mutation route, authentication implementation, permission/data-scope
  model, database migration, continuity surface, roadmap or CVF core path is
  opened.
- The 300-line Python and 200-line TypeScript/JavaScript hard limits remain
  unchanged. No debt exception or compressed formatting is authorized.
- Claude remains worker-only: no stage, commit, push or self-approval.

## 5. Next control-chain move

Translate this decision into a SPEC amendment and exact Work Order amendment,
then independently review their feasibility before repair resumes.
