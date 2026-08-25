# Independent DESIGN Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Reviewed phase: `DESIGN` only
- Reviewer role: `INDEPENDENT_DESIGN_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

The review compared
`docs/decisions/DESIGN_2026-08-23_CVF_CORE_REFRESH.md` with the accepted INTAKE
and final INTAKE review, canonical continuity and parked P4-C checkpoint,
manifest/policy/AGENTS requirements, current reconciler, installer, initializer
and doctor source, current pin/knowledge structures, and the reviewed
2026-08-20 refresh evidence and rollback lessons.

Read-only verification confirmed the selected reconciler flags are bounded to
`-WorkspaceRoot`: `-UpdateProjectManifests`, `-OverlaySourcePath` and
`-AllowPendingCoreBackup` are excluded. The root ceiling resolves to the exact
17 accepted targets. The downstream incremental ceiling contains 12 unique
paths: ten pre-existing mutable carriers plus worker-owned root-effects and
worker-return evidence. Manifest and AGENTS full pins, ignored local binding,
the three affected Project Knowledge source pins, implementation truth, the
canonical/mirror/bootstrap/memory/handoff/index continuity surfaces and both
worker evidence artifacts are covered. The independent completion review is
correctly reviewer-only and outside worker output.

The preimage/increment model is feasible despite the pre-existing dirty P4-C
set: it freezes every non-assessment dirty path, byte-protects all unrelated
governance/P4-C artifacts, uses BUILD-start hashes for the ten mutable
carriers, admits only two newly created worker evidence paths, and requires an
empty staged set. The rollback design preserves rather than deletes Core,
root, downstream and failure evidence, with containment, move/restore,
hash-verification, new-root quarantine and post-rollback doctor recording.

Current read-only state remains downstream `HEAD` and `origin/main` both at
`0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, staged zero, and clean hidden Core
`7d9f360a3df11ac998972728000785799399c02b` exactly `0` ahead / `1` behind
frozen fetched target
`3b031fec35473e6ee6a554c4c72400e7a23b06c5`. Session-state and
`git diff --check` pass. No network or filesystem effect was performed, and
the operator assessment was not accessed or used.

## Numbered findings

1. **CORE-REFRESH-DESIGN-REV-F1 — The two-operation public Git ceiling is
   impossible under the selected command graph.** The reconciler performs one
   `git clone`. The selected `scripts/initialize_cvf_clone.ps1` then performs
   `git fetch origin main --quiet`, and subsequently invokes
   `check_cvf_workspace_agent_enforcement.ps1`; that doctor independently
   performs another `git fetch origin main --quiet`. The declared BUILD path
   therefore performs at least three public Git operations before any later
   independent-review doctor rerun, not the stated "second and final" two.
   The 2026-08-20 receipt counted clone plus initializer fetch but does not
   override current executable source truth. Repair the design to choose and
   freeze an actually executable command graph: either authorize and account
   for all three worker operations plus each separately owner-scoped reviewer
   doctor fetch, or select a reviewed alternative that truly limits the count
   while still regenerating the ignored binding and satisfying the mandatory
   doctor. Every authorized operation must bind the exact public URL, no
   credentials and the frozen target, with target movement triggering rollback
   and stop.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted DESIGN boundaries

Apart from F1, the direct reconciler selection, exact 17-root and 12-downstream
incremental ceilings, pin/binding/knowledge equality model, dirty-carrier
preimages, reviewer-only completion artifact, executable preservation-only
rollback, P4-C parking/protection and no product/provider/install/database/
deployment/commit/push/claim widening are internally consistent and feasible.

Invariant-family applicability is validly `NOT_APPLICABLE`: this maintenance
tranche does not introduce or materially change a runtime shared receipt,
outcome-field, counter, multi-validator or coupled contract family.

## Disposition

`DESIGN_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-DESIGN-REV-F1` for bounded DESIGN repair and
independent rereview. SPEC, WORK_ORDER, reconciliation and BUILD remain
unauthorized.

## Bounded rereview — CORE-REFRESH-DESIGN-REV-F1

The repaired DESIGN now binds BUILD to exactly three worker-owned,
unauthenticated public Git operations against the manifest-declared remote
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`: the
reconciler clone, the initializer fetch, and the fetch performed by the doctor
invoked from the initializer. Each operation must record its command owner,
endpoint, observed full target and exit code; credential helpers and secrets
are forbidden. All three operations are frozen to
`3b031fec35473e6ee6a554c4c72400e7a23b06c5`, and any observed target movement
requires rollback and stop.

Independent REVIEW owns exactly one additional, separately recorded doctor
fetch. Each later same-scope rereview, if required, independently owns at most
one further separately recorded doctor fetch. These reviewer-owned operations
cannot be counted as worker evidence or inherited as BUILD authority. This
correctly models the executable reconciler/initializer/doctor command graph
without widening the BUILD network ceiling.

1. **CORE-REFRESH-DESIGN-REV-F1 — CLOSED.** The repaired operation count,
   ownership, exact endpoint, no-credential rule, frozen-target check and
   movement-triggered rollback/stop conditions are complete and testable.

No other accepted DESIGN boundary regressed. The exact 17 root targets and 12
downstream incremental paths, ten mutable carriers plus two worker evidence
paths, pin/binding/knowledge/continuity coverage, reviewer-only completion
artifact, preservation-first rollback, P4-C protection, invariant-family
`NOT_APPLICABLE` decision and prohibited side-effect/claim boundaries remain
intact.

Rereview guards: `python scripts/check_session_state.py` passed;
`git diff --check` passed; the staged set is empty; hidden Core remains clean
at `7d9f360a3df11ac998972728000785799399c02b`, exactly `0` ahead / `1` behind
the frozen fetched target. No network, reconciliation, provider, credential,
install, deployment, commit or push operation was performed. The operator
assessment was not accessed or used.

### Rereview findings and waivers

1. Findings: `NONE`.
2. Waivers: `NONE`.

## Final disposition after bounded rereview

`DESIGN_REVIEW_PASS`.

The earlier `DESIGN_REVIEW_CHANGES_REQUIRED` disposition is superseded for
this DESIGN revision. SPEC may proceed only through an explicit role/phase
transition; reconciliation and BUILD remain unauthorized.

## DESIGN amendment rereview — conditional rollback network

- Amendment source: SPEC finding `CORE-REFRESH-SPEC-REV-F2`
- Reviewer role: `INDEPENDENT_DESIGN_AMENDMENT_REVIEWER`
- Amendment scope: success/failure/rollback public-Git operation accounting
- Amendment disposition: `AMENDMENT_PASS`

The amendment correctly separates the successful BUILD path from failure
handling. Success requires exactly the ordered three worker-owned operations:
reconciler clone, initializer fetch and initializer-invoked doctor fetch. An
early failure records only the actually executed ordered prefix, from zero
through three; it cannot manufacture the three-operation success condition.

After restoration, failure rollback owns exactly one additional conditional
doctor fetch under the distinct `ROLLBACK_VERIFIER` identity. Total
worker-plus-rollback network use is therefore bounded to at most four on a
failure path. The verifier uses only
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`, carries
the same no-credential/no-secret and frozen-target rules, records mismatch or
movement, and leaves the tranche stopped. It is explicitly forbidden as
BUILD-success evidence. Independent REVIEW/rereview doctor fetches retain
their separately owner-scoped accounting and do not inherit worker authority.

1. Amendment findings: `NONE`.
2. Amendment waivers: `NONE`.

The amendment is consistent with the preservation-first rollback sequence and
its required post-restoration doctor record. It does not regress the exact
17-root or 12-downstream ceilings, preimage/increment model, pin/knowledge/
continuity equality, P4-C protection, reviewer-only completion artifact,
invariant-family `NOT_APPLICABLE` decision, or prohibited provider/product/
credential/install/database/deployment/commit/push and claim boundaries.

Read-only amendment guards confirmed `python scripts/check_session_state.py`
and `git diff --check` pass, the staged set is empty, and hidden Core remains
clean at `7d9f360a3df11ac998972728000785799399c02b`, exactly `0` ahead / `1`
behind frozen target `3b031fec35473e6ee6a554c4c72400e7a23b06c5`.
No network, reconciliation or other external effect occurred, and the
operator assessment was not accessed or used.

### DESIGN amendment final disposition

`AMENDMENT_PASS`.

This disposition covers only the conditional rollback-network DESIGN
amendment. It does not constitute SPEC rereview or authorize WORK_ORDER,
reconciliation or BUILD.

## Independent evidence-contract amendment review — 2026-08-23

- Reviewer role: `INDEPENDENT_DESIGN_AMENDMENT_REVIEWER`
- Reviewed section: `## Evidence-contract amendment — 2026-08-23`
- Review scope: the three provenance blockers retained by the consolidated
  authorization rereview only
- Amendment disposition: `AMENDMENT_PASS`

### Independent evaluation

1. **Reconciler checkpoint and preservation — PASS.** The amendment no longer
   asks a final filesystem receipt to prove continuous non-existence. It
   requires a raw `RECONCILER_RETURN` observation before any worker rollback
   or later project mutation, with the command-envelope invocation/time,
   canonical-Core inventory and complete inventories for every matching
   failed candidate. BUILD-start observations byte-freeze every pre-existing
   candidate, and final evidence preserves the observed prior/new states
   byte-exact. Read together with the still-accepted rollback rule that moves
   the replacement canonical Core to a contained failed-Core path, the
   preservation relation also covers the reconciler-return canonical clone
   when a later initializer/doctor failure triggers rollback. Honest absence
   is now only `NOT_OBSERVED_AT_RECONCILER_RETURN`; it is expressly not proof
   that no partial directory existed earlier. This closes the logical
   overclaim behind the candidate blocker without weakening preserve/no-delete
   safety.

2. **UUID envelope correlation — PASS.** One fresh UUID per reconciler,
   initializer, rollback-verifier or reviewer-doctor envelope joins exact
   normalized outer command/arguments, PowerShell PID, transcript, exit,
   trace paths and the trace2 `def_param`/SID/argv/start/exit/endpoint records.
   The one-to-exact-owned-prefix and cross-envelope uniqueness rules make a
   bare fetch ineligible for a doctor claim and supply the previously missing
   rollback/reviewer command surfaces. The amendment correctly names this
   deterministic cross-surface invocation correlation, not kernel-attested
   parent/child ancestry. That narrower claim is supportable with the
   authorized local surfaces; OS audit/ETW remains a separately authorized
   alternative rather than an implicit dependency.

3. **Reviewer-observed append preservation — PASS.** Each rereviewer must
   observe and freeze the pre-mutation completion hash, canonical prior-runs
   digest and exact reviewer-anchor path/type/size/hash inventory, then retain
   those observed bytes while adding exactly one new run and anchor. First
   review has an explicit absent/empty prestate. This supplies an independent
   pre/post relation instead of deriving “prior” state solely from the final
   mutable payload. The accepted claim is accurately limited to
   `REVIEWER_OBSERVED_APPEND_PRESERVATION`; it does not claim WORM storage,
   signatures, or absence of tampering before the current reviewer observed
   the state.

4. **Invariant-family applicability — PASS.** This materially changed R2
   evidence contract has shared receipt/observation shapes across success,
   ordered failures, rollback, first review and rereview; outcome-controlled
   required/forbidden/conditional fields; multiple validator consumers; and
   adjacent findings. Those are direct applicability triggers in
   `docs/cvf/INVARIANT_FAMILY_STANDARD.md`. Superseding the earlier
   `NOT_APPLICABLE` decision is required, not scope widening. The amendment
   correctly assigns the SPEC-authored registered matrix as sole semantic
   owner, requires a canonical digest, and confines later Work Order/review
   documents to references and the shared proof procedure. Exact family id,
   paths, outcome rows and digest properly remain SPEC decisions.

### Boundary and feasibility

The amendment preserves the accepted three-operation success graph,
zero-to-three failure prefix plus conditional rollback verifier, separately
owned review doctor, frozen endpoint/target/no-credential rules, exact 17-root
and 12-worker-path ceilings, ten-carrier rollback, P4-C protection,
reviewer-only completion ownership and zero provider/install/deployment/
commit/push boundary. The matrix/registry and reviewer observation/anchor
surfaces are governance evidence decided before later authorization; they do
not silently become worker product scope or current BUILD authority.

The selected architecture is feasible as a deterministic local contract. Its
later SPEC must make the checkpoint order, canonical-Core-to-failed-path
preservation relation, UUID envelope ownership, first-review/rereview
prestates and all required/forbidden/conditional fields exhaustive in the one
registered matrix. That is normal SPEC materialization of this DESIGN, not an
open DESIGN finding.

### Findings and waivers

1. Findings: `NONE`.
2. Waivers: `NONE`.

Read-only review used no network, reconciliation, provider, credential,
installation, deployment, commit or push. The operator assessment was not
opened, read, hashed, inventoried, staged, edited or used.

### Evidence-contract amendment final disposition

`AMENDMENT_PASS`.

This PASS applies only to the DESIGN evidence-contract amendment. SPEC may
proceed through the recorded phase/role transition and must register the
triggered invariant family before SPEC review. The current Work Order remains
historical reviewed input; Work Order repair, reconciliation and BUILD remain
unauthorized.
