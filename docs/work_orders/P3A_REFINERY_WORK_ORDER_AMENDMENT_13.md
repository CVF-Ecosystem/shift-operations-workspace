# Work Order Amendment 13 — P3-A Runtime-Neutral UTF-8 Decode Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-13-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 12 SHA-256: `a16c32a5c351d4fabb06ad64f24d0f3ad3bcc3dda5194e978d8abf1e3b627918`
- Amendment 12 review SHA-256: `6b807775c665c98d089be047ab81d6dd9a953759cca1906b6a32474c53aa9d32`
- Amendment 12 authority checkpoint: `82071ee8f8fb0615e763d20789c52c7db7a5b594`
- Amendment 12 acknowledgment checkpoint: `bf9daaf3feb108c8f9fd63352e5d80ddfec7e717`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and fail-stop truth

Amendment 12 preflight passed. At step 2, separate local PowerShell commands
successfully selected and SHA-verified both UTF-8 archive blocks and returned
their base64 payloads. Before patch construction, the V8 orchestration raised
`ReferenceError: TextDecoder is not defined`. `apply_patch` was never called.
Execution stopped immediately without retry: zero repair touches, archives
absent, later gates `NOT_RUN`, zero provider/network/remote-ingest calls.
Amendment 12 and its R2 are consumed.

## Retained bindings and scope

All Amendment 12 bindings remain unchanged:

- exact-28 manifest `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791`;
- protected-26 `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20`;
- Python hashes `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c`
  and `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623`;
- memory block `331` / `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e`;
- handoff block `390` / `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14`;
- staged zero and both archives absent.

The exact repair ceiling remains the same six paths and final exact 32:
`pipeline.py`, `protection.py`, canonical memory, its named archive, active
handoff, and its named foundation archive. The other 26 BUILD paths are
byte-immutable. Retain the reviewed semantic helper move, lossless rotations,
relative links, line limits and one atomic `apply_patch` from Amendment 12.

## Corrected decoder contract

Retain independently selected, normalized, line-counted and SHA-verified
UTF-8/base64 payloads. Decode base64 to bytes with a bounded local algorithm,
then decode UTF-8 with an explicit pure-JavaScript scalar-value decoder that:

- accepts valid 1-, 2-, 3- and 4-byte sequences;
- rejects invalid continuation bytes, truncation, overlong encodings,
  surrogate scalar values and values above `U+10FFFF`;
- emits surrogate pairs only for valid scalars above `U+FFFF`;
- rechecks decoded line counts before patch construction.

Do not depend on `TextDecoder`, `atob`, Node, optional JSON properties, helper
files or shell/Python writes. Any decode/count/digest/patch rejection stops
without retry before later gates.

## Ordered continuation and boundary

Run Amendment 12's valid multi-line preflight once, then the corrected decode
and one atomic six-path patch, file-size gate, focused Refinery `53`, catalog
check, full non-live suite, session/repository/static checks, and final exact-
32/six-touch/protected/archive/link/line/staged audit. Each command runs once;
stop first failure. No provider/network/remote-ingest, unrelated edit, BUILD
commit, self-review, FREEZE or later lane. PASS yields only a dirty local
candidate pending independent BUILD review.

Independent authorization review and a pushed authority checkpoint are
required, followed by fresh exact human R2 for Amendment 13, exact six repair
paths/final exact 32, zero provider/network/remote-ingest, one invocation and
no retry.
