# Work Order Amendment 11 — P3-A Atomic Patch Construction Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-11-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 10 SHA-256: `6c396f1fc6faad345a5ae12d3d928e515d4c5bbf46a14b9743015740e1b2634b`
- Amendment 10 authorization re-review 2 SHA-256: `f06ca38053b6315922513b0f646c7c5e8cda69f9beb0ad072d4fc21409c23944`
- Amendment 10 authority checkpoint: `14139b9b38d18f31d34a2a2e9c1a2a02415b47af`
- Amendment 10 acknowledgment checkpoint: `9b1e34df7661a6a9877046ac65f770c772d1495b`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

Amendment 10's pushed-lineage and immutable preflight passed in full. Before
any repair edit, the local orchestration that was constructing one atomic
`apply_patch` payload raised:

`TypeError: Cannot read properties of undefined (reading 'split')`

The failure occurred while expanding `data.memoryBlock`; `apply_patch` was
never called. Execution stopped immediately and was not retried. Exactly zero
repair paths changed, both archives remain absent, all post-repair gates are
`NOT_RUN`, and provider/network/remote-ingest calls were `0/0/0`. Amendment 10
and its R2 are consumed.

This amendment corrects only the local patch-construction contract. It does
not expand or alter the already independently accepted repair semantics.

## Exact retained binding

Using ordinal case-sensitive sorting and UTF-8 records
`path + NUL + lowercase_file_sha256 + LF`:

- retained BUILD paths: `28`;
- retained exact-28 manifest SHA-256:
  `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791`;
- protected existing-candidate paths: `26`;
- protected-26 manifest SHA-256:
  `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20`;
- staged paths: `0`.

Python pre-hashes remain:

- `pipeline.py`: `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c`;
- `protection.py`: `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623`.

Normalized archive-source blocks remain:

- memory: unique `**2026-07-22 (P-FIX-6):**` start through immediately before
  unique `## Continuity drift` heading, `331` lines,
  SHA-256 `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e`;
- active handoff: unique `## Intake boundary` through EOF, `390` lines,
  SHA-256 `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14`.

Normalize universal newlines to LF and hash
`"\n".join(selected_lines) + "\n"` as UTF-8. Both archive paths must be absent.

## Exact repair ceiling — unchanged 6 paths; final exact 32

Only these paths may change or be created:

1. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
2. `packages/refinery-bridge/src/refinery_bridge/protection.py`
3. `SESSION/SESSION_MEMORY.md`
4. `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md`
5. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`
6. `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md`

The two Python paths already belong to the retained 28. The two modified
front doors and two archives add four paths, so final dirty scope is exact 32.
The other 26 retained BUILD paths are byte-immutable.

## Retained repair semantics

Move the exact closed `StageReason -> QuarantineReason` mapping from
`pipeline.py` to `protection.py` as `quarantine_reason`, import it back under
the existing private alias `_quarantine_reason`, and remove only the resulting
unused enum import. Do not change behavior, public contracts, receipt order,
error routing, tests, dependencies, assertions, catalog metrics or debt.

Move the exact normalized memory and handoff blocks verbatim into their named
archives. Each archive receives only a short title/preservation note before
the verbatim block. Replace each moved block with a resolving relative pointer;
keep current P3-A/disposition content and later canonical memory sections in
their front doors. All four Markdown files must be at most 600 lines.

## Corrected patch-construction contract

Before calling `apply_patch`, obtain each source block independently as a
single UTF-8/base64 payload from a read-only local command. Decode each payload
directly, verify its line count and SHA-256 against the bindings above, and
construct one atomic patch covering all six paths. Do not depend on optional
JSON object properties, do not use shell/Python file writes, and do not call
`apply_patch` unless both decoded blocks pass. A patch rejection or any decode,
count, digest, marker or scope mismatch is the first failure and stops without
retry.

## Ordered continuation

Run once, stopping at the first non-zero command or contract failure:

1. verify pushed authority lineage, artifact hashes, empty staged set,
   exact-28/protected-26 manifests, Python pre-hashes, block bindings and
   archive absence;
2. construct and apply the single corrected atomic six-path patch above;
3. run `python scripts/check_file_size.py` once;
4. run the retained focused Refinery suite once (`53` expected);
5. run `python scripts/generate_catalog.py --check` once and require no
   catalog mutation;
6. run the full non-live pytest suite once;
7. run session-state, repository validator, JSON/YAML, forbidden import/I/O,
   secret and diff checks once;
8. verify exact final 32 paths, exact six repair touches, unchanged
   protected-26 digest, equivalent source behavior, verbatim archives,
   resolving links, line limits and empty staged set.

Retain without rerun all Amendment 8/9 evidence named by Amendment 10. No
provider/network/remote-ingest call is permitted.

## Stop and claim boundary

A pass yields only a dirty exact-32 deterministic-local BUILD/continuity
candidate pending fresh independent BUILD review. No BUILD commit/push,
self-review, FREEZE, runtime caller, persistence, `data_scope`, retrieval/RAG,
learning, production or Phase 3 completion is authorized.

## Required review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to this
Amendment SHA and the corrected atomic patch construction. After its bounded
authority checkpoint is pushed, the operator must provide a fresh exact R2
for Amendment 11, exactly six repair paths/final exact 32 and zero provider/
network/remote-ingest calls. That acknowledgment authorizes one invocation and
no retry.
