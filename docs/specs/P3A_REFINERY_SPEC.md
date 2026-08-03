# SPEC — P3-A Deterministic Refinery Boundary

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent ADR: `docs/decisions/ADR_2026-08-03_P3A_REFINERY.md`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1: `docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_1.md`
- Amendment SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Design Amendment 2: `docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_2.md`
- Amendment 2 SHA-256: `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`
- Risk: `R2`
- Control-chain phase: `SPEC`
- Status: `SPEC_CANDIDATE_PENDING_INDEPENDENT_REVIEW`

## Scope and vocabulary

This SPEC defines a pure, deterministic local Python boundary. It accepts all
input and versioned rules explicitly and performs no network, provider,
database, filesystem discovery, environment-secret access, raw persistence or
quarantine persistence. Its public output is the closed union in R9/R24;
structural pre-admission decides whether the nine-stage pipeline can safely
begin. `MUST`, `MUST NOT`, `EXACTLY` and `IF AND ONLY IF` are normative.

## Normative requirements

### R1 — Closed enums

The implementation MUST define only these V1 values:

- `SourceType`: `PROJECT_KNOWLEDGE`, `INTERNAL_MESSAGE`,
  `EXTERNAL_UNTRUSTED_FIXTURE`;
- `Sensitivity`: `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`, in that
  non-decreasing order and exactly aligned with `data-policy.yaml`;
- `Disposition`: `CANDIDATE_READY`, `NO_CANDIDATE_DUPLICATE`,
  `NO_CANDIDATE_QUARANTINED`, `NO_CANDIDATE_FALLBACK`;
- `StageOutcome`: `PASS`, `FAIL`, `NOT_RUN`;
- `DedupeStatus`: `UNIQUE`, `EXACT_SOURCE_MATCH`, `REDACTED_TEXT_MATCH`,
  `DIGEST_COLLISION_SUSPECTED`, `INSUFFICIENT_CONTEXT`.

Unknown enum values MUST be rejected, not coerced.

### R2 — Exact pipeline order

Every admitted `RefineryResultV1` MUST contain exactly one receipt for each
stage, in this order:

1. `ENVELOPE`;
2. `NORMALIZATION`;
3. `TERMINOLOGY`;
4. `CLASSIFICATION`;
5. `CONFLICT`;
6. `REDACTION`;
7. `DEDUPE`;
8. `QUALITY`;
9. `CANDIDATE_ADMISSION`.

No stage may be reordered, omitted or repeated. Structural pre-admission in R9
is a parser/model-construction gate, not a tenth stage; its rejection branch
contains no stage receipts.

### R3 — Closed reason vocabularies

The quarantine reason is exactly one of `PROVENANCE_MISMATCH`,
`AMBIGUOUS_VALUE`, `UNSUPPORTED_TRANSFORM`,
`DEDUPE_CONTEXT_INVALID`, `DIGEST_COLLISION_SUSPECTED`, `POLICY_DRIFT`,
`REDACTION_FAILED`, `REDACTION_RESIDUE`, `CONFLICT_DETECTED`,
`QUALITY_INCOMPLETE`, `STAGE_INVARIANT_ERROR`.

The fallback reason is exactly one of `QUARANTINE_ROUTE_UNAVAILABLE`,
`STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR`. A fallback receipt MUST also set
`caller_action = "USE_EXISTING_NON_AI_RULE_WORKFLOW"`.

`StageReason` is a separate closed enum containing exactly `STAGE_PASS`,
`PROVENANCE_MISMATCH`, `UNSUPPORTED_TRANSFORM`,
`POLICY_DRIFT`, `AMBIGUOUS_LOCAL_TIME`, `AMBIGUOUS_ACTION_STATE`,
`CONFLICT_DETECTED`, `REDACTION_FAILED`, `REDACTION_RESIDUE`,
`DEDUPE_CONTEXT_INVALID`, `EXACT_SOURCE_MATCH`, `DIGEST_COLLISION_SUSPECTED`,
`INSUFFICIENT_CONTEXT`, `QUALITY_INCOMPLETE`, `STAGE_UNAVAILABLE`,
`STAGE_INVARIANT_ERROR`, `PRIOR_STAGE_FAILED`. R17 closes the permitted
stage/outcome combinations. Unknown values in any of these three reason types
MUST be rejected and the types MUST NOT be substituted for one another.

### R4 — Safe identifiers and versions

`source_id`, `source_version`, `source_owner_id`, `scope_id`, `prior_source_id`,
`owner_id`, `sink_id` and every rule/policy version MUST be Unicode strings of
1..128 code points after surrounding-whitespace rejection. They MUST contain
no control characters, line breaks, path traversal segment `..`, URI userinfo,
secret value or raw message content. `source_link` MUST be an opaque Unicode
string of 1..512 code points under the same prohibitions. The refinery MUST NOT
dereference or interpret it as authority.

### R5 — Time, text and collection bounds

All datetimes MUST be timezone-aware UTC and serialized with `Z`; naive or
non-UTC values are invalid. `raw_text` MUST be strictly decoded Unicode, 1..65536
code points, with no unpaired surrogate. Labels and terminology tokens MUST be
1..128 code points. `topic_labels` MUST contain at most 64 values. Any list
described as unique MUST reject duplicates rather than silently remove them at
the boundary.

### R6 — FingerprintV1

`FingerprintV1` has exactly `sha256`, `sha512`, `byte_length`. Digests MUST be
lowercase hexadecimal of lengths 64 and 128. `byte_length` MUST be a non-negative
integer, not `bool`, and equal the measured byte length of locally computed
content. Fingerprints received from callers MUST be structurally validated.

### R7 — Canonical JSON

Every fingerprinted JSON preimage MUST be serialized exactly as:

```python
json.dumps(
    preimage,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

Preimages MUST reject floats, nulls, non-string mapping keys and unknown fields.
Set-like lists MUST be unique and sorted by Unicode code-point order before
serialization. No platform locale or default encoding may affect bytes.

### R8 — Three non-interchangeable fingerprints

The implementation MUST expose distinct types and constructors for:

1. `source_fingerprint`, over exact `raw_text.encode("utf-8")` before any
   normalization;
2. `dedupe_content_fingerprint`, over the exact R19 preimage;
3. `candidate_fingerprint`, over the exact R23 preimage.

No cross-type comparison, assignment or constructor substitution is allowed.
Digest equality is not a signature, source authority or delivery receipt.

### R9 — Structural pre-admission and RefineryEnvelopeV1

The public boundary accepts arbitrary host-language input and returns the closed
R24 union. Structural pre-admission is total and first validates exact field
set, schema, type, R4/R5 bounds, strict Unicode encodability and disclosure
safety. It also establishes that `raw_text.encode("utf-8")` is computable and
that source owner/link are safe public provenance.

Any structural failure returns `PreAdmissionRejectionV1` with exactly:
`schema_version="1.0"`, `kind="PRE_ADMISSION_REJECTION"`,
`reason="INVALID_ENVELOPE"`, one-or-more sorted unique `safe_error_codes`, and
`caller_action="USE_EXISTING_NON_AI_RULE_WORKFLOW"`. Safe codes are closed to
`INVALID_SCHEMA_VERSION`, `FIELD_SET_MISMATCH`, `INVALID_SOURCE_ID`,
`INVALID_SOURCE_VERSION`, `INVALID_SOURCE_LINK`, `INVALID_SOURCE_TYPE`,
`INVALID_RAW_TEXT`, `INVALID_RECEIVED_AT`, `INVALID_DECLARED_SENSITIVITY`,
`INVALID_SOURCE_OWNER_ID`, `INVALID_SOURCE_FINGERPRINT`. Unknown/empty codes or
extra fields are invalid.

That branch contains no disposition, input/provenance value, source field,
fingerprint, text, stage/quality receipt, route, candidate, matched value,
exception or stack. It fingerprints/refers to no invalid value, fabricates no
provenance and makes no quarantine/storage/deletion/acknowledgment/retry claim.
Non-mapping, missing, extra, unpaired-surrogate, malformed-fingerprint and
disclosure-unsafe inputs MUST all yield this fixed safe branch deterministically.

Only structurally admitted input constructs `RefineryEnvelopeV1`, with exactly
`schema_version="1.0"`, `source_id`, `source_version`, `source_link`,
`source_type`, `raw_text`, `received_at`, `declared_sensitivity`,
`source_owner_id`, `source_fingerprint`. ENVELOPE locally recomputes the exact
text fingerprint. A supplied mismatch fails with `PROVENANCE_MISMATCH`; the
full result uses the safe local fingerprint plus validated owner/link and MUST
NOT echo the mismatched fingerprint. No public branch contains `raw_text`.

### R10 — Injected ControlBundleV1

The caller MUST supply exactly nine non-empty R4 version tokens and associated
deterministic controls: `envelope_schema_version`,
`normalization_rules_version`, `terminology_rules_version`,
`classification_rules_version`, `conflict_rules_version`,
`redaction_rules_version`, `dedupe_rules_version`, `quality_rules_version`,
`candidate_admission_rules_version`. Receipt `control_version` sources map
exactly, in R2 order, to those nine fields. Substitution, defaulting, omission,
or cross-stage reuse is invalid. A `NOT_RUN` receipt retains its own mapped
version; pre-admission rejection has none.

`ControlBundleV1` construction rejects missing, malformed, unknown, defaulted or
substituted version fields before boundary execution; it returns no refinery
output and exposes only a sanitized configuration code. The boundary is total
over arbitrary envelope payload only when supplied this valid typed bundle.
Runtime drift against an explicit accepted-policy version fails the applicable
stage as `POLICY_DRIFT`; an explicitly versioned but unavailable executable
control yields `STAGE_UNAVAILABLE`. Thus every admitted result can populate all
nine receipt versions without invention. Controls MUST be data-only or pure
local callables and MUST NOT perform I/O. R19/R23 fingerprint preimages retain
only their fixed four/five transform/quality versions; other versions remain
visible in receipts and are not falsely included in candidate digests.

### R11 — Safe normalization

`NORMALIZATION` may perform only Unicode NFC, CRLF/CR to LF, bounded horizontal
whitespace cleanup and canonical formatting of already explicit fully qualified
values. It MUST be deterministic and idempotent. It MUST NOT translate,
paraphrase, infer timezone/AM-PM, change tense/action state or fill missing
values. In particular, `11h40` MUST NOT become `23:40`.

### R12 — Terminology matching

`TERMINOLOGY` may replace only an exact reviewed token-boundary match from the
injected map. Matching and replacement order MUST be deterministic; overlapping
or cyclic rules are invalid. A rule may not assert that `đang xuống` equals
`đang xử lý` unless that exact equivalence exists in the reviewed rule set.
Receipts contain rule id and safe offsets/counts, never matched text.

### R13 — Classification and conflict

`CLASSIFICATION` MUST emit one sensitivity plus sorted unique topic labels.
Declared sensitivity is a floor; detectors may only retain or escalate it.
Unknown detector output, enum drift or downgrade attempt fails with
`POLICY_DRIFT`. Topic labels convey no data placement or retrieval authority.

`CONFLICT` MUST reject unresolved ambiguous local time, mutually inconsistent
explicit values, unsupported transform requests and ambiguous action state.
It emits `AMBIGUOUS_VALUE`, `CONFLICT_DETECTED` or `UNSUPPORTED_TRANSFORM` as
applicable and MUST NOT choose a plausible interpretation.

### R14 — Redaction

`REDACTION` applies deterministic high-confidence rules to the normalized text
and emits typed placeholders such as `<redacted:credential>`. Replacement spans
MUST be in bounds, non-overlapping and applied in a deterministic order.
Malformed/overlapping rules or unsafe replacement yield `REDACTION_FAILED`.
Suspected sensitive content without a safe replacement or any detector residue
yields `REDACTION_RESIDUE`. Receipts expose only rule/type, safe offsets and
counts; they MUST NOT echo matched values.

### R15 — DedupeContextV1

`DedupeContextV1` has exactly `scope_id`, inclusive UTC `window_start`,
`window_end`, and `records`. The window MUST not be inverted. `records` contains
0..500 unique `DedupeRecordV1` values, each with exactly `scope_id`,
`prior_source_id`, `observed_at`, `source_fingerprint` and optional
`dedupe_content_fingerprint`. Every record scope MUST equal the context scope;
every observed time MUST be inside the inclusive window; prior source ids MUST
be unique. Invalid context yields `DEDUPE_CONTEXT_INVALID`. Missing context
yields `INSUFFICIENT_CONTEXT` and follows the no-candidate mapping in R21.

### R16 — Dedupe mechanics

Stage 7 runs only after R14 passes. It compares source fingerprints only with
source fingerprints and dedupe-content fingerprints only with their own type.
All three fingerprint fields must equal for a normal match. Two fingerprints
are collision-suspected exactly when they are not full-triple equal and
(`sha256` is equal OR `sha512` is equal). This includes one equal digest with
the other digest/length unequal, and both digests equal with unequal length.
If neither digest is equal, the pair is neither a match nor a collision signal.
Collision has precedence over every normal-match result.

Exact source equality yields `EXACT_SOURCE_MATCH`; otherwise exact content
equality yields `REDACTED_TEXT_MATCH`; otherwise `UNIQUE`. Matching records are
sorted by `(observed_at, prior_source_id)`; the first is the selected safe id,
while all safe match ids and the count remain in the receipt. Input record
permutation MUST NOT change the receipt. Content match is advisory and does not
suppress a candidate; source match yields duplicate disposition. Neither proves
global identity or exactly-once delivery.

### R17 — StageReceiptV1 and fail-stop execution

Each stage receipt has exactly `stage`, `control_version`, `outcome`,
`reason_codes`, nullable typed `dedupe_status`, `safe_counts`, `safe_offsets`
and `safe_ids`. Collections are bounded, sorted and contain no
raw/matched/redacted secret value. `control_version` is populated only from the
exact R10 stage mapping. `reason_codes` is exactly one `StageReason`. The only
legal nine-receipt language is either
`PASS` repeated nine times, or zero or more `PASS` receipts followed by exactly
one `FAIL` and then only `NOT_RUN` receipts. Therefore a receipt is `NOT_RUN` IF
AND ONLY IF an earlier receipt is `FAIL`; an orphan/premature `NOT_RUN` is
invalid. A `NOT_RUN` receipt has reason `PRIOR_STAGE_FAILED` and empty counts,
offsets and ids; its stage MUST NOT execute. A `PASS` receipt has only
`STAGE_PASS`. A `FAIL` receipt has one reason allowed by this table:

| Stage | Permitted `FAIL` reasons |
|---|---|
| `ENVELOPE` | `PROVENANCE_MISMATCH`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `NORMALIZATION` | `UNSUPPORTED_TRANSFORM`, `POLICY_DRIFT`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `TERMINOLOGY` | `UNSUPPORTED_TRANSFORM`, `POLICY_DRIFT`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `CLASSIFICATION` | `POLICY_DRIFT`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `CONFLICT` | `AMBIGUOUS_LOCAL_TIME`, `AMBIGUOUS_ACTION_STATE`, `CONFLICT_DETECTED`, `UNSUPPORTED_TRANSFORM`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `REDACTION` | `REDACTION_FAILED`, `REDACTION_RESIDUE`, `POLICY_DRIFT`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `DEDUPE` | `DEDUPE_CONTEXT_INVALID`, `EXACT_SOURCE_MATCH`, `DIGEST_COLLISION_SUSPECTED`, `INSUFFICIENT_CONTEXT`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `QUALITY` | `QUALITY_INCOMPLETE`, `STAGE_UNAVAILABLE`, `STAGE_INVARIANT_ERROR` |
| `CANDIDATE_ADMISSION` | `STAGE_INVARIANT_ERROR`, `STAGE_UNAVAILABLE` |

The first `FAIL` maps through R21. `AMBIGUOUS_LOCAL_TIME` and
`AMBIGUOUS_ACTION_STATE` map to quarantine reason `AMBIGUOUS_VALUE`;
`INSUFFICIENT_CONTEXT` maps to `DEDUPE_CONTEXT_INVALID`; identically named
stage/quarantine reasons map directly. `STAGE_UNAVAILABLE` and
`STAGE_INVARIANT_ERROR` always take R21 fallback precedence. Unexpected
exceptions are sanitized to `STAGE_INVARIANT_ERROR`; messages/stacks are not
public output. Model construction MUST reject every other reason/outcome/stage
combination.

`dedupe_status` is null for every non-DEDUPE receipt and DEDUPE `NOT_RUN`.
For executed DEDUPE its only legal combinations are:

| Outcome/reason | `dedupe_status` |
|---|---|
| `PASS` / `STAGE_PASS` | `UNIQUE` or `REDACTED_TEXT_MATCH` |
| `FAIL` / `EXACT_SOURCE_MATCH` | `EXACT_SOURCE_MATCH` |
| `FAIL` / `DIGEST_COLLISION_SUSPECTED` | `DIGEST_COLLISION_SUSPECTED` |
| `FAIL` / `INSUFFICIENT_CONTEXT` | `INSUFFICIENT_CONTEXT` |
| `FAIL` / `DEDUPE_CONTEXT_INVALID` | null |
| `FAIL` / `STAGE_UNAVAILABLE` or `STAGE_INVARIANT_ERROR` | null |

Exact-source match therefore stops QUALITY/CANDIDATE_ADMISSION as `NOT_RUN`
and selects duplicate disposition under R21; the separate quality receipt uses
only actual PASS stages and cannot upgrade it. `UNIQUE` and advisory
`REDACTED_TEXT_MATCH` allow later stages. Every unlisted tuple is invalid, and
consumers MUST NOT infer status from ids/counts.

### R18 — QuarantineRouteV1

The caller-supplied route has exactly `owner_id`, `sink_id`, `policy_version`,
`retention_days=30`, `sink_available`. Source owner, quarantine owner and sink
are distinct fields; equality does not merge their authority. A quarantine
disposition requires a valid route with the current policy version, exact
30-day hint and `sink_available=True`. Otherwise disposition is fallback with
`QUARANTINE_ROUTE_UNAVAILABLE`. The result is only a routing/retention hint and
MUST NOT claim storage, deletion, delivery or acknowledgment.

### R19 — DedupeContentV1

The exact canonical preimage is:

`schema_version="1.0"`, `redacted_normalized_text`, `sensitivity`, sorted unique
`topic_labels`, `normalization_rules_version`, `terminology_rules_version`,
`classification_rules_version`, `redaction_rules_version`.

It contains no source identity/version/owner/link/time, quality, candidate
fingerprint, provider or retrieval field. It is constructed only after stage 6
PASS and fingerprinted under R7.

### R20 — QualityReceiptV1

The quality receipt has exactly `rules_version`, `provenance`, `normalization`,
`protection`, `integrity`, `total`, `threshold=100`. Each component is exactly
0 or 25; total is their integer sum. Mapping is: stage 1; stages 2–3 with no
ambiguity; stages 4–6; stage 7 plus no stage-5 conflict. Only actual PASS
receipts contribute. Quality cannot upgrade an earlier failure. The score is
control coverage only—not truth, probability, semantic confidence or production
quality. This separate receipt is always present on `RefineryResultV1`, even if
the QUALITY stage is `NOT_RUN`; skipped/failed components are zero, including
integrity after an exact-source duplicate.

### R21 — Total disposition precedence

Disposition MUST be selected mechanically in this order:

1. unavailable stage/invariant, or required quarantine with invalid/unavailable
   route: `NO_CANDIDATE_FALLBACK`;
2. valid `EXACT_SOURCE_MATCH`: `NO_CANDIDATE_DUPLICATE`;
3. any R3 quarantine reason, collision, invalid/missing dedupe context, or
   quality below 100: `NO_CANDIDATE_QUARANTINED` when R18 is valid, otherwise
   fallback by step 1;
4. exactly nine PASS receipts plus quality 100: `CANDIDATE_READY`.

`REDACTED_TEXT_MATCH` alone remains eligible for step 4.

### R22 — Typed no-candidate receipts

`DuplicateReceiptV1` has exactly dedupe status, selected prior source id, sorted
match ids and match count. `QuarantineReceiptV1` has exactly reason, source
owner/link/fingerprint and the R18 route/hint. `FallbackReceiptV1` has exactly
reason and `caller_action`. Exactly one matching receipt is present for its
no-candidate disposition; the other two are absent. All three are absent for a
ready result. No receipt contains raw text or matched secret values.

### R23 — ContextCandidateV1

The exact candidate preimage has only:

1. `schema_version="1.0"`;
2. `redacted_normalized_text`;
3. `sensitivity`;
4. sorted unique `topic_labels`;
5. `source_id`, `source_version`, `source_owner_id`, `source_link`, and exact
   `source_fingerprint` triple;
6. exact `normalization_rules_version`, `terminology_rules_version`,
   `classification_rules_version`, `redaction_rules_version`,
   `quality_rules_version`;
7. `quality_score`, plus `provenance`, `normalization`, `protection`, `integrity`
   integer component scores.

No optional or extra V1 field is allowed. It excludes raw text, confirmed-fact
status, provider instruction, embedding and retrieval metadata. The
`candidate_fingerprint` is computed from this full preimage under R7 and stored
beside, not inside, it.

### R24 — RefineryBoundaryOutputV1 invariant

`RefineryBoundaryOutputV1` is exactly
`PreAdmissionRejectionV1 | RefineryResultV1`. Presence of the exact
`kind="PRE_ADMISSION_REJECTION"` field selects only the R9 rejection schema;
`RefineryResultV1` forbids `kind`. Thus the closed field sets are unambiguous
without adding a field to the parent-fixed result.

Every `RefineryResultV1` contains exactly `schema_version="1.0"`, `disposition`,
`source_owner_id`, `source_link`, `source_fingerprint`, the nine R17 receipts,
R20 quality receipt, nullable `context_candidate`, nullable
`candidate_fingerprint`, and the three nullable R22 receipts. Candidate and
candidate fingerprint are non-null IF AND ONLY IF disposition is
`CANDIDATE_READY`; otherwise both are null. Construction MUST reject every
contradictory combination. A pre-admission rejection obeys only R9 and cannot be
coerced into a disposition-bearing result or satisfy any candidate claim.

### R25 — Determinism and monotonic properties

For identical explicit inputs/controls the full boundary-output bytes MUST be
identical, including arbitrary invalid-input rejection.
Normalization MUST be idempotent. Dedupe result MUST be invariant to record
permutation. Raising declared sensitivity with otherwise identical inputs MUST
never lower output sensitivity. Adding a detector hit MUST never lower output
sensitivity or improve a failed protection component.

### R26 — I/O and disclosure prohibition

Boundary and pipeline modules MUST have no network/provider/database calls, filesystem or
environment discovery, secret reads, wall-clock reads or randomness. Current
time is accepted only as explicit test/caller data when needed. Public models,
receipts, exceptions, logs and snapshots MUST not disclose raw input or matched
sensitive values. This applies equally to pre-admission and typed-control
construction failures.

### R27 — Fixture matrix

Repository-owned synthetic fixtures MUST cover at least these 28 independent
cases: non-mapping pre-admission; missing-field pre-admission; extra-field
pre-admission; unpaired-surrogate pre-admission; disclosure-unsafe-link
pre-admission; malformed-fingerprint pre-admission; valid structural fingerprint
mismatch with safe full result; control-version substitution rejection; valid
ready; NFC/line-ending/whitespace idempotence; explicit qualified
time; ambiguous `11h40`; unsupported action reinterpretation; exact reviewed
terminology; terminology overlap/cycle rejection; sensitivity retention;
sensitivity escalation; downgrade/policy drift; high-confidence redaction;
redaction overlap; redaction residue; conflict; exact source duplicate;
cross-source redacted-content match; collision suspicion; invalid/out-of-window
dedupe context; unavailable quarantine route; unexpected invariant fallback.

### R28 — Existing fixture treatment

The existing fixture containing `11h40` MUST remain a negative fixture after
adding required source metadata. It MUST produce no candidate and MUST NOT be
silently corrected. A separate fully qualified-time fixture proves the positive
path. All fixtures are synthetic and prove no external ingest or operational
truth.

### R29 — Package and dependency boundary

Implementation is confined to a deterministic package under
`packages/refinery-bridge` plus explicitly authorized tests/fixtures/contracts.
It MUST NOT import application routers, ledgers, provider adapters, retrieval
code or `cvf_runtime.data_scope`. Sensitivity parity with `data-policy.yaml`
MUST be verified by a contract test; this does not make data scope load-bearing.

### R30 — Claim boundary

P3-A evidence may claim only deterministic local refinement, typed fail-closed
receipts and reproducible candidate bytes. It MUST NOT claim confirmed truth,
raw retention, external/remote ingest, provider behavior, DLP/minimization
enforcement, P3-B/P3-C, retrieval, RAG, learning, Integration Edge, production
readiness or AI governance.

## Acceptance criteria

- **AC-01:** Independent review verifies immutable parent ADR and both amendment
  hashes, resolves every R1–R30 requirement and returns `SPEC_REVIEW_PASS`, no
  waiver.
- **AC-02:** Unit tests prove all closed enums, schemas, unknown-field rejection,
  bounds, UTC constraints, the total R9 pre-admission branch, invalid-control
  constructor rejection, all nine exact control-version sources/substitution
  rejection and contradictory union/result construction failures.
- **AC-03:** Golden-byte tests independently recompute all three typed
  fingerprints using R7, prove cross-type substitution is rejected, and cover
  both-digests-equal/length-different plus each-single-digest-equal vectors.
- **AC-04:** Tests prove exact nine-stage order, the complete `PASS^9` or
  `PASS* FAIL NOT_RUN*` language, rejection of orphan/premature `NOT_RUN`, empty
  non-executed receipt data, sanitized invariant fallback and total R21
  precedence. Exact-source match MUST be DEDUPE `FAIL`, later receipts `NOT_RUN`,
  integrity zero and duplicate disposition. A static cross-reference check
  verifies every normative R-number resolves to its intended requirement/schema.
- **AC-05:** Property tests prove determinism, normalization idempotence, dedupe
  permutation invariance, sensitivity monotonicity and stable safe bytes for
  arbitrary invalid-envelope rejection.
- **AC-06:** Dedupe tests prove inclusive window/scope/bound validation,
  deterministic selection, full-triple equality, collision precedence, exact
  source suppression and advisory cross-source content matching. Collision
  vectors cover both digests equal with length unequal, each single digest equal,
  and neither digest equal. Public-schema assertions distinguish typed `UNIQUE`
  from `REDACTED_TEXT_MATCH` without interpreting ids/counts.
- **AC-07:** Redaction/adversarial tests prove no matched-value leakage through
  either union branch, control-construction failure, receipt, exception, log or
  snapshot surface, and prove no fabricated provenance.
- **AC-08:** The R27 matrix passes, including the retained negative `11h40`
  fixture and separate positive fully qualified-time fixture.
- **AC-09:** A contract test proves exact sensitivity parity with
  `data-policy.yaml` while imports/call tracing prove no `data_scope`, provider,
  network, database, filesystem discovery or secret access.
- **AC-10:** Repository, JSON, session-state, file-size, catalog/diff and secret
  gates pass for the exact authorized changed set.
- **AC-11:** BUILD and local review use zero provider calls. Any later assertion
  that this boundary gates AI/provider context requires a separate R2 work order,
  real runtime caller and fresh real-provider evidence.
- **AC-12:** Registry/catalog status, if changed, remains `partial` and states the
  bounded local/no-runtime-caller boundary; no roadmap successor is activated by
  P3-A SPEC or BUILD alone.

## Stop conditions

Stop at the first failing acceptance gate, out-of-scope path, parent/amendment
hash drift, secret exposure, attempted I/O/provider call, ambiguous contract or
candidate-on-failure behavior. Do not waive, retry a provider, or continue to a
later control-chain phase. SPEC review pass transfers only to
`WORK_ORDER_AUTHOR`; it grants no BUILD authority.
