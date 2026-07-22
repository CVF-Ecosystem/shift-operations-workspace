# SPEC AMENDMENT 1 — P1-B Operations-Domain Extraction (catalog gate)

- Amendment id: `SPEC-P1B-AMENDMENT-1`
- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase at authoring time: `SPEC` (amendment, mid-tranche)
- Risk: **R2** — unchanged
- Status: **PROPOSED** — not approved, not built against
- Amends: `docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC.md`
- Design: `docs/decisions/ADR_2026-07-23_P1B_CATALOG_GATE_ADDENDUM.md`
- Work order amendment:
  `docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER_AMENDMENT_1.md`

## 1. Scope of this amendment

This amendment supersedes **only** the parts of the parent SPEC listed in §2,
and **only** to resolve the catalog/path-count conflict found during BUILD.
Everything else in the parent SPEC — R1–R8, AC-01…AC-12, AC-15…AC-18, §5 out of
scope, §8 live-evidence boundary, §9 definition of done — remains in force
**verbatim and unamended**.

Nothing here changes what the code does. No API contract, response schema,
OpenAPI output, database schema, migration, lifecycle semantics, enum value, or
CVF gate behaviour is affected. No provider call is made or permitted, and no
secret is read.

## 2. Superseded surface

| Parent element | Disposition |
|---|---|
| **AC-13** | **Superseded** by §4 below (validator dependency made explicit; catalog must PASS within C3). |
| **AC-14** | **Superseded** by §5 below (status change moves from FREEZE/C4 into C3). |
| All other ACs and requirements | Unchanged. |

## 3. Findings that forced this amendment

### 3.1 The catalog gate cannot be deferred

BUILD produced:

```
python -m pytest -q                              -> 291 passed, 1 failed
  FAILED tests/integration/test_catalog_drift_detection.py::
         test_check_passes_on_unmodified_repository
python scripts/generate_catalog.py --check       -> exit 1
python scripts/testing/validate_repository.py    -> exit 1
```

```
CATALOG VERIFY: FAIL
  - catalog totals are stale: registry code_loc 3762 -> recomputed 3907,
    code_files 95 -> 98
  - workspace-api: loc 1818 -> recomputed 1726
  - operations-domain: loc 0 -> recomputed 237, code_files 0 -> 3
  - docs/catalog/MODULE_CATALOG.md does not match what MODULE_REGISTRY.json
    would generate
```

**Validator dependency, stated explicitly because the parent SPEC treated the
two as independent:** `scripts/testing/validate_repository.py` invokes the same
catalog check. A catalog failure therefore fails **both** AC-13 checks at once;
they cannot be satisfied separately.

Catalog metrics are a pure function of the source tree in the same commit.
Extracting a package necessarily changes them. With `docs/catalog/**` prohibited
in C3, parent AC-12 (zero failures) and parent AC-13 (validators PASS) were
**jointly unsatisfiable** — an authorization defect, not an implementation one.

### 3.2 Three allowlisted files must stay unchanged

`tests/cvf/test_auth_login.py` (imports only `User`, which does not move),
`tests/cvf/test_ledger_protocol.py` and
`tests/integration/test_sql_ledger_integrity.py` (import only the shim
namespace `domain_models`, which Rule A requires to stay so the injected
`SqlLedger(models=...)` namespace still exposes `User`).

Editing them would be churn to satisfy an arithmetic target, and for the two
Rule A files would break `operations_ledger._rows.build_user`.

## 4. AC-13 (superseded) — repository validators, with the catalog inside C3

**AC-13.** After C3's changes are applied, all four of the following exit `0`:

| # | Command | Requirement |
|---|---|---|
| 1 | `python scripts/generate_catalog.py --check` | PASS |
| 2 | `python scripts/testing/validate_repository.py` | PASS — **note it re-runs check 1 internally; a catalog failure fails this too** |
| 3 | `python scripts/check_session_state.py` | PASS |
| 4 | `python scripts/check_file_size.py` | PASS |

To make 1 and 2 achievable, **`docs/catalog/MODULE_REGISTRY.json` and
`docs/catalog/MODULE_CATALOG.md` are now part of the C3 changed set**, subject
to §5. Parent AC-12 is unchanged and still requires the full suite to report
**≥ 221 passed with zero failures and zero errors** — which now includes
`tests/integration/test_catalog_drift_detection.py` passing.

## 5. AC-14 (superseded) — evidence-led catalog update, now in C3

**AC-14.** The catalog is updated inside C3, from observed source truth only:

**AC-14.1 — status.** `operations-domain` moves `stub` → **`partial`**, and
only if `packages/operations-domain/src/**` really contains non-empty Python
source (`metrics.loc > 0` after regeneration). It **must not** become
`enforced`: incidents, handovers, reports and approvals still have no models,
which is exactly the registry legend's definition of `partial` ("some runtime
code exists but the intended capability/chain is incomplete").

**AC-14.2 — descriptive fields.** `operations-domain`'s `enforcement`, `tests`
and `next_step` (and `depends_on`/`contract` if warranted) are updated to match
source truth. Specifically, the current text
`"None yet. Domain models currently live inline in
workspace-api/domain/models.py."` is false once C3 lands and **must not
survive**.

**AC-14.3 — workspace-api wording.** Any `workspace-api` text asserting that
the domain models or lifecycle guards are defined inside that app is corrected.
Specifically `"domain/lifecycle.py enforces data-state, task-status, and
customer-request-status transitions"` must be corrected: those guards now live
in `operations_domain.lifecycle` and are re-exported through the shim.

**AC-14.4 — generator-only outputs.** `MODULE_CATALOG.md` is produced solely by
`python scripts/generate_catalog.py --write`. Every `metrics` block is
generator output. Neither is hand-edited — a hand-edit is detectable by the
drift test and is stop condition S8.

**AC-14.5 — no other catalog change.** No other module's status, no other
module entry, no `cvf_controls` vocabulary change, and no `status_legend`
change. `IMPLEMENTATION_STATUS.json` is **not** touched in C3; it remains C4.

**AC-14.6 — order of operations.** Hand-edit the registry's `modules` block
first, then run `--write` to regenerate `metrics` and `MODULE_CATALOG.md`, then
re-run `--check`. Running `--write` before the hand-edit would bake the stale
description into the generated Markdown.

## 6. Changed-set expectation (informative here; normative in the WORK_ORDER amendment)

```
  43   parent allowlist
-  3   intentionally unchanged (§3.2)
+  2   docs/catalog/MODULE_REGISTRY.json, docs/catalog/MODULE_CATALOG.md
= 42   expected C3 changed set
```

The allowlist is a **ceiling, not a checklist**. Touching fewer paths than
listed is conformant provided every touched path is on the list; touching any
path not on the list remains stop condition S1.

## 7. Boundary — unchanged and restated so it cannot drift

This amendment does **not** relax anything. Still in force:

- `packages/operations-ledger/**` — **zero-line diff** (parent AC-10/R6);
- the `SqlLedger(models=...)` seam and the `Ledger` Protocol are not refactored;
- `User` does not move (parent R4.4);
- shim class identity per module pair (parent AC-04a/AC-04b, §4.1);
- serialization/enum/lifecycle/OpenAPI parity via canonical bytes (parent
  AC-06/AC-07/AC-08/AC-09, §4.4);
- repository-scoped import isolation (parent AC-01/AC-15, §4.3);
- **AC-16 unchanged** — PostgreSQL live round-trip remains an open pre-ship
  limitation; nothing here claims a Phase 1 exit gate. Ticking a roadmap item
  is not a phase gate;
- **AC-17 unchanged** — no provider call, no secret read, no credential in the
  diff;
- **AC-18 unchanged** — rollback rehearsal in a temporary worktree/clone
  outside the primary workspace, scoped to C3's paths against `C3_PARENT`, with
  C1/C2 required to survive and the suite returning to the **221 passed**
  baseline;
- prohibited paths otherwise unchanged: `.cvf/**`, `database/**`,
  `packages/cvf-runtime/**`, `packages/cvf-application-profile/**` (including
  `known-principals.yaml`), `workspace_api/auth/**`, `apps/workspace-web/**`,
  `infrastructure/**`;
- lanes 2–4 remain closed;
- High Finding #4 remains **OPEN**;
- P1-B is **not complete** and must not be described as complete.

## 8. Definition of done for the amended tranche

Parent §9 plus:

- the two catalog paths are updated inside C3 under §5;
- `--check` and `validate_repository.py` both exit `0`;
- the full suite reports **≥ 221 passed, 0 failed, 0 errors**;
- the C3 changed set is exactly the 42 paths of §6, all within the amended
  allowlist;
- C4 contains no catalog path.
