# Agent Handoff - P4-A1 Governed Retrieval INTAKE

- Date: `2026-08-10`
- Repository: `shift-operations-workspace`
- Branch: `main`
- Intake execution base: `d878001`
- Current phase: `INTAKE`
- Current mode: `p4a1_governed_retrieval_intake_review_pending`
- Active role: `INDEPENDENT_INTAKE_REVIEWER`
- Risk: `R2`
- Provider/product-API/POST calls in this intake: `0/0/0`
- Runtime/database/source changes: `NONE`

## Active authority

The operator accepted the LPCI1-inspired project roadmap and authorized the
next governed step. The only active artifact is:

`docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`

Frozen SHA-256:

`7c32cd312ad4d889aa5039fbc32c032ee4312e0976224411cac106145b1ffde7`

Status is `OPEN_FOR_INTAKE_REVIEW`. This handoff grants independent INTAKE
review only. No DESIGN, SPEC, WORK_ORDER, BUILD, provider, network, database,
product API or runtime authority exists.

## Canonical source chain

1. `AGENTS.md`
2. `.cvf/manifest.json`
3. `.cvf/policy.json`
4. `SESSION/ACTIVE_SESSION_STATE.json`
5. this active handoff
6. `docs/implementation/EXECUTION_ROADMAP.md`, P4-A1/P4-A2
7. P3-C closure and reviewed BUILD `4cc0691`
8. the frozen P4-A1 INTAKE above
9. `docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md`

The operator-supplied LPCI1 sequence is design input, not canonical runtime
source. Do not cite provider-specific memory or a private provenance copy as
project authority.

## Bound architecture direction

P4-A1 must evaluate this order:

`query -> authenticate -> authorize permitted scope -> resolve a corpus only
within that scope -> deterministic retrieval/filter -> use-time revalidation
-> bounded evidence receipt`

Key invariants:

- authorization precedes every protected read, count, match and rank;
- corpus selection can narrow but never widen server-authorized scope;
- P3-C `RetrievalReadyV1` remains the evidence/provenance envelope;
- canonical records stay blocked while source digest owners are missing;
- citations use chunk/content/source hashes and source version, not path alone;
- no evidence establishes a future zero-provider-attempt invariant;
- INTERNAL knowledge is not relabeled PUBLIC or treated as external-AI
  eligible;
- FastAPI/application services own governance; React remains a thin client;
- provider generation and output citation validation remain P4-A/P4-A2 work.

## LPCI1-REF coordination gate

`LPCI1-REF` is a separate CVF-repository lane requiring its own governed
authority. It is non-blocking for P4-A1 and an entry gate before P4-A/P4-A2
DESIGN. Downstream may consume only its reviewed provider-neutral reference
contract/evidence packet and must not import LPCI1 Web as a runtime dependency.

## P3-B dependency requirement

The INTAKE explicitly maps, but does not close, the remaining P3-B controls:

- `data_scope`: future context placement and minimization decision;
- `cost`: deterministic context facts now, provider budget later;
- `termination`: bounded local retrieval now, provider execution later.

No future agent may claim these controls are load-bearing for AI until a
separately authorized real caller and fresh live governance proof exist.

## Parked work

- P4-A1 DESIGN and all implementation;
- source digest owner implementation;
- P4-A gateway/provider execution;
- P4-A2 RAG, embeddings, hybrid retrieval, reranking and output citation
  validation;
- persistence, vector/index infrastructure and background sync;
- application memory and governed learning;
- durable AI-answer audit and production deployment;
- CVF core pin reconciliation.
- LPCI1-REF implementation and closure in its owning repository.

## Workspace synchronization note

The sibling CVF core was fast-forwarded to
`2103a38fda01ee827e9fc6c3be38a824fa5d54ad`. Workspace doctor returned 24
passes and one warning because `.cvf/manifest.json` still pins
`9b039ea6b532176d92536338659bd346f019cd5a`. This product intake does not
repair the pin. Keep the mismatch visible and route any repair through a
separate governed core-pin batch.

## Required independent review

The reviewer must verify the intake against current project source and return
exactly one disposition:

- `INTAKE_REVIEW_PASS`
- `INTAKE_REVIEW_CHANGES_REQUIRED`
- `INTAKE_BLOCKED_SOURCE_OR_OWNER`

Review all foreseeable boundary/source findings in one consolidated pass. The
reviewer may run local read-only checks, but may not edit the design, implement,
call providers/network/product APIs, modify a database, stage, commit or push.

## Next allowed move

Obtain one consolidated independent review of the frozen P4-A1 INTAKE. Only
`INTAKE_REVIEW_PASS` may transfer its twelve-decision packet to
`DESIGN_AUTHOR`. No later-phase authority carries forward.

## Claim boundary

This handoff proves only that a bounded P4-A1 INTAKE artifact exists and is
ready for independent review. It does not prove retrieval, source admission,
authorization enforcement, data-scope enforcement, provider behavior, output
grounding, durable audit, RAG, vector/index, persistence or production
readiness.
