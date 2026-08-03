# P3-A Refinery Work Order Amendment 9 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 9 SHA-256: `417a11af86915cca0249e3559236f498fc96f7e60c8363376b4493f26aefca0e`
- Consumed Amendment 8 SHA-256: `4401af42da2f4da8c0f1bb856e624684f4309eb6c00f6f0407270331d1dd3347`
- Amendment 8 authorization review SHA-256: `6c324b4931947b7ee55068140524dce8575a47b2f7797c7db2635b8815e9fd87`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Amendment 8 authority checkpoint: `844855f4297101093c3d2fc53517292a525592bc`
- Amendment 8 acknowledgment checkpoint: `132003c80fa073b28ebe7026e201ac1db5537eb0`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 9 accurately consumes Amendment 8's first-failure stop, preserves
all 28 BUILD paths byte-for-byte after the completed three-path repair, and
authorizes no further repair. Its singular file-size command, repository
validator, one bounded inline static command, final audit, stop-first/no-retry
discipline, and zero-call boundary are sufficient and non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not authorize continuation by itself. The reviewed authority
checkpoint must be committed/pushed, then the operator must provide the exact
fresh Amendment 9 R2 acknowledgment before one no-retry invocation may begin.

## Consumed Amendment 8 truth

Independent Git, artifact, continuity, and source checks establish:

- `HEAD == origin/main == 132003c80fa073b28ebe7026e201ac1db5537eb0`;
- `844855f4297101093c3d2fc53517292a525592bc` is the Amendment 8 authority
  review commit, and `132003c80fa073b28ebe7026e201ac1db5537eb0` is its pushed
  R2 acknowledgment checkpoint;
- Amendment 8 preflight passed, followed by the direct probe `7/7`;
- the exact three-path repair completed, the knowledge validator passed, the
  focused rehearsal passed `86`, catalog check passed, the full non-live suite
  passed `1593 passed, 128 skipped`, and session-state passed;
- the next command named nonexistent `scripts/check_file_sizes.py`, failed
  before any remaining static/final gate, and was not retried;
- no later command or repair ran, staged paths remained zero, and provider,
  network, and remote-ingest calls were all zero.

Amendment 8 and its R2 are consumed. Amendment 9 does not retry or relabel the
failed plural-path command; it specifies the tracked singular guard as a new,
separately reviewed continuation.

## Independent post-repair binding reproduction

The reviewer used typed `string[]` path collections, ordinal ordering, UTF-8,
and records encoded as `path + NUL + lowercase_file_sha256 + LF`.

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact BUILD paths | `28` | `28` | `PASS` |
| Post-repair BUILD manifest | `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791` | same | `PASS` |
| Immutable source/test paths | `10` | `10` | `PASS` |
| Source/test manifest | `addb052c9bafb6cd977435268304d43396b304d65ea730db0060890447ab7352` | same | `PASS` |
| Protected paths | `25` | `25` | `PASS` |
| Protected manifest | `513ba54f7af8b0b44fd4143009aa87bb21faa19c82adc671c99c01fe2676dda1` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |

The three completed repair outputs retain their exact bound hashes:

| Path | SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `1fb8b6e1638b69e6df3ababb823cc18e12238b3d0d2841e501074ff461c22d35` |
| `docs/catalog/MODULE_CATALOG.md` | `94e6c6e960d0b944edeecd34a971da7b6b3ebe70228eecd43b7cf4a761e13dd6` |
| `knowledge/manifest.json` | `b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9` |

The working tree also contains Amendment 9 and four continuity artifacts;
they are governance surfaces outside the exact 28-path BUILD subset. No extra
implementation, test, fixture, contract, catalog, status, or knowledge path is
present in that BUILD subset.

## Remaining-gate contract review

Repository tracking is singular: `scripts/check_file_size.py` and
`scripts/testing/validate_repository.py` are tracked, while
`scripts/check_file_sizes.py` is not. The singular guard is a read-only file
size/debt check. The repository validator requires that same singular path and
aggregates catalog, session-state, and file-size checks. Its internal invocation
of the file-size guard is part of the separately named aggregate validator,
not a retry of Amendment 8's nonexistent plural-path failure.

The one inline command is bounded to local, read-only validation: exact dirty
BUILD membership, empty staged/unmerged sets, `git diff --check`, parsing the
changed JSON files and Refinery YAML contract, AST inspection of only Refinery
source for forbidden provider/network/process imports and filesystem I/O, and
high-confidence secret-pattern scanning over only the exact 28 text paths. It
must return non-zero at its first finding, reveal neither contents nor secrets,
and perform no edit or external call.

The order is fail-closed: actual Git lineage and every immutable binding first;
the three remaining commands exactly once; then the final exact-28, zero-touch,
unchanged-digest/surface-hash, and staged-zero audit. All 28 BUILD paths are
immutable and the repair ceiling is exactly zero.

Retained evidence is explicitly not rerun: Amendment 5 focused `53`, Amendment
8 direct probe `7/7`, catalog write/check, knowledge validator, focused `86`,
full non-live `1593 passed, 128 skipped`, and session-state PASS. The failed
Amendment 5 probe, Amendment 6 preflight, Amendment 7 selector, and Amendment 8
plural-path command are neither retried nor relabeled. No standalone inventory,
search, catalog write, test, or earlier gate is authorized.

## Claim boundary and next governed move

The continuation permits exactly zero provider, network, and remote-ingest
calls and no retry. A pass yields only a dirty exact 28-path deterministic-local
BUILD candidate pending fresh independent BUILD review. It authorizes no BUILD
commit/push, self-review, FREEZE, runtime caller, persistence, `data_scope`,
retrieval/RAG, learning, production, P3-A closure, or Phase 3 completion claim.

After this review and synchronized continuity are committed/pushed while all
28 BUILD paths remain unstaged, the operator must provide Amendment 9's exact
fresh R2 acknowledgment. That acknowledgment authorizes one continuation
invocation only.
