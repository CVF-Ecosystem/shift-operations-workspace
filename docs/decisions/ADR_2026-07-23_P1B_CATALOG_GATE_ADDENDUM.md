# ADR 2026-07-23 (Addendum) — The catalog gate belongs to the P1-B BUILD commit

- ADR id: `ADR-2026-07-23-P1B-CATALOG-GATE-ADDENDUM`
- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase at authoring time: `DESIGN` (amendment, mid-tranche)
- Risk: **R2** — unchanged from the parent tranche
- Status: **PROPOSED** — awaiting independent review and commit. **BUILD is
  paused; no further implementation file may change until this lands.**
- Amends: `docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md`
- Companion amendments:
  `docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC_AMENDMENT_1.md`,
  `docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER_AMENDMENT_1.md`
- Parent authorization commit (C1): `3e3df420bceca97d8047927a2098ea726d427aa8`
- Pre-BUILD continuity commit (C2): `1e56a72e2259f142fd26cc3035e81814f2856d35`

## 1. What happened

BUILD executed the authorized changed set and reached a **stop condition**, not
a defect. The implementation is behaviourally clean; the *authorization* is
internally inconsistent.

Running the required evidence produced:

```
python -m pytest -q
  291 passed, 1 failed
  FAILED tests/integration/test_catalog_drift_detection.py::test_check_passes_on_unmodified_repository

python scripts/generate_catalog.py --check          -> exit 1
python scripts/testing/validate_repository.py       -> exit 1
```

with this diagnostic:

```
CATALOG VERIFY: FAIL
  - catalog totals are stale: registry says {'modules': 20, 'code_loc': 3762,
    'code_files': 95, ...}, recomputed is {'modules': 20, 'code_loc': 3907,
    'code_files': 98, ...}
  - workspace-api: metrics are stale: registry says {'loc': 1818, ...},
    recomputed is {'loc': 1726, ...}
  - operations-domain: metrics are stale: registry says {'loc': 0,
    'code_files': 0, ...}, recomputed is {'loc': 237, 'code_files': 3, ...}
  - docs/catalog/MODULE_CATALOG.md does not match what MODULE_REGISTRY.json
    would generate - run `python scripts/generate_catalog.py --write`
```

The IMPLEMENTATION_WORKER correctly refused to regenerate the catalog (a
prohibited path in C3, stop condition S1), refused to weaken or skip the
failing test (S4), and stopped to report.

## 2. Root cause 1 — the catalog conflict is structural

`scripts/generate_catalog.py --check` was deliberately hardened by **P-FIX-5**
to recompute LOC/file metrics from the source tree and re-render
`MODULE_CATALOG.md` in memory, then diff both against disk. It has negative
tests (`tests/integration/test_catalog_drift_detection.py`) proving it is a
real gate rather than a shallow one. That is a feature working exactly as
designed.

`scripts/testing/validate_repository.py` *calls* that same catalog check, so
AC-13 inherits the failure — the two are not independent checks.

The parent WORK_ORDER placed `docs/catalog/**` on the **prohibited** list for
C3 (§4) and reserved catalog regeneration for C4/FREEZE (§11). But C3, by
definition, adds real Python source to `operations-domain` (0 → 237 LOC,
0 → 3 files) and removes it from `workspace-api` (1818 → 1726 LOC). Catalog
metrics are a **pure function of the source tree in the same commit**.

Therefore:

> With the catalog deferred to C4, **AC-12 (zero failures) and AC-13
> (validators PASS) cannot both be satisfied inside C3's allowlist, in any
> ordering of the work.** The parent WORK_ORDER authorized an unsatisfiable
> commit.

This is not recoverable by better implementation. It requires an amendment.

## 3. Decision 1 — move exactly two catalog paths from C4 into C3

**`docs/catalog/MODULE_REGISTRY.json` and `docs/catalog/MODULE_CATALOG.md`
move from the C4 allowlist into the C3 allowlist.** They are removed from C4
entirely; C4 retains only the roadmap, `IMPLEMENTATION_STATUS.json`, and the
continuity/closure surfaces.

Rationale: a commit should leave the tree green. Metrics describing the source
belong in the same commit as the source that produced them — separating them
guarantees a red tree at C3 and breaks both `git bisect` and the AC-18 rollback
rehearsal (which asserts the suite returns to a clean baseline).

### 3.1 What may change inside those two files

Bounded deliberately, because "the catalog is now in scope" must not become a
licence to restate the project's status:

- `operations-domain`: `stub` → **`partial`**. **Never `enforced`** — the
  blueprint areas (incidents, handovers, reports, approvals) still have no
  models, which is precisely what the registry legend calls "some runtime code
  exists but the intended capability/chain is incomplete".
- `operations-domain`: `enforcement`, `tests`, `next_step` and, if needed,
  `depends_on`/`contract` updated to observed source truth. The current text —
  *"None yet. Domain models currently live inline in
  workspace-api/domain/models.py."* — becomes false the moment C3 lands and
  must not survive.
- `workspace-api`: wording corrected wherever it still asserts that the domain
  models or the lifecycle guards are defined inside that app. In particular
  *"domain/lifecycle.py enforces data-state, task-status, and
  customer-request-status transitions"* is no longer accurate: those guards now
  live in `operations_domain.lifecycle` and are re-exported.
- `metrics` blocks and `MODULE_CATALOG.md`: **generator output only.** Produced
  by `python scripts/generate_catalog.py --write`, never hand-edited. This
  constraint is inherited unchanged from the registry's own description field.

### 3.2 What must NOT change

No other module entry, no status other than `operations-domain`'s, no
`cvf_controls` vocabulary, no roadmap item, and nothing in
`IMPLEMENTATION_STATUS.json` — that file stays a C4 concern.

## 4. Root cause 2 — the path count conflated "allowed" with "required"

The parent WORK_ORDER §3.1 stated a total of **43 paths** and made a differing
total a stop condition. That treated the allowlist as a set of *mandatory*
edits. It is not: an allowlist is a **ceiling**, and three of the listed files
must stay untouched *by this tranche's own design*:

| File | Why it must not change |
|---|---|
| `tests/cvf/test_auth_login.py` | Its only `workspace_api.domain` import is `User`, and **`User` does not move** (ADR §2.2, Rule B). |
| `tests/cvf/test_ledger_protocol.py` | Its only such import is the shim namespace `domain_models`, which **Rule A requires to stay** so the injected `SqlLedger(models=...)` namespace still exposes `User`. |
| `tests/integration/test_sql_ledger_integrity.py` | Same as above — namespace-only import, Rule A. |

Editing them to reach an arithmetic target would have been churn manufactured
to satisfy a number, and for the two Rule A files it would have actively broken
`operations_ledger._rows.build_user`. The IMPLEMENTATION_WORKER was right to
leave them alone and report the discrepancy instead.

## 5. Decision 2 — the expected C3 changed set is 42 paths

```
  43   parent WORK_ORDER allowlist
-  3   intentionally unchanged (table in §4)
= 40   current C3 working tree
+  2   docs/catalog/MODULE_REGISTRY.json, docs/catalog/MODULE_CATALOG.md
= 42   amended expected C3 changed set
```

The three unchanged files **remain on the allowlist** — they stay permitted,
they are simply not required. The allowlist is explicitly re-characterised as a
ceiling, so "fewer paths than listed, with every touched path on the list" is
conformant; "any path not on the list" remains stop condition S1.

## 6. Alternatives considered

### A1 — Keep the catalog in C4; accept a red tree at C3 (rejected)

Leaves `main` failing between C3 and C4. It breaks `git bisect`, and it breaks
AC-18: the rollback rehearsal asserts the reverted tree returns to the
**221 passed** baseline, which cannot be asserted from a knowingly-red starting
point. It also contradicts `CONTRIBUTING.md`'s definition of done ("tests liên
quan pass").

### A2 — Regenerate the catalog in a separate commit immediately after C3 (rejected)

Same red-tree window as A1, merely shorter, plus it splits one mechanical
change across two commits for no reviewability gain. The metrics are not an
independent decision; they are derived data.

### A3 — Relax or skip the catalog drift test for this tranche (rejected outright)

The gate was built by P-FIX-5 *because* an earlier agent's catalog check was
shallow enough to pass while drifting. Weakening it to make a tranche green is
the exact anti-pattern this project's review history documents twice. It is
also stop condition S4.

### A4 — Manufacture edits in the three files to reach 43 (rejected)

Churn for a number, and for two of the three it would introduce a real runtime
regression. See §4.

## 7. Consequences

### 7.1 Accepted

- C3 becomes a slightly larger commit that includes derived catalog data. This
  is the price of every commit leaving the tree green.
- `operations-domain` becomes `partial` in the same commit that makes it true,
  so the registry never asserts a state the filesystem does not have.
- C4 shrinks to roadmap + `IMPLEMENTATION_STATUS.json` + continuity/closure.

### 7.2 Explicitly unchanged

Every other boundary from the parent ADR/SPEC/WORK_ORDER survives verbatim:

- `packages/operations-ledger/**` still requires a **zero-line diff**; the
  `SqlLedger(models=...)` seam is still not refactored;
- `User` still does not move;
- no API contract, response schema, OpenAPI output, database schema, migration,
  lifecycle semantics, enum value, or CVF gate behaviour changes;
- no change to authentication, approval, or `known-principals.yaml` — High
  Finding #4 remains **OPEN**;
- lanes 2–4 (known-principals ↔ users, P2-A incidents/handovers, P2-C
  frontend) remain closed and must not be opened, scoped, or started;
- no provider call and no secret read; the tranche still asserts no
  AI-governance claim, so Mandatory Governance Proof is still not triggered;
- P1-B is still **not complete**, the Phase 1 exit gate is still **not met**,
  and the PostgreSQL live round-trip remains an open pre-ship limitation;
- `cd36b27` and all history remain untouched.

### 7.3 Rollback

Unchanged in kind. C3 remains a single revertable commit; adding two derived
files to it does not alter that. `C3_PARENT` is still the reference point, and
the rehearsal still runs in a temporary worktree outside the primary workspace.

## 8. Process note

This amendment exists because the control chain worked. The stop condition was
raised by the implementer against their own work, the reviewer confirmed it,
and the fix is being authorized through DESIGN → SPEC → WORK_ORDER before any
further code moves — rather than being absorbed silently into a BUILD commit,
which is the failure mode `cd36b27` recorded.

Role route for the amendment: IMPLEMENTATION_WORKER → SPEC_AUTHOR →
WORK_ORDER_AUTHOR (this document and its two companions), with Codex retaining
independent REVIEWER and COMMIT_STEWARD. The transition back to
IMPLEMENTATION_WORKER happens only **after** the amendment is reviewed and
committed.
