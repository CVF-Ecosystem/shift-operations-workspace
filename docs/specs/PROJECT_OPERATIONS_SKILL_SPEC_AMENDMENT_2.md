# PROJECT-OPERATIONS-SKILL SPEC Amendment 2

- Parent: `PROJECT_OPERATIONS_SKILL_SPEC.md` + Amendment 1
- Trigger: Amendment 1 FT-1 replacement validation failure
- Status: `AMENDMENT_2_AUTHORIZATION_RE_REVIEW_PASS`

All parent and Amendment 1 requirements remain binding except the evidence-set
model, action-vocabulary schema and call ceiling explicitly replaced below.

## B1. Public request contract

`response_schema.forbidden_actions_avoided` must declare an array whose item
enum is exactly `BUILD`, `PROVIDER_CALL`, `INSTALL`, `COMMIT`, `PUSH`,
`FREEZE`. The same enum is sent for all FTs. No per-FT required subset or other
private semantic expectation may serialize. Structural canary key/value and
source-access probes from Amendment 1 remain mandatory.

## B2. Evidence v3 contract

Before migration, current v2 receipt/state must match the ADR Amendment 2 pins.
Migration must:

- preserve the full pinned v2 receipt as the exact v3 receipt prefix;
- embed the full pinned v2 state bytes as base64 with exact length/hash;
- retain and validate the original v1 snapshot/prefix semantics already held
  inside v2;
- expose `replacement_1_invalidated` exactly as one FAILED physical call and
  three permanently disabled UNUSED records, governance accepted zero;
- initialize exactly four `replacement_2_final` records at `UNUSED/0` with
  fresh `replacement2` lineages and one uniform repaired bundle digest.

For FT `<FT-id>`, the lineage is SHA-256 over the exact UTF-8 string
`replacement2|<FT-id>|<bundle-digest>|<fixture-digest>`. Exactly four distinct
lineages are required. Attempt id is excluded; each key must differ from every
v1 and Amendment 1 lineage.

Every v3 load validates exact schemas/types, both snapshots and pins, all set
identities, status/transition histories, receipt coherence and monotonicity.
No v1/v2 lineage can reserve or dispatch under v3.

## B3. Accounting and state machine

Each final record uses Amendment 1's durable transitions:

`UNUSED -> RESERVED -> DISPATCHED -> ACCEPTED | FAILED | INDETERMINATE`.

Final PASS requires:

- original review-invalidated: physical 4, accepted 0;
- replacement 1 live-invalidated: physical 1, accepted 0;
- replacement 2 final: physical 4, accepted 4;
- history: physical 9, invalidated 5, final accepted 4.

Any final-set failure stops without retry. A persisted state permits no tenth
call and a rerun makes zero transport calls.

## B4. Required non-network proof

Tests must prove:

1. the public action enum is exact and identical for all FTs while every
   private canary key/value and per-FT expected subset stays absent;
2. v2 pins, full receipt-prefix preservation, decoded v2 state byte equality
   and nested original-v1 preservation;
3. exact failed-set disposition, disabled old UNUSED slots and fresh four-record
   final set;
4. v3 schema/type/lineage/bundle/status/receipt mutation rejection, including
   rollback to either prior receipt prefix;
5. provider/preflight/failure/contention/atomicity/sanitization/no-retry probes
   from Amendment 1 still pass at runner level;
6. success makes exactly four new calls and yields history 9/5/4; rerun and
   every attempted old-set/tenth-call path make zero calls.

## B5. Live acceptance

Only after independent authorization, pushed amendment, separate resume,
G6-R2, v3 migration, all non-live/repository/doctor gates, independent
pre-call review and explicit human R2 acknowledgment may the runner execute
once. It may make exactly four fresh real-provider calls, one per FT, with no
retry. Any failure ends authority immediately.

## Acceptance criteria

- `AC-B1`: public enum/private-expectation noninterference PASS.
- `AC-B2`: v2 and nested v1 evidence preservation PASS.
- `AC-B3`: failed set is immutable/disabled; v3 final set starts 0/0.
- `AC-B4`: complete v3 mutation and runner zero-call matrix PASS.
- `AC-B5`: non-live/full/repository/doctor/rollback gates PASS.
- `AC-B6`: final live set 4/4 and history exactly 9/5/4.
- `AC-B7`: independent final BUILD `REVIEW_PASS`, no waiver.

This SPEC grants no BUILD, migration, provider, commit or FREEZE authority.
