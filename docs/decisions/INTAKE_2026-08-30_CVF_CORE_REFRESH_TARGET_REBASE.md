# INTAKE — CVF Public-Core Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase: `INTAKE`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_INTAKE_REVIEW`
- Active role: `INTAKE_AUTHOR`
- Parked product lane: P4-E at `DESIGN_REVIEW_PASS`

## Request and authority

The prior governed refresh attempt froze target
`06c3d040a3dc8fa22fa27f2f9c3e40739def075e`. Its sole reconciler invocation
instead observed public `main`
`d7860138350130d6d105826ce186f1beeaba3c2d`; it stopped before pin edits or
initializer, rolled back completely and received independent
`REVIEW_PASS_FAILURE_ROLLED_BACK`, findings/waivers `NONE/NONE`.

On 2026-08-30 the operator answered `tiếp tục`. This grants fresh INTAKE
documentation and independent INTAKE review for rebasing the governed target
to the observed `d786013...`. It does not authorize DESIGN, SPEC, Work Order,
network, reconciler, initializer, hidden-Core/workspace-root mutation, new
target adoption, provider/credential use, product/database change,
installation, deployment, commit or push.

## Current verified local truth

- Restored Core is clean at old pin
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6` with the expected public remote.
- Local Core `origin/main` is `d7860138350130d6d105826ce186f1beeaba3c2d`,
  observed independently by the failed replacement clone and the rollback
  verifier. No new fetch was used for this INTAKE.
- Old pin is `0` commits ahead and `5` behind the proposed target.
- The five commits are `06c3d04`, `2aa1784`, `771cb39`, `a64bbc8` and
  `d786013`; the tip is dated 2026-08-29 and titled
  `sync: public EARTR source-pack profile from governance@e9d718c2e`.
- The cumulative delta contains 202 paths, including 121 paths outside
  Markdown/docs-only classification. This is not a documentation-only refresh.
- Local comparison shows no change in the sanctioned reconciler, doctor,
  new-workspace script or `governance/toolkit/05_OPERATION` surface selected by
  the prior Work Order.
- Downstream project source/product state is not changed by this INTAKE. The
  prior failed-attempt evidence remains immutable and staged content is zero.

## Intent and acceptance boundary

The intent is to decide whether a new governed attempt may use
`d7860138350130d6d105826ce186f1beeaba3c2d` as its frozen public-Core target,
while preserving the bootstrap-native command graph, workspace isolation,
P4-E checkpoint and narrow deterministic reconciliation claim.

A later successful attempt would update only the hidden Core reference,
declared workspace-root kit, downstream manifest/AGENTS/binding pins and
maintenance continuity/evidence carriers. It would not adopt the 202-path Core
delta into product runtime, prove CVF control of an AI agent, or establish
production/deployment readiness.

## Constraints carried forward

1. Phase order remains `INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW → FREEZE`.
2. Risk remains R2 because a later attempt uses public Git network and mutates
   hidden Core/workspace-root governance carriers.
3. A fresh target is never adopted implicitly. Any target different from
   `d786013...` stops the later attempt and requires another governed rebase.
4. The prior attempt's root receipt, worker return, completion review, evidence
   directory and preserved replacement are immutable historical evidence.
5. A new DESIGN must assign collision-free attempt-2 paths for worker receipt,
   worker return, completion review, evidence directory and any conditional
   reviewer-movement rollback/rereview artifacts. No prior evidence path may be
   overwritten or reinterpreted.
6. The protected operator assessment remains wholly excluded: no open, read,
   hash, inventory, stage or use. Broad untracked inventory remains forbidden.
7. P4-E decisions/handoff remain byte-protected and semantically parked at
   `DESIGN_REVIEW_PASS` throughout reconciliation governance.
8. No credentials, provider call, package install, product/database mutation,
   deployment, commit or push belongs to this INTAKE.

## Risk and failure model

- `TARGET_MOVEMENT`: advertised/cloned public tip differs from `d786013...`.
- `PATH_OR_TOOL_DRIFT`: sanctioned bootstrap surfaces differ before BUILD.
- `PREIMAGE_OR_CONTAINMENT_FAILURE`: complete recoverable preimages or exact
  workspace containment cannot be proved.
- `EVIDENCE_COLLISION`: any new attempt path already exists or overlaps prior
  evidence.
- `ROLLBACK_FAILURE`: old Core/root/pins/shared carriers/binding cannot be
  restored honestly.
- `CLAIM_EXPANSION`: refresh is restated as runtime adoption, AI governance or
  production readiness.

All are fail-closed. No retry or target rebase occurs inside a BUILD attempt.

## INTAKE acceptance criteria

Independent review must verify:

1. the old pin, proposed target, five-commit ancestry and 202/121 path facts;
2. the prior attempt's `FAILURE_ROLLED_BACK` and terminal review receipts;
3. unchanged sanctioned bootstrap/reconciler surface at the proposed target;
4. R2 classification and absence of current external-effect authority;
5. immutable prior evidence plus mandatory collision-free attempt-2 lifecycle;
6. parked P4-E and protected-assessment boundaries; and
7. findings and waivers explicitly recorded.

## Next governed move

Independent INTAKE review only. DESIGN, SPEC, Work Order, BUILD, network/Core/
root effects, P4-E SPEC, commit and push remain unauthorized until
`INTAKE_REVIEW_PASS` and an explicit phase transition.
