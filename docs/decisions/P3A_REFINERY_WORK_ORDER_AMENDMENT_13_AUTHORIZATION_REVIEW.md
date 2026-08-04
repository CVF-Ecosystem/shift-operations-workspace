# P3-A Refinery Work Order Amendment 13 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment 13 SHA-256: `332895d89799ec724031057cf265b1c84e6a62a8510b6f86363a4fe309f9da50`
- Consumed Amendment 12 SHA-256: `a16c32a5c351d4fabb06ad64f24d0f3ad3bcc3dda5194e978d8abf1e3b627918`
- Amendment 12 review SHA-256: `6b807775c665c98d089be047ab81d6dd9a953759cca1906b6a32474c53aa9d32`
- Amendment 12 authority checkpoint: `82071ee8f8fb0615e763d20789c52c7db7a5b594`
- Amendment 12 acknowledgment checkpoint: `bf9daaf3feb108c8f9fd63352e5d80ddfec7e717`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 13 truthfully consumes Amendment 12's runtime-only decoder failure
before patch construction and corrects only that seam. Its strict pure-JavaScript
scalar decoder contract is runtime-neutral and fail-closed for every malformed
UTF-8 class, while retaining independent base64/source verification and the
single atomic six-path patch. Exact six/final-32 scope, semantic repair,
lossless rotations, ordered gates, stop-first/no-retry discipline, and the
zero-call boundary remain sufficient and non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not itself authorize continuation. The authority checkpoint
must be committed/pushed and followed by Amendment 13's fresh exact human R2
acknowledgment before one no-retry invocation may begin.

## Consumed Amendment 12 truth

Independent Git and canonical continuity checks establish:

- `HEAD == origin/main == bf9daaf3feb108c8f9fd63352e5d80ddfec7e717`;
- `82071ee8f8fb0615e763d20789c52c7db7a5b594` is the pushed Amendment 12
  authority checkpoint and `bf9daaf3feb108c8f9fd63352e5d80ddfec7e717`
  is its pushed R2 acknowledgment checkpoint;
- Amendment 12's canonical multi-line preflight passed;
- at step 2, two independent local commands successfully selected, normalized,
  line-counted, SHA-verified, and base64-encoded the two archive blocks;
- V8 then raised `ReferenceError: TextDecoder is not defined` before patch
  construction and before `apply_patch`;
- repair touches remained `0/6`, both archives stayed absent, and every later
  gate was `NOT_RUN`;
- execution stopped without retry and provider/network/remote-ingest calls
  were `0/0/0`.

Amendment 12 and its R2 are consumed. Amendment 13 is a separately reviewed
runtime-neutral decode command under fresh authority, not a retry or relabeling
of the failed `TextDecoder` invocation.

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

The exact BUILD set remains 28 and the protected set remains 26. Therefore the
decoder failure left the complete accepted repair input byte-unchanged.

## Strict pure-JavaScript decoder review

The decoder requirements are complete and executable without `TextDecoder`,
`atob`, Node, helper files, or optional runtime APIs:

- independently generated payloads retain strict base64 decoding/validation
  and the previously reviewed source count/digest checks;
- ASCII bytes decode directly; valid two-, three-, and four-byte sequences are
  accepted only with the required continuation-byte structure;
- isolated continuations, invalid lead bytes, truncation, and invalid
  continuations fail immediately;
- minimum scalar bounds for each width reject overlong forms, including
  `C0/C1`, `E0` low continuations, and `F0` low continuations;
- the `ED A0..BF` range is rejected as surrogate scalars, and `F4 90..BF` plus
  all higher leads are rejected above `U+10FFFF`;
- code points through `U+FFFF` are emitted directly only when non-surrogate;
  valid scalars from `U+10000` through `U+10FFFF` emit exactly one UTF-16
  surrogate pair;
- decoded line counts and retained SHA/source bindings are rechecked before
  patch construction.

Any base64, UTF-8, count, digest, marker, scope, or patch error stops before
later gates and is not retried. This prevents replacement-character recovery,
silent byte loss, invalid-scalar acceptance, or environment-dependent decode.

## Exact repair, atomicity, and ordered gates

The repair ceiling remains exactly six paths and final exact 32. Both Python
paths already belong to the retained 28; two modified front doors and two new
archives add four. The other 26 BUILD paths remain byte-immutable.

Only after both independently decoded blocks pass every verification may one
patch covering all six operations be constructed and sent through one
`apply_patch` call. Shell/Python writes, helper/temp repository files, partial
sequential patches, and retry are prohibited; patch rejection is the first
failure.

The retained semantic move relocates only the closed quarantine-reason mapping
from the 304-line pipeline into the 241-line protection module, imports it back
under its private alias, and removes only the newly unused enum import. It may
not change behavior, contracts, receipts, routing, tests, dependencies,
assertions, catalog metrics, or debt. Exact verified blocks move verbatim into
their bounded archives with resolving relative links and four Markdown files
at or below 600 lines.

The continuation order remains fail-closed: Amendment 12's valid preflight;
strict decode and one atomic six-path patch; file-size; focused Refinery `53`;
catalog `--check`; full non-live suite; session/repository/static checks; final
exact-32/six-touch/protected/archive/link/line/staged audit. Each command runs
once and the first failure stops.

## Claim boundary and next governed move

No provider/network/remote-ingest call, unrelated edit, retry, waiver,
debt/exception entry, catalog write, BUILD commit/push, self-review, FREEZE,
or later lane is authorized. A pass yields only a dirty deterministic-local
exact-32 candidate pending fresh independent BUILD review; it proves no runtime
caller, persistence, `data_scope`, retrieval/RAG, learning, production, P3-A
closure, or Phase 3 completion.

COMMIT_STEWARD may create/push only the Amendment 13 authority checkpoint under
the bounded governance discipline while preserving exact-28 BUILD unstaged and
both archives absent. Then stop for fresh exact Amendment 13 R2, authorizing
one invocation only and no retry.
