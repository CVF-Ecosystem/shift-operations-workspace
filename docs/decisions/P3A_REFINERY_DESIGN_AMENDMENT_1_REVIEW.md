# P3-A Refinery — Independent DESIGN Amendment 1 Review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `INDEPENDENT_DESIGN_AMENDMENT_REVIEWER`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Parent DESIGN review SHA-256: `fcb8c3f96bd2ed524c2bb4457a338a3e9c7cfde4b120090091e298d30eb2ab45`
- Parent DESIGN re-review SHA-256: `1a76e69a153de0a23911da6a735cc46ba91aaeebdceeaacaa6d921289b5c113c`
- Reviewed Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Disposition: `DESIGN_AMENDMENT_REVIEW_PASS`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed boundary

This review treats the reviewed parent ADR as immutable and evaluates only the
stage-order and fingerprint-separation overrides in Amendment 1. Parent rules
not expressly superseded remain binding. The pass applies only to the exact
parent and amendment hashes above.

No provider, helper, network, POST, staging, commit or push action was used.

## Trigger validation

The identified contradiction is real:

- parent stage 4 attempted duplicate analysis before parent stage 6 produced
  redacted normalized content, so `REDACTED_TEXT_MATCH` had no executable
  preimage at the point where it was required;
- the parent `candidate_fingerprint` is produced from the final candidate
  preimage after quality/admission and contains source identity/provenance, so
  it is both unavailable during early dedupe and unsuitable for matching the
  same protected content across different sources.

This is a DESIGN contradiction rather than a SPEC implementation choice. The
amendment correctly repairs it without modifying the reviewed parent bytes.

## Amendment verification

### Corrected nine-stage order — PASS

The amended sequence is executable: envelope, syntax, terminology,
sensitivity/topic, ambiguity/conflict, redaction/residue, dedupe, quality and
admission. Stage 7 therefore receives both the original source fingerprint
from stage 1 and protected content produced only after stage 6 PASS.

Both `EXACT_SOURCE_MATCH` and `REDACTED_TEXT_MATCH` occur solely inside stage
7. Exact-source comparison uses only fingerprint triples and content matching
uses only the redacted-content preimage; neither comparison requires emitting
raw text or matched sensitive values. If stage 6 does not PASS, stage 7 is
`NOT_RUN`, no dedupe-content fingerprint is created and neither match is
reported through a fabricated receipt.

### Fingerprint separation and canonicalization — PASS

The three fingerprint types have distinct, non-circular preimages:

1. `source_fingerprint` covers the exact input UTF-8 bytes before any
   normalization;
2. `dedupe_content_fingerprint` covers a closed `DedupeContentV1` canonical
   JSON preimage containing protected content, sensitivity, sorted unique
   topics and the four transformation-rule versions, with no source,
   timestamp, quality, candidate-fingerprint or provider/retrieval field;
3. `candidate_fingerprint` remains over the complete parent
   `ContextCandidateV1` preimage, including source provenance and quality, and
   is stored outside its own preimage.

Each result is a typed lowercase SHA-256, lowercase SHA-512 and byte-length
triple. Source and protected-content comparisons are same-type only;
cross-type comparison/substitution is forbidden. `DedupeContentV1` and
`ContextCandidateV1` both use the parent's exact UTF-8 `json.dumps` canonical
serialization, including sorted keys, compact separators, unescaped Unicode,
NaN rejection and the inherited schema restrictions. Cross-source protected
content can now match without importing source provenance into its preimage.

### Dedupe mechanics and disposition — PASS

`DedupeRecordV1` now stores the source fingerprint and optional
dedupe-content fingerprint needed by stage 7, not the later final-candidate
fingerprint. The parent non-empty scope, inclusive UTC window, 500-record
bound, unique-id validation and `(observed_at, prior_source_id)` selection
order remain intact.

Full triple equality defines a same-type match. A one-digest agreement with
the other digest or length differing remains the typed
`DIGEST_COLLISION_SUSPECTED` signal; cross-type values cannot generate a
match or collision. Exact source duplicate, advisory redacted-content match,
invalid/missing context, collision quarantine and no-exactly-once boundaries
retain the parent's total disposition precedence. Moving the analysis does not
grant global identity, persistence or delivery authority.

### Quality and receipt invariants — PASS

The four 25-point components now map coherently to the amended order:
provenance to stage 1, normalization to stages 2–3 plus resolved ambiguity,
protection to stages 4–6, and integrity to stage 7 plus no stage-5 conflict.
Stage 8 may score only actual PASS evidence and cannot upgrade an earlier
failure; stage 9 still admits only at 100/100.

Exactly nine receipts remain mandatory in the amended fixed order. After the
first non-PASS receipt every later stage is `NOT_RUN`. Parent disposition
precedence, typed non-ready receipts, contradictory-combination rejection and
the invariant `context_candidate != null` exactly for `CANDIDATE_READY`
remain unchanged. No early source-match shortcut can bypass sensitivity,
conflict or redaction stages, and no partial candidate can escape fallback.

## Preserved parent boundaries

- Normalization remains syntax-only: no paraphrase, translation, action-state
  reinterpretation, timezone guess or AM/PM inference.
- Sensitivity remains separate from topic labels, non-decreasing from the
  declared floor and exactly aligned with the four-value data-policy
  vocabulary; policy drift fails closed.
- Redaction receipts and public errors do not echo original matches or raw
  text; residue and unsafe spans remain quarantine conditions.
- Quality 100 remains deterministic control coverage, not truth, confidence
  or production quality.
- P3-A owns neither upstream raw retention nor quarantine persistence. The
  30-day value remains a policy hint and unavailable routing remains fallback.
- The ambiguous-time/action fixture remains negative; synthetic fixtures prove
  deterministic local behavior only.
- The package remains local and non-provider. P3-B `data_scope` runtime
  wiring, P3-C retrieval contracts, external ingest, retrieval/RAG, learning,
  confirmed truth, persistence and production remain parked. Any future AI
  governance claim still requires a real caller and separately authorized
  fresh real-provider evidence.

## Disposition and transfer boundary

`DESIGN_AMENDMENT_REVIEW_PASS` with no waiver. The parent ADR plus unchanged
Amendment 1 at SHA-256
`dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
**may return to `SPEC_AUTHOR`**. Any byte change to the amendment or parent ADR
invalidates this transfer and requires independent DESIGN review.

This receipt grants resumption of SPEC authoring only. It grants no
WORK_ORDER, BUILD, provider/helper/network/POST, remote ingest, persistence,
retrieval/RAG, staging, commit, push or later-lane authority.
