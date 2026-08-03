# P3-A Refinery — Independent SPEC Re-review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `REVIEWER`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Retained failed SPEC review SHA-256: `dba16f97407a7e0f1e49afa462346acf68bc0224d48e718f7b11c5b402898549`
- Re-reviewed SPEC SHA-256: `f836f5d382dbb58d6b992a417edd16235da5c56fa9d6dbcc04149d11e5749ffc`
- Disposition: `REVIEW_FAIL`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed scope and changed-set observation

The re-review checked retained F1–F4 first, then regressed every R1–R30 and
AC-01 through AC-12 against the immutable reviewed parent ADR and Design
Amendment 1. It covered executable model construction, receipt state and
quality semantics, fingerprints/dedupe, total disposition, disclosure/I/O,
fixtures, dependency direction and claim boundaries.

Immediately before this receipt was created, the unstaged set consisted of:

- repaired `docs/specs/P3A_REFINERY_SPEC.md` (untracked);
- retained `docs/decisions/P3A_REFINERY_SPEC_REVIEW.md` (untracked);
- four pre-existing modified continuity paths:
  `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`, and
  `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The staged set was empty. This reviewer added only this re-review path and did
not edit the SPEC, retained review, DESIGN artifacts or continuity.

## Retained finding closure

- **F1 CLOSED:** R8 now binds dedupe-content and candidate fingerprints to R19
  and R23, and R15 binds missing-context disposition to R21. AC-04 adds a
  normative cross-reference check.
- **F2 CLOSED:** R3 defines a separate closed `StageReason` enum; R17 defines
  the only permitted reason for PASS/NOT_RUN and an exhaustive per-stage FAIL
  table, including typed local-time/action ambiguity and explicit mappings to
  top-level reasons.
- **F3 CLOSED:** R17 admits exactly `PASS^9` or `PASS* FAIL NOT_RUN*`, makes
  NOT_RUN conditional in both directions, empties non-executed receipt data
  and rejects every other combination. AC-04 covers orphan/premature NOT_RUN.
- **F4 CLOSED:** R16 defines collision as unequal full triples with either
  digest equal, explicitly including both-digests-equal/length-different.
  AC-03 and AC-06 carry the required positive and negative vectors.

All four repairs are precise and no waiver was used. Regression nevertheless
found the new blocking contradictions below.

## New findings

### F5 — Invalid envelopes cannot produce the mandatory public result schema

R9 requires unknown/extra fields, missing/empty values, invalid bounds/time,
invalid text and malformed source provenance to fail `ENVELOPE` with
`INVALID_ENVELOPE` or `PROVENANCE_MISMATCH`. R21 then requires a typed
quarantine/fallback disposition. But R24 requires **every** result to contain
non-null `source_owner_id`, `source_link` and a structurally valid
`source_fingerprint`, while R4/R6 require those values themselves to be valid
and R26 forbids reflecting raw/secret-bearing invalid input.

For an envelope missing `source_owner_id` or `source_link`, containing an
unpaired surrogate that cannot be UTF-8 fingerprinted, or carrying a prohibited
secret/raw value in its link, no conforming R24 result can be constructed.
Copying the input violates R4/R6/R26; inventing a replacement violates bounded
provenance and deterministic source linkage; returning no result violates
R2/R9/R21/R24. AC-02 currently asks for these failures without defining a
constructible public output.

Required repair: define an independently reviewed pre-admission rejection
schema whose provenance fields are explicitly nullable/absent and whose safe
error fields cannot echo invalid input, or amend the DESIGN/result invariant
to distinguish untrusted-envelope rejection from post-validation
`RefineryResultV1`. Specify exactly when a locally recomputed fingerprint is
possible and prohibit fabricated provenance. Add tests for every missing,
unencodable and disclosure-unsafe provenance field.

### F6 — Ready results cannot represent the required dedupe status

R1 closes `DedupeStatus`; R16 requires stage 7 to yield `UNIQUE`,
`EXACT_SOURCE_MATCH`, `REDACTED_TEXT_MATCH`, collision or insufficient context,
and requires safe match ids/count in its receipt. Yet R17's exact
`StageReceiptV1` has no `dedupe_status` field and a successful DEDUPE receipt
may contain only reason `STAGE_PASS`. R22 carries a typed dedupe status only in
`DuplicateReceiptV1`, which exists solely for
`NO_CANDIDATE_DUPLICATE`. R24 requires all three no-candidate receipts absent
for `CANDIDATE_READY`.

Consequently a ready `UNIQUE` result and a ready advisory
`REDACTED_TEXT_MATCH` result have no typed location for their distinct R16
status. Safe ids/counts do not solve the schema issue: their meaning is not a
closed substitute for `DedupeStatus`, and arbitrary absence/presence cannot
prove which status was emitted. AC-06 cannot assert the advisory cross-source
match through the public model without implementation-specific inference.

Required repair: add an exact typed dedupe result/status field to the DEDUPE
stage receipt or to every `RefineryResultV1`, define its nullability for
NOT_RUN/FAIL, and preserve the separate duplicate/quarantine/fallback receipt
invariants. Add public-schema tests distinguishing UNIQUE from
REDACTED_TEXT_MATCH without parsing counts or ids heuristically.

### F7 — Three mandatory stage receipt versions have no normative source

R17 requires every one of the nine exact receipts to contain
`rule_set_version`, and R4 requires every rule/policy version to be a non-empty
bounded identifier. R10 supplies six rule sets: normalization, terminology,
classification, conflict, redaction and quality. It does not define which
version populates `ENVELOPE`, `DEDUPE` or `CANDIDATE_ADMISSION`; nor does it
define separate schema/dedupe/admission algorithm versions. Reusing an
unrelated rule version or inventing a constant would both satisfy the current
text, producing non-identical but nominally conforming receipt bytes and
undermining R25 determinism across implementations.

Required repair: give each of the nine receipt version fields one exact
normative source (including explicit versioned schema/dedupe/admission rule or
algorithm bundles), or rename/generalize the field and close its mapping.
Add AC-02/golden-result coverage proving all nine values and rejecting
substitution between stages.

## Regression assessment

- The repaired fingerprint cross-references, closed reasons, fail-stop receipt
  language and collision predicate are now faithful to the reviewed DESIGN.
- R1–R30 otherwise retain syntax-only/no-paraphrase behavior, sensitivity/topic
  separation and exact data-policy parity, redaction leakage protection,
  caller-scoped advisory dedupe, 100/100 control coverage, quarantine/raw
  non-ownership, deterministic fixtures and candidate-null fail-closed intent.
- AC-01 fails because this re-review has findings. AC-02 and AC-06 cannot be
  executable until F5–F7 close; AC-03–AC-05 and AC-07–AC-12 remain bounded but
  cannot authorize progression past a failed earlier gate.
- The zero-I/O boundary remains intact: no provider/network/database,
  filesystem/environment discovery, secret read, wall-clock read or randomness
  is permitted in the pipeline. Public surfaces remain intended to exclude raw
  and matched-sensitive values.
- P3-B/P3-C, runtime `data_scope`, provider behavior, external ingest,
  persistence, retrieval/RAG, learning, confirmed truth and production remain
  outside the SPEC.

## Disposition

`REVIEW_FAIL` with no waiver. Retained F1–F4 are closed, but new F5–F7 prevent
an executable and disclosure-safe SPEC. The candidate must return to governed
DESIGN/SPEC repair as appropriate and **may not transfer to
`WORK_ORDER_AUTHOR`**.

This receipt grants no WORK_ORDER, BUILD, provider/network call, remote ingest,
persistence, retrieval/RAG, staging, commit, push or later-lane authority. No
provider or network call was performed during this re-review.
