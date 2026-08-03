# Work Order Amendment 1 — Project Operations Skill Review Repair

- Parent: `PROJECT_OPERATIONS_SKILL_WORK_ORDER.md`
- Repair findings: `POS-BUILD-REV-F1..F5`
- Status: `AUTHORIZATION_RE_REVIEW_PASS — REPAIR BLOCKED UNTIL PUSHED RESUME CHECKPOINT AND G6-R`

## 1. Exact repair ceiling

Repair only the same eight parent BUILD paths. Every path remains required;
the skill and metadata may stay byte-identical if independent diff inspection
proves F1-F5 need no change there. No ninth final path, new temp/lock name,
catalog, continuity or provider-config edit is authorized in repair BUILD.

The current eight paths remain unstaged. Before repair, verify exact originals:
receipt `39659` bytes / SHA-256
`d21d64467538fee3a8a2608c8b0907975cab523ce4075637322c400ebc233b9e`;
state `42044` bytes / SHA-256
`e94534b121bdc937d1cb695663d6e1eb3366e6ec0fae41d43ed4a14d072342d5`.
After G6-R, receipt migration keeps those exact bytes as prefix; state migration
embeds those exact bytes base64 with hash/length and exposes validated original
semantics. Any mismatch stops before repair/network.

## 2. Repair implementation order

1. Split public fixtures from private expectations by API/access boundary; add
   unique private-canary and answer-prescribing-instruction scans.
2. Add durable `DISPATCHED/physical_call=1` before transport and crash probes.
3. Add exact state schemas, recomputed identities, status/type validation and
   state/receipt coherence plus full mutation matrix.
4. Add strict response types and complete zero-call preflight matrix.
5. Migrate retained evidence to `original_invalidated` plus empty
   `replacement_final`; verify exact receipt prefix and decoded state snapshot,
   historical physical four and governance accepted zero.
6. Run focused tests, full non-live suite, quick validation, repository gates,
   secret scan and doctor. Inspect exact eight paths and zero runtime residue.
7. Only then run the amended runner once for exactly four replacement calls.
8. Run post-call non-network gates and exact-parent rollback rehearsal; report
   history `8 physical / 4 invalidated / 4 final accepted`.

## 3. Replacement call authority

After independent amendment approval, pushed amendment, separate repair-resume
checkpoint and G6-R PASS, authorize exactly four new physical calls: one
replacement lineage for each FT. They use the repaired uniform bundle and
public fixture digests. No retry, fifth replacement or ninth historical call.
Any failed/indeterminate replacement consumes its slot and stops for another
reviewed amendment.

## 4. G6-R

Before repair: rehydrate amendment reads; verify HEAD/origin equality with the
pushed repair checkpoint; confirm the exact eight partial BUILD paths and zero
staged/runtime residue; verify both pinned originals, recompute original bundle
and 4-call history; verify
provider prerequisites without values; run current full non-live baseline,
repository gates and doctor. No call or repair edit on failure.

Before replacement network: all amended tests and preflight matrices must pass,
the repaired bundle must be stable, original evidence must be durably marked
invalid, and replacement records must all be `UNUSED` at physical zero.

## 5. Independent review and commit

The `REPAIR_WORKER` may not stage/commit/push/self-review. The independent
`REVIEWER` performs source and state mutation probes without provider calls,
confirms F1-F5 closed, original evidence retained, replacement 4/4 and history
8/4/4. Only `REVIEW_PASS` transfers exact-eight-path commit ownership to the
`COMMIT_STEWARD`; C4 remains separate.

## 6. Stop conditions

Stop on answer leakage, non-exact type, unaccounted dispatch, invalid state
accepted, state/receipt mismatch, original evidence loss, mixed replacement
bundle, preflight call/mutation, outside path, failed gate, runtime residue,
secret output, replacement failure, retry route or possible ninth call.

This amendment authorizes no repair or provider call until independent
authorization `REVIEW_PASS` and the pushed checkpoint/G6-R sequence complete.

## 7. Authorization disposition

`AMENDMENT_1_AUTHORIZATION_RE_REVIEW_PASS`, no open finding or waiver. Repair
1 closed the initial three amendment findings. The same eight partial BUILD
paths remain unstaged; exactly four replacement calls become available only
after this amendment and a separate resume checkpoint are pushed and G6-R
passes. No ninth historical call is authorized.
