# P3-A Refinery Work Order Amendment 8 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 8 SHA-256: `4401af42da2f4da8c0f1bb856e624684f4309eb6c00f6f0407270331d1dd3347`
- Consumed Amendment 7 SHA-256: `8712b18a43a35555573bce36f3fe6afd1b91b9709036dce1f1663dddd4c5c965`
- Amendment 7 authorization review SHA-256: `4f55a537bfb356f399ab3722b71af56771091049f8b2b7e2851fac1dd4fe72fc`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Amendment 7 authority checkpoint: `dda6d1d9dc176ee2d7bc051d7cf96ea2895f14bc`
- Amendment 7 acknowledgment checkpoint: `9742c3bede7658ab9c56724ad0ad58d23a9a5e9d`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 8 truthfully records Amendment 7's selector failure before test-case
execution, preserves the complete BUILD candidate byte-for-byte, and replaces
pytest-node guessing with a bounded direct seven-case contract over immutable
source/tests. The exact three-path ceiling, remaining-gate order, stop-first/
no-retry discipline and zero-call boundary remain sufficient and
non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not itself authorize continuation. The reviewed authority
checkpoint must be committed/pushed and followed by Amendment 8's fresh exact
human R2 acknowledgment before one no-retry invocation may begin.

## Consumed Amendment 7 stop truth

Independent Git and continuity checks establish:

- Amendment 7 authority checkpoint
  `dda6d1d9dc176ee2d7bc051d7cf96ea2895f14bc` exists as a commit;
- `HEAD == origin/main == 9742c3bede7658ab9c56724ad0ad58d23a9a5e9d`;
- that exact commit is the pushed Amendment 7 R2 acknowledgment checkpoint;
- Amendment 7 preflight passed actual lineage, artifact hashes, empty staged
  set and exact 10/25/28 bindings;
- the stdin probe collected node ids, then its guessed selector found no node
  containing `zero_quality`;
- it stopped before executing any selected test case and was not retried;
- no repair edit, test case or later gate ran;
- the dirty BUILD candidate and empty staged set remained unchanged;
- no BUILD commit/push and no provider/network/remote-ingest call occurred.

Amendment 7 and its R2 are consumed. Amendment 8 does not adopt collection as
case evidence and does not retry or relabel the failed selector probe. Its
direct probe is a new, differently specified command under a separately
reviewed Amendment and fresh R2.

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

The three writable surfaces retain their bound starting hashes:

| Path | SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38` |
| `docs/catalog/MODULE_CATALOG.md` | `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92` |
| `knowledge/manifest.json` | `461e6b5a4f72ba9f86e71c1562455176392c30e14d838a6fcef09cf62e6bb429` |

## Direct seven-case probe review

The reviewer inspected the immutable pipeline, protection, public-output,
receipt, control and fixture surfaces. Each direct case is executable against
the current API and checks a distinct required boundary:

| Case | Direct mechanism | Required evidence |
|---|---|---|
| `zero_quality_ready` | mutate a valid ready result to an all-zero quality receipt | public result validation rejects unbound R20 quality |
| `unbound_fingerprint` | replace the candidate fingerprint with valid-shape zero digests/length | public result validation recomputes and rejects the R23 mismatch |
| `invalid_offsets` | directly construct a NORMALIZATION receipt with `(9, 2)` | receipt validation rejects reversed offsets |
| `disposition_mismatch` | convert the no-context quarantine result into an invented duplicate result | R21/first-failure binding rejects the contradictory disposition |
| `policy_drift` | temporarily downgrade RESTRICTED classification to PUBLIC | CLASSIFICATION fails exactly `POLICY_DRIFT` |
| `stage_unavailable` | temporarily raise typed `StageUnavailableError` from normalization | typed failure, next `NOT_RUN`, and fallback disposition are all required |
| `sanitized_unexpected_exception` | temporarily raise `RuntimeError("raw-secret")` from conflict with an in-memory log handler | `STAGE_INVARIANT_ERROR`; secret absent from serialized result and logs |

The contract avoids pytest collection and node ids entirely. It requires one
`python -` process, explicit `ValidationError` helpers that fail on acceptance,
a seven-label order/count assertion, and `finally` restoration for every
temporary function replacement and logging handler. It permits output only of
safe case labels and `AMENDMENT_8_SEVEN_CASE_PROBE_PASS`; raw exceptions,
payloads and serialized results are prohibited. A top-level failure must
therefore remain sanitized rather than emitting exception content.

The import environment remains correct for Windows:

- `packages/refinery-bridge/src` exposes `refinery_bridge`;
- `tests/unit` exposes `_refinery_fixtures`;
- `;` is the Windows path separator;
- the PowerShell process environment must be assigned immediately before the
  one stdin probe, for example
  `$env:PYTHONPATH = 'packages/refinery-bridge/src;tests/unit'`.

This probe directly covers the corrected-review invariant/fail-stop/disclosure
finding without changing or executing pytest nodes and without modifying any
protected source/test file.

## Exact scope and remaining gates

The only writable BUILD paths remain:

1. `docs/catalog/MODULE_REGISTRY.json`;
2. `docs/catalog/MODULE_CATALOG.md`;
3. `knowledge/manifest.json`.

They are sufficient to restore only
`cvf-application-profile.status=contract-only`, retain
`refinery-bridge.status=partial`, render generator-owned catalog output, and
update only the resulting registry pin. The other 25 paths—including all ten
source/tests that passed the retained focused `53` gate—remain byte-immutable.
No new BUILD path, source/test change, runtime caller, behavior, dependency,
contract or wider documentation change is authorized. Final BUILD diff remains
exact 28.

The ordered continuation is complete and fail-closed: fresh lineage/hash/
binding preflight; one direct probe; isolated registry and catalog write; exact
knowledge pin; knowledge/local-helper, catalog, full non-live and repository/
static gates once; then final exact-three-touch and immutable 10/25/28 audit.

The retained focused `53 passed` command is not rerun. The failed Amendment 5
probe, Amendment 6 preflight and Amendment 7 selector probe are neither retried
nor relabeled. No standalone inventory, collection or search command is
authorized. Every Amendment 8 command runs at most once and stops on its first
non-zero result or contract failure.

## Claim boundary and next governed move

The continuation permits zero provider, network and remote-ingest calls. A
successful invocation yields only a dirty exact 28-path deterministic-local
BUILD candidate pending fresh independent BUILD review. It establishes no
runtime caller, persistence, `data_scope`, retrieval/RAG, learning, production,
P3-A closure or Phase 3 completion claim.

After this review and synchronized continuity are committed/pushed while all
28 BUILD paths remain unstaged, the operator must provide Amendment 8's exact
fresh R2 acknowledgment. That acknowledgment authorizes one continuation
invocation only and no retry. It does not authorize BUILD commit/push,
self-review, FREEZE or a later lane.
