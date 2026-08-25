# Independent SPEC Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Reviewed phase: `SPEC` only
- Reviewer role: `INDEPENDENT_SPEC_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

The review compared
`docs/specs/CVF_CORE_REFRESH_2026-08-23_SPEC.md` with the accepted INTAKE and
final INTAKE review, accepted DESIGN and final DESIGN rereview, canonical
continuity, the parked P4-C state, current downstream/Core Git state, and the
actual reconciler, wrapper installer, initializer and doctor command graph.

Read-only verification confirmed downstream `HEAD == origin/main ==
0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, an empty staged set, and a clean
hidden Core at `7d9f360a3df11ac998972728000785799399c02b`, exactly `0` ahead / `1`
behind the already-fetched frozen target
`3b031fec35473e6ee6a554c4c72400e7a23b06c5`. The reconciler performs the
declared clone; the initializer performs a fetch and invokes the doctor; the
doctor performs its own fetch. `python scripts/check_session_state.py` and
`git diff --check` passed. No network, reconciliation or other external effect
was performed, and the operator assessment was not accessed or used.

## Numbered findings

1. **CORE-REFRESH-SPEC-REV-F1 — The failure acceptance branch drops mandatory
   safety and scope requirements.** `AC-05` permits a failure disposition when
   only `R15` is satisfied, whereas `R15` describes restoration mechanics but
   does not retain the assessment prohibition, endpoint/credential boundary,
   staged-zero requirement, P4-C protection, evidence ownership, or the
   provider/product/install/database/deployment/commit/push prohibitions from
   `R2`, `R4`, `R8`, `R11`, `R12`, `R14` and `R16`. It could therefore accept
   a rollback receipt after an otherwise unauthorized effect. The success
   branch also ends at `R16`, leaving `R17` outside the stated success
   acceptance. Repair `AC-05` so both success and failure retain every
   always-applicable safety, ownership, evidence and no-effect requirement,
   with `R15` added for failure, and include `R17` in the applicable accepted
   set.

2. **CORE-REFRESH-SPEC-REV-F2 — Network counting is not defined for failure
   and rollback.** `R4` says BUILD performs exactly three operations, which is
   impossible after an early clone/fetch failure, while `R15` always requires
   a post-rollback doctor state. The actual doctor performs a public Git fetch;
   after a failure occurring after the third worker operation, that doctor is
   a fourth BUILD/rollback network operation unless it is separately bounded.
   The accepted DESIGN ceiling is exactly three worker-owned operations and
   requires rollback/stop on movement, so the SPEC must distinguish the
   success count from an early-failure prefix and explicitly define whether
   post-rollback evidence is an offline state capture or a separately
   authorized, owner-scoped doctor fetch. It must never silently exceed or
   reuse the three-operation BUILD authority.

3. **CORE-REFRESH-SPEC-REV-F3 — The required-command contract cannot reproduce
   the quantitative acceptance claims.** The command list omits the selected
   reconciler invocation and the independent-review doctor invocation, and it
   contains no exact commands/parsers for full local/remote commit equality,
   remote URL, the three-operation owner/count record, 17-root inventory and
   hashes, 12-path incremental comparison, four-way pin/binding equality,
   staged-zero evidence, or root-effects JSON validation. Nevertheless `R13`
   requires an unidentified "JSON guard", `AC-03` says `R9-R13` all "exit
   zero" even though those requirements are not executable commands, and the
   final paragraph defers the missing proof commands to a future Work Order.
   A Work Order may bind exact paths and owners, but it cannot invent the SPEC
   acceptance oracle. Add deterministic commands or named validators with
   explicit expected results for each claim, including the exact reviewer-only
   completion artifact path and worker evidence paths inherited from DESIGN.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted SPEC boundaries

Subject only to F1-F3, R1-R17 preserve the accepted maintenance boundary:
frozen public target and exact remote, full pin/header/binding equality, exact
17-root and 12-downstream ceilings, protected dirty P4-C coexistence, bounded
knowledge-pin and continuity updates, reviewer-owned completion review,
preservation-first rollback, and no product/provider/credential/install/
database/deployment/commit/push or AI-governance claim.

Invariant-family applicability remains validly `NOT_APPLICABLE`. This tranche
does not introduce or materially change a runtime shared receipt/model,
outcome-controlled field set, counter relation, multi-validator contract,
coupled prompt/schema artifact, or adjacent runtime invariant family.

## Disposition

`SPEC_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-SPEC-REV-F1..F3` for one bounded SPEC repair and
independent rereview. WORK_ORDER, reconciliation and BUILD remain
unauthorized.

## Bounded rereview — CORE-REFRESH-SPEC-REV-F1..F3

- Prerequisite DESIGN amendment: `AMENDMENT_PASS`
- Rereview role: `INDEPENDENT_SPEC_REVIEWER`
- Rereview scope: repaired F1-F3 only
- Rereview disposition: `SPEC_REVIEW_CHANGES_REQUIRED`

1. **CORE-REFRESH-SPEC-REV-F1 — RESIDUAL
   `CORE-REFRESH-SPEC-REV-F1-R1`.** `AC-05` now includes `R17` on success and
   names several always-applicable requirements on failure, but its failure
   set still omits `R1`, `R3`, `R7`, `R9` and `R10`. Those are not
   success-only outcomes: BUILD-start base/staged/Core preconditions, exact
   reconciler flags, root/profile/sibling boundaries, knowledge classification/
   ownership/policy restrictions, and implementation/module/catalog/roadmap/
   product-status restrictions must remain true even when rollback is needed.
   `R12` evidence and `R15` restoration do not authorize a transient or
   untested violation, and cannot substitute for explicitly accepting those
   requirements. Add `R1`, `R3`, `R7`, `R9` and `R10` to the failure branch's
   always-applicable set. `R6` and `R13` may remain success-only because a
   restored prior Core intentionally cannot satisfy refreshed-target equality
   or the success doctor gate.
2. **CORE-REFRESH-SPEC-REV-F2 — CLOSED.** `R4` now defines exactly the ordered
   three-operation success path and records only the executed zero-to-three
   prefix on early failure. `R15`, backed by the independently accepted DESIGN
   amendment, grants exactly one separately identified conditional
   `ROLLBACK_VERIFIER` doctor fetch after restoration, caps worker/rollback use
   at four, preserves URL/no-credential/frozen-target rules, and forbids use
   of rollback verification as success evidence.
3. **CORE-REFRESH-SPEC-REV-F3 — CLOSED.** The required command set now names
   the reconciler, initializer and independent doctor commands. The normative
   `PIN_EQUALITY_PROBE`, `ROOT_EFFECTS_PROBE`, `INCREMENTAL_SCOPE_PROBE`,
   `JSON_PARSE_PROBE` and `REVIEW_OWNERSHIP_PROBE` define deterministic inputs,
   predicates and expected exit semantics for full pin equality, exact
   17-root/12-increment inventories, operation ownership/count, JSON parsing,
   staged zero, assessment exclusion, protected P4-C hashes, exact worker
   evidence paths and reviewer-only completion artifact ownership. Exact
   inline bodies and frozen arrays may be bound without changing those
   predicates in the Work Order.

### Rereview waivers

1. `NONE`. No finding is waived or deferred.

No unrelated boundary regressed. The exact target/remote, pin/knowledge/
continuity model, preservation-first rollback, P4-C protection, invariant
family `NOT_APPLICABLE` decision and prohibited external-effect/claim boundary
remain intact.

Read-only rereview confirmed downstream `HEAD == origin/main ==
0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, an empty staged set, and clean
hidden Core `7d9f360a3df11ac998972728000785799399c02b` exactly `0` ahead / `1`
behind frozen fetched target
`3b031fec35473e6ee6a554c4c72400e7a23b06c5`. Session-state and
`git diff --check` guards pass. No network, reconciliation or other external
effect occurred, and the operator assessment was not accessed or used.

## Final disposition after bounded rereview

`SPEC_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-SPEC-REV-F1-R1` for bounded repair and independent
rereview. F2 and F3 are closed without waiver. WORK_ORDER, reconciliation and
BUILD remain unauthorized.

## Final bounded rereview — CORE-REFRESH-SPEC-REV-F1-R1

- Rereview role: `INDEPENDENT_SPEC_REVIEWER`
- Rereview scope: residual F1-R1 only
- Findings: `NONE`
- Waivers: `NONE`

1. **CORE-REFRESH-SPEC-REV-F1-R1 — CLOSED.** `AC-05` now explicitly retains
   all always-applicable `R1-R5`, `R7-R12` and `R14-R17` requirements on the
   failure branch, including the complete `R15` rollback. This preserves
   BUILD-start preconditions, exact reconciler flags, network/target rules,
   root/profile/sibling restrictions, incremental and P4-C protection,
   knowledge/status restrictions, continuity, evidence and independent-review
   ownership, prohibited-effect/claim rules and invariant-family disposition.
   Only `R6` refreshed-target equality and `R13` success gates are correctly
   success-only after restoration of the prior Core.

The repaired branch is consistent with the accepted DESIGN amendment: success
still requires exactly three ordered worker operations; failure records only
the executed zero-to-three prefix plus exactly one conditional
`ROLLBACK_VERIFIER` doctor fetch, with total worker/rollback use at most four.
No earlier F2/F3 closure or other accepted boundary regressed.

Read-only final rereview confirmed downstream `HEAD == origin/main ==
0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, an empty staged set, and clean
hidden Core `7d9f360a3df11ac998972728000785799399c02b` exactly `0` ahead / `1`
behind frozen fetched target
`3b031fec35473e6ee6a554c4c72400e7a23b06c5`. Session-state and
`git diff --check` guards pass. No network, reconciliation or other external
effect occurred, and the operator assessment was not accessed or used.

## Final SPEC disposition

`SPEC_REVIEW_PASS`.

The earlier `SPEC_REVIEW_CHANGES_REQUIRED` dispositions remain as historical
evidence and are superseded for this SPEC revision. F1-F3 and F1-R1 are closed
without waiver. WORK_ORDER may proceed only through an explicit role/phase
transition; reconciliation and BUILD remain unauthorized.

## Independent evidence-contract SPEC amendment review — 2026-08-23

- Reviewer role: `INDEPENDENT_SPEC_AMENDMENT_REVIEWER`
- Reviewed scope: the evidence-contract SPEC amendment, registered matrix,
  registry entry and canonical pin only
- Amendment disposition: `SPEC_AMENDMENT_CHANGES_REQUIRED`

### Recomputed evidence

- DESIGN canonical SHA-256:
  `b15ee41c0ee7d57609bc65a2c5bcbbeb116cb88c9a8a3b55df2191dab7ca5f67`;
- matrix canonical SHA-256:
  `b7c6fae25546fed3d809ded53c8fe0c582cf0d188619044c7f4f856887ba6c39`;
- amended SPEC canonical SHA-256:
  `def92a5dc7909bfc2d76ae123c0e40421337c2f3ce46cf1112d3ab0bbbaa23c2`.

The DESIGN and matrix digests match the SPEC declarations, matrix contract
source and Python pin. Registry identity/path/role/risk/lifecycle are
consistent. The repository invariant guard passes. Independent in-memory
shape probes accepted one mechanically valid positive for each of all seven
declared outcomes and rejected all generated mutations: 35 for `SUCCESS`, 37
for each `FAILURE_PREFIX_0..3`, 38 for `FIRST_REVIEW`, and 39 for
`REREVIEW_APPEND`. The focused invariant tests pass `35 passed, 2 skipped`.

### Numbered findings

1. **CORE-REFRESH-SPEC-AMEND-REV-F1 — The matrix is not yet the sole semantic
   owner of the amended contract.** The SPEC correctly says that later
   validators must consume the matrix rather than copied rules, but essential
   accepted semantics exist only in `AR1..AR9`/`AAC-01..04`, not in the seven
   matrix shapes. In particular:

   - candidate preservation is represented only by three opaque digest fields
     plus receipt-supplied `candidate_preservation_confirmed=true`; no matrix
     relation binds the AR1 observation to final prior/new candidate equality
     or binds a displaced canonical-Core inventory to its failed-Core result;
   - `NOT_OBSERVED_AT_RECONCILER_RETURN` and its prohibition on continuous-
     absence inference have no owned matrix field/domain;
   - the exact envelope owner/UUID/PID/normalized command/window, one-to-owned-
     prefix mapping, UUID/SID/fingerprint disjointness and exact doctor-vs-bare-
     fetch rule are compressed into an unconstrained digest plus a correlation
     claim, with no matrix fields or relations that validators can consume;
   - review outcomes use `correlation_claim=DETERMINISTIC_CROSS_SURFACE` but do
     not own the distinct accepted claim
     `REVIEWER_OBSERVED_APPEND_PRESERVATION`; their prestate hashes and
     `prior_preserved=true` have no digest/pre-post/one-new-anchor relation.

   Consequently a root-effects or independent-review validator must copy or
   reinterpret the SPEC prose to enforce the three blockers, contrary to the
   standard's “matrix is sole semantic source” rule. The passing generic guard
   proves the declared reduced shapes, not the missing DESIGN relations. Move
   every required fact/domain/relation into the matrix (using nested shapes and
   digest/field relations where appropriate), keep SPEC to applicability,
   matrix id/digest, acceptance routing and claim boundary, then regenerate
   the pin/digests and rerun the full two-surface corpus.

2. **CORE-REFRESH-SPEC-AMEND-REV-F2 — `FAILURE_PREFIX_0` is feasible for one
   subcase but is not exhaustive under the unchanged post-start failure
   boundary.** A zero-operation prefix can validly have
   `RECONCILER_RETURN` when the exact reconciler outer command was invoked and
   exited before emitting a clone span, so the declared shape has an honest
   witness. But existing R15 covers *any* post-start failure, and BUILD-start
   evidence/preimage/containment work occurs before the reconciler invocation.
   A failure after BUILD start but before that command is launched has zero Git
   operations and no reconciler envelope or `RECONCILER_RETURN`; it cannot
   satisfy the matrix's only zero-prefix terminal shape, which requires both
   digests. The family therefore does not yet exhaust the accepted failure
   space. Either define the governed start boundary at successful entry into
   the reconciler envelope without weakening preflight/rollback safety, or add
   a distinct pre-reconciler abort shape with reconciler-return/envelope fields
   forbidden and the applicable preservation/stop evidence required.

### Waivers and accepted boundaries

1. Waivers: `NONE`.

The family registration, seven declared discriminator values, canonical
digest binding, two representation-surface declaration, zero mutation
exclusions, narrowed observation/correlation/append claims, frozen target,
17-root/12-path/ten-carrier ceilings and prohibited external-effect boundary
are accepted subject only to F1-F2. These findings do not revive any prior
closed SPEC issue or authorize a Work Order edit.

Local guards passed: session state, invariant-family JSON guard, file-size,
focused invariant tests and `git diff --check`; staged set is empty. No
network, reconciliation, provider, credential, installation, deployment,
commit or push occurred. The operator assessment was not opened, read, hashed,
inventoried, staged, edited or used.

### Evidence-contract SPEC amendment final disposition

`SPEC_AMENDMENT_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-SPEC-AMEND-REV-F1` and
`CORE-REFRESH-SPEC-AMEND-REV-F2` for bounded SPEC/matrix/pin repair and
independent rereview. Work Order repair, reconciliation and BUILD remain
unauthorized.

## Bounded evidence-contract SPEC amendment rereview — F1/F2

- Reviewer role: `INDEPENDENT_SPEC_AMENDMENT_REVIEWER`
- Scope: repaired F1-F2 only
- Rereview disposition: `SPEC_AMENDMENT_CHANGES_REQUIRED`

### Recomputed evidence and accepted repairs

- DESIGN canonical SHA-256:
  `b15ee41c0ee7d57609bc65a2c5bcbbeb116cb88c9a8a3b55df2191dab7ca5f67`;
- repaired matrix canonical SHA-256:
  `eecab315cc0f17c7a71ea9979b6f24d4e3ae0e778c1b3344c8fcf54e4f8e7620`;
- repaired SPEC canonical SHA-256:
  `d83546a63b6d0871ed1ac84bafce525bbeed8ce3ad2062bd1c30c09ce98e8c5a`.

The matrix digest matches the SPEC declaration, Python pin and registered
family path. The repair adds the eighth `PRE_RECONCILER_STOP` outcome and
makes it mechanically feasible: it has zero worker-network prefix, forbids
reconciler checkpoint/Core/build-envelope fields, preserves BUILD-start prior
candidates, requires exactly one separately enveloped rollback verifier,
forbids direct-fetch substitution and remains stopped. `FAILURE_PREFIX_0` is
now distinct and feasible for the exact subcase where the reconciler envelope
was invoked and returned a `RECONCILER_RETURN` observation after no governed
network operation completed.

Candidate build/final and checkpoint/final equality, UUID correlation,
zero-direct-fetch, exact doctor/outer-command identities, first-review empty
prestate and rereview completion/runs/anchor preservation now live in the
matrix as fields, domains and supported equality/digest/count relations. The
SPEC confines itself to architecture, raw derivation, routing and claim
boundaries. `prefix_mapping`, `window_relation`, `identity_relation`, command
contract and direct-fetch count are explicitly validator-recomputed enum/
counter facts; they are not mislabeled as schema-native relation kinds. This
is an honest use of the current schema's limited native
`FIELD_EQUALITY`/`DIGEST_EQUALITY`/`COUNTER_EQUALITY` vocabulary.

Independent positives matched both declared validator-surface functions for
all eight shapes. Matrix-generated mutation results were:
`PRE_RECONCILER_STOP 74/74`, `SUCCESS 92/92`, each
`FAILURE_PREFIX_0..3 99/99`, `FIRST_REVIEW 98/98`, and
`REREVIEW_APPEND 105/105` rejected.

### Residual findings

1. **CORE-REFRESH-SPEC-AMEND-REV-F1 — RESIDUAL
   `CORE-REFRESH-SPEC-AMEND-REV-F1-R1`: checkpoint-Core byte equality is not
   feasible across the authorized post-checkpoint Git operations.** Every
   `SUCCESS` and `FAILURE_PREFIX_0..3` shape requires
   `checkpoint_core == final_checkpoint_core`. The checkpoint is the complete
   canonical-Core inventory immediately after reconciler return. Success then
   necessarily runs initializer fetch and initializer-doctor fetch; later
   failure prefixes may run either before rollback. Those authorized Git
   operations can create or rewrite administrative files such as
   `.git/FETCH_HEAD` even while HEAD, tracked tree, remote and target remain
   correct. On rollback, the displaced failed-Core therefore preserves the
   post-fetch replacement, not necessarily a byte-identical copy of the AR1
   inventory. The current equality can reject an honest SUCCESS or later
   failure, or force deletion/rewriting of valid post-checkpoint evidence to
   manufacture equality. Keep the immutable AR1 observation artifact
   hash-bound, but define a feasible live-Core preservation relation: bind
   tracked tree/target and an explicit allowed administrative delta, or retain
   separate AR1 and final inventories without asserting full equality.

2. **CORE-REFRESH-SPEC-AMEND-REV-F1 — RESIDUAL
   `CORE-REFRESH-SPEC-AMEND-REV-F1-R2`: `FAILURE_PREFIX_1` omits an honest
   command-envelope variant.** One completed clone followed by a reconciler
   failure is correctly represented by
   `outer_command_contract=RECONCILER_EXACT`. But the reconciler may return
   successfully, then the exact initializer may be invoked and fail before
   its fetch emits a governed network operation. That outcome still has
   `network_prefix_count=1`, but it owns both reconciler and initializer
   envelopes and cannot match the only `FAILURE_PREFIX_1` shape. Add a second
   shape under the same outcome (or an equivalent matrix-owned discriminator)
   for the invoked-initializer/no-initializer-fetch subcase, retaining the
   same preservation, rollback, stop and zero-direct-fetch requirements.

### Finding closure and waivers

1. `CORE-REFRESH-SPEC-AMEND-REV-F2`: **CLOSED** for the pre-reconciler versus
   invoked-reconciler zero-prefix distinction.
2. `CORE-REFRESH-SPEC-AMEND-REV-F1`: remains open only as residuals F1-R1 and
   F1-R2 above.
3. Waivers: `NONE`.

Local session, invariant-family, file-size and `git diff --check` guards pass;
focused invariant tests pass `35 passed, 2 skipped`; staged set is empty. No
network, reconciliation, provider, credential, installation, deployment,
commit or push occurred. The operator assessment was not opened, read, hashed,
inventoried, staged, edited or used.

### Final disposition after bounded amendment rereview

`SPEC_AMENDMENT_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-SPEC-AMEND-REV-F1-R1` and
`CORE-REFRESH-SPEC-AMEND-REV-F1-R2` for bounded matrix/SPEC/pin repair and
independent rereview. Work Order repair, reconciliation and BUILD remain
unauthorized.

## Bounded evidence-contract SPEC amendment rereview — F1-R1/F1-R2, repair round 2

- Reviewer role: `INDEPENDENT_SPEC_AMENDMENT_REVIEWER`
- Scope: residuals `CORE-REFRESH-SPEC-AMEND-REV-F1-R1` and
  `CORE-REFRESH-SPEC-AMEND-REV-F1-R2` only
- Rereview disposition: `SPEC_AMENDMENT_PASS`

### Independent evidence

- DESIGN canonical SHA-256:
  `b15ee41c0ee7d57609bc65a2c5bcbbeb116cb88c9a8a3b55df2191dab7ca5f67`;
- matrix canonical SHA-256:
  `b62eae333a65a6770727abed9348828ac1ca61805f5fc8c48c5fd0e41053228e`;
- repaired SPEC canonical SHA-256:
  `19f7e4cd805aecc6423b17513d10bb3bffe2bb5fc13a25f5eba59c921c8f6bda`.

The recomputed matrix digest equals the SPEC declaration and Python pin, and
the registered family still resolves to the same matrix path. The matrix
`boundedClaim` now defines `checkpoint_core`/`final_checkpoint_core` equality
as equality of canonical tracked target, tracked tree and worktree state plus
an allowed Git-administrative-delta classification. It explicitly excludes
full `.git` byte equality and applies the same tracked scope to a displaced
replacement. Therefore authorized fetch metadata changes do not falsify the
claim, while tracked target/tree/worktree drift remains detectable for both
SUCCESS preservation and failure rollback. This closes F1-R1 without widening
the claim to continuous filesystem or complete Git-administration equality.

`FAILURE_PREFIX_1_VALID.outer_command_contract` now admits exactly
`RECONCILER_EXACT` and
`RECONCILER_EXACT+INITIALIZER_EXACT_BEFORE_FETCH`, while
`network_prefix_count` remains exactly one. Independently constructed honest
positives for both variants each matched exactly this one shape. For each
positive, all `99/99` matrix-generated mutations were rejected; explicit
prefix-count and unsupported-command-contract mutations were also rejected.
This closes F1-R2 while preserving the single completed governed Git-operation
prefix.

Local deterministic checks passed: session state, invariant-family repository
guard, file-size guard and `git diff --check`; focused invariant tests passed
`35 passed, 2 skipped`; staged set is empty. No network, reconciliation,
provider, credential, installation, deployment, commit or push occurred. The
operator assessment was not opened, read, hashed, inventoried, staged, edited
or used.

### Finding closure and waivers

1. `CORE-REFRESH-SPEC-AMEND-REV-F1-R1`: **CLOSED**.
2. `CORE-REFRESH-SPEC-AMEND-REV-F1-R2`: **CLOSED**.
3. Findings: `NONE`.
4. Waivers: `NONE`.

### Final disposition after repair round 2

`SPEC_AMENDMENT_PASS`.

This disposition accepts only the bounded evidence-contract SPEC amendment.
The current Work Order is not repaired or authorized by this review;
reconciliation, network activity and BUILD remain unauthorized.
