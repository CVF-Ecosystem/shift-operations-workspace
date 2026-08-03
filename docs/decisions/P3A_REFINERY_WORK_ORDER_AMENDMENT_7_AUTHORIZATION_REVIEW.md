# P3-A Refinery Work Order Amendment 7 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 7 SHA-256: `8712b18a43a35555573bce36f3fe6afd1b91b9709036dce1f1663dddd4c5c965`
- Consumed Amendment 6 SHA-256: `57c8322d82126b4202bbbe5bbbd6df6b3a3aae27ba5a28e1e67b8e6832fe4317`
- Amendment 6 authorization review SHA-256: `cd85418046d45acc261f42595cb1e215350b91235c763f829545896ca8548250`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Amendment 6 authority checkpoint: `e4ac4594383d73a9aa581c93ca75347af4502ca6`
- Amendment 6 acknowledgment checkpoint: `65b47e4a1b42d4ad41424f4c616bfb3f65790e0f`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 7 truthfully records Amendment 6's first-preflight-assertion stop,
corrects the acknowledgment lineage to the actual pushed Git commit, preserves
the complete candidate byte-for-byte, and reauthorizes only the still-unrun
probe and later three-path catalog/knowledge sequence. The scope, ordering,
no-retry rule and zero-call boundary remain sufficient and non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not itself authorize the continuation. The reviewed authority
checkpoint must be committed/pushed and followed by Amendment 7's fresh exact
human R2 acknowledgment before one no-retry invocation may begin.

## Consumed Amendment 6 stop truth

Independent Git and continuity checks establish:

- Amendment 6 authority checkpoint
  `e4ac4594383d73a9aa581c93ca75347af4502ca6` exists as a commit;
- `HEAD == origin/main == 65b47e4a1b42d4ad41424f4c616bfb3f65790e0f`;
- that exact commit is the pushed Amendment 6 R2 acknowledgment checkpoint;
- the worker's first preflight assertion instead hard-coded
  `65b47e4e36e3f42f07b615e9cddeeb969f9afae1` and failed immediately;
- no later preflight assertion, seven-case probe, repair edit, test or later
  gate ran;
- the failed preflight was not retried or adopted as evidence;
- the dirty BUILD candidate and empty staged set remained unchanged;
- no BUILD commit/push and no provider/network/remote-ingest call occurred.

Amendment 6 and its R2 are consumed. Amendment 7 explicitly binds the actual
Git checkpoint and treats its preflight as a fresh command under a separately
reviewed Amendment and fresh R2, not a retry or relabeling of the failed
Amendment 6 assertion.

## Independent retained-binding reproduction

The reviewer used typed `string[]` collections,
`[Array]::Sort(..., [StringComparer]::Ordinal)`, UTF-8, and records encoded as
`path + NUL + lowercase_file_sha256 + LF`.

| Binding | Expected | Reproduced | Result |
|---|---|---|---|
| Exact BUILD paths | `28` | `28` | `PASS` |
| Exact BUILD manifest | `c9e021d3f58bc996daac0d1ec3d21513419d465ab948555b7b62f18d62183d4e` | same | `PASS` |
| Immutable source/test paths | `10` | `10` | `PASS` |
| Immutable source/test manifest | `addb052c9bafb6cd977435268304d43396b304d65ea730db0060890447ab7352` | same | `PASS` |
| Exact repair paths | `3` | `3` | `PASS` |
| Protected paths | `25` | `25` | `PASS` |
| Protected manifest | `513ba54f7af8b0b44fd4143009aa87bb21faa19c82adc671c99c01fe2676dda1` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |

The three writable surfaces also retain their bound starting hashes:

| Path | SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38` |
| `docs/catalog/MODULE_CATALOG.md` | `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92` |
| `knowledge/manifest.json` | `461e6b5a4f72ba9f86e71c1562455176392c30e14d838a6fcef09cf62e6bb429` |

## Exact scope and non-expansion

The only writable BUILD paths remain:

1. `docs/catalog/MODULE_REGISTRY.json`;
2. `docs/catalog/MODULE_CATALOG.md`;
3. `knowledge/manifest.json`.

They are sufficient to restore only
`cvf-application-profile.status=contract-only`, retain
`refinery-bridge.status=partial`, render the generator-owned catalog, and
update only the resulting registry pin. All other 25 BUILD paths—including
the ten source/test paths that already passed the focused `53` gate—remain
byte-immutable. No new BUILD path, source/test change, behavior, dependency,
runtime caller, contract or wider documentation edit is authorized. Final
BUILD diff remains exact 28.

## Probe environment and remaining gates

The seven-case probe environment remains sufficient:

- `packages/refinery-bridge/src` exposes `refinery_bridge`;
- `tests/unit` exposes `_refinery_fixtures`;
- Windows uses `;` between those `PYTHONPATH` roots;
- the environment must be assigned in the same PowerShell process as the
  single `python -` probe invocation (for example through
  `$env:PYTHONPATH = 'packages/refinery-bridge/src;tests/unit'`).

The probe must execute zero-quality-ready, unbound-fingerprint,
invalid-offset, disposition-mismatch, policy-drift, stage-unavailable and
sanitized-unexpected-exception cases. An import failure, missing case,
disclosure or invariant failure stops the invocation.

The remaining sequence is complete and fail-closed:

1. verify actual Git lineage, artifact hashes, staged state and exact
   10/25/28 bindings;
2. run the corrected seven-case probe once;
3. perform the isolated registry correction and catalog `--write` once;
4. update only the registry pin;
5. run knowledge validator and focused local-helper rehearsal once;
6. run catalog `--check`, full non-live suite and repository/static gates once;
7. finish with exact-28, exact-three-touch, immutable 10/25 and staged-state
   verification.

The Amendment 5 focused `53 passed` command is retained and not rerun. The
failed Amendment 5 probe and Amendment 6 preflight are neither retried nor
relabeled. No standalone inventory/search command is authorized. Each new
Amendment 7 command runs at most once, stopping at the first non-zero result or
contract failure.

## Claim boundary and next governed move

The continuation permits zero provider, network and remote-ingest calls. A
successful invocation yields only a dirty exact 28-path deterministic-local
BUILD candidate pending fresh independent BUILD review. It establishes no
runtime caller, persistence, `data_scope`, retrieval/RAG, learning, production,
P3-A closure or Phase 3 completion claim.

After this review and synchronized continuity are committed/pushed while all
28 BUILD paths remain unstaged, the operator must provide Amendment 7's exact
fresh R2 acknowledgment. That acknowledgment authorizes one continuation
invocation only and no retry. It does not authorize BUILD commit/push,
self-review, FREEZE or a later lane.
