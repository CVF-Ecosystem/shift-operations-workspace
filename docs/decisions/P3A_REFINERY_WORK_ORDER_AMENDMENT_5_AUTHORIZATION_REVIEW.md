# P3-A Refinery Work Order Amendment 5 — Independent Authorization Review

- Review date: `2026-08-03`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 5 SHA-256: `44c2576895356e8cb83a7df1d99c945e3a5a354a11e7655521e5288e54e07726`
- Consumed Amendment 4 SHA-256: `0f79fcc75ae468c0c56a2db39d821738e0b863bf94710f2eebcbf845020fd0dd`
- Amendment 4 authorization review SHA-256: `e18217e6c41a958fdd3dc38f0e334c9153e4521929ca1b8758f33a7f856bb320`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Amendment 4 acknowledgment checkpoint: `9dd0900486d961f53bf673a22133bd78f7cccbad`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 5 truthfully binds the retained partial BUILD after Amendment 4's
stop-first event, preserves the exact 13-path repair ceiling and final exact 28
BUILD paths, excludes retry of the failed inventory command, and provides a
sufficient, non-expansive ordered continuation for corrected-review findings
F2-F6. There are no open authorization findings and no waiver.

This PASS does not itself authorize repair. The authority checkpoint must be
committed/pushed and followed by the fresh exact human R2 acknowledgment named
by Amendment 5 before one continuation invocation may begin.

## Consumed Amendment 4 stop truth

Independent repository and continuity checks establish:

- `HEAD == origin/main == 9dd0900486d961f53bf673a22133bd78f7cccbad`;
- that commit is the pushed Amendment 4 R2 acknowledgment checkpoint;
- Amendment 4 preflight passed its authority, exact-28, protected-15 and empty
  staged-set checks;
- five authorized source paths were then partially edited;
- before focused tests, the read-only Windows `rg` command passed literal
  `tests/unit/test_refinery*`, returned non-zero, and triggered stop-first;
- the command was not retried;
- focused tests, public-invariant probe, catalog write, knowledge update,
  catalog check, full suite and later repository gates were `NOT_RUN`;
- no BUILD commit/push and no provider/network/remote-ingest call occurred.

Amendment 4 and its R2 are therefore consumed. Amendment 5 correctly treats
the five source edits as retained partial work with no correctness claim; it
does not relabel any Amendment 4 command as new evidence.

## Independent binding reproduction

The reviewer used typed `string[]` collections,
`[Array]::Sort(..., [StringComparer]::Ordinal)`, UTF-8, and records encoded as
`path + NUL + lowercase_file_sha256 + LF`.

| Binding | Expected | Reproduced | Result |
|---|---|---|---|
| Exact retained BUILD paths | `28` | `28` | `PASS` |
| Exact retained manifest | `c785597e0f15a8a9c4710f65bd21d15713206edfce929a1ad7be7dbe81ece17a` | same | `PASS` |
| Exact repair ceiling | `13` | `13` | `PASS` |
| Protected paths | `15` | `15` | `PASS` |
| Protected manifest | `ce531fb7fe4b8fa7c97aa29863cf1980a8665f5d74d21fb3d17259af37644784` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |

The five retained partial-source hashes also reproduce exactly:

| Path | SHA-256 |
|---|---|
| `packages/refinery-bridge/src/refinery_bridge/controls.py` | `cdf42a528bffac7b031ed100c0d94f067d7e725884dfbe939a9340e4e9651a14` |
| `packages/refinery-bridge/src/refinery_bridge/receipt_models.py` | `32bdf786127faa773b8b6a83128c178d45098bb44871e144b03667d7ba7133d3` |
| `packages/refinery-bridge/src/refinery_bridge/output_models.py` | `240a76f60c14691acd7af255405ece6f381d157b836dad4a5f031b24f8b1f8b9` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `1ff509d87747bcfb864823029ee5edfbfff5d8176e2a1612a1391d61f6425219` |
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `616a0baa1ef58a042e4a4e17914e6dae134b28b1c48eb2314baa6453a5ed343e` |

## Repair-scope sufficiency and non-expansion

Amendment 5 preserves exactly Amendment 4's reviewed 13 paths:

1. five Refinery source paths for controls, receipts, public output,
   protection and pipeline behavior;
2. five focused test/helper paths for public invariants, fail-stop behavior,
   disclosure checks and the executable 28-case R27 matrix;
3. registry and generated catalog paths for the isolated
   `cvf-application-profile` correction while retaining
   `refinery-bridge=partial`;
4. `knowledge/manifest.json` for only the resulting registry source-pin update.

Those surfaces remain sufficient for F2 public-result binding, F3 executable
R27 coverage, F4 total sanitized fail-stop paths, F5 safe-string/collection/
offset validation and F6 catalog correction. The other 15 BUILD paths remain
byte-immutable. No new path, input contract, enum, canonical/dedupe behavior,
runtime caller or broader architectural change is authorized.

## Ordered gates and no-retry assessment

The sequence is coherent and fail-closed:

1. fresh authority/hash/exact-set/staged preflight;
2. complete only the authorized source/test repair;
3. focused Refinery tests once;
4. dedicated public-invariant/fail-stop/disclosure probe once;
5. isolated registry correction and one catalog write;
6. exact registry-pin update;
7. knowledge validator and focused local-helper rehearsal once;
8. catalog check, full non-live suite and repository/static gates once;
9. final exact-28, 13-path ceiling, protected-15 and staged-set audit.

The failed Amendment 4 `rg` inventory command is expressly not retried and is
not a gate. Amendment 5 prohibits a replacement standalone inventory/search
command during repair. Every newly authorized command runs at most once, and
the invocation stops on its first non-zero result or contract failure.

## Claim boundary and next governed move

The continuation permits zero provider, network and remote-ingest calls. A
successful invocation yields only a dirty exact 28-path deterministic-local
BUILD candidate pending fresh independent BUILD review. It establishes no
runtime caller, persistence, `data_scope`, retrieval/RAG, learning, production,
P3-A closure or Phase 3 completion claim.

Open authorization findings: `NONE`. Waivers: `NONE`.

After this reviewed Amendment and synchronized continuity are committed/pushed
while all BUILD paths remain unstaged, the operator must provide Amendment 5's
fresh exact R2 acknowledgment. That acknowledgment authorizes one continuation
invocation only, with no retry. It does not authorize BUILD commit/push,
self-review, FREEZE or any later lane.
