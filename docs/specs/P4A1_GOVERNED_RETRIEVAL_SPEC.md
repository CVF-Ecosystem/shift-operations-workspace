# SPEC - P4-A1 Governed Retrieval Foundation

- Tranche: `P4-A1-GOVERNED-RETRIEVAL-2026-08-10`
- Parent ADR: `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`
- Parent ADR SHA-256: `8dbdfbaded8ed523eb465bc3c657620a323fafae465f5d0d0d66fe8cac6aa4fc`
- Parent INTAKE: `docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`
- Parent INTAKE SHA-256: `7c32cd312ad4d889aa5039fbc32c032ee4312e0976224411cac106145b1ffde7`
- DESIGN review: `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Review transfer: operator-supplied independent read-only review at
  `d878001b6a1a536218b2c66019243510ef3f7aec`
- Risk: `R2`
- Control-chain phase: `SPEC`
- Status: `SPEC_CANDIDATE_PENDING_INDEPENDENT_REVIEW`
- Provider/network/product-API/database calls: `0/0/0/0`

## Scope and normative language

This SPEC converts the accepted twelve-decision ADR into twelve testable
requirements. `MUST`, `MUST NOT`, `EXACTLY`, and `IF AND ONLY IF` are
normative. Each `AC-xx` is the acceptance criterion for the requirement with
the same ordinal.

P4-A1 is a local deterministic retrieval foundation. It does not authorize an
LLM, provider, vector/index persistence, durable retrieval audit, answer
validation, RAG, deployment, or a product route. `RetrievalReadyV1` remains the
only evidence/provenance envelope.

## Current implementation truth versus intended behavior

| Surface | Current implementation truth | This SPEC requires later |
|---|---|---|
| P3-C envelope | `RetrievalReadyV1` exists with a 65536-character text ceiling and strict source/provenance fields. | Reuse without weakening or duplicating it. |
| Canonical admission | All canonical record branches return `SOURCE_DIGEST_OWNER_MISSING`. | Remain blocked until each named digest owner and a retrieval-retention owner pass separate review. |
| Permission | `_ACTION_MIN_ROLE` has no `retrieval.query`; unknown actions fail closed. | `DESIGN_NEW`: add `retrieval.query` at minimum role `viewer` only in a later authorized BUILD. |
| Assignment | `AssignmentScope.require_shift` exists. | Reuse it before every protected source read. |
| Bounded reads | Existing helpers cap Message, Task, and CustomerRequest at 500; they do not cover every type. | Extend the pattern through a separately specified service without claiming current all-type support. |
| Retrieval package/service | `packages/governed-retrieval/` and `workspace_api.application.governed_retrieval` do not exist. | `DESIGN_NEW`: create them only under a later reviewed work order. |
| Digest owner module | `operations_domain.retrieval_digests` and its six functions do not exist. | `DESIGN_NEW`: independently review each source contract before enabling its type. |
| P3-B gates | Data scope, cost, and termination are callable but have no load-bearing AI caller. | Carry facts only; do not claim closure or placement authority. |
| Project Knowledge | Manifest classification is `INTERNAL`; consumers are local governed agents/human operators; local index is eligible. | Keep `LOCAL_ONLY` and never provider eligible or PUBLIC. |
| Receipt/audit | No retrieval receipt exists; `AuditRecord` and Ledger audit are mutation surfaces. | Return an ephemeral retrieval receipt and perform no P4-A1 audit write. |

## Normative requirements

### R1 - Owner and dependency boundary

The intended implementation MUST create one pure package named
`governed-retrieval` under `packages/governed-retrieval/`. It owns V1 request
and result models, immutable corpus descriptors, normalization, lexical
ranking, projection, and canonical receipt hashing. It MUST accept all evidence
and execution metadata explicitly and MAY import only the standard library,
Pydantic, and `retrieval_contracts`.

The DESIGN-new `workspace_api.application.governed_retrieval` service owns the
application orchestration: authenticated principal input, permission,
assignment admission, server registry access, Ledger/source reads, P3-A/P3-C
construction, revalidation, and pure-engine invocation.

The only new dependency arrows are:

- `workspace-api -> governed-retrieval -> retrieval-contracts`;
- `workspace-api -> cvf-runtime`;
- `workspace-api -> operations-ledger -> operations-domain`.

Existing `retrieval-contracts -> refinery-bridge` and
`retrieval-contracts -> operations-domain` arrows remain. `operations-domain`,
`operations-ledger`, `retrieval-contracts`, and `governed-retrieval` MUST NOT
import `workspace-api`, `workspace-web`, FastAPI, `ai-gateway`, provider
adapters, or a reverse dependency not listed above. The pure package MUST NOT
perform ledger, database, filesystem discovery, environment, network,
provider, API, wall-clock, or secret access. No frontend-to-database path,
second query repository, provider abstraction, or persistent index is allowed.

**Acceptance AC-01:** An AST/import and call-boundary suite proves every
allowed arrow, fails on each forbidden import/access class, and proves the pure
engine receives explicit values only. Source inspection also proves the domain
and ledger packages retain zero API/UI/provider/gateway imports.

### R2 - GovernedRetrievalRequestV1 and closed validation failures

`GovernedRetrievalRequestV1` MUST reject unknown fields and contain exactly:

- `contract_version`, literal `"1.0"`;
- `query`;
- `corpus_id`;
- `filters: RetrievalFiltersV1`;
- `result_limit`, integer 1-20 and not `bool`, default 10;
- `context_budget: ContextBudgetV1`.

`RetrievalFiltersV1` contains exactly `shift_ids`, `record_types`,
`truth_classes`, and `lifecycle_statuses`. Every collection is a tuple, sorted
by Unicode code-point order, and duplicate-free. `shift_ids` MUST contain one
or two safe ids for a shift corpus. `PROJECT_KNOWLEDGE_LOCAL_V1` MUST contain
exactly one shift id used only as an active-assignment access anchor. The other
three tuples MAY be empty to request the full server allowlist; a non-empty
tuple only narrows it.

`ContextBudgetV1` contains exactly `max_projection_records`,
`max_snippet_codepoints`, `max_snippet_utf8_bytes`,
`max_serialized_utf8_bytes`, and `max_estimated_input_tokens`. Every value is a
positive integer, not `bool`, and is no greater than its R8 server maximum.

Query preprocessing MUST strictly decode Unicode, reject NUL/unpaired
surrogates, canonicalize CRLF/CR to LF, collapse Unicode whitespace, and remove
surrounding whitespace. The resulting query MUST contain 1-512 code points,
at most 4096 UTF-8 bytes, no Unicode `Cc` control, and at most 64 R6 tokens.
The normalized query, not the raw wire form, is the request value used later.

The request failure code enum is closed to exactly:

1. `REQUEST_SHAPE_INVALID` for non-mapping, schema-version, field-set, or type
   failure;
2. `QUERY_INVALID` for decode, NUL/surrogate/control, or empty-query failure;
3. `QUERY_LIMIT_EXCEEDED` for code-point, UTF-8-byte, or token overflow;
4. `CORPUS_ID_INVALID` for an unknown registry id after R3 authorization;
5. `FILTER_INVALID` for malformed, unsorted, duplicate, or invalid-cardinality
   filter input;
6. `FILTER_WIDENS_SCOPE` for a well-formed filter outside the authorized
   corpus descriptor after R3 authorization;
7. `RESULT_LIMIT_INVALID`;
8. `CONTEXT_BUDGET_INVALID`.

Structural validation runs in the listed precedence order where applicable
and MUST NOT resolve the corpus or call protected state. Corpus-id and
allowlist semantics run only after R3 permits registry resolution. Every code
maps to final `INVALID_REQUEST` without adding another request-error code.

The body MUST NOT accept `correlation_id`. The application service generates a
UUIDv4 `retrieval_correlation_id` and binds it to an internal
`GovernedRetrievalExecutionV1`. A transport `x-request-id` is an untrusted trace
hint and MUST NOT supply authority, receipt identity, or correlation identity.

**Acceptance AC-02:** Contract tests cover every field/type/default/bound,
each of the eight codes, multi-failure precedence, strict extra-field
rejection, one/two-shift rules, client attempts to set correlation, and a spy
that observes zero registry/Ledger/source calls during structural validation.

### R3 - Five-stage authorization and read ordering

The application boundary MUST execute exactly these ordered stages:

1. bounded structural request validation with zero protected reads;
2. authentication through `get_principal` and a verified bearer token;
3. `require_action(principal, "retrieval.query")`;
4. `AssignmentScope.require_shift` for every requested shift id and the same
   principal, inside the R7 Ledger unit;
5. only after all prior stages pass, resolve the server corpus and read any
   protected source.

`retrieval.query` is DESIGN_NEW, absent from current `_ACTION_MIN_ROLE`, and
MUST later be owned by `cvf_runtime.permission` at minimum role `viewer`.
Until a separately reviewed BUILD adds it, the service is not dispatch-ready;
unknown-action fail-closed behavior MUST NOT be bypassed.

Failure at authentication, permission, or any assignment MUST prevent corpus
resolution and every protected read, count, match, and rank. Missing shift and
missing assignment MUST return the same enumeration-safe `ACCESS_DENIED`
shape. A Project Knowledge anchor grants local access only; it does not make a
document shift-owned. Denial MUST reveal no shift existence, corpus member,
source count, or match count.

**Acceptance AC-03:** An ordered call-spy suite covers failure at each stage
and proves zero later calls, including multi-shift failure after one admitted
shift. Positive tests prove every assignment call precedes corpus resolution
and the first source access. Source truth checks prove `retrieval.query` is
still absent before BUILD and current `require_action` rejects it.

### R4 - Immutable server corpus registry

The V1 registry MUST be immutable process configuration. A client value MUST
never become a path, URL, table/column name, query fragment, filesystem glob,
adapter import, or source location. The registry contains exactly:

| Corpus id | Truth/source class | Allowed types | Initial state |
|---|---|---|---|
| `SHIFT_CONFIRMED_OPERATIONS_V1` | `CANONICAL_OPERATIONAL_RECORD` | OperationalEvent, Task, CustomerRequest, Incident, Handover, Report | `DEPENDENCY_BLOCKED` |
| `SHIFT_ADVISORY_MESSAGES_V1` | `ADVISORY_SOURCE_EVIDENCE` | Message | `DEPENDENCY_BLOCKED` |
| `PROJECT_KNOWLEDGE_LOCAL_V1` | `ADVISORY_SOURCE_EVIDENCE` | `PROJECT_KNOWLEDGE` | `LOCAL_ONLY` |

The first corpus MUST remain blocked until every selected type has both a
reviewed digest owner and retrieval-use retention/erasure owner. The second
MUST remain blocked until its retention owner and P3-A binding caller exist.
A blocked corpus returns `CORPUS_UNAVAILABLE` after authorization without
reading or counting any source.

The server intersects filters only after authorization. A valid subset may
narrow descriptor values and authorized shifts. A value outside the descriptor
is `FILTER_WIDENS_SCOPE`; an authorized subset with no records/matches is
`NO_EVIDENCE`.

Project Knowledge MUST pass current manifest shape, allowed-consumer, source
pin, current raw-byte pin digest, active owner,
`eligibleForLocalIndex = true`, and local retention assertion checks. Its
classification is always `INTERNAL`, state always `LOCAL_ONLY`, and
`provider_attempt_authorized` always false. It MUST NOT become PUBLIC or
external-AI eligible.

**Acceptance AC-04:** Registry golden tests assert the exact three ids,
classes, type sets, and initial states; mutation and malicious selector tests
fail. Negative tests prove blocked corpora perform zero source calls, filters
cannot widen, and every Project Knowledge prerequisite fails closed while its
classification/provider fields remain exact.

### R5 - Eight-source eligibility matrix and six DESIGN_NEW digest owners

P4-A1 MUST pass evidence through the current P3-C constructor and MUST accept
only `RetrievalReadyV1`. It MUST NOT construct a second provenance envelope or
path-only evidence identity.

| Source type | P3-C eligibility retained by P4-A1 | Field selector | Digest owner status |
|---|---|---|---|
| OperationalEvent | CONFIRMED, CORRECTED, or FROZEN | `title` | DESIGN_NEW `operations_domain.retrieval_digests.operational_event_source_digest_v1` |
| Task | data state CONFIRMED, CORRECTED, or FROZEN | `title` | DESIGN_NEW `operations_domain.retrieval_digests.task_source_digest_v1` |
| CustomerRequest | persisted and shift-bound | `summary` | DESIGN_NEW `operations_domain.retrieval_digests.customer_request_source_digest_v1` |
| Incident | ACKNOWLEDGED, MITIGATING, RESOLVED, or CLOSED | `summary` | DESIGN_NEW `operations_domain.retrieval_digests.incident_source_digest_v1` |
| Handover | REVIEWED or ACKNOWLEDGED | `items/{item_id}/summary` | DESIGN_NEW `operations_domain.retrieval_digests.handover_source_digest_v1` |
| Report | current APPROVED or FROZEN snapshot | `content` | DESIGN_NEW `operations_domain.retrieval_digests.report_source_digest_v1` |
| Message | INTERNAL persisted message bound to an admitted P3-A candidate | `text` | current P3-C content digest; retrieval-retention owner missing |
| `PROJECT_KNOWLEDGE` | current manifest/pins/owner, advisory local-only | `document` | current source pin plus candidate fingerprint; manifest entry owns local retention assertion |

Each of the six new canonical digest functions MUST receive its own independent
source-field, canonical-byte, version, and lifecycle review before its type is
enabled. Its preimage MUST enumerate explicit source-owned fields. It MUST NOT
use unrestricted `model_dump`, copy a digest implementation into
`retrieval_contracts`, or import/alias/access/wrap/call application helpers
`handover_service.compute_source_digest` or
`report_snapshot.compute_source_digest`.

Digest ownership does not prove retention ownership. Canonical and Message
corpora MUST remain disabled when retrieval-use retention/erasure authority is
missing, expired, erased, or inactive, even if a digest function passes.
`SOURCE_DIGEST_OWNER_MISSING`, `RETENTION_OWNER_NOT_FOUND`, and every other
P3-C non-admission MUST remain fail-closed and may be counted only after R3.

**Acceptance AC-05:** Matrix tests cover all eight `RecordType` values, every
eligible/ineligible lifecycle and selector, and exact P3-C non-admission
propagation. Static/adversarial tests prove all six missing owners continue to
yield `SOURCE_DIGEST_OWNER_MISSING`, forbidden digest helpers are unreachable,
and digest success alone cannot enable a source without active retention.

### R6 - Deterministic lexical retrieval and hard limits

The query and candidate matching view MUST be normalized by Unicode NFC,
`casefold`, CRLF/CR to LF, and whitespace collapse. Tokenization MUST produce
maximal contiguous sequences whose Unicode categories are Letter or Number.
No stemming, fuzzy match, transliteration, synonym, translation, embedding,
LLM, locale collation, or evidence-text rewrite is allowed.

Candidate normalization MUST also emit an offset map into the unchanged P3-C
text, which is already NFC. Scan source code points left to right: CRLF emits
one LF mapped to the consumed two-code-point interval; CR emits LF mapped to
its interval; every code point emitted by one source code point's `casefold`
maps to that source interval; and each maximal whitespace run emits one ASCII
space mapped to the union of its source intervals. Trimmed edge whitespace
emits nothing. A normalized match `[a,b)` maps to the minimum source start and
maximum source end of its emitted members. This map, never normalized-string
indices, supplies R8 offsets and makes casefold expansion deterministic.

Let `Q` be the ordered query token sequence and `Qset` its distinct values.
For a candidate's normalized text:

- `phrase_hit` is 1 if the complete normalized query is a code-point substring,
  otherwise 0;
- `distinct_query_tokens_matched` is the size of the subset of `Qset` present
  in the candidate token sequence;
- `total_token_occurrences` is the count of candidate tokens whose value is in
  `Qset`.

A candidate matches IF AND ONLY IF `phrase_hit = 1` or
`distinct_query_tokens_matched > 0`. Its score is the exact integer:

`phrase_hit * 1000000 + distinct_query_tokens_matched * 1000 +
min(total_token_occurrences, 255)`

Sort descending by score, then ascending by the seven-part tuple
`(truth_class, record_type, record_id-or-source_id, source_version_kind,
source_version_value, field_selector, chunk_id)`. Version value is decimal
ASCII for integer version, the exact safe string for source-string version,
and empty string for unversioned. No float, locale, map order, adapter order,
or input permutation may affect output.

Equal `chunk_id` plus byte-identical canonical `RetrievalReadyV1` values
collapses to one candidate. Equal `chunk_id` with unequal canonical bytes
returns `INVARIANT_FAILURE`. Different versions are not coalesced. The service
ranks at most the top `result_limit` values and does not backfill from below
that boundary after R7 staleness.

Hard limits are exactly:

- 500 read records per source-type/shift;
- 100 Project Knowledge manifest entries;
- 2000 admitted candidates before ranking;
- 20 requested/result candidates;
- 4 evidence projections.

Source/aggregate overflow returns `RETRIEVAL_LIMIT_EXCEEDED` without silent
truncation. Applying the explicit `result_limit` after complete bounded ranking
is not silent truncation and MUST be recorded in the receipt.

**Acceptance AC-06:** Golden and property tests independently recompute token
sets, the integer score, all seven tie fields, duplicate behavior, and each
limit boundary at N/N+1. Permutation, locale, repeated-run, Unicode, and score-
tie tests produce identical ordered canonical results.

### R7 - Single-unit use-time revalidation

After authentication and permission, every Ledger-backed execution MUST open
one `Ledger.transaction()` and pass its single `unit` token to assignment
admission, source reads, exact-id reloads, correction reads, and the final
assignment checks. No second Ledger unit may contribute to the same receipt.
This is a backend-transaction claim only, not a linearizability claim.

The service ranks bounded candidates, selects at most `result_limit`, then
reloads every selected source by exact id before projection. It MUST reconstruct
the current P3-C input and compare source digest, version union, correction
lineage, lifecycle and parent-shift observation, retention/erasure assertion,
content digest, chunk id, and revalidation token. It MUST re-run every selected
shift assignment immediately before returning and before leaving the unit.

Project Knowledge MUST instead recheck manifest entry, allowed consumer,
`INTERNAL` classification, source pin, current raw-byte pin digest,
local-index flag, owner, and retention assertion in the same execution. It
MUST NOT silently refresh a changed value into the ranked request.

Digest/version/correction/lifecycle/retention drift removes the individual
item and records only a safe reason. Assignment drift denies the entire
response. If no selected item remains, final outcome is `STALE_EVIDENCE`.
Local timeout or cancellation returns the R11 stopped variant; it never
produces a partial projection.

**Acceptance AC-07:** Instrumented InMemoryLedger and SqlLedger/SQLite tests
prove one transaction and one unit identity across every call, exact reload
and final assignment ordering, all seven drift classes, per-item removal,
whole-response assignment denial, all-stale behavior, no backfill, and no
silent refresh. PostgreSQL parity is required before any PostgreSQL claim.

### R8 - EvidenceProjectionV1 and context budget

`EvidenceProjectionV1` MUST reject unknown fields and contain exactly:

- complete `citation: CitationV1` from R9;
- `truth_class`, `field_selector`, and P3-A `sensitivity`;
- `content_snippet`;
- `snippet_start_codepoint` inclusive and `snippet_end_codepoint` exclusive;
- `snippet_digest_sha256` over exact snippet UTF-8 bytes;
- `projection_complete`, true IF AND ONLY IF the offsets cover the entire
  `redacted_normalized_text`.

The projection's `truth_class`, `field_selector`, digest, and offsets MUST equal
the same-named nested citation values. Construction rejects any mismatch.

It MUST NOT contain raw/redacted-away content, arbitrary path, full domain
object, or the complete P3-C provenance chain. The backend execution retains
the unchanged `RetrievalReadyV1`, including its existing maximum of 65536
characters and complete content/source/chunk identity.

Server maxima are exactly:

- 4 projection records;
- 1024 Unicode code points per snippet;
- 3072 UTF-8 bytes per snippet;
- 16384 canonical serialized UTF-8 bytes for the projection tuple;
- 4096 estimated input tokens;
- token estimate label `UTF8_BYTES_DIV_2_ESTIMATE_V1`, with value
  `(serialized_utf8_bytes + 1) // 2`.

The client may request only lower positive ceilings. For each revalidated
candidate, select a best lexical span by preferring a full-query phrase span
over a token span and then the lowest starting code-point offset. Let the span
midpoint be `floor((start + end) / 2)`. A text longer than the code-point budget
uses a clamped window of that length centered on the midpoint. If its UTF-8
bytes exceed the byte budget, remove one code point at a time from the side
farther from the match midpoint; equal distance removes from the high/end side.
The match span MUST remain present and every cut MUST be a Unicode boundary.
If the source interval containing the complete selected match cannot fit either
client snippet ceiling, omit that candidate's whole projection and continue in
rank order only within the already selected R6 `result_limit` boundary. If no
projection fits, return `CONTEXT_BUDGET_EXCEEDED`; never clip the match.

Take the top R6-ranked revalidated records up to the applied record ceiling.
If aggregate serialized-byte or estimate limits fail, remove the lowest-ranked
whole projection until both pass and record the omission count. Citation,
version, offsets, and provenance hashes MUST never be truncated. If no complete
identity plus non-empty snippet fits, return `CONTEXT_BUDGET_EXCEEDED` and
structurally omit projections/handoff under R11.

**Acceptance AC-08:** Boundary tests cover source lengths 65535/65536/65537,
code-point and multi-byte UTF-8 edges, phrase-versus-token selection,
lowest-offset ties, centered/clamped windows, deterministic byte trimming,
match preservation, snippet digest/offset/complete flag, whole-projection
removal, and every budget at N/N+1 without provenance truncation.

### R9 - CitationV1, RetrievalReceiptV1, and canonical hashes

The normative field sets, negative-receipt null semantics, citation-id binding,
stage language, closed nested schemas, and canonical hash preimages are defined
only by `docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md`. That appendix
is part of this V1 contract, MUST be reviewed and pinned with this SPEC, and
MUST NOT be independently weakened. Every result still returns one safe,
ephemeral receipt; P4-A1 performs zero audit or Ledger writes.

**Acceptance AC-09:** Schema and golden-byte tests prove exact fields,
exclusive safe id, eleven-stage order/language, timing constraints, canonical
preimages, independent hash recomputation, tamper sensitivity, and safe denied
receipts. Audit spies prove zero audit writes for every final outcome.

### R10 - FutureContextHandoffV1 and unchanged P3-B status

`FutureContextHandoffV1` MUST reject unknown fields and contain exactly:

- `retrieval_receipt_hash_sha256`, `evidence_set_hash_sha256`, and ordered
  `citation_ids`;
- sorted unique `classifications` and `sensitivities` from projections;
- `serialized_context_bytes`, `snippet_codepoints`, `projection_count`,
  `estimated_input_tokens`, and
  `token_estimate_method="UTF8_BYTES_DIV_2_ESTIMATE_V1"`;
- exact applied retrieval/context ceilings;
- local `elapsed_ms`, configured timeout, and timeout/cancellation outcome;
- `minimization_evidence_status="NOT_PROVEN"`;
- `placement_enforcement_status="NOT_EVALUATED"`;
- `runtime_caller_status="NO_LOAD_BEARING_CALLER"`;
- `provider_attempt_authorized=false` and `provider_attempts=0`.

It MUST contain no provider/model id, placement decision, provider tokenizer
claim, spend, usage, credential, or generated output. It is evidence for a
future context builder, not P3-B satisfaction. Future P4-A must separately
evaluate minimization, call `assert_placement_allowed`, calculate actual
provider input/output budget and call `assert_within_budget`, then enforce
`assert_not_terminated` immediately before and across provider execution.
Local retrieval termination facts do not substitute for that state.

**Acceptance AC-10:** Contract tests prove the exact fields and three unchanged
P3-C literals, classification/sensitivity derivation, exact budget/timing
facts, absence of provider/spend/placement fields, and false/zero provider
authority. Source and claim checks continue to report P3-B as not load-bearing.

### R11 - Ten-variant GovernedRetrievalResultV1 union

`GovernedRetrievalResultV1` MUST be a strict union of exactly ten structural
variants. Every variant contains only `contract_version="1.0"`, its closed
`outcome`, `receipt`, and `provider_attempts=0`, except the positive fields
explicitly listed below:

| Variant | Closed outcome literal | Positive-only fields |
|---|---|---|
| `EvidenceAvailableV1` | `EVIDENCE_AVAILABLE` | non-empty `projections` tuple, `future_context_handoff` |
| `NoEvidenceV1` | `NO_EVIDENCE` | none |
| `AccessDeniedV1` | `ACCESS_DENIED` | none |
| `CorpusUnavailableV1` | `CORPUS_UNAVAILABLE` | none |
| `StaleEvidenceV1` | `STALE_EVIDENCE` | none |
| `RetrievalLimitExceededV1` | `RETRIEVAL_LIMIT_EXCEEDED` | none |
| `RetrievalStoppedV1` | `RETRIEVAL_TIMEOUT` or `RETRIEVAL_CANCELLED` | none |
| `ContextBudgetExceededV1` | `CONTEXT_BUDGET_EXCEEDED` | none |
| `InvalidRequestV1` | `INVALID_REQUEST` | none |
| `InvariantFailureV1` | `INVARIANT_FAILURE` | none |

Only `EvidenceAvailableV1` may define the two positive fields, and its
projection tuple contains 1-4 values. Every negative schema structurally omits
both fields; null or empty placeholders are invalid. Denial/unavailable
variants disclose no protected counts. Expected empty/stale/limit/stopped/
budget failures are typed results without raw source, stack, or provider data.

P4-A1 MUST have no provider import, request model, adapter, or callable. A
future provider boundary may accept only a separately validated P4-A context
builder output derived from non-empty `EvidenceAvailableV1` plus successful
P3-B gates. It MUST NOT accept any P4-A1 negative variant directly.

**Acceptance AC-11:** Union construction tests prove exactly ten schemas,
every listed outcome discriminator, 1-4 positive projections, extra-field
rejection, and structural absence of projections/handoff on all negative
variants. Call tracing proves every branch has provider attempts zero and no
P4-A1 code path can resolve a provider symbol.

### R12 - V1 evolution, seven proof classes, and LPCI1-REF

All V1 models MUST reject unknown fields and enum values. A minor revision may
add only an optional field with an explicit fail-closed default and MUST NOT
change a canonical preimage. A new required field, relaxed authorization or
eligibility, changed normalization/score/hash meaning, changed corpus meaning,
or changed required field requires a new major version plus migration. There
is no permissive fallback to V1.

A future BUILD evidence packet MUST contain these seven proof classes:

1. schema and golden-byte/hash tests for request, result, citation, projection,
   handoff, and receipt;
2. static dependency/import/I/O tests for R1;
3. negative-leakage call spies proving zero protected reads before all R3
   gates;
4. InMemoryLedger and SqlLedger/SQLite parity for order, limits, denial, and
   revalidation, plus PostgreSQL parity before a PostgreSQL claim;
5. property tests for input/duplicate permutation, LF/CRLF, NFC/non-NFC,
   Unicode casefold, byte/code-point boundaries, score ties, budgets, and
   repeated execution;
6. adversarial digest/version/correction/lifecycle/retention/assignment drift
   plus continued missing-owner proof;
7. only in later P4-A authority, a provider spy proving every negative P4-A1
   result causes zero attempts.

P4-A1 SPEC/local BUILD uses zero provider calls and may claim only a local
provider-free deterministic retrieval foundation. Fresh real-provider proof is
mandatory only for a later claim about outbound governance, grounded answers,
provider failure behavior, or hosted execution.

`LPCI1-REF` is non-blocking for P4-A1 and remains separately governed in its
owning CVF repository. It is an entry gate before P4-A or P4-A2 DESIGN. Only
accepted LPCI1-REF evidence or a fresh operator-approved alternative reference
plan may satisfy that gate; it MUST NOT be silently waived. This downstream
tranche MUST NOT implement, repair, test, commit, or claim LPCI1-REF.

**Acceptance AC-12:** Version-compatibility tests reject every forbidden V1
change; the review evidence maps all seven proof classes to runnable future
tests without executing class 7 in P4-A1. Governance inspection confirms zero
provider/live calls, the exact P4-A1 claim, and the unchanged LPCI1-REF entry
gate before any P4-A/P4-A2 DESIGN.

## ADR-to-SPEC trace matrix

| ADR decision | SPEC requirement | Acceptance |
|---|---|---|
| Decision 1 | R1 owner/dependencies | AC-01 |
| Decision 2 | R2 request/validation | AC-02 |
| Decision 3 | R3 authorization order | AC-03 |
| Decision 4 | R4 corpus registry | AC-04 |
| Decision 5 | R5 source/digest owners | AC-05 |
| Decision 6 | R6 deterministic retrieval | AC-06 |
| Decision 7 | R7 use-time revalidation | AC-07 |
| Decision 8 | R8 projection/budget | AC-08 |
| Decision 9 | R9 citation/receipt | AC-09 |
| Decision 10 | R10 P3-B handoff | AC-10 |
| Decision 11 | R11 result union | AC-11 |
| Decision 12 | R12 evolution/proof/LPCI1-REF | AC-12 |

## Stop conditions

Stop on parent hash drift, a thirteenth requirement, missing acceptance mapping,
authorization after protected access, client scope widening, a generic or
unreviewed canonical digest, absent retention authority, provenance truncation,
Project Knowledge reclassification, negative-result positive fields, audit
write, provider/network/product-API/database call, implementation/test source,
roadmap/core-pin edit, failed repository guard, or authority beyond SPEC.

An independent review must return exactly `SPEC_REVIEW_PASS`,
`SPEC_REVIEW_CHANGES_REQUIRED`, or `SPEC_BLOCKED_SOURCE_OR_OWNER`. Only
`SPEC_REVIEW_PASS` may transfer this exact requirement packet to
`WORK_ORDER_AUTHOR`; it grants no BUILD authority.

## Claim boundary

This artifact specifies intended behavior only. It does not prove the package,
service, permission, digest owners, corpus registry, query engine, projection,
receipt, or result union exists. It does not prove canonical retrieval,
load-bearing P3-B gates, durable audit, provider grounding, RAG, vector/index,
persistence, live deployment, or production readiness.

P4-A1 may later close with dependency-blocked corpora still fail-closed, but it
MUST NOT claim confirmed-record retrieval until every applicable digest and
retrieval-retention owner is independently accepted and implemented.

## Next governed move

Obtain one consolidated independent SPEC review against the accepted ADR and
current source. Do not open a work order, implementation, test, provider call,
commit, push, or later-phase artifact before `SPEC_REVIEW_PASS`.
