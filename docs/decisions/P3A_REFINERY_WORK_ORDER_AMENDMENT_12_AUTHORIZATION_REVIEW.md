# P3-A Refinery Work Order Amendment 12 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment 12 SHA-256: `a16c32a5c351d4fabb06ad64f24d0f3ad3bcc3dda5194e978d8abf1e3b627918`
- Consumed Amendment 11 SHA-256: `fe59ef90d61fddba14f15f61d7f69260542b4d8852a9b2110d80e0ef5dd84287`
- Amendment 11 review SHA-256: `4979d8b607b1605da378fab6ed6fb5db798e6977c577e5dea7a8954f8ca61503`
- Amendment 11 authority checkpoint: `c88a752734fe2cc87b6b1028c3efb5cc702340fd`
- Amendment 11 acknowledgment checkpoint: `f56456f1bdeed4874dfc81378073d4eacf4de2b8`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 12 accurately consumes Amendment 11's parser-time preflight stop and
corrects only that syntax defect. A canonical multi-line PowerShell script with
literal `foreach ($item in $paths)` token separation is syntactically valid;
PowerShell parses the complete script before executing assertions, so the
fail-first boundary remains intact. The accepted verified-base64/atomic-patch
repair, exact six/final-32 scope, immutable bindings, ordered gates,
stop-first/no-retry discipline, and zero-call boundary remain sufficient and
non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not authorize continuation by itself. The authority checkpoint
must be committed/pushed, then the operator must provide Amendment 12's fresh
exact human R2 acknowledgment before one no-retry invocation may begin.

## Consumed Amendment 11 truth

Independent Git and canonical continuity checks establish:

- `HEAD == origin/main == f56456f1bdeed4874dfc81378073d4eacf4de2b8`;
- `c88a752734fe2cc87b6b1028c3efb5cc702340fd` is the pushed Amendment 11
  authorization checkpoint and `f56456f1bdeed4874dfc81378073d4eacf4de2b8`
  is its pushed R2 acknowledgment checkpoint;
- the first preflight command failed at parse time on emitted
  `foreach($x in$p)` before any assertion executed;
- no repair path changed, both archives remained absent, and all repair/gate
  steps were `NOT_RUN`;
- the command was not retried and provider/network/remote-ingest calls were
  `0/0/0`.

Amendment 11 and its R2 are consumed. Amendment 12 does not retry or relabel
that invalid command; it provides a separately reviewed canonical syntax
contract requiring fresh authority.

## Independent retained-binding reproduction

Using ordinal case-sensitive path sorting, UTF-8 records encoded as
`path + NUL + lowercase_file_sha256 + LF`, and the reviewed LF-normalized block
algorithm, the reviewer reproduced:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact retained BUILD manifest | `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791` | same | `PASS` |
| Protected-26 manifest | `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20` | same | `PASS` |
| `pipeline.py` pre-hash | `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c` | same | `PASS` |
| `protection.py` pre-hash | `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623` | same | `PASS` |
| Memory archive block | `331` / `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e` | same | `PASS` |
| Handoff archive block | `390` / `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Both archive paths | absent | absent | `PASS` |

The exact retained BUILD set remains 28 paths and the protected set remains 26.
Therefore Amendment 11's parser stop caused zero repair touch and no partial
atomic-patch output.

## Corrected preflight and retained repair contract

The required preflight form is executable and bounded:

- it must be a multi-line PowerShell script, avoiding minified token adjacency;
- the path loop must use the literal canonical form
  `foreach ($item in $paths)`;
- PowerShell parses the complete script before execution, so any parser failure
  occurs before the first lineage/hash assertion and before every write;
- any later assertion failure stops immediately without repair or retry.

After preflight PASS, Amendment 12 incorporates Amendment 11 steps 2-8 without
semantic expansion: obtain each archive block independently as one UTF-8/base64
payload; decode and verify count/digest; construct one atomic patch covering
all six paths; call `apply_patch` once; then file-size, focused Refinery `53`,
catalog `--check`, full non-live suite, repository/static checks, and final
exact-scope/integrity audit. A decode, digest, marker, scope, patch, or gate
failure stops and is not retried.

The repair ceiling remains exactly six paths. Both Python paths already belong
to retained exact 28; the two modified front doors and two archives add four,
yielding final exact 32. The other 26 BUILD paths remain byte-immutable.

The retained semantic repair moves only the closed quarantine-reason mapping
from the 304-line pipeline into the 241-line protection module, imports it back
under the private alias, and removes only the newly unused enum import. It may
not change behavior, contracts, receipts, routing, tests, dependencies,
assertions, catalog metrics, or debt. The two exact normalized blocks move
verbatim into bounded archives with resolving relative links and all four
Markdown files at or below 600 lines.

## Claim boundary and next governed move

No provider/network/remote-ingest call, retry, unrelated edit, waiver,
debt/exception entry, catalog write, BUILD commit/push, self-review, FREEZE,
or later lane is authorized. A pass yields only a dirty exact-32
deterministic-local BUILD/continuity candidate pending independent BUILD review;
it proves no runtime, persistence, `data_scope`, retrieval/RAG, learning,
production, P3-A closure, or Phase 3 completion.

COMMIT_STEWARD may create/push only the Amendment 12 authority checkpoint under
the bounded governance discipline while preserving exact-28 BUILD unstaged and
both archives absent. Then stop for fresh exact Amendment 12 R2, authorizing
one continuation invocation only and no retry.
