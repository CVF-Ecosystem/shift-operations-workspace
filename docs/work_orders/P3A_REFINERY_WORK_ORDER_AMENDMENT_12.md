# Work Order Amendment 12 — P3-A Preflight Syntax Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-12-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 11 SHA-256: `fe59ef90d61fddba14f15f61d7f69260542b4d8852a9b2110d80e0ef5dd84287`
- Amendment 11 review SHA-256: `4979d8b607b1605da378fab6ed6fb5db798e6977c577e5dea7a8954f8ca61503`
- Amendment 11 authority checkpoint: `c88a752734fe2cc87b6b1028c3efb5cc702340fd`
- Amendment 11 acknowledgment checkpoint: `f56456f1bdeed4874dfc81378073d4eacf4de2b8`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and fail-stop truth

The Amendment 11 continuation stopped at its first preflight command before
any assertion executed. PowerShell returned a parser error because the inline
manifest helper emitted `foreach($x in$p)` instead of syntactically valid
`foreach ($x in $p)`. The command was not retried. No repair path changed,
both archives remain absent, every repair/gate is `NOT_RUN`, and provider/
network/remote-ingest calls were zero. Amendment 11 and its R2 are consumed.

## Retained immutable bindings

- exact retained BUILD: `28`, manifest
  `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791`;
- protected paths: `26`, manifest
  `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20`;
- `pipeline.py` pre-hash:
  `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c`;
- `protection.py` pre-hash:
  `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623`;
- memory archive block: `331` lines,
  `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e`;
- handoff archive block: `390` lines,
  `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14`;
- staged paths: `0`; both archive paths absent.

Manifest records remain ordinal UTF-8
`path + NUL + lowercase_file_sha256 + LF`. Block normalization remains LF plus
`"\n".join(selected_lines) + "\n"` before UTF-8 SHA-256.

## Exact scope and retained repair

The repair ceiling remains exactly the same six paths and final exact 32:

1. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
2. `packages/refinery-bridge/src/refinery_bridge/protection.py`
3. `SESSION/SESSION_MEMORY.md`
4. `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md`
5. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`
6. `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md`

Retain Amendment 11's reviewed semantic helper move, lossless archive
rotation, independently decoded/verified UTF-8/base64 block inputs and one
atomic `apply_patch`. The other 26 BUILD paths remain byte-immutable.

## Corrected continuation

Use a multi-line PowerShell preflight with canonical token separation,
including the literal valid form `foreach ($item in $paths)`. Parse the entire
preflight before execution; any parser/assertion failure stops without retry.
On PASS, follow Amendment 11 steps 2-8 exactly once: verified base64 inputs,
one atomic six-path patch, file-size, focused Refinery `53`, catalog check,
full non-live suite, session/repository/static checks, and final exact-32/
six-touch/protected/archive/link/line/staged audit. Stop first failure.

No provider/network/remote-ingest call, retry, unrelated edit, BUILD commit,
self-review, FREEZE or later-lane action is permitted. A pass yields only a
dirty deterministic-local candidate pending independent BUILD review.

## Required review and fresh R2

Independent authorization review with no waiver is required. After its
authority checkpoint is pushed, a fresh exact human R2 for Amendment 12,
exactly six repair paths/final exact 32 and zero provider/network/remote-ingest
is required for one invocation and no retry.
