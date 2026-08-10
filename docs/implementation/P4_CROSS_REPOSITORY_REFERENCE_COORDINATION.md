# P4 Cross-Repository Reference Coordination

- Record class: `PLANNING_POINTER`
- Date: `2026-08-10`
- Status: `P4A1_CLOSED_BOUNDED_REFERENCE_LANE_PARKED`
- Owning project: `shift-operations-workspace`
- Runtime authority: `NONE`
- Provider/network authority: `NONE`

## Purpose

Coordinate reference evidence that is produced in another governed repository
without making that repository a runtime dependency or widening the current
P4-A1 tranche.

## LPCI1-REF lane

| Field | Disposition |
|---|---|
| Lane id | `LPCI1-REF` |
| Owning repository | CVF repository under its own governed authority chain |
| Status | `PLANNED_EXTERNAL_REFERENCE_LANE_REQUIRES_SEPARATE_CVF_AUTHORITY` |
| P4-A1 dependency | `NON_BLOCKING` |
| P4-A/P4-A2 dependency | `ENTRY_GATE_BEFORE_DESIGN` |
| Downstream consumption | Reviewed provider-neutral reference contract and evidence packet only |
| Forbidden coupling | Code import, deployment dependency, shared secret/config, direct database dependency or promotion to project source of truth |

## Required LPCI1-REF completion evidence

The owning CVF lane must independently govern and verify:

1. clean LPCI1 focused governance tests with stale fixtures repaired;
2. structured answer output plus citation membership validation against the
   exact granted evidence set;
3. source, content, evidence and model-response hash semantics;
4. no-valid-evidence proof with zero provider attempts;
5. no-provider, safe-error, timeout and provider-attempt accounting behavior;
6. fresh real-provider proof and hosted smoke on the accepted LPCI1 HEAD;
7. a bounded public-only claim that excludes complete RAG, restricted-data
   authorization, durable persistence and production deployment;
8. a provider-neutral reference contract/evidence packet suitable for review
   by downstream P4-A/P4-A2 DESIGN.

## Sequencing

P4-A1 deterministic provider-free retrieval is now `CLOSED_BOUNDED` without
LPCI1-REF closure. P4-A and P4-A2 DESIGN remain parked and must not open until
accepted LPCI1-REF evidence is available or a fresh operator-approved
alternative reference plan explicitly replaces the entry gate.

## Repository boundary

This downstream coordination record does not authorize changes in the CVF
provenance repository, public-core repository or LPCI1 Web. The owning CVF lane
must open its own governed intake, source verification, work order, review,
live-proof budget and closure evidence.

## Claim boundary

This file records sequencing and evidence expectations plus the bounded P4-A1
coordination disposition. It does not prove LPCI1-REF exists or passes, open
P4-A/P4-A2, make external code a dependency, or prove provider, LLM-answer,
RAG, durable persistence/audit, deployment or production behavior.
