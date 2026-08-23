# INTAKE — Cross-Agent Invariant Learning

- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Date: `2026-08-22`
- Phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE_REVIEW_PASS`
- Authority: operator-directed fresh INTAKE after P4-B FREEZE
- DESIGN/BUILD/provider/network/install/database/commit/push/deployment: `NONE`

## Intent

Turn the repeated P4-B review/repair lesson into provider-neutral,
repository-native learning so every human and agent follows the same method.
The learning must not depend on chat history, provider-local memory, model
identity or informal reviewer recollection.

## Problem statement

Several P4-B repairs closed the reported examples while leaving an adjacent
member of the same invariant family open. The final live issue came from a
second copy of a prompt-linked schema drifting from the canonical prompt.
Green tests therefore proved individual probes but did not always prove the
complete outcome/fact/counter family or cross-artifact contract identity.

The recurring failure pattern is:

1. prose requirement is translated into individual conditions;
2. tests cover known examples rather than the full invariant family;
3. model, schema, fixture, prompt or receipt copies drift independently;
4. a reviewer mutates an adjacent field and finds another fail-open shape;
5. the repair/review cycle repeats.

## Requested outcome

A future DESIGN should define one shared method that can become load-bearing
repository guidance and deterministic checks. At minimum it must address:

- a canonical invariant matrix for every terminal outcome;
- required, forbidden and conditional fields plus exact counter relations;
- positive coverage generated from every real service-emitted terminal shape;
- paired model/schema acceptance parity;
- one-field deletion/change/addition mutation tests around every valid shape;
- canonical ownership/reuse for prompt-schema, contract-fixture and similar
  coupled artifacts instead of independent copies;
- a closure rule that the whole invariant family must be proved, not merely
  the reviewer-provided examples;
- Work Order and reviewer checklists that use the same source of truth;
- a deterministic repository guard capable of detecting missing parity,
  mutation coverage or prohibited duplicate contract ownership;
- Project Knowledge and continuity routing so all supported agents read the
  same versioned rule.

## Candidate artifact classes for DESIGN evaluation

- provider-neutral rule additions to `AGENTS.md`;
- one canonical CVF invariant-learning guide;
- machine-readable invariant-matrix schema and reusable template;
- reusable test helpers or generators for parity and mutations;
- Work Order/review checklist templates;
- deterministic repository validation and its negative tests;
- Project Knowledge entry, source pins, catalog/status/continuity updates.

These are candidates, not authorized paths or an approved architecture.
DESIGN must minimize duplication and assess whether an existing project skill
or validation framework should own each behavior.

## Constraints and claim boundary

- Provider-neutral: no Claude/Codex/Gemini-specific instruction or memory.
- Repository-native and reviewable; chat history is not canonical learning.
- No external code/runtime/config/database/secret/deployment import.
- No provider/network call is needed to design or test the learning mechanics;
  any later governance-behavior claim follows the project's live-proof rule.
- Do not weaken independent review or let an implementation worker self-close
  R2/R3 governance-significant changes.
- Do not create a mechanism that blindly generates tests from the same faulty
  implementation it is meant to verify; accepted terminal shapes require an
  independently stated contract source.
- This tranche does not reopen or rewrite P4-B history and does not claim that
  future findings are impossible.

## Intake acceptance questions

Independent INTAKE review must decide whether the boundary is complete and
whether the future DESIGN must explicitly resolve:

1. the single canonical owner and serialization format of invariant matrices;
2. how emitted-shape positives remain independent from validators;
3. minimum mutation operators and parity guarantees;
4. applicability thresholds beyond P4-B without forcing irrelevant projects;
5. guard integration, rollout and legacy-waiver handling;
6. file-size/catalog/knowledge/continuity impacts and an exact-path ceiling;
7. reviewer independence and evidence requirements for the learning tranche.

## Stop condition

Independent INTAKE review passed with findings/waivers `NONE/NONE`. Stop at
`INTAKE_REVIEW_PASS_AWAITING_DESIGN_AUTHORITY`. Do not proceed to DESIGN, SPEC,
WORK_ORDER or BUILD without fresh authority.
