# ADR - P4-A1 Governed Retrieval Foundation

- Tranche: `P4-A1-GOVERNED-RETRIEVAL-2026-08-10`
- DESIGN base: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Parent INTAKE: `docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`
- Parent INTAKE SHA-256: `7c32cd312ad4d889aa5039fbc32c032ee4312e0976224411cac106145b1ffde7`
- INTAKE review: `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Review transfer: operator-supplied independent read-only delta review at the DESIGN base
- Risk: `R2`
- Control-chain phase: `DESIGN`
- Status: `DESIGN_CANDIDATE_PENDING_INDEPENDENT_REVIEW`
- Provider/network/product-API/database calls: `0/0/0/0`

## Context

P3-C now provides a strict `RetrievalReadyV1` evidence envelope, but it does
not retrieve, persist, authorize, or call a provider. Canonical operational
records still return `SOURCE_DIGEST_OWNER_MISSING`, and their retrieval-use
retention owner is also absent. The current data-scope evidence explicitly says
`NOT_EVALUATED`, `NOT_PROVEN`, and `NO_LOAD_BEARING_CALLER`.

P4-A1 therefore creates a provider-free retrieval foundation. Its binding
order is:

`bounded query -> authenticate -> permission -> active assignment -> resolve
server corpus -> protected read -> P3-C admission -> deterministic match ->
use-time revalidation -> bounded evidence receipt`

No protected record may be read, counted, matched, or ranked before all three
authorization stages pass. The corpus selector can only narrow the authorized
scope. Provider generation, answer validation, durable audit, vector/index
persistence, and RAG remain outside this design.

## Current source basis

| Fact | Current owner | Design consequence |
|---|---|---|
| `RetrievalReadyV1` owns text, chunk/content/source identity, scope, lifecycle, retention, provenance, and data-scope evidence. | `retrieval_contracts.contract_models.RetrievalReadyV1` | It remains the only evidence envelope. |
| Canonical records return `SOURCE_DIGEST_OWNER_MISSING`. | `retrieval_contracts.constructor._construct_retrieval_contract` | No canonical corpus entry becomes enabled merely by this ADR. |
| Active membership is checked through `AssignmentScope.require_shift`. | `workspace_api.application.assignment_scope.AssignmentScope` | Reuse it before every protected source read. |
| Existing bounded browser reads cover only Message, Task, and CustomerRequest and reject 501 or more. | `workspace_api.application.browser_reads` | Reuse the pattern and limit, not an unsupported all-type claim. |
| No retrieval read-action exists in `_ACTION_MIN_ROLE`. | `cvf_runtime.permission` | `retrieval.query` below is explicitly `DESIGN_NEW`, not current behavior. |
| `operations-domain` is a sink, and the current domain/ledger trees do not import API, UI, provider, or gateway layers. | `operations_domain.models`; `operations_ledger.ledger.Ledger` | Future import guards preserve this direction. |
| Project Knowledge is `INTERNAL`, local-index eligible, and limited to local governed agents and human operators. | `knowledge/manifest.json` | It may be local advisory evidence only. |
| The current request-id middleware accepts a client header. | `workspace_api.middleware.request_id.RequestIdMiddleware` | A separate server-generated retrieval correlation id is required. |

## Decision 1 - Owner and dependency direction

Create one pure project-native package, `packages/governed-retrieval/`, to own
the V1 request/result contracts, corpus descriptors, query normalization,
lexical ranking, evidence projection, canonical receipt hashing, and a pure
engine over already admitted `RetrievalReadyV1` values. It may import only the
standard library, Pydantic, and `retrieval_contracts`. It performs no ledger,
filesystem discovery, environment, network, provider, API, or database access.

One DESIGN-new application service under
`workspace_api.application.governed_retrieval` owns authentication handoff,
permission, assignment admission, server corpus lookup, Ledger reads, P3-A/P3-C
construction, use-time revalidation, and invocation of the pure engine. A
future FastAPI route may call this service; React remains a thin HTTP client
and owns no governance decision.

The dependency arrows are exactly:

- `workspace-api -> governed-retrieval -> retrieval-contracts`;
- `workspace-api -> cvf-runtime`;
- `workspace-api -> operations-ledger -> operations-domain`;
- `retrieval-contracts -> refinery-bridge` and `operations-domain`, as today.

`operations-domain`, `operations-ledger`, `retrieval-contracts`, and
`governed-retrieval` must not import `workspace-api`, `workspace-web`, FastAPI,
provider adapters, `ai-gateway`, or one another in a reverse direction not
listed above. Static import tests must prove the boundary. No second query
repository, frontend-to-database path, index store, or provider abstraction is
created in P4-A1.

## Decision 2 - Request contract and validation

The external body is `GovernedRetrievalRequestV1` with exactly:

- `contract_version = "1.0"`;
- `query`: a strict Unicode string, 1-512 code points after surrounding
  whitespace removal, at most 4096 UTF-8 bytes, no NUL/control character, and
  at most 64 normalized lexical tokens;
- `corpus_id`: one exact server-registry id from Decision 4;
- `filters`: `shift_ids`, `record_types`, `truth_classes`, and
  `lifecycle_statuses`, each sorted and unique and each only narrowing the
  selected corpus; shift-bound corpora require one or two shift ids;
- `result_limit`: integer 1-20, default 10;
- `context_budget`: client-requested ceilings for records, per-record text,
  serialized bytes, and estimated tokens. Every value must be positive and no
  greater than the server maxima in Decision 8.

Unknown fields, enums, corpus ids, duplicate/unsorted filters, out-of-range
limits, malformed Unicode, or a filter not allowed by the selected corpus are
typed failures. The closed validation codes are `REQUEST_SHAPE_INVALID`,
`QUERY_INVALID`, `QUERY_LIMIT_EXCEEDED`, `CORPUS_ID_INVALID`,
`FILTER_INVALID`, `FILTER_WIDENS_SCOPE`, `RESULT_LIMIT_INVALID`, and
`CONTEXT_BUDGET_INVALID`. Validation may inspect only the bounded request; it
must not resolve a corpus or touch protected state.

`correlation_id` is not accepted from the body. On service entry the backend
creates a UUIDv4 `retrieval_correlation_id` and binds it to an internal
`GovernedRetrievalExecutionV1`. The transport `x-request-id` may remain a trace
hint, but because the current middleware accepts a client value it is neither
authority nor the retrieval receipt identity.

## Decision 3 - Authorization order

The application service executes these stages in exact order:

1. validate the bounded request without protected reads;
2. authenticate through `get_principal` and a verified bearer token;
3. call `require_action(principal, "retrieval.query")`;
4. for every requested shift id, call `AssignmentScope.require_shift` with the
   same Ledger unit and principal;
5. only after every requested shift passes, resolve the corpus and read source
   records.

`retrieval.query` is a DESIGN-new governed action owned by
`cvf_runtime.permission`, with minimum role `viewer`. It makes the permission
stage explicit while preserving the current ability of an assigned viewer to
read. It must be added only by a later reviewed BUILD; until then the retrieval
service is not dispatch-ready.

An empty shift set is invalid for a shift corpus. Project Knowledge also
requires one current active-shift assignment as a local operator access anchor;
the anchor does not make the document shift-owned. Missing shift and missing
assignment use the same enumeration-safe denial. No failure response exposes
which shift, corpus member, match count, or record caused denial.

## Decision 4 - Server-owned corpus registry

The registry is immutable process configuration loaded by the backend, never a
client path, URL, table name, query fragment, or filesystem glob. V1 defines
exactly these ids:

| Corpus id | Source class | Allowed source types | Initial state |
|---|---|---|---|
| `SHIFT_CONFIRMED_OPERATIONS_V1` | `CANONICAL_OPERATIONAL_RECORD` | OperationalEvent, Task, CustomerRequest, Incident, Handover, Report | `DEPENDENCY_BLOCKED` until every selected type has reviewed digest and retrieval-retention owners |
| `SHIFT_ADVISORY_MESSAGES_V1` | `ADVISORY_SOURCE_EVIDENCE` | Message | `DEPENDENCY_BLOCKED` until a retrieval-retention owner and P3-A binding caller exist |
| `PROJECT_KNOWLEDGE_LOCAL_V1` | `ADVISORY_SOURCE_EVIDENCE` | `PROJECT_KNOWLEDGE` entries that are current and local-index eligible | `LOCAL_ONLY`; never provider eligible |

Each descriptor fixes classification, allowed record types/statuses, source
adapter, maximum shifts, and whether local human/operator consumption is
allowed. The server first intersects request filters with the authorized shift
set and descriptor allowlists. Empty intersection is a typed no-evidence
result; any attempted expansion is `FILTER_WIDENS_SCOPE`.

Project Knowledge admission additionally requires a current valid manifest,
an allowed consumer, matching source pins, `eligibleForLocalIndex = true`, and
an active owner. Its `INTERNAL` classification is preserved. A disabled corpus
returns `CORPUS_UNAVAILABLE` without reading or counting its sources.

## Decision 5 - Source eligibility and separately reviewed digest owners

The P3-C eligibility matrix remains binding. P4-A1 does not create a second
source projection or a weaker citation object.

| Source type | Initial retrieval disposition | Field selector | Digest owner required before canonical admission |
|---|---|---|---|
| OperationalEvent | conditional; state CONFIRMED, CORRECTED, or FROZEN | `title` | DESIGN-new `operations_domain.retrieval_digests.operational_event_source_digest_v1` |
| Task | conditional; data state CONFIRMED, CORRECTED, or FROZEN | `title` | DESIGN-new `operations_domain.retrieval_digests.task_source_digest_v1` |
| CustomerRequest | conditional; persisted and shift-bound | `summary` | DESIGN-new `operations_domain.retrieval_digests.customer_request_source_digest_v1` |
| Incident | conditional; ACKNOWLEDGED, MITIGATING, RESOLVED, or CLOSED | `summary` | DESIGN-new `operations_domain.retrieval_digests.incident_source_digest_v1` |
| Handover | conditional; REVIEWED or ACKNOWLEDGED | `items/{item_id}/summary` | DESIGN-new `operations_domain.retrieval_digests.handover_source_digest_v1` |
| Report | conditional; current APPROVED or FROZEN snapshot | `content` | DESIGN-new `operations_domain.retrieval_digests.report_source_digest_v1` |
| Message | advisory and conditional; INTERNAL persisted message with admitted P3-A candidate | `text` | current P3-C content digest; separate retrieval-retention owner still required |
| `PROJECT_KNOWLEDGE` | advisory local-only when manifest/pins/owner are current | `document` | current source pin plus candidate fingerprint; manifest entry owns the local retention assertion |

The six named canonical functions are separate public source contracts, not
existing symbols. Each must receive independent source-set, canonical-byte,
version, and lifecycle review before its record type is enabled. They must hash
explicit source-owned canonical fields and must not use an unrestricted
`model_dump`, an application-layer Report/Handover helper, or a digest copied
into `retrieval-contracts`.

A digest owner is not a retention owner. Canonical and Message corpora remain
disabled if retrieval-use retention/erasure authority is absent, even after a
digest function passes. `SOURCE_DIGEST_OWNER_MISSING`,
`RETENTION_OWNER_NOT_FOUND`, expired/erased disposition, or any P3-C
non-admission stays fail-closed and is counted only in a safe receipt after
authorization.

## Decision 6 - Deterministic lexical retrieval

Query normalization is Unicode NFC, `casefold`, line-ending and whitespace
collapse, followed by tokenization into contiguous Unicode letter/number
sequences. There is no stemming, fuzzy match, transliteration, synonym,
translation, embedding, LLM, or locale-dependent collation. Evidence text is
never rewritten for matching.

After authorization, structured filters run on typed P3-C metadata. A lexical
candidate must contain the normalized full query phrase or at least one query
token. Its integer score is:

`phrase_hit * 1000000 + distinct_query_tokens_matched * 1000 +
min(total_token_occurrences, 255)`

Results sort by descending score, then by the stable ascending tuple
`(truth_class, record_type, record_id-or-source_id, source_version_kind,
source_version_value, field_selector, chunk_id)`. No float or input iteration
order affects ranking.

An exact duplicate `chunk_id` with byte-identical canonical
`RetrievalReadyV1` content collapses to one candidate. The same `chunk_id` with
different canonical bytes is `INVARIANT_FAILURE` for the request, never a
tie. Multiple versions are not silently coalesced; use-time revalidation
rejects every non-current value.

Each source-type/shift read is capped at 500 records, matching the established
bounded-read maximum. Project Knowledge is capped at 100 manifest entries.
The aggregate pre-ranking cap is 2000 admitted candidates, the result cap is
20, and the evidence projection cap is 4. Exceeding a source or aggregate cap
returns `RETRIEVAL_LIMIT_EXCEEDED`; no list is silently truncated.

## Decision 7 - Use-time revalidation

Ledger-backed execution uses one `Ledger.transaction()` unit for assignment
admission, source reads, exact-id reloads, correction reads, and the final
assignment check. All unit-aware calls receive the same `unit` token. Backend
parity proof must show the supported Ledger implementations observe the same
fail-closed behavior; this ADR does not claim linearizability beyond the
backend transaction contract.

Immediately after ranking and before projection, the service reloads each
selected source by exact id and reconstructs its P3-C input from current state.
It recomputes and compares source digest, version binding, correction lineage,
lifecycle/parent-shift observation, retention/erasure assertion, content
digest, chunk id, and revalidation token. It then re-runs active assignment for
all selected shifts immediately before returning.

Project Knowledge instead rechecks the manifest entry, consumer class,
classification, source pin, current raw-byte pin digest, local-index flag, and
owner/retention assertion. It is never reclassified as PUBLIC.

A changed source is not silently refreshed into the same ranked execution.
Digest/version/correction/lifecycle/retention drift removes that item and
records a safe reason. Assignment drift denies the entire response. If all
matched items are removed, the result is `STALE_EVIDENCE`; the caller must make
a new request.

## Decision 8 - Evidence projection and context budget

`EvidenceProjectionV1` contains exactly:

- the complete `CitationV1` from Decision 9;
- `truth_class`, `field_selector`, and P3-A sensitivity;
- `content_snippet`, `snippet_start_codepoint`, `snippet_end_codepoint`,
  `snippet_digest_sha256`, and `projection_complete`.

It never contains raw text, redacted-away values, arbitrary paths, the complete
domain object, or the full P3-C provenance receipt chain. The full
`RetrievalReadyV1` remains the evidence/provenance owner held inside the
backend execution.

Server maxima are exactly 4 projections, 1024 Unicode code points and 3072
UTF-8 bytes of snippet text per projection, 16384 canonical serialized UTF-8
bytes for the whole projection array, and 4096 estimated input tokens. The
deterministic estimate is `ceil(serialized_utf8_bytes / 2)` and is labeled
`UTF8_BYTES_DIV_2_ESTIMATE_V1`, not a provider tokenizer or cost proof. A client
may request smaller values only.

This reconciles the existing 65536-character P3-C text ceiling as follows. The
source value remains unchanged and fully identified by its content/source/chunk
hashes. The snippet is a separate projection: a deterministic 1024-code-point
window centered on the first best lexical match, with a lower starting offset
winning ties, then reduced only at a Unicode boundary to satisfy 3072 bytes.
Offsets, snippet digest, and `projection_complete` make that reduction explicit.

The engine takes at most the top four revalidated records. If the aggregate
byte/token budget is exceeded, it removes the lowest-ranked whole projection
and records the omission count. It never drops or truncates citation,
provenance identity, version, or hash fields. If one complete identity plus a
non-empty snippet cannot fit, return `CONTEXT_BUDGET_EXCEEDED` with no evidence
handoff.

## Decision 9 - Citation and retrieval receipt

`CitationV1` contains `chunk_id`, `content_digest_sha256`,
`source_digest_sha256`, the exact P3-C version union, `truth_class`,
`record_type`, safe `record_id` or `source_id`, `field_selector`,
`revalidation_token`, `source_cutoff_utc`, `snippet_digest_sha256`, and snippet
offsets. A path alone is never a citation.

`RetrievalReceiptV1` contains:

- `contract_version`, server UUID `receipt_id`, and
  `retrieval_correlation_id`;
- `started_at_utc`, `finished_at_utc`, integer `elapsed_ms`, and source cutoff;
- corpus id and an authorization-scope digest, never an arbitrary path;
- the fixed stage sequence `REQUEST_VALIDATED`, `AUTHENTICATED`,
  `PERMISSION_AUTHORIZED`, `ASSIGNMENT_AUTHORIZED`, `CORPUS_RESOLVED`,
  `SOURCES_READ`, `P3C_ADMITTED`, `MATCHED_AND_RANKED`, `REVALIDATED`,
  `PROJECTED`, `RECEIPT_EMITTED`;
- for every stage, one of `PASS`, `DENY`, `FAIL`, or `NOT_RUN`, a stable safe
  reason code, and non-sensitive counts;
- final outcome, requested/applied limits, candidate/admitted/matched/stale/
  projected/omitted counts, timeout/cancellation facts, ordered citation ids,
  `evidence_set_hash_sha256`, and `receipt_hash_sha256`.

Canonical JSON uses UTF-8, NFC strings, sorted keys, compact separators, no
floats/NaN/Infinity, and fixed array ordering. The evidence-set hash covers the
ordered citations and projections. The receipt hash covers the receipt with
its own hash field omitted.

The receipt is an ephemeral response artifact. It is not an
`operations_domain` record, `AuditRecord`, approval, correction, or durable
Ledger entry, and P4-A1 performs no audit write. Correlation plus hashes enable
bounded verification but do not prove durable persistence or an AI answer.

## Decision 10 - Exact P3-B handoff facts

Only an `EVIDENCE_AVAILABLE` result carries `FutureContextHandoffV1`, containing:

- retrieval receipt/evidence-set hashes and ordered citation ids;
- classification and sensitivity sets from admitted evidence;
- exact serialized bytes, snippet code points, projection count,
  `estimated_input_tokens`, and `UTF8_BYTES_DIV_2_ESTIMATE_V1`;
- applied retrieval/context ceilings and local `elapsed_ms`/timeout/
  cancellation outcome;
- carried P3-C values `minimization_evidence_status = "NOT_PROVEN"`,
  `placement_enforcement_status = "NOT_EVALUATED"`, and
  `runtime_caller_status = "NO_LOAD_BEARING_CALLER"`;
- `provider_attempt_authorized = false`, `provider_attempts = 0`, and no
  provider, model, spend, usage, or placement claim.

This handoff is evidence for, not satisfaction of, P3-B. A future P4-A context
builder must re-evaluate classification and minimization evidence, call
`assert_placement_allowed`, compute actual provider input/output token budget
and call `assert_within_budget`, then enforce `assert_not_terminated`
immediately before and across any provider attempt. Retrieval timeout facts do
not substitute for provider termination state. P3-B remains open until those
calls are load-bearing and live proof is separately authorized.

## Decision 11 - No-evidence and denial semantics

`GovernedRetrievalResultV1` is a strict union with final outcomes:

- `EVIDENCE_AVAILABLE`;
- `NO_EVIDENCE` for an authorized, available corpus with no lexical match;
- `ACCESS_DENIED` for authentication, permission, or assignment failure;
- `CORPUS_UNAVAILABLE` for a disabled/missing-owner corpus;
- `STALE_EVIDENCE` when every selected match fails revalidation;
- `RETRIEVAL_LIMIT_EXCEEDED`;
- `RETRIEVAL_TIMEOUT` or `RETRIEVAL_CANCELLED`;
- `CONTEXT_BUDGET_EXCEEDED`;
- `INVALID_REQUEST`;
- `INVARIANT_FAILURE`.

Only `EVIDENCE_AVAILABLE` has a non-empty projection tuple and the bounded
future-context handoff. Every other variant structurally omits both fields and
reports `provider_attempts = 0`. Denial and unavailable results expose no
protected counts. Expected empty/stale/limit/timeout outcomes are typed data,
not exceptions with source content.

P4-A1 has no provider import, request type, adapter, or callable. A future
provider boundary may accept only a separately validated context-builder
output derived from non-empty `EVIDENCE_AVAILABLE` plus successful P3-B gates.
It cannot accept the negative union variants. Thus no evidence, denial,
unavailability, staleness, timeout, or budget failure has a path to a provider
attempt.

## Decision 12 - Evolution, proof, and LPCI1-REF gate

V1 models reject unknown fields/enums. An additive minor revision may add only
an optional field with an explicit fail-closed default and must preserve all
canonical preimages. New required fields, relaxed authorization/eligibility,
changed normalization/score/hash semantics, or changed corpus meaning requires
a new major version and migration; there is no permissive fallback to V1.

A future SPEC and BUILD must require:

- schema/golden tests for request, result, citation, projection, and receipt
  canonical bytes/hashes;
- static dependency tests proving the arrows in Decision 1 and zero provider,
  UI, network, or database access from the pure engine;
- instrumented negative-leakage tests proving zero protected Ledger calls
  before authentication, permission, and every requested assignment pass;
- InMemoryLedger and SqlLedger/SQLite parity for ordering, limits,
  revalidation, and enumeration-safe denial, with PostgreSQL parity required
  before any PostgreSQL/production claim;
- property tests over input permutation, duplicate order, LF/CRLF, NFC/non-NFC,
  Unicode casefolding, byte/code-point boundaries, score ties, budgets, and
  repeated execution;
- adversarial digest/version/correction/lifecycle/retention/assignment drift
  tests and continued `SOURCE_DIGEST_OWNER_MISSING` proof for every unreviewed
  canonical digest owner;
- a provider-spy seam only in a later P4-A test, proving every negative P4-A1
  result yields zero provider attempts.

P4-A1 DESIGN/SPEC/local BUILD needs zero live/provider calls and may close only
the provider-free bounded retrieval claim. Any later claim about outbound
governance, evidence-grounded answers, provider errors, or hosted behavior
requires fresh real-provider proof under separately approved authority.

`LPCI1-REF` remains non-blocking for P4-A1. It remains an entry gate before
P4-A or P4-A2 DESIGN: only accepted evidence from its separately governed CVF
lane, or a fresh operator-approved alternative reference plan, may satisfy the
gate. P4-A/P4-A2 may not silently waive it, and this downstream ADR does not
implement, test, repair, commit, or claim LPCI1-REF.

## Alternatives rejected

- Put retrieval inside `retrieval-contracts`: rejected because P3-C explicitly
  owns a pure non-retrieving contract/constructor boundary.
- Search in React or call the Ledger from the frontend: rejected because it
  bypasses backend authorization and receipts.
- Let clients provide paths/tables or arbitrary corpus definitions: rejected
  because a selector may narrow but never create authority.
- Enable canonical records with a generic Pydantic dump: rejected because the
  source-owning digest contract is missing.
- Treat P3-A redaction as minimization or P3-C data-scope fields as placement
  approval: rejected because those fields explicitly say not proven/evaluated.
- Add vector search, embeddings, reranking, an LLM, or persistent index now:
  rejected because these belong to later separately governed tranches.
- Write a retrieval receipt or future model answer to the Operations Ledger:
  rejected because neither is canonical operational truth.

## Design acceptance

Independent review must confirm all twelve accepted INTAKE decisions are
resolved without weakening P3-C identity, authorization ordering, INTERNAL
classification, owner gaps, P3-B status, or the LPCI1-REF entry gate. It must
also confirm that the exact limits and result union are implementable through a
separate testable SPEC.

One consolidated independent DESIGN review returns exactly one of
`DESIGN_REVIEW_PASS`, `DESIGN_REVIEW_CHANGES_REQUIRED`, or
`DESIGN_BLOCKED_SOURCE_OR_OWNER`. No review authority is inferred by this ADR.

## Claim boundary

This ADR is a design candidate only. It does not prove retrieval exists,
canonical records are admissible, authorization/data-scope/cost/termination is
load-bearing for retrieval or AI, Project Knowledge may leave the local
boundary, receipts are durable, an LLM is grounded, citations are answer-
validated, or RAG/vector/index/provider/deployment/production behavior exists.

P4-A1 may later close as a provider-free foundation while disabled corpora
remain fail-closed, but it must not claim confirmed-record retrieval until the
named digest and retrieval-retention owners are independently accepted and
implemented.

## Next governed move

Obtain one consolidated independent DESIGN review of this ADR against the
accepted INTAKE and current source. Only `DESIGN_REVIEW_PASS` may transfer the
exact contract to `SPEC_AUTHOR`. No SPEC, work order, implementation, provider
call, commit, push, or later-phase artifact is authorized now.
