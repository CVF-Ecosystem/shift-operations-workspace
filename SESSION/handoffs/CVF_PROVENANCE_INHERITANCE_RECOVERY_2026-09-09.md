# Handoff - CVF Provenance Inheritance Recovery

- Tranche: `CVF-PROVENANCE-INHERITANCE-RECOVERY-2026-09-09`
- Status: `FREEZE / CLOSED_BOUNDED / READY_FOR_NEXT_GOVERNED_TRANCHE`
- Risk: `R2`
- Active role: `ORCHESTRATOR`
- Branch: `chore/cvf-provenance-inheritance-recovery`
- Updated: `2026-09-09`

## Startup truth

This is the operator's first-party project. Read `.cvf/manifest.json` and
`AGENTS.md` first. Public CVF Core is pinned at
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4`; the operator-local rule pack is
mandatory and comes from private provenance
`bee38695ebac452e0ea6b3487706ed5c84f5fc2e`. Both are read-only. Work only in
this repository.

## Closed recovery

The 2026-09-09 recovery reconciled current CVF governance and continuity,
eliminated platform-dependent digest failures, repaired stale Project Knowledge
and invariant fixtures, and preserved product truth. See
`docs/decisions/CVF_PROVENANCE_INHERITANCE_RECOVERY_COMPLETION_2026-09-09.md`
for the evidence ledger and claim boundary.

The workspace doctor passes all 24 mandatory checks. Its only note is the
intentional legacy-catalog compatibility path: this mature project's registry
and generator use a different schema at the paths reserved by catalog kit 1.1.
Do not replace them mechanically; catalog migration is a separate parked
tranche.

## Product truth

Product behavior is unchanged. Phases 0-3 remain closed within their prior
boundaries. Phase 4 is 7/8. P4-E identity/conversation routing remains at
independently accepted `DESIGN_REVIEW_PASS`; the former Core-refresh blocker is
satisfied, but SPEC, Work Order and BUILD have not been granted. Phase 5 is
not started.

## Next allowed move

Record a fresh explicit P4-E transition from accepted DESIGN to SPEC. Then
author and independently review the SPEC and a bounded Work Order before any
BUILD. Keep Phase 5, external-repository absorption, catalog schema migration,
and XR1 historical-object debt parked.

## Prohibited carry-forward

- Do not mutate public Core or private provenance from this project.
- Do not start P4-E BUILD from this handoff.
- Do not treat historical live receipts as evidence for new behavior.
- Do not expand local/disposable evidence into production readiness.
- Do not assume the catalog note means its schema may be overwritten.

## Predecessor

`SESSION/handoffs/CVF_GOVERNANCE_CONTROL_LOSS_LEARNING_2026-08-31.md` remains
settled historical evidence and must not be rewritten.
