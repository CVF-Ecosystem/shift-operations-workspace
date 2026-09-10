# External Repository Absorption Intake Handoff

Status: INTAKE_READY / SOURCE_SET_REQUIRED

Date: 2026-09-10

## Operator Decision

After Phase 4 and the CVF machine-inheritance refresh were pushed to GitHub,
the operator selected return to external-repository absorption work.

## External Repository Absorption Entry Control

| Field | Disposition |
|---|---|
| sourceType | External repository set; exact repository URLs/paths are not yet identified in current project authority. |
| upstreamSourceMirrorDisposition | `PENDING_SOURCE_IDENTIFICATION`; do not clone, fetch, or treat any prior derived package as current upstream authority. |
| enumerationManifestPlan | After the operator identifies the source set, pin each immutable upstream commit and enumerate with hidden/no-ignore coverage into a per-repository manifest. |
| perFileTerminalLedgerPlan | Reconcile every enumerated file to one terminal status: `READ`, `ADAPTED`, `DEFERRED`, `REJECTED`, `NO_NEW_VALUE`, or `BLOCKED_UNREADABLE`. |
| ownerOverlapRoute | Compare value against existing CVF/project owner surfaces before opening any new implementation or governance owner. |
| valueDispositionRoute | Classify each item as absorb, adapt, defer, reject, block, or no-new-value; preserve package/runtime/checker candidates through the governed conditional-reopen route. |
| claimBoundary | Intake readiness only; no source corpus was enumerated, read, absorbed, imported, executed, or promoted. |

## Next Allowed Move

Obtain the exact repository URL/path set and intended absorption outcome from
the operator. Then open a bounded source-intake/corpus receipt before any
semantic absorption. Network clone/fetch, external-agent delivery, code import,
product mutation, provider/live execution, deployment, and production remain
unauthorized until their applicable gates are explicitly opened.

## Retained Closures

P4-E and Phase 4 remain `FREEZE / CLOSED_BOUNDED`. The ADIF-0057 inheritance
refresh remains closed at commits `d64530f` and `e7815c3`; reopening absorption
does not reopen either closure.

## Parked

Phase 5, governed-catalog schema migration, and XR1 debt remain parked unless
the operator selects one separately.
