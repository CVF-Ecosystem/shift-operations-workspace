# WORK ORDER AMENDMENT 1 — P1-B Operations-Domain Extraction (catalog gate)

- Amendment id: `WO-P1B-AMENDMENT-1`
- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase at authoring time: `WORK_ORDER` (amendment, mid-tranche)
- Risk: **R2** — REVIEWER remains independent from IMPLEMENTATION_WORKER
- Status: **DRAFT — NOT COMMITTED. BUILD REMAINS PAUSED.**
- Amends: `docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER.md`
- Design: `docs/decisions/ADR_2026-07-23_P1B_CATALOG_GATE_ADDENDUM.md`
- Spec amendment:
  `docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC_AMENDMENT_1.md`
- C1 `3e3df420bceca97d8047927a2098ea726d427aa8` · C2 `1e56a72e2259f142fd26cc3035e81814f2856d35`

## 1. Scope

This amendment supersedes **only** parent §§3.1, 6, 8, 10 and 11, and **only**
within the catalog / path-count conflict. Parent §§1, 2, 4, 5, 7, 9, 12, 13 —
objective, roles, prohibited paths, out-of-scope list, pre-BUILD gates, git
discipline, rollback plan and checkpoint history — remain in force **verbatim**.

## 2. Why (summary; full text in the ADR addendum and SPEC amendment)

BUILD hit a stop condition. `generate_catalog.py --check` recomputes metrics
from source (hardened by P-FIX-5, negative-tested), and
`validate_repository.py` **calls that same check**. C3 necessarily changes those
metrics (`operations-domain` 0 → 237 LOC / 0 → 3 files; `workspace-api`
1818 → 1726 LOC). With `docs/catalog/**` prohibited in C3, parent AC-12 and
AC-13 were jointly unsatisfiable.

Separately, three allowlisted files must stay untouched by design, so the
parent's "43 paths" total wrongly treated a ceiling as a checklist.

## 3. Parent §3.1 superseded — amended C3 allowlist

Everything in parent §3.1 stands, **plus** the following two paths, which move
out of C4 and into C3:

```
docs/catalog/MODULE_REGISTRY.json
docs/catalog/MODULE_CATALOG.md
```

### 3.1 Bounded permission for those two files

- `operations-domain`: `stub` → **`partial`**. **`enforced` is prohibited.**
- `operations-domain`: `enforcement`, `tests`, `next_step` (and
  `depends_on`/`contract` if warranted) updated to observed source truth. The
  string `"None yet. Domain models currently live inline in
  workspace-api/domain/models.py."` must not survive.
- `workspace-api`: correct any wording asserting the models/lifecycle live in
  that app — in particular `"domain/lifecycle.py enforces data-state,
  task-status, and customer-request-status transitions"`.
- `MODULE_CATALOG.md` and every `metrics` block: **generator output only**, via
  `python scripts/generate_catalog.py --write`. Hand-editing either is S8.
- Order: hand-edit the registry `modules` block → `--write` → `--check`.
- **No other module entry, status, `cvf_controls` entry, or `status_legend`
  change. `IMPLEMENTATION_STATUS.json` is NOT touched in C3.**

### 3.2 Three allowlisted files intentionally unchanged

These stay **on** the allowlist (permitted) but are **not** required, and must
not be edited to reach a path count:

| File | Reason |
|---|---|
| `tests/cvf/test_auth_login.py` | Only imports `User`; `User` does not move (Rule B). |
| `tests/cvf/test_ledger_protocol.py` | Only imports the shim namespace `domain_models`; Rule A requires it to stay. |
| `tests/integration/test_sql_ledger_integrity.py` | Same — namespace-only import, Rule A. |

Editing the latter two would break `operations_ledger._rows.build_user`.

### 3.3 Amended path total

```
  43   parent allowlist
-  3   intentionally unchanged (§3.2)
= 40   C3 working tree as built
+  2   the two catalog paths (§3)
= 42   expected C3 changed set
```

**The allowlist is a ceiling, not a checklist.** Fewer touched paths than
listed is conformant provided every touched path is on the list. Any path not
on the list remains **S1**.

## 4. Parent §6 superseded — amended evidence table

| # | Command | Required result |
|---|---|---|
| E-1 | `git rev-parse HEAD origin/main` | equal at start of BUILD |
| E-2 | `git status --porcelain -uall` | changed set = the **42** paths of §3.3, all within the amended allowlist |
| E-3 | `git diff --stat -- packages/operations-ledger/` | **empty** (AC-10) |
| E-4 | targeted run of the three new test files | all pass (AC-01…AC-08) |
| E-5 | `python -m pytest -q tests/integration tests/cvf` | all pass, **including `test_catalog_drift_detection.py`** (AC-11) |
| E-6 | `python -m pytest -q` | **≥ 221 passed, 0 failed, 0 errors** (AC-12) |
| E-7 | `python scripts/testing/validate_repository.py` | exit `0` — **re-runs E-8 internally** (AC-13) |
| E-8 | `python scripts/generate_catalog.py --check` | exit `0` (AC-13) |
| E-9 | `python scripts/check_session_state.py` | exit `0` |
| E-10 | `python scripts/check_file_size.py` | exit `0` |
| E-11 | `git diff --check` | clean |
| E-12 | rollback rehearsal in a temporary worktree/clone (parent §12.1) | C3 paths match `C3_PARENT`; C1/C2 intact; suite exactly **221 passed**; worktree removed |
| E-13 | workspace doctor (`-ProjectPath`) | `PASS (24/24)` |
| E-14 | catalog status audit | `operations-domain` is `partial`, **not** `enforced`; no other module status changed |
| E-15 | secret scan over added lines of the changed set | no credential |

Exit codes must be captured **unpiped** — piping to `tail` yields the pipe's
status, not the script's. That mistake was made once during BUILD evidence and
must not recur.

Every number is quoted from the run that produced it. Copying a count from a
prior handoff is itself a stop condition.

## 5. Parent §8 superseded — amended stop conditions

All parent S1–S11 remain, with these corrections:

- **S1 (amended)** — triggers on a path **outside** the amended allowlist, or
  on any parent-§4 prohibited path. It **no longer** triggers merely because
  the touched-path count differs from the allowlist size (§3.3).
- **S3 (unchanged)** — the suite dropping below 221 passed, or any failure or
  error, remains a stop. With the catalog now in C3, the drift test must pass
  rather than be tolerated.
- **S8 (amended)** — adds: hand-editing `MODULE_CATALOG.md` or any `metrics`
  block instead of regenerating; or setting `operations-domain` to `enforced`.
- **S12 (new)** — any catalog edit beyond §3.1's bounded permission (another
  module's status, `status_legend`, `cvf_controls`, or
  `IMPLEMENTATION_STATUS.json`).
- **S13 (new)** — discovering that another authorization surface is likewise
  unsatisfiable. Stop and report; do not amend the authorization from inside
  BUILD.

## 6. Parent §10 superseded — amended commit plan

| # | Contents | Owner | Gate |
|---|---|---|---|
| **C1** | Three authorization artifacts | COMMIT_STEWARD | done — `3e3df42` |
| **C2** | Pre-BUILD continuity | COMMIT_STEWARD | done — `1e56a72` |
| **C2b** | **This amendment: the three addendum files only, zero implementation files** | COMMIT_STEWARD | after independent review |
| **C3** | BUILD: the 42 paths of §3.3 | COMMIT_STEWARD | after independent REVIEW_PASS on all ACs |
| **C4** | Roadmap + `IMPLEMENTATION_STATUS.json` + continuity/closure — **no catalog path** | COMMIT_STEWARD | only if authorized at FREEZE |

**C2b must contain exactly three files** — the ADR addendum, this amendment,
and the SPEC amendment — and **no** implementation file. That is the
commit-graph proof that the authorization fix preceded the resumed BUILD, the
same structure C1 provided for the original authorization.

The 40 already-built C3 paths stay **uncommitted and unstaged** across C2b.
They are not discarded, not reverted, and not staged into C2b.

## 7. Parent §11 superseded — amended C4 allowlist

The two catalog paths are **removed** from C4. C4 is now:

```
docs/implementation/EXECUTION_ROADMAP.md   # tick P1-B [x]; record bounded scope
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/handoffs/AGENT_HANDOFF_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md
```

Constraints carried over unchanged: ticking P1-B `[x]` closes a **roadmap
item**, not the Phase 1 exit gate; the PostgreSQL pre-ship limitation wording
must survive verbatim (AC-16); the FREEZE record must claim no
governance/AI evidence; `check_session_state.py` must pass before C4 commits.

**A catalog path appearing in C4 is now S1.**

## 8. Roles and resumption

- Amendment authored by Claude as **SPEC_AUTHOR / WORK_ORDER_AUTHOR**, having
  transitioned out of IMPLEMENTATION_WORKER. No implementation file was touched
  while authoring it.
- **Codex retains independent REVIEWER and COMMIT_STEWARD** and is authorized
  to clear the remaining reviewer/steward gates without re-asking the operator,
  provided scope does not change and no stop condition is hit.
- **Claude may transition back to IMPLEMENTATION_WORKER only after C2b is
  reviewed and committed**, and must state that transition explicitly before
  touching the catalog files.
- Claude does not stage, commit, amend, push, or create branches at any point.
  No `git add -A` / `git add .`, no amend/rebase/reset/force-push.

## 9. Boundary — unchanged

Restated so no reader mistakes this amendment for a scope change. Still
prohibited: touching `packages/operations-ledger/**` (zero-line diff);
refactoring the `SqlLedger(models=...)` seam or the `Ledger` Protocol; moving
`User`; changing any API contract, response schema, OpenAPI output, database
schema, migration, lifecycle semantics, enum value, or CVF gate behaviour;
editing `workspace_api/auth/**`, `known-principals.yaml`, `.cvf/**`,
`database/**`, `packages/cvf-runtime/**`, `apps/workspace-web/**`,
`infrastructure/**`; opening lanes 2–4; calling a provider; reading a secret.

High Finding #4 remains **OPEN**. P1-B is **not complete**. The Phase 1 exit
gate is **not met** and PostgreSQL has still never been verified live.

## 10. Checkpoint state at the time of writing

- The 40 C3 implementation paths exist, **unstaged and uncommitted**, unchanged
  by this amendment.
- Exactly three new addendum files exist, unstaged.
- Expanded worktree total: **43** entries.
- No continuity, roadmap, `IMPLEMENTATION_STATUS.json`, or catalog file was
  touched by this amendment checkpoint.
- Nothing staged, committed, or pushed. No branch created. No BUILD action.
- No provider call; no secret read.

Returned checkpoint: `READY_FOR_INDEPENDENT_AUTHORIZATION_AMENDMENT_REVIEW`.
