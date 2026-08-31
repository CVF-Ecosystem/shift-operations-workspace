# INTAKE — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase: `INTAKE`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_INTAKE_REVIEW`
- Active role: `INTAKE_AUTHOR`
- Parked product lane: P4-E at `DESIGN_REVIEW_PASS`

## Request and authority

The prior target-rebase attempt for `d7860138350130d6d105826ce186f1beeaba3c2d`
closed bounded as `FAILURE_ROLLED_BACK` with independent
`REVIEW_PASS_FAILURE_ROLLED_BACK`, findings/waivers `NONE/NONE`. A later
protocol-exception DESIGN review observed that the mandatory doctor fetched
and moved local `origin/main` to
`0281e93bab4a75083973eb7242fd2bc8f65055d3`, while the clean hidden Core stayed
at old pin `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`. That review stopped on
`TARGET_DRIFT` and authorized no BUILD or reconcile.

On 2026-08-30 the operator explicitly approved opening a fresh target-rebase
INTAKE for `0281e93`, while withholding BUILD/reconcile until a Work Order has
been independently reviewed. This authority permits this INTAKE and its
independent review only. It does not authorize DESIGN, SPEC, WORK_ORDER,
doctor/fetch, reconciler, initializer, hidden-Core/workspace-root/pin/binding
mutation, provider or credential use, installation, product/database change,
deployment, commit or push.

## Current verified local truth

- Hidden Core is clean at old pin
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6` with public remote
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`.
- Existing local `refs/remotes/origin/main` is exactly
  `0281e93bab4a75083973eb7242fd2bc8f65055d3`. No fetch was used to establish
  the INTAKE facts below; the target was already present after the recorded
  doctor effect.
- Old pin versus proposed target is exactly `0` commits ahead and `6` behind.
  The final added commit is dated 2026-08-30 and titled
  `sync: public surface update from governance@334f34611`.
- The cumulative old-pin-to-target delta is `256` paths, including `173`
  paths outside Markdown/docs-only classification. The delta from the prior
  frozen target `d786013...` to `0281e93...` is `63` paths, `58` outside that
  classification. This is not a documentation-only refresh.
- The selected sanctioned Core surfaces are unchanged between old pin and
  proposed target: reconciler blob `4b705c6b...`, doctor blob `2ad83efe...`,
  new-workspace blob `5f311a1a...`, and operation-tree `23fe8bd3...`.
  The downstream initializer remains SHA-256 `bb37b162...209c8`.
- The project worktree contains pre-existing governed continuity, evidence and
  invariant-family work. It must be preserved; this INTAKE neither claims a
  clean downstream worktree nor authorizes broad untracked inventory.

## Intent and acceptance boundary

The intent is to decide whether a new governed path may freeze `0281e93...`
as the exact public-Core target and, only after DESIGN, SPEC and an
independently reviewed exact Work Order, request separate operator authority
for external-effect BUILD.

A later successful BUILD could update only the hidden Core, declared
workspace-root kit, exact downstream pin/binding carriers and bounded
maintenance continuity/evidence. It would not adopt the 256-path Core delta
as downstream product runtime, prove that CVF controlled an AI/agent, or
establish deployment or production readiness.

## Constraints and failure model

1. The phase order is `INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE`.
2. R2 remains controlling because a later BUILD would use public Git network
   and mutate hidden-Core/workspace governance surfaces.
3. `0281e93...` is an intake proposal, not an adopted pin. Any further target
   movement is `TARGET_DRIFT`, fails closed and requires fresh authority.
4. No additional doctor or fetch is allowed before a reviewed Work Order
   expressly accounts for its network and remote-ref effects.
5. Prior attempt-1/attempt-2, fixture-repair and protocol-exception artifacts
   are immutable inputs. A later DESIGN must assign collision-free successor
   evidence paths and preserve failed state before rollback.
6. The protected operator assessment remains excluded: no open, read, hash,
   inventory, stage or use. Broad downstream untracked inventory is forbidden.
7. P4-E remains byte-protected and parked at `DESIGN_REVIEW_PASS`; XR1 debt is
   unchanged.
8. No provider call is required for this repository-maintenance claim. Mock
   output cannot be used as governance evidence, and no AI-governance behavior
   claim is made.
9. BUILD/reconcile remains prohibited until the exact Work Order is
   independently reviewed; that review alone must not be treated as external-
   effect approval unless the later authority record says so explicitly.

Fail-closed conditions include `TARGET_DRIFT`, `TOOL_OR_EFFECT_DRIFT`,
`PREIMAGE_OR_CONTAINMENT_FAILURE`, `EVIDENCE_COLLISION`,
`ROLLBACK_INCOMPLETENESS`, `PROTECTED_STATE_CONTACT` and `CLAIM_EXPANSION`.

## INTAKE acceptance criteria

Independent review must verify:

1. the explicit operator boundary and R2 classification;
2. exact old pin, proposed target, public remote, `0/6` ancestry and the
   `256/173` plus prior-target `63/58` delta facts using local objects only;
3. the recorded doctor-induced target movement without running doctor/fetch;
4. selected sanctioned tool/tree equality and initializer hash;
5. immutable predecessor evidence, collision-free successor lifecycle,
   rollback and target-drift obligations;
6. P4-E, protected-assessment, dirty-worktree preservation and claim
   boundaries; and
7. findings and waivers explicitly recorded.

## Next governed move

Independent INTAKE review only. DESIGN, SPEC, WORK_ORDER, BUILD, doctor/fetch,
reconcile, Core/root/pin/binding effects, fixture repair, protocol activation,
P4-E SPEC, commit and push remain unauthorized.
