# ADR — P3-A Deterministic Refinery Boundary

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent INTAKE: `docs/decisions/INTAKE_2026-08-03_P3A_REFINERY.md`
- INTAKE review: `INTAKE_REVIEW_PASS`, no waiver
- Risk: `R2`
- Control-chain phase: `DESIGN`
- Status: `DESIGN_CANDIDATE_PENDING_INDEPENDENT_REVIEW`

## Context

P3-A must turn the contract-only `refinery-bridge` into a real local boundary
before any retrieval or LLM context work. It must clean and classify candidate
input without confirming operational truth, inventing missing values, owning
raw-source retention or claiming that `data_scope` is load-bearing.

The current YAML contract is insufficient: it has no versioned provenance,
quarantine, data-quality, stage receipt or fallback result. The existing
fixture is not golden truth because it lacks required source metadata, changes
ambiguous `11h40` to `23:40`, and may over-interpret `đang xuống` as already
processing the incident.

## Decision 1 — Pure local package and dependency boundary

Implement a deterministic Python package under `packages/refinery-bridge`.
The pipeline accepts explicit values and injected versioned rules; it performs
no network, provider, database, filesystem discovery or environment-secret
access. It may use repository dependencies already present, but it does not
import application routers, ledgers, provider adapters or retrieval code.

P3-A does not call `cvf_runtime.data_scope`. Instead, its sensitivity enum and
contract tests stay exactly aligned with `data-policy.yaml`. P3-B owns the
future runtime caller that consumes a successful P3-A receipt.

## Decision 2 — Versioned input envelope and bounded provenance

The logical `RefineryEnvelope` contains:

- `schema_version = "1.0"`;
- non-empty `source_id`, `source_version` and bounded opaque `source_link`;
- `source_type` from `PROJECT_KNOWLEDGE`, `INTERNAL_MESSAGE`, or
  `EXTERNAL_UNTRUSTED_FIXTURE`;
- `raw_text` as a strictly decoded Unicode string;
- timezone-aware UTC `received_at`;
- declared sensitivity from `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, or
  `RESTRICTED`;
- `source_owner_id`, distinct from the source link and quarantine owner;
- `source_fingerprint` containing lowercase SHA-256, lowercase SHA-512 and byte
  length over `raw_text.encode("utf-8")` before any normalization.

This fingerprint proves only the exact text field supplied to the boundary. It does
not prove an upstream envelope, signature, sender, channel or exactly-once
delivery. P3-A never stores or deletes raw input.

## Decision 3 — Fixed fail-closed stage order

The pipeline order is:

1. envelope/schema/provenance validation;
2. safe syntactic normalization;
3. terminology matching;
4. duplicate analysis;
5. sensitivity classification and topic labeling;
6. redaction;
7. ambiguity/conflict evaluation;
8. data-quality coverage calculation;
9. context-candidate admission.

Every stage emits a typed receipt with `stage`, `rule_set_version`, `outcome`,
stable reason codes and safe counts/offsets. Receipts never echo secrets or raw
matched values. A required-stage failure makes candidate admission impossible.

## Decision 4 — Normalization never paraphrases

Allowed normalization is limited to deterministic syntax:

- Unicode NFC;
- canonical line endings;
- bounded whitespace cleanup;
- exact token-boundary terminology mapping from an injected, versioned map;
- canonical formatting only for already explicit, fully qualified values.

No fuzzy substitution, translation, tense/action reinterpretation, timezone
guess or AM/PM inference is permitted. `11h40` remains unresolved and yields
`AMBIGUOUS_LOCAL_TIME`; `đang xuống` cannot become `đang xử lý` without an
explicit reviewed terminology rule proving equivalence.

## Decision 5 — Dedupe is advisory, caller-scoped and mechanically bounded

P3-A has no dedupe store. `DedupeContextV1` contains a non-empty `scope_id`,
inclusive UTC `window_start`/`window_end`, and at most 500 unique prior records.
Each `DedupeRecordV1` is the exact tuple `(scope_id, prior_source_id,
observed_at, source_fingerprint, candidate_fingerprint?)`. `observed_at` must
fall inside the window; duplicate prior ids, inverted windows, out-of-window
records or malformed fingerprints make the context invalid.

A fingerprint is exactly `(sha256, sha512, byte_length)`. An exact source match
requires all three fields equal inside the same scope/window. If one digest
matches while the other digest or byte length differs, the result is
`DIGEST_COLLISION_SUSPECTED` and is quarantined. A candidate match uses the same
three-field equality over canonical redacted-candidate bytes. Match selection is
deterministic: sort matching records by `(observed_at, prior_source_id)` and use
the first only for the receipt; all match ids/count remain recorded safely.

Results are `UNIQUE`, `EXACT_SOURCE_MATCH`, `REDACTED_TEXT_MATCH`,
`DIGEST_COLLISION_SUSPECTED`, or `INSUFFICIENT_CONTEXT`.
`EXACT_SOURCE_MATCH` yields `NO_CANDIDATE_DUPLICATE`.
`REDACTED_TEXT_MATCH` is advisory and does not by itself suppress a candidate,
establish identity or prove exactly-once delivery. Invalid/missing context and
collision signals fail closed through the disposition mapping below.

## Decision 6 — Sensitivity and topic labels are separate

`sensitivity` uses only the four data-policy classifications. The declared
value is a floor: deterministic detectors may escalate sensitivity but never
downgrade it. Unknown detector output or policy drift quarantines the result.

Domain/topic labels such as `equipment_downtime` live in a separate
`topic_labels` field and grant no placement authority. P3-A emits no provider
placement decision and makes no minimization-complete claim.

## Decision 7 — Versioned redaction with no matched-value leakage

An injected `RedactionRuleSet` owns deterministic high-confidence rules and a
version. Successful replacements use typed placeholders such as
`<redacted:credential>`; receipts contain only type, safe offsets and counts,
never original matched content. Raw text is not returned in the public result.

Rule failure, malformed spans, overlapping replacements, suspected sensitive
content without a safe replacement, or post-redaction detector residue yields
`NO_CANDIDATE_QUARANTINED`. Sanitized errors expose stable codes only.

## Decision 8 — Quarantine ownership and reasons are explicit

The top-level disposition is exactly one of:

- `CANDIDATE_READY`;
- `NO_CANDIDATE_DUPLICATE`;
- `NO_CANDIDATE_QUARANTINED`;
- `NO_CANDIDATE_FALLBACK`.

P3-A does not persist quarantine. It emits a reason, policy retention hint
(`30` days from current policy), source owner/link/fingerprint and safe receipts
for an explicit `QuarantineRouteV1(owner_id, sink_id, policy_version,
retention_days, sink_available)` supplied by the caller. `source_owner_id`,
`owner_id` and `sink_id` are distinct opaque authorities. That route and hint
are not proof that anything was retained or acknowledged.

The closed quarantine reason taxonomy is:

- `INVALID_ENVELOPE`;
- `PROVENANCE_MISMATCH`;
- `AMBIGUOUS_VALUE`;
- `UNSUPPORTED_TRANSFORM`;
- `DEDUPE_CONTEXT_INVALID`;
- `DIGEST_COLLISION_SUSPECTED`;
- `POLICY_DRIFT`;
- `REDACTION_FAILED`;
- `REDACTION_RESIDUE`;
- `CONFLICT_DETECTED`;
- `QUALITY_INCOMPLETE`;
- `STAGE_INVARIANT_ERROR`.

When quarantine is required but the route is absent, invalid, unavailable or
does not specify the exact current 30-day hint, the top-level result is
`NO_CANDIDATE_FALLBACK` with `QUARANTINE_ROUTE_UNAVAILABLE`; it never claims a
quarantine sink accepted data.

“Fallback về rules” means a typed `NO_CANDIDATE_FALLBACK` instructing the
caller to remain on an existing non-AI/rule workflow. It never means returning
a partially refined context candidate. Known stage failures become sanitized
fallback/quarantine results; unexpected programmer/invariant errors fail closed
with no candidate and a stable generic code.

## Decision 9 — Quality is control coverage, not truth confidence

`quality_score` is an integer `0..100` made from four deterministic components,
each worth 25 points:

1. provenance validity;
2. normalization/terminology completeness with no unresolved ambiguity;
3. sensitivity/redaction completeness;
4. integrity completeness: no conflict, invalid dedupe state or failed stage.

The initial admission threshold is exactly `100`. Any lower score produces a
typed no-candidate outcome. The score must be described as control coverage,
never probability, semantic truth, model confidence or production quality.

All nine stage receipts always exist in fixed order. After the first non-PASS
receipt, later stages are exactly `NOT_RUN`; they may not fabricate successful
receipts. Quality components are computed only from actual PASS receipts, so a
skipped/failed component contributes zero. The quality receipt itself exists
even for no-candidate results and cannot upgrade an earlier failure.

## Decision 10 — Context candidate schema and digest are reproducible

A `ContextCandidateV1` exists if and only if all required stage receipts PASS,
no duplicate/quarantine/fallback applies, and quality is `100`. Its exact
preimage fields are:

1. `schema_version` (`"1.0"`);
2. `redacted_normalized_text`;
3. `sensitivity`;
4. sorted unique `topic_labels`;
5. `source_id`, `source_version`, `source_owner_id`, `source_link` and exact
   source fingerprint triple;
6. exact `normalization_rules_version`, `terminology_rules_version`,
   `classification_rules_version`, `redaction_rules_version`,
   `quality_rules_version`;
7. `quality_score` and four named integer component scores.

No other or optional field is allowed in V1. It never contains `raw_text`,
confirmed-fact status, provider instructions, embeddings or retrieval metadata.

Canonical bytes are UTF-8 of `json.dumps(preimage, sort_keys=True,
separators=(",", ":"), ensure_ascii=False, allow_nan=False)`. Schema forbids
floats, nulls and non-string map keys; topic labels are Unicode-codepoint sorted
and unique before serialization. `candidate_fingerprint` is computed after
serialization as lowercase SHA-256, lowercase SHA-512 and byte length, and is
stored beside—not inside—the preimage. It is a change/dedupe aid, not a
signature or authority receipt.

## Decision 10A — Failure-to-disposition mapping is total

Disposition precedence is mechanical:

1. known stage unavailability/invariant error, or a required-but-unavailable
   quarantine route → `NO_CANDIDATE_FALLBACK`;
2. valid `EXACT_SOURCE_MATCH` → `NO_CANDIDATE_DUPLICATE`;
3. any closed quarantine reason, collision signal, invalid dedupe context, or
   final quality below 100 → `NO_CANDIDATE_QUARANTINED` when a valid route
   exists, otherwise fallback by rule 1;
4. only nine PASS receipts plus quality 100 → `CANDIDATE_READY`.

`RefineryResultV1` always contains disposition, source owner/link/fingerprint,
the exact nine receipts and quality receipt. Exactly one of duplicate,
quarantine or fallback receipt is present for its matching no-candidate
disposition; all are absent for ready. `context_candidate` is non-null exactly
for `CANDIDATE_READY` and null for every other disposition. Model construction
must reject any contradictory combination.

## Decision 11 — Fixture strategy

Retain the current fixture as an explicit negative/quarantine case after adding
its missing metadata; do not silently correct it into a positive golden case.
Add separate positive and adversarial fixtures for fully qualified time,
Unicode/terminology, exact duplicate, sensitivity escalation, redaction,
overlap/residue, conflict, policy drift and sanitized fallback.

All fixtures are synthetic and repository-owned. They prove deterministic local
behavior only, not external ingestion or real operational correctness.

## Decision 12 — Evidence and closure boundary

DESIGN/SPEC/local BUILD require zero provider calls. Unit/contract/property
tests and deterministic fixtures are appropriate for the bounded local claim.
If a later tranche claims that this pipeline actually gates provider/AI context,
that requires a real runtime caller plus fresh real-provider evidence under a
separate R2 call budget.

P3-A closure must not claim P3-B, P3-C, retrieval, RAG, learning, Integration
Edge, raw persistence, load-bearing DLP/minimization, confirmed truth or
production readiness.

## Alternatives rejected

- **Reuse the current YAML unchanged:** rejected; it cannot express roadmap
  quarantine, quality, provenance or fallback requirements.
- **Use an LLM for normalization/classification:** rejected; nondeterministic,
  expands provider/data risk and is unnecessary for P3-A.
- **Treat content hash as global dedupe/exactly-once:** rejected; scope,
  collision and delivery semantics are absent.
- **Return partial candidates on failure:** rejected; silently bypasses the
  mandatory refinement boundary.
- **Wire `data_scope` now:** rejected; that is P3-B and requires a real caller
  and minimization-evidence contract.
- **Correct the ambiguous fixture by choosing a time/action:** rejected; that
  repeats the `invent_missing_values` defect.

## Design acceptance

DESIGN is acceptable only if independent review confirms every INTAKE decision
is resolved, all outputs fail closed, candidate existence is a strict invariant,
raw-retention and AI claims remain bounded, and the design is specific enough
for a separate testable SPEC. No implementation authority follows from this
ADR.
