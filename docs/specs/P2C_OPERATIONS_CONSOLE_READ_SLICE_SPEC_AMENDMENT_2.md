# SPEC Amendment 2 — P2-C C3a Repair Scope

- ID: `P2C-OPERATIONS-CONSOLE-READ-SLICE-SPEC-AMENDMENT-2`
- Parent:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC.md`
- Prior amendment:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC_AMENDMENT_1.md`
- Design addendum:
  `docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM_2.md`
- Risk: R2
- Status: `SPEC_COMPLETE — REPAIR_SCOPE_ONLY`

All parent requirements (R1-R19/AC-01-AC-19) and Amendment 1 requirements
(R20-R22/AC-20-AC-22) remain binding.

## R23 — declared, reproducible OpenAPI-affecting dependency policy

`pyproject.toml` must declare `jsonschema` and `referencing` as dev
dependencies so that `tests/contract/test_contract_files.py` and any other
test importing them collects successfully in a fresh CPython 3.13.12
environment with no pre-warmed cache.

`pyproject.toml` must also implement exactly one of the following two
deterministic OpenAPI-drift policies for packages whose version range
affects generated OpenAPI output (at minimum FastAPI and Pydantic). A
floating range paired with a documented version-assumption note is not
acceptable under either option, because it does not make fresh dependency
resolution reproducible and can silently reintroduce F14:

- **(a) exact/bounded constraints** — narrow every package a probe confirms
  actually changes generated OpenAPI bytes to exact or tightly bounded
  version ranges, so a fresh install on CPython 3.13.12 deterministically
  resolves to the versions the golden output was computed against; or
- **(b) environment-independent structural proof** — remove reliance on any
  dependency-sensitive full-document hash and rely instead on the
  structural delta proof already required by R21, which does not depend on
  exact installed versions.

Either policy must retain a negative-protection mechanism that fails loudly
on unrelated API drift rather than silently passing after a blind hash
refresh. If policy (a) is chosen, the worker must additionally: probe and
name which package(s) actually change the generated OpenAPI bytes; apply
deterministic constraints, never a blind hash refresh; fresh-install and
gather evidence on CPython 3.13.12; record the exact resolved versions in
the evidence; and prove that an unrelated path/method/schema/security
mutation still fails the golden-chain test under the pinned versions.

This requirement does not authorize regenerating `uv.lock` or changing lock
strategy in this tranche. CPython `3.13.12` is the review interpreter for
all evidence required by this amendment; it does not authorize any
production runtime-version change beyond the pre-existing `>=3.12` floor
already in `pyproject.toml`.

## R24 — OpenAPI golden proof survives real dependency resolution

The five golden/hash failures observed under fresh CPython 3.13.12 (`5
failed, 647 passed, 55 skipped`) must be root-caused to specific
FastAPI/Pydantic version-range behavior, not assumed. The repair must
resolve them under whichever single policy R23 selects:

- under policy (a), narrow the dependency range so the previously-golden
  output is what a fresh install actually produces, with evidence the
  narrowed range still satisfies every other constraint in
  `pyproject.toml` and the exact resolved versions are recorded; or
- under policy (b), update the golden proof through the same mechanical
  delta-proof discipline Amendment 1 required for R21 (structural
  subtraction back to a named baseline, not a hash literal edit), removing
  reliance on a dependency-sensitive full-document hash.

Either path must leave the negative-protection property intact: a test must
still fail for any unrelated path, mutation operation, schema or security
change, on the resolved dependency set. A blind digest refresh satisfies
neither policy.

## R25 — shift-query/mutation extraction

`SqlLedger`'s shift-query and shift-mutation implementation may delegate to:

```text
packages/operations-ledger/src/operations_ledger/_shift_queries.py
```

The split must:

- restore the formatting/readability of the code that was compressed in the
  prior repair (the docstring and the two unrelated mutation methods
  identified by finding F13) rather than carrying the compression forward
  into the new file;
- bring both `sql_ledger.py` and `_shift_queries.py` to at most 300 physical
  lines each;
- preserve exact existing mutation behavior — no behavioral change to any
  shift mutation method, proven by the existing test suite passing unchanged
  in its assertions;
- not turn `_shift_queries.py` into a second Ledger implementation or give it
  ownership of queries/mutations unrelated to shifts;
- not apply compressed formatting, minification or line-merging to either
  file to satisfy the 300-line guard.

## R26 — canonical schema correctness for nullable fields and status enums

`packages/workspace-contracts/tasks/task.schema.json` and
`packages/workspace-contracts/customers/customer-request.schema.json` must
each validate every response the corresponding route/domain model can
actually produce, including nullable fields such as `Task.owner_id`.

Both schemas must constrain their `status` field to the canonical
`TaskStatus` and `CustomerRequestStatus` enum members respectively (not a
generic `"type": "string"`), so a value outside the canonical lifecycle is
rejected.

`packages/workspace-contracts/open-work/open-work.schema.json` continues to
`$ref` these two canonical schemas (and the existing `incident.schema.json`)
unchanged in that respect — this requirement corrects the referenced
schemas, it does not fork a parallel open-work-only vocabulary.

Required test evidence:

- a positive test that validates an actual `GET /shifts/{shift_id}/open-work`
  (or task-read) route response containing a real unassigned task
  (`owner_id=None`) against `task.schema.json`, proving the schema accepts
  it;
- negative tests proving an invalid `Task.status` value and an invalid
  `CustomerRequest.status` value are each rejected by their respective
  schema.

## R27 — enforced 500-record ceiling across all three read surfaces and all backends

SPEC R4's 500-record ceiling must be proven as the identical full matrix,
not merely asserted, and not merely sampled with "at least one" case per
backend. The canonical matrix is:

- **InMemoryLedger:**
  - `GET /shifts`: 500 admitted (HTTP 200, full set), 501 refused
    (controlled HTTP 409/422, no partial result);
  - `GET /events?shift_id=...`: 500 admitted, 501 refused;
  - open-work `tasks` group: 500 admitted, 501 refused;
  - open-work `customer_requests` group: 500 admitted, 501 refused;
  - open-work `incidents` group: 500 admitted, 501 refused.
- **SQLite:** the identical full matrix above, driven through the real
  API/`SqlLedger` dependency chain (not a row-count assertion against the
  database alone).
- **PostgreSQL 16 live:** the identical full matrix above, driven through
  the real API/`SqlLedger` dependency chain, with a controlled 409/422 for
  every 501 case, no partial response, and exact container/anonymous-volume
  cleanup after the run.

This matrix is exact and binding on all three backends alike; no backend or
surface is exempted, and no evidence may substitute a partial ("at least
one case") PostgreSQL proof for this full matrix. The limit check must be
proven on the same path production traffic would use, not only against the
database directly.

Test files must not claim a limit/ceiling test exists in a docstring unless
the file contains that test; `tests/integration/test_p2c_read_api.py`'s
existing docstring claim must either be backed by a real 500/501 test or
removed.

## Additional acceptance criteria

- **AC-23:** `pyproject.toml` declares `jsonschema` and `referencing` as dev
  dependencies; a fresh CPython 3.13.12 environment with no pre-warmed cache
  installs from the amended file and collects the full test suite with zero
  collection errors.
- **AC-24:** `pyproject.toml` implements exactly one of R23's two
  deterministic policies (never a floating range plus a version note); under
  it, fresh CPython 3.13.12 evidence shows the previously-observed five
  golden/hash failures resolved without a blind digest refresh; if policy
  (a) was chosen, the exact resolved versions are recorded and an unrelated
  path/method/schema/security mutation is proven to still fail the
  golden-chain test; the negative-protection property is demonstrated either
  way.
- **AC-25:** `_shift_queries.py` exists, both it and `sql_ledger.py` are at
  most 300 lines each with restored (not compressed) formatting, and every
  existing shift-mutation test passes with unchanged assertions.
- **AC-26:** `task.schema.json` and `customer-request.schema.json` each
  accept a real captured route response containing a null nullable field
  and each reject an out-of-enum `status`; `open-work.schema.json`'s
  `$ref`-based reuse is unchanged.
- **AC-27:** the full R27 matrix — `GET /shifts`, `GET /events` and each of
  the three open-work groups, at both 500 (admitted, HTTP 200) and 501
  (refused, controlled 4xx, no partial result) — passes identically on
  InMemory, SQLite and PostgreSQL 16 live, with the SQLite and PostgreSQL
  cases each driven through the real API/`SqlLedger` path and PostgreSQL
  cleanup exact; no backend or surface is proven by only a partial sample.
- **AC-28:** the real Alibaba provider call required by R16/AC-16 either
  completes with a sanitized `Overall outcome: PASS` receipt showing exactly
  one call after the admitted JWT reads and zero calls for every refusal, or
  the repair stops and reports `BLOCKED_LIVE_PROVIDER_CREDENTIAL` — no
  `REVIEW_PASS` or "load-bearing" documentation claim is made while the
  receipt remains `BLOCKED`.
- **AC-29:** `docs/cvf/CVF_CONTROL_MAPPING.md` describes the P2C read
  surfaces as load-bearing/closed only if AC-28's receipt is `PASS`;
  otherwise it states the bounded, non-load-bearing status honestly.

## Claim boundary

This amendment repairs feasibility and correctness only. It does not widen
the read-console product claim, authorize C3b, or reduce any live
PostgreSQL/provider, regression, cleanup, secret-safety or independent-review
requirement carried over from the parent SPEC and Amendment 1.
