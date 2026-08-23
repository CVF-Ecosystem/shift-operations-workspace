---
name: operate-shift-workspace
description: >-
  Operate the shift-operations-workspace through its governed continuity,
  phase, role, evidence, review, repair, and closure workflow. Use when
  resuming this project, opening or advancing a tranche, preparing a bounded
  worker handoff, reviewing or repairing work, or closing and synchronizing
  project state.
---

# Operate Shift Workspace

Use this skill as a navigation procedure over current repository authority.
Never treat the skill as permission, approval, enforcement, or canonical
project truth.

## Establish the authority boundary

1. Confirm the working directory is the project root.
2. Confirm the workspace-boundary `WORKSPACE_RULES.md` required by the current
   project contract exists. Stop if the workspace boundary is uncertain.
3. Read the applicable `AGENTS.md` completely before material work.
4. Read `.cvf/manifest.json` and `.cvf/policy.json`. Resolve the CVF core only
   from the manifest and permitted local binding; keep the core read-only.
5. Treat current repository files and reviewed evidence as truth. Do not copy
   their changing contents into this skill or substitute memory/chat history.

Stop if any required authority file is missing or unreadable.

## Rehydrate current continuity

Rehydrate before material work on a new/resumed session, context transfer,
tranche transition, role transfer, or canonical handoff/state change.

1. Read every document declared by the current manifest and applicable agent
   contract.
2. Read the manifest-declared canonical continuity paths in their required
   order.
3. Follow canonical active state to its active handoff. Treat compatibility
   mirrors as mirrors, not competing truth.
4. Read implementation status, documentation index, roadmap, and any
   machine-required reads named by active state.
5. Compare canonical surfaces. If they disagree, stop at INTAKE and report
   `BLOCKED_CONTINUITY_DRIFT`; never choose a winner silently.
6. Run the current workspace doctor/bootstrap procedure required by
   `AGENTS.md`. Stop on a new failure or unapproved warning.
7. Emit the exact current CVF Agent Declaration before the first substantive
   action and again at every required rehydration trigger.

## Route phase, risk, and role

Preserve this control chain without skipping:

`INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE`

Keep it distinct from the business roadmap. Classify the request under the
current risk policy and stay within its ceiling.

Use only provider-neutral responsibility names:

- `ORCHESTRATOR` routes authority, dependencies, and the next move.
- `SPEC_AUTHOR` writes testable intended behavior and claim boundaries.
- `WORK_ORDER_AUTHOR` fixes exact paths, ownership, evidence, stop conditions,
  rollback, provider budget, and commit boundaries.
- `IMPLEMENTATION_WORKER` changes only the approved BUILD set.
- `REVIEWER` independently checks requirements, source, tests, and evidence.
- `REPAIR_WORKER` closes accepted findings within authorized repair scope.
- `CLOSER`, `COMMIT_STEWARD`, and `SESSION_SYNC_STEWARD` close their explicit
  responsibilities without absorbing another role silently.

State and record each role transition before acting. Require an independent
reviewer for R2, R3, or governance-significant work.

## Advance one governed tranche

### INTAKE

Capture intent, authority, constraints, risk, exclusions, dependencies,
current truth, unresolved decisions, and one next allowed move. Do not design
until the request boundary is explicit.

### DESIGN

Record architecture, boundaries, alternatives, acceptance approach, data and
provider implications, and unresolved tradeoffs. Do not present intended
design as implemented truth.

### SPEC

Convert approved design into numbered, testable requirements and acceptance
criteria. Define negative cases, claim boundary, evidence type, cleanup,
rollback, and failure semantics. Require a real provider API call for every
claim that governance controls AI/agent behavior; mock evidence is UI-only.

Check `docs/cvf/INVARIANT_FAMILY_STANDARD.md` applicability triggers for a
new or materially changed R2/R3 contract surface. Declare a registered
family id or a reviewable `NOT_APPLICABLE` reason; never restate matrix
rules here.

### WORK_ORDER

Authorize an exact changed set with no wildcard or hidden reserve. Name:

- required and protected paths;
- role ownership and independence;
- prerequisite and pre-BUILD gates;
- test/evidence order and any exact provider-call budget;
- secret/DLP and sanitization requirements;
- stop, amendment, cleanup, rollback, staging, commit, and push rules.

Require independent authorization review. Invocation of this skill never
grants BUILD, provider-call, installation, commit, push, approval, self-review,
or FREEZE authority.

If a family was registered at SPEC, complete
`docs/templates/INVARIANT_FAMILY_PROOF.md` with matrix id/digest, adapter/
test paths, exclusions, and exact commands; do not copy matrix content.

### BUILD

Rehydrate and acknowledge the tranche before source work. Pass every required
pre-BUILD gate. Change only exact approved paths; preserve unrelated user
changes. Stop on a missing/unnecessary path, required split, changed baseline,
failed gate, unsafe evidence path, or scope conflict. Request a reviewed
amendment instead of silently broadening authority.

Run focused tests first, then the authorized full/repository/live evidence in
the mandated order. Keep provider calls behind every refusal and durability
gate. Record honest failures, call counts, and cleanup. Do not stage, commit,
push, or self-approve unless the current Work Order explicitly assigns that
separate responsibility.

### REVIEW and repair

The independent reviewer must compare current authority, exact diff, source,
tests, outputs, evidence receipts, provider-call accounting, cleanup, and claim
wording. Do not trust a worker's declared PASS without rerunning permissible
checks.

Return actionable findings with severity and exact repair. Retain failed or
invalidated evidence. A repair worker may change only the accepted repair set;
new paths, provider calls, or broader claims require a reviewed amendment.
Re-review until `REVIEW_PASS` or a truthful blocker remains.

When a family was registered, the reviewer independently recomputes the
matrix digest and reruns the full corpus via `docs/templates/
INVARIANT_FAMILY_PROOF.md`; closing only reviewer-supplied probes is
forbidden.

### FREEZE

Freeze only after independent `REVIEW_PASS`, required evidence, exact commit
ownership, cleanup, and synchronized canonical truth. Update the active
handoff, memory, active state and mirror, implementation status, roadmap, and
catalog only when their current contracts require it. Regenerate derived
artifacts with current repository tools; do not hand-edit generated truth.

Keep closure bounded. Control-chain FREEZE does not imply roadmap-phase,
production, provider-universal, or future-behavior completion. Commit/push a
completed tranche separately when the current contribution contract requires
it, then verify a clean worktree and local/remote equality.

## Stop and refuse

Stop or refuse when asked to:

- skip a control-chain phase or build from loose chat;
- work through continuity drift or missing required truth;
- exceed an exact path, role, risk, provider-call, or external-write boundary;
- expose, persist, print, or commit a secret or unsanitized payload;
- use mock output as governance-behavior evidence;
- call a provider, install, stage, commit, push, approve, self-review, or
  FREEZE without explicit current authority;
- hide a failed gate, dissent, invalidated receipt, residue, or open finding;
- broaden a reviewed claim or roadmap disposition silently;
- write into the read-only CVF core or another workspace.

Report the precise blocker, preserved evidence, and smallest governed next
move. Do not invent permission to make progress.

## Validate this navigation

Before relying on a changed copy of this skill, run the current skill-creator
validator, project contract tests, repository gates, and independent forward
tests required by its approved Work Order. A prompt can guide behavior; only
current controls and recorded evidence can support a governance claim.
