# ADR Amendment 1 — P3-A Dedupe Stage and Fingerprint Separation

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent ADR: `docs/decisions/ADR_2026-08-03_P3A_REFINERY.md`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Risk: `R2`
- Control-chain phase: `DESIGN`
- Status: `DESIGN_AMENDMENT_PENDING_INDEPENDENT_REVIEW`

## Trigger

During SPEC translation, the author found an internal contradiction that cannot
be silently resolved downstream:

1. Parent Decision 3 orders duplicate analysis before sensitivity
   classification and redaction.
2. Parent Decision 5 requires `REDACTED_TEXT_MATCH`, which cannot exist before
   redacted normalized content exists.
3. The phrase `candidate_fingerprint` is also overloaded. The final candidate
   fingerprint from Decision 10 contains source identity/provenance, so content
   from two distinct sources will not match even when the redacted semantic
   content is identical.

The parent ADR remains immutable. This amendment supersedes only the affected
stage order and dedupe fingerprint naming/semantics.

## Amendment Decision 1 — Corrected nine-stage order

The exact stage order is now:

1. envelope/schema/provenance validation;
2. safe syntactic normalization;
3. terminology matching;
4. sensitivity classification and separate topic labeling;
5. ambiguity/conflict evaluation;
6. redaction plus post-redaction residue detection;
7. duplicate analysis;
8. data-quality coverage calculation;
9. context-candidate admission.

All parent receipt, `NOT_RUN`, failure precedence and candidate-absence rules
remain unchanged. Exact-source duplicate evaluation occurs inside stage 7; it
is intentionally not an early shortcut, so every earlier privacy/conflict
stage has a fixed receipt and dedupe never consumes unredacted output for
content matching.

## Amendment Decision 2 — Three distinct fingerprints

The design has exactly three non-interchangeable fingerprint types. Each is a
triple `(lowercase_sha256, lowercase_sha512, byte_length)`:

1. `source_fingerprint`: over exact input `raw_text.encode("utf-8")` before
   normalization; proves only the supplied text field.
2. `dedupe_content_fingerprint`: over canonical JSON for
   `DedupeContentV1`, whose exact preimage is
   `(schema_version="1.0", redacted_normalized_text, sensitivity,
   sorted_unique_topic_labels, normalization_rules_version,
   terminology_rules_version, classification_rules_version,
   redaction_rules_version)`. It contains no source id/version/owner/link,
   received time, quality result, candidate digest or provider/retrieval data.
3. `candidate_fingerprint`: over the full `ContextCandidateV1` preimage already
   fixed by parent Decision 10, including source identity/provenance and quality.

All canonical JSON uses the parent's exact UTF-8 `json.dumps` rules. The
dedupe-content and final-candidate fingerprints may coincide only by accident;
they are different typed fields and must never be substituted.

## Amendment Decision 3 — Corrected dedupe record and matches

`DedupeRecordV1` is now the exact tuple `(scope_id, prior_source_id,
observed_at, source_fingerprint, dedupe_content_fingerprint?)`.

- `EXACT_SOURCE_MATCH` compares `source_fingerprint` triples.
- `REDACTED_TEXT_MATCH` compares `dedupe_content_fingerprint` triples after
  stage 6 PASS.
- A one-digest match with another digest or length mismatch within the same
  fingerprint type yields `DIGEST_COLLISION_SUSPECTED`.
- Cross-type comparison is forbidden.
- Window, scope, bound, ordering, collision, advisory/no-exactly-once and
  disposition rules from parent Decision 5 remain unchanged.

If stage 6 is not PASS, stage 7 is `NOT_RUN`; no content fingerprint is
computed. Exact source matching is also not emitted through a skipped receipt.
The earlier failure already guarantees candidate absence.

## Amendment Decision 4 — Quality mapping

The four 25-point components are interpreted against the corrected order:

- provenance: stage 1;
- normalization completeness: stages 2–3 with no unresolved ambiguity;
- protection completeness: stages 4–6;
- integrity completeness: stage 7 plus absence of conflict from stage 5.

Stage 8 calculates only from actual PASS receipts. Stage 9 admits a candidate
only at 100/100 and otherwise follows the parent's total disposition mapping.

## Preserved design

Everything else in parent ADR SHA-256 `57ec06fc…e696e` remains binding:
pure local/no-provider package, no paraphrase or time inference, sensitivity/
topic separation, explicit ownership/quarantine taxonomy, no raw persistence,
typed fallback, exact candidate preimage, negative fixture strategy, P3-B/P3-C
parking and provider-evidence claim boundary.

## Review and transfer

Independent DESIGN amendment review must confirm the stage order is executable,
all three fingerprints are non-circular/reproducible, cross-source content
matching excludes provenance, and receipt/disposition invariants still hold.
Only `DESIGN_AMENDMENT_REVIEW_PASS` may return authority to `SPEC_AUTHOR`.

