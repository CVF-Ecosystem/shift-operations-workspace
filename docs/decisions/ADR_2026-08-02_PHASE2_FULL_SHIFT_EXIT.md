# ADR — Phase 2 Full-Shift Exit Evidence Architecture

- ADR id: `ADR-P2-FULL-SHIFT-EXIT-001`
- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Phase: `DESIGN`
- Risk: `R2`
- Source baseline: `e1ac14beaf426ded1b763ff3373b238a065c4694`
- Decision: `PROPOSED_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`

## Context

Phase 2's remaining gate is composition, not another feature vertical. Existing
receipts prove each component separately, but separate green tests do not prove
that identity, assignment, CAS, offline replay, polling, handover snapshot,
Report approval and atomic freeze remain coherent in one record lineage.

## Decision

Use a three-layer evidence design over the same logical scenario.

### 1. Real browser and real FastAPI

A dedicated Playwright spec drives all user-visible operational actions through
the rendered React UI. It uses three authenticated browser principals: operator,
source supervisor and distinct receiver/receipt approver. Direct API reads may
observe identifiers and final state, but may not replace an action the UI
already exposes.

The scenario creates source/destination shifts with an exact 12-hour scheduled
window, appends an event, creates a task, stages its transition while
pre-dispatch offline, reconnects and observes the committed transition, then
keeps the operator page open while `sup1` confirms that event in a second page;
the operator's confirmed timeline must update through polling without reload.
It creates/reviews/
acknowledges a handover whose snapshot contains that task, closes the source
shift, generates/submits/receipts/approves the current END_SHIFT Report and
freezes the shift. Queue storage must be empty at completion.

The supervisor-only staffing control plane is rendered independently of
ordinary assignment-scoped operational selection. Therefore `sup1` uses the
rendered staffing UI, while initially unassigned, to assign `sup1` and `sup2`
to both source and destination shifts. No assignment bootstrap API call or
other positive-action API substitution is permitted.

### 2. Disposable PostgreSQL durability

A dedicated opt-in live test runs the full authenticated FastAPI/JWT chain on
the existing disposable PostgreSQL 16 runner. After engine disposal/reconnect
it verifies the scheduled interval, final FROZEN shift, frozen current Report,
ACKNOWLEDGED handover and exact open-work snapshot, task/event state, approval
binding and required actor-bound audit actions. It joins the pinned live-suite
runner; no second container orchestrator is created.

### 3. Governance evidence

A dedicated runner executes its API/governance refusal cases and one genuine
integrated shift before provider admission. Its own counter must observe zero
provider calls for anonymous, unassigned, stale-CAS, premature-freeze and
missing-receipt cases. Transport ambiguity is owned by the separate real-browser
run: it proves one request, no queue insertion/automatic retry, visible
`outcome_unknown`, then reconciles the authoritative final state without
assuming the mutation did not commit. The browser wrapper writes a sanitized
temporary JSON result; the governance runner validates and references that
result without claiming its in-process counter observed the browser process.
Only after durable final-state/audit verification and exact-parent rehearsal may
the runner make exactly one real provider call and emit a sanitized receipt.
The provider response is evidence metadata only and never operational truth.

## Alternatives rejected

- **Aggregate prior receipts:** rejected because it does not prove composition
  or a single lineage.
- **Service-only test:** rejected because it bypasses JWT, route, UI and
  transport boundaries.
- **Browser-only proof:** rejected because browser-visible state cannot prove
  durable audit/approval persistence after reconnect.
- **Real 12-hour wait:** rejected; reliability/soak belongs to later hardening.
  The exit gate proves a complete lifecycle for a persisted 12-hour schedule.
- **New orchestration/product endpoint:** rejected because the product already
  exposes the required bounded capabilities.

## Failure and claim boundary

Any discovered product/API/UI gap stops BUILD for a separately reviewed
amendment; the evidence tranche may not absorb the repair. Passing proves only
the integrated Phase 2 functional lifecycle on real browser/FastAPI, SQLite and
disposable local PostgreSQL 16 with one real provider-backed governance receipt.
It does not prove wall-clock endurance, production readiness, external channels,
AI operation, Phase 3, or the parked post-Phase-2 sequence.
