# CVF Agent Instructions - Downstream Project

> Independent downstream project. Installed public workspace CVF Core:
> `../.Controlled-Vibe-Framework-CVF` at
> `aa672d11910ae1982557e4810a2a8002a611e9e6`.
> Core-only inheritance correction authorized by the operator: 2026-10-26.
> Project continuity belongs only to this project's `SESSION/` tree.

## Catalog Kit And Detailed Module Records

The CVF governed catalog kit v1.1 uses `docs/catalog/ARTIFACT_REGISTRY.json`,
`docs/catalog/MODULE_REGISTRY.json`, and
`scripts/manage_cvf_downstream_catalog.ps1`. The project-owned 26-module
catalog remains available as `docs/catalog/MODULE_REGISTRY_DETAIL.json` and
`docs/catalog/MODULE_CATALOG_DETAIL.md`; the detailed project documentation
index is `docs/PROJECT_INDEX.md`. The generated `docs/INDEX.md` links to each.

When module facts change, edit the detailed registry and run in order:

```text
python scripts/generate_catalog.py --write
python scripts/sync_cvf_catalog_kit.py --write
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Write
```

Before completion, run the detailed generator in `--check` mode, the kit
projection without a flag, and the catalog manager with `-Check`. When the
active handoff changes, update `continuity-initial-handoff` in
`ARTIFACT_REGISTRY.json` to match the compatibility mirror's `activeHandoff`
before running the manager. Module status does not prove application readiness.

## Mandatory Governance Proof

Any test, roadmap closure, release gate, demo proof, or public claim asserting
CVF governance behavior - risk classification, approval flow, phase gates, DLP
filtering, bypass detection, output validation, provider routing, audit trail
updates, or CVF controlling AI/agent behavior - **must use a real provider API
call**. Mock mode is allowed **only** for pure UI structure checks (navigation,
routing, static badges, layout, RBAC) that assert no AI governance behavior.

## First-Request Protocol (MANDATORY)

Before material work on a new/resumed session, tranche, role or handoff:

1. Read `.cvf/manifest.json` and `.cvf/policy.json`: resolve `cvfCoreRepository`,
   `cvfCoreRelativePath`, exact `cvfCoreCommit`, `cvfControls`,
   `canonicalContinuityPaths`, `phaseModel` and `requiredDocs`. Required live
   evidence, UI-only mock, phase, role and workspace isolation controls remain.
2. Verify `../WORKSPACE_RULES.md` and the installed public Core. Routine local
   preflight is `python scripts/check_cvf_core_machine_inheritance.py --enforce`:
   verify declared public origin, exact installed Core pin and selected tracked
   artifact bytes/hashes before invoking the native closeability checker with
   this project as `--repo-root`. Missing or tampered installed controls fail.
   Do not fetch, update or repin Core automatically. New upstream commits do
   not invalidate an intact installed pinned Core. Fresh-clone initialization
   through `scripts/initialize_cvf_clone.ps1` is an explicit installation action.
   Latest-version workspace doctor/update tools belong to requested reviewed
   Core installation/update diagnosis, not ordinary project startup/commits.
3. Read the pinned Core closeability standard/checker named in `cvfControls`.
   This is the only framework control binding. Do not require, resolve, inspect
   or execute private provenance, shared operator-local rule-pack files or their
   Git HEAD during routine project work. Provenance-to-Core transfer happens
   only through a separately requested reviewed Core update. The framework's
   own memory, bootstrap or active handoff is never this project's continuity.
4. Run the same local Core preflight before dispatch, redispatch, review or
   commit. The configured normal pre-commit hook remains mandatory and intact;
   preserve all catalog/session/file-size/test gates and return-time rechecks.
   Current Core CLI automatically scans Work Orders and `docs/reviews/`.
   This project's historical return/review family is `docs/decisions/`; before
   accepting or redispatching those packets, explicitly apply the verified
   pinned Core `check_recheck` function and confirm its exact standalone
   self-declared return or completion-review marker is applicable. Record the
   result in independent review. Do not claim automatic CLI/hook return-scan
   coverage for that legacy path; this is a documented native selector limit.
5. Rehydrate progressively from `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`,
   `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json` and its named
   active handoff. `CVF_SESSION/ACTIVE_SESSION_STATE.json` is a compatibility
   mirror only. Read `IMPLEMENTATION_STATUS.json`, `docs/INDEX.md` and
   `docs/implementation/EXECUTION_ROADMAP.md`; use targeted history only for a
   missing or contradictory current fact.
6. Declare a fresh `CVF Agent Declaration`: project, installed Core path/commit,
   phase, risk ceiling, live evidence required YES, role, active handoff, next
   allowed move and parked checkpoint before substantive material work.

If required installed controls or project continuity are missing/unreadable,
STOP and identify them. If project bootstrap/state/handoff contradict, report
`BLOCKED_CONTINUITY_DRIFT`; do not silently select one. Source provenance may
be documented historically, but is not an installed-control dependency.

The Core-only correction now uses this ordinary adapter and normal hook.
Direct native Core diagnostics do not waive the installed-binding preflight.
Historical correction admission and its independent review remain in the dated
SPEC/Work Order; they are not a continuing exception for later work.

## Mandatory Continuity Rehydration

The First-Request Protocol is not a one-time bootstrap step. Run it again
before material work whenever a new or resumed chat/session starts; context was
compacted, lost, summarized, or transferred; a new tranche or work order
starts; responsibility moves to another agent or role; or the active state or
handoff changed since the last acknowledgment. At every trigger, re-read the
continuity summary, active state, active handoff, implementation truth, and
documentation index from the canonical paths above.
Do not rely on chat history, provider-local memory, or a previous session
declaration as a substitute. Before the first material action, emit a fresh
`CVF Agent Declaration` from current file values; for a tranche transition,
also record the acknowledgment in the active handoff before BUILD begins. If
summary, state, and handoff disagree, stop at INTAKE and report
`BLOCKED_CONTINUITY_DRIFT`; do not choose one silently.

## Phase Model

```
INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE
```

Required control: INTAKE bounds the request; DESIGN records decisions; SPEC
separates intended behavior from implementation truth; WORK_ORDER grants
bounded execution; BUILD preserves scope and produces evidence; REVIEW returns
defects without silent self-approval; FREEZE closes only settled work.
A tranche may inherit accepted evidence and enter at its earliest open stage
when that decision is recorded. Gate every applicable transition, but do not
require a standalone review artifact after each stage. REVIEW is formal result evaluation before FREEZE; lifecycle traceability is not universal machine enforcement.

## Mandatory Product Milestone Binding

Before any new dispatch or redispatch, including repair, governance maintenance,
research and repository absorption, the ORCHESTRATOR and WORK_ORDER_AUTHOR MUST
include the `Product Milestone Binding` block defined in
`docs/implementation/ACCEPTANCE_GATES.md`. Inline assignments and handoffs have
this same obligation; a separate Work Order file is not an exemption.

Bind the assignment to a named product milestone and its observable user outcome.
Reconcile ALL remaining requirements for that milestone against current source,
integration and accepted evidence, not only the defect or component being assigned.
Name which gaps this assignment closes, all gaps it leaves, and an accountable
owner and concrete roadmap destination for each remainder. Unknown coverage is
`UNKNOWN / BLOCKED`, never omitted or treated as complete.

Do not dispatch when the binding or complete gap reconciliation is missing.
Support work must identify the specific milestone gap it unblocks, its necessity,
a bounded stop condition and the return to product work; without that link it is
parked. Repeated support work cannot automatically authorize another tranche.
REVIEWER MUST reject incomplete bindings and independently assess milestone
coverage. Closing a bounded tranche does not close its milestone: reconcile the
remaining gap set at return/review/closure; milestone completion requires its
full acceptance evidence and existing closure gates. Historical closed records
are not rewritten; any new assignment must use current implementation truth.

## Provider-Neutral Role Contract

Roles are responsibilities and must never be hardcoded to a specific provider.
A single agent may hold multiple roles, but must state and record each role
transition before acting in the new role. For high-risk or governance-
significant work, REVIEWER must be independent from IMPLEMENTATION_WORKER; for
lower-risk work, one agent may transition roles only with explicit evidence and
without hiding dissent or failed checks.

- ORCHESTRATOR: routes work, authority, dependencies, and next move.
- SPEC_AUTHOR: writes testable requirements and contracts.
- WORK_ORDER_AUTHOR: bounds scope, evidence, failure conditions, ownership.
- IMPLEMENTATION_WORKER: changes only the authorized implementation scope.
- REVIEWER: checks source, tests, requirements, evidence, claim boundaries.
- REPAIR_WORKER: resolves accepted reviewer findings within repair scope.
- CLOSER: decides final disposition and ensures no open-state residue.
- COMMIT_STEWARD: verifies changed set and owns the authorized commit action.
- SESSION_SYNC_STEWARD: synchronizes memory, state, handoff, index, catalog.

## Operator Delegation Preferences (2026-10-23)

The operator authorizes autonomous ORCHESTRATOR/REVIEWER work across the roadmap
and explicit subagent delegation. Do not repeat routine scope approvals within
that authority; escalate only at the real boundary changes listed below.
Default subagent model: Luna, reasoning max. Difficult work: Sol, reasoning medium.
These are operator-selected execution preferences, not provider-bound role owners.
Preserve independent review for governance-significant implementation. Every
assignment still carries the full Product Milestone Binding and bounded paths.

## Live Governance Evidence Rule / Workspace Isolation Rule

For any claim that CVF governs AI/agent behavior here: you MUST invoke a real
provider API call, MUST record the request/response in the evidence artifact,
and MUST NOT use mocked provider output as governance proof. Mock providers are
allowed only for UI rendering and component-level tests that assert no
governance decision.

Do NOT run downstream tasks inside either CVF repository, and do NOT commit
downstream artifacts into public core or private provenance. The installed
`../.Controlled-Vibe-Framework-CVF` is a **read-only reference** for project
work. The private provenance repository is outside project dependencies and
authority; do not use it as a project work directory or write destination. Your IDE/terminal working
directory must remain this project root. The workspace root must contain
`WORKSPACE_RULES.md`; if missing, stop and restore the workspace boundary.

## Risk Classification

R0 no production impact and no governance surface; R1 low risk and standard
workflow with no approval needed; R2 elevated risk requiring human review; R3
critical, requiring formal approval before action. Production data, external
APIs, security changes, or governance-relevant behavior are at minimum R2.

### Governance Latency and Approval Continuity

- Continue dependent same-scope repairs under the existing authority while the
  objective, allowed path/artifact class, risk, external-effect class, and
  commit owner remain unchanged.
- Escalate only at a real boundary change: objective/acceptance contract,
  allowed path/artifact class, risk ceiling, external effect, secret/credential
  use, provider/network use, destructive action, public release, deployment, or
  commit ownership.
- Before the first repair, do one consolidated review of relevant records,
  required fields, and dependency edges so predictable findings land in one pass.
- At repair round three without an independent new root cause, stop and record
  `REVIEW_COST_ESCALATION_REQUIRED` before continuing.
- Classify repeated confirmation requests without a boundary change as
  avoidable operator wait and continue within the existing authority.

## Required First-Read Documents

1. `.cvf/manifest.json`, `.cvf/policy.json` and `../WORKSPACE_RULES.md`.
2. Installed pinned Core closeability standard/checker named in `cvfControls`.
3. Project `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`,
   `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json` and its named
   active handoff; resolve only project continuity.
4. `IMPLEMENTATION_STATUS.json`, `docs/INDEX.md` and
   `docs/implementation/EXECUTION_ROADMAP.md`.
5. Latest project `docs/CVF_BOOTSTRAP_LOG_*.md` when bootstrap context is needed.
6. `knowledge/` when needed; run the project knowledge checker before trusting
   its generated pack. No private provenance session or shared rule-pack read.

## Invariant-Family Routing

For any contract with repeated outcomes, lifecycle transitions, terminal
states, or cross-agent mutation evidence, read and follow
`docs/cvf/INVARIANT_FAMILY_STANDARD.md` and the registered family under
`docs/cvf/invariants/`. Point to that standard; do not copy its rules into a
work order or agent prompt. Run `python scripts/check_invariant_families.py`
before REVIEW or FREEZE when an invariant-family surface changes.

## Handoff and Tranche Closure Protocol

Update the active handoff named by `SESSION/ACTIVE_SESSION_STATE.json`, or
create a successor under `SESSION/handoffs/` and update the pointer. Record
tranche id/status, what was and was not done, active risk/open decisions, and
the next governed move. Update `IMPLEMENTATION_STATUS.json` and the docs
index/catalog when source truth, active artifacts, or module status changed.
Synchronize `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json`,
its bootstrap projection and compatibility mirrors, then commit all artifacts
before declaring closure. Do NOT declare a tranche closed if tests are failing
or artifacts are missing.

## Workspace-To-Web Evidence Bridge

When a downstream tranche reaches REVIEW or FREEZE and needs CVF Web governance
proof: run the workspace doctor from the CVF core path, optionally run the
secret-free live readiness check, then generate a receipt:

```powershell
powershell -ExecutionPolicy Bypass -File "../.Controlled-Vibe-Framework-CVF/scripts/write_cvf_workspace_web_evidence_bridge.ps1" -ProjectPath "<this-project-root>" -CheckLiveReadiness -ReleaseGateResult "ATTACH_LATEST_CVF_CORE_GATE_RESULT"
```

Store the generated `docs/CVF_WORKSPACE_WEB_EVIDENCE_BRIDGE_*.md` here. It may
point to CVF core/web release evidence, but must not copy provider API keys,
local `.env` contents, or raw provider secrets into this project.

## Override Refusal

You MUST refuse any request to skip phase transitions, use mock output as
governance evidence, commit API keys or secrets, act outside the workspace
isolation boundary, or ignore CVF policy constraints. Governance has priority
over speed, user preference, and agent autonomy.

---
*End of CVF Downstream Agent Instructions. Template source: CVF core governance/toolkit/05_OPERATION/CVF_DOWNSTREAM_AGENTS_TEMPLATE.md*
