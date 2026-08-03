# P3-A Refinery — Independent DESIGN Amendment 2 Review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `INDEPENDENT_DESIGN_REVIEWER`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Trigger SPEC re-review SHA-256: `a39555ab980adb5e28148763e4d28764b845da5590ca07eaed32a317cc78e3a4`
- Reviewed Design Amendment 2 SHA-256: `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`
- Disposition: `DESIGN_AMENDMENT_REVIEW_PASS`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed boundary and changed-set observation

This review evaluated only Design Amendment 2 against retained SPEC re-review
findings F5–F7 and regressed the affected invariants against the immutable
parent ADR and reviewed Amendment 1. Parent decisions not expressly superseded
remain binding. This pass applies only to the exact hashes above.

Immediately before this receipt was created, the unstaged set contained the
Amendment 2 candidate, the retained SPEC candidate and two retained SPEC review
receipts, plus the four pre-existing modified continuity paths:

- `docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_2.md`;
- `docs/specs/P3A_REFINERY_SPEC.md`;
- `docs/decisions/P3A_REFINERY_SPEC_REVIEW.md`;
- `docs/decisions/P3A_REFINERY_SPEC_REREVIEW.md`;
- `SESSION/SESSION_MEMORY.md`;
- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The staged set was empty. This reviewer added only this review path and did not
edit Amendment 2, either parent DESIGN artifact, the failed SPEC candidate,
retained reviews or continuity.

No provider, network, SPEC edit, WORK_ORDER, BUILD, staging, commit or push
action was performed.

## Finding closure

### F5 — CLOSED: constructible and disclosure-safe public union

The amended public output is the closed tagged union
`PreAdmissionRejectionV1 | RefineryResultV1`. Structural pre-admission is a
parser/model-construction gate, explicitly not a tenth stage and not a
successful ENVELOPE receipt. The nine-stage pipeline begins only after every
required field is present, typed, bounded, strictly encodable and safe enough
to construct the non-null provenance fields of `RefineryResultV1`.

Every structural failure returns the exact provenance-free
`PreAdmissionRejectionV1`: fixed schema/kind/reason/caller action and one or
more sorted unique values from an eleven-value safe error-code enum. It has no
disposition, input/provenance value, receipt, route, candidate, exception or
stack and cannot claim quarantine, persistence, deletion, acknowledgment or
retry. Unknown/empty codes and extra fields are rejected. Because invalid
field values are never reflected or fingerprinted, arbitrary non-mapping,
missing, extra, surrogate-containing, malformed-fingerprint and
disclosure-unsafe input has a deterministic safe result without fabricated
provenance.

After pre-admission succeeds, the exact raw-text fingerprint can be recomputed.
A structurally valid caller fingerprint mismatch therefore remains a full
ENVELOPE `PROVENANCE_MISMATCH` result using the locally recomputed fingerprint
and already validated owner/link; the untrusted mismatched fingerprint is not
echoed as provenance. `INVALID_ENVELOPE` moves to the pre-admission branch,
while the parent nine-receipt/non-null-provenance invariant is correctly
narrowed to `RefineryResultV1` only.

### F6 — CLOSED: typed dedupe outcome and fail-stop disposition

`StageReceiptV1` now carries nullable typed `dedupe_status`. It is null on all
non-DEDUPE stages and on DEDUPE `NOT_RUN`; the amendment gives every executed
DEDUPE outcome/reason an exact status or required null. Successful stage-7
results can therefore distinguish `UNIQUE` from advisory
`REDACTED_TEXT_MATCH` without inferring from counts or ids.

`EXACT_SOURCE_MATCH` is a closed stage reason permitted only for DEDUPE FAIL
and maps to typed status `EXACT_SOURCE_MATCH`. It stops QUALITY and
CANDIDATE_ADMISSION as `NOT_RUN`, while the separate always-present quality
receipt uses only actual PASS evidence and cannot upgrade the duplicate. The
parent disposition precedence then selects `NO_CANDIDATE_DUPLICATE` and its
separate duplicate receipt. Collision, insufficient context, invalid context,
unavailability and invariant errors retain their closed status/nullability and
reviewed fail-closed dispositions. Every unlisted outcome/reason/status tuple
is model-invalid.

This preserves stage 7 after redaction, same-type fingerprint comparisons,
collision precedence, caller-scoped advisory semantics and the absence of any
global identity or exactly-once claim.

### F7 — CLOSED: one control-version source per stage

The injected pure-local control bundle now has exactly nine non-empty bounded
version tokens. The amendment maps them one-to-one and positionally to
ENVELOPE, NORMALIZATION, TERMINOLOGY, CLASSIFICATION, CONFLICT, REDACTION,
DEDUPE, QUALITY and CANDIDATE_ADMISSION. Renaming the receipt field to
`control_version` correctly covers schema/algorithm controls without calling
all nine rule sets. Substitution, defaulting, omission and cross-stage reuse are
invalid; NOT_RUN retains the mapped version of the skipped control and does
not pretend it executed. Pre-admission has no stage control version.

The candidate preimage remains limited to the parent-fixed five versions and
the dedupe-content preimage remains limited to Amendment 1's four transform
versions. The additional envelope/conflict/dedupe/admission versions appear in
the full receipt sequence only, so neither candidate fingerprint becomes
circular or is misrepresented as a digest of the full boundary output.

## Regression of preserved invariants

- The tagged union is total without weakening disclosure: neither branch may
  expose raw input, matched sensitive values, unsafe provenance, exceptions or
  stacks. No branch fabricates source evidence or claims persistence.
- Structural pre-admission does not reorder, add to or bypass the corrected
  nine-stage pipeline; it defines whether that pipeline can safely begin.
- Exactly one first stage FAIL still forces every later stage to NOT_RUN.
  Exact-source duplicate, collision, missing/invalid context, quarantine-route
  failure and invariant/unavailable controls retain deterministic disposition
  precedence and candidate-null behavior.
- Quality remains four 25-point control-coverage components with a strict
  100/100 admission threshold, never truth, confidence or production quality.
- The three fingerprint types, canonicalization, source-free dedupe-content
  preimage and full candidate preimage remain unchanged, non-circular and
  non-interchangeable.
- Syntax-only normalization, no paraphrase/time inference, sensitivity/topic
  separation, exact data-policy vocabulary, redaction fail-closed behavior,
  synthetic negative fixtures and raw/quarantine non-ownership remain binding.
- The package remains deterministic and local with no provider/network,
  database, filesystem/environment discovery, secret read, clock or randomness.
  P3-B/P3-C, runtime `data_scope`, external ingest, persistence,
  retrieval/RAG, learning, confirmed truth, AI governance and production remain
  outside P3-A.

## Disposition and transfer boundary

`DESIGN_AMENDMENT_REVIEW_PASS` with no waiver. F5–F7 are closed at DESIGN for
the unchanged Amendment 2 SHA-256
`393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`.
The parent ADR plus Amendments 1 and 2 **may return to `SPEC_AUTHOR`** for a
fresh repaired SPEC and independent SPEC review. Any byte change to this
DESIGN lineage invalidates the transfer and requires independent re-review.

This receipt grants SPEC repair only. It grants no WORK_ORDER, BUILD,
provider/network call, remote ingest, persistence, retrieval/RAG, staging,
commit, push or later-lane authority.
