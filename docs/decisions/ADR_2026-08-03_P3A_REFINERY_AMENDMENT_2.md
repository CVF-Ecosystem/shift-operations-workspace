# ADR Amendment 2 — P3-A Admission and Receipt Constructibility

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent ADR: `docs/decisions/ADR_2026-08-03_P3A_REFINERY.md`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1: `docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_1.md`
- Design Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Failed SPEC review SHA-256: `dba16f97407a7e0f1e49afa462346acf68bc0224d48e718f7b11c5b402898549`
- Failed SPEC re-review SHA-256: `a39555ab980adb5e28148763e4d28764b845da5590ca07eaed32a317cc78e3a4`
- Risk: `R2`
- Control-chain phase: `DESIGN`
- Status: `DESIGN_AMENDMENT_2_PENDING_INDEPENDENT_REVIEW`

## Trigger and bounded authority

Independent SPEC review F1-F4 were repaired and independently closed. The
regression re-review then returned `REVIEW_FAIL`, no waiver, on F5-F7:

1. structurally invalid or disclosure-unsafe input cannot construct the
   parent's mandatory non-null safe provenance result without echo/fabrication;
2. ready `UNIQUE` and advisory `REDACTED_TEXT_MATCH` outcomes have no typed
   public location;
3. three mandatory stage receipt versions have no normative source.

F5 changes the parent result invariant, so it cannot be resolved silently in
SPEC. This amendment supersedes only the admission/result union, public dedupe
status and stage-version source decisions described below. Parent ADR and
Amendment 1 remain binding everywhere else.

## Amendment Decision 1 — Structural pre-admission precedes the nine stages

The public boundary returns a closed tagged union:

```text
RefineryBoundaryOutputV1 = PreAdmissionRejectionV1 | RefineryResultV1
```

Structural pre-admission is a parser/model-construction gate, not a tenth
pipeline stage and not a successful envelope receipt. It decides whether the
untrusted input can safely construct the non-null provenance fields required by
`RefineryResultV1`. The reviewed nine-stage order applies only after structural
pre-admission succeeds.

Structural pre-admission validates the exact field set, schema version, field
types, bounds, strict Unicode encodability and disclosure safety of every
envelope value. It also establishes that `raw_text.encode("utf-8")` can be
computed and that `source_owner_id` and `source_link` are safe to return. Any
structural failure returns only `PreAdmissionRejectionV1`; it does not enter
ENVELOPE, construct nine stage receipts, route quarantine or claim persistence.

An input reaches ENVELOPE only if every required structural field is present,
typed, bounded, encodable and safe. At that point the implementation locally
recomputes `source_fingerprint`. If the caller-supplied structurally valid
fingerprint differs, ENVELOPE fails with `PROVENANCE_MISMATCH` and the full
`RefineryResultV1` uses the safe locally recomputed fingerprint plus validated
source owner/link. No caller-supplied mismatched fingerprint is echoed as
provenance.

This split means `INVALID_ENVELOPE` is a pre-admission rejection reason in V1.
`PROVENANCE_MISMATCH` remains a stage/quarantine reason after safe construction.
The parent statement that every result has nine receipts and non-null source
provenance is narrowed to every `RefineryResultV1`, not to the union's
pre-admission branch.

## Amendment Decision 2 — Exact pre-admission rejection schema

`PreAdmissionRejectionV1` contains exactly:

1. `schema_version = "1.0"`;
2. `kind = "PRE_ADMISSION_REJECTION"`;
3. `reason = "INVALID_ENVELOPE"`;
4. sorted unique `safe_error_codes`, containing one or more values from the
   closed enum below;
5. `caller_action = "USE_EXISTING_NON_AI_RULE_WORKFLOW"`.

The closed safe error codes are:

- `INVALID_SCHEMA_VERSION`;
- `FIELD_SET_MISMATCH`;
- `INVALID_SOURCE_ID`;
- `INVALID_SOURCE_VERSION`;
- `INVALID_SOURCE_LINK`;
- `INVALID_SOURCE_TYPE`;
- `INVALID_RAW_TEXT`;
- `INVALID_RECEIVED_AT`;
- `INVALID_DECLARED_SENSITIVITY`;
- `INVALID_SOURCE_OWNER_ID`;
- `INVALID_SOURCE_FINGERPRINT`.

The branch contains no disposition, source id/version/owner/link/fingerprint,
raw or normalized text, stage/quality receipt, route, candidate, matched value,
exception message or stack. It does not say the input was quarantined, stored,
deleted, acknowledged or retried. Error codes identify invalid fields only and
never include field values. Model construction rejects unknown/empty codes or
extra fields.

The parser is total over arbitrary host-language input: an unpaired surrogate,
non-mapping input, missing field, extra field, invalid link, secret-like unsafe
value or unencodable text can always produce this fixed safe branch without
fingerprinting, reflecting or fabricating provenance. Identical invalid input
under identical explicit schema controls yields identical rejection bytes.

## Amendment Decision 3 — Typed dedupe status on the stage receipt

The uniform `StageReceiptV1` adds one nullable field:

```text
dedupe_status: DedupeStatus | null
```

It is null for every non-DEDUPE stage and when DEDUPE is `NOT_RUN`. For an
executed DEDUPE stage it is governed exactly as follows:

| DEDUPE outcome/reason | `dedupe_status` |
|---|---|
| `PASS` / `STAGE_PASS` | `UNIQUE` or `REDACTED_TEXT_MATCH` |
| `FAIL` / `EXACT_SOURCE_MATCH` | `EXACT_SOURCE_MATCH` |
| `FAIL` / `DIGEST_COLLISION_SUSPECTED` | `DIGEST_COLLISION_SUSPECTED` |
| `FAIL` / `INSUFFICIENT_CONTEXT` | `INSUFFICIENT_CONTEXT` |
| `FAIL` / `DEDUPE_CONTEXT_INVALID` | null |
| `FAIL` / `STAGE_UNAVAILABLE` or `STAGE_INVARIANT_ERROR` | null |

`EXACT_SOURCE_MATCH` is therefore added to the closed stage-reason enum and is
permitted only on DEDUPE `FAIL`. This closes the receipt language: exact-source
duplicate stops later stages and takes duplicate disposition precedence;
collision/missing/invalid context stop later stages and take their reviewed
fail-closed dispositions. A separate always-present quality receipt computes
only from stages that actually passed and cannot upgrade the failure.

`UNIQUE` and `REDACTED_TEXT_MATCH` are the only successful DEDUPE statuses.
The latter remains advisory, permits later stages to run and is distinguishable
from `UNIQUE` through the typed public field. Safe selected/match ids and counts
remain in the receipt. `DuplicateReceiptV1` remains present only for the final
`NO_CANDIDATE_DUPLICATE` disposition and does not replace stage status.

Every other outcome/reason/status combination is model-invalid. No consumer may
infer status heuristically from counts or ids.

## Amendment Decision 4 — Exact control version for every stage

The injected pure local control bundle contains exactly nine non-empty bounded
version tokens and their associated deterministic controls:

1. `envelope_schema_version`;
2. `normalization_rules_version`;
3. `terminology_rules_version`;
4. `classification_rules_version`;
5. `conflict_rules_version`;
6. `redaction_rules_version`;
7. `dedupe_rules_version`;
8. `quality_rules_version`;
9. `candidate_admission_rules_version`.

To avoid calling schema/algorithm versions “rule sets,” the receipt field is
renamed from `rule_set_version` to `control_version`. Its source mapping is
positionally exact:

| Stage | `control_version` source |
|---|---|
| `ENVELOPE` | `envelope_schema_version` |
| `NORMALIZATION` | `normalization_rules_version` |
| `TERMINOLOGY` | `terminology_rules_version` |
| `CLASSIFICATION` | `classification_rules_version` |
| `CONFLICT` | `conflict_rules_version` |
| `REDACTION` | `redaction_rules_version` |
| `DEDUPE` | `dedupe_rules_version` |
| `QUALITY` | `quality_rules_version` |
| `CANDIDATE_ADMISSION` | `candidate_admission_rules_version` |

Substitution, defaulting, omission or reuse from another stage is invalid. A
`NOT_RUN` receipt still carries its own mapped explicit control version, because
the version describes the control that was skipped, not fabricated execution.
Pre-admission rejection has no stage receipt or control version.

The exact `ContextCandidateV1` preimage remains unchanged and contains only the
five parent-fixed normalization, terminology, classification, redaction and
quality versions. The exact Amendment 1 `DedupeContentV1` preimage remains
unchanged with its four content-transform versions. The additional versions
are visible in the full stage receipt sequence; neither candidate fingerprint
is misrepresented as a digest of the whole public result.

## Amendment Decision 5 — Required SPEC and evidence updates

The repaired SPEC must:

- replace the universal result claim with the exact tagged union and test
  pre-admission branch totality over non-mapping, missing, extra, unencodable,
  disclosure-unsafe and malformed-fingerprint inputs;
- state exactly when locally recomputed safe provenance permits a full
  `PROVENANCE_MISMATCH` result and prohibit fabricated provenance;
- add `dedupe_status` and the exact outcome/reason/nullability matrix above,
  including public `UNIQUE` versus `REDACTED_TEXT_MATCH` tests;
- add `EXACT_SOURCE_MATCH` to the closed stage-reason table and prove later
  receipts are `NOT_RUN` while quality cannot upgrade duplicate disposition;
- rename receipt `rule_set_version` to `control_version`, bind the nine exact
  sources and test stage-version substitution rejection;
- retain the already closed F1-F4 repairs and regress all R/AC contracts.

All evidence remains deterministic and local with zero provider/network calls.
The no-raw/no-secret disclosure tests apply to both union branches and every
error/log/snapshot surface.

## Preserved design and claim boundary

Parent ADR `57ec06fc…e696e` and Amendment 1 `dc091f2b…f0e4a` otherwise remain
binding: corrected nine-stage order after admission, three non-interchangeable
fingerprints, syntax-only normalization, separate sensitivity/topics,
caller-scoped advisory dedupe, no raw/quarantine persistence, closed fallback,
100/100 control coverage, exact candidate preimage, deterministic fixtures and
pure local execution.

This amendment does not authorize SPEC continuation, WORK_ORDER, BUILD,
provider/network calls, remote ingest, P3-B/P3-C, runtime `data_scope`,
retrieval/RAG, learning, confirmed truth or production claims. Only independent
`DESIGN_AMENDMENT_REVIEW_PASS`, no waiver, may return authority to
`SPEC_AUTHOR`.

