# INTAKE — Project Operations Skill

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE_CAPTURED_PENDING_DESIGN`
- Trigger: automatic post-Phase-2 sequence activated by C4 `0a29192`
- Source truth baseline: `0a29192dacf7380ee565a13bc48a164eb79e65a9`

## Intent

Create a concise, reusable, provider-neutral skill that helps an agent operate
this project through its governed workflow without reconstructing the same
continuity, phase, role, evidence, review and closure rules every session. The
skill is an operational guide over existing project truth; it is not a new CVF
runtime, policy engine or source of canonical project state.

## Concrete use examples

1. “Resume the active tranche” → rehydrate the manifest/policy/continuity,
   emit the current declaration, detect drift and identify the sole allowed
   next move before editing.
2. “Open the next tranche” → run fresh INTAKE, classify risk, preserve the
   seven-step control chain and distinguish it from the five-phase roadmap.
3. “Prepare a worker handoff” → produce a provider-neutral, exact-path Work
   Order with roles, evidence order, stop conditions and commit ownership.
4. “Review and close this tranche” → require independent evidence review,
   exact changed-set/cleanup checks, separate BUILD and C4 commits, and bounded
   continuity synchronization.
5. “Prove governance behavior” → enforce the real-provider evidence rule and
   refuse mock evidence for approval/risk/DLP/routing/audit behavior.

## Requested capability boundary

- Read canonical project/CVF front doors and route to the active handoff.
- Apply the project's risk, role-transition, isolation, evidence and commit
  discipline without hardcoding Claude, Codex or another provider.
- Prefer progressive disclosure: keep the skill body concise and link only to
  the project references needed for the current phase.
- Reuse deterministic scripts only where repetition is fragile; never copy
  secrets, local bindings, provider credentials or machine-specific paths.

## Explicit exclusions

- No skill implementation, installation or personal Codex-home write in this
  INTAKE tranche.
- No automatic provider call, commit, push, approval, self-review or FREEZE.
- No duplication of canonical continuity, policy, roadmap or catalog content
  into a second source of truth.
- No knowledge-pack, Refinery, retrieval/RAG or learning-runtime work; those
  remain later ordered tranches.
- No claim that a prompt/skill itself enforces governance at runtime.

## Decisions required in DESIGN

1. Portable repository-owned skill source and its exact path versus a personal
   installation target. Workspace isolation prohibits silently writing outside
   the project; installation, if desired, needs explicit authority.
2. Minimal reference set and update/freshness mechanism that avoids copying
   long project documents into `SKILL.md`.
3. Which checks warrant bundled deterministic scripts versus direct reuse of
   existing repository scripts.
4. Validation plan: structural skill validation, realistic forward tests,
   independent review, and whether any governance-behavior claim is intended
   (which would require fresh real-provider evidence).

## Risk and stop conditions

The skill can steer future agents and is therefore R2. Stop on ambiguous
installation location, a second canonical truth source, provider-named role
logic, mock governance proof, out-of-workspace writes, secret inclusion,
automatic external side effects, skipped control-chain phase or a BUILD path
without an independently reviewed Work Order.

## INTAKE exit

INTAKE is complete when this boundary and the concrete examples are accepted as
the basis for DESIGN. The sole next move is DESIGN; no implementation authority
is carried by this document.
