# Independent DESIGN Review — CVF Public-Core Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase reviewed: `DESIGN`
- Risk: `R2`
- Role: `INDEPENDENT_DESIGN_REVIEWER`
- Reviewed DESIGN SHA-256:
  `90313677f0efffcc2e5dd78b6e1efb95e2e919c1494adc9c9274128ec0865f73`
- Disposition: `DESIGN_REVIEW_PASS`
- Findings: `NONE`
- Waivers: `NONE`

## Review boundary and method

The reviewer did not author the DESIGN. Review used only explicit local,
allowlisted reads of current continuity, the accepted INTAKE and review, the
prior accepted Core-refresh architecture/amendment/contract/closure evidence,
the invariant-family standard, and local Git objects already present in the
restored hidden Core. Read-only commands recomputed the DESIGN hash, Core
refs, ancestry, tracked cumulative delta, selected sanctioned-tool objects,
downstream initializer hash, staged state and exact existence state of the six
attempt-2 evidence paths.

No fetch, doctor, reconciler, initializer, provider call, credential access,
package installation, hidden-Core/workspace-root/product/database/deployment
mutation, commit or push occurred. The protected operator assessment was not
opened, read, hashed, staged, inventoried or used. No broad downstream
untracked inventory was performed. Creation of this review document is the
reviewer's sole mutation.

## Independent evidence and assessment

### Frozen target and bootstrap-native graph

- Restored Core `HEAD` is clean at
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`; existing local
  `refs/remotes/origin/main` is
  `d7860138350130d6d105826ce186f1beeaba3c2d`.
- Local ancestry is exactly `0` ahead and `5` behind. The cumulative tracked
  delta is `202` paths, of which `121` are outside the accepted Markdown/
  `docs/`/`documentation/` classification. The DESIGN correctly avoids a
  documentation-only or product-runtime-adoption claim.
- Git object ids match old-to-target for the sanctioned reconciler
  (`4b705c6b...`), doctor (`2ad83efe...`), new-workspace script
  (`5f311a1a...`) and `governance/toolkit/05_OPERATION` tree
  (`23fe8bd3...`); the scoped name-status delta is empty. The downstream
  initializer remains
  `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`.
- D1-D3 preserve the accepted two-script command graph: zero-effect frozen-
  target preflight, preservation before the one reconciler invocation,
  immediate target checkpoint, exact two-pin bridge, then exactly one
  downstream initializer. Target movement at any checkpoint is fail-closed;
  no retry or in-attempt target rebase is admitted.

### Effect ceilings and rollback ownership

The DESIGN carries forward the exact prior ceiling shape without importing
the old attempt's evidence names: `17` enumerated workspace-root targets; two
pin carriers; nine current shared continuity carriers, with the active
target-rebase handoff replacing the closed attempt-1 handoff; the ignored
local binding; and two worker-owned attempt-2 artifacts. It requires the later
SPEC and Work Order to enumerate rather than infer the 17-root set and to
classify every effect as `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE`.

Preservation and rollback cover old Core, roots, pins, shared carriers and
binding before reconciliation. Originally absent targets must return to
absence, while backups, failed replacements and failure deltas remain
retained. Worker-time failure restores preimages, runs only the contractually
allowed rollback verifier, writes truthful failure evidence and stops without
pin/initializer continuation or retry. Incomplete restoration remains an open
failure and cannot receive a clean-rollback claim.

Temporal ownership is closed and non-concurrent. The implementation worker
owns initial execution and worker-time rollback only. A completion reviewer
does not repair. Reviewer-observed target movement preserves the immutable
success receipt, worker return and movement review, then routes a distinct
rollback-only repair worker using frozen BUILD preimages, followed by a
distinct terminal rereviewer. The closer acts only after accepted terminal
review; commit stewardship remains inactive. This is consistent with the
accepted 2026-08-29 reviewer-movement amendment and does not widen authority.

### Collision-free attempt-2 lifecycle

All six exact attempt-2 paths were independently checked and are currently
absent: the contained evidence directory, worker JSON, worker Markdown,
completion review, conditional reviewer-movement rollback JSON and
conditional terminal rereview. The corresponding attempt-1 receipt, worker
return, completion review and contained evidence directory remain present and
historical. The DESIGN forbids reuse or reinterpretation of those paths.

The two worker artifacts neither self-hash nor cross-hash. Their final hashes
belong to the separately owned completion review. A conditional rollback JSON
does not self-hash, remains immutable for the terminal rereviewer, and the
rereview does not self-hash. No impossible final-hash dependency or evidence-
ownership cycle was found.

### Invariant family, outcomes and claim boundary

Applicability is correctly `TRIGGERED` under
`docs/cvf/INVARIANT_FAMILY_STANDARD.md`: the attempt has shared receipts over
multiple outcomes, outcome-controlled fields, exact counter/temporal
relations and multiple validator roles. Requiring a successor family, new
matrix, canonical digest machine pin and shared proof before SPEC review is
correct. The immutable attempt-1 family is not amended or reinterpreted.

The required later outcome coverage includes zero-effect refusal, success,
complete and incomplete worker rollback, reviewer target movement, and
complete and incomplete reviewer-movement rollback. The DESIGN also requires
ordered command counts, verifier-stage truth and mutually exclusive evidence
lifecycles, while leaving exact per-outcome rules to the successor matrix.

P4-E remains parked at accepted `DESIGN_REVIEW_PASS`; XR1 remains separate.
The protected assessment, provider/credential, product/database, installation,
deployment, commit and push boundaries are explicit. No AI/agent-governance
claim is made, so provider evidence is neither used nor claimed. A later
successful closure is limited to deterministic Core freshness/pin
reconciliation within enumerated paths.

## Numbered findings

`NONE`.

## Waivers

`NONE`.

## Disposition

`DESIGN_REVIEW_PASS`.

The target-rebase DESIGN is internally consistent, executable at architecture
level, preserves immutable attempt-1 evidence and role-separated rollback,
and introduces no unauthorized external effect. This disposition closes only
the DESIGN review gate. SPEC requires an explicit phase transition and must
materialize the successor invariant family, exact path lists, hashes, command
accounting, terminal grammar and evidence validation before any Work Order or
BUILD authority exists.
