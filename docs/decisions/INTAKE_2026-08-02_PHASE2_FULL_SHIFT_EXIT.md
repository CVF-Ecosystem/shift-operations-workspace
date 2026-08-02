# INTAKE — Phase 2 Full-Shift Exit Gate

- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Phase: `INTAKE`
- Risk: `R2`
- Requested by: operator continuation after P2-D C4
- Source baseline: `e1ac14beaf426ded1b763ff3373b238a065c4694`
- Status: `READY_FOR_DESIGN`

## Intent

Close the remaining Phase 2 dependency by proving one coherent governed shift
through `start → updates → tasks → handover → report → freeze` while AI and
external channels are not part of operational execution. The proof must use
the already-built P2-A/P2-R/P2-C/P2-D surfaces, real authenticated routes,
durable persistence and the existing CVF gates; it must not invent a parallel
workflow or repair unrelated product behavior silently.

## Current truth

- P2-R, P2-C and P2-D are independently `CLOSED_BOUNDED`.
- The React console exposes shift creation/close, events, tasks, handovers,
  Report submission, supervisor approval and freeze.
- Backend services enforce identity, active assignment, permission, CAS,
  approval, handover/report freeze prerequisites and actor-bound audit.
- Existing tests prove the verticals separately, but no single evidence run
  proves they compose into one shift from start through freeze.
- Phase 2 therefore remains `IN PROGRESS`; the post-Phase-2 queue is parked.

## Required outcome

Produce independent, reproducible evidence that one scheduled 12-hour shift:

1. is created by an authenticated assigned operator;
2. receives a confirmed operational update and a task transition;
3. exercises P2-D bounded offline replay and polling inside that lifecycle;
4. creates a handover with a non-empty persisted open-work snapshot, distinct
   reviewer and destination-assigned receiver acknowledgement;
5. closes, generates/submits a current END_SHIFT Report, obtains a distinct
   durable approval receipt, approves the Report and freezes atomically;
6. retains the expected final records and actor-bound audits after reconnect;
7. keeps provider calls at zero through the governance runner's own refusal
   gates, validates the separately produced browser evidence, then makes
   exactly one sanitized real-provider evidence call.

## Boundaries

- Evidence/integration tranche only: no new product behavior, backend API,
  domain model, migration, dependency, lockfile, policy or CI change.
- The 12-hour assertion is the persisted scheduled interval and complete
  lifecycle, not a 12-hour wall-clock soak or performance/reliability claim.
- No production/managed PostgreSQL, HA, load, backup/restore, tenant/provider
  `data_scope`, external channel, AI-generated operational truth or Phase 3+
  capability claim.
- Mock mode may support pure unit structure only; it cannot satisfy browser,
  PostgreSQL, audit or governance evidence.
- Phase 2 cannot close until BUILD is independently reviewed/pushed and a
  separate FREEZE truth-sync confirms no stale/open residue.

## Authority and stop conditions

This INTAKE authorizes DESIGN/SPEC/WORK_ORDER authoring only. BUILD/provider
calls remain prohibited until independent authorization `REVIEW_PASS`, pushed
authorization artifacts, a separate pre-BUILD continuity checkpoint and fresh
G6. Stop on source/continuity drift, an API or UI capability gap, an
unavoidable production-source edit, incomplete cleanup, unsanitized output or
any attempt to treat prior P2-D/provider receipts as fresh exit-gate evidence.
