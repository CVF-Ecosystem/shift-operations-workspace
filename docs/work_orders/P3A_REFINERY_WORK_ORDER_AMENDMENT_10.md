# Work Order Amendment 10 — P3-A File-Size Guard Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-10-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 9 SHA-256: `417a11af86915cca0249e3559236f498fc96f7e60c8363376b4493f26aefca0e`
- Amendment 9 authorization review SHA-256: `6b7819f41d769c0304b495d26319d64619944b5d869fd92ee0fc9115f3786c46`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Amendment 9 acknowledgment checkpoint: `be63d4505e8b79e96e849090f34462b9918ed550`
- Amendment 9 authority checkpoint: `422890062dbf5ee28346311abb6a2a4b13dee5f9`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

The Amendment 9 acknowledgment was pushed at
`be63d4505e8b79e96e849090f34462b9918ed550`. Its preflight passed the exact
immutable post-repair 28-path binding and zero-repair boundary. The first
remaining gate, `python scripts/check_file_size.py`, returned non-zero with
exactly three findings:

1. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`: `304 > 300`;
2. `SESSION/SESSION_MEMORY.md`: `616 > 600`;
3. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`: `724 > 600`.

Execution stopped immediately. Repository/static/final gates were not run and
the file-size command was not retried. Zero provider/network/remote-ingest
calls occurred. Amendment 9 and its R2 are consumed.

The operator requested proactive finding resolution. This amendment repairs
all three findings without an exception/debt entry, preserves continuity
history in bounded archives, and keeps Refinery behavior unchanged.

## Exact retained pre-repair binding

Using typed ordinal case-sensitive sorting and UTF-8 records
`path + NUL + lowercase_file_sha256 + LF`:

- retained BUILD path count: `28`;
- retained exact manifest SHA-256:
  `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791`;
- immutable existing-candidate path count: `26`;
- immutable protected-26 manifest SHA-256:
  `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20`;
- staged path count: `0`.

Python repair pre-hashes:

| Existing repair path | SHA-256 |
|---|---|
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623` |

Both new archive paths below must be absent at preflight. Any mismatch stops.

Continuity is bound by the exact blocks that will be archived, not volatile
whole-file preambles:

| Source block | Normalized lines | SHA-256 |
|---|---:|---|
| `SESSION/SESSION_MEMORY.md`: line beginning `**2026-07-22 (P-FIX-6):**` through immediately before `## Continuity drift — operator ĐÃ giải quyết (giữ lại làm hồ sơ)` | `331` | `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e` |
| active handoff: `## Intake boundary` through EOF | `390` | `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14` |

Compute each digest by universal-newline normalization to LF, exact unique
start/end markers, `"\n".join(selected_lines) + "\n"`, then UTF-8 SHA-256.
Markers must occur exactly once. Authority review and R2 entries may only be
appended before these blocks and are controlled by exact Git checkpoint
lineage; any change inside either archive-source block fails preflight.

Initial authorization review
`43dad00859cb906e446c1e6875dafedbc522e1374c070da195adcf22aa947a14`
returned F1, which is closed. First re-review
`4ed7b30f48f876337cbedd63074098104f6f9b4f1a979e4a54d3fd532f546b7f`
returned only F2 (mandatory R2 append invalidates whole-file hash). The block
binding above resolves both findings and requires fresh independent re-review.

## Exact repair ceiling — 6 paths; final exact 32 paths

Only these paths may change or be created:

1. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
2. `packages/refinery-bridge/src/refinery_bridge/protection.py`
3. `SESSION/SESSION_MEMORY.md`
4. `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md`
5. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`
6. `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md`

The other 26 retained BUILD paths are byte-immutable. Four continuity paths
are added to the dirty set (two modified tracked front doors plus two new
archives), while both Python repair paths already belong to the retained 28.
The final dirty set is therefore exact 32 paths. No other path may change.

## Source split contract

Move `_quarantine_reason` without semantic change from `pipeline.py` to
`protection.py`:

- move its exact closed `StageReason -> QuarantineReason` mapping and return;
- import `QuarantineReason` in `protection.py`;
- import `quarantine_reason` into `pipeline.py` under the existing private
  alias `_quarantine_reason` and remove the now-unused enum import;
- do not change `_failed_result`, `refine`, public contracts, receipt order,
  error routing, tests, dependencies or any other behavior;
- finish with both Python files at or below 300 lines; no compressed statements,
  assertion deletion, exception/debt entry or catalog metric change.

## Continuity rotation contract

Preserve text verbatim while rotating long history:

- in `SESSION/SESSION_MEMORY.md`, move the bounded historical block beginning
  at `2026-07-22 (P-FIX-6)` and ending immediately before
  `## Continuity drift — operator ĐÃ giải quyết` into
  `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md`; replace it with
  a relative archive pointer and keep all current P3-A/top entries plus later
  canonical sections in the front door;
- in the active P3-A handoff, move the block beginning `## Intake boundary`
  through end-of-file verbatim into
  `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md`;
  replace it with a relative archive pointer while keeping the current
  disposition and Amendment 4-10 chain in the active handoff;
- each archive gets only a short title/preservation note plus the verbatim
  moved block; no historical claim may be edited, summarized away or deleted;
- all four Markdown files must be at or below 600 lines and links must resolve;
  canonical active state/handoff pointers do not change.

## Ordered continuation

Run once in this exact order, stopping on the first non-zero command or
contract failure:

1. verify pushed authority lineage, Work Order/review/rereview hashes, empty
   staged set, exact retained-28/protected-26 digests, both Python pre-hashes,
   both exact continuity block digests/line counts and both archives absent;
2. perform only the exact six-path source split and continuity rotation;
3. run `python scripts/check_file_size.py` once;
4. run the retained focused Refinery suite once (`53` expected) because two
   source files moved code;
5. run catalog `python scripts/generate_catalog.py --check` once and require no
   catalog mutation;
6. run the full non-live pytest suite once;
7. run session-state, repository validator, JSON/YAML, forbidden import/I/O,
   secret and diff checks once;
8. verify exact final 32 paths, exact six repair touches, unchanged
   protected-26 digest, equivalent source behavior, archive integrity/links,
   file-size limits and empty staged set.

Retain without rerun: Amendment 8 direct probe 7/7, three-path catalog/
knowledge repair, project-knowledge validator, focused Knowledge Pack `86` and
its catalog write/check evidence. The failed Amendment 9 file-size command is
not retried or relabeled; Amendment 10's post-repair file-size command is fresh.
No provider/network/remote-ingest call is permitted.

## Stop and claim boundary

A pass yields only a dirty exact 32-path deterministic-local BUILD/continuity
repair candidate pending fresh independent BUILD review. It authorizes no
BUILD commit/push, self-review, FREEZE, runtime caller, persistence,
`data_scope`, retrieval/RAG, learning, production or Phase 3 completion claim.

## Required review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to this
Amendment SHA, six repair/final-32 boundary, protected digest, semantic source
move, lossless continuity rotation, ordered gates and zero-call/no-retry rule.
After its authority checkpoint is committed/pushed, the operator must send:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-10-2026-08-04,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 6 repair paths và final
> exact 32 BUILD/continuity paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
