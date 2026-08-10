# INTAKE - P4-A1 Governed Retrieval Foundation

- Tranche: `P4-A1-GOVERNED-RETRIEVAL-2026-08-10`
- Execution base: `d878001`
- Parent closure: P3-C retrieval-ready contract `FREEZE / CLOSED_BOUNDED`
  at reviewed BUILD `4cc0691`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INTAKE_REVIEW`
- Active roles: `ORCHESTRATOR`, `INTAKE_AUTHOR`
- Provider/product-API/POST calls: `0/0/0`
- Runtime, database and source changes: `NONE`
- Operator direction: continue the accepted LPCI1-inspired roadmap as a
  project-native governed retrieval use case and preserve one shared artifact
  for later agents

## Request and roadmap position

The operator accepted the architecture assessment and instructed the project
to proceed through the proposed roadmap. The canonical project roadmap already
names P4-A1 as the next bounded item: deterministic filtered search over
confirmed records, authorization and data-scope before retrieval, mandatory
citation/source version, and a context budget. Lexical or structured retrieval
is sufficient before vector search.

This INTAKE converts that direction into one provider-neutral, project-native
request boundary. It does not import the CVF provenance workspace's LPCI1 Web
route, promote an external implementation to project authority, or grant any
later control-chain phase.

The LPCI1 sequence supplied by the operator is design input only:

`query -> corpus -> filter -> authorization -> evidence -> LLM -> cited answer -> audit`

P4-A1 must correct the security ordering before DESIGN:

`query -> authenticate -> authorize permitted scope -> resolve a corpus only
within that scope -> deterministic retrieval/filter -> use-time revalidation
-> bounded evidence receipt`

Provider generation, output citation validation and durable AI-answer audit are
later phases and are not part of this INTAKE.

## Current implementation truth

| Current fact | Verified source | Consequence for P4-A1 |
|---|---|---|
| P4-A1 requires deterministic filtered search, authorization plus data-scope before retrieval, citations/source versions and a context budget. | `docs/implementation/EXECUTION_ROADMAP.md:449-453` | DESIGN must preserve all five controls and may begin without vector search. |
| P4-A2 separately owns hybrid retrieval, reranking, prompt-injection isolation, stale-index detection and output citation validation. | `docs/implementation/EXECUTION_ROADMAP.md:454-457` | P4-A1 must not claim RAG or LLM output grounding. |
| P3-C is closed at BUILD `4cc0691`; its package performs no retrieval, persistence, authorization, provider or network work. | `docs/implementation/EXECUTION_ROADMAP.md:428-430`; `packages/retrieval-contracts/README.md:3-8` | P4-A1 must add a caller without weakening the P3-C contract boundary. |
| `RetrievalReadyV1` already carries redacted normalized text, content digest, chunk id, source reference, scope, lifecycle, retention, provenance and data-scope evidence. | `packages/retrieval-contracts/src/retrieval_contracts/contract_models.py:210-223` | Reuse this evidence envelope; do not create a weaker path-only citation model. |
| P3-C data-scope evidence is explicitly `NOT_EVALUATED`, `NOT_PROVEN` and `NO_LOAD_BEARING_CALLER`. | `packages/retrieval-contracts/src/retrieval_contracts/contract_models.py:161-165` | P4-A1 must dependency-map P3-B and cannot treat the carried evidence as authorization. |
| Canonical operational records currently fail closed with `SOURCE_DIGEST_OWNER_MISSING`. | `packages/retrieval-contracts/src/retrieval_contracts/constructor.py:179-183` | Confirmed ledger records cannot be admitted until a separately reviewed source digest owner exists. |
| The backend already has a canonical active-assignment check for a principal and shift. | `apps/workspace-api/src/workspace_api/application/assignment_scope.py:23-35` | Prefer this scope owner instead of inventing retrieval-specific identity or tenant semantics. |
| Existing browser read helpers authenticate, require an active assignment and then return bounded per-shift lists for Message, Task and CustomerRequest. | `apps/workspace-api/src/workspace_api/application/browser_reads.py:53-78` | Reuse the authorization order and bounded-read pattern; do not infer that every record type is already covered. |
| INTERNAL data requires minimization and placement evaluation before outbound AI use. | `packages/cvf-runtime/src/cvf_runtime/data_scope.py:3-15`, `:48-64` | Retrieval may remain local, but any future provider handoff must call a load-bearing data-scope gate. |
| Cost and termination gates exist but require a real caller to become load-bearing. | `packages/cvf-runtime/src/cvf_runtime/budget.py:3-8`, `:26-59`; `packages/cvf-runtime/src/cvf_runtime/termination.py:3-6`, `:46-55` | P4-A1 must define the dependency interface but must not enable a provider call. |
| The AI gateway is only a provider-neutral contract/scaffold. | `packages/ai-gateway/contracts/provider_interface.py:5-22`; `packages/ai-gateway/README.md:1-3` | Do not bind P4-A1 to OpenAI, a Next.js route or a provider-specific environment variable. |
| The project knowledge pack is `INTERNAL` and allowed only for local governed agents and human operators, while remaining eligible for a local index. | `knowledge/manifest.json:4`, `:15-18`, `:43` | It may support local deterministic evaluation but is not automatically eligible for an external model. |
| All governance enforcement belongs in the FastAPI backend, not the React frontend. | `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md:43-50` | Any later web surface is a thin client over a governed backend API. |
| The API already emits a request correlation id and the Ledger exposes append-only audit operations. | `apps/workspace-api/src/workspace_api/middleware/request_id.py:5-9`; `packages/operations-ledger/src/operations_ledger/ledger.py:215-217` | DESIGN must decide whether a retrieval receipt reuses or extends these owners without turning an AI answer into canonical operational truth. |

## Problem statement

The project can create strict retrieval-ready values but has no governed caller
that can answer a query by selecting only current, authorized and bounded
evidence. A naive caller could:

- search before authorization and leak cross-shift existence or ranking;
- let a client-provided corpus selector widen the caller's permitted scope;
- bypass active-assignment checks or invent tenant semantics;
- retrieve a stale, corrected, expired or erased source;
- treat `DataScopeEvidenceV1` as proof even though it says not evaluated;
- cite only a path and lose source version, digest and revalidation lineage;
- send INTERNAL data to a provider before minimization and placement approval;
- call an LLM with no valid evidence;
- write provider output into the Operations Ledger as if it were confirmed truth.

## Proposed bounded objective

Design a local, deterministic, provider-free P4-A1 retrieval foundation that:

1. accepts a bounded query and a corpus selector that can only narrow the
   authenticated principal's already-authorized scope;
2. authenticates and evaluates current active-assignment scope before reading,
   matching, counting or ranking protected records;
3. admits only eligible P3-C `RetrievalReadyV1` evidence and preserves typed
   non-admission reasons;
4. performs deterministic lexical and structured filtering with stable
   ordering, explicit limits and no semantic model call;
5. revalidates source digest, version, lifecycle, correction, retention and
   scope at use time before returning evidence;
6. enforces a bounded evidence projection and context budget without sending
   the projection to a provider;
7. returns citations identified by chunk id, content digest, source digest,
   source version and safe source reference;
8. emits a request-correlated retrieval receipt that distinguishes admitted,
   filtered, denied, stale, unavailable and no-evidence outcomes;
9. returns a typed no-evidence outcome and establishes the future invariant
   that no evidence means zero provider attempts;
10. leaves provider generation, structured answer validation, durable AI audit,
    RAG, vector indexing and external deployment parked.

## LPCI1 pattern disposition

| LPCI1 pattern | P4-A1 disposition | Project-native adaptation |
|---|---|---|
| Public-only admission | `ADAPT` | Use authenticated active-assignment and project data-scope rules; never relabel INTERNAL material as PUBLIC. |
| Corpus selection | `ADAPT` | Selector narrows a server-resolved authorized corpus; it cannot supply arbitrary paths or widen scope. |
| Deterministic filtering | `REUSE_CONCEPT` | Implement lexical/structured filtering over typed P3-C evidence with stable ordering. |
| Bounded snippets/context | `REUSE_AND_STRENGTHEN` | Use P3-C redacted normalized text plus explicit record, code-point and byte/token budgets. |
| No evidence, no provider call | `RETAIN_AS_INVARIANT` | P4-A1 proves the no-evidence result locally; a later P4-A/P4-A2 caller must prove zero provider attempts. |
| No key and safe provider errors | `DEFER_TO_P4A` | Provider lifecycle is outside P4-A1. |
| Response hash and audit correlation | `ADAPT_AND_STRENGTHEN` | Preserve request correlation and use P3-C content/source/chunk hashes; do not claim durable AI-answer audit. |
| Prompt-only evidence grounding | `REJECT_AS_SUFFICIENT` | Later generation requires structured output and citation membership validation; a prompt alone is not enforcement. |
| Next.js API implementation | `DO_NOT_IMPORT` | Governance remains in FastAPI/application services; React remains a thin HTTP client. |

## Cross-repository LPCI1-REF coordination lane

The operator separately authorized `LPCI1-REF` as a cross-repository reference
completion lane. It is not a P4-A1 implementation dependency, is not counted as
a Shift Operations Phase 4 milestone, and creates no authority to modify the
CVF provenance or public-core repository from this downstream tranche.

| Field | Disposition |
|---|---|
| Lane id | `LPCI1-REF` |
| Coordination record | `docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md` |
| Owning repository | CVF repository under a separate governed authority chain |
| Current downstream status | `PLANNED_EXTERNAL_REFERENCE_LANE_REQUIRES_SEPARATE_CVF_AUTHORITY` |
| P4-A1 dependency | `NON_BLOCKING` - deterministic provider-free retrieval may proceed after its own review chain |
| P4-A/P4-A2 dependency | `ENTRY_GATE` - accepted LPCI1-REF evidence must be reviewed before provider-generation or governed-RAG DESIGN begins |
| Runtime relationship | Reference and acceptance input only; never a code-level or deployment dependency |
| Source-authority boundary | Operator-approved coordination direction only until the owning CVF lane produces reviewed artifacts |

The separately governed LPCI1-REF lane must resolve at least:

1. stale LPCI1 governance-test fixtures and a clean focused regression result;
2. structured answer output and membership validation for every returned
   citation against the granted evidence set;
3. source, content, evidence and model-response hash semantics sufficient for
   independent receipt verification;
4. negative proof that no valid evidence produces zero provider attempts;
5. `NO_PROVIDER_CONFIGURED`, safe provider errors, timeout and provider-attempt
   accounting without secret or raw-provider leakage;
6. fresh real-provider proof and hosted smoke on the accepted LPCI1 HEAD;
7. a bounded public-only claim that does not promote LPCI1 into a complete RAG,
   restricted-data, durable-persistence or production-deployment system;
8. a provider-neutral reference contract or evidence packet consumable by
   downstream P4-A/P4-A2 DESIGN without importing the LPCI1 Web implementation.

If LPCI1-REF is unavailable or not accepted, P4-A1 may still close within its
provider-free retrieval boundary. P4-A and P4-A2 must remain parked or record a
fresh operator-approved alternative reference plan; they may not silently
waive the entry gate.

## P3-B dependency map

P4-A1 DESIGN must make these interfaces explicit without implementing provider
behavior:

| P3-B control | Current owner | P4-A1 responsibility | Later load-bearing owner |
|---|---|---|---|
| `data_scope` | `cvf_runtime.data_scope` and `RetrievalReadyV1.data_scope_evidence` | Separate record authorization from provider-placement approval; define evidence handed to a future context builder. | P4-A context builder immediately before any outbound call. |
| `cost` | `cvf_runtime.budget` | Define deterministic retrieval/context ceilings and expose requested budget facts; do not record provider spend. | P4-A gateway before provider attempt and usage ledger after response. |
| `termination` | `cvf_runtime.termination` | Define bounded query execution, timeout/cancellation result and receipt fields for local retrieval. | P4-A gateway across provider execution and retry/fallback. |

This dependency map does not close P3-B. P3-B remains open until a later
authorized real call site invokes the controls and fresh live governance proof
passes.

## Hard boundaries

This INTAKE authorizes no implementation. P4-A1 must not:

- call an LLM, provider, network service, product API, POST route or browser;
- add provider credentials, models, deployment configuration or live evidence;
- implement P4-A, P4-A2, P4-A3, P4-B, RAG, embeddings, reranking, vector search,
  index persistence, background synchronization or learning;
- treat the operator-supplied LPCI1 description or private provenance source as
  canonical project runtime authority;
- copy the LPCI1 Next.js route, hard-code a provider or introduce a second
  frontend-to-database path;
- search or rank protected records before principal and shift-scope admission;
- allow a client-selected corpus to widen server-authorized scope;
- admit a canonical operational record while its source digest owner is
  missing;
- claim tenant isolation, minimization, DLP, placement enforcement or durable
  AI audit;
- mutate, confirm, correct, approve, close or freeze operational truth;
- persist a generated answer in the Operations Ledger as canonical truth;
- modify the CVF core pin or resolve the local core/manifest warning inside
  this product tranche.
- implement, repair, test, commit or claim closure of LPCI1-REF inside this
  downstream tranche.

## Cheap-alternative inventory

| Alternative | Default disposition | Reason |
|---|---|---|
| Reuse active-assignment-scoped bounded read helpers and P3-C evidence. | `PREFER` | Smallest project-native surface with existing owners. |
| Start with lexical matching plus structured filters and deterministic ordering. | `PREFER` | Meets the roadmap without vector infrastructure or provider cost. |
| Use a dedicated local retrieval application service behind FastAPI. | `EVALUATE_FIRST` | Preserves backend governance and provider-neutral dependency direction. |
| Evaluate Project Knowledge as a local-only advisory fixture. | `EVALUATE_WITH_POLICY_BOUNDARY` | It is locally index-eligible but INTERNAL and not canonical operational truth. |
| Add canonical digest owners for selected confirmed record types. | `REQUIRED_DEPENDENCY` | P3-C currently fails closed for those records; ownership requires separate source review. |
| Search current API responses in the React client. | `REJECT` | Authorization, leakage control and receipts would be bypassable. |
| Copy LPCI1 Web or expose its public-only authorization model. | `REJECT` | Wrong stack, wrong classification and weaker source identity. |
| Add vector database, embeddings or semantic RAG now. | `REJECT_IN_P4A1` | Explicitly belongs to P4-A2 or later. |
| Call an LLM to rank or summarize retrieval results. | `REJECT_IN_P4A1` | Violates provider-free deterministic foundation and live-proof authority. |

## Decisions required before DESIGN closes

1. **Owner and dependency direction:** choose the smallest application/package
   boundary for the retrieval service and prove domain/ledger packages do not
   import API, UI, provider or gateway layers.
2. **Request contract:** define query, corpus selector, structured filters,
   result limit, context budget, correlation id and typed validation failures.
3. **Authorization order:** define authentication, permission and active-shift
   assignment checks before any protected source read, count, match or rank.
4. **Corpus registry:** define server-owned corpus ids, source classes and
   narrowing semantics; client input must not provide arbitrary paths or widen
   scope.
5. **Source eligibility and digest owners:** enumerate initially supported
   source types and name the separate reviewed digest owner required for each
   canonical operational record.
6. **Deterministic retrieval:** define normalization, lexical match semantics,
   structured filters, stable score/order, tie-breaking, duplicate handling and
   hard result limits.
7. **Use-time revalidation:** define source reload/revalidation behavior for
   digest, version, correction, lifecycle, retention and assignment changes.
8. **Evidence projection and budget:** define exact included fields, per-record
   text limit, record limit, serialized-byte or token estimate limit and
   fail-closed behavior without truncating provenance identity.
9. **Citation and receipt schema:** define chunk/content/source hashes, source
   version, safe reference, decision stages, outcome, correlation and timing;
   explicitly separate retrieval receipts from canonical operational records.
10. **P3-B handoff:** define the exact data-scope, cost and termination facts a
    future P4-A context builder consumes, without claiming those gates are
    load-bearing now.
11. **No-evidence and denial semantics:** define stable outcomes and prove that
    denial, unavailable evidence, stale evidence and empty match cannot reach a
    future provider boundary.
12. **Evolution and proof:** define contract versioning, backend parity,
    negative leakage tests, property/determinism tests and the later fresh live
    proof boundary without opening provider authority; preserve the separate
    LPCI1-REF entry gate before P4-A/P4-A2 DESIGN.

## Acceptance criteria for this INTAKE

INTAKE is acceptable only if independent review confirms:

- the request matches P4-A1 and starts from reviewed P3-C BUILD `4cc0691`;
- authorization occurs before any protected read, match, count or rank;
- a corpus selector can narrow but never widen server-authorized scope;
- the P3-C envelope remains the evidence identity and provenance owner;
- canonical operational records remain blocked until digest owners exist;
- the P3-B dependency map is explicit without claiming P3-B closure;
- INTERNAL Project Knowledge is not promoted to PUBLIC or external-AI eligible;
- the twelve DESIGN decisions cover retrieval, revalidation, citations,
  receipts, budgets, negative outcomes and proof boundaries;
- LPCI1 remains an adapted pattern, not an imported dependency or source of
  project truth;
- LPCI1-REF is non-blocking for P4-A1, separately governed in its owning
  repository, and an explicit entry gate before P4-A/P4-A2 DESIGN;
- P4-A2, provider calls, persistence, vector/index, learning and live proof
  remain parked;
- no DESIGN, SPEC, WORK_ORDER or BUILD authority is inferred.

## Governance cost and latency controls

- One consolidated INTAKE review must report all foreseeable boundary and
  source findings in one pass.
- Same-scope corrections remain under this INTAKE review authority.
- At repair round three without a new independent root cause, stop with
  `REVIEW_COST_ESCALATION_REQUIRED`.
- DESIGN should prefer one ADR and one independent review. Amendments require a
  real changed boundary, source fact or unresolved correctness defect.
- No test matrix, provider budget, deployment lane or implementation path set
  opens before DESIGN is accepted.

## Operational synchronization note

The mandatory workspace doctor passed with one warning after the sibling CVF
core was fast-forwarded to `2103a38fda01ee827e9fc6c3be38a824fa5d54ad`:
`.cvf/manifest.json:4` still pins
`9b039ea6b532176d92536338659bd346f019cd5a`. This INTAKE does not repair or
reinterpret that pin. A separate governed core-pin reconciliation is required
before any later artifact claims exact carrier-pin parity.

## Risk and evidence posture

`R2` is retained because the future caller controls which INTERNAL operational
evidence becomes retrievable and could later become outbound model context.
This INTAKE changes documentation and continuity only. It needs no provider,
network, database, runtime or product API call. Any later claim that CVF
controls retrieval or outbound AI context requires separate reviewed authority
and, where provider behavior is claimed, fresh real-provider evidence.

## Stop conditions

Stop and return to the orchestrator if review finds:

- authorization cannot precede every protected read/match/count/rank path;
- a selected canonical record type has no source digest owner;
- the corpus selector can widen scope or accept arbitrary source paths;
- use-time revalidation cannot fail closed on source or assignment drift;
- P4-A1 requires provider, vector/index persistence or P4-A2 behavior to be
  meaningful;
- retrieval receipts would become canonical operational truth;
- tenant isolation or external placement is required but lacks an owning
  source or policy contract;
- continuity, project/core boundary or classification evidence drifts.

These are DESIGN blockers, not permission to widen this tranche.

## Independent review contract

The next role is `INDEPENDENT_INTAKE_REVIEWER`. Review this artifact against
the cited project source, active handoff and roadmap. Preserve disagreements
and return exactly one disposition:

- `INTAKE_REVIEW_PASS`
- `INTAKE_REVIEW_CHANGES_REQUIRED`
- `INTAKE_BLOCKED_SOURCE_OR_OWNER`

The reviewer may perform local read-only source checks. The reviewer may not
design, implement, call providers/network/product APIs, modify the database,
stage, commit, push or infer later-phase authority.

## Claim boundary

This artifact only bounds P4-A1 INTAKE. It does not prove retrieval exists,
that authorization or data-scope is load-bearing for retrieval, that canonical
records are admissible, that an LLM is evidence-grounded, that citation output
is validated, that audit is durable, or that RAG/provider/vector/persistence/
production behavior exists.

## Next governed move

Obtain one consolidated independent INTAKE review. Only
`INTAKE_REVIEW_PASS` may transfer the bounded twelve-decision packet to
`DESIGN_AUTHOR`. No DESIGN drafting, source change, provider/network/product
API call, database change, staging, commit of later-phase artifacts or BUILD is
authorized by this INTAKE alone.
