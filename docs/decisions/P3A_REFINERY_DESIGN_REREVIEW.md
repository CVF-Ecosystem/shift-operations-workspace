# P3-A Refinery — Independent DESIGN Re-review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `INDEPENDENT_DESIGN_REREVIEWER`
- Re-reviewed ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Retained DESIGN review SHA-256: `fcb8c3f96bd2ed524c2bb4457a338a3e9c7cfde4b120090091e298d30eb2ab45`
- Parent INTAKE SHA-256: `271dd0085da921ff9f9d75ec9864bb09f56d9c45df8491aa4a82e26041a239b7`
- INTAKE review SHA-256: `a1fbe91244c0932f9d21fa29fd779d8a51f9c54158c8ccbb9febf1d0809b7e28`
- Disposition: `DESIGN_REVIEW_PASS`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed boundary

This re-review compared the repaired ADR with retained findings F1–F4, the
accepted INTAKE and INTAKE review, current continuity, the refinery contract
and boundary/control documents, `data-policy.yaml`, and the existing negative
fixture. The pass applies only to the exact ADR hash above.

No provider, helper, network, POST, staging, commit or push action was used.

## Finding closure

### F1 — CLOSED: dedupe and collision mechanics

`DedupeContextV1` now fixes the scope, inclusive UTC window, 500-record bound
and validation failures. Each prior record has an exact tuple and every source
or candidate fingerprint is the three-field `(sha256, sha512, byte_length)`.
Full triple equality defines a match; partial digest/length agreement is a
typed `DIGEST_COLLISION_SUSPECTED` quarantine signal. Matching is deterministically
ordered by `(observed_at, prior_source_id)`, and malformed, duplicate-id,
out-of-window or missing context fails closed. Source-match suppression and
redacted-candidate advisory matching remain caller-scoped and make no global
identity or exactly-once claim.

### F2 — CLOSED: source/quarantine ownership and route behavior

The envelope now carries an explicit opaque `source_owner_id`, distinct from
`source_link`, quarantine `owner_id` and `sink_id`. `QuarantineRouteV1` binds
those quarantine authorities to policy version, the current 30-day hint and
route availability. The closed twelve-value quarantine reason taxonomy covers
envelope/provenance, ambiguity/transform, dedupe/collision, policy, redaction,
conflict, quality and invariant failures. An absent, invalid or unavailable
route—or a non-current retention hint—deterministically returns
`NO_CANDIDATE_FALLBACK / QUARANTINE_ROUTE_UNAVAILABLE`; it can never admit a
candidate or imply sink acknowledgment. P3-A owns neither raw retention nor
quarantine persistence.

### F3 — CLOSED: receipts, disposition and candidate absence

The ADR requires exactly nine stage receipts in fixed order. After the first
non-PASS receipt, every later stage is `NOT_RUN`; skipped stages cannot be
reported as successful, and the quality receipt cannot upgrade an earlier
failure. The precedence is total: unavailable/invariant/no-route fallback,
then valid exact duplicate, then routed closed quarantine/invalid-context/
collision/below-100 outcomes, and finally ready only after nine PASS receipts
and quality 100.

`RefineryResultV1` makes the invariant structural: exactly the matching
duplicate, quarantine or fallback receipt exists for a non-ready disposition;
none exists for ready; contradictory combinations are rejected; and
`context_candidate` is non-null exactly for `CANDIDATE_READY` and null for all
other dispositions. There is no partial-candidate fallback.

### F4 — CLOSED: candidate schema and reproducible fingerprint

`ContextCandidateV1` now has a closed V1 preimage: schema version, redacted
normalized text, sensitivity, sorted unique topic labels, the named source
identity/owner/link/version fields and source fingerprint triple, the five
named rule-set versions, and quality score plus four named integer components.
No optional or additional V1 preimage field is allowed, and raw text and all
truth/provider/retrieval fields are forbidden.

Canonical bytes are explicitly UTF-8 over Python `json.dumps` with sorted
keys, compact separators, unescaped Unicode and NaN rejection; floats, nulls
and non-string map keys are prohibited, and topic-label ordering is defined.
The stored candidate fingerprint is lowercase SHA-256, lowercase SHA-512 and
byte length over those bytes, beside and therefore excluded from its own
preimage. It is only a change/dedupe aid, not a signature or authority receipt.

## Rechecked accepted boundaries

- Provenance fingerprints the exact strictly decoded UTF-8 text supplied
  before normalization and does not attest the upstream envelope, sender,
  channel, signature, retention or delivery semantics.
- Normalization remains deterministic and syntax-only. It forbids fuzzy
  substitution, translation, tense/action reinterpretation and inferred
  AM/PM/timezone. The unsupported `11h40 -> 23:40` and action paraphrase stay
  negative evidence.
- Sensitivity remains exactly `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, or
  `RESTRICTED`, aligned by contract tests with `data-policy.yaml`, separate
  from topic labels and non-decreasing from the declared floor. Policy drift
  fails closed.
- Redaction outputs and public errors do not echo matched values or raw text;
  malformed/overlapping spans, unsafe replacement and residue fail closed.
- Quality 100 is deterministic control coverage, never truth, probability,
  semantic confidence or production quality.
- The current fixture remains a negative/quarantine case; separate synthetic
  positive and adversarial fixtures are required and prove only local
  deterministic behavior.
- Dependency direction stays a pure local package with no provider, network,
  database, environment-secret, application-router, ledger or retrieval
  dependency. P3-A does not call or claim load-bearing `data_scope`.
- P3-B runtime gate wiring, P3-C retrieval contracts, retrieval/RAG, learning,
  external ingest, persistence, confirmed truth and production remain parked.
  Any future claim that this boundary actually gates provider context needs a
  real runtime caller and separately authorized fresh real-provider evidence.

## Disposition and transfer boundary

`DESIGN_REVIEW_PASS` with no waiver. All retained F1–F4 findings are closed at
the DESIGN level. The unchanged candidate at ADR SHA-256
`57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e` **may
transfer to `SPEC_AUTHOR`**. Any ADR content change invalidates this transfer
and requires independent re-review.

This receipt grants SPEC authoring only. It grants no WORK_ORDER, BUILD,
provider/helper/network/POST, remote ingest, persistence, retrieval/RAG,
staging, commit, push or later-lane authority.
