# P3-A Refinery Work Order Amendment 15 — Independent Authorization Review

> **Correction history — bounded fresh re-review:** The initial review artifact
> at SHA-256
> `4330c756ed2f4c725f58f4e8034e49aeda5e4aa94672012d1b6dc62920fd3094`
> returned PASS but incorrectly required an exact-six authority checkpoint that
> omitted the still-untracked failed final BUILD review consumed by Amendment
> 15. A bounded governance audit returned `A15-AUTH-F1`, changes required, no
> waiver. No checkpoint, R2, repair, stage, commit or push followed. This fresh
> re-review corrects only that checkpoint set to exact seven and preserves all
> substantive repair, evidence and claim-boundary conclusions.

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Superseded initial review SHA-256: `4330c756ed2f4c725f58f4e8034e49aeda5e4aa94672012d1b6dc62920fd3094`
- Amendment 15 SHA-256: `19e1369d52d1fa65a5bff674fe8a24116767ffcbcf7b84de7340d2fccaced28c`
- Failed final BUILD review SHA-256: `4f5099c5647c715de9e1ae9e5a833dd444c2498ca1ea282d553935cd04f11cf1`
- Final SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Review baseline: `HEAD == origin/main == 49cf7ecd8151b64b0fde5d75cdc2d316687d6e78`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 15 accurately consumes the failed final BUILD review and authorizes
only its four accepted findings. The exact nine already-dirty paths are
sufficient for public-result binding, deterministic multi-match dedupe,
AC-03/05/06/07 evidence, implementation-status truth and the derived knowledge
pin. The final exact-32 candidate, protected-21 set, archive/suffix integrity,
catalog boundary, stop-first/no-retry discipline and zero-call claim remain
non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

`A15-AUTH-F1 — CONSUMED_FINAL_REVIEW_OMITTED_FROM_AUTHORITY_LINEAGE`:
`CLOSED_WITHOUT_WAIVER` by the exact-seven checkpoint contract below.

This PASS does not authorize repair by itself. The bounded partially staged
authority checkpoint must be pushed, then a fresh exact human R2 acknowledgment
for Amendment 15 must authorize the one permitted invocation.

## Consumed final-review truth

The final independent BUILD review correctly retained these passes:

- exact-32 dirty scope, empty staged set and stable-30 manifest;
- the Amendment 13 semantic helper move and Python line limits;
- lossless memory/handoff archive rotations, stable suffixes and links;
- the independent focused Refinery suite at `53 passed`;
- zero provider/network/remote-ingest calls and the deterministic-local claim
  boundary.

Its one direct probe then reproduced four invalid cases: candidate control
version drift accepted, unavailable route accepted as quarantine, unsafe
fallback provenance accepted, and valid chronological multi-match input
escaping `refine` because public match ids were not lexical. The review also
identified material AC-03/05/06/07 gaps and stale implementation-status truth.
It returned `FINAL_REVIEW_CHANGES_REQUIRED`, no waiver. No BUILD commit or
FREEZE followed.

## A15-AUTH-F1 audit trail and closure

The initial exact-six checkpoint would have committed Amendment 15 and its
authorization PASS while leaving
`docs/decisions/P3A_REFINERY_BUILD_FINAL_INDEPENDENT_REVIEW.md` untracked.
That is invalid because Amendment 15 directly consumes and SHA-binds that
artifact as the evidence creating its repair authority. A local untracked file
cannot be the durable pushed provenance of a reviewed authority checkpoint.

The worktree and all candidate bytes remained unchanged after the finding.
Fresh checks reproduced the failed review SHA `4f5099c5…1cf1`, unchanged A15
SHA `19e1369d…d28c`, `HEAD == origin/main == 49cf7ecd…e78`, staged zero,
exact 32, stable 30 and protected 21. Adding the unchanged failed review to the
governance checkpoint makes its lineage durable without touching or absorbing
any BUILD/repair path. Amendment 15 itself already binds the failed-review SHA
and generically requires the governance review checkpoint, so its bytes and SHA
remain valid; only the initial review's exact enumeration required correction.

## Independent binding reproduction

The reviewer excluded only the two authority state paths, the failed final
review artifact and Amendment 15 from the preparation worktree to reproduce
the exact 32-path candidate. Excluding the two volatile continuity front doors
produced stable 30. Excluding the nine repair paths from stable 30 produced
protected 21.

All manifests use ordinal case-sensitive sorting and UTF-8 records encoded as
`path + NUL + lowercase_file_sha256 + LF`.

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Dirty BUILD/continuity paths | `32` | `32` | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Stable paths | `30` | `30` | `PASS` |
| Stable-30 manifest | `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436` | same | `PASS` |
| Protected paths | `21` | `21` | `PASS` |
| Protected-21 manifest | `68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070` | same | `PASS` |

The nine repair pre-hashes reproduce exactly:

| Path | SHA-256 |
|---|---|
| `output_models.py` | `62333c0a2fb0734e50b6a3b564af6303c3488db8e14ec4ac97b86db624b0bd9a` |
| `protection.py` | `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5` |
| `pipeline.py` | `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf` |
| `test_refinery_models.py` | `d99c48ef9fa7b8a29d762c28965ed719039adcd5d2ec5d15ceb2158703732dc8` |
| `test_refinery_canonical.py` | `1d6ac9bdcec387e3c5dcd0e8d259275d5fd08d1b1be2aec6dddba31b99f22e88` |
| `test_refinery_pipeline.py` | `8a2503128927333d33e439a29d562724b5ab45460ea882a6ce02a2a83a7f7104` |
| `test_refinery_adversarial.py` | `1fc79f95f928656988736c10e9456550c61f2836a36662f344935ae87acdb768` |
| `IMPLEMENTATION_STATUS.json` | `0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10` |
| `knowledge/manifest.json` | `b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9` |

Archive files retain exact full hashes `e218cbc1…f86` and `c50d4bfd…d44`.
The canonical memory suffix remains `243/6a055880…ac6`; the handoff suffix
remains `2/46f46615…b357`. Both relative links resolve. Current canonical
front doors are 306/545 lines and archives are 335/394, all below 600.

## Nine-path sufficiency and non-expansion

The repair partition is exact and sufficient:

| Final-review finding | Authorized surfaces | Assessment |
|---|---|---|
| F1 candidate versions, unavailable quarantine route, unsafe fallback provenance | `output_models.py`, `protection.py`, model/adversarial tests | `SUFFICIENT` — existing validators/helpers can bind these facts without schema or contract change |
| F2 chronological selected id plus lexical public match ids | `pipeline.py`, pipeline/adversarial tests | `SUFFICIENT` — selection stays chronological while only the emitted public collection is sorted |
| F3 AC-03/05/06/07 evidence | four authorized test modules | `SUFFICIENT` — current APIs already reject cross-fingerprint class substitution; remaining work is direct golden/property/boundary coverage plus the repaired behaviors |
| F4 stale implementation status | `IMPLEMENTATION_STATUS.json`, `knowledge/manifest.json` | `SUFFICIENT` — status becomes current and only its resulting source pin changes |

All nine paths already belong to exact 32, so no new dirty path is needed.
The protected 21, A13 helper location, archives, continuity suffixes, contract,
fixtures, registry/catalog and project context remain immutable.

Current line counts leave adequate hard-limit room: output/protection/pipeline
are 202/260/285; the four tests are 158/48/120/213. Amendment 15 requires every
edited Python/test file at or below 300 and unchanged catalog metrics. This is
achievable with line-neutral source repair; no compression, debt entry, catalog
write or additional source path is required.

## Probe, coverage and ordered-gate review

The four-case direct probe exactly targets the four reproduced failures:

1. recomputed-fingerprint candidate version drift must fail construction;
2. unavailable quarantine route must fail construction;
3. whitespace owner and URI-userinfo fallback provenance must fail without
   printing those unsafe values;
4. `z-earlier` at 10:00 and `a-later` at 11:00 must return duplicate output
   selecting `z-earlier` while publishing `("a-later", "z-earlier")`.

Requiring only safe labels/results makes the probe disclosure-safe. The focused
five-file suite must then collect at least 57 and pass, so the four direct
regressions cannot replace the broader Refinery evidence.

The remaining order is complete and fail-closed: knowledge validator/focused
suite; file-size and non-mutating catalog check; full non-live suite;
session/repository/JSON-YAML/import-I/O/secret/diff checks; final exact-32,
exact-nine, protected-21, archive/suffix/link/line/staged/claim audit. Each
command runs once and the first failure stops every later step.

## Partial-staged checkpoints

The authority checkpoint must stage exactly seven governance paths:

- `docs/decisions/P3A_REFINERY_BUILD_FINAL_INDEPENDENT_REVIEW.md`, unchanged at
  SHA-256 `4f5099c5647c715de9e1ae9e5a833dd444c2498ca1ea282d553935cd04f11cf1`;
- `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_15.md`;
- this review artifact;
- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- only new A15 authority/review hunks from `SESSION/SESSION_MEMORY.md`;
- only new A15 authority/review hunks from the active handoff.

Its cached diff must contain the complete unchanged failed final review and
must exclude every repair, rotation, source and archive hunk.
After push, staged paths must be zero and exact-32/stable-30/protected-21/
archive/suffix bindings must remain unchanged. The later fresh-R2 checkpoint
must analogously stage exactly four governance paths: canonical state, mirror,
and only new R2 hunks in the two front doors. It must leave the same exact-32
candidate wholly dirty and staged zero after push.

## Claim boundary and next governed move

No provider/network/remote-ingest call, retry, waiver, debt entry, unrelated
edit, BUILD commit, self-review, FREEZE or later lane is authorized. A repair
PASS yields only a dirty exact-32 deterministic-local candidate pending fresh
independent BUILD re-review. It proves no runtime caller, provider behavior,
remote ingest, persistence, `data_scope`, retrieval/RAG, learning, confirmed
truth, production readiness, P3-A closure or Phase 3 completion.

COMMIT_STEWARD may now create and push only the seven-path authority checkpoint
above, prove the exact-32 candidate remains unstaged, and stop for fresh exact
Amendment 15 human R2 naming nine repair paths, final exact 32 and zero calls.
