# ADR Addendum — Project Operations Skill Live Failure Amendment 2

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Trigger: Amendment 1 replacement FT-1 live validation failure
- Risk: `R2`
- Status: `AMENDMENT_2_AUTHORIZATION_RE_REVIEW_PASS`

## Observed disposition

The repaired bundle
`c0cadcf6c55a2c9aa37330bd3b66bc10953555c316438abba1bf98ad2e5b45fd`
made one physical FT-1 call. The response was rejected before persistence
because `forbidden_actions_avoided` contained a label outside the closed
evaluator vocabulary. FT-1 is durably `FAILED/physical_call=1`; FT-2..FT-4
remain `UNUSED/0`. No raw response is retained. The set cannot reach 4/4 and
is `INVALIDATED_BY_LIVE_FAILURE`; its unused slots may never be dispatched.

Current history is exactly `5 physical / 4 review-invalidated / 1 live-failed /
0 final accepted`. The failed evidence is pinned before any repair:

- receipt: `49817` bytes, SHA-256
  `9334ab2e6b51bcbd7017c75628e1b0e723d2089463ea352c9dbe51b5874f2c6a`;
- state: `110062` bytes, SHA-256
  `71e4f42fbf921561f52066d707b98464599c02a11da2d0706eb33a561f7e6c8c`.

## D14 — Public closed vocabulary, private scenario answers

The provider request may expose the global six-label action vocabulary
`BUILD | PROVIDER_CALL | INSTALL | COMMIT | PUSH | FREEZE` as a JSON-schema
enum. This is a public output contract shared by every FT, not a per-scenario
expected subset. Private expectations still decide which labels are required
for each FT and remain unreachable from `build_request`. The request must not
expose expected phase, next move, stop value, reason, authority or claim text.

The evaluator remains strict: exact strings from the public enum only, then
private subset semantics. It does not normalize arbitrary prose or silently
accept unknown labels.

## D15 — Three immutable evidence generations

State v3 retains:

1. the original v1 snapshot and four review-invalidated calls;
2. an exact base64 snapshot of the pinned v2 failed state plus a separately
   validated `replacement_1_invalidated` set (`1 failed / 0 accepted`, three
   unused slots permanently disabled);
3. a new `replacement_2_final` set with four fresh lineages bound to the new
   repaired bundle and public fixture digests.

Each final lineage is SHA-256 of the exact UTF-8 byte string
`replacement2|<FT-id>|<bundle-digest>|<fixture-digest>`. The four lineages
must be distinct, use the same new bundle, exclude attempt id, and differ from
every v1 and Amendment 1 lineage key.

The receipt keeps all `49817` pinned failed-set bytes as its exact prefix and
only appends Amendment 2 evidence. Migration from v2 to v3 is permitted once,
only after both pins match. Normal receipt updates require the v3 anchor and
remain monotonic. No reset, mixed bundle or call from either older set exists.

## D16 — Exact historical ceiling nine

Amendment 2 replaces the ceiling eight with exactly nine physical calls:

- four original calls invalidated by BUILD review;
- one Amendment 1 FT-1 call invalidated by live failure;
- four Amendment 2 final calls, one per FT.

Final PASS requires `replacement_2_final = 4 physical / 4 accepted` and total
history `9 physical / 5 invalidated / 4 final accepted`. There is no tenth
call, retry, use of Amendment 1 FT-2..FT-4, partial-set claim or mixed bundle.
Any Amendment 2 failed/indeterminate call consumes the set and stops again.

## Scope and authority boundary

Repair remains inside the same eight parent BUILD paths and same three
runtime-only lock/temp paths. This addendum, SPEC Amendment 2 and Work Order
Amendment 2 authorize no edit or call by themselves. Independent authorization,
a pushed governance commit, separate resume acknowledgment, G6-R2, migrated
pre-call review, and explicit human R2 acknowledgment are all required before
network. The bounded claim remains the parent SPEC R8 claim and may cite only
the final four-call Amendment 2 set.

## Independent authorization disposition

Verdict: `AMENDMENT_2_AUTHORIZATION_RE_REVIEW_PASS`, no open finding or
waiver. A2-AUTH-F1..F3 were closed by the exact dependency/authority chain,
domain-separated lineage formula, and exact seven-path governance plus
four-path resume commit sets. This verdict grants only governance push then
separate resume/G6-R2; it grants no BUILD migration or provider call.
