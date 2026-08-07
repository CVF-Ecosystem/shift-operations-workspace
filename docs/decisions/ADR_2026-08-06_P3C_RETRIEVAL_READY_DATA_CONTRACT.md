# ADR - P3-C Retrieval-Ready Data Contract

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- DESIGN base: `6cfa12877033f56fce982b5a06ce8d70c08a9abf`
- Parent INTAKE: `docs/decisions/INTAKE_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`
- INTAKE review: `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Risk: `R2`
- Control-chain phase: `DESIGN`
- Status: `DESIGN_R1_CANDIDATE_PENDING_INDEPENDENT_REREVIEW`
- Provider/product-API/POST calls: `0/0/0`

## Context

P3-A produces a deterministic redacted `ContextCandidateV1`, but that value is
not retrieval-ready. It has no canonical operational record binding, retrieval
scope, correction/freeze observation, retention/erasure disposition or use-time
revalidation contract. `data_scope` also has no load-bearing AI caller and
does not accept minimization evidence.

P3-C must define the stable local contract before P4-A1 may implement search or
indexing. The design must not make contract work depend on a vector database,
provider call, runtime retrieval service or a new tenant subsystem.

## DESIGN R1 repair note

Independent review returned `DESIGN_REVIEW_CHANGES_REQUIRED` with one finding,
`P3C-DESIGN-F1`: Decision 1 incorrectly described schema-only
`workspace-contracts` as an existing wired Python package. R1 replaces only
that owner/dependency decision and its direct consequence text. Decisions 2-10
remain unchanged and passed review as written. No waiver is used.

## Decision 1 - New bounded sibling Python owner `retrieval-contracts`

Current `packages/workspace-contracts/` is a schema-only directory: it has no
`pyproject.toml`, Python source tree or root `pythonpath` entry, and tests read
its JSON files directly. P3-C will not silently convert that surface into a
Python package.

The P3-C models, exported schema and deterministic reference constructor belong
to one explicit new sibling package:

`packages/retrieval-contracts/`

It follows the established package pattern used by `refinery-bridge` and
`operations-domain`:

- package-local `pyproject.toml`;
- `src/retrieval_contracts/` Python namespace;
- explicit root test `pythonpath` entry;
- package-local contract/schema export and tests;
- one new module-registry entry created only during an authorized BUILD.

`retrieval-contracts` may import the existing `refinery_bridge` result models
and `operations_domain` canonical models. The dependency direction is exactly:

`retrieval-contracts` -> `refinery-bridge`

`retrieval-contracts` -> `operations-domain`

Neither existing package currently imports `retrieval_contracts`; future
boundary tests must keep both reverse imports forbidden. The new package must
not import `workspace-api`, `operations-ledger`, `cvf-runtime`, provider or
retrieval runtime modules. This makes the proposed direction acyclic without
reclassifying a schema directory as an existing Python package.

The constructor accepts explicit in-memory values only. It performs no ledger,
database, filesystem discovery, environment, network, provider or policy
lookup. Application/runtime ownership remains P4-A1.

Rejected alternatives:

- adding retrieval semantics to P3-A pipeline stages, because Refinery must
  remain source-cleaning and non-retrieval;
- placing the constructor in schema-only `workspace-contracts`, because that
  would silently widen its current source class and wiring;
- creating a retrieval service/runtime now, because no query/index behavior is
  authorized; the new package is a contract/constructor boundary only;
- duplicating operational models inside a standalone schema-only package.

## Decision 2 - Two truth classes and an exact source eligibility matrix

Every output declares one of two truth classes:

- `CANONICAL_OPERATIONAL_RECORD`: a current persisted domain record that meets
  the per-type eligibility rule below;
- `ADVISORY_SOURCE_EVIDENCE`: a P3-A candidate that remains evidence/advisory
  material and must never be presented as confirmed operational truth.

| Source type | Truth class | Eligibility | Version binding |
|---|---|---|---|
| `OperationalEvent` | canonical | `CONFIRMED`, `CORRECTED`, or `FROZEN` | required integer `version >= 1` |
| `Task` | canonical | data state `CONFIRMED`, `CORRECTED`, or `FROZEN`; task status is retained, including terminal/cancelled | required integer `version >= 1` |
| `CustomerRequest` | canonical | any persisted lifecycle status | required integer `version >= 1` from the domain model |
| `Incident` | canonical | `ACKNOWLEDGED`, `MITIGATING`, `RESOLVED`, or `CLOSED` | required integer `version >= 1` |
| `Handover` | canonical | `REVIEWED` or `ACKNOWLEDGED` | required integer `version >= 1` |
| `Report` | canonical | `APPROVED` or `FROZEN` | required report version plus snapshot digest |
| `Message` | advisory evidence | persisted message linked to an admitted P3-A candidate | typed `UNVERSIONED`; canonical digest required |
| `PROJECT_KNOWLEDGE` | advisory evidence | admitted P3-A candidate with current source pin | typed `SOURCE_VERSION_STRING`; no record id |
| `Correction` | lineage only | never chunked independently; binds target record and previous/new version | target-version transition only |
| `Shift` | scope/lifecycle anchor only | never chunked independently | shift version/status observation |

`REPORTED` incidents, `DRAFT` handovers, non-admitted Refinery inputs and all
unknown source types return typed non-admission. Adding a source type is a
schema-versioned change, not a permissive default.

Canonical operational projection requires an additive P3-A source vocabulary
value `CANONICAL_OPERATIONAL_RECORD`. The projection text and metadata are
created deterministically from an allowlisted source field before Refinery.
This is an integration extension, not a new Refinery stage or semantic rewrite.
Until SPEC source-verifies this extension, canonical-record admission remains
blocked; advisory P3-A candidates do not silently become canonical truth.

## Decision 3 - Exact source reference and version union

`SourceReferenceV1` contains:

- `source_class`, `record_type`, optional `record_id` and required
  `source_digest_sha256`;
- exactly one version form: `INTEGER_VERSION`, `SOURCE_VERSION_STRING`, or
  `UNVERSIONED`;
- `observed_at_utc` and `source_cutoff_utc`;
- optional correction lineage `(correction_id, previous_version,
  new_version)` only when it targets the same record/version transition;
- P3-A `source_id`, `source_version`, source/candidate fingerprints and all
  five rules-version fields.

The canonical operational digest uses the source-owning canonical JSON shape,
not a generic Pydantic dump guessed by P3-C. Existing Report/Handover digest
helpers may be reused only where their exact source set matches. SPEC must map
each record type to its owning digest function or return
`SOURCE_DIGEST_OWNER_MISSING`.

## Decision 4 - One deterministic field-bound chunk per candidate

V1 creates exactly one `FIELD_BOUND` chunk from one admitted P3-A candidate.
There is no arbitrary token/character splitting, overlap, summarization,
translation, embedding or semantic merge.

The chunk contains:

- `contract_version = "1.0"`;
- `field_selector` from a closed per-source allowlist;
- the P3-A `redacted_normalized_text` unchanged;
- source reference, scope, lifecycle, retention and provenance blocks;
- `content_digest_sha256` over the exact UTF-8 text;
- `chunk_id` as lowercase SHA-256 over canonical JSON of contract version,
  truth class, source reference, field selector, candidate fingerprint, scope,
  lifecycle and content digest.

Canonical JSON is UTF-8, NFC, lexicographically sorted keys, compact separators,
JSON booleans/null, and no NaN/Infinity. `chunk_id` deliberately excludes
volatile validation timestamps and includes no raw/redacted-away value.

Stable ordering is `(truth_class, record_type-or-source-class, record_id-or-
source_id, field_selector, chunk_id)`.

## Decision 5 - Scope is descriptive and tenant-required use fails closed

`ScopeV1` contains:

- `workspace_scope = "shift-operations-workspace"` as a contract namespace,
  not an authorization or tenant claim;
- `tenant_scope_status = "NOT_MODELED"` and no tenant id;
- zero, one or two sorted unique shift ids (two only for a Handover);
- optional `effective_from_utc`, `effective_to_utc` and required
  `observed_at_utc`.

Missing required shift linkage, an inverted time range or more than two shift
ids returns `SCOPE_INVALID`. Any caller requiring tenant isolation must reject
`NOT_MODELED` with `TENANT_SCOPE_NOT_MODELED`. Shift assignment and this scope
block do not prove authorization; P4-A1 must evaluate the current principal and
assignment before retrieval.

## Decision 6 - Lifecycle observation never becomes an immutability claim

`LifecycleObservationV1` carries source status/state, source version form,
parent shift id/version/status when applicable, report status/snapshot digest
when applicable, and correction lineage.

Every admitted value has `requires_use_time_revalidation = true`. Its
`revalidation_token` hashes the stable chunk id plus source digest/version,
source lifecycle, parent-shift version/status, correction lineage and retention
disposition. A future retrieval caller must re-read authoritative state and
recompute the token before returning a chunk.

Parent shift `FROZEN` is not treated as universal immutability because the
current correction path may record a post-freeze correction. Any mismatch
returns `STALE_SOURCE`; it never silently refreshes or serves the old chunk.

## Decision 7 - Retention and erasure are owner assertions, not P3-C policy

`RetentionDispositionV1` is exactly one of:

- `OWNER_ASSERTED_ACTIVE`;
- `OWNER_ASSERTED_EXPIRED`;
- `OWNER_ASSERTED_ERASED`;
- `OWNER_NOT_FOUND`.

It carries owner id, policy version, checked time, optional expiry and erasure
times, and source evidence id. Only `OWNER_ASSERTED_ACTIVE` may produce a
retrieval-ready value. All other values produce typed non-admission.

P3-C does not convert the existing 365-day raw-message or 30-day quarantine
rules into retrieval retention. Unless an owning source explicitly declares a
retrieval-use disposition, the result is `RETENTION_OWNER_NOT_FOUND`. This
means the initial implementation may prove valid fail-closed behavior while
producing no ready canonical-record fixture; it must not invent indefinite
retention merely to make a positive test pass.

## Decision 8 - Provenance is a closed deterministic chain

`ProvenanceV1` binds:

1. P3-A source fingerprint and candidate fingerprint;
2. all nine P3-A stage receipt outcomes and rules versions;
3. canonical source reference/digest/version;
4. field selector and content digest;
5. scope and lifecycle observations;
6. retention owner assertion;
7. P3-C contract version, chunk id and revalidation token.

Ready admission requires nine P3-A `PASS` receipts, quality score 100, no
quarantine/fallback/duplicate disposition, and exact candidate fingerprint
recomputation. Provenance receipts carry stable ids, digests, enums and counts
only; they never copy raw text, secrets or redacted originals.

## Decision 9 - Data-scope and minimization remain NOT_EVALUATED

The contract carries the P3-A sensitivity and these exact fields:

- `minimization_status = "NOT_PROVEN"`;
- `placement_status = "NOT_EVALUATED"`;
- `placement_receipt = null`.

P3-A redaction and 100/100 quality do not prove minimization. P3-C never calls
`assert_placement_allowed` and never selects a provider placement. P3-B/P4 may
later add a separately governed receipt after a load-bearing caller evaluates
current policy. A consumer must reject outbound/provider use while status is
not evaluated.

## Decision 10 - Typed result union and schema evolution

The pure constructor returns exactly one of:

- `RetrievalReadyRecordV1` with one `RetrievalChunkV1`; or
- `RetrievalNonAdmissionV1` with sorted unique reason codes and safe source ids.

Closed reason codes include:

`REFINERY_CANDIDATE_INVALID`, `SOURCE_TYPE_UNSUPPORTED`,
`SOURCE_STATE_INELIGIBLE`, `SOURCE_VERSION_INVALID`,
`SOURCE_DIGEST_OWNER_MISSING`, `SOURCE_DIGEST_MISMATCH`, `SCOPE_INVALID`,
`TENANT_SCOPE_NOT_MODELED`, `CORRECTION_LINEAGE_INVALID`, `STALE_SOURCE`,
`RETENTION_OWNER_NOT_FOUND`, `RETENTION_EXPIRED`, `ERASURE_APPLIED`,
`CANONICALIZATION_FAILED`, and `CONTRACT_INVARIANT_ERROR`.

Unknown fields/enums fail validation. V1 additive changes may only add optional
fields with an explicit default that preserves fail-closed behavior. New
required fields, changed digest preimages, relaxed eligibility or enum meaning
requires a new major contract version and migration plan. There is no silent
fallback to V1.

## Deterministic admission algorithm

The future reference constructor runs in this order:

1. strict input/result shape validation;
2. P3-A candidate/receipt/fingerprint validation;
3. source eligibility and truth-class resolution;
4. source digest/version/correction validation;
5. scope and lifecycle validation;
6. retention/erasure owner validation;
7. exact content digest and chunk-id computation;
8. provenance and revalidation-token binding;
9. ready/non-admission result construction.

The first failed step returns a typed non-admission result; later steps are not
run. Expected validation failures are data, not exceptions. Unexpected
invariants return `CONTRACT_INVARIANT_ERROR` without raw content leakage.

## Acceptance approach for future SPEC

SPEC must require at minimum:

- exact schema/field/enum and canonical-byte golden tests;
- per-source eligibility/version/digest matrix tests;
- negative tests for every non-admission code;
- tenant-required, missing-owner, expired, erased, correction and stale-token
  adversarial tests;
- proof that raw/redacted-away values never occur in result/errors/receipts;
- cross-platform LF/CRLF and Unicode canonicalization tests;
- dependency/import tests proving zero app/ledger/provider/network access;
- no positive canonical-record ready fixture until retention owner and the
  additive P3-A source mapping are source-verified.

No provider call is needed to prove this local deterministic contract. A later
claim about live retrieval or outbound AI governance requires separately
authorized real-provider evidence.

## Consequences and bounded cost

Benefits:

- one explicit bounded Python owner, no retrieval service or vector store;
- explicit source truth and no invented tenant/retention authority;
- stale/corrected/erased material fails closed;
- P4-A1 receives a deterministic contract and revalidation obligation.

Costs:

- current owner gaps intentionally prevent a broad positive ready fixture;
- one new sibling package, root pythonpath entry and module-registry record are
  required instead of silently widening schema-only `workspace-contracts`;
- canonical operational sources need a source-verified additive P3-A mapping;
- P4-A1 must still implement current authorization and revalidation.

One consolidated independent DESIGN review must report all foreseeable
source/dependency/contract findings together. Same-scope repairs retain the
review authority. At repair round three without a new root cause, stop with
`REVIEW_COST_ESCALATION_REQUIRED`.

## Rejected expansion

This DESIGN does not authorize retrieval/query/ranking, vector/index storage,
background sync, provider calls, P3-B placement enforcement, P4, tenant
creation, retention policy creation, ledger mutation, deployment or production
claims. The rejected governed-plan runner branch remains unrelated and parked.

## Claim boundary

This ADR is a design candidate only. No P3-C schema, constructor, chunk,
retention/erasure enforcement, tenant isolation, revalidation runtime,
retrieval, RAG or provider behavior exists from this document.

## Next governed move

Obtain one consolidated independent DESIGN review against the accepted INTAKE
and cited current source. Only `DESIGN_REVIEW_PASS` may transfer the exact
contract decisions to `SPEC_AUTHOR`. No SPEC drafting or implementation is
authorized before that review.
