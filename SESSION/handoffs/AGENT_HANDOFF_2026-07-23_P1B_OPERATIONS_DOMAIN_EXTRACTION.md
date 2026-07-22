# Agent Handoff — 2026-07-23 (P1-B Operations-Domain Extraction — FREEZE)

## Disposition

- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase: `FREEZE`
- Risk: R2 (import-boundary refactor across every governed vertical)
- Result: **`CLOSED_BOUNDED`**
- Live provider evidence: **not required and not produced** — this tranche
  asserts no AI/agent-governance claim (SPEC §8)

The tranche ran the full control chain in order, with every gate recorded in the
commit graph: INTAKE → DESIGN → operator-confirmed lane → SPEC → operator-approved
WORK_ORDER → pre-BUILD continuity → BUILD (paused for an authorization amendment,
then resumed) → independent REVIEW → FREEZE.

## What this tranche did

The twelve operational types (`DataState`, `RiskClass`, `ShiftStatus`,
`TaskStatus`, `CustomerRequestStatus`, `EvidenceRef`, `Shift`, `Message`,
`OperationalEvent`, `Correction`, `Task`, `CustomerRequest`) and the three
lifecycle guards (`assert_transition`, `assert_task_transition`,
`assert_customer_request_transition`) now have a **single canonical definition**
in `packages/operations-domain/src/operations_domain/` (`models.py`,
`lifecycle.py`), moved verbatim out of `workspace-api`.

`workspace_api.domain.models` and `workspace_api.domain.lifecycle` are now
**compatibility shims** that re-export those same objects with proven object
identity (`is`, not `==`, asserted per module pair), not redefinitions. All
moved-type imports were repointed to `operations_domain` (32 import lines
changed); the documented `User` imports, the `SqlLedger` shim-namespace imports,
and the shim-identity test's imports intentionally remain. The package imports
only the standard library and `pydantic` — it is a dependency **sink** that
never imports `workspace_api`, `operations_ledger`, `cvf_runtime`, `fastapi` or
`sqlalchemy`, enforced by a repository-scoped import-isolation
subprocess.

`operations-domain` moved **`stub` → `partial`** (never `enforced`).

## Verified facts

| Fact | Value |
|---|---|
| C1 — authorization artifacts (ADR + SPEC + WORK_ORDER, no implementation) | `3e3df420bceca97d8047927a2098ea726d427aa8` |
| C2 — pre-BUILD continuity (operator lane acknowledgment) | `1e56a72e2259f142fd26cc3035e81814f2856d35` |
| C2b — authorization amendment (ADR addendum + SPEC/WO amendment 1, no implementation) | `ab75abb854607694740c0558d00a5d4a4cb99dfd` |
| C3 — BUILD, 42 paths, independent REVIEW_PASS AC-01…AC-18 | `f68cf634f67984d64562dd8bfd0962ef01eb91fe` |
| C4 — this FREEZE closure (roadmap + status + continuity) | committed separately, no catalog/source/test path |
| Full suite | **292 passed** (221 baseline + 71 new), 0 failed, 0 errors |
| `packages/operations-ledger/` diff | **empty** (zero-line) |
| Workspace doctor | `PASS (24/24)` |

Each authorization/amendment commit contains **zero implementation files**,
which is the commit-graph proof that DESIGN/SPEC/WORK_ORDER (and the mid-tranche
amendment) preceded the BUILD they authorize.

## The catalog-gate conflict, and why it matters

During BUILD, `generate_catalog.py --check` (hardened by P-FIX-5 to recompute
metrics from source) failed because C3 necessarily changed LOC/file counts, and
`validate_repository.py` calls that same check. With `docs/catalog/**`
prohibited in C3, AC-12 (zero failures) and AC-13 (validators PASS) were
**jointly unsatisfiable** — an authorization defect, not an implementation one.

The IMPLEMENTATION_WORKER **stopped** rather than regenerate a prohibited path
or weaken the drift test, and reported. The authorization was amended through
DESIGN → SPEC → WORK_ORDER (**C2b**) to move the two catalog files from C4 into
C3 before BUILD resumed. This is the control chain catching an authorization
defect instead of absorbing it silently into a BUILD commit — the failure mode
`cd36b27` recorded.

## Review evidence (re-run by the independent reviewer, not trusted from report)

- Targeted three new test files: **71 passed**
- `tests/integration` + `tests/cvf`: **210 passed**
- Full suite: **292 passed**, 0 failed, 0 errors
- `validate_repository.py`, `generate_catalog.py --check`,
  `check_session_state.py`, `check_file_size.py`: PASS
- Workspace doctor: 24/24
- `git diff --check`: clean · `packages/operations-ledger/`: zero-line diff
- **AC-18 rollback rehearsal**: ran in a temporary worktree outside the primary
  workspace; after reverting C3 the C3 paths matched `C3_PARENT` `ab75abb`,
  C1/C2/C2b remained intact, the suite returned to the **221 passed** baseline,
  and the temporary worktree was cleaned up — PASS.

## Verified boundary — what this tranche did NOT do

- **`User` did not move.** It belongs to the authentication boundary; its
  canonical home stays `workspace_api.domain.models`, which is now both a shim
  (for the operational types) and the canonical home of `User`. Its relocation
  is owned by lane 2 (`known-principals.yaml` ↔ users), not this tranche.
- **The `SqlLedger(models=...)` seam and the `Ledger` Protocol were not
  refactored** — `packages/operations-ledger/**` has a zero-line diff.
- No API contract, response schema, OpenAPI output, database schema, migration,
  lifecycle semantics, enum value, or CVF gate behaviour changed (all compared
  as canonical bytes).
- No change to authentication, approval, or `known-principals.yaml`.
- `operations-domain` is **`partial`, not `enforced`**: incidents, handovers,
  reports, approvals and audit still have no operational model or runtime, and
  the per-domain blueprint subdirectories are still README-only.
- **No AI/agent-governance claim** — no provider call was made or required.

## Claims preserved from earlier tranches

- **P2-B** remains frozen at `4e15ea4`; `identity` load-bearing within its
  receipt boundary only. **P2-B disposition unchanged.**
- **`CVF-CORE-PIN-2026-07-23`** remains `FREEZE / CLOSED_BOUNDED`; core and pin
  at `6ce1cf0`. **Disposition unchanged.**
- **High Finding #4 remains OPEN.** `known-principals.yaml` is still a registry
  check, not reconciled with the `users` table. Not touched by P1-B. Do not say
  "all findings fixed".
- **Phase 1 exit gate is NOT met.** Ticking P1-B closes a roadmap item, not the
  phase. The **PostgreSQL live round-trip has never run** (no Docker) and
  remains a pre-ship gate.
- `cd36b27` remains untouched historical evidence.

## Next governed move

Return to **INTAKE** for lane 2 of the operator's confirmed four-lane order:

1. ~~P1-B operations-domain extraction~~ — **DONE (this tranche)**
2. **`known-principals.yaml` ↔ authenticated users reconciliation** (High
   Finding #4) — **the next lane**
3. P2-A remaining — incidents / handovers (each needs a new governed migration
   first)
4. P2-C — frontend

Lane 2 is only **named** here as the next move. Do not DESIGN, SPEC, WORK_ORDER,
or BUILD it in this closure. Do not begin it from a loose chat instruction; it
starts at a fresh INTAKE.
