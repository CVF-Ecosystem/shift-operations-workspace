# Independent INTAKE Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Reviewed phase: `INTAKE` only
- Reviewer role: `INDEPENDENT_INTAKE_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `INTAKE_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

The review compared
`docs/decisions/INTAKE_2026-08-23_CVF_CORE_REFRESH.md` against current
canonical continuity and handoff, AGENTS and manifest/policy requirements,
the fetched public-Core graph and delta, the actual reconciler/root-wrapper
sources, the current downstream dirty/staged state, and the independently
reviewed 2026-08-20 refresh lineage.

The operator's `next` response opened only this prerequisite INTAKE after the
doctor blocked P4-C on Core freshness. R2 is correct because the contemplated
action includes public network access, hidden-Core replacement, workspace-root
writes and downstream governance-pin changes. No reconciliation or later-phase
authority follows from that response.

Independent read-only checks reproduced:

- hidden-Core `HEAD`, `main` and manifest pin:
  `7d9f360a3df11ac998972728000785799399c02b`;
- fetched `origin/main` target:
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`;
- current Core is clean, its merge-base with the target is current `HEAD`, and
  the graph is exactly `0` ahead / `1` behind;
- the sole public commit changes only `README.md`, adds
  `docs/guides/CVF_EXTERNAL_AGENT_ROUND_TRIP_KIT.md`, and changes
  `docs/guides/external-agent-review-guide.md`, totaling 293 insertions;
- downstream `HEAD` and `origin/main` both equal
  `0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, with an empty staged set;
- the pre-INTAKE P4-C set excluding the evidence-ineligible assessment is
  exactly 19 paths, and its LF-terminated sorted-path digest is
  `0dd882e328a44a9659ba289594b194adf7111d5ee729104ba500082767adc7c9`;
- `python scripts/check_session_state.py` and `git diff --check` pass.

The current doctor failure is the declared `BEHIND_PUBLIC_REMOTE` trigger, not
evidence of reconciliation. No new fetch was performed during this review.
The operator assessment was not opened, edited, staged, hashed or used.

## Numbered findings

1. **CORE-REFRESH-INTAKE-REV-F1 — The reconciler-managed root inventory is
   incomplete.** The current public-safe installer also manages
   `WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json` through preserve-if-present /
   create-if-missing semantics and may delete
   `Get-CVF-Workspace-OverlayProfiles.ps1`. The INTAKE enumerates neither of
   those targets, although it enumerates the other root writes and only two of
   the three obsolete overlay deletions. The 2026-08-20 independent review
   specifically required all 17 root targets—including absent/deletion
   candidates—to receive existence, preimage, postimage and rollback
   treatment. Add both paths to the declared root-effect inventory and keep
   the later exact evidence contract aligned with the complete set.

2. **CORE-REFRESH-INTAKE-REV-F2 — The reconciler's rollback gap is not stated
   explicitly enough to control failure after clone.** Source inspection shows
   that its `catch` restores the old Core when a replacement failure occurs,
   but it does not restore workspace-root artifacts or downstream files already
   written before the failure. On success followed by a later pin, initializer,
   gate or continuity failure, it likewise supplies no automatic complete
   rollback. The INTAKE requires preimages in general, but does not record this
   non-atomic behavior or require the later DESIGN/WORK_ORDER to define the
   executable post-clone rollback used successfully in the 2026-08-20 tranche:
   containment checks, preservation/move of the failed replacement, restoration
   of the original Core, hash-verified restoration of prior root files,
   quarantine of newly created root files, downstream-pin restoration, no
   deletion of evidence/backups, and a recorded post-rollback doctor state.
   Make that obligation explicit so a partial root refresh cannot be treated as
   reconciler-level atomic success.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted INTAKE boundaries

Subject only to F1 and F2, the INTAKE correctly records operator authority,
R2 classification, exact local/target ancestry and documentation-only delta,
the public unauthenticated Git boundary, rejection of
`-UpdateProjectManifests`, separate full downstream pin and ignored-binding
regeneration, preserved Core/root backups, frozen-target stop behavior, and
the no-provider/no-governance-behavior-claim boundary.

P4-C is correctly parked at repaired Work Order F1 pending rereview. Its 14
non-continuity paths and P4-C handoff remain protected, while only five shared
continuity carriers may record the parking/restore transition. Neither P4-C
BUILD nor Core reconciliation is authorized by this review.

## Disposition

`INTAKE_REVIEW_CHANGES_REQUIRED`.

Return only F1 and F2 for one bounded INTAKE repair and independent rereview.
DESIGN, SPEC, WORK_ORDER, BUILD, reconciliation, provider/credential/install/
deployment/commit/push effects remain unauthorized.

## Bounded rereview — CORE-REFRESH-INTAKE-REV-F1..F2

- Rereview role: `INDEPENDENT_INTAKE_REVIEWER`
- Rereview scope: repaired F1 and F2 only
- Rereview findings: `NONE`
- Rereview waivers: `NONE`

1. **F1 CLOSED.** The repaired INTAKE now identifies exactly 17 unique
   reconciler-managed workspace-root targets: `WORKSPACE_RULES.md`; all 12
   unconditional installer write targets; the preserve-if-present /
   create-if-missing `WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json`; and all
   three possible obsolete-overlay deletion targets, including
   `Get-CVF-Workspace-OverlayProfiles.ps1`. It requires existence, SHA-256
   preimage/postimage and create/delete evidence across the complete set and
   retains every backup.
2. **F2 CLOSED.** The repaired INTAKE explicitly states that the reconciler is
   not atomic across Core, root and later downstream effects. It requires the
   later DESIGN and Work Order to make rollback executable through exact-root
   containment checks; preservation/move of the failed replacement; original-
   Core restoration; hash-verified restoration of prior root artifacts;
   quarantine of newly created root artifacts in a preserved failed-delta
   tree; downstream pin/header/continuity preimage restoration; deletion of no
   backup or evidence; and recorded trigger, move, hash and post-rollback
   doctor results before stop.

Independent rereview found canonical continuity consistent at
`cvf_core_refresh_intake_repair_ready_for_rereview`. The session-state guard
and `git diff --check` passed, the staged set remained empty, and read-only
Core refs remained local `7d9f360a3df11ac998972728000785799399c02b`
versus frozen fetched target
`3b031fec35473e6ee6a554c4c72400e7a23b06c5` (`0` ahead / `1` behind). No
network, reconciliation or external effect occurred, and the assessment was
not accessed or used.

## Final disposition after bounded rereview

`INTAKE_REVIEW_PASS`.

The initial `INTAKE_REVIEW_CHANGES_REQUIRED` remains above as historical
evidence and is superseded by this disposition. F1 and F2 are closed without
waiver. DESIGN may proceed only through a fresh declared role/phase
transition; reconciliation and BUILD remain unauthorized.

## Target-rebase amendment rereview — 2026-08-24

- Role: `INDEPENDENT_INTAKE_REVIEWER`
- Scope: only the appended target-rebase amendment
- Findings: `NONE`
- Waivers: `NONE`

Canonical continuity and the active handoff record exact operator authority for
target `864c4e0e6139f3e32067dea41f43f240e505c0d8`. Read-only local Git evidence
confirms that target descends from
`3b031fec35473e6ee6a554c4c72400e7a23b06c5` and that the incremental range is
exactly two commits touching only three documentation/projection paths:
`docs/guides/CVF_EXTERNAL_AGENT_ROUND_TRIP_KIT.md`,
`docs/guides/external-agent-review-guide.md`, and
`docs/reference/CVF_EXTERNAL_AGENT_OWNER_SURFACE_INDEX.json`.

The preserved failed-attempt receipts confirm `TARGET_MOVEMENT`, public-operation
prefix `1`, no initializer invocation, restored Core
`7d9f360a3df11ac998972728000785799399c02b` clean, all `17/17` root effects and
`10/10` carriers verified, project status restored, and staged count zero. The
failed replacement remains preserved at the newly observed target. The
rollback verifier's sole failure was the expected freshness mismatch against
the advanced public tip, not restoration failure.

The amendment changes only the frozen target and dependent pins. R2 scope,
sanctioned scripts, exact `17/12/10` ceilings, assessment exclusion, rollback,
no-provider, and no-commit/push boundaries remain unchanged. The session-state
guard and `git diff --check` pass; the staged set is empty. No network or other
external effect occurred during this rereview.

### Target-rebase disposition

`INTAKE_REVIEW_PASS`.

The target/pin amendment may proceed to DESIGN under a fresh role/phase gate.
This disposition does not authorize reconciliation or BUILD; any further target
movement still requires stop and rollback.
