# Independent SPEC Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Review date: `2026-08-29`
- Role: `INDEPENDENT_SPEC_REVIEWER`
- Risk: `R2`
- Reviewed SPEC raw SHA-256:
  `286e7a467d3368ba47681ba9bc34fd1070a0242c7f7cc71649f37545291b05f6`
- Reviewed matrix raw/canonical SHA-256:
  `d79286a0d89b51987ac0f86dc81dcf6b4290ab3eb3c4482a9032b882571a4037`
- Registry raw SHA-256:
  `ec2ff31d7a72154b7a2f21c189e9164e455360228f44591b1a45842babf971d5`
- Machine pin raw SHA-256:
  `92001ddca75afd4e49481d6265cae5d4649b7d8dfac5da93830a20e4a0b2cb66`
- Accepted DESIGN raw SHA-256:
  `2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`

## Review boundary

This review used only allowlisted local reads and deterministic checks. Its
sole mutation is this reviewer-owned receipt. It performed no network or
doctor call, reconciler/initializer execution, hidden-Core/workspace-root/
product/continuity mutation, provider call, credential use, installation,
database action, deployment, commit or push. It did not touch, hash or
inventory the protected operator assessment and did not perform broad
untracked inventory.

## Independently verified requirements

1. R1-R12 preserve the frozen remote, old pin and target, the sanctioned
   two-script command graph, zero-effect preflight, ordered 17-root accounting,
   categorized 13-path worker ceiling, pin sequencing, five-way success
   equality, preservation-first rollback, P4-E parking and narrow role/path
   ownership.
2. R13-R17 correctly trigger a new R2 invariant family, separate the root-
   effects JSON semantic owner from its Markdown summary, assign final worker-
   artifact hashes to independent terminal review without a self/cross-hash
   cycle, and retain a bounded non-provider claim.
3. The registry entry is unique and points to the reviewed matrix. The matrix
   has exactly one shape for each of its three outcomes, a closed top-level
   projection, safe ownership binding and a digest pin whose independently
   recomputed canonical value is `d79286a...`.
4. The pre-existing `CVF-CORE-REFRESH-EVIDENCE-CONTRACT` remains byte-
   independent and scoped to the 2026-08-23 checkpoint/command-correlation and
   review-append contract. The new family is scoped to the 2026-08-29 terminal
   projection. No operative ownership binding crosses the two families, so no
   semantic-owner collision was found.
5. Generic conformance is mechanically feasible: generated valid projections
   for all three shapes were accepted, and all `97`, `103` and `87` generated
   one-fact mutations respectively were rejected. This mechanical result does
   not cure the semantic gaps below.

## Numbered findings

1. **`CORE-REFRESH-SPEC-REV-F1` — the matrix does not bind the tranche's fixed
   old pin and target.** R1 fixes both full commits, but every matrix shape
   constrains `target` and `old_pin` only as arbitrary 40-character lowercase
   hexadecimal strings. The success relations therefore prove only internal
   equality to an arbitrary hash. An independent probe replaced the target and
   all five success pin/head fields with `1111...1111`; the generic matrix
   matcher still returned `True`. This breaks parity with a conforming
   independent validator, which must reject any target other than R1.

   Repair the sole semantic matrix so both tranche refs are exact constants,
   then recompute its canonical digest and update every pin/consumer. Add a
   focused negative proving an internally equal but wrong target and a wrong
   old pin are rejected.

2. **`CORE-REFRESH-SPEC-REV-F2` — the incomplete-rollback shape cannot
   represent every R10 incomplete state truthfully.** R10 assigns
   `FAILURE_ROLLBACK_INCOMPLETE` when any containment, restore or hash check
   fails. That includes a canonical Core or pin carrier that is absent,
   unreadable or not a Git object after a failed restore. The matrix nevertheless
   requires `core_head`, `manifest_pin`, `agents_pin` and `binding_pin` to be
   present 40-character hashes, and also unconditionally asserts the P4-E
   checkpoint, staged-zero and both evidence creations. A probe replacing the
   incomplete projection's Core value with the truthful sentinel `ABSENT` was
   rejected. A worker would therefore have to fabricate a hash or fail to emit
   the only allowed terminal shape precisely in the fail-closed case.

   Model observed state explicitly and make success-only restoration facts
   conditional/forbidden when they cannot be established. The repair must
   cover at least absent, unreadable and readable-but-unrestored Core/pin states
   without weakening the narrow claim or inventing success.

3. **`CORE-REFRESH-SPEC-REV-F3` — failure doctor/stage semantics contradict
   the prose command contract.** R10 permits *at most* one rollback verifier,
   while the `FAILURE_ROLLED_BACK` matrix shape requires exactly one and requires
   its recorded flag to be true. Separately, the failure-stage domain admits
   `WORKER_DOCTOR`, although R2 and R8 explicitly forbid a separate worker
   doctor and assign the only successful-path doctor to the initializer. The
   current contract can reject a prose-valid zero-verifier complete rollback
   and accept a forbidden command stage.

   Choose and state one exact complete-rollback verifier rule in SPEC and
   matrix, and use stage identities that map one-to-one to the authorized
   command graph. Add cross-surface positives/negatives for every permitted
   stage/count pair.

4. **`CORE-REFRESH-SPEC-REV-F4` — reviewer-time target movement has no
   executable evidence-carrier lifecycle.** R11 preauthorizes a distinct
   `REPAIR_WORKER` to roll back after a previously successful worker return.
   At that point both canonical evidence carriers already exist with `SUCCESS`.
   Accepted DESIGN section 8 forbids overwriting them and requires a reviewed
   attempt-path change for a later attempt; SPEC R15 simultaneously says both
   carriers begin absent and survive as `CREATE` for every worker terminal
   path. The matrix admits `REVIEW_TARGET_MOVEMENT` only in failure shapes, but
   no authorized path can create or update the canonical failure projection
   without violating one of those rules.

   This crosses the accepted DESIGN evidence-lifecycle boundary. Return to a
   bounded DESIGN amendment (then re-pin/review SPEC) that declares immutable
   success evidence plus a separately owned rollback record, or another
   non-overwriting lifecycle with exact path, owner, pre-state and hash rules.
   Do not silently reinterpret `CREATE` as `UPDATE`.

## Waivers

`NONE`.

## Deterministic checks

- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family repository guard: `PASS` with no diagnostics.
- Focused invariant unit/integration tests: `35 passed, 2 skipped`.
- Generated matrix positives/mutations: `3/3` positives accepted; all
  `287/287` generated one-fact mutations rejected.
- Catalog drift guard: `PASS` (`26` modules).
- File-size guard: `PASS`.
- Scoped diff check before review receipt: `PASS`.
- Scoped staged set: empty.

## Final disposition

`SPEC_REVIEW_CHANGES_REQUIRED` — findings F1-F4 open; waivers `NONE`.

F4 requires a bounded DESIGN amendment and independent DESIGN amendment review.
F1-F3 then require matrix/SPEC/pin repair and fresh independent SPEC rereview.
WORK_ORDER, reconciliation/network/root effects, P4-E SPEC, commit and push
remain unauthorized.

---

## Independent SPEC rereview — 2026-08-29

- Role: `INDEPENDENT_SPEC_REREVIEWER`
- Recomputed repaired SPEC raw SHA-256:
  `06fccd5de41ac03ea42b5e3d83138f1c114f87100faf41de9dd9d8c977169ccb`
- Recomputed matrix raw/canonical SHA-256:
  `ab6546e0c654ed093348341285bdc399f47c86d11ab611d5aa17c7ce6d459c90`
- Recomputed registry raw SHA-256:
  `ec2ff31d7a72154b7a2f21c189e9164e455360228f44591b1a45842babf971d5`
- Recomputed machine-pin raw SHA-256:
  `0ff61a598578b340ef314b7287802fc34590cab8582b48470c1f12c21255050a`
- Accepted DESIGN amendment raw SHA-256:
  `2f250e98914f671b19f7be3a820f2b216c277e8f8900e2f77ceaab69255a44e0`
- DESIGN amendment review artifact raw SHA-256:
  `c1056479cd53abc2ccbe3209a8304fc33976d258685f28919f9b267f249a7aff`
- Prior review artifact pre-append raw SHA-256:
  `e642644480972f8ebdbfc82eb33c01f5efa4d886eb5ac1c47e9f1b97bdf609d9`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`

### Rereview boundary

This fresh rereview rehydrated current canonical continuity and inspected only
allowlisted local artifacts. Its sole mutation is this appended reviewer-owned
section. It performed no network or doctor call, reconciler or initializer
execution, hidden-Core/workspace-root/product/continuity mutation, provider
call, credential use, installation, database action, deployment, commit or
push. It did not touch, read, hash or inventory the protected operator
assessment and performed no broad untracked inventory.

### Prior finding status

1. `CORE-REFRESH-SPEC-REV-F1`: **`CLOSED`**. Every one of the five shapes now
   binds the exact old pin and frozen target as constants. Independently
   generated success projections with an internally equal but wrong target or
   a wrong old pin are rejected.
2. `CORE-REFRESH-SPEC-REV-F2`: **`CLOSED`**. Both incomplete shapes forbid
   success-only Core/pin hashes, exact restore counters, staged-zero and P4-E
   success assertions. They admit explicit absent, unreadable and readable-
   unrestored observations. Honest incomplete positives match without
   fabricating any hash or clean-restore fact; injected `core_head`,
   `staged_count`, `p4e_checkpoint` or initial-worker evidence-create count is
   rejected.
3. `CORE-REFRESH-SPEC-REV-F3`: **`OPEN`**. The authorized initial execution
   stage/prefix tokens are now closed and contain no `WORKER_DOCTOR`; complete
   rollback requires exactly `ONE_RECORDED`. The incomplete shapes, however,
   independently enumerate rollback failure stage and verifier state without
   relating them. Both generic validators accept
   `CONTAINMENT_CHECK + ONE_RECORDED`, even though the verifier occurs only
   after containment and restoration, and accept `EVIDENCE_WRITE + NOT_RUN`,
   even though that stage follows the verifier step. These are invalid temporal
   combinations, while R14 explicitly requires negatives for verifier states
   where forbidden.

   Repair the sole matrix/prose contract with one closed rollback-stage/
   verifier-state token or an equally machine-checkable relation for each
   incomplete outcome. At minimum, pre-verifier failures must require
   `NOT_RUN`, while post-verifier evidence failure must require
   `ONE_RECORDED`. Recompute and re-pin the matrix and add the cross-product
   negatives required by R14.
4. `CORE-REFRESH-SPEC-REV-F4`: **`OPEN`**. The accepted DESIGN amendment closes
   the ordinary target-movement lifecycle: the two worker artifacts and first
   completion review are immutable; the repair worker alone may create one
   conditional JSON; a later independent rereviewer owns one Markdown receipt;
   path ceilings and temporal carrier intersections are exact; and hash
   ownership has no self/cross cycle. But both conditional incomplete prose
   and matrix still admit rollback failure stage `EVIDENCE_WRITE` while
   requiring that same sole conditional JSON to exist with `CREATE`. If writing
   that only semantic record is the failed operation, it cannot contain the
   projection that reports its own failure, and no other repair-owned evidence
   path exists. R11 also calls that JSON the sole semantic owner.

   Define `EVIDENCE_WRITE` narrowly as failure of an earlier independently
   named evidence write that leaves the conditional record writable, or remove
   it from the conditional outcome and specify the independent rereviewer's
   authority to record an absent/unreadable conditional record. The repair must
   preserve the immutable three-artifact boundary and must not introduce an
   undeclared self-owning terminal path.

### Matrix, ownership and conformance result

- Exactly five outcomes exist and every outcome has exactly one shape.
- Canonical digest recomputation equals the SPEC and machine pin:
  `ab6546e0...59c90`.
- Registry identity/path/owner/risk/lifecycle match; the 2026-08-23 legacy
  family remains a separate unchanged semantic owner with no cross-binding.
- All `5/5` independently generated positive projections were accepted.
- The complete generated one-fact corpus contained `404` mutations
  (`69/70/62/111/92` by shape); all `404/404` were rejected.
- Immutable prior-artifact one-side hash changes and wrong conditional
  path/effect/self-hash additions are rejected. Mechanical one-fact coverage
  does not detect the valid-domain cross-field combinations retained in F3.

### Adjacent findings and waivers

- Adjacent findings: `NONE` beyond retained F3/F4.
- Waivers: `NONE`.

### Deterministic guards

- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family repository guard: `PASS` with no diagnostics.
- Focused invariant unit/integration tests: `35 passed, 2 skipped`.
- Catalog drift guard: `PASS` (`26` modules).
- File-size guard: `PASS`.
- Scoped diff check before this append: `PASS`.
- Scoped staged set: empty.

### Final rereview disposition

`SPEC_REVIEW_CHANGES_REQUIRED` — F1/F2 closed; F3/F4 remain open; adjacent
findings `NONE`, waivers `NONE`.

Return only F3/F4 to a declared `REPAIR_WORKER`, then route the recomputed
matrix/SPEC/pin to a fresh independent SPEC rereviewer. WORK_ORDER,
reconciliation/network/root effects, P4-E SPEC, commit and push remain
unauthorized.

---

## Independent SPEC rereview — retained F3/F4 closure — 2026-08-29

- Role: `INDEPENDENT_SPEC_REREVIEWER`
- Recomputed repaired SPEC raw SHA-256:
  `03932a375516ff100e452a40c92fa4886e5e4b1bb10488d446dc8faa162b4f01`
- Recomputed matrix raw/canonical SHA-256:
  `5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`
- Recomputed registry raw SHA-256:
  `ec2ff31d7a72154b7a2f21c189e9164e455360228f44591b1a45842babf971d5`
- Recomputed machine-pin raw SHA-256:
  `6ad871371d551ff55ca263a0d605573176e5218108b8e3032888e4cfe84511ae`
- Accepted DESIGN amendment raw SHA-256:
  `2f250e98914f671b19f7be3a820f2b216c277e8f8900e2f77ceaab69255a44e0`
- DESIGN amendment review artifact raw SHA-256:
  `c1056479cd53abc2ccbe3209a8304fc33976d258685f28919f9b267f249a7aff`
- Prior review artifact pre-append raw SHA-256:
  `81a561e4d457d72ef5837e5c10ac3cfe2639df9cd5c595cc06927229a5828598`
- Disposition: `SPEC_REVIEW_PASS`

### Rereview boundary

This fresh rereview rehydrated current canonical continuity and inspected only
the allowlisted SPEC, matrix/pin/registry, accepted DESIGN amendment/review and
prior SPEC review history. Its sole mutation is this appended reviewer-owned
section. It performed no network or doctor call, reconciler or initializer
execution, hidden-Core/workspace-root/product/continuity mutation, provider
call, credential use, installation, database action, deployment, commit or
push. It did not touch, read, hash or inventory the protected operator
assessment and performed no broad untracked inventory.

### Final finding disposition

1. `CORE-REFRESH-SPEC-REV-F1`: **`CLOSED`**. All five shapes retain exact old-
   pin and frozen-target constants. Wrong-but-internally-equal target and wrong
   old-pin probes remain rejected.
2. `CORE-REFRESH-SPEC-REV-F2`: **`CLOSED`**. Both incomplete outcomes retain
   honest observation states and forbid fabricated hashes, exact restoration,
   staged-zero, P4-E-success and evidence-availability facts.
3. `CORE-REFRESH-SPEC-REV-F3`: **`CLOSED`**. Each incomplete shape now has one
   closed `rollback_failure_verifier_pair` domain. Pre-verifier failures permit
   only `NOT_RUN`; verifier failure permits the two transcript-observable
   states; the single post-verifier write stage permits only `ONE_RECORDED`.
   Complete rollback still requires exactly one verifier. The original
   execution-stage/network-prefix domain remains closed and contains no
   separate `WORKER_DOCTOR`.

   The focused cross-product used the union of ten stage labels across both
   incomplete outcomes, both verifier states and both shapes: all `40/40`
   results matched the declared domains (`20` accepted, `20` rejected, zero
   mismatch). This includes rejection of the other outcome's owner-specific
   write stage and every temporally invalid verifier combination.
4. `CORE-REFRESH-SPEC-REV-F4`: **`CLOSED`**. Initial-worker
   `WORKER_RETURN_WRITE:ONE_RECORDED` is recordable in the already-writable
   canonical root JSON. Conditional
   `SHARED_FAILURE_CONTINUITY_WRITE:ONE_RECORDED` refers only to a shared-
   carrier continuity write and leaves the separately owned conditional
   rollback JSON writable. `EVIDENCE_WRITE` is absent from the matrix; explicit
   probes attempting either incomplete shape with that token are rejected.
   Failure to create a sole semantic JSON cannot self-report as its own matrix
   outcome. The immutable two worker artifacts plus completion review, the
   conditional rollback JSON and later rereview receipt retain their reviewed
   temporal path ceilings, owners and non-circular hash lifecycle. No new
   authority was introduced.

### Matrix, ownership and conformance result

- Exactly five outcomes exist; every outcome has exactly one shape.
- Canonical digest recomputation equals the SPEC and machine pin:
  `5f6e477d...a8025`.
- Registry identity/path/owner/risk/lifecycle agree. The 2026-08-23 legacy
  family remains unchanged and separately bound, with no semantic-owner
  collision.
- All `5/5` independently generated positive projections were accepted.
- Complete generated one-fact corpus: `400` mutations
  (`69/70/60/111/90`); all `400/400` were rejected.
- Focused 40-pair temporal cross-product: `20` accepted, `20` rejected, zero
  mismatch.
- Wrong fixed refs, fabricated incomplete success facts, changed immutable
  hashes, wrong conditional paths/effects, rollback self-hash fields and both
  self-owning `EVIDENCE_WRITE` probes are rejected.

### Adjacent findings and waivers

- Adjacent findings: `NONE`.
- Waivers: `NONE`.

### Deterministic guards

- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family repository guard: `PASS` with no diagnostics.
- Focused invariant unit/integration tests: `35 passed, 2 skipped`.
- Catalog drift guard: `PASS` (`26` modules).
- File-size guard: `PASS`.
- Scoped diff check before this append: `PASS`.
- Scoped staged set: empty.

### Final rereview disposition

`SPEC_REVIEW_PASS` — F1-F4 closed; findings `NONE`, waivers `NONE`.

The ORCHESTRATOR may open WORK_ORDER only through an explicit phase transition.
Reconciliation/network/root effects, P4-E SPEC, commit and push remain
unauthorized.
