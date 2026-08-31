# DESIGN — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Phase: `DESIGN`
- Risk: `R2`
- Parent gate: `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Status: `OPEN_FOR_INDEPENDENT_DESIGN_REVIEW`
- Current Core: `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen observed target: `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`
- Active role: `DESIGN_AUTHOR`

## 1. Selected architecture

Use the existing bootstrap-native reconciliation path only:

1. capture a complete bounded preflight and preservation set;
2. invoke the sanctioned public-Core reconciler from the downstream project
   root with only the workspace-root argument and no manifest-update, overlay
   or pending-backup override;
3. immediately verify the replacement Core remote, clean state and full target;
4. replace exactly the downstream manifest pin and generated `AGENTS.md` pin
   header from the old full hash to the frozen full hash;
5. invoke `scripts/initialize_cvf_clone.ps1` to consume the new pin, regenerate
   the ignored local binding and run its built-in doctor;
6. write bounded evidence and synchronize the exact maintenance/continuity
   carriers; then return for independent completion review.

No custom clone implementation, in-place pull, public-profile synchronization,
product import or Core runtime adoption is selected. Refreshing the hidden
read-only reference does not make its 190-path runtime/governance delta part of
the downstream application.

## 2. Ownership and locations

- The sanctioned reconciler owns hidden-Core backup/replacement and the
  accepted 17 workspace-root targets named by the INTAKE.
- The downstream worker owns only the exact pin patch, initializer invocation,
  ignored binding regeneration, two worker evidence artifacts and declared
  continuity carriers.
- The current Core and every backup/evidence/preimage/failed-delta directory
  must resolve beneath the exact workspace root. The downstream repository is
  never used as a backup destination.
- `SESSION/handoffs/CVF_CORE_REFRESH_2026-08-29.md` remains the active
  maintenance handoff. The P4-E handoff and P4-E decision artifacts are parked
  predecessor evidence and are read-only during BUILD.
- Independent completion review owns only its review artifact and its own
  doctor invocation. Worker evidence cannot self-approve completion.

## 3. Preservation-first preflight

Before any authorized external effect, a later Work Order must require one
contained refresh evidence directory under `_cvf-core-backups/` and record:

- exact workspace/project/Core containment roots and resolved paths;
- Core `HEAD`, local `origin/main`, expected remote, clean status and ancestry;
- downstream `HEAD`, local `origin/main` and staged-zero state;
- current active rule-pack profile path, value and raw hash, which must prove
  `operator-local` before execution and remain byte-identical afterward;
- existence, type, size and raw SHA-256 preimages for all 17 accepted root
  targets, including explicit absence of the three overlay targets;
- for each of the 13 section-7 paths and ignored local binding: explicit
  `PRESENT` plus raw preimage, or explicit `ABSENT`; both evidence paths must
  be `ABSENT` for the first BUILD or preflight stops;
- full raw hashes for every explicitly named parked P4-E artifact and every
  pre-BUILD Core-refresh governance artifact;
- existence and complete contained inventory for prior Core backups and any
  pre-existing failed-replacement/failed-root-delta directories relevant to
  this tranche.

The protected operator assessment remains wholly unobserved. Preflight may use
tracked-diff status plus explicit allowlisted paths; it must not run a broad
untracked inventory. Consequently, evidence must not claim global absence or
byte equality for arbitrary untracked files. It may claim only preservation of
explicitly observed paths and conformance to authorized command/output paths.

Any Core dirt, staged path, unexpected tracked delta, missing explicit artifact,
changed reconciler surface, non-operator-local profile, containment failure or
preimage failure stops before reconciliation.

## 4. Ordered successful execution graph

### Step A — reconciler

Invoke the unchanged Core script
`scripts/update_cvf_workspace_public_core.ps1` from the current clean Core with
the exact workspace-root argument only. Explicitly omit
`-UpdateProjectManifests`, overlay input and pending-Core-backup override.

The command performs the single public clone and may update the 17 root
targets. Immediately on return, before pin or initializer changes, record the
exit code, canonical Core existence, resolved backup paths, full replacement
Core `HEAD`, remote, clean status and root-effect postimages. Exit nonzero,
missing backup, unexpected root target or replacement target other than
`06c3d040...` enters rollback.

All 17 root entries form one closed ordered set. Each entry records relative
and resolved contained path, existence, type, size and raw hash when present,
plus exactly one computed effect: `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE`.
Success and rollback must each account for 17/17 with no residual root effect.

### Step B — pin bridge

After Step A alone proves clean Core `HEAD == origin/main ==` frozen target:

- replace `.cvf/manifest.json.cvfCoreCommit` exactly once from the old full pin
  to the new full pin, with no other manifest field change;
- replace the generated `AGENTS.md` `CVF Commit` header exactly once from the
  old full pin to the new full pin, with no other `AGENTS.md` content change.

Zero or multiple matches, any unexpected byte delta, JSON invalidity or pin
inequality enters rollback.

### Step C — initializer and built-in doctor

Invoke `scripts/initialize_cvf_clone.ps1` from the downstream project. It must
consume the already patched target, use the existing Core, fetch the declared
public remote, check out the full pin, regenerate `.cvf/local-binding.json` and
invoke its built-in workspace doctor. The worker does not run a separate fourth
doctor on the successful path.

Success requires the initializer exit zero, doctor PASS with only the accepted
legacy-catalog warning, clean Core and equality of:

1. Core `HEAD`;
2. Core local `origin/main`;
3. `.cvf/manifest.json.cvfCoreCommit`;
4. the `AGENTS.md` full pin header; and
5. `.cvf/local-binding.json.resolvedCoreCommit`.

All five must equal the frozen target. Otherwise rollback begins.

### Step D — downstream synchronization

Write the root-effects receipt and worker return, then update only the exact
maintenance/status/continuity carriers in section 7. Preserve P4-E at
`DESIGN_REVIEW_PASS` and set the next move to independent completion review.
Run JSON, session/mirror, Project Knowledge, invariant-family, catalog,
file-size, repository and scoped diff guards. Staged content remains forbidden.
After independent `REVIEW_PASS`, a separately declared
`CLOSER/SESSION_SYNC_STEWARD` owns the final return-to-P4-E edits on these same
continuity paths; neither worker nor reviewer may silently open P4-E SPEC.

## 5. Network and target-movement model

The successful worker graph permits exactly three ordered, top-level Git
operations—not inferred HTTP-request counts—to
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`:

1. reconciler-owned clone;
2. initializer-owned fetch;
3. initializer-doctor-owned fetch.

Each command transcript records owner, ordered position, endpoint, exit code
and observed full target. Credential helpers, tokens and alternate remotes are
forbidden. Success requires all three operations and the frozen target.

Failure records only the actually executed ordered prefix `0..3`; it cannot
manufacture a success count. After restoration, rollback may invoke exactly one
additional doctor as `ROLLBACK_VERIFIER`. That fetch is failure evidence only,
may observe a newer public tip and does not convert failure to success.

After a successful worker return, the independent completion reviewer owns
exactly one fresh doctor invocation and its one fetch. A later rereviewer, only
if required, owns at most one separately authorized doctor invocation. Reviewer
operations never count as worker evidence.

If the reviewer-owned doctor observes target movement after a successful
worker return, the reviewer records `REVIEW_TARGET_MOVEMENT` and performs no
repair. The reviewed Work Order must preauthorize a distinct `REPAIR_WORKER`
to execute rollback only, using the frozen BUILD preimages, with no new
reconciliation attempt. After rollback evidence and rereview, any new target
still requires fresh operator authority and phase amendments.

Any advertised or cloned `main` different from the frozen target causes stop
and preservation-first rollback. Rebasing the target requires fresh operator
authority plus bounded INTAKE/DESIGN/SPEC/Work Order review as applicable.

## 6. Executable rollback

On any failure after Step A begins:

1. record the trigger and containment results before moving anything;
2. preserve the replacement Core at a unique failed-replacement path; never
   delete it or any prior backup/evidence;
3. restore the prior clean Core to the canonical path and verify its old full
   commit and expected remote;
4. restore every previously existing root target byte-exact from preimage;
   move every newly created root target with no preimage into a contained
   failed-root-delta tree;
5. first restore both pin carriers, all nine shared continuity carriers and
   local binding to their observed preimages and record that checkpoint;
6. run at most one rollback-verifier doctor and record its exact result; the
   expected freshness failure after restoring an old Core is not success;
7. only afterward may shared carriers record the failure, while pins/binding
   and parked P4-E artifacts remain restored;
8. retain the two canonical evidence artifacts as the sole exception to
   restoring their recorded `ABSENT` state. Record each as `CREATE`; their
   final raw hashes belong to the later independent terminal review;
   no other absent-before-BUILD downstream path may survive. Stop without retry.

If any restore/hash/containment check fails, disposition is
`FAILURE_ROLLBACK_INCOMPLETE`; the worker must not continue or claim a clean
rollback.

## 7. Exact downstream worker ceiling

The worker may change at most these 13 tracked downstream paths, classified as
two pin carriers (P), nine shared continuity carriers (S), and two evidence
carriers (E):

1. `(P)` `.cvf/manifest.json`
2. `(P)` `AGENTS.md`
3. `(S)` `knowledge/manifest.json`
4. `(S)` `IMPLEMENTATION_STATUS.json`
5. `(S)` `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
6. `(S)` `SESSION/ACTIVE_SESSION_STATE.json`
7. `(S)` `CVF_SESSION/ACTIVE_SESSION_STATE.json`
8. `(S)` `SESSION/SESSION_MEMORY.md`
9. `(S)` `SESSION/handoffs/CVF_CORE_REFRESH_2026-08-29.md`
10. `(S)` `docs/INDEX.md`
11. `(S)` `docs/implementation/EXECUTION_ROADMAP.md`
12. `(E)` `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json`
13. `(E)` `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md`

The ignored `.cvf/local-binding.json` is one additional declared local effect.
The independent reviewer alone may create
`docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md`.

INTAKE/review/DESIGN/SPEC/Work Order artifacts, all P4-E decision/handoff
artifacts, product/runtime/database/catalog files and every other tracked path
are protected byte-exact. A Work Order may narrow this ceiling but may not add
a path without returning to the appropriate reviewed phase.

## 8. Evidence and claim contract

`CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json` is the canonical machine
receipt. It owns outcome, frozen/observed refs, command results, network prefix,
Core/backup locations, 17 root pre/post states, downstream carrier checkpoints,
pin/binding equality, guard results, rollback state and prohibited-effect
assertions. The Markdown worker return summarizes and links it; it is not a
second semantic owner.

Evidence-carrier precedence is explicit: fresh BUILD requires both canonical
paths absent; success or failure may create and retain exactly both. Their
recorded pre-state and `CREATE` effect are mandatory. Neither worker artifact
may contain its own final raw hash or require the other's final hash. A later
retry cannot overwrite them and requires a reviewed attempt-path change.

Terminal outcomes are `SUCCESS`, `FAILURE_ROLLED_BACK` and
`FAILURE_ROLLBACK_INCOMPLETE`. Success requires the exact three-operation
worker graph and five-way target equality. Failure forbids success claims,
records only its executed prefix and conditionally owns one rollback verifier.
For every worker outcome, an independent terminal reviewer recomputes the
receipt, path ceilings, target, doctor/rollback and claim boundary, and records
the final raw SHA-256 of both worker evidence artifacts in the separately owned
completion-review artifact. That artifact need not and must not self-hash.

Evidence may claim only named pre/post observations and preservation
relations. It must not claim continuous filesystem observation, OS-attested
process ancestry, WORM/tamper-proof history or arbitrary-untracked absence.

This evidence supports only deterministic public-Core pin/freshness
reconciliation. It does not prove that CVF controls an AI/agent, that Core
runtime code is adopted by the downstream product, or that either repository
is production-ready. No provider call is required for this claim.

## 9. Invariant-family applicability

`APPLICABLE`. This R2 tranche introduces one shared machine receipt across
three outcomes, outcome-controlled fields, exact network-counter relations and
worker/reviewer validator surfaces. Before SPEC review, the SPEC_AUTHOR must
register family `CVF-CORE-REFRESH-OUTCOMES-2026-08-29` in the canonical
registry, create its sole semantic matrix under `docs/cvf/invariants/`, and
bind its canonical digest from SPEC, Work Order and review proof. Per-outcome
rules must not be copied into those later artifacts.

## 10. Alternatives rejected

- Manual `git pull` or root wrapper: lacks the required preserved replacement
  and downstream pin sequencing.
- `-UpdateProjectManifests`: may rewrite unrelated sibling manifests and does
  not match this portable downstream pin contract.
- Custom clone/bootstrap scripts: duplicate unchanged sanctioned tooling and
  widen command/evidence scope.
- Treating the Core delta as documentation-only: contradicted by 115 paths
  outside `docs/` and Markdown.
- Full arbitrary-untracked inventory: violates the protected assessment
  boundary and would support an unjustified global absence claim.
- Provider evidence: irrelevant to the bounded maintenance claim and not
  authorized.

## 11. DESIGN acceptance and next move

Independent review must verify command feasibility, target movement handling,
the exact 17-root/13-worker ceilings, pin sequencing, success/failure network
accounting, executable rollback, P4-E byte protection, invariant-family
trigger and narrow claim boundary.

Next move is independent DESIGN review only. SPEC, Work Order, reconciliation,
network/root effects, P4-E SPEC, commit and push remain unauthorized.
