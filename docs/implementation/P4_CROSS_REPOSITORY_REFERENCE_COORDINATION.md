# P4 Cross-Repository Reference Coordination

- Record class: `PLANNING_POINTER`
- Date: `2026-08-10`
- Status: `P4A_AND_P4A2_PROJECT_NATIVE_ALTERNATIVES_APPROVED_LPCI1_REF_REMAINS_PARKED`
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

## P4-A alternative disposition — 2026-08-20

The operator opened P4-A and delegated the bounded reference-plan decision to
the acting project orchestrator. For `P4A-AI-GATEWAY-2026-08-20`, the
orchestrator approved a project-native plan based only on the reviewed local
P4-A1 contracts/receipts, the pinned public CVF Core as read-only governance
guidance, and existing secret-safe live-evidence patterns. This explicitly
replaces the `LPCI1-REF` entry gate for P4-A only.

`LPCI1-REF` itself remains unexecuted and requires separate CVF authority. The
replacement imports no external repository code, truth, configuration,
deployment, database, or secret, and it does not apply to P4-A2.

## P4-A2 alternative disposition — 2026-08-21

The operator separately approved a P4-A2-specific project-native alternative
for `P4A2-GOVERNED-RAG-2026-08-21`. For P4-A2 DESIGN only, the accepted local
P4-A1/P4-A contracts, receipts and independent reviews plus the pinned public
CVF Core's read-only guidance replace the `LPCI1-REF` entry gate. The mapping
is bounded as follows:

| Required reference property | Approved project-native source |
|---|---|
| Clean retrieval mechanics and authorization-before-read boundaries | Reviewed P4-A1 contracts, source tests, receipts and FREEZE closure |
| Structured output and exact citation-membership validation | P4-A strict-schema boundary plus the P4-A2 INTAKE requirement to validate membership against the granted P4-A1 evidence set |
| Source/content/evidence/response hash semantics | P3-C/P4-A1 identity and receipt contracts plus P4-A request/response receipt bindings |
| No-valid-evidence and refusal paths with zero provider attempts | P4-A1 negative-result variants and P4-A zero-attempt refusal tests/live-evidence pattern |
| Safe errors, timeout, cancellation and provider-attempt accounting | Reviewed P4-A gateway contracts, tests, receipts and completion review |
| Real-provider governance proof | P4-A replacement receipt is a pattern only; any later P4-A2 governance claim requires a fresh P4-A2 real-provider proof |
| Bounded public claim | P4-A1 and P4-A closure claim boundaries; neither is widened into a RAG, application, persistence, deployment or production claim |
| Provider-neutral RAG guidance | Local provider-neutral contracts plus read-only public Core retrieval-boundary, RAG-skill and hierarchical-governance guidance |

No public-Core or external code, runtime, configuration, database, secret or
deployment artifact may be imported. Public-Core material is design guidance,
not downstream implementation authority or source of runtime truth; any older
path-oriented examples must not weaken the project's reviewed corpus/source/
content/chunk/version/hash and citation identities. `LPCI1-REF` remains parked
and separately governed.

P4-A2 later completed BUILD, repaired review findings, received independent
final `REVIEW_PASS`, and reached `FREEZE / CLOSED_BOUNDED` with a fresh
P4-A2-specific live receipt. That closure does not execute, import or close
`LPCI1-REF`; the external lane remains parked under separate CVF authority.

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
