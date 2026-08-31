# SPEC — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Phase: `SPEC`
- Risk: `R2`
- Status: `REPAIRED_FOR_INDEPENDENT_SPEC_REREVIEW`
- Accepted DESIGN:
  `docs/decisions/DESIGN_2026-08-29_CVF_CORE_REFRESH.md`
- Accepted DESIGN raw SHA-256:
  `2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443`
- Accepted DESIGN amendment:
  `docs/decisions/DESIGN_AMENDMENT_2026-08-29_CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT.md`
- Accepted DESIGN amendment raw SHA-256:
  `2f250e98914f671b19f7be3a820f2b216c277e8f8900e2f77ceaab69255a44e0`
- Invariant family: `CVF-CORE-REFRESH-OUTCOMES-2026-08-29`
- Matrix canonical digest:
  `5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`
- Active role: `SPEC_AUTHOR`

## R1 — Fixed source, old pin and target

The only permitted public remote is
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`. The old
Core/pin is `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`; the only accepted next target
is `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`. Any different remote, ancestry,
advertised tip, cloned target or post-fetch tip is a terminal stop requiring
the reviewed rollback branch. Target rebase is not implicit repair.

## R2 — Exact successful command graph

The Work Order shall freeze the exact resolved paths and arguments for only:

1. the current Core's sanctioned
   `scripts/update_cvf_workspace_public_core.ps1` with `-WorkspaceRoot` only;
2. two exact local full-pin replacements in `.cvf/manifest.json` and the
   generated `AGENTS.md` header; and
3. downstream `scripts/initialize_cvf_clone.ps1` once.

`-UpdateProjectManifests`, overlays, pending-backup override, public-profile
sync, manual pull, custom clone and a separate worker doctor are forbidden.

## R3 — Zero-effect preflight gate

Before the first external effect, verify and record:

- resolved workspace/project/Core containment and the expected public remote;
- clean old Core at R1 with local target object/ancestry as accepted;
- downstream `HEAD == origin/main == a8e2ad8199d700a238d7d74bdbf85329446228de`
  and staged zero;
- unchanged reconciler/workspace-kit surfaces and reconciler SHA-256
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`;
- active profile path/value/hash proving `operator-local`;
- fresh, collision-free contained backup/evidence destinations; and
- both canonical worker evidence paths, the conditional reviewer-movement
  rollback JSON and its terminal rereview path are absent.

Any failed predicate stops with zero network/root/Core mutation and no worker
evidence-path creation.

## R4 — Root-effect preimages and accounting

Capture existence, relative and resolved contained path, type, size, raw
SHA-256 and recoverable bytes for the exact ordered 17-target set in accepted
INTAKE/DESIGN. The active profile preimage is also frozen. Every post-state
classifies each target exactly once as `CREATE`, `UPDATE`, `DELETE` or
`NO_CHANGE`; success and rollback each account for 17/17 with no residual root
effect. No backup, failed replacement or failed-root delta may be deleted.

## R5 — Downstream preimages and categories

For all 13 tracked paths in DESIGN section 7 and ignored local binding, record
`PRESENT` plus raw preimage or explicit `ABSENT`. Categories are exactly two
pin carriers, nine shared continuity carriers and two evidence carriers.
Dedicated P4-E/governance artifacts are independently hashed and protected;
shared carriers must preserve the P4-E `DESIGN_REVIEW_PASS` semantic fields.

The protected assessment remains wholly excluded. No broad untracked
inventory or global arbitrary-untracked absence/byte-equality claim is allowed.

## R6 — Reconciler return checkpoint

Immediately after the reconciler returns and before pin mutation, record its
exit, transcript, canonical Core/backup locations, 17 root post-observations
and replacement Core state. Proceed only when the Core is clean, its remote is
R1 and `HEAD == origin/main ==` the frozen target. Any other state enters R10.

## R7 — Exact pin bridge

After R6 passes, replace exactly one old full hash with the target in each of:

- `.cvf/manifest.json.cvfCoreCommit`; and
- the generated `AGENTS.md` `CVF Commit` header.

No unrelated byte change is permitted. Zero/multiple matches, parse failure,
write failure or target drift enters R10.

## R8 — Initializer and five-way equality

Run the initializer once. Success requires exit zero, Core clean, its built-in
doctor PASS with only the bounded legacy-catalog warning, and target equality
across Core `HEAD`, Core local `origin/main`, manifest, AGENTS header and
ignored local binding. No standalone worker doctor may follow.

## R9 — Public-operation accounting

Count top-level Git operations, not HTTP requests. Worker success is exactly
the ordered three-operation graph selected by DESIGN. Failure records only its
actual ordered prefix. Each operation records owner, position, command,
endpoint, full observed target and exit; credentials/helpers/tokens and any
alternate endpoint are forbidden.

Independent successful terminal review owns one separate doctor invocation.
Any genuine rereview owns at most one separately recorded doctor invocation;
reviewer operations never satisfy worker counters.

## R10 — Preservation-first rollback

Any failure after external execution begins shall:

1. containment-check every move/restore source and destination;
2. preserve the failed replacement and raw evidence;
3. restore the old Core and verify its commit, remote and clean state;
4. restore existing root targets byte-exact and quarantine newly created root
   targets into the contained failed-delta tree;
5. restore pin/shared carriers and binding to the recorded checkpoint;
6. run at most one rollback-verifier doctor after restoration;
7. then allow only shared carriers to record failure while pins/binding and
   dedicated P4-E artifacts remain restored; and
8. retain exactly the two canonical worker evidence artifacts as the sole
   surviving absent-before-BUILD downstream creations.

Complete restoration requires exactly one recorded rollback verifier. For an
incomplete attempt, the matrix combines the rollback failure point and
verifier state into one closed `rollback_failure_verifier_pair`. Every failure
before the verifier is `:NOT_RUN`; a verifier failure may be `:NOT_RUN` or
`:ONE_RECORDED` according to the actual transcript; only a later worker-return
write failure is `WORKER_RETURN_WRITE:ONE_RECORDED`. The canonical root JSON
must already remain writable for that last token; failure to write the root
JSON cannot self-report as a matrix outcome.

The matrix separately combines every authorized original failure stage with
its permitted executed network prefix as `failure_stage_prefix_pair`; it
contains no `WORKER_DOCTOR` stage. Complete and incomplete restoration remain
distinct fail-closed states. Neither permits retry or success.

An incomplete projection must not fabricate Core/pin hashes, staged zero,
P4-E preservation or both evidence creations. It instead records the exact
blocking component plus `ABSENT`, `UNREADABLE` or
`READABLE_UNRESTORED`, and separate observation states for staged content,
P4-E and worker-return availability. Detailed per-path observations remain in
the receipt outside the terminal projection.

## R11 — Reviewer-time target movement

If the independent reviewer doctor observes target movement, the reviewer
creates only the immutable completion review with disposition
`REVIEW_TARGET_MOVEMENT` and performs no repair. The original successful root
receipt and worker return remain immutable. The Work Order may preauthorize
only a distinct `REPAIR_WORKER` to execute R10 rollback from frozen BUILD
preimages, with no new reconciliation attempt, and create exactly:

`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-29.json`.

That JSON begins `ABSENT`, is the sole semantic owner of outcome
`REVIEW_TARGET_MOVEMENT_ROLLED_BACK` or
`REVIEW_TARGET_MOVEMENT_ROLLBACK_INCOMPLETE`, and never self-hashes. A fresh
independent rereviewer alone may then create the initially absent
`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-29.md`
and record final hashes for the four earlier artifacts. Any target rebase then
requires fresh operator authority and reviewed phase amendments.

The conditional incomplete outcome uses the same closed rollback/verifier
pair rule. Its sole post-verifier write-stage token is
`SHARED_FAILURE_CONTINUITY_WRITE:ONE_RECORDED`: it means a shared-carrier
failure-continuity write failed while the separate conditional JSON remained
writable. Failure to create that JSON is not an `EVIDENCE_WRITE` outcome and
must never be described by the absent record itself.

## R12 — Exact path and ownership ceilings

The initial worker ceiling is exactly the 13 tracked paths in DESIGN section 7
plus ignored `.cvf/local-binding.json`. The independent terminal reviewer alone
may create
`docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md`.

Only after that review records target movement, the repair worker may touch the
intentional temporal intersection of two pins, nine shared carriers and the
binding for restoration/failure continuity, plus create its one conditional
rollback JSON: at most 12 tracked paths and one ignored local effect. It may
not update the two worker artifacts or completion review. The terminal
rereviewer alone owns its one separate Markdown `CREATE` path.

After review PASS, a declared `CLOSER/SESSION_SYNC_STEWARD` may update only the
same shared continuity carriers to return to parked P4-E. No role may silently
open P4-E SPEC. Every other tracked path is byte-protected.

## R13 — Canonical invariant family

The sole per-outcome receipt owner is
`docs/cvf/invariants/cvf-core-refresh-outcomes-2026-08-29.json`, family
`CVF-CORE-REFRESH-OUTCOMES-2026-08-29`, canonical digest
`5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`.
The machine pin is
`docs/specs/cvf_core_refresh_2026_08_29_invariant_pin.py`.

The matrix validates exactly five outcomes across the closed
`terminalInvariantProjection` embedded in the initial root-effects receipt or
conditional rollback JSON and independently reconstructed by terminal review.
It is not the schema for unrelated receipt detail such as the 17 root-entry
array. Both old pin and target are exact constants, not generic hash patterns.

The legacy active family `CVF-CORE-REFRESH-EVIDENCE-CONTRACT` remains unchanged
historical evidence for the 2026-08-23 contract; it is not an operative semantic
owner for this tranche. Work Order/reviews reference, but never restate, the new
matrix's field/outcome rules.

## R14 — Conformance evidence

Before BUILD return, a matrix-digest-pinned deterministic adapter defined
exactly by the Work Order shall emit one disposable positive per matrix outcome
under the contained evidence directory. The generic invariant contract and an
independent validator must accept each intended positive exclusively and
reject the complete generated one-fact mutation corpus. The worker returns the
conformance summary; the reviewer recomputes digest/corpus, samples one raw
positive per outcome and verifies the adapter did not derive expectations from
the worker output.

Focused negatives must include an internally equal but wrong target, a wrong
old pin, every invalid stage/prefix token, every invalid rollback-stage/
verifier-state cross-product, fabricated hashes/success-only fields in
incomplete outcomes, changed hashes
for each immutable prior artifact, wrong conditional path/effect and any
attempt to add a rollback-record self-hash.

Required repository guards include:

- `python scripts/check_invariant_families.py --json`;
- focused invariant unit/integration tests named by the matrix; and
- canonical pin recomputation.

## R15 — Evidence ownership and self-hash prohibition

The root-effects JSON is the sole initial-worker semantic receipt; the Markdown
worker return is only a summary. Both begin absent and may survive as `CREATE`
on every readable initial-worker terminal path. Neither contains its own final
raw hash or requires the other's final hash. An incomplete outcome records an
unavailable/unreadable worker return honestly rather than fabricating both
creations. The independent terminal review records every readable worker-
artifact hash and does not self-hash.

For reviewer-time movement, both worker artifacts and the completion review
are immutable. Complete conditional rollback proves their pre/post hashes
equal; incomplete rollback records per-artifact observation states without
inventing hashes. The conditional rollback JSON is `CREATE` only and cannot
contain its own final hash. Its later rereview owns final hashes and does not
self-hash or require a future fact inside the repair projection.

## R16 — Final deterministic gates

Worker and reviewer run the applicable JSON, session/mirror, Project Knowledge,
invariant-family, catalog, file-size, repository and scoped diff guards. Staged
set is zero. Completion review independently verifies command/output surfaces,
17-root and 13-path ceilings, pin/target state, P4-E preservation and all
prohibited effects.

## R17 — Claim and effect boundary

The tranche may prove only deterministic public-Core pin/freshness
reconciliation. It does not adopt Core runtime into the product, prove CVF
control of AI/agents, provider behavior, continuous observation, OS process
ancestry, WORM history, arbitrary-untracked absence, deployment or production
readiness. Provider calls, secrets, credentials, package installation,
product/database changes, deployment, release, commit and push are forbidden.

## Acceptance criteria

- `AC1`: R1-R5 pass before any external effect.
- `AC2`: successful worker evidence proves R6-R9 and the matrix-selected
  success shape without claiming tranche closure.
- `AC3`: every post-start failure satisfies the matrix-selected failure shape
  and R10; reviewer-time movement selects one of its two distinct R11 shapes.
- `AC4`: exact R12 ownership/path ceilings and P4-E parking hold.
- `AC5`: R13-R15 invariant digest, conformance and non-circular hash ownership
  pass with no duplicated semantic owner.
- `AC6`: independent review recomputes R16 and records findings/waivers.
- `AC7`: R17 remains true for every outcome.

## Next governed move

Fresh independent SPEC rereview only. Work Order, reconciliation,
network/root effects, P4-E SPEC, commit and push remain unauthorized.
