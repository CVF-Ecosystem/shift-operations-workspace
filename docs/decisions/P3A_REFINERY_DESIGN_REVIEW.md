# P3-A Refinery — Independent DESIGN Review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `INDEPENDENT_DESIGN_REVIEWER`
- Reviewed ADR SHA-256: `73787ca1fb52a68d8cabfd90d32b205841ac23adaaebe20b4be80a261f8b6efc`
- Parent INTAKE SHA-256: `271dd0085da921ff9f9d75ec9864bb09f56d9c45df8491aa4a82e26041a239b7`
- INTAKE review SHA-256: `a1fbe91244c0932f9d21fa29fd779d8a51f9c54158c8ccbb9febf1d0809b7e28`
- Disposition: `REVIEW_FAIL`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed boundary

The review compared the ADR with the accepted INTAKE and its independent
review, current continuity, the refinery contract and boundary documents,
`data-policy.yaml`, context-control mapping, and the current refinery fixture.
No provider, helper, network, POST, staging, commit or push action was used.

## Confirmed design strengths

- Provenance is explicitly limited to lowercase SHA-256 of the exact strictly
  decoded `raw_text.encode("utf-8")` supplied to P3-A before normalization. It
  is not represented as proof of the upstream envelope, sender, channel,
  signature, retention or exactly-once delivery.
- The fixed local stage sequence, no-provider dependency direction and strict
  candidate admission intent are consistent with P3-A. P3-B runtime gate
  wiring, P3-C retrieval contracts and all provider/RAG claims remain parked.
- Normalization is syntax-only. The ADR correctly rejects paraphrase, inferred
  AM/PM/timezone and action-state reinterpretation; `11h40` remains ambiguous
  and the existing fixture remains negative rather than golden truth.
- Sensitivity uses the four-value data-policy vocabulary and is separate from
  topic labels. Declared sensitivity is a non-decreasing floor, policy drift
  fails closed, and neither field grants provider placement authority.
- Redaction receipts exclude matched values, public results exclude raw text,
  residue and malformed/overlapping spans quarantine, and sanitized errors use
  stable codes. The 30-day quarantine value is only a policy hint, not a
  persistence claim.
- Quality `100` is expressly control coverage rather than truth, confidence or
  production quality. Partial candidates, confirmed facts, embeddings,
  retrieval metadata and provider instructions are excluded.

## Blocking findings

### F1 — Dedupe identity and collision behavior are not mechanically defined

Decision 5 names a caller scope, window and prior digests, but it does not
define the exact tuple that constitutes an `EXACT_SOURCE_MATCH`, whether both
the source digest and source identity/version must agree, or how a purported
hash collision is represented and detected. A digest equality alone cannot
distinguish a duplicate from a collision. “Hash collision ... fails closed”
therefore has no testable input signal or stable result/reason mapping.

Repair requires an exact comparison tuple and window inclusion rule, a typed
collision/inconsistent-history signal and outcome, and explicit behavior for
same digest with incompatible source metadata. The design must retain its
caller-scoped advisory boundary and make no exactly-once claim.

### F2 — Quarantine ownership and reason taxonomy remain unresolved

Decision 8 refers only to an unspecified “upstream owner,” emits an unspecified
reason, and does not define behavior when no quarantine sink/owner is supplied
or accepts the handoff. It likewise does not name the upstream owner or
external dependency responsible for source-link availability. This does not
close the accepted INTAKE obligations for owner/handoff semantics, a reason
taxonomy and no-sink fail-closed behavior.

Repair requires a closed, versioned quarantine reason vocabulary; an explicit
caller-owned handoff contract (including accepted/rejected/unavailable sink
semantics); an explicit source-link availability dependency; and a guarantee
that absence or rejection can never yield a candidate. The 30-day value must
remain a non-enforcement hint and P3-A must not acquire persistence ownership.

### F3 — Failure, quality and top-level disposition mapping is ambiguous

The ADR defines four top-level dispositions, but says known failures become
“fallback/quarantine results” without mapping each stage failure, ambiguity,
conflict, quality score below 100, policy drift, dedupe insufficiency and
invariant error to exactly one disposition and stable reason. Consequently the
same input could conform while producing either `NO_CANDIDATE_QUARANTINED` or
`NO_CANDIDATE_FALLBACK`. The statement that every stage emits a receipt also
does not define `SKIPPED_AFTER_FAILURE`, while candidate admission is itself a
stage whose PASS is included in the candidate-existence condition, creating a
circular or implementation-dependent receipt invariant.

Repair requires a total deterministic failure-to-disposition/reason table,
receipt behavior for all stages after the first failure, and a non-circular
admission invariant. It must state that the candidate field is absent for
every non-ready disposition, not merely that partial candidates are rejected.

### F4 — `ContextCandidateV1` and its canonical digest are underspecified

Decision 10 lists conceptual contents but not an exact field schema,
cardinality, optionality or ordering. “Canonical JSON for the candidate fields”
does not identify the canonicalization algorithm, UTF-8/Unicode treatment,
object-key and array ordering, number/string serialization, digest algorithm,
or whether the digest field is excluded from its own preimage. Independent
implementations therefore cannot reproduce one stable candidate digest.

Repair requires the exact candidate field set and types, deterministic ordering
rules for all collections, a named canonical byte serialization, a named
digest algorithm, and an explicit preimage that excludes the digest itself.
The schema must preserve the strict no-raw-text and redacted-text-only boundary.

## Eight-decision closure assessment

1. Envelope/version and text-field digest semantics: resolved, except the
   source-link ownership/availability part retained in F2.
2. Deterministic normalization and ambiguity: resolved.
3. Dedupe identity/scope/window/collision: not resolved; F1.
4. Sensitivity versus topic vocabulary: resolved.
5. Redaction policy and leakage behavior: resolved at DESIGN level.
6. Quarantine ownership/taxonomy/30-day relationship: not resolved; F2.
7. Quality dimensions/threshold/fail-closed behavior: component intent is
   resolved, but deterministic disposition and receipt semantics are not; F3.
8. Exact fallback and no-partial-candidate behavior: intent is resolved, but
   the total typed mapping and field-absence invariant are not; F3.

Fixture strategy, dependency direction and the P3-B/P3-C/provider claim
boundary are acceptable. They do not cure F1–F4.

## Disposition and transfer boundary

`REVIEW_FAIL` with no waiver. The candidate must return to `DESIGN_AUTHOR` for
repair and independent re-review. It **may not transfer to `SPEC_AUTHOR`**.
This receipt grants no SPEC, WORK_ORDER, BUILD, provider/helper/network/POST,
remote ingest, persistence, retrieval/RAG, staging, commit, push or later-lane
authority.
