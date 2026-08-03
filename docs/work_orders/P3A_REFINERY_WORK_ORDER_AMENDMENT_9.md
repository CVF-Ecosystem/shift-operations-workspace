# Work Order Amendment 9 — P3-A Exact Static-Gate and Final-Audit Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-9-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 8 SHA-256: `4401af42da2f4da8c0f1bb856e624684f4309eb6c00f6f0407270331d1dd3347`
- Amendment 8 authorization review SHA-256: `6c324b4931947b7ee55068140524dce8575a47b2f7797c7db2635b8815e9fd87`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Amendment 8 acknowledgment checkpoint: `132003c80fa073b28ebe7026e201ac1db5537eb0`
- Amendment 8 authority checkpoint: `844855f4297101093c3d2fc53517292a525592bc`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

The Amendment 8 acknowledgment was pushed at
`132003c80fa073b28ebe7026e201ac1db5537eb0`. Its preflight passed. The exact
direct seven-case probe passed 7/7. The authorized three-path repair completed:
only `cvf-application-profile.status` was restored to `contract-only`,
`refinery-bridge.status` remained `partial`, the catalog was generated once,
and only the registry source pin changed in the active project-context
knowledge entry. Project-knowledge validation passed; focused Knowledge Pack
rehearsal passed `86`; catalog check passed; full non-live suite passed
`1593 passed, 128 skipped`; session-state passed.

The next command attempted the nonexistent plural path
`scripts/check_file_sizes.py` and returned non-zero before file-size,
repository, JSON/YAML, forbidden import/I/O, secret, diff or final audits ran.
It was not retried. Zero provider/network/remote-ingest calls occurred during
the invocation. Amendment 8 and its R2 are consumed.

This amendment corrects the command to the tracked singular script
`scripts/check_file_size.py`, binds the completed repair output as immutable,
and authorizes only never-run static/final verification. No BUILD edit remains.

## Exact retained post-repair binding

Using typed ordinal case-sensitive sorting and UTF-8 records
`path + NUL + lowercase_file_sha256 + LF`:

- exact BUILD path count: `28`;
- exact current manifest SHA-256:
  `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791`;
- source/test path count: `10`;
- immutable source/test manifest SHA-256:
  `addb052c9bafb6cd977435268304d43396b304d65ea730db0060890447ab7352`;
- immutable all-other path count: `25`;
- immutable protected-25 manifest SHA-256:
  `513ba54f7af8b0b44fd4143009aa87bb21faa19c82adc671c99c01fe2676dda1`;
- staged path count: `0`.

Completed repair-surface hashes are:

| Path | SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `1fb8b6e1638b69e6df3ababb823cc18e12238b3d0d2841e501074ff461c22d35` |
| `docs/catalog/MODULE_CATALOG.md` | `94e6c6e960d0b944edeecd34a971da7b6b3ebe70228eecd43b7cf4a761e13dd6` |
| `knowledge/manifest.json` | `b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9` |

Any preflight mismatch stops the continuation.

## Exact repair-touch ceiling — 0 paths

All exact 28 BUILD paths are byte-immutable for this verification-only
continuation. No existing BUILD path may change and no new BUILD path may be
created. Final diff remains exact 28.

## Exact remaining static-gate contract

Run these never-run checks once, in order:

1. `python scripts/check_file_size.py`;
2. `python scripts/testing/validate_repository.py`;
3. one local inline validation command that:
   - requires empty staged/unmerged sets, `git diff --check` PASS and the exact
     28-path dirty set;
   - parses the changed JSON files plus Refinery contract YAML;
   - AST-checks only `packages/refinery-bridge/src/refinery_bridge/*.py` and
     rejects network/provider/process imports plus filesystem I/O calls;
   - scans the exact 28 text paths for high-confidence private-key, AWS access
     key, OpenAI-style key and assigned API/secret/access-token patterns.

The inline command must not edit files, contact a provider/network, print file
contents or print any suspected secret. Any finding returns non-zero.

## Ordered continuation

Run once in this exact order, stopping on the first non-zero command or
contract failure:

1. verify actual pushed authority lineage from Git, bound artifact hashes,
   empty staged set and exact immutable 10/25/28/post-repair digests;
2. run the exact remaining static-gate contract above once;
3. verify final exact 28 paths, zero repair touches during Amendment 9,
   unchanged exact-28/source-test-10/protected-25/repair-surface digests and
   empty staged set.

Retain without rerun: Amendment 5 focused `53`; Amendment 8 direct probe 7/7;
catalog write/check; project-knowledge validator; focused Knowledge Pack `86`;
full non-live `1593 passed, 128 skipped`; session-state PASS. Failed Amendment
5 probe, Amendment 6 preflight, Amendment 7 selector probe and Amendment 8
plural file-size command are not retried or relabeled. No standalone inventory,
search, catalog write, test or earlier-gate command is authorized.

## Stop and claim boundary

This continuation permits zero provider, network and remote-ingest calls and no
retry. A pass yields only a dirty exact 28-path deterministic-local BUILD
candidate pending fresh independent BUILD review. It authorizes no BUILD
commit/push, self-review, FREEZE, runtime caller, persistence, `data_scope`,
retrieval/RAG, learning, production or Phase 3 completion claim.

## Required review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to this
Amendment SHA, completed-retained evidence, exact immutable 10/25/28 binding,
zero repair paths, singular file-size/repository/static commands and zero-call/
no-retry boundary. After the reviewed authority checkpoint is committed/pushed,
the operator must send:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-9-2026-08-04,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 0 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
