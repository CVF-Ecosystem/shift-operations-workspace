# PROJECT-OPERATIONS-SKILL SPEC Amendment 4

- Parent: base SPEC + Amendments 1–3
- Status: `AMENDMENT_4_AUTHORIZATION_RE_REVIEW_PASS`

## D1. Uniform phase semantics

Every request must define `current_phase` as the phase explicitly reported by
the synthetic canonical-state facts before blocker evaluation, and
`next_allowed_move` as the governed action after blocker evaluation. The same
definition and seven-field public schema apply to all FTs. Private expected
phases are FT-1 SPEC, FT-2 WORK_ORDER, FT-3 SPEC and FT-4 REVIEW. Amendment 3's
private next/stop/reason/action-subset rules and exact public tokens remain.
No per-FT expected value, equivalence, subset or canary may serialize.

Evaluation remains strict enum equality/membership/subset logic with no prose,
substring, coercion or retroactive acceptance. Tests must exhaust every allowed
equivalence and every disallowed phase/next/stop/reason/action removal for all
FTs, and prove FT-2 WORK_ORDER+STOP_AT_INTAKE succeeds while INTAKE fails.

## D2. Evidence v5

Migration is allowed only from the exact Amendment 4 pins. It preserves the
full v4 receipt as exact prefix, embeds the full v4 state with exact length/hash
and recursively validates v3/v2/v1. It exposes `replacement_3_invalidated`
exactly as physical 2, mechanical accepted 1, failed 1, governance accepted 0:
FT-1 ACCEPTED/1, FT-2 FAILED/1 with exact safe candidate, FT-3..FT-4 disabled
UNUSED/0. It initializes four `replacement_4_final` records at UNUSED/0.

Each new lineage is SHA-256 over exact UTF-8
`replacement4|<FT-id>|<bundle-digest>|<fixture-digest>`, four distinct values
under one current bundle and unequal to every prior key. Every load validates
exact schemas/types, all snapshots/pins/prefixes, candidate safety, identities,
statuses, transitions, receipt coherence and monotonicity.

## D3. Accounting, proof and live acceptance

Migrated start is exactly `8/8/0`; final PASS is replacement 4 `4/4` and total
`12/8/4`. Existing durable dispatch-before-transport, candidate sanitization,
preflight/atomicity/contention/failure/no-retry tests remain. Tests additionally
prove all older dispatch and thirteenth-call paths make zero transport calls.

Only after authorization PASS, pushed governance and separate resume, G6-R4,
independent source/temp review, zero-call v5 migration, focused/full/repository/
doctor gates, independent migrated-state pre-call review and a new human R2
acknowledgment may the runner execute once for at most four real calls. It
stops at the first failure and is never rerun.

## Acceptance criteria

- `AC-D1`: one global phase meaning and exhaustive private matrix PASS.
- `AC-D2`: exact v4/v3/v2/v1 preservation and replacement-3 invalidation PASS.
- `AC-D3`: fresh replacement-4 identity and mutation/no-call matrix PASS.
- `AC-D4`: migration 8/8/0; final live set 4/4 and total 12/8/4.
- `AC-D5`: all gates and independent final BUILD REVIEW_PASS, no waiver.

Authorization re-review passed without finding or waiver. This SPEC grants
only the exact governance push and separate resume; no BUILD, migration,
provider or FREEZE authority.
