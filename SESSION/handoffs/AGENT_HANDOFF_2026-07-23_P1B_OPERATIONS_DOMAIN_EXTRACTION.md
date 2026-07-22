# Agent Handoff — 2026-07-23 (P1-B Operations-Domain Extraction — PRE-BUILD)

## Disposition

- Tranche: `P1B-OPERATIONS-DOMAIN-EXTRACTION`
- Control-chain phase: `WORK_ORDER` **approved** — standing immediately before
  `BUILD`
- Risk: R2 (import-boundary refactor across every governed vertical)
- Status: **BUILD HAS NOT STARTED. No source, test, catalog, roadmap or status
  file has been touched by this tranche.**
- Live provider evidence: **not required and not produced** — this tranche
  asserts no AI/agent-governance claim (SPEC §8)

This handoff records gate **G4** of the approved WORK_ORDER: the pre-BUILD
continuity acknowledgment. It is a checkpoint record, not a completion record.

## Operator lane decision — the drift is resolved

The `CVF-CORE-PIN-2026-07-23` FREEZE recorded an open continuity drift and
deliberately refused to resolve it: `CONTRIBUTING.md:21` rules that the next
unchecked roadmap item is taken in order, `EXECUTION_ROADMAP.md:207` shows that
item is **P1-B**, while the recorded lane list offered only P2-A remaining,
`known-principals.yaml` ↔ users, and P2-C — with P1-B absent. No agent was
permitted to choose.

**The operator has now resolved it**, confirming this order:

| # | Lane | State |
|---|---|---|
| 1 | **P1-B — operations-domain extraction** | **OPEN — the only lane authorized** |
| 2 | `known-principals.yaml` ↔ authenticated users (High Finding #4) | not opened |
| 3 | P2-A remaining — incidents / handovers | not opened |
| 4 | P2-C — frontend | not opened |

Lanes 2–4 must not be implemented, scoped, or started. The drift no longer
needs agent-side handling: it was resolved by the authority that owned it.

## Gate status

| Gate | Requirement | State |
|---|---|---|
| **G1** | Independent review of the authorization artifacts | **PASS** — two review rounds; `REVIEW_CHANGES_REQUIRED` findings F1–F4, then F5–F6, all repaired in the artifacts before approval |
| **G2** | Authorization artifacts committed separately, zero implementation files | **PASS** — commit `3e3df420bceca97d8047927a2098ea726d427aa8`, exactly 3 files, 1436 insertions, no source/test file |
| **G3** | Operator approves the WORK_ORDER | **PASS** — approved **intact**, no amendment, at `3e3df42` |
| **G4** | Continuity records the operator's lane choice before BUILD | **IN PROGRESS — this commit (C2)** |
| **G5** | Role transition to IMPLEMENTATION_WORKER stated | not yet — occurs after C2 is committed |
| **G6** | Clean start re-verified at the moment BUILD begins | not yet |

## Authorization artifacts (committed at C1 `3e3df42`)

- `docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md` — DESIGN
- `docs/specs/P1B_OPERATIONS_DOMAIN_EXTRACTION_SPEC.md` — testable requirements
  R1–R8 and acceptance criteria AC-01…AC-18
- `docs/work_orders/P1B_OPERATIONS_DOMAIN_EXTRACTION_WORK_ORDER.md` — the
  approved bounded changed set, prohibited paths, stop conditions, commit plan

That C1 commit contains **no implementation file**, which is the commit-graph
proof that DESIGN → SPEC → WORK_ORDER preceded BUILD — the same structure
`CVF-CORE-PIN-2026-07-23` used at `76e7360`, and the structure whose absence
made `cd36b27` an unauthorized build candidate.

## Verified state at the time of writing

| Fact | Value |
|---|---|
| `HEAD` == `origin/main` | `3e3df420bceca97d8047927a2098ea726d427aa8` |
| Branch / worktree | `main`, clean before C2 |
| Workspace doctor | `RESULT: PASS (24/24 checks passed)` |
| Test baseline | **221 passed** (run at `ed3d944`; re-verified at G6 before BUILD) |

## What BUILD (C3) will do, once authorized

Create `packages/operations-domain/src/operations_domain/` as the single
canonical home of twelve operational models and three lifecycle guards; leave
`workspace_api.domain.models` / `.lifecycle` as re-export shims with asserted
object identity; repoint 43 import statements across 30 files. `User` does
**not** move — it belongs to the authentication boundary and its relocation is
lane 2's decision. `packages/operations-ledger/**` must show a **zero-line
diff**: the `SqlLedger(models=...)` injection seam is deliberately not
refactored.

Authoritative scope is the WORK_ORDER's allowlist (43 paths), not this summary.

## Role route

```
ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR        (Claude, C1 artifacts)
  -> independent REVIEWER x2                             (Codex, F1-F6)
  -> OPERATOR APPROVAL (G3)                              (intact, 3e3df42)
  -> SESSION_SYNC_STEWARD                                (Claude, this C2)
  -> IMPLEMENTATION_WORKER                               (Claude, C3 - AFTER C2 commits)
  -> independent REVIEWER / COMMIT_STEWARD               (Codex)
```

- **Next role after C2 is committed: Claude → IMPLEMENTATION_WORKER**, stated
  explicitly before the first source edit (G5).
- **Codex holds independent REVIEWER and COMMIT_STEWARD** throughout, as R2
  requires. Codex is authorized to clear the remaining reviewer/steward gates
  without re-asking the operator, provided scope does not change and no stop
  condition is hit.
- Claude does not stage, commit, amend, push, or create branches at any point.

## Claim boundary — unchanged by this tranche

This handoff changes **no** prior disposition and asserts **no** new capability:

- **P2-B** remains frozen exactly as at `4e15ea4`. `identity` is load-bearing
  and governance-approved **within its receipt boundary only**; still no
  refresh tokens, revocation, self-service registration, password reset, login
  rate-limiting, or real admin provisioning.
- **`CVF-CORE-PIN-2026-07-23`** remains `FREEZE / CLOSED_BOUNDED`; core and pin
  stay at `6ce1cf0`. It is not AI-governance evidence.
- **High Finding #4 remains OPEN.** `known-principals.yaml` is still a registry
  check, not authentication, and is not reconciled with the `users` table. This
  tranche does not touch it.
- **P1-B is NOT complete.** It is authorized and about to start.
- **Phase 1 exit gate is NOT met.** Ticking a roadmap item is not a phase gate.
- **PostgreSQL round-trip has never been run live** in this environment and
  remains a pre-ship limitation.
- `cd36b27` remains untouched historical evidence — no rewrite, squash, amend,
  rebase, or force-push by this tranche.
- No provider call was made and no secret was read; none is required, because
  no AI-governance claim is asserted.

## Next governed move

1. Codex reviews and commits **C2** (this handoff plus the three continuity
   files) as COMMIT_STEWARD.
2. Claude states the transition to IMPLEMENTATION_WORKER (G5), re-verifies the
   clean start (G6), and executes **C3** strictly inside the WORK_ORDER
   allowlist.
3. Codex independently reviews C3 by re-running every AC — not by trusting
   reported numbers — and commits it.
4. **C4** (catalog, roadmap, status, continuity closure) only at FREEZE, only
   from observed source truth, only if explicitly authorized.

Do not begin BUILD from a loose chat instruction, and do not open lanes 2–4.
