# Agent Handoff — 2026-07-23 (CVF Core Pin — FREEZE)

## Disposition

- Tranche: `CVF-CORE-PIN-2026-07-23`
- Control-chain phase: `FREEZE`
- Risk: R2 (governance-core pin)
- Result: `CLOSED_BOUNDED`
- Live provider evidence: **not required and not produced** — this tranche
  makes no AI/agent governance behavior claim

The tranche ran the full control chain in order, with every gate recorded in
the commit graph itself: INTAKE → DESIGN → SPEC → operator-approved
WORK_ORDER → BUILD → independent REVIEW → FREEZE.

## What this tranche did

The workspace doctor was failing 23/24 with
`CVF public core matches origin/main → BEHIND_PUBLIC_REMOTE`: the hidden
sibling CVF core sat at `c1076dc`, while public `origin/main` had moved to
`6ce1cf0`. `AGENTS.md`'s First-Request Protocol requires a passing doctor
before material work, so every later tranche would have started from a
failing gate.

The hidden core was reconciled to public `origin/main` using the framework's
own sanctioned reconciler
(`.Controlled-Vibe-Framework-CVF/scripts/update_cvf_workspace_public_core.ps1`,
invoked with `-WorkspaceRoot` only), and `.cvf/manifest.json`'s
`cvfCoreCommit` was re-pinned to the full 40-character new hash. The
in-repository changed set for BUILD was exactly one file, one line.

The upstream delta was a single commit,
`6ce1cf0 docs: reconcile seven-step loop and provider claims`, touching four
CVF core documentation files (`ARCHITECTURE.md`, `PROVIDERS.md`, `README.md`,
`docs/reference/CVF_PROVIDER_LANE_READINESS_MATRIX.md`). No CVF core script,
governance toolkit template, or workspace kit file changed.

## Verified facts

| Fact | Value |
|---|---|
| Authorization-artifacts commit (ADR + SPEC + WORK_ORDER, no implementation) | `76e7360` |
| BUILD / REVIEW_PASS core-pin commit (`.cvf/manifest.json` only) | `da9a122` |
| FREEZE authorization addendum commit (SPEC §9 + WORK_ORDER §13) | `18d67d3` |
| CVF core HEAD, core `origin/main`, and manifest `cvfCoreCommit` | all three `6ce1cf0` (`6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`) |
| Workspace doctor | `RESULT: PASS (24/24 checks passed)` + `FRESH_CLONE_CONTINUITY_PASS` |
| P2-B FREEZE | committed **separately** as `4e15ea4` |

`da9a122` and `4e15ea4` share no path — that is the direct evidence the two
tranches were never batched into one commit, as this project's commit
discipline requires.

## Verified boundary

This tranche established **only** that the hidden CVF core matches public
`origin/main` at `6ce1cf0`, that the manifest pin matches it, and that local
enforcement artifacts pass 24/24.

It did **not** establish, and must not be described as establishing:

- that any CVF control is load-bearing or newly enforced;
- any live governance evidence of AI/agent behavior — the doctor proves local
  enforcement artifacts and public-core freshness only, and `WORKSPACE_RULES.md`
  states that boundary itself;
- any change to the `P2B-AUTHENTICATION-REPAIR` FREEZE disposition or its
  sanitized Alibaba evidence receipt;
- closure of High Finding #4;
- that PostgreSQL, approval quorum, or any roadmap item advanced;
- that the four upstream documentation changes were audited for content
  correctness — they are accepted as the public core's own state.

## Claims preserved from earlier tranches

- **P2-B remains bounded exactly as frozen at `4e15ea4`.** `identity` is
  load-bearing and governance-approved **within its receipt boundary only**.
  There are still no refresh tokens, no revocation, no self-service
  registration, no password reset, no login rate-limiting, and no real admin
  provisioning flow (`scripts/seed_dev_users.py` is dev/test only).
  PostgreSQL has never been round-trip verified live.
- **High Finding #4 remains OPEN.** `known-principals.yaml` is still a
  registry check, not authentication, and has not been reconciled with the
  authenticated `users` table.
- **`cd36b27` remains the original unauthorized build candidate**, retained
  unrewritten as historical evidence. It was not amended, squashed, rebased,
  or force-pushed by this tranche or any other.

## Continuity drift — recorded, NOT resolved

There is a real disagreement between the roadmap-ordering rule and the
recorded next move. It is recorded here as an open question for the operator.
No agent may resolve it.

| Source | Says |
|---|---|
| `CONTRIBUTING.md:21` | ordering rule — take the next `[ ]` roadmap item in order (`lấy item [ ] kế tiếp theo thứ tự`) |
| `docs/implementation/EXECUTION_ROADMAP.md:207` | the first `[ ]` item is **P1-B** — extract domain models into `operations-domain` |
| `SESSION/ACTIVE_SESSION_STATE.json` `next_allowed_move` (before this handoff) | offered only P2-A (remaining incidents/handovers), `known-principals.yaml` ↔ `users` (High Finding #4), and P2-C — **P1-B absent** |

Applying the ordering rule literally selects **P1-B**. The recorded lane list
does not contain P1-B. Both surfaces are governed artifacts; neither was
silently overridden here.

**No lane has been chosen, ranked, or reprioritized, and the roadmap was not
edited.** Resolving this is the operator's decision, not an agent's.

## Next governed move

Start a new control chain at **INTAKE** so the operator can confirm which
lane is active. The candidate lanes are the union of both surfaces above:

- **P1-B** — extract domain models into `operations-domain` (what the
  ordering rule selects);
- **P2-A (remaining)** — incidents and handovers, each requiring a new
  governed migration first;
- **known-principals.yaml ↔ users reconciliation** — High Finding #4;
- **P2-C** — frontend UI for verticals that already have a backend.

Do not begin BUILD from a loose chat instruction, and do not pick a lane on
the operator's behalf.
