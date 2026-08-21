# INTAKE — P4-A2 Governed RAG

- Tranche: `P4A2-GOVERNED-RAG-2026-08-21`
- Execution base: `4016fc6708844ecea1dedc4e76dfccf2ae314c9e`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE_REVIEW_PASS_OPEN_FOR_DESIGN`
- Role transition: `COMMIT_STEWARD → ORCHESTRATOR → INTAKE_AUTHOR → REVIEWER → ORCHESTRATOR`
- Provider/network/product-API/install/database/deployment effects: `0/0/0/0/0/0`
- Commit/push authority: `NONE/NONE`

## Operator request

The operator explicitly opened `P4A2-GOVERNED-RAG-2026-08-21`, required the
control chain to begin at INTAKE, fixed the risk ceiling at R2, required a
provider-neutral design, prohibited deployment and push, and withheld BUILD
authority until an independent authorization review passes.

This artifact captures request, evidence, dependency, external-effect and
claim boundaries only. It grants no DESIGN, SPEC, WORK_ORDER or BUILD action.

## Roadmap position and parent truth

P4-A2 is the second closed-loop AI milestone after three reviewed foundations:

1. P3-C `retrieval-contracts` owns strict source/content/chunk/lifecycle/
   retention/provenance identities but performs no retrieval or authorization.
2. P4-A1 `governed-retrieval` is `CLOSED_BOUNDED`: identity, permission and
   assignment precede local deterministic lexical retrieval; citations,
   evidence projections, context budgets and ephemeral receipts are bounded.
3. P4-A `ai-gateway` is `CLOSED_BOUNDED`: `AIGateway.execute` is the sole
   provider dispatch point and invokes the real data-scope, budget and
   termination gates before at most one provider attempt.

Phase 4 is `PARTIAL (1/8)`. Closing P4-A2 would advance only the governed-RAG
milestone; it would not close P4-B, P4-A3, application APIs/UI, durable audit,
deployment or production readiness.

## Current implementation truth

| Fact | Evidence | P4-A2 consequence |
|---|---|---|
| P4-A1 admits positive evidence only for `PROJECT_KNOWLEDGE_LOCAL_V1`; both operational corpora remain dependency-blocked. | `packages/governed-retrieval/README.md`; P4-A1 FREEZE closure | P4-A2 cannot claim operational-record RAG or silently enable blocked corpora. |
| `EvidenceAvailableV1` carries projections plus `FutureContextHandoffV1`; every negative retrieval result structurally omits both. | `governed_retrieval.result_models` | Only the positive variant may enter any future generation pipeline. |
| P4-A1 handoff facts remain `minimization_evidence_status=NOT_PROVEN`, `placement_enforcement_status=NOT_EVALUATED`, `runtime_caller_status=NO_LOAD_BEARING_CALLER`. | `governed_retrieval.receipt_models` | P4-A2 must not relabel these facts or send INTERNAL evidence externally without a separately verifiable minimization/admission step. |
| Workspace application code calls governed retrieval, but no application code composes its result into `AIGateway`. | repository symbol scan | P4-A2 must name a single composition owner without claiming a public API/UI route. |
| P4-A gateway rejects INTERNAL external placement without positive minimization and validates structured JSON, but it does not validate citation membership against a granted evidence set. | P4-A SPEC/source/final review | P4-A2 owns the pre-gateway context builder and post-gateway grounded-answer validator; provider dispatch remains gateway-owned. |
| No vector/embedding/reranking dependency or index owner exists in project source. | dependency/source scan | DESIGN must select and bound the semantic substrate, lifecycle and external effects; INTAKE cannot assume a vector database or provider embedding API. |
| Roadmap P4-A2 requires hybrid retrieval, reranking, prompt-injection isolation, context lineage, stale-index detection and output citation validation. | `docs/implementation/EXECUTION_ROADMAP.md` | DESIGN must cover all six behaviors or explicitly narrow the milestone with operator approval. |
| `LPCI1-REF` remains `PLANNED_EXTERNAL_REFERENCE_LANE_REQUIRES_SEPARATE_CVF_AUTHORITY` and is an entry gate before P4-A2 DESIGN. | `docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md` | INTAKE may proceed; DESIGN may not open until reviewed LPCI1-REF evidence exists or the operator explicitly approves a P4-A2-specific alternative plan. |
| The P4-A project-native alternative explicitly replaced the reference gate for P4-A only and states that it does not apply to P4-A2. | same coordination record, lines 51–62 | P4-A closure cannot be treated as an implicit P4-A2 waiver. |

## Problem statement

The project has bounded evidence retrieval and a governed provider gateway but
no reviewed component that binds them into a grounded answer. A naive bridge
could bypass governance by:

- passing a P4-A1 negative result or stale evidence to a provider;
- treating INTERNAL/LOCAL_ONLY evidence as externally eligible without
  minimization and placement proof;
- sending embeddings through a second provider call path outside
  `AIGateway.execute`;
- accepting prompt instructions embedded in retrieved evidence;
- letting vector/index results widen the server-authorized corpus;
- using stale embeddings after source/content/version/corpus-policy drift;
- accepting model citations not present in the granted evidence set;
- returning uncited prose or persisting generated output as operational truth;
- hiding provider attempts, reranking behavior, context lineage or omissions.

## Proposed bounded objective

Prepare a provider-neutral P4-A2 design for one governed-RAG composition that:

1. accepts only a validated non-empty P4-A1 `EvidenceAvailableV1` result;
2. preserves P4-A1 authorization, corpus, source, citation and revalidation
   identities without allowing semantic retrieval to widen scope;
3. defines deterministic hybrid score fusion and reranking with stable ties,
   explicit ceilings and recorded component scores;
4. binds every semantic/index entry to corpus id, source/content/chunk hashes,
   source version, embedding contract/version and index-build identity;
5. fails closed on stale, missing, incompatible or partially rebuilt index
   state and falls back only to an explicitly reviewed lexical-only outcome;
6. treats retrieved text as untrusted evidence data, isolates it from system
   instructions and records prompt-injection detection/omission outcomes;
7. produces independently verifiable minimization evidence before any INTERNAL
   evidence can reach the external-placement gate;
8. routes every provider operation through the one reviewed gateway boundary,
   or parks semantic behavior whose operation cannot fit that invariant;
9. requests a strict structured answer containing citation ids and validates
   every returned citation as a member of the exact granted evidence set;
10. rejects uncited claims, unknown citations, altered evidence lineage,
    invalid schema and provider identity mismatch without turning output into
    canonical operational truth;
11. emits sanitized retrieval/context/provider/answer receipts whose hashes
    bind the full lineage without prompt, evidence body, output body or secret;
12. proves every denial/no-evidence/stale-index/injection/budget/termination
    branch causes zero provider attempts and permits at most one authorized
    answer-generation attempt in a later live-evidence run.

## Hard boundaries

This INTAKE authorizes no implementation. P4-A2 must not yet:

- create DESIGN, SPEC, WORK_ORDER, source, test, index, migration or runtime
  artifacts;
- install a vector database, embedding/reranking/model package or provider SDK;
- call an embedding, reranking, generation or other provider/network API;
- mutate the P4-A1/P4-A reviewed contracts or create a second dispatch path;
- enable operational corpora whose digest/retention owners remain blocked;
- expose an API/UI route, persist vectors/answers/audit, deploy, publish or push;
- modify the hidden CVF Core or execute/claim the external `LPCI1-REF` lane;
- use mock output as proof of RAG/governance behavior;
- claim grounded truth, production readiness, complete Phase 4 or P4-B closure.

## Reference entry gate — resolved for P4-A2 DESIGN

Checkpoint `P4A2-INTAKE-D1-REFERENCE-PLAN` has two valid resolutions:

1. independently accepted `LPCI1-REF` evidence from its separately authorized
   owning-CVF lane; or
2. a fresh operator-approved P4-A2-specific project-native alternative that
   enumerates the local reviewed sources replacing each required reference
   property and explicitly retains the no-import/no-runtime-dependency rule.

Current disposition: `PROJECT_NATIVE_ALTERNATIVE_ACCEPTED_FOR_P4A2_DESIGN`.
On 2026-08-21 the operator explicitly selected option 2: accepted P4-A1/P4-A
contracts, receipts and reviews plus public CVF Core read-only guidance replace
`LPCI1-REF` for P4-A2 DESIGN. No external code, runtime, configuration,
database, secret or deployment may be imported. The independently reviewed
mapping is recorded in
`docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md`.
`LPCI1-REF` itself remains parked under separate authority.

## Decisions required before DESIGN may close

1. Reference-plan resolution and evidence mapping.
2. Composition owner and dependency direction between workspace application,
   governed retrieval and AI gateway; no cyclic or provider-specific import.
3. Semantic substrate: local deterministic model, injected embedding service,
   or a deliberately narrower non-semantic first slice.
4. Whether embedding/reranking are provider operations and how the gateway's
   sole-dispatch invariant applies to them.
5. Index ownership, build/rebuild transaction, persistence class, versioning,
   source deletion/correction propagation and stale-index fail-closed rules.
6. Hybrid score normalization, fusion, reranking, stable ties, duplicate rules,
   budgets and lexical-only fallback semantics.
7. Exact minimization evidence owner and verification contract for INTERNAL
   Project Knowledge before external placement.
8. Prompt construction and injection isolation: instruction/data separation,
   delimiters, allowed transformations and safe failure outcomes.
9. Strict answer schema, claim granularity, citation membership, completeness,
   abstention and output-validation behavior.
10. End-to-end lineage/hash contract across query, corpus, index, evidence set,
    context, schema, model response and validated answer.
11. Attempt, timeout, cancellation, cost, termination and fallback accounting,
    including zero-call negative branches and no retry.
12. Live-evidence class, credential/network endpoint, installation effects,
    exact path ceiling, rollback/preservation and commit ownership.

## Cheap-alternative inventory

| Alternative | INTAKE disposition | Reason |
|---|---|---|
| Compose P4-A1 positive evidence directly into P4-A with citation membership validation. | `EVALUATE_BASELINE` | Reuses reviewed owners and exposes the minimum grounded-answer seam, but alone does not satisfy semantic/hybrid retrieval. |
| Deterministic lexical + local deterministic feature vectors and weighted fusion. | `EVALUATE` | Provider-neutral and testable; DESIGN must prove it is materially semantic enough for the P4-A2 claim. |
| Injected embedding protocol implemented behind the same governed dispatch boundary. | `EVALUATE_WITH_EXTERNAL_EFFECTS` | Preserves provider neutrality but may require expanding the gateway contract and live-call accounting. |
| External vector database or managed embedding service. | `DEFER_BY_DEFAULT` | Adds network, persistence, credentials, deletion/rebuild and deployment boundaries before the core contract is settled. |
| LLM reranker or a second provider call. | `REJECT_BY_DEFAULT` | Conflicts with the at-most-one answer-generation attempt and increases cost/termination/evidence complexity. |
| Client-side RAG or direct provider SDK call. | `REJECT` | Bypasses authorization, data-scope, gateway and receipt ownership. |

## INTAKE-stage write ceiling

This INTAKE authoring/synchronization pass may create or modify exactly:

1. `docs/decisions/INTAKE_2026-08-21_P4A2_GOVERNED_RAG.md`
2. `SESSION/handoffs/P4A2_GOVERNED_RAG_2026-08-21.md`
3. `SESSION/ACTIVE_SESSION_STATE.json`
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
5. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
6. `SESSION/SESSION_MEMORY.md`
7. `docs/implementation/EXECUTION_ROADMAP.md`
8. `IMPLEMENTATION_STATUS.json`
9. `knowledge/PROJECT_CONTEXT.md`
10. `knowledge/manifest.json`

No commit or push is authorized by this INTAKE pass.

### Consolidated-review amendment ceiling

The independent review adds only the review artifact and updates the existing
coordination record. The resulting INTAKE plus review changed set is exactly
the original ten paths above plus:

11. `docs/decisions/P4A2_GOVERNED_RAG_INTAKE_REVIEW_2026-08-21.md`
12. `docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md`

## Acceptance criteria for INTAKE review

INTAKE may pass only if review confirms:

- the operator's R2/provider-neutral/no-deploy/no-push/no-BUILD-before-review
  boundary is preserved;
- parent P3-C, P4-A1 and P4-A claims are accurate and not widened;
- P4-A2 consumes only positive, current, authorized evidence;
- operational corpora and canonical truth remain blocked/unchanged;
- semantic/index/reranking owners and external effects remain decisions, not
  silently selected implementations;
- minimization and placement are separate, positive, verifiable preconditions;
- every provider operation remains subordinate to the sole gateway boundary;
- prompt injection and output citation membership are enforcement contracts,
  not prompt-only aspirations;
- the reference entry gate is not silently waived;
- all twelve DESIGN decisions and failure/receipt/live-proof boundaries are
  explicit; and
- no later control-chain authority is inferred.

## Next governed move

INTAKE review passed and `P4A2-INTAKE-D1-REFERENCE-PLAN` is resolved for
P4-A2 DESIGN only. The next allowed move is DESIGN authoring under the approved
project-native reference mapping. No SPEC, WORK_ORDER, BUILD, provider call,
install, commit, push or deployment is authorized.
