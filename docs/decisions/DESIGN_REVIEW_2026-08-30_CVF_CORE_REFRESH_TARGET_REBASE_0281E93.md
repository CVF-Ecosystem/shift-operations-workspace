# Independent DESIGN Review — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase reviewed: `DESIGN`
- Risk: `R2`
- Role: `INDEPENDENT_DESIGN_REVIEWER`
- Reviewed DESIGN SHA-256:
  `1fc8c00dd19bfd08a4b185f1fdc41fbe58991a7006248a593a5fc6fc371cb8b5`
- Disposition: `DESIGN_REVIEW_PASS`
- Findings: `NONE`
- Waivers: `NONE`
- Date: `2026-08-30`

## Review boundary and independence

The reviewer did not author or repair the DESIGN. Review compared its exact
bytes with the accepted exact-target INTAKE and review, the prior target-rebase
architecture, attempt-2 failure and reviewed rollback, the open conformance-
fixture repair lineage, the rejected protocol-exception DESIGN and findings
`DR-F1..DR-F4`, current sanctioned scripts, the invariant-family standard and
registry, and local Git objects already present in the hidden Core.

No doctor, fetch, reconciler, initializer, provider call, credential access,
installation, broad downstream untracked inventory, Core/workspace-root/pin/
binding/product/database/deployment mutation, continuity edit, commit or push
occurred. The protected operator assessment was not opened, read, hashed,
inventoried, staged or used. Creation of this review is the reviewer's sole
mutation; this artifact intentionally does not self-hash.

## Independent local evidence

### Exact target and frozen tools

- The reviewed DESIGN bytes match the declared SHA-256 above.
- Hidden Core is clean at old pin
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`; its existing local
  `refs/remotes/origin/main` is exactly
  `0281e93bab4a75083973eb7242fd2bc8f65055d3`.
- Local ancestry is exactly `0` ahead / `6` behind and the cumulative tracked
  delta is `256` paths. These checks used local objects only.
- Reconciler raw/blob are `96ac0cce...58196c` / `4b705c6b...f4945`, doctor
  raw/blob are `2410bbab...96b` / `2ad83efe...c8c`, new-workspace raw/blob
  are `7e5567c5...27032` / `5f311a1a...3c5a`, and the operation tree is
  `23fe8bd3...bbb6` at both old pin and target.
- The downstream initializer is `bb37b162...209c8`; the active rule-pack
  selector is `f51bacd2...c855`. The DESIGN correctly makes any later byte,
  object or profile movement a pre-effect refusal.

The architecture accounts honestly for the current scripts. The reconciler
performs the replacement clone and refreshes the exact 17 workspace-root
targets; the initializer performs one fetch and invokes the doctor, whose own
freshness check performs another fetch. Thus the successful three-operation
Git network sequence and the required post-doctor five-way equality are
correct. Nothing in the DESIGN mislabels the doctor as read-only or
zero-network, closing the substance of protocol-exception `DR-F1`.

### P0 feasibility and fixture lineage

The current frozen conformance implementation hashes match its reviewed
lineage: contract `19616eca...497`, generator `d5f2e133...82ae`, ownership
validator `71ec4c54...aac7`, oracle `f9bf70a8...6cdc`, and strict harness
`cae96b6e...adb9`. A read-only in-memory execution of the frozen harness
reproduced `PASS`, seven exclusive positives, `894/894` exact generator/oracle
mutations and `40/40` temporal judgments. Targeted probes confirmed every one
of the six SHA-field instances rejects literal `"x"` on both the repository
matcher and independent strict surface.

The open fixture findings remain accurately bounded. `F1` concerns a raw-text
test assertion and `F2` concerns two missing helper copies in a disposable-
repository fixture; neither invalidates the retained harness semantics above.
Their exact current test preimages remain `49dba6d8...14a7` and
`44cdf845...79e6`. The DESIGN does not edit, authorize, close or suppress that
lineage, does not repoint its hard-coded top-level runner, and requires the
future target-family P0 adapter to consume pinned generic functions and
recompute counts. P0 is therefore architecturally feasible without an
unauthorized fixture repair. Any byte drift or need to repair remains a
zero-effect refusal.

### Evidence lifecycle, ceilings and rollback

All six exact attempt-3 paths named by the DESIGN are currently absent. They
are distinct from attempt-1, attempt-2, fixture-repair and protocol-exception
artifacts. Hash ownership is acyclic: worker artifacts do not self-hash or
cross-hash; completion review owns their final hashes; a conditional rollback
record does not self-hash; and the terminal rereview owns readable prior
hashes without depending on a future artifact.

The effect model is executable and bounded:

- workspace-root effects are the exact 17 reconciler-managed targets, each
  requiring one `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE` observation;
- initial downstream tracked effects are exactly two pin carriers, nine shared
  continuity carriers and two worker artifacts, with the ignored binding as
  the sole additional local effect;
- hidden-Core backup/replacement and failed-state retention are separately
  observed and contained rather than being concealed as root-file effects;
- every other downstream path, including fixture, protocol, P4-E, catalog,
  product/runtime and database surfaces, remains byte-protected; and
- broad untracked inventory is neither required nor permitted.

Worker-time failure preserves the observed failure before restoring Core,
17 roots, two pins, nine shared carriers and binding from preimages. The one
rollback-verifier doctor is explicitly treated as a network/ref effect and its
actual before/after state must be recorded. Incomplete restoration has a
separate non-success outcome and cannot fabricate unavailable hashes or
checks.

Reviewer target movement is also closed without self-repair or retargeting. A
distinct completion reviewer may run only the exact authorized doctor; remote-
ref movement produces immutable `REVIEW_TARGET_MOVEMENT` and stops. A distinct
rollback-only repair worker may use only BUILD preimages and create the
conditional rollback record; a distinct rereviewer owns the terminal result.
This preserves the accepted reviewer-movement architecture and does not revive
the rejected self-amending protocol. The DESIGN therefore also avoids the
authority, activation and receipt-lifecycle defects in `DR-F2..DR-F4`.

### Phase, invariant family and claims

Role and phase separation are explicit. DESIGN review does not grant SPEC,
Work Order or BUILD authority. Even a later authorization-review PASS leaves
external effects ungranted until an explicit authority record exists. Worker,
completion reviewer, conditional repair worker, terminal rereviewer, closer,
session steward and commit steward have non-overlapping responsibilities.

Invariant-family applicability is correctly `TRIGGERED` because attempt 3 has
shared outcome receipts, outcome-controlled fields, exact counter/temporal
relations, multiple validator surfaces and an adjacent conformance failure.
The registry currently contains the immutable predecessor families and no
attempt-3 successor, as expected at DESIGN. Requiring the SPEC author to add a
new matrix, registry entry and one-way digest pin before SPEC review follows
the invariant-family standard and preserves sole semantic ownership in the
future matrix.

The bounded claim is accurate. A later accepted success can establish only
exact public-Core freshness and pin reconciliation inside the enumerated
workspace boundary. It cannot establish AI/agent governance behavior,
provider behavior, downstream runtime adoption of the Core delta, arbitrary-
untracked absence, fixture-repair closure, P4-E implementation, database,
deployment or production readiness. No mock or provider evidence is used for
this repository-maintenance design claim.

## Findings

`NONE`.

## Waivers

`NONE`.

## Disposition

`DESIGN_REVIEW_PASS`.

The exact-target DESIGN is internally consistent and executable at architecture
level. It freezes the real doctor/network effect graph, makes strict P0 a
pre-effect condition without borrowing fixture-repair authority, assigns a
collision-free attempt-3 evidence lifecycle, closes root/downstream/binding
effects and rollback ownership, handles reviewer target movement without
retry, triggers a successor invariant family, and keeps claims bounded.

This closes only the independent DESIGN review gate. An explicit transition is
required before SPEC. SPEC, Work Order, BUILD, doctor/fetch/reconcile,
Core/root/pin/binding mutation, fixture repair, provider/credential use,
installation, product/database change, deployment, commit, push and P4-E SPEC
remain unauthorized by this review.
