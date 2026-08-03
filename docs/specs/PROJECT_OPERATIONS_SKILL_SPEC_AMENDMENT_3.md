# PROJECT-OPERATIONS-SKILL SPEC Amendment 3

- Parent: `PROJECT_OPERATIONS_SKILL_SPEC.md` + Amendments 1 and 2
- Trigger: Amendment 2 FT-1 private-semantic rejection
- Status: `AMENDMENT_3_AUTHORIZATION_REVIEW_PASS`

All parent requirements remain binding except the response representation,
evidence generation and physical-call ceiling explicitly replaced below.

## C1. Uniform public response contract

Every FT request must serialize the identical strict seven-field response
schema and public vocabularies in ADR Amendment 3 D17. No per-FT expected
value, equivalence class, required forbidden-action subset, canary key/value or
private evaluator record may be reachable from `build_request`.

The evaluator requires exact keys, strict types, enum membership, unique action
labels, exact authority/claim tokens, then private equality, membership and
subset rules. It must perform no case folding, substring matching, arbitrary
prose normalization or truthy coercion.

## C2. Bounded candidate retention

On private-semantic failure only, the runner may persist `candidate_response`
after all public structural and safety validation succeeds. The value must be
the canonical parsed seven-field object and contain only public enum/token and
boolean values. It must be rejected/omitted for invalid JSON, wrong keys or
types, unknown/duplicate enum values, unsafe content or provider-envelope
data. Its presence never changes `FAILED`, accounting or no-retry behavior.

## C3. Evidence v4 contract

Migration is allowed only when the current receipt/state match the Amendment 3
pins. It must:

- preserve all pinned v3 receipt bytes as the exact v4 receipt prefix;
- embed all pinned v3 state bytes as base64 with exact length/hash;
- recursively validate the nested v2/v1 snapshots and prefixes;
- expose replacement 2 as FT-1 `FAILED/1`, FT-2..FT-4 disabled `UNUSED/0`,
  governance accepted zero;
- initialize exactly four `replacement_3_final` records at `UNUSED/0` with one
  new uniform bundle and fresh lineages.

For each FT, lineage is SHA-256 of exact UTF-8
`replacement3|<FT-id>|<bundle-digest>|<fixture-digest>`. The keys must be four
distinct values and unequal to every prior-generation key. Every load validates
exact schema/types, all pins/snapshots/prefixes, identities, bundles, statuses,
transitions, receipt coherence and monotonicity.

## C4. Accounting and state machine

The durable state machine remains
`UNUSED -> RESERVED -> DISPATCHED -> ACCEPTED | FAILED | INDETERMINATE`.
Final PASS requires original `4/0`, replacement 1 `1/0`, replacement 2 `1/0`,
replacement 3 `4/4`, and total `10 physical / 6 invalidated / 4 final
accepted`. Any final-set failure stops without retry. A completed or failed v4
state permits no further transport call and no path can make an eleventh call.

## C5. Required non-network proof

Tests must prove:

1. identical public schema/enums for all FTs and structural noninterference of
   all private answers/canaries;
2. exact deterministic private semantics for each FT, including every allowed
   equivalence and every rejected neighboring value;
3. candidate retention only after safe public validation, canonical content,
   durable FAILED accounting, and absence of envelope/free text/secrets;
4. exact v3 pins/prefix/snapshot plus recursive v2/v1 preservation;
5. immutable disabled replacement 2 and four fresh replacement-3 records;
6. v4 schema/type/lineage/bundle/status/receipt/rollback mutation rejection;
7. preflight, provider failure, contention, atomicity, sanitization and
   no-retry probes retained from prior amendments;
8. success makes exactly four new calls and produces 10/6/4; rerun, old-set,
   failed-set and eleventh-call probes make zero transport calls.

## C6. Live acceptance

Only after authorization review PASS, pushed amendment, separate pushed resume,
G6-R3, zero-call v4 migration, all repository/doctor gates, independent source
and migrated-state reviews, and a fresh explicit human R2 acknowledgment may
the runner execute once. It may make exactly four fresh real-provider calls,
one per FT, without retry. Any failure ends authority immediately.

## Acceptance criteria

- `AC-C1`: uniform public structured contract/private noninterference PASS.
- `AC-C2`: deterministic equivalence and rejection matrix PASS.
- `AC-C3`: bounded semantic-failure diagnostics PASS.
- `AC-C4`: v3/v2/v1 preservation and replacement-2 invalidation PASS.
- `AC-C5`: v4 mutation/zero-call/exact 10/6/4 matrix PASS.
- `AC-C6`: full non-live/repository/doctor/rollback gates PASS.
- `AC-C7`: final live replacement set 4/4 and total exactly 10/6/4.
- `AC-C8`: independent final BUILD `REVIEW_PASS`, no waiver.

Independent authorization review passed without finding or waiver. This SPEC
grants only the exact governance commit/push and separate resume checkpoint; it
grants no BUILD, migration, provider or FREEZE authority.
