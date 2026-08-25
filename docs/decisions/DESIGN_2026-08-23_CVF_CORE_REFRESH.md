# DESIGN — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Phase: `DESIGN`
- Risk: `R2`
- Parent gate: `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Status: `OPEN_FOR_INDEPENDENT_DESIGN_REVIEW`
- Active role: `DESIGN_AUTHOR`
- Frozen Core target: `3b031fec35473e6ee6a554c4c72400e7a23b06c5`

## Selected design

Use the sanctioned hidden-Core reconciler directly from the downstream project
root, with only `-WorkspaceRoot` and without `-UpdateProjectManifests`, overlay
or pending-Core override. Before invoking it, create a timestamped workspace-
root preimage tree under `_cvf-core-backups/workspace-root-preimages-*` for all
17 declared root targets and an evidence-ineligible downstream rollback
preimage tree for the ten mutable downstream carriers listed below. Preserve
relative paths, existence state and raw SHA-256.

The reconciler backs up and replaces the clean hidden Core, performs exactly
one public clone, refreshes root artifacts, and retains the old clone. After it
returns, require full target equality and clean Core state; then patch this
project's full manifest/header pins explicitly and run
`scripts/initialize_cvf_clone.ps1`. The initializer performs one fetch,
regenerates ignored local binding, and invokes the doctor, whose freshness
check performs another fetch. Any observed tip other than the frozen target
at any operation triggers rollback and stop.

## External-effect architecture

- Successful BUILD network path: exactly three unauthenticated public Git
  operations to the declared CVF GitHub remote only—reconciler clone,
  initializer fetch, and initializer-invoked doctor fetch. An early failure
  consumes only the executed ordered prefix (zero through three), never a
  synthetic success count. Each records command owner, endpoint, observed full
  target and exit code; no credential helper or secret is used.
- Failure rollback owns exactly one additional conditional doctor fetch after
  restoration. It is recorded as `ROLLBACK_VERIFIER`, is not BUILD-success
  evidence, and makes total worker/rollback network use at most four. It uses
  the same URL/no-credential/frozen-target rules; any mismatch is recorded and
  the tranche remains stopped rather than accepting rollback as success.
- Independent REVIEW owns exactly one additional public Git fetch for its
  mandatory doctor rerun. Each later same-scope rereview, if required, owns at
  most one separately recorded doctor fetch. Reviewer operations are never
  counted as worker evidence or silently inherited by BUILD.
- Root ceiling: exactly the 17 targets enumerated by accepted INTAKE.
- Hidden-Core ceiling: canonical clone, one reconciler-created prior-Core
  backup, and on failure one preserved failed-replacement path, all contained
  by the exact workspace root.
- Active `operator-local` profile is read-only; no public-profile sync.
- No sibling manifest mutation, product source, catalog, roadmap, provider,
  credential, dependency install, database, deployment, commit or push.

## Exact downstream BUILD increment ceiling (12 paths)

1. `.cvf/manifest.json`
2. `AGENTS.md`
3. `knowledge/manifest.json`
4. `IMPLEMENTATION_STATUS.json`
5. `SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
7. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
8. `SESSION/SESSION_MEMORY.md`
9. `SESSION/handoffs/CVF_CORE_REFRESH_2026-08-23.md`
10. `docs/INDEX.md`
11. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json`
12. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md`

The later independent completion reviewer alone may create
`docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-23.md`. Governance
artifacts authored before BUILD—including INTAKE/reviews/DESIGN/SPEC/Work
Order—and all P4-C artifacts are protected from the worker.

Because the repository intentionally contains parked P4-C and Core-refresh
governance changes, BUILD scope is measured incrementally, not by treating the
whole `git status` as worker output. Immediately before BUILD, the Work Order
must freeze a sorted inventory with raw SHA-256 and existence for every dirty
path except the assessment. For the ten pre-existing mutable carriers above,
it must also freeze BUILD-start preimages. At return, unchanged protected paths
must match byte-for-byte, each worker-created path must be in the 12-path
ceiling, and each mutable carrier delta must be attributable only to the
refresh. Staging remains empty.

## Pin and knowledge consistency

- `.cvf/manifest.json.cvfCoreCommit` and the generated `AGENTS.md` header use
  the full target hash; no unrelated fields/content change.
- Ignored `.cvf/local-binding.json.resolvedCoreCommit` is regenerated and must
  equal Core HEAD, Core `origin/main` and manifest pin.
- `knowledge/manifest.json` refreshes only source pins made stale by authorized
  manifest/header/implementation-truth changes. It must pass the knowledge
  guard and may not change classification, owners or consumption policy.
- `IMPLEMENTATION_STATUS.json` records only this maintenance receipt and must
  not alter roadmap or module status.

## Evidence model

The root-effects JSON is the machine receipt and must contain schema/tranche/
target/timestamps, observed commits, exact allowed network operations, Core
and root/downstream backup paths, before/after arrays for all 17 root targets,
downstream BUILD-start/return inventories, commands/exit codes, rollback state
and staged-zero evidence. The worker return summarizes it without claiming
governance behavior or production readiness.

Required success gates include four-way Core/pin/binding equality, clean Core,
doctor PASS (bounded legacy warning allowed), session/mirror, knowledge,
catalog, file-size, invariant-family, repository and JSON guards, plus
`git diff --check`. Independent REVIEW recomputes all target, hash, containment,
incremental-scope and command evidence.

## Executable rollback design

On any failure after the reconciler begins:

1. resolve and verify canonical Core, prior-Core backup, failed-Core target,
   root preimages, failed-root delta and downstream preimages all remain inside
   the exact workspace root and outside every downstream repository except the
   named downstream preimage sources;
2. move, never delete, the replacement Core to the failed-Core backup and
   restore the prior Core to the canonical location;
3. restore every previously existing root target from preimage and verify its
   hash; move each newly created root target into the failed-root-delta tree;
4. restore the ten mutable downstream carriers from BUILD-start preimages,
   except retain/update the two evidence paths needed to record failure;
5. preserve every clone, backup, failed delta and evidence artifact; delete
   nothing; record trigger, containment results, moves, hashes, final Core/pin
   state and post-rollback doctor result, then stop.

## Alternatives rejected

- Root `Update-CVF-Workspace.ps1`: smaller in-place fast-forward, but no Core
  backup/rollback and no downstream pin update.
- `-UpdateProjectManifests`: skips this portable manifest and would broadly
  rewrite unrelated absolute-schema sibling manifests.
- Manual `git pull`: bypasses the sanctioned reconciler required by project
  protocol.
- Proceeding with P4-C while doctor fails: violates the freshness gate.

## Invariant-family applicability

`NOT_APPLICABLE`: this maintenance tranche introduces no shared receipt/model
contract, outcome-controlled fields, counter relations, multiple validator
surfaces, coupled prompt/schema artifacts or adjacent runtime invariant family.

## Next governed move

Independent DESIGN review only. SPEC, Work Order, reconciliation and BUILD
remain unauthorized.

## Evidence-contract amendment — 2026-08-23

- Amendment authority: operator-approved reopening of `DESIGN/SPEC` for the
  three provenance blockers retained by the post-escalation authorization
  rereview
- Amendment status: `OPEN_FOR_INDEPENDENT_DESIGN_AMENDMENT_REVIEW`
- Author role: `DESIGN_AUTHOR`
- Effect boundary: documentation and deterministic local checks only; no Core
  mutation, network, reconciliation, BUILD, install, provider, commit or push

### Problem statement and claim correction

The prior Work Order tried to make an ordinary, uncommitted filesystem receipt
prove three stronger properties than its available observation surfaces can
establish: continuous non-existence of a partial clone, kernel-level ancestry
between an outer PowerShell process and Git trace2 spans, and externally
immutable review history. Repeatedly adding receipt fields cannot convert
post-hoc observations into those guarantees.

This amendment preserves the safety outcome while correcting the proof claim.
Evidence must prove named observations, exact byte preservation and
cross-surface consistency. It must not claim continuous observation,
tamper-proof process attestation or cryptographic immutability. Any future need
for those stronger claims requires a separate boundary decision authorizing an
OS audit/ETW facility or externally immutable/signature-backed store.

### Selected evidence architecture

#### 1. Reconciler-return observation and candidate preservation

The worker command envelope performs one inseparable ordered sequence: record
its start marker; invoke the exact reconciler command; capture its exit; and,
before any worker rollback handler or later project mutation, write an
immediate `RECONCILER_RETURN` observation into raw evidence. That observation
records the canonical-Core existence and complete contained inventory and all
matching failed-replacement candidate paths with existence plus complete
relative-path/type/size/raw-SHA-256 inventories. The timestamp and invocation
id are shared with the command envelope.

BUILD-start evidence must similarly freeze complete byte inventories—not only
names or existence—for every pre-existing failed-replacement candidate. Final
success or failure evidence must reproduce each prior candidate byte-exact and
must preserve every new candidate observed at `RECONCILER_RETURN` byte-exact at
a contained final path. An absent candidate is reported only as
`NOT_OBSERVED_AT_RECONCILER_RETURN`; it may not be restated as proof that a
partial directory never existed during reconciler execution. This design
proves the two observed checkpoints and their preservation relation.

#### 2. Command-envelope and Git-operation correlation

Every worker, rollback-verifier and independent-review doctor invocation uses
the same deterministic command-envelope contract. Each envelope records a
fresh UUID, envelope PowerShell PID, exact normalized command and arguments,
start/exit timestamps, exit code, transcript hash and raw trace paths. Before
launch, it injects the UUID through the already reviewed per-invocation Git
trace configuration. The corresponding raw trace2 `def_param`, SID, argv,
start/exit and endpoint records must contain that UUID and fall within the
envelope window. One UUID maps to exactly the operation prefix owned by that
outer command and cannot occur in another BUILD/rollback/review envelope.

The rollback verifier and every reviewer doctor must therefore carry the exact
doctor PowerShell command, their own envelope/transcript/exit record and their
own disjoint trace UUID; a bare `git fetch` is not an acceptable substitute.
The resulting claim is deterministic invocation correlation across envelope,
transcript and Git trace surfaces. It is explicitly not kernel-attested parent/
child ancestry and cannot be described as such.

#### 3. Reviewer-observed append preservation

Before changing a completion payload on a rereview, the independent reviewer
freezes a `PRIOR_REVIEW_STATE` observation containing the current completion
artifact existence/raw hash, canonical digest of its current `reviewRuns`, and
the exact path/type/size/raw-hash inventory of the existing reviewer-anchor
directory. A fresh disjoint review UUID then creates exactly one new anchor and
appends exactly one run while preserving every observed prior payload element
and anchor byte-exact. The current reviewer recomputes the pre/post relation and
records it in the completion review and new anchor.

For the first review, the prior completion state is explicitly absent and the
prior anchor inventory is empty. For later reviews, the observation is a
reviewer-owned precondition for that run. The accepted claim is
`REVIEWER_OBSERVED_APPEND_PRESERVATION`; it is not external WORM storage,
signed history or proof that an earlier local state could never have been
rewritten before the reviewer observed it.

### Outcome and ownership contract

The later SPEC must define the shared evidence contract for `SUCCESS`, each
ordered failure prefix, `ROLLBACK_VERIFIER`, first `REVIEW` and appended
`REREVIEW`. Required/forbidden/conditional observation, envelope, trace,
candidate and prior-review fields must be owned once and consumed identically
by the root-effects validator and independent-review validator. Worker evidence
cannot satisfy reviewer ownership; reviewer evidence cannot convert failure to
success.

This is a materially changed R2 shared receipt with outcome-controlled fields,
multiple validator surfaces and prior adjacent-family findings. The earlier
`NOT_APPLICABLE` decision is superseded for this amendment. Before SPEC review,
`SPEC_AUTHOR` must register one invariant family under
`docs/cvf/invariants/registry.json`, make its matrix the sole semantic owner of
the outcome/field/relation rules, and reference its canonical digest rather
than copying matrix rules into the Work Order or review.

### Changed-set and later-phase effect

This DESIGN amendment changes no worker/root/network ceiling. It anticipates a
SPEC-owned invariant matrix and registry entry plus reviewer-owned preflight/
anchor evidence surfaces. Exact paths and digests are decided in SPEC and must
later be reflected in a newly reviewed Work Order. The current Work Order and
its `6ab0929b...` digest remain historical reviewed input and are not repaired
under this authority.

### Alternatives rejected

- Require OS kernel ancestry (ETW/auditing) and external WORM or signed
  attestation now: stronger assurance, but it introduces new host facilities,
  external effects and authority not present in this tranche.
- Infer historical absence or immutability from final-state receipts: not
  logically supportable and already produced repeated same-root review cost.
- Drop candidate, command or review-history proof entirely: would weaken the
  accepted preservation and independent-ownership controls.

### Amendment stop conditions and next move

Stop if independent review finds that an accepted safety outcome depends on a
stronger claim than the selected observation/correlation model, or if the
proposed invariant family cannot express all terminal outcomes without
duplicated semantic ownership. Next move is independent DESIGN amendment
review only. SPEC remains gated on `DESIGN_AMENDMENT_PASS`; Work Order repair,
reconciliation and BUILD remain unauthorized.
