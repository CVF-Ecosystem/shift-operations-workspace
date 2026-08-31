# INTAKE — CVF Core Refresh Attempt 4 Retained Carrier

- Tranche: `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31`
- Date: `2026-08-31`
- Phase: `INTAKE`
- Status: `READY_FOR_INDEPENDENT_INTAKE_REVIEW`
- Risk: `R2`
- Active role: `INTAKE_AUTHOR`
- BUILD authority: `NOT_GRANTED`
- External-effect authority: `NOT_GRANTED`
- Parent rebase tranche:
  `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-2026-08-31`
- Accepted parent DESIGN SHA-256:
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- Independent parent DESIGN review SHA-256:
  `8b259c3823589d17937f5b25b85fa0c7ac8559003f68a360d96c8a04d3d85ede`

## 1. Authority and intent

The operator authorized the orchestrator to continue through governed
tranches without repeated confirmation. The independently accepted parent
DESIGN requires a separate prerequisite carrier tranche before the parked
attempt-4 rebase may advance to SPEC. The orchestrator recorded that
transition in
`SESSION/handoffs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31.md`.

This INTAKE opens only the carrier prerequisite. Its intent is to govern the
later creation, deterministic verification, independent review and freeze of
one retained PowerShell carrier and its test suite. The carrier must make the
parent DESIGN's exact raw-token dispatcher, mode separation, closed callable
graph and zero-network/no-effect rehearsal contract independently reviewable
as stable bytes before any later rebase Work Order can reference them.

This authority does not open or resume the parent rebase SPEC, Work Order or
BUILD. It does not authorize execution of the future carrier against the Core,
or any external effect.

## 2. Risk classification

Risk is `R2`. Although this prerequisite has a zero-external-effect BUILD
boundary, its future executable source is governance-significant and is
intended to become an activation dependency for a separate Core reconciliation
tranche. Human review, explicit phase transitions and independent REVIEW are
therefore mandatory. The project policy risk ceiling remains `R2`.

No provider call is required to establish this repository-maintenance INTAKE.
No claim that CVF governs AI or agent behavior is made; mock output is not
accepted as governance evidence.

## 3. Full control-chain boundary

This prerequisite must traverse its own complete chain without skipping:

```text
INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE
```

Each phase owns only its phase artifact or expressly reviewed changed set.
Passing one phase does not silently authorize the next. In particular:

- INTAKE review may authorize DESIGN only;
- DESIGN review PASS is required before SPEC;
- SPEC review PASS is required before Work Order;
- independent authorization review of the exact Work Order is required before
  BUILD;
- a distinct implementation worker may act only within the reviewed BUILD
  ceiling; and
- independent completion REVIEW must pass before FREEZE publishes the exact
  carrier and test hashes.

The parent rebase remains parked throughout this prerequisite. Carrier FREEZE
is a dependency that may support a later explicit parent phase transition; it
is not parent BUILD or external-effect authority.

## 4. Exact eventual implementation ceiling

A future independently reviewed carrier Work Order may authorize BUILD changes
to exactly these two implementation paths and no others:

1. `scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1`
2. `tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py`

The `.ps1` is retained implementation source. The `.py` is its deterministic
static, raw-dispatcher, call-graph, mutation-corpus and no-effect contract test.
They do not exist by authority of this INTAKE, and this phase must not create,
patch, copy, regenerate or execute either file.

The future Work Order must enumerate an exact path-by-path changed-set ceiling
before BUILD and must preserve the parent DESIGN's requirement that its Work
Order author owns only the Work Order while a distinct implementation worker
owns only these two implementation paths.

## 5. Allowed governance artifact families

Subject to separate phase transitions and exact phase ownership, this tranche
may later create only the bounded governance families required for its chain:

- one carrier INTAKE and one independent INTAKE review;
- one carrier DESIGN and one independent DESIGN review;
- one carrier SPEC, one invariant matrix, one static invariant pin, one
  registry entry and one independent SPEC review;
- one exact carrier Work Order and one independent authorization review;
- the two exact BUILD paths above and one implementation-worker return;
- one independent completion review; and
- one carrier handoff plus only the bounded canonical continuity, index and
  implementation-status records required for terminal FREEZE synchronization.

DESIGN and SPEC must convert these artifact classes into collision-free exact
paths before their respective downstream gates. Applicability under
`docs/cvf/INVARIANT_FAMILY_STANDARD.md` is treated as triggered by the R2
mode-dependent carrier contract, multiple validator surfaces and the adjacent
attempt-3 wrapper failure. The SPEC author, not this INTAKE author, owns the
new matrix, static pin and registry entry.

No phase author may modify an artifact owned by another phase. No governance
artifact family listed here expands the exact two-path implementation ceiling.

## 6. Acceptance approach for later phases

DESIGN must retain and make testable the accepted parent architecture,
including at minimum:

- a raw `$args` dispatcher with no PowerShell `param(...)` binding and exact,
  case-sensitive `ParseOnly`, `DryRun` and `Execute` tuples;
- deterministic refusal of missing, duplicate, reordered, abbreviated,
  aliased, positional, combined, coercion-shaped or extra tokens;
- closed per-mode in-process API, native-child and argv allowlists;
- deterministic AST/function call-graph closure with mutation negatives;
- no child process in `ParseOnly`, only exact local read-only Git queries in
  `DryRun`, and explicit separation from the later parent `Execute` authority;
- `ParseOnly` and `DryRun` zero filesystem-write, zero network-attempt and
  zero network-child evidence with canonical counters and child ledgers;
- mode-specific, acyclic artifact/hash inputs with later authority identities
  deferred to parent `Execute`; and
- fail-closed behavior on parser, hash, path, containment, reparse, callable,
  child, argument, counter or contract drift.

SPEC must express the accepted DESIGN as exact requirements, outcome/mode
matrix relations, static pins, mutation-corpus ids, expected refusal codes,
counts and digests. The Work Order must bind the accepted artifact hashes and
exact local verification commands. BUILD must create only the two exact paths.
REVIEW must independently hash and inspect the retained bytes, execute the
authorized deterministic tests and demonstrate the no-effect modes without
doctor, fetch, reconcile or network. FREEZE must publish the exact raw SHA-256
of both BUILD files and preserve a bounded claim.

Historical results, prose assertions or a worker's self-review are not fresh
acceptance evidence. A provider call would not substitute for deterministic
carrier source and test evidence.

## 7. Roles and independence

- `ORCHESTRATOR` records authority, routes phases and keeps the parent rebase
  parked; it does not implement or self-approve.
- `INTAKE_AUTHOR` owns only this document.
- `INDEPENDENT_INTAKE_REVIEWER` owns only the INTAKE review and must state
  findings and waivers explicitly.
- Later `DESIGN_AUTHOR`, `SPEC_AUTHOR` and `WORK_ORDER_AUTHOR` own only their
  respective phase artifacts.
- A distinct `INDEPENDENT_DESIGN_REVIEWER`, `INDEPENDENT_SPEC_REVIEWER` and
  `INDEPENDENT_AUTHORIZATION_REVIEWER` check the exact accepted bytes at each
  gate.
- A distinct `IMPLEMENTATION_WORKER` may own only the two exact BUILD paths
  after authorization review PASS.
- An `INDEPENDENT_COMPLETION_REVIEWER` must compare requirements, source,
  tests, outputs and changed-set evidence before `CLOSER` and
  `SESSION_SYNC_STEWARD` perform bounded FREEZE synchronization.
- No commit steward is activated by this INTAKE. Commit and push remain
  unauthorized.

## 8. Explicit exclusions and protected-state rule

This tranche has zero Core, workspace-root, downstream-pin, binding, parent
rebase-lifecycle, network, provider, credential, fixture, product, runtime,
database, installation, deployment, release, commit or push authority.
Specifically excluded are:

- doctor, initializer, fetch, clone, pull, push, reconciler or any remote
  access;
- mutation or execution inside the hidden CVF Core or workspace root;
- manifest/AGENTS pin changes or `.cvf/local-binding.json` regeneration;
- parent attempt-4 SPEC, Work Order, evidence directory, reconciliation,
  rollback or completion lifecycle;
- the inherited conformance fixture and its baseline of
  `28 passed, 2 skipped, 7 failed`;
- P4-E source or phase movement, XR1 repair, product/API/UI/runtime/database
  changes, installation, deployment or release; and
- any provider/AI-governance, production-readiness or target-adoption claim.

The protected operator assessment must not be opened, read, hashed, named,
inventoried, staged or used. Broad downstream untracked inventory is
prohibited. Verification must use only exact allowlisted paths and local
read-only facts needed for the current phase.

## 9. Stop conditions

Stop without widening scope, retrying or repairing in place if any of the
following occurs:

- continuity, phase, role, authority, accepted parent DESIGN or review hash
  drift;
- any request to create or execute the carrier before exact Work Order review;
- path collision, changed-set ambiguity or inability to preserve exact phase
  ownership;
- any need for doctor, fetch, reconcile, network, credentials, Core/root/pin/
  binding mutation or parent rebase activation;
- any contact with protected state or need for broad inventory;
- a need to alter the fixture, P4-E, XR1, product/runtime/database, install,
  deployment, release, commit or push boundary; or
- missing, unreadable, contradictory or unverifiable required evidence.

A stop is a bounded refusal and does not grant another role permission to
hotfix, reinterpret or silently advance the phase.

## 10. Bounded claim and next move

This INTAKE proves only that the operator's continuing authority and the
accepted parent DESIGN have been converted into a bounded R2 prerequisite
request with a full seven-phase chain, an exact future two-path implementation
ceiling and zero external-effect authority. It does not prove the carrier
exists, is correct, is executable, has passed tests or may be used by the
parent rebase.

Next governed move: a distinct `INDEPENDENT_INTAKE_REVIEWER` compares this
exact artifact against the active carrier handoff, the accepted parent DESIGN
and its final independent review, using local allowlisted facts only. Carrier
DESIGN, SPEC, Work Order, BUILD, source creation, test creation, execution,
doctor/fetch/reconcile, network and all other external effects remain
unauthorized until their explicit later gates.
