# SPEC - P3-C Retrieval-Ready Data Contract

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Parent ADR: `docs/decisions/ADR_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`
- Parent ADR SHA-256: `f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`
- DESIGN R1 review: `docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_DESIGN_REREVIEW.md`
- DESIGN disposition: `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Risk: `R2`
- Control-chain phase: `SPEC`
- Status: `SPEC_R1_CANDIDATE_PENDING_INDEPENDENT_REREVIEW`
- Provider/product-API/POST calls: `0/0/0`

## Scope and normative language

This SPEC defines a pure local contract and deterministic constructor. It does
not define a query service, index, vector store, persistence layer, provider
adapter, router or authorization decision. `MUST`, `MUST NOT`, `EXACTLY` and
`IF AND ONLY IF` are normative.

The owner is a proposed new sibling Python package,
`packages/retrieval-contracts/`. The package does not exist in current source;
its creation requires a separately reviewed Work Order and BUILD.

## Source verification boundary

| Claimed source fact | Current source | Verified symbol or section | SPEC disposition |
|---|---|---|---|
| P3-A admitted envelope/candidate/result | `packages/refinery-bridge/src/refinery_bridge/input_models.py`; `packages/refinery-bridge/src/refinery_bridge/output_models.py` | `RefineryEnvelopeV1`, `ContextCandidateV1`, `RefineryResultV1` | Reuse exact classes; do not duplicate |
| P3-A source types | `packages/refinery-bridge/src/refinery_bridge/enums.py` | `SourceType` | Additive `CANONICAL_OPERATIONAL_RECORD` is new and requires BUILD authority |
| Canonical operational models | `packages/operations-domain/src/operations_domain/models.py` | `OperationalEvent`, `Task`, `CustomerRequest`, `Incident`, `Handover`, `Message`, `Correction`, `Shift` | Reuse exact classes |
| Report snapshot model/internals | `packages/operations-domain/src/operations_domain/report_models.py` | `Report`, `ReportContent.snapshot_digest`, `_canonical_bytes`, `_recompute_record_digest` | Stored digest shape is validated; private helpers validate already-canonical Report dict records and are not a public generic owner |
| Current application digest helpers | `apps/workspace-api/src/workspace_api/application/report_snapshot.py`; `apps/workspace-api/src/workspace_api/application/handover_service.py` | `compute_source_digest` | Exact existing helpers, but importing `workspace_api` is forbidden by the passed dependency design |
| Allowed-package generic record digest owner | repository search at SPEC base `42d12af` | no public owner in `operations_domain` or `refinery_bridge` for Event, Task, CustomerRequest, Incident, Handover, Report or Message | Return `SOURCE_DIGEST_OWNER_MISSING` unless an exact owner is added by a separately reviewed source change |
| Report manifest record digests | `packages/operations-domain/src/operations_domain/report_models.py` | `ReportSourceRef.source_digest`, `ReportContent._manifest_matches_records_exactly` | Valid only inside the matching immutable Report snapshot |
| Handover item digest | `packages/operations-domain/src/operations_domain/models.py` | `HandoverItem.source_digest` | Binds the referenced item source; not a digest of the Handover itself |
| Current package wiring | root `pyproject.toml`; package-local `pyproject.toml` files | pytest `pythonpath`; `refinery-bridge`; `operations-domain` | New sibling package/root path entry are proposed, not current truth |
| Data-scope status | `docs/cvf/CVF_CONTROL_MAPPING.md` | `data_scope` row | Callable but no runtime caller; minimization is not load-bearing |

## Normative requirements

### R1 - Closed enums

V1 MUST define only these values:

- `TruthClass`: `CANONICAL_OPERATIONAL_RECORD`, `ADVISORY_SOURCE_EVIDENCE`;
- `RecordType`: `OperationalEvent`, `Task`, `CustomerRequest`, `Incident`,
  `Handover`, `Report`, `Message`, `PROJECT_KNOWLEDGE`;
- `VersionKind`: `INTEGER_VERSION`, `SOURCE_VERSION_STRING`, `UNVERSIONED`;
- `RetentionDisposition`: `OWNER_ASSERTED_ACTIVE`,
  `OWNER_ASSERTED_EXPIRED`, `OWNER_ASSERTED_ERASED`, `OWNER_NOT_FOUND`;
- `TenantScopeStatus`: `NOT_MODELED`;
- `DataScopeStatus`: `NOT_EVALUATED`;
- `ResultKind`: `RETRIEVAL_READY`, `NOT_ADMITTED`;
- `NonAdmissionReason`: `REFINERY_RESULT_NOT_READY`,
  `CANDIDATE_BINDING_MISMATCH`, `UNKNOWN_SOURCE_TYPE`, `SOURCE_NOT_ELIGIBLE`,
  `SOURCE_VERSION_INVALID`, `SOURCE_DIGEST_OWNER_MISSING`,
  `SOURCE_DIGEST_MISMATCH`, `SOURCE_PROJECTION_MISMATCH`, `SCOPE_INVALID`,
  `TENANT_SCOPE_NOT_MODELED`, `LIFECYCLE_INVALID`, `STALE_SOURCE`,
  `RETENTION_OWNER_NOT_FOUND`, `RETENTION_NOT_ACTIVE`,
  `PROVENANCE_INVALID`, `DATA_SCOPE_EVIDENCE_INVALID`,
  `CONTRACT_VERSION_UNSUPPORTED`, `INVARIANT_VIOLATION`.

Unknown values MUST be rejected, not coerced or mapped to a permissive default.

### R2 - Strict model behavior and common bounds

Every V1 model MUST reject unknown fields. Integers MUST reject `bool`.
Identifiers MUST be non-empty strings of at most 128 Unicode code points after
surrounding-whitespace rejection. Digests MUST be lowercase hexadecimal SHA-256
of length 64. Datetimes MUST be timezone-aware UTC and serialize with `Z`.
Collections described as sorted/unique MUST reject unsorted or duplicate input.

Public errors and non-admission results MUST contain only closed reason tokens
and safe identifiers. They MUST NOT echo source text, redacted-away values,
credentials, exception messages or stack traces.

### R3 - Exact constructor input

`RetrievalContractInputV1` MUST contain exactly:

- `contract_version="1.0"`;
- one admitted `RefineryEnvelopeV1`;
- one `RefineryResultV1` whose disposition is `CANDIDATE_READY`;
- one matching `ContextCandidateV1` and `CandidateFingerprintV1` taken from
  that result;
- exactly one typed source value from R5;
- `field_selector` from R6;
- `source_cutoff_utc` and `observed_at_utc`;
- zero or one `Correction` lineage value;
- one `ScopeInputV1`;
- one `RetentionAssertionV1`;
- one `DataScopeEvidenceV1`;
- `tenant_required`, a strict boolean supplied by the future caller.

The public constructor MUST be total over arbitrary host-language payloads and
return the R18 union. It MUST NOT perform I/O or source discovery.

### R4 - P3-A candidate binding

The supplied candidate and candidate fingerprint MUST be object/value-equal to
the candidate and fingerprint embedded in the supplied `RefineryResultV1`.
The envelope source id, version, owner, link and source fingerprint MUST equal
their candidate/result counterparts, and the envelope raw-text fingerprint
MUST recompute exactly. The envelope raw text is constructor-only input and
MUST NOT appear in either R18 output branch.
The result MUST have nine `PASS` stage receipts, quality 100 and no duplicate,
quarantine or fallback receipt, as already enforced by P3-A.

Any mismatch returns `CANDIDATE_BINDING_MISMATCH`. A non-ready refinery result
returns `REFINERY_RESULT_NOT_READY`. P3-C MUST NOT construct, repair, upgrade or
reinterpret a P3-A candidate.

### R5 - Typed source union and eligibility

The source union and admission predicates are exact:

| Source value | Truth class | Admission predicate | Version kind/value |
|---|---|---|---|
| `OperationalEvent` | canonical | state in `CONFIRMED`, `CORRECTED`, `FROZEN` | integer `version >= 1` |
| `Task` | canonical | data state in `CONFIRMED`, `CORRECTED`, `FROZEN`; any valid task status | integer `version >= 1` |
| `CustomerRequest` | canonical | any persisted lifecycle status and non-null `shift_id` | integer `version >= 1` |
| `Incident` | canonical | status in `ACKNOWLEDGED`, `MITIGATING`, `RESOLVED`, `CLOSED` | integer `version >= 1` |
| `Handover` | canonical | status in `REVIEWED`, `ACKNOWLEDGED` | integer `version >= 1` |
| `Report` | canonical | status in `APPROVED`, `FROZEN`, `is_current=true` | integer report version plus snapshot digest |
| `Message` | advisory | persisted message, `source="INTERNAL"`, and exact R7 candidate linkage | `UNVERSIONED` |
| `ProjectKnowledgeSourceV1` | advisory | exact R7 source pin/candidate linkage | `SOURCE_VERSION_STRING` |

`Correction` and `Shift` are context-only inputs and MUST NOT be selected as a
chunk source. `REPORTED` Incident, `DRAFT` Handover, non-current Report,
ineligible data state and unknown type return `SOURCE_NOT_ELIGIBLE` or
`UNKNOWN_SOURCE_TYPE` deterministically.

### R6 - Closed field selectors and exact projection bytes

One admitted input produces exactly one field-bound candidate. The closed
selectors and pre-Refinery source text are:

| Record type | `field_selector` | Exact source text before P3-A |
|---|---|---|
| `OperationalEvent` | `title` | `record.title` |
| `Task` | `title` | `record.title` |
| `CustomerRequest` | `summary` | `record.summary` |
| `Incident` | `summary` | `record.summary` |
| `Handover` | `items/<item_id>/summary` | exact `summary` of that unique item id |
| `Report` | `content` | UTF-8 decode of the source-owner canonical JSON bytes for `Report.content` |
| `Message` | `text` | `record.text` |
| `PROJECT_KNOWLEDGE` | `document` | exact text fingerprinted by P3-A |

No joining, splitting, overlap, summarization, translation, semantic merge or
fallback selector is allowed. The selected exact source text MUST equal the
admitted P3-A envelope raw text. Missing item, duplicate item id, empty selected
text or any byte mismatch with the envelope/source fingerprint returns
`SOURCE_PROJECTION_MISMATCH`.

### R7 - Advisory linkage

For `Message`, envelope source type MUST be `INTERNAL_MESSAGE`, candidate
`source_id` MUST equal lowercase string form of `message_id`, and the SHA-256
and byte length of exact `message.text.encode("utf-8")` MUST equal the P3-A
source fingerprint. Envelope/candidate `source_version` MUST be exactly
`UNVERSIONED`. The SourceReference source digest is that fingerprint's SHA-256.
No Message authority or confirmed-truth claim follows.

`ProjectKnowledgeSourceV1` contains exactly `source_id`, `source_pin`,
`current_source_pin` and `source_owner_id`. All four values MUST match the
candidate fields as applicable; `source_pin` MUST equal `current_source_pin`
and candidate `source_version`. The source digest is the candidate source
fingerprint SHA-256. A stale pin returns `STALE_SOURCE`.

### R8 - Canonical-record projection and digest stop

Canonical source candidates require additive P3-A envelope source type
`CANONICAL_OPERATIONAL_RECORD`. Candidate `source_id` MUST equal the lowercase
record UUID, `source_version` MUST equal the decimal record version, and the R6
projection fingerprint MUST match the P3-A source fingerprint.

V1 MUST use a source-owned digest reachable through the passed dependency
direction. At the current source base:

- Event, Task, CustomerRequest, Incident, Handover and Report have no public
  digest owner in either allowed dependency package and MUST return
  `SOURCE_DIGEST_OWNER_MISSING`;
- `Report.content.snapshot_digest` is stored owner evidence, but its current
  recomputation helper lives under forbidden `workspace_api`; shape validation
  alone MUST NOT admit the Report;
- current application `compute_source_digest` helpers MUST NOT be imported or
  copied into `retrieval_contracts` merely to bypass the dependency boundary;
- `operations_domain.report_models._canonical_bytes` and
  `operations_domain.report_models._recompute_record_digest` are private
  ReportContent-validation helpers, not public digest-owner contracts;
  `retrieval_contracts` MUST NOT import, call, alias, wrap or copy either helper
  as a generic digest shortcut;
- a `ReportSourceRef.source_digest` may be used only for the exact record inside
  that same validated Report snapshot, never as a global record digest;
- `HandoverItem.source_digest` MUST NOT be used as the Handover digest.

Adding a public domain-owned digest later is a separately reviewed source
change with parity tests against the current application helpers. P3-C MUST NOT
hash a generic Pydantic dump and call it source authority.

### R9 - `VersionBindingV1` union

The version union has exact tagged shapes:

- integer: `kind`, `integer_version`; no string value;
- source string: `kind`, `source_version_string`; no integer value;
- unversioned: only `kind="UNVERSIONED"`.

Integer values are `>=1`. Source strings satisfy R2. Contradictory, empty or
multi-form values return `SOURCE_VERSION_INVALID`.

### R10 - `SourceReferenceV1`

The reference contains exactly `source_class`, `record_type`, nullable
`record_id`, `source_digest_sha256`, one R9 version, `observed_at_utc`,
`source_cutoff_utc`, nullable correction lineage, P3-A `source_id`,
`source_version`, source fingerprint, candidate fingerprint and the five
candidate rules-version fields.

`record_id` is required except for `PROJECT_KNOWLEDGE`. Cutoff MUST be no later
than observation. Correction lineage is allowed only when its record id/type
match the selected source and `previous_version < new_version ==` selected
integer version. Otherwise return `LIFECYCLE_INVALID`.

### R11 - `ScopeV1`

`ScopeV1` contains exactly `workspace_scope="shift-operations-workspace"`,
`tenant_scope_status="NOT_MODELED"`, sorted unique `shift_ids`, nullable
`effective_from_utc`, nullable `effective_to_utc`, and `observed_at_utc`.

Event, Task, Incident, Message and Report require exactly their one `shift_id`.
CustomerRequest requires its non-null `shift_id`. Handover requires exactly
`from_shift_id` and `to_shift_id`, sorted. Project knowledge requires zero
shift ids. More than two ids, wrong linkage or inverted effective time returns
`SCOPE_INVALID`. If `tenant_required=true`, return
`TENANT_SCOPE_NOT_MODELED`; the workspace name is not tenant authorization.

### R12 - `LifecycleObservationV1`

The lifecycle block contains source status/state, R9 version, nullable parent
Shift id/version/status, nullable Report status/snapshot digest, nullable
Correction lineage, `requires_use_time_revalidation=true`, and
`revalidation_token`.

Parent Shift observation is required for every shift-linked source. It MUST
match the source shift id and carry integer version `>=1`. Report observation
is required only for Report. Frozen parent/source status is observation, not an
immutability assertion.

### R13 - Retention and erasure

`RetentionAssertionV1` contains exactly disposition, `owner_id`,
`policy_version`, `checked_at_utc`, nullable `expires_at_utc`, nullable
`erased_at_utc`, and `source_evidence_id`.

Only `OWNER_ASSERTED_ACTIVE` with a non-expired assertion may admit. Active
forbids `erased_at_utc`. Expired requires expiry no later than checked time.
Erased requires erasure no later than checked time. Missing owner/evidence
returns `RETENTION_OWNER_NOT_FOUND`; expired/erased returns
`RETENTION_NOT_ACTIVE`. P3-C MUST NOT synthesize owner evidence or reuse raw-
message/quarantine retention as retrieval policy.

### R14 - Data-scope evidence remains non-load-bearing

`DataScopeEvidenceV1` contains exactly
`status="NOT_EVALUATED"`, `minimization_evidence_status="NOT_PROVEN"`,
`placement_enforcement_status="NOT_EVALUATED"`, and
`runtime_caller_status="NO_LOAD_BEARING_CALLER"`.

Any other value or any claim of allowed placement returns
`DATA_SCOPE_EVIDENCE_INVALID`. This block MUST NOT affect ready admission and
MUST NOT be presented as minimization, placement or authorization proof.

### R15 - Closed provenance

`ProvenanceV1` contains exactly the P3-A source/candidate fingerprints; all
nine ordered P3-A stage names/outcomes/control versions; the five candidate
rules versions; source reference digest/version; field selector; retention
evidence id/policy version; and constructor contract version.

All nine outcomes MUST be `PASS`. Values MUST match the bound P3-A result and
other V1 blocks. No extra hop, URL, provider receipt, free-form metadata or
caller assertion is allowed. Mismatch returns `PROVENANCE_INVALID`.

### R16 - Canonical JSON and `chunk_id`

Canonical JSON MUST use Unicode NFC strings and exactly:

```python
json.dumps(
    preimage,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

Floats, non-string map keys, unknown fields and non-NFC strings are forbidden.
The `content_digest_sha256` is SHA-256 of exact
`candidate.redacted_normalized_text.encode("utf-8")`.

The `chunk_id` is lowercase SHA-256 over canonical JSON containing exactly:
`contract_version`, `truth_class`, full `source_reference`, `field_selector`,
candidate fingerprint, full `scope`, full lifecycle observation excluding
`revalidation_token`, and `content_digest_sha256`. It excludes validation time,
data-scope evidence and all retention fields; retention participates in the
separate R17 use-time revalidation token.

### R17 - Revalidation token

The token is lowercase SHA-256 over canonical JSON containing exactly
`chunk_id`, source digest/version, source lifecycle, parent Shift
id/version/status, Report status/snapshot digest, correction lineage, and
retention disposition/owner/policy/evidence id.

The constructor computes it only from explicit input. A future retrieval caller
MUST re-read authoritative source, parent, correction and retention state and
recompute before serving. Any difference returns `STALE_SOURCE`; it MUST NOT
silently refresh or serve the prior chunk.

### R18 - Closed result union

`RetrievalContractResultV1` is exactly:

- `RetrievalReadyV1`: `kind="RETRIEVAL_READY"`, `contract_version="1.0"`,
  truth class, field selector, unchanged redacted normalized text, content
  digest, chunk id, source reference, scope, lifecycle, retention, provenance
  and data-scope evidence; or
- `RetrievalNonAdmissionV1`: `kind="NOT_ADMITTED"`,
  `contract_version="1.0"`, one R1 reason, nullable safe source id and nullable
  safe record id.

The branches have disjoint exact field sets. Non-admission contains no chunk,
text, digest beyond a safe source/record id, partial ready object or retry
claim. `RetrievalReadyV1` exists IF AND ONLY IF R4-R17 all pass.

When multiple defects exist, the constructor MUST select the first reason in
this fixed precedence: unsupported contract/structural invariant; P3-A result
or binding; unknown/ineligible source; version; projection; digest owner/digest
match; scope/tenant; lifecycle/staleness; retention; provenance; data-scope
evidence; final invariant. Within one class, the enum order in R1 is used.
Input order or exception order MUST NOT select the public reason.

### R19 - Determinism and ordering

Identical explicit input MUST produce byte-identical result JSON. Ready values
sort by `(truth_class, record_type, record_id-or-source_id, field_selector,
chunk_id)`. Input mapping order and equivalent timezone spelling MUST NOT alter
the result after strict UTC normalization. No wall clock, randomness, locale or
filesystem default may affect output.

### R20 - Package and dependency boundary

The proposed package MUST have its own `pyproject.toml` and
`src/retrieval_contracts/`. It may import only standard library, Pydantic,
`refinery_bridge` and `operations_domain`. Root pytest `pythonpath` may add only
`packages/retrieval-contracts/src` for this package.

`refinery_bridge` and `operations_domain` MUST NOT import
`retrieval_contracts`. The new package MUST NOT import `workspace_api`,
`operations_ledger`, `cvf_runtime`, FastAPI, SQLAlchemy, provider, vector/index
or retrieval runtime modules. Static import tests MUST enforce both directions.
The same tests MUST inspect imports and attribute access and fail if any
`retrieval_contracts` module imports, aliases, accesses, wraps or calls
`operations_domain.report_models._canonical_bytes` or
`operations_domain.report_models._recompute_record_digest`. Their existing
internal use inside `operations_domain.report_models` remains unchanged.

### R21 - I/O and external-effect prohibition

The constructor and models MUST make zero network, provider, database,
filesystem, environment, secret, clock, random, subprocess, router or ledger
calls. All time and owner assertions are explicit input. No BUILD test in this
tranche may claim that a runtime caller enforces retrieval or data placement.

### R22 - Schema evolution

V1 exact-field models reject unknown fields. Additive optional fields require a
new minor contract version and dual-version parser tests. Removed, renamed,
retyped, reinterpreted, newly required fields, enum changes and canonical-byte
changes require a new major version plus explicit migration. Unknown versions
return `CONTRACT_VERSION_UNSUPPORTED`; no best-effort parsing is allowed.

### R23 - Required fixture matrix

Repository-owned synthetic fixtures MUST independently cover at least:

1. non-mapping input and unknown field;
2. non-ready/mismatched P3-A result;
3. every eligible and one ineligible lifecycle per source type;
4. unknown source type;
5. each VersionBinding branch and every contradictory combination;
6. stored Report snapshot digest shape plus missing allowed recomputation owner;
7. missing digest owner for Event, Task, CustomerRequest, Incident, Handover
   and Report;
8. forbidden generic Pydantic-dump digest substitution and a static negative
   fixture proving `retrieval_contracts` cannot import, alias, access, wrap or
   call `operations_domain.report_models._canonical_bytes` or
   `_recompute_record_digest`;
9. Message exact linkage and text mismatch;
10. Project Knowledge current and stale pins;
11. all R6 selectors, including missing Handover item;
12. zero/one/two shift scope plus wrong/more-than-two/inverted cases;
13. `tenant_required=true` fail-closed behavior;
14. correction valid and wrong-record/wrong-version lineage;
15. each retention disposition and stale active assertion;
16. malformed/non-load-bearing data-scope evidence;
17. all-nine-PASS provenance and each mismatch class;
18. canonical JSON NFC, key order, NaN/float and unknown-field rejection;
19. independent `content_digest_sha256`, `chunk_id` and revalidation-token
    recomputation;
20. deterministic repeat/order and stale revalidation;
21. non-admission disclosure safety;
22. import/I-O prohibitions and zero provider/network calls.

## Acceptance criteria

- **AC-01:** Independent review verifies the immutable ADR hash, DESIGN pass,
  every R1-R23 requirement and returns `SPEC_REVIEW_PASS`, waiver `NONE`.
- **AC-02:** Source review confirms the new owner is proposed, not existing,
  and confirms every source-verification row against build-base source.
- **AC-03:** Contract tests prove all closed enums, exact fields, strict bounds,
  union disjointness, unknown-version behavior and safe non-admission.
- **AC-04:** Eligibility tests cover the complete R5 matrix without permissive
  fallback or promotion of advisory evidence to canonical truth.
- **AC-05:** Digest tests prove stored Report evidence is insufficient without
  an allowed recomputation owner, prove advisory P3-A fingerprint paths and
  prove fail-closed absence for every ownerless canonical type.
- **AC-06:** Projection, scope, lifecycle, correction, retention and provenance
  tests cover every R23 negative case and never return a partial chunk.
- **AC-07:** Independent golden-byte tests recompute content digest, chunk id
  and revalidation token from R16/R17 without calling implementation helpers.
- **AC-08:** Property tests prove deterministic output, stable ordering and
  disclosure-safe total non-admission for arbitrary invalid payloads.
- **AC-09:** Import/static-call tests prove the R20 dependency graph and R21
  zero-I/O boundary; root/package test wiring stays exact and acyclic.
- **AC-10:** Repository, session-state, catalog, file-size, JSON, diff and
  secret gates pass for the exact future authorized changed set.
- **AC-11:** BUILD uses zero provider/product-network/POST calls. Any later
  runtime governance claim requires a separate R2 Work Order, real caller and
  fresh provider-backed evidence.
- **AC-12:** Registry/catalog wording, if later changed, remains `partial` and
  states contract-only/no-runtime-caller/no-tenant/no-placement enforcement.

## Cheap alternatives retained

- Keep P3-A output unchanged and let a future caller use it directly: rejected
  because it lacks record/scope/lifecycle/retention/revalidation binding.
- Put Python in schema-only `workspace-contracts`: rejected because it widens
  a current source class and repeats the DESIGN F1 defect.
- Add a retrieval service/vector store now: rejected because contract proof is
  cheaper and no retrieval runtime is authorized.
- Invent generic record digests to produce positive fixtures: rejected; typed
  fail-closed results are cheaper and honest.

## Stop conditions and transfer boundary

Stop at the first parent hash drift, unresolved source fact, ambiguous schema,
new source owner, out-of-scope path, I/O/provider attempt, secret exposure,
partial-ready behavior or failing gate. Do not draft a Work Order, build a
package or consume a provider call from this SPEC.

Only independent `SPEC_REVIEW_PASS` with no unresolved finding may transfer to
`WORK_ORDER_AUTHOR`. That transfer grants Work Order authoring only, not BUILD,
retrieval, provider calls, persistence, vector/index, deployment or production
authority.
